# Glint Fiction — P0 审计与修复报告（CURRENT P0 AUDIT）

审计对象：`api/fiction/generate.js`（修复前版本）、`api/_lib/retrieval.js`、`api/_lib/prompts.js`、`api/_lib/credits.js`、`supabase-fiction-schema.sql`、Pipeline 全链路。
修复落点：`api/fiction/generate.js`（全量重写 v2）、`supabase-fiction-migration-p0.sql`（新增）。

## 一、审计发现（修复前）

| # | 问题 | 文件 | 位置/机制 | 严重度 | 修复方案 | 状态 |
|---|------|------|-----------|--------|----------|------|
| A1 | Rewrite 后直接进 Memory，无二次评分 | generate.js | 旧 `rewrite` 步返回 `nextStep:'memory'` | 🔴 P0 | gate 闭环：rewrite→continuity→edit→score，最多 2 次重写 | ✅ 已修 |
| A2 | Continuity verdict 不控制流程 | generate.js | 旧 `continuity` 恒返回 `nextStep:'edit'` | 🔴 P0 | high(critical/major) 未达重写上限→强制 rewrite；仅 minor→edit | ✅ 已修 |
| A3 | Memory 无验证，AI 错误可永久污染圣经 | generate.js | 旧 `applyMemory()` 直写 bible | 🔴 P0 | memory_candidates + memory_validator，仅 approved 入库 | ✅ 已修 |
| A4 | Memory 非幂等：重试重复插入 timeline/事件 | generate.js | 旧 `applyMemory()` 直接 insert | 🔴 P0 | claim_chapter_memory RPC（首写获胜）+ source_task_id 唯一索引 + 状态历史唯一约束 | ✅ 已修 |
| A5 | 检索按创建顺序 LIMIT，非相关性 | retrieval.js | characters LIMIT 14 等裸查询 | 🔴 P0 | 结构化相关性评分（本章计划角色 +5 / 伏笔揭示窗口 +6 / 主角 +2 / 近期登场 +2），优先级 > created_at | ✅ 已修 |
| A6 | 伏笔不随章节提升优先级，无揭示闸门 | retrieval.js | 无 planned_reveal 逻辑 | 🟠 P0 | foreshadowPriority()：距揭示 ≤5 章 +6、≤15 章 +3、过期 −4；DO NOT REVEAL 门控 | ✅ 已修 |
| A7 | 任务 insert 并发竞争 | generate.js | A/B 同时 insert，无冲突处理 | 🔴 P0 | upsert ignoreDuplicates + 重查，双方共享同一任务行 | ✅ 已修 |
| A8 | 步骤可并发重复执行（双倍生成+双倍扣费） | generate.js | 无步骤级声明 | 🔴 P0 | generation_outputs 唯一索引 (task_id, kind) + runOnce() 缓存回放 | ✅ 已修 |
| A9 | used_credits 只在 finishStep 落库，重试结算失真 | generate.js | charge() 仅改内存 | 🟠 P0 | charge() 立即 update 数据库 | ✅ 已修 |
| A10 | quality_scores 无 attempt_no，重写分数覆盖语义不明 | schema | 无该列 | 🟡 P0 | attempt_no 列 + (novel,chapter,attempt) 唯一索引 | ✅ 已修 |
| A11 | 关系只有 trust/attraction/conflict | schema/prompts | — | 🟡 P0 | 全轴支持（trust/love/attraction/anger/fear/suspicion/jealousy/intimacy/conflict/respect），只写变化字段 | ✅ 已修 |
| A12 | 永久事实与滚动事实混存，永久事实可被截断 | generate.js | `slice(-200)` 无差别截断 | 🟠 P0 | bible.permanent_facts 独立存储、永不截断；important_facts 滚动窗口 | ✅ 已修 |
| A13 | 人物状态无历史，无法做 Character Arc | schema | 仅 current_state | 🟡 P0 | character_state_history 表（每章快照+增量+原因+任务源） | ✅ 已修 |
| A14 | credits 重复扣费 | credits.js | lock/settle/refund 均按 unique(reference) 幂等 | 🟢 低危 | 保持；配合 A8 步骤幂等彻底封死 | ✅ 复核通过 |
| A15 | outline 步用内联提示词未走 agent 注册表 | generate.js | 硬编码 system | 🟢 低危 | 保持（功能正常，非 P0），注册表覆盖仍生效于其他 12 个调用点 | 📝 记录在案 |

## 二、修复后 Pipeline（generate.js v2 状态机）

```
Story Bible
→ 相关性检索 (P0-7: 本章角色/主线/揭示窗口伏笔/最近摘要/critical 时间线)
→ outline → draft
→ continuity ── fail(high) 且重写<2 → rewrite ──┐
│                否则 → edit                      │ (回到 continuity)
→ edit (edit_a{rc})                               │
→ score (score_a{rc}, attempt_no=rc+1)           │
     score<8 且重写<2 → rewrite → continuity ─────┘
     score<8 且重写=2 → memory (gate_status=needs_review)
     score≥8 → memory
→ memory: memory_updater 出候选 → memory_validator 逐条裁决(存 memory_candidates)
         → claim_chapter_memory RPC(首写获胜, 幂等) → 仅 approved 事实入 bible
         → 人物状态增量+历史 / 全轴关系 / timeline(source_task_id) / 线索 / 伏笔
         → chapters.gate_status = approved|needs_review
→ 结算积分（实际用量, 一次性）
```

## 三、数据库变更（supabase-fiction-migration-p0.sql，幂等可重复执行）

- 新表：`memory_candidates`（novel/chapter/task/type/content/confidence/status/validator_note）
- 新表：`character_state_history`（唯一约束 novel+character+chapter；state/state_deltas/reason/source_task_id）
- 新列：`timeline_events.source_task_id` + 部分唯一索引 (novel,chapter,source_task_id,event)
- 新列：`quality_scores.attempt_no` + 唯一索引 (novel,chapter,attempt)
- 新列：`chapters.gate_status`、`chapters.rewrite_count`
- 新 RPC：`claim_chapter_memory()` — 原子声明，同章 memory 至多应用一次
- 新索引：`generation_outputs (task_id, kind)` 唯一（步骤级幂等，先去重旧数据）
- RLS：两新表按 novels.user_id 归属（与基础 schema 同模式）
- seed：prompt_templates 注册 memory_validator / reader_simulator / reviser / action

## 四、9 项压力测试（TEST 1–9）

⚠️ 前置：迁移 SQL 需在 Supabase Dashboard → SQL Editor 执行（本环境无 DDL 权限）。执行后按 tests/p0-stress.md 跑全量验证，结果将回填本节。
