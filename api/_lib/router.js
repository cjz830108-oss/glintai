// Glint Fiction — Model Router
// Unified generate()/jsonGenerate() over DeepSeek + OpenAI.
// Business code NEVER calls provider APIs directly — always via this router.
// Keys live server-side only (env). Failure on one provider auto-falls back.

const PROVIDERS = {
  deepseek: {
    url: 'https://api.deepseek.com/chat/completions',
    key: () => process.env.DEEPSEEK_API_KEY,
    models: { light: 'deepseek-chat', creative: 'deepseek-chat', deep: 'deepseek-reasoner' },
    priceIn: 0.27 / 1e6,   // USD per token (approx list price)
    priceOut: 1.10 / 1e6,
  },
  openai: {
    url: 'https://api.openai.com/v1/chat/completions',
    key: () => process.env.OPENAI_API_KEY,
    models: { light: 'gpt-4o-mini', creative: 'gpt-4o-mini', deep: 'gpt-4o' },
    priceIn: 0.15 / 1e6,
    priceOut: 0.60 / 1e6,
  },
};

// Task tier → provider preference order (env overridable)
const TIERS = {
  light:    (process.env.MODEL_LIGHT    || 'deepseek,openai').split(','),
  creative: (process.env.MODEL_CREATIVE || 'deepseek,openai').split(','),
  deep:     (process.env.MODEL_DEEP     || 'openai,deepseek').split(','),
};

async function callProvider(providerName, { system, user, temperature, maxTokens, jsonMode, timeoutMs, tier }) {
  const p = PROVIDERS[providerName];
  const key = p.key();
  if (!key) throw Object.assign(new Error(`No API key for ${providerName}`), { code: 'no_key' });

  const body = {
    model: p.models[tier] || p.models.light,
    messages: [
      { role: 'system', content: system },
      { role: 'user', content: user },
    ],
    temperature: temperature ?? 0.8,
    max_tokens: maxTokens || 4096,
    stream: false,
  };
  if (jsonMode) body.response_format = { type: 'json_object' };

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs || 120000);
  try {
    const r = await fetch(p.url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${key}` },
      body: JSON.stringify(body),
      signal: ctrl.signal,
    });
    if (!r.ok) {
      const text = await r.text().catch(() => '');
      throw Object.assign(new Error(`${providerName} ${r.status}: ${text.slice(0, 300)}`), { code: 'provider_error' });
    }
    const data = await r.json();
    const choice = data.choices?.[0]?.message?.content ?? '';
    const usage = data.usage || { prompt_tokens: 0, completion_tokens: 0, prompt_tokens_details: {} };
    return {
      text: choice,
      provider: providerName,
      model: data.model || body.model,
      usage: {
        input: usage.prompt_tokens || 0,
        output: usage.completion_tokens || 0,
        cached: usage.prompt_tokens_details?.cached_tokens || 0,
      },
      costUsd:
        (usage.prompt_tokens || 0) * p.priceIn + (usage.completion_tokens || 0) * p.priceOut,
    };
  } finally {
    clearTimeout(timer);
  }
}

/**
 * generate({ tier, system, user, temperature, maxTokens, json, timeoutMs })
 * tier: 'light' | 'creative' | 'deep'
 * json: true → force JSON output and return parsed object (throws on bad JSON)
 * Returns { text?, data?, provider, model, usage, costUsd }
 */
export async function generate(opts) {
  const { tier = 'light', json = false } = opts;
  const order = TIERS[tier] || TIERS.light;
  const errors = [];

  for (const name of order) {
    if (!PROVIDERS[name]) continue;
    try {
      const out = await callProvider(name, opts);
      if (json) {
        out.data = extractJson(out.text);
        if (out.data === undefined) throw Object.assign(new Error('Bad JSON from provider'), { code: 'bad_json' });
      }
      return out;
    } catch (err) {
      errors.push(`${name}: ${err.message}`);
    }
  }
  throw Object.assign(new Error(`All model providers failed → ${errors.join(' | ')}`), {
    code: 'router_failed',
    status: 502,
  });
}

/** Parse JSON out of a model response (handles ```json fences and prose wrappers). */
export function extractJson(text) {
  if (!text) return undefined;
  const fenced = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  const candidates = [fenced?.[1], text];
  for (const c of candidates) {
    if (!c) continue;
    const start = Math.min(...['{', '['].map((ch) => {
      const i = c.indexOf(ch);
      return i === -1 ? Infinity : i;
    }));
    if (start === Infinity) continue;
    const slice = c.slice(start);
    try {
      return JSON.parse(slice);
    } catch {
      // try trimming to last closing brace/bracket
      const lastBrace = Math.max(slice.lastIndexOf('}'), slice.lastIndexOf(']'));
      if (lastBrace > 0) {
        try {
          return JSON.parse(slice.slice(0, lastBrace + 1));
        } catch { /* next */ }
      }
    }
  }
  return undefined;
}

/** Credit cost model: 1 credit ≈ $0.004 raw API cost, minimum per-call floors. */
export function toCredits(costUsd, floor = 1) {
  return Math.max(floor, Math.ceil(costUsd / 0.004));
}

// Rough pre-estimates used to LOCK credits before a pipeline runs.
export const ESTIMATES = {
  blueprint: 8,     // architect call
  expand: 14,       // characters + full outline
  chapter: 30,      // outline+draft+continuity+edit+score(+quality rewrite)+memory
  action: 6,        // single rewrite/continue/improve call
};
