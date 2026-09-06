# Glint AI → Glint AI 2.0 (AI Fiction Studio) — PROJECT AUDIT & PLANS

Generated: 2026-09-06 · Scope: V1 / P0 implementation

---

# CURRENT PROJECT AUDIT

## 技术栈（实测核实）
| 层 | 现状 | 结论 |
|---|---|---|
| 前端 | 纯静态多页 HTML（无框架、无构建），赛博朋克暗色主题（#07070d/#00f0ff/#ff2e97） | ✅ 保留 |
| 部署 | Vercel，push to main 自动部署，品牌域名 glintai.tools | ✅ 保留 |
| 后端 | Vercel serverless：`api/paypal-webhook.js`（PayPal 订阅）、`api/supabase-proxy.js`、`api/stripe-webhook.js`（弃用残留） | ✅ 保留模式，新增 `api/fiction/*` |
| 依赖 | `package.json` 仅 `@supabase/supabase-js`，type:module | ✅ 够用，**无需新依赖** |
| 数据库 | Supabase（PostgreSQL）：`profiles`（plan/用量字段）+ RLS | ✅ 保留，新增 fiction 表 |
| Auth | Supabase Auth（magic link + 邮箱密码），Site URL 已配 | ✅ 直接复用 |
| 支付 | PayPal 定期付款 JS SDK（Pro $9 plan `P-8JY3…` / Team $29 plan `P-5C81…`） | ✅ 保留；Credits 打包购买列 P1 |
| AI 接口 | 无服务端 AI 调用；工具页全部 client-side 本地运行 | 🆕 新建 Model Router |
| 内容 | 16 工具页 + 98 博客页 + sitemap 122 URL + llms.txt 90 引用 | ✅ 全部保留为 SEO 资产 |
| 分析 | Plausible + ads.js/analytics.js | ✅ 保留 |

## 页面清单（当前）
- `/` 首页（617 行）：定位 "AI toolkit for creators & marketers"，16 工具 + 定价 + FAQ + 博客网格
- `/tools/*.html` ×16 + `/tools/index.html`
- `/blog/*.html` ×97 篇 + `/blog/index.html`
- `/about/`、`/dashboard/`（占位）、`/extension/`（waitlist 占位）、`404.html`

## 可以保留的代码
- supabase-auth.js / 登录弹窗 / PayPal SDK 渲染 —— 原样复用
- paypal-webhook.js —— 原样复用（profiles.plan 逻辑不动）
- 全部 16 工具页 + 98 博客页 + sitemap/llms —— SEO 资产不破坏
- 赛博朋克 CSS 设计语言 —— Studio 沿用同一视觉体系

## 必须重构 / 新建的代码
| 模块 | 动作 |
|---|---|
| Model Router | 🆕 `api/_lib/router.js`（DeepSeek + OpenAI provider，统一 generate/jsonGenerate，失败降级） |
| Prompt Engine | 🆕 `api/_lib/prompts.js`（6 Agent 的全部 prompt 集中服务端管理，版本化常量） |
| Credits 系统 | 🆕 `api/_lib/credits.js`（预估→锁定→结算→释放，事务流水） |
| Memory Retrieval | 🆕 `api/_lib/retrieval.js`（结构化检索：相关角色/状态/关系/伏笔/近章摘要，V1 用 SQL 结构化检索，不上 pgvector） |
| Genre Skills | 🆕 `api/_lib/skills.js`（Romance/Billionaire/Werewolf/Fantasy/Thriller 5 套 genre-level skill 数据） |
| Fiction API | 🆕 `api/fiction/*.js`（novels/blueprint/context/generate/chapter/credits/config） |
| Studio UI | 🆕 `/studio/`（dashboard、new 向导、novel 工作台、章节编辑器、导出） |
| 数据库 | 🆕 `supabase-fiction-schema.sql`（~25 张表 + RLS） |
| SEO | 🆕 6 落地页 + /guides hub + 3 指南（本批已产出）；首页 hero 改版 |

## 可以废弃的代码
- `api/stripe-webhook.js`（7 行弃用残留）—— 本批不动（无害），下批删

## 新系统需要增加的模块
见 "ARCHITECTURE PLAN"。

---

# MIGRATION PLAN（增量，不推倒重来）

原则：静态站壳不动，新增 `/studio` 前端 + `api/fiction` 后端，数据库纯新增表（profiles 只加 credits 列）。

| 阶段 | 内容 | 状态 |
|---|---|---|
| M1 | 审计文档 + 全套 SQL schema | 本批 ✅ |
| M2 | Model Router / Prompts / Credits / Retrieval / Skills（服务端 lib） | 本批 ✅ |
| M3 | Fiction API 端点（novels/blueprint/context/generate/chapter/credits/config） | 本批 ✅ |
| M4 | Studio UI（dashboard / 7 步向导 / 工作台 / 编辑器 / 导出 TXT+DOCX+EPUB） | 本批 ✅ |
| M5 | SEO：6 落地页 + guides + 首页改版 + sitemap/llms | 本批 ✅ |
| M6 | 大哥配置 DEEPSEEK_API_KEY/OPENAI_API_KEY 环境变量 → 线上跑通第一本测试小说 | 待用户 |
| M7 | P1：Continuity 深检 / Reader Simulator / Feedback 面板 / Skills 版本化 / Continue My Novel 导入 | 后续批 |
| M8 | Credits 打包购买（PayPal 新建产品）替换/并存现有 Pro/Team 订阅 | 后续批 |

---

# DATABASE PLAN

新表全部 `user_id` 归属 + RLS 强隔离（`auth.uid() = user_id`），服务端用 service_role 写入。每表含 created_at/updated_at，novels 含 deleted_at（软删）。

核心表（完整 DDL 见 `supabase-fiction-schema.sql`）：
`novels` · `story_bibles` · `characters` · `character_states` · `relationships` · `world_entities` · `timeline_events` · `plot_threads` · `foreshadowing` · `chapters` · `chapter_summaries` · `generation_tasks` · `generation_outputs` · `generation_feedback` · `quality_scores` · `credit_wallets` · `credit_transactions` · `model_usage` · `prompt_templates` · `prompt_versions` · `skills` · `skill_versions` · `skill_metrics` · `user_preferences`

要点：
- Credits 不放 profiles（避免与旧订阅逻辑纠缠）：`credit_wallets(balance int)` + `credit_transactions`（type: grant/lock/settle/refund，reference 唯一防重复扣费）。
- `generation_tasks`：unique task_id 幂等 + status(queued/processing/completed/failed/cancelled) + 锁定金额。
- 章节正文存 `chapters(content text)`，摘要存 `chapter_summaries`（Memory Retrieval 主数据源）。

---

# ARCHITECTURE PLAN

```
浏览器 /studio/*.html
  │  fetch + Bearer<supabase access_token>
  ▼
api/fiction/*.js  (Vercel serverless, Node 18+, ESM)
  ├─ _lib/db.js        Supabase admin + 用户鉴权（getUser(jwt)）
  ├─ _lib/router.js    ModelRouter.generate / jsonGenerate（DeepSeek⇄OpenAI 降级）
  ├─ _lib/credits.js   estimate → lock → settle/refund
  ├─ _lib/retrieval.js 章节 ctx：角色+状态+关系+伏笔+线程+近3章摘要
  ├─ _lib/prompts.js   6 Agent prompt 模板（服务端私有）
  └─ _lib/skills.js    5 genre skills
  ▼
Supabase PostgreSQL (RLS + service_role)
  ▼
DeepSeek / OpenAI (env keys, 仅服务端)
```

**长任务策略（适配 serverless 超时）**：章节生成 = 前端驱动的多步流水线，每步一个独立 API 调用并持久化进度：
`outline → draft → continuity → edit → score → memory`
前端显示 Planning…/Writing…/Checking continuity…/Polishing…/Finalizing…。任一步失败可从断点重试（generation_tasks.step 状态机），不重复扣费。

**6 Agent 映射**：Story Architect=blueprint 生成；Character Director=blueprint 角色部分；Plot Planner=chapter outline；Novel Writer=draft；Continuity Editor=continuity 检查；Literary Editor=edit。Reader Simulator=P1。

**模型分工（Model Router 默认表，可改）**：轻任务(title/summary/classify)→DeepSeek；正文创作→DeepSeek(高配)或 OpenAI；深度检查→OpenAI。`MODEL preference` 环境变量可覆盖。

**验收标准（V1 链路）**：注册 → 创建小说 → Blueprint → 角色 → 大纲 → Chapter 1 → Chapter 2 → Continue → Rewrite → 保存 → 重开仍记得人物/剧情/伏笔 → 扣 Credits → Export。线上实测需 DEEPSEEK_API_KEY（或 OPENAI_API_KEY）环境变量 + Supabase 执行新 SQL。

---

# 环境变量（新增，部署前必须配置）
| 变量 | 用途 |
|---|---|
| `DEEPSEEK_API_KEY` | 主力创作模型（缺省时自动降级 OpenAI） |
| `OPENAI_API_KEY` | 备用/深度检查模型 |
| `SUPABASE_ANON_KEY` | studio 前端登录用（api/fiction/config.js 下发） |
已存在复用：`SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`。
