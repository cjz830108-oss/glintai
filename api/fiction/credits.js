// /api/fiction/credits — GET wallet + recent transactions
import { json, fail, cors, requireUser } from '../_lib/db.js';
import { getWallet } from '../_lib/credits.js';

export const maxDuration = 10;

export default async function handler(req, res) {
  if (cors(req, res)) return;
  if (req.method !== 'GET') return fail(res, 405, 'method', 'Use GET.');
  return requireUser(req, res, async (user) => {
    const wallet = await getWallet(user.id);
    json(res, 200, { wallet });
  });
}
