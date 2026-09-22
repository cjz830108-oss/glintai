/* =========================================================================
 * Glint AI — PayPal webhook → Supabase (subscription status sync)
 * -------------------------------------------------------------------------
 * SERVERLESS FUNCTION. Deploy to:
 *   - Vercel:   /api/paypal-webhook.js  (Node.js, default export)
 *   - Netlify:  /netlify/functions/paypal-webhook.js  (use event.body as rawBody)
 *
 * Required env vars (set in the host dashboard, never in client code):
 *   PAYPAL_CLIENT_ID
 *   PAYPAL_CLIENT_SECRET
 *   PAYPAL_WEBHOOK_ID          (from PayPal → Developers → Webhooks)
 *   PAYPAL_MODE=live|sandbox
 *   SUPABASE_URL
 *   SUPABASE_SERVICE_ROLE_KEY  (server-only — bypasses RLS)
 *   SKIP_VERIFY=true           (optional, dev only — skips signature check)
 *
 * In PayPal → Developers → Webhooks, point the endpoint at this function's URL
 * and subscribe to billing events:
 *   BILLING.SUBSCRIPTION.ACTIVATED
 *   BILLING.SUBSCRIPTION.CANCELLED
 *   BILLING.SUBSCRIPTION.EXPIRED
 *   BILLING.SUBSCRIPTION.SUSPENDED
 *   BILLING.SUBSCRIPTION.PAYMENT.FAILED
 *   PAYMENT.SALE.COMPLETED          (fires on first payment AND every renewal — grants monthly credits)
 *
 * Credit grants are idempotent by unique reference `paypal:sale:<sale_id>`,
 * so PayPal retries / webhook redelivery never double-credits a wallet.
 * ========================================================================= */

import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';
import { grantCredits } from './_lib/credits.js';

export const config = { api: { bodyParser: false } };

const sb = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);
const BASE = process.env.PAYPAL_MODE === 'live'
  ? 'https://api.paypal.com'
  : 'https://api.sandbox.paypal.com';

// plan_id → tier mapping (env overrides the configured live plan ids)
const PLAN_IDS = {
  [process.env.PAYPAL_PLAN_PRO || 'P-8JY348393B145582ENJ2IRFQ']: 'pro',
  [process.env.PAYPAL_PLAN_TEAM || 'P-5C811609NL238632RNJ2ITIA']: 'team',
};
// tier → monthly credits granted on every billing cycle
const PLAN_CREDITS = { pro: 8000, team: 60000 };

function tierFromPlanId(planId) {
  return (planId && PLAN_IDS[planId]) || null;
}

function tierFromAmount(total) {
  const n = parseFloat(total);
  if (Number.isNaN(n)) return null;
  if (n >= 29) return 'team';
  if (n >= 9) return 'pro';
  return null;
}

async function getAccessToken() {
  const id = process.env.PAYPAL_CLIENT_ID;
  const secret = process.env.PAYPAL_CLIENT_SECRET;
  const res = await fetch(`${BASE}/v1/oauth2/token`, {
    method: 'POST',
    headers: {
      Authorization: 'Basic ' + Buffer.from(`${id}:${secret}`).toString('base64'),
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'grant_type=client_credentials'
  });
  const json = await res.json();
  return json.access_token;
}

async function verifyWebhook(rawBody, headers) {
  if (process.env.SKIP_VERIFY === 'true') return true;
  try {
    const cert = await (await fetch(headers['paypal-cert-url'])).text();
    const pub = crypto.createPublicKey(cert);
    const expected = [
      headers['paypal-transmission-id'],
      headers['paypal-transmission-time'],
      process.env.PAYPAL_WEBHOOK_ID,
      crypto.createHash('sha256').update(rawBody).digest('hex')
    ].join('|');
    const sig = Buffer.from(headers['paypal-transmission-sig'], 'base64');
    return crypto.verify('sha256', Buffer.from(expected), pub, sig);
  } catch (e) {
    console.error('verifyWebhook error', e);
    return false;
  }
}

async function readRaw(req) {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  return Buffer.concat(chunks).toString('utf8');
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end('Method not allowed');

  const rawBody = await readRaw(req);
  const ok = await verifyWebhook(rawBody, req.headers);
  if (!ok) return res.status(400).send('Invalid signature');

  let event;
  try { event = JSON.parse(rawBody); } catch { return res.status(400).send('Bad JSON'); }

  try {
    const t = event.event_type;
    const email = event.resource?.subscriber?.email_address
               || event.resource?.payer?.email_address;

    if (t === 'BILLING.SUBSCRIPTION.ACTIVATED') {
      const tier = tierFromPlanId(event.resource?.plan_id) || 'pro';
      await upsertPlan(email, tier, 'active');
    } else if (t === 'PAYMENT.SALE.COMPLETED') {
      const tier = tierFromAmount(event.resource?.amount?.total);
      if (tier) {
        await upsertPlan(email, tier, 'active');
        await grantMonthlyCredits(email, tier, event.resource?.id);
      } else {
        console.warn('PAYMENT.SALE.COMPLETED with unmapped amount', event.resource?.amount?.total);
      }
    } else if (['BILLING.SUBSCRIPTION.CANCELLED',
                'BILLING.SUBSCRIPTION.EXPIRED',
                'BILLING.SUBSCRIPTION.SUSPENDED'].includes(t)) {
      await upsertPlan(email, 'free', 'canceled');
    } else if (t === 'BILLING.SUBSCRIPTION.PAYMENT.FAILED') {
      await upsertPlan(email, 'free', 'past_due');
    }
    return res.status(200).json({ received: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: err.message });
  }
}

async function upsertPlan(email, plan, status) {
  if (!email) { console.error('upsertPlan: no email on event'); return; }
  // The webhook matches the user by email (PayPal subscriber email == Supabase auth email).
  // `paypal_email` is stored on the profile at signup; see SETUP.md.
  const { error } = await sb
    .from('profiles')
    .update({ plan, sub_status: status, paypal_email: email })
    .eq('email', email);
  if (error) console.error('upsertPlan failed:', error);
}

/** Grant the plan's monthly credits. Idempotent: `paypal:sale:<sale_id>` is unique. */
async function grantMonthlyCredits(email, tier, saleId) {
  if (!email || !saleId) { console.error('grantMonthlyCredits: missing email/saleId'); return; }
  const amount = PLAN_CREDITS[tier] || 0;
  if (!amount) return;
  const { data: profile } = await sb.from('profiles').select('id').eq('email', email).maybeSingle();
  if (!profile) { console.error('grantMonthlyCredits: no profile for', email); return; }
  // ensure a wallet row exists (grantCredits bumps an existing row)
  const { data: w } = await sb.from('credit_wallets').select('user_id').eq('user_id', profile.id).maybeSingle();
  if (!w) {
    const { error } = await sb.from('credit_wallets').insert({ user_id: profile.id, balance: 0 });
    if (error && error.code !== '23505') console.error('wallet create failed:', error);
  }
  await grantCredits(profile.id, amount, `paypal:sale:${saleId}`, { source: 'paypal', tier });
  console.log(`[webhook] granted ${amount} credits (${tier}) for sale ${saleId} → ${email}`);
}
