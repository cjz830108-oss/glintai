# Glint AI 项目扫描报告（10 点）— 升级前现状

> 按用户 point 43 要求：先扫描整个项目，再开始修改。本报告为**修改前的现状基线**，后续所有改动都以此为准。
> 扫描时间：2026-08-12 · 项目根：`/c/Users/Administrator/WorkBuddy/2026-08-06-17-48-44`

---

## 1. 当前项目结构

```
/ (根)
├── index.html              首页（1130 行，单文件，含全部 16 工具交互 + 博客网格 + 登录弹窗）
├── tools/                  16 个工具独立 SEO 落地页（/tools/<slug>.html）
│   ├── ai-humanizer.html … background-remover.html（均由 gen_tool_pages.py 生成）
├── blog/                   34 篇 SEO 长文（含 Aug 13 / Aug 26 两批）
│   └── assets/             博客配图 + 缩略图（各 34 张 hero png + 34 张 thumb）
├── api/                    3 个 Vercel 服务函数
│   ├── paypal-webhook.js   校验 PayPal 签名 → 写 profiles.plan（已可投产）
│   ├── supabase-proxy.js   /api/sb 反向代理（绕 GFW，免 Supabase Pro）
│   └── stripe-webhook.js   ⚠️ 弃用残留（无害）
├── assets/                 tools.css / tools.js（工具页样式与脚本）
├── vendor/                 supabase.min.js（本地兜底）
├── supabase-auth.js        前端：Supabase 认证 + PayPal JS SDK 订阅按钮
├── supabase-schema.sql     profiles 表 + trigger + RLS
├── gen_tool_pages.py       生成 16 工具页的脚本（PANELS + TOOLS 双数据源）
├── package.json / vercel.json / robots.txt / sitemap.xml / icon.svg
├── _specs/  drafts/  reports/   内容管线工作文件（非线上站点，可忽略）
└── p2-tools.js             独立语法检查 JS（未在主页引用）

部署：Vercel 自动部署（`git push` → `cjz830108-oss/glintai` 的 main）。
线上域名：https://glintai.tools（CNAME 指向 Vercel）。
```

## 2. 当前使用的技术

- **纯静态多页 HTML 站点**，无构建系统 / 无框架 / 无 Bundler。
- 首页 `index.html` 内联 `<style>` + 原生 `<script>`（vanilla JS 工具逻辑 + Supabase/PayPal 桥接）。
- 工具逻辑：100% 客户端（正则/启发式/本地 pdf.js），**无后端 AI 调用**（"Pro AI" 目前是占位承诺）。
- 认证：Supabase Auth，经同源代理 `/api/sb`（避免 `*.supabase.co` 被 GFW 拦截，且免 $25 Pro）。
- 支付：PayPal Subscriptions（JS SDK 订阅按钮）+ 服务端 webhook 回写 `profiles.plan`。
- 样式：赛博朋克暗色（`--bg #07070d` / `--brand #00f0ff` / `--brand-2 #ff2e97`），通过覆盖 `:root` 变量 + `cyberpunk override` 块实现，HTML 结构与 JS 逻辑未动。
- 图片生成：Agnes AI（出图）+ Pillow 后处理（去水印/裁切）。

## 3. 当前哪些功能已经完成（真实可用）

| 模块 | 状态 |
|---|---|
| 16 个免费工具（前端交互） | ✅ 全部真实可用（humanize/paraphrase/detect/grammar/pdf/summarize/readability/md/json/pw/yt/hash/serp/wc/bio/bg） |
| 工具 SEO 落地页（16 个） | ✅ 独立 URL、双 JSON-LD、canonical、OG |
| 博客系统（34 篇） | ✅ 独立页 + 互链成网 + sitemap |
| Supabase 认证骨架 | ✅ email+密码 / Magic Link / 登出 / 会话恢复 |
| PayPal 订阅骨架 | ✅ JS SDK 按钮渲染 + webhook 服务端校验（已配 6 个环境变量） |
| 赛博朋克视觉 | ✅ 全局一致 |
| robots.txt / sitemap.xml | ✅ 51 URLs |
| 隐私承诺（无追踪） | ✅ 当前确实无分析/追踪脚本 |

## 4. 哪些功能是假实现 / 占位（重点整改对象）

1. **"Pro AI 能力"全部是占位文案**：摘要/背景移除等工具写"Pro unlocks GPT-level"，但**无任何真实 AI 调用、无用量系统、无配额、无 paywall 触发**。
2. **PayPal 收钱链路从未实测跑通**：基础设施齐全，但"用真实交易把 `profiles.plan` 翻 pro"这一环被跳过两次，webhook 内部匹配逻辑可能藏 bug。
3. **定价与 PayPal 计划价不符**：页面写 Pro $9/mo，PayPal 实际计划 `P-8JY348393B145582ENJ2IRFQ` 是 $9（非 $9.99）；**年付 $79 / Team 计划未配置**。
4. **无 /tools、/extension、/resources、/dashboard、404 页面**（nav/footer 多处 `#` 死链）。
5. **无 Google 登录**（只有 email+密码 + Magic Link）。
6. **无广告占位、无分析（隐私友好）、无联盟/affiliate 页**。
7. **无客户端用量计数器 / 内联 paywall**（当前付费入口是粗暴的"Get Pro"锚点）。
8. **Team 计划** 文案写"Contact sales"，但用户新需求是 "Coming soon"——需改。
9. **blog 配图/缩略图 34 套**已存在，但首页博客网格仅展示 34 张中的部分（已全量 34 张）。

## 5. 哪些地方需要修改（按 point 41 优先级）

**P0（优先）**
- Homepage：定位/hero 重写（"everyday AI toolkit for creators & marketers" + tagline）。
- 16 工具按 **6 大分类** 重组；首页只展示 6 个 Most Popular + 分类浏览 + Explore All Tools → /tools。
- Pricing 重设计：Free $0 / Pro **$9.99/mo + $79/yr (Save 34%)** / Team **$29 Coming soon**。
- 新增 /tools（全工具交互页）、/extension（Coming soon + waitlist）、/resources + /ai-tools（affiliate）、/dashboard（登录门禁）、404。
- Nav / Footer 重构 + **Google 登录**。
- 统一用量计数器 + **内联 paywall（非报错）**。
- Humanizer/Detector 合规文案（"make AI writing sound natural"，**绝不写 bypass detectors**）。
- DB 增字段（用量/订阅周期）；Supabase 配 Google OAuth + redirect URLs；PayPal 配年付计划 + 价格对齐。
- sitemap/robots 增加新页面；工具页↔博客↔新页互链。

**P1**
- 广告占位、隐私友好分析占位、Admin 看板思路、移动端/性能复核、authenticity（不堆假数据）。

## 6. 哪些地方不能动（保命清单）

- **所有现有工具 URL**（`/tools/<slug>.html`）、**所有博客 URL**（`/blog/*.html`）——SEO 权重沉淀，改动即掉排名。
- **SEO 元数据体系**：canonical / OG / Twitter / WebSite+Organization+FAQPage+SoftwareApplication JSON-LD / breadcrumb——保留并延伸到新页。
- **赛博朋克视觉系统**（`:root` 变量 + override 块）——只覆盖变量，不重写结构。
- **`api/paypal-webhook.js` 的服务端签名校验逻辑**——绝不信任前端成功回调。
- **`/api/sb` 代理**与 Supabase anon key / PayPal client-id（已填，勿误清）。
- **`gen_tool_pages.py` 的 PANELS/TOOLS 数据源**——新增工具走脚本，不手工改产物。
- **隐私立场**：保持"默认无追踪"，分析必须隐私友好（不引入 GA 级追踪）。

## 7. 数据库需要增加哪些字段（profiles 表）

```sql
-- 在现有 id/email/plan/sub_status/paypal_email/created_at 基础上增加：
ai_credits_used    int   default 0,      -- 当期已用 AI 额度
ai_credits_limit   int   default 50,     -- 免费档月度额度（Pro 视为无限）
pdf_pages_used     int   default 0,
pdf_pages_limit    int   default 20,
exports_used       int   default 0,
period_start       timestamptz default now(),  -- 月度重置锚点
subscription_period text,                -- 'monthly' | 'yearly' | null
subscription_end   timestamptz,          -- 到期日（用于续费/降级判断）
google_id          text,                 -- Google OAuth subject（可选）
last_seen          timestamptz
```
> 免费档用量优先 localStorage 计数 + 月度重置；Pro 由 webhook 写 `plan='pro'` + `subscription_end` 解锁无限。RLS 策略需覆盖新字段（仅本人/服务角色可读写）。

## 8. PayPal 需要什么配置

- **Pro 月付**：现有 `P-8JY348393B145582ENJ2IRFQ` 实为 **$9**，页面将显示 **$9.99** → 需在 PayPal 后台把该计划价格改为 $9.99，或新建 $9.99 计划并更新 `PAYPAL_PLANS.pro`。
- **Pro 年付 $79（Save 34%）**：**需新建年度订阅计划**，拿到 plan_id 填入 `PAYPAL_PLANS.pro_yearly`（当前为空占位）。
- **Team $29**：新需求为 "Coming soon" → 前端隐藏购买按钮、显示等待列表，暂不启用 `P-5C811609NL238632RNJ2ITIA` 购买。
- **Webhook**：确认后台 webhook 投递 URL = `https://glintai.tools/api/paypal-webhook`（无 .js），订阅事件含 `BILLING.SUBSCRIPTION.ACTIVATED / UPDATED / CANCELLED / PAYMENT.SUCCEEDED`。
- 6 个环境变量已设（CLIENT_ID/SECRET/WEBHOOK_ID/MODE/SUPABASE_URL/SERVICE_ROLE_KEY），无需重设。

## 9. Supabase 需要什么配置

- **启用 Google  provider**：Authentication → Providers → Google → 填 Client ID/Secret（OAuth 应用回调 `https://glintai.tools/api/sb/auth/v1/callback`）。
- **Redirect URLs**：Add `https://glintai.tools/`、`https://glintai.tools/dashboard/`、`https://glintai.tools/extension/`。Site URL = `https://glintai.tools`。
- **运行新 SQL**：`supabase-schema.sql` 追加第 7 节字段 + RLS 调整（见第 7 节）。
- 保持：Email 登录开启、Confirm email 视情况关闭（本地邮箱+密码路径）、服务角色仅用于 webhook。
- `profiles.plan` 匹配逻辑：webhook 按 **付款邮箱 = 登录邮箱** 写入，需向用户强调两邮箱一致。

## 10. SEO 需要修改什么

- **新增页面必须带完整 SEO 头**：唯一 `<title>` / `meta description` / `canonical` / OG / Twitter / JSON-LD（WebSite/Organization 复用；新页加 `BreadcrumbList`）。
- **sitemap.xml** 增加：`/tools/`、`/resources/`、`/extension/`（Coming soon 页可 `noindex` 或先不收录）、`/dashboard/`（登录后页，`noindex`）。保持现有 51 条不动。
- **robots.txt** 保持允许抓取，新增页按需 `Disallow`。
- **内部链接**：工具页 ↔ 博客 ↔ /resources ↔ /ai-tools 互链成网（复用现有 `reports/seo-audit` 思路）。
- **不破坏现有 URL**；新页用新路径，必要时旧锚点 `#tools` 通过 `/tools/` 承接（无需 301，因为旧的是页内锚点非独立 URL）。
- **合规文案**：Humanizer 页面/首页强调 "make AI writing sound natural / more readable"，**删除任何暗示绕过检测器的措辞**（当前文案已较合规，仅微调）。
- **authenticity**：禁止在首页/定价堆"用户数/省钱数"等假指标；只用真实事实（16 tools、free、no signup、no tracking）。
- **structured data 一致性**：新页 JSON-LD 的 `@id` 与 canonical 对齐，避免重复内容被罚。

---
### 下一步
报告已交付。立即进入**修改阶段（Batch 1）**：Homepage 定位/hero + 6 大分类 + /tools 页 + Pricing 重设计 + Nav/Footer + Google 登录 + DB 字段 + sitemap 更新，完成后本地提交（**不 push**，需用户给 fine-grained PAT）。

---

## 用量 / 变现运行时（2026-08-12 追加）

新增 3 个前端模块 + 1 个注入脚本，统一承载「免费→注册→Pro」漏斗与变现占位：

- **`/usage.js`** — 统一用量引擎。维护 `TOOLS` 注册表（slug→函数名+输出元素+类型 ai/pdf/free）。
  - 页面加载后**自动包裹全局工具函数**（无需改任何工具源码）：匿名用户在 localStorage 计数、永不硬拦截（保留 "No signup" 信任点）；登录 Free 用户受 `profiles.ai_credits_limit`(默认50)/`pdf_pages_limit`(默认20) 月度额度限制；超额时在该工具的**输出区渲染行内 paywall 卡片**（非报错），引导 Upgrade / 登录。Pro/Team 无限。
  - 登录用户的用量通过同源代理 `/api/sb` 写回 `profiles`（`ai_credits_used`/`pdf_pages_used`），月度过期自动归零。
  - 匿名用户用满 5 次 AI 后弹出一次性可关闭的「创建免费账号」软提示。
  - 提供 `#glint-usage-banner`（Free 用户显示剩余额度），已置于 `/tools/` 页。
- **`/ads.js`** — 广告占位系统。有 `[data-ad]` 槽位则填充；未配置 `GLINT_ADS_CLIENT` 时渲染带「Advertisement」标签的占位框；工具页自动在首个 `.tool-card` 后注入一个内容广告位。配置 AdSense 后自动加载真实广告。
- **`/analytics.js`** — 隐私友好分析（Plausible，无 cookie）。设置 `window.GLINT_PLAUSIBLE_DOMAIN` 后加载；`usage.js` 通过 `GlintAnalytics.event('tool_used', …)` 上报产品事件。未配置时完全 no-op。
- **`/inject_runtime.py`** — 幂等注入器，已把上述运行时（及工具页所需的 supabase 代理 + auth 弹窗）写入全部页面。重跑安全。

### 激活清单（上线前）
1. **PayPal 价格对齐**：UI 显示 Pro $9.99/mo，但 PayPal 计划 `P-8JY348393B145582ENJ2IRFQ` 实际为 $9。需在 PayPal 后台新建 $9.99/月（及可选的 $79/年）计划，并更新 `supabase-auth.js` 的 `PAYPAL_PLANS.pro`（与 scan 报告第8点一致）。
2. **AdSense**：在页头 `<script>window.GLINT_ADS_CLIENT='ca-pub-xxxx'</script>` 设置发布商 ID。
3. **Plausible**：在页头 `<script>window.GLINT_PLAUSIBLE_DOMAIN='glintai.tools'</script>` 设置域名。
4. **Supabase**：已跑过 `supabase-schema.sql`（含用量字段 + RLS 自更新）。Google OAuth 回调须 = `https://<域名>/dashboard/`。
5. **已知限制**：16 个独立工具页原本无 auth 弹窗，本次已注入 supabase+弹窗，使登录/拦截在全站生效；paywall 的「Upgrade」链接到 `/#pricing`（真实 PayPal 按钮所在），订阅后需刷新 `/tools/` 让 `usage.js` 重新拉取 `plan`。
