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
 *
 * NOTE (Vercel): bodyParser is disabled below so we can read the RAW body,
 * which is required for PayPal signature verification. On Netlify/Functions,
 * use `event.body` directly instead of readRaw(req).
 * ========================================================================= */

import { createClient } from '@supabase/supabase-js';
import crypto from 'crypto';

export const config = { api: { bodyParser: false } };

const sb = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY);
const BASE = process.env.PAYPAL_MODE === 'live'
  ? 'https://api.paypal.com'
  : 'https://api.sandbox.paypal.com';

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
      await upsertPlan(email, 'pro', 'active');
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
