// Glint Fiction — Credits ledger (wallet + transactions, idempotent by reference)
// Flow per task: estimate → lock → execute → settle(actual) → refund unused.
// Task failure → refund full locked amount. Never double-charge (unique reference).
import { admin } from './db.js';

export const FREE_GRANT = 100; // signup credits

export async function ensureWallet(userId) {
  const { data: w } = await admin.from('credit_wallets').select('*').eq('user_id', userId).maybeSingle();
  if (w) return w;
  const { data: created, error } = await admin
    .from('credit_wallets')
    .insert({ user_id: userId, balance: 0 })
    .select()
    .single();
  if (error) throw Object.assign(new Error(error.message), { status: 500, code: 'db' });
  // initial grant (idempotent by unique reference)
  await grantCredits(userId, FREE_GRANT, `grant:signup:${userId}`);
  return { ...created, balance: created.balance + FREE_GRANT };
}

async function bumpWallet(userId, delta, spend = false) {
  const { data: w } = await admin.from('credit_wallets').select('*').eq('user_id', userId).single();
  const balance = w.balance + delta;
  if (balance < 0) throw Object.assign(new Error('Insufficient credits.'), { status: 402, code: 'insufficient_credits' });
  const patch = { balance, updated_at: new Date().toISOString() };
  if (spend) patch.lifetime_spent = w.lifetime_spent + Math.max(0, -delta);
  await admin.from('credit_wallets').update(patch).eq('user_id', userId);
  return balance;
}

export async function grantCredits(userId, amount, reference, meta = {}) {
  return applyTx(userId, 'grant', amount, reference, null, meta);
}

export async function lockCredits(userId, amount, taskId, meta = {}) {
  if (amount <= 0) return 0;
  const balance = await bumpWallet(userId, -amount);
  await admin.from('credit_transactions').insert({
    user_id: userId, type: 'lock', amount: -amount, balance_after: balance, reference: `lock:${taskId}`, task_id: taskId, meta,
  });
  return balance;
}

/** Settle a locked task: charge `used` of `locked`, refund the rest. */
export async function settleCredits(userId, taskId, used, locked) {
  const refund = Math.max(0, locked - used);
  let ops = [];
  if (used > 0) {
    const balance = await bumpWallet(userId, 0, true); // count spend without changing balance (already locked)
    ops.push(['settle', 0, balance, `settle:${taskId}`]);
    await admin.from('credit_transactions').insert({
      user_id: userId, type: 'settle', amount: 0, balance_after: balance, reference: `settle:${taskId}`, task_id: taskId,
      meta: { used },
    });
  }
  if (refund > 0) {
    const balance = await bumpWallet(userId, refund);
    await admin.from('credit_transactions').insert({
      user_id: userId, type: 'refund', amount: refund, balance_after: balance, reference: `refund:${taskId}`, task_id: taskId,
      meta: { locked, used },
    });
  }
  return { used, refund, ops };
}

/** Refund a fully failed task. Idempotent via unique reference. */
export async function refundTask(userId, taskId, locked) {
  if (locked <= 0) return;
  const { data: existing } = await admin
    .from('credit_transactions').select('id').eq('reference', `refund:${taskId}`).maybeSingle();
  if (existing) return;
  const balance = await bumpWallet(userId, locked);
  await admin.from('credit_transactions').insert({
    user_id: userId, type: 'refund', amount: locked, balance_after: balance, reference: `refund:${taskId}`, task_id: taskId,
    meta: { reason: 'task_failed' },
  });
}

async function applyTx(userId, type, amount, reference, taskId, meta) {
  const { data: existing } = await admin
    .from('credit_transactions').select('id').eq('reference', reference).maybeSingle();
  if (existing) return; // already applied (idempotent)
  const balance = await bumpWallet(userId, amount);
  await admin.from('credit_transactions').insert({
    user_id: userId, type, amount, balance_after: balance, reference, task_id: taskId, meta,
  });
  if (type === 'grant' || type === 'purchase' || type === 'bonus') {
    const { data: w } = await admin.from('credit_wallets').select('lifetime_granted').eq('user_id', userId).single();
    await admin.from('credit_wallets').update({ lifetime_granted: (w?.lifetime_granted || 0) + amount }).eq('user_id', userId);
  }
}

export async function getWallet(userId) {
  await ensureWallet(userId);
  const { data: w } = await admin.from('credit_wallets').select('balance,lifetime_granted,lifetime_spent').eq('user_id', userId).single();
  const { data: txs } = await admin
    .from('credit_transactions').select('type,amount,balance_after,task_id,meta,created_at')
    .eq('user_id', userId).order('created_at', { ascending: false }).limit(20);
  return { ...w, recent: txs || [] };
}
