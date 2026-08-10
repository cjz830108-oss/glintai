# Glint AI — 环境变量 & 配置清单（复制粘贴级）

## A. 前端（改 `supabase-auth.js` 顶部常量）
这些是写进浏览器代码的，**不是机密**，但必须先填。

| 常量 | 去哪拿 | 示例 |
|---|---|---|
| `SUPABASE_URL` | Supabase → Settings → API → Project URL | `https://xxxx.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API → anon public key | `eyJ...` |
| `PAYPAL_CLIENT_ID` | ✅ 已填（PayPal 计划 SDK 里的 client-id） | `BAAXQX...` |
| `PAYPAL_PLANS.pro` | ✅ 已填 | `P-8JY3...` |
| `PAYPAL_PLANS.team` | ✅ 已填 | `P-5C81...` |

## B. Serverless 环境变量（Vercel/Netlify 后台设置）
这些是**机密**，绝不进前端代码。

| 变量 | 去哪拿 | 说明 |
|---|---|---|
| `PAYPAL_CLIENT_ID` | PayPal → Developers → My Apps & Credentials → 你的 App | 和前端同一个值 |
| `PAYPAL_CLIENT_SECRET` | 同上 App 页 → 点 Show 显示 Secret | 保密 |
| `PAYPAL_WEBHOOK_ID` | PayPal → Developers → Webhooks → 你的 webhook → ID（形如 `WH-xxxx`） | |
| `PAYPAL_MODE` | 填 `live` 或 `sandbox` | 当前用 `live`（计划与 client-id 均为 Live，事件只发 Live webhook） |
| `SUPABASE_URL` | Supabase → Settings → API | |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → service_role（保密！） | 绕过 RLS，仅供 webhook |
| `SKIP_VERIFY` | 可选 | 仅开发期设 `true` 跳过签名校验，上线必须删掉 |

## B2. Vercel 一键粘贴板（Environment Variables 文本框直接粘）
复制下面整段到 Vercel → Settings → Environment Variables 编辑框（每行 `KEY=VALUE`），
Environment 选 **Production**（或 All）。Save 后点 **Redeploy** 让函数读新变量。

```
PAYPAL_CLIENT_ID=BAAXQXi1cmysWiOuEybXGpWsj1XoEYgQjHjc5z_kW5mHPxKFu45jsRBPWcLhwAUUf0_GueumV1XinIEJpk
PAYPAL_CLIENT_SECRET=<从 PayPal App 页 Show 复制，必填>
PAYPAL_WEBHOOK_ID=8JD66128R2488310G
PAYPAL_MODE=live
SUPABASE_URL=https://czqupmfabemkmtigidiy.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<从 Supabase Settings→API 的 service_role 复制，必填，保密>
```

- `PAYPAL_WEBHOOK_ID`：若后台显示为 `WH-8JD66128R2488310G` 带前缀，请带前缀一起填。
- `PAYPAL_MODE=live`：因订阅计划与 client-id 均为 Live，事件只发 Live webhook，故直接走 live 真测（用另一 PayPal 账号小额订阅 $9 验证后取消/退款）。
- 两个 `<...>` 占位需替换；`service_role` key 切勿写进前端代码或提交仓库。

## C. 一次性 SQL
在 Supabase → SQL Editor 跑一遍 `supabase-schema.sql`。

## D. Supabase Auth 配置
Supabase → Authentication → Providers → 开启 **Email**（勾选 **Magic Link / 密码less 登录**，代码里 `signInWithOtp` 用的就是它；同时 Email+Password 也已支持）。

## E. 部署顺序
1. 跑 SQL（C）
2. 开启 Email / Magic Link 登录（D）
3. 在托管平台设好 B 的环境变量
4. 部署站点 + `api/paypal-webhook.js`
5. PayPal → Developers → Webhooks，把回调地址指到
   `https://<你的域名>/api/paypal-webhook`   // 注意：Vercel 的 function 路由不带 .js 后缀
   并订阅以下事件：
   - `BILLING.SUBSCRIPTION.ACTIVATED`
   - `BILLING.SUBSCRIPTION.CANCELLED`
   - `BILLING.SUBSCRIPTION.EXPIRED`
   - `BILLING.SUBSCRIPTION.SUSPENDED`
   - `BILLING.SUBSCRIPTION.PAYMENT.FAILED`
6. 当前计划与 client-id 均为 Live，直接 `PAYPAL_MODE=live` 用另一 PayPal 账号真订阅一笔 $9 验证（`profiles.plan` 翻 `pro` 后取消/退款）。纯沙盒测法见 F。

## F. 跑通第一笔的注意事项
- **顺序**：先注册/登录（Supabase），再用**同一个邮箱**走 PayPal 付款。
  因为 webhook 按邮箱匹配，没注册的邮箱付款会匹配不到 profile 行。
- **sandbox 测试**：需在 PayPal Developer 另建 sandbox App，拿 sandbox 的
  client-id + 两个 sandbox plan_id，临时替换进 `PAYPAL_CLIENT_ID` / `PAYPAL_PLANS`，
  测完再换回 live 的值。
- 上线前把 `SKIP_VERIFY` 删掉，确保签名校验生效。
