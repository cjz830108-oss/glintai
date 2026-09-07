# CURRENT SYSTEM AUDIT — Glint AI Fiction Engine V1
> 2026-09-07 · 基于代码逐文件核实（api/_lib ×7、api/fiction ×10、studio ×7、schema SQL ×1、index.html），非记忆推测。
> 线上状态：`/api/fiction/config` = **503 not_configured** → 整个 Fiction Studio 后端当前**不可用**。

---

## 0) 一句话结论
**引擎的"骨架和记忆系统"是真的，且质量不错；但它现在是一台没通电的机器**——数据库没建、环境变量没配，0 个用户能写小说。同时商业模型（Credits）与购买路径断裂、质量门/读者模拟器缺失、免费漏斗断链、首页残留开发提示。

---

## 1) 真实实现 ✅（有后端逻辑、非 UI 假象）

| 模块 | 证据 | 状态 |
|---|---|---|
| Story Memory 结构化检索 | `api/_lib/retrieval.js`：并行查询 7 类表 → 组装 12 类上下文（bible/角色+状态/关系/活跃线索/伏笔/最近3章摘要/critical时间线/style guide/genre skill/anti-AI/facts/forbidden），预算 ~4k tokens，**从不塞全文** | ✅ 真实，符合 spec §四 |
| Chapter 6 步管线 | `api/fiction/generate.js`：outline→draft→continuity→edit→score→memory，客户端驱动、可断点续跑、taskId 幂等、abort 全额退款 | ✅ 真实 |
| Memory 回写 | `generate.js applyMemory()`：章摘要、角色状态 signed deltas（clamp 0-100）、关系更新、时间线、线索状态、伏笔状态、bible facts（cap 200）、open questions | ✅ 真实，Character Memory 会随剧情演变 |
| Blueprint 三步 | `novels.js`(architect) + `blueprint.js`(approve/regenerate/**expand**: 角色总监→落库 cast+关系+世界+线索+伏笔；剧情规划→full chapter_plan 存 bible) | ✅ 真实 |
| Credits 账本 | `_lib/credits.js`：wallet ledger、lock→settle→refund、unique reference 幂等、注册赠 100 | ✅ 真实（但见 §3-6 断裂） |
| Model Router | `_lib/router.js`：deepseek+openai、light/creative/deep 三档、失败自动 fallback、JSON mode、token 成本核算、`model_usage` 落库 | ✅ 真实（模型名过时，见 §3-8） |
| 8 个 Agent Prompt | `_lib/prompts.js`：architect/character_director/plot_planner/novel_writer/continuity_editor/literary_editor/quality_scorer/memory_updater，全部服务端、版本号 1.0.0 | ✅ 真实（缺 Reader Simulator，见 §3-2） |
| 数据隔离 | 每端点 `requireUser`(JWT 验证) + `ownNovel`(所有权) + schema 全表 RLS defense-in-depth | ✅ 真实，A/B 用户不可能互串 |
| AI 章内动作 | `chapter.js`：continue/improve/more_emotional/improve_dialogue/shorten/expand/change_pov + 作者备注，带 story context | ✅ 真实 |
| Export | `studio/export.js`：TXT/DOC/EPUB（零依赖 zip writer：CRC32+stored，含 OPF+NCX） | ✅ 真实（PDF/Kindle EPUB 缺） |
| Continue My Novel | `import.js`：TXT 分章入库 → 采样首2+中1+末2章 → deep 模型逆向提取 bible（角色/关系/世界/线索/伏笔/时间线/facts）→ 逐章摘要 → 续写 | ✅ 真实（DOCX/EPUB/PDF 输入缺） |
| Free Generator | `free.js`：无注册 3次/IP/天（内存限流） | ✅ 真实但漏斗断链（§3-5） |
| Genre Skills | `skills.js`：romance/billionaire_romance/werewolf/fantasy/thriller 五套结构化技能 + ANTI_AI_RULES | ✅ 真实（代码版；DB skills 表未 seed） |
| Studio UI | 左侧 8 区（Overview/Bible/Characters/World/Plot/Timeline/Foreshadowing/Chapters）+ 自动保存 + 👍👎反馈 | ✅ 真实（Memory Panel 弱，§3-4） |

## 2) 只有 UI / 断裂 / 假功能 ⚠️

1. **整条后端没通电**：Vercel 缺 `DEEPSEEK_API_KEY`/`OPENAI_API_KEY`/`SUPABASE_ANON_KEY`，Supabase 未跑 `supabase-fiction-schema.sql`（23 张表）。**线上目前 0 用户能创建小说**。
2. **首页定价区还是旧工具站商业模型**：Free/$9 Pro/$29 Team（月费+PayPal 订阅），与 Studio 的 Credits 体系完全脱节。Pro 权益文案（"GPT-level summaries/Chrome extension"）是旧站文案。
3. **Credits 无法充值**：wallet 只有注册赠 100，用完后无任何购买入口。PayPal webhook 只翻 `profiles.plan`，不给 wallet 加 credits → **商业模式断链**。
4. **首页 footer 开发提示泄露**（index.html:577）："Payments via PayPal · Accounts via Supabase — configure in supabase-auth.js (see SETUP.md) to go live" —— 违反 spec §二十九。
5. **supabase-auth.js 被加载两次**（相对+绝对路径各一次，index.html 底部）→ Supabase client 双初始化，潜在重复订阅/事件。
6. **Free 漏斗断链**：生成的故事没有传递到 Studio——CTA 只是裸链接 `/studio/new.html`，idea/genre/正文全丢，用户到向导要重头输入。spec §十九要求"注册→保存 Story→进 Studio"。
7. **Team 计划 "Coming soon"**：占位 CTA（链接 /extension/#waitlist，该页存在=200，不算死链，但属假功能按钮）。

## 3) 缺失（spec 要求但代码里没有）❌

| # | 缺口 | spec 条款 | 优先级 |
|---|---|---|---|
| 1 | **Quality Gate 无重写循环**：score 只记录，无 `overall<8.0→auto rewrite` / `<7.0→regenerate` 逻辑 | §十二 | P0 |
| 2 | **Reader Simulator**：无独立 agent；只有 quality_scorer 的 reader_engagement 单轴 | §十一 | P1（spec 允许后置） |
| 3 | **Continuity 硬门**：verdict=revise 不阻断管线，issues 只软传递给 literary_editor；critical 问题不会触发重写 | §九 STEP13 | P0 |
| 4 | **User Writing Memory 无读写代码**：`user_preferences` 表建了但 new.html 向导不读不写 | §十五 | P1 |
| 5 | **Cliché Detector 不是检测器**：只是 prompt 规则（ANTI_AI_RULES）+ editor 指令，无量化检测/频率统计 | §十三 | P1 |
| 6 | **章节元数据展示不全**：章节卡只有字数+status，无 quality score/角色变化/线索推进/伏笔动作（编辑器里只有 last overall） | §二十三 | P1 |
| 7 | **Memory Panel**：无"What AI remembers"独立面板（Bible 页签部分承担，但弱） | §二十二 | P1 |
| 8 | **模型名过时**：gpt-4o-mini/gpt-4o（spec 写 GPT-5.4/5.4-mini/DeepSeek V4 Flash）；单模型 tier（router.js:36 有 bug 痕迹：`p.models.light && jsonMode ? light : light` 恒为 light，creative/deep tier 实际**没有**按 tier 选模型！） | §十八 | P0（tier 失效=成本错配） |
| 9 | **character_state 无历史快照**：只存最新值（JSONB），spec 要求 per-chapter 记录；历史只能从 chapter_summaries.state_deltas 反推 | §三/§五 | P2 |
| 10 | PDF 导出、Kindle-friendly EPUB | §二十四 | P2 |
| 11 | DOCX/EPUB/PDF 导入（现仅 TXT） | §二十 | P2 |
| 12 | Series Mode（Series Bible 共享） | §二十一 | P3（spec 列为未来） |
| 13 | Delete Story/Account、Privacy Policy、数据所有权声明 | §二十五 | P1（novels 有 deleted_at 软删字段但无 API） |
| 14 | schema 缺字段：novels 无 subgenre/synopsis/tone 完整度、characters 字段塞 JSONB（功能等价、可接受） | §三 | P2 |

## 4) 技术风险 / Bug

1. **router.js:36 tier 选择失效**（上表 3-8）：creative 和 light 都发同一个模型。当前配置下 DeepSeek 便宜所以损失小，但一切到 openai 优先就烧钱。**这是真 bug**。
2. **Vercel Hobby 12 函数上限已满**：api/ 下正好 12 个 handler（paypal-webhook、supabase-proxy + fiction×10）。**新增任何 API 前必须先合并/删除**。
3. `free.js` 内存限流在多实例/冷启动下会漏（已知妥协，注释标明）。
4. `supabase-proxy.js` 硬编码回退 Supabase project host（`czqupmfabelihtligdy.supabase.co`）——project ref 公开（Supabase anon 本来公开，低危）。
5. credits `settleCredits` 里 `bumpWallet(userId, 0, true)` 仅为记 lifetime_spent，settle 事务 amount=0 —— 账本能跑但 lifetime_spent 统计依赖调用顺序，minor。
6. 双重加载 supabase-auth.js（见 §2-5）。

## 5) 距离 Fiction Engine V1 的真实工作量

- **通电**（用户操作：跑 SQL + 配 3 个环境变量 + Redeploy）：0.5 天 → 立即解锁全部已建功能
- **P0 修复**（tier bug、quality gate 硬门、free 漏斗 handoff、首页清理：footer 提示/双加载/旧定价区改 Credits 模式、Credits 充值路径）：2-3 天
- **P1**（Reader Simulator、User Preferences 读写、Memory Panel、章节元数据、隐私/删除、Cliché 量化）：3-5 天
- **P2/P3**（历史快照、PDF/Kindle、多格式导入、Series Mode）：后续迭代

## 6) 最优先行动（PHASE 1 已完成即本审计）
1. **你（用户）**：Supabase SQL Editor 跑 schema → Vercel 加 3 个 env → Redeploy → 告诉我"配好了"
2. **我**：修 router tier bug → quality gate 硬门 + auto-rewrite → free 漏斗 handoff → 首页清理（开发提示/双加载/Credits 定价区）
3. **然后**：跑 spec §三十的三个真实测试（Emma 疤痕 / Alexander 咖啡 / Silver Ring）
