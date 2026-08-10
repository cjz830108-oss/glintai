// Vercel Node Function — Supabase API 反向代理（绕 GFW 封锁，免 $25 Pro）
// 经 vercel.json 的 rewrites 把 /api/sb/* 转到本文件，原始路径放在 ?_path= 里。
// 浏览器只跟你的 Vercel 域名通信（国内可达），由 Vercel 海外节点去连 supabase.co。
export const config = { api: { bodyParser: false } };

// 优先读环境变量 SUPABASE_URL（Vercel 里配置，便于不改代码换项目）；缺省回退到写死的 host
const SB_URL = (process.env.SUPABASE_URL || 'https://czqupmfabeliihtligdy.supabase.co').replace(/\/+$/, '');
// 只转发这些请求头，避免 accept-encoding / content-length / host 等干扰 fetch
const ALLOW_HEADERS = [
  'authorization', 'apikey', 'content-type', 'accept',
  'x-client-info', 'prefer', 'user-agent',
];

export default async function handler(req, res) {
  let targetStr = '';
  try {
    const q = req.query || {};
    let p = q._path || '';
    if (p && !p.startsWith('/')) p = '/' + p;

    const target = new URL(SB_URL + p);
    targetStr = target.toString();
    // 转发原始查询参数（去掉内部用的 _path）
    for (const [k, v] of Object.entries(q)) {
      if (k === '_path') continue;
      if (Array.isArray(v)) v.forEach((x) => target.searchParams.append(k, x));
      else target.searchParams.append(k, v);
    }
    targetStr = target.toString();

    const headers = {};
    for (const h of ALLOW_HEADERS) {
      if (req.headers[h]) headers[h] = req.headers[h];
    }

    const init = { method: req.method, headers };
    if (!['GET', 'HEAD'].includes(req.method)) {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      init.body = Buffer.concat(chunks);
      init.duplex = 'half'; // Node fetch 发送 body 必填
    }

    const r = await fetch(targetStr, init);
    const buf = await r.arrayBuffer();

    // 回传响应头（跳过会被 Node 自动处理的传输类头）
    const SKIP = ['content-length', 'transfer-encoding', 'connection', 'keep-alive', 'content-encoding'];
    for (const [k, v] of r.headers.entries()) {
      if (SKIP.includes(k.toLowerCase())) continue;
      res.setHeader(k, v);
    }
    res.setHeader('access-control-allow-origin', '*');
    res.status(r.status).send(Buffer.from(buf));
  } catch (e) {
    const cause = e && e.cause
      ? (e.cause.code ? `${e.cause.code} ${e.cause.message}` : e.cause.message)
      : '';
    res.status(502).json({
      error: 'Proxy error',
      message: String(e && e.message),
      cause: String(cause),
      target: targetStr,
    });
  }
}
