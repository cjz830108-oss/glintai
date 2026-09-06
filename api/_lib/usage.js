// Glint Fiction — usage accounting helper
import { admin } from './db.js';

export async function recordUsage(userId, novelId, taskId, agent, out, credits = 0) {
  await admin.from('model_usage').insert({
    user_id: userId, novel_id: novelId || null, task_id: taskId || null, agent,
    provider: out.provider, model: out.model,
    input_tokens: out.usage?.input || 0, output_tokens: out.usage?.output || 0,
    cached_tokens: out.usage?.cached || 0,
    estimated_cost_usd: out.costUsd || 0, credits_charged: credits, success: true,
  });
}
