# Glint AI — Go Live Checklist (PayPal + Supabase)

This guide turns the MVP into a site that can **take recurring payments**
(PayPal Subscriptions) and **manage accounts** (Supabase). Everything is wired
in `supabase-auth.js` and `api/paypal-webhook.js` — you only fill in keys and
click a few buttons in the two dashboards. No backend code to write.

---

## 0. What you need (free tiers are fine)
- A **PayPal Business** account — https://www.paypal.com
  - *China:* must be registered under a business license (company **or 个体工商户 / sole proprietor**). A personal account cannot create subscriptions or receive business payments. (a personal account
  can't create subscriptions; upgrade or open a business account)
- A **Supabase** project — https://supabase.com (free tier)
- A static host: **Vercel** or **Netlify** (for the site + the webhook function)

---

## 1. Supabase — project + table + keys
1. Create a project. Copy **Project URL** and **anon public key** from
   *Settings → API*.
2. In *SQL Editor*, run:

   ```sql
   create table if not exists profiles (
     id uuid primary key references auth.users(id) on delete cascade,
     email text,
     paypal_email text,
     plan text default 'free',
     sub_status text default 'free'
   );
   alter table profiles enable row level security;
   create policy "users read own profile"
     on profiles for select using (auth.uid() = id);
   ```

3. Paste the URL + anon key into `supabase-auth.js`:
   ```js
   const SUPABASE_URL = 'https://XXXX.supabase.co';
   const SUPABASE_ANON_KEY = 'eyJ...';
   ```

---

## 2. PayPal — business account, subscription plans (China / 贝宝支付)
1. 登录 PayPal 中国企业账户（贝宝支付）。进入 **收付款 → 定期付款**。
2. 创建两个定期付款计划：
   - **Glint AI Pro — $9.00 USD / 每月**（无开户费、无试用期）
   - **Glint AI Team — $29.00 USD / 每月**
3. 每个计划创建完成后，PayPal 会生成一段 **JS SDK 订阅按钮代码**，里面包含：
   - `client-id=BA...`（复制这串）
   - `plan_id: 'P-...'`（复制这串）
4. 把这两段填进 `supabase-auth.js`：
   ```js
   const PAYPAL_CLIENT_ID = 'BAAXQXi1...';   // 从 SDK 代码的 client-id 复制
   const PAYPAL_PLANS = {
     pro:  'P-8JY348393B145582ENJ2IRFQ',     // 从 SDK 代码的 plan_id 复制
     team: 'P-XXXXXXXXXXXXXXXXXXXX'          // Team 计划的 plan_id
   };
   ```
   填好后，定价卡片会自动隐藏占位 CTA、渲染真实 PayPal 订阅按钮。
5. 另外记下 **PayPal Developers → My Apps & Credentials** 里 App 的
   `PAYPAL_CLIENT_SECRET`（webhook 校验用，见第 3 步）。

> 注：PayPal 中国版走的是「JS SDK 订阅按钮」集成（不是国际版的 shareable link）。
> 代码已经按这个方式写好，你只需填 client-id 和 plan_id。

---

## 3. PayPal webhook → Supabase (so Pro actually unlocks)
1. In *PayPal Developers → Webhooks*, add an endpoint pointing at your deployed
   function URL (`https://your-site.vercel.app/api/paypal-webhook`).
   - Subscribe to: `BILLING.SUBSCRIPTION.ACTIVATED`, `...CANCELLED`,
     `...EXPIRED`, `...SUSPENDED`, `...PAYMENT.FAILED`.
   - Copy the **Webhook ID** (`WH-...`).
2. In Supabase *Settings → API*, copy the **service_role** key (server-only).
3. Deploy `api/paypal-webhook.js` to your host and set these env vars there:
   ```
   PAYPAL_CLIENT_ID=...
   PAYPAL_CLIENT_SECRET=...
   PAYPAL_WEBHOOK_ID=WH-...
   PAYPAL_MODE=sandbox        # switch to "live" after testing
   SUPABASE_URL=https://XXXX.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   ```
4. **Test in sandbox first**: use a PayPal sandbox buyer account to subscribe,
   confirm the function logs `received:true` and the `profiles.plan` flips to
   `pro`. Then set `PAYPAL_MODE=live`.

Now when a user pays, the webhook writes `plan='pro'` to their `profiles` row,
and the site shows "Open app" instead of "Get Pro".

---

## 4. Newsletter (capture emails)
The form currently stores to `localStorage` as a placeholder. To capture real
emails, point it at an email provider:
- **Formspree:** set the form `action` to your Formspree endpoint and `method="POST"`.
- **Or** post to your own API route that adds the email to Supabase / Mailchimp.

---

## 5. Local preview vs. live
- Locally you'll see the UI (login modal, pricing buttons). Payments and auth
  need the real keys above — fill them and deploy to test end-to-end.
- Until keys are set, buttons show a friendly "configure me" hint instead of
  breaking.

---

## Deploy (one minute)
Push the folder to Vercel/Netlify (drag-drop or git). The static site + the
`api/` function deploy together. Set env vars, done.

---

## 中国主体落地清单（China-specific）

你选了"国内公司/个体户 + PayPal 中国 Business"起步。按这个顺序走：

1. **主体**：注册**个体工商户**（最省事，无注册资本、税务最简）或一人有限公司。
   - 渠道：当地政务服务网 / 市场监管局线上办，或找代理（约 300–800 元）。
   - 材料：经营者身份证、经营场所证明。时间 1–3 天，官费基本为 0。
2. **银行**：开个体户结算户或对公户，用于绑定 PayPal 收款提现。
3. **PayPal 中国 Business**：用营业执照注册，完成商家认证，在 *Developers → My Apps & Credentials* 拿到 `PAYPAL_CLIENT_ID` / `PAYPAL_CLIENT_SECRET`。
4. **订阅计划**：收付款 → 定期付款 建 Pro $9.99/月、Team $29/月，从生成的 SDK 代码复制 `client-id` 与两个 `plan_id`，填进 `supabase-auth.js` 的 `PAYPAL_CLIENT_ID` / `PAYPAL_PLANS`。
5. **部署**：填 `api/paypal-webhook.js` 的环境变量（见第 3 步），sandbox 先测一笔再切 live。
6. **提现 / 结汇**：PayPal 提国内银行每笔约 $35 + 中间行费；银行会要求做"跨境服务贸易收入"申报（备服务合同/发票，可自制）。量大可走 PingPong / 万里汇等跨境收款平台（需公司主体，费率更低）。
7. **税务**：个体户按"经营所得"申报，找代账约 2000 元/年；小规模纳税人月销售额 ≤10 万免征增值税，年应纳税所得额 ≤300 万企业所得税实际 5%。
8. **欧盟 VAT**：向欧盟 / 英国用户收款另涉 VAT，PayPal 不代交。前期小额可暂缓；做大了走 Paddle / Lemon Squeezy（MoR，替你交全球税）更省心（需有主体签合同）。

**注意**：以上为通行做法框架，非税务 / 法律意见。金额做大前建议咨询跨境财税顾问。
