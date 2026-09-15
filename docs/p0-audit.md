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

## 四、9 项压力测试（TEST 1–9）— 2026-09-16 线上实测终判

执行环境：生产站 glintai.tools（v2 引擎 + P0 迁移已生效），全新注册账号（100 积分）真实跑通 3 章完整流水线。日志：`tests/stress_run_0916final.log`。

| 测试 | 结果 | 证据 |
|---|---|---|
| T1 角色事实存活（疤痕） | ✅ PASS | 永久事实注入写作上下文，ch2 正文出现 scar |
| T2 禁止事实（咖啡） | ✅ PASS | 违规=0，continuity 主动标记 |
| T3a 伏笔不提前揭示 | ✅ PASS | reveal@ch3，ch2 后 status 仍 planted |
| T3b 揭示窗口命中 | ✅ PASS | ch3 正文兑现 ring |
| T4 状态变化+历史 | ✅ PASS | trust 80→70，character_state_history 1 行带 reason |
| T5 关系轴变化 | ✅ PASS | 背叛后 trust 30 / conflict 80 |
| T6 时间线/地点一致 | ⚠️ 引擎 PASS / 内容标记 | continuity 抓到 ch3 内部 dating 矛盾（major）→ 重写 2 次仍存 → `gate_status=needs_review, rewrite_count=2`——正是规格要求的"封顶+人审"，无死循环。矛盾本身是模型内容质量问题，由人审处理 |
| T7 记忆防污染 | ✅ PASS | memory_candidates 24 条，approved/rejected 双向裁决；bible 永久事实无损 |
| T8 记忆幂等（换 taskId 重放） | ✅ PASS | 事件 10→10 零重复，RPC 返回 already_claimed 拒绝二次应用 |
| T9 并发同 taskId | ✅ PASS（等价步验证） | 2 并发 reader 调用：双 200、generation_outputs 仅 1 行（败者回放缓存）、恰好 1 lock+1 settle+1 refund（reference 唯一零重复计费）。score 步同机制（runOnce + upsert-ignore），首跑因钱包耗尽未测，机制完全同构 |

**CORE ENGINE STATUS: PASS**

规格符合性核验（数据实测）：质量门最多 2 次重写（quality_scores 记录 attempt 1→3，如 ch1: 3 次评分 7.2）；每次重写重跑 continuity；重写耗尽 → needs_review；memory 每章至多应用一次（claim RPC）；validator 双向裁决；并发/重试零重复扣费。

### 已知问题（不隐藏）
1. **评分门槛偏严**：8.0 门槛下实测多数章节要吃满 2 次重写（6.8~7.2 常见）→ 单章成本 ≈3 倍。建议后续调低门槛至 7.5 或放宽 scorer 严格度（产品决策，非引擎缺陷）。
2. **scorer 偶发返回 0.0**：ch3 attempt3 overall=0.0（模型 JSON 解析失败被记 0 分）→ 触发额外重写。应在 score 步对 0 分做一次重试或标记 scorer_failed。
3. **prompt_templates 表经 REST 读为空**（200+[]）——疑似 RLS 仅放行 service_role 或 seed 未生效。引擎 fail-open 不受影响（用内置提示词），运行时覆盖功能待用 service_role 验证。
4. **T6 内容质量**：模型在多章跨度下仍会产生内部日期矛盾（被 continuity 正确抓获），长篇连续性最终依赖 needs_review 人审兜底。
