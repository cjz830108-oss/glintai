-- =============================================================================
-- Glint Fiction — P0 Migration: long-form stability hardening
-- Run in Supabase SQL Editor (Dashboard → SQL → New query → paste → Run).
-- Idempotent: safe to run twice.
-- =============================================================================

-- ---------------------------------------------------------------------------
-- P0-3) memory_candidates — Memory Updater proposes, Validator disposes.
-- Only status='approved' rows may enter the durable story memory.
-- ---------------------------------------------------------------------------
create table if not exists public.memory_candidates (
  id          bigserial primary key,
  novel_id    uuid not null references public.novels(id) on delete cascade,
  chapter_no  int  not null,
  task_id     text,
  type        text not null,                 -- fact|timeline|thread|foreshadow|relationship|state_delta
  content     jsonb not null default '{}'::jsonb,
  source      text not null default 'memory_updater',
  confidence  numeric(4,2) not null default 0.50,
  status      text not null default 'candidate', -- candidate|approved|rejected
  validator_note text,
  created_at  timestamptz not null default now()
);
create index if not exists memory_candidates_novel_idx on public.memory_candidates (novel_id, chapter_no);

-- ---------------------------------------------------------------------------
-- P0-5) character_state_history — per-chapter emotional state snapshots.
-- current_state stays "latest"; history preserves the arc + the reason why.
-- ---------------------------------------------------------------------------
create table if not exists public.character_state_history (
  id             bigserial primary key,
  novel_id       uuid not null references public.novels(id) on delete cascade,
  character_id   uuid not null references public.characters(id) on delete cascade,
  chapter_no     int  not null,
  state          jsonb not null default '{}'::jsonb,   -- full snapshot AFTER applying deltas
  state_deltas   jsonb not null default '{}'::jsonb,   -- signed deltas applied this chapter
  reason         text,                                  -- "Alexander lied about the missing ring."
  source_task_id text,
  created_at     timestamptz not null default now(),
  constraint character_state_history_unique unique (novel_id, character_id, chapter_no)
);
create index if not exists character_state_history_char_idx on public.character_state_history (character_id, chapter_no);

-- ---------------------------------------------------------------------------
-- P0-4) Memory idempotency
--   a) timeline_events get a source task + per-task/event uniqueness
--   b) atomic claim RPC: the first memory run for (novel, chapter) wins;
--      retries see claim=false and skip re-applying memory.
-- ---------------------------------------------------------------------------
alter table public.timeline_events add column if not exists source_task_id text;
create unique index if not exists timeline_events_task_unique
  on public.timeline_events (novel_id, chapter_no, source_task_id, event)
  where source_task_id is not null;

-- ---------------------------------------------------------------------------
-- P0-9b) generation_outputs — one output per (task, kind): step-level idempotency.
--   Retries / concurrent duplicate step calls replay the cached output instead of
--   re-running (and re-charging) the step. Repeatable steps use attempt-suffixed
--   kinds (score_a1, rewrite_a2, ...) so gate re-passes get their own slot.
--   Dedupe any legacy duplicate rows first (keep the earliest = first execution).
-- ---------------------------------------------------------------------------
delete from public.generation_outputs a
  using public.generation_outputs b
  where a.task_id = b.task_id and a.kind = b.kind and a.id > b.id;
create unique index if not exists generation_outputs_task_kind_unique
  on public.generation_outputs (task_id, kind);

create or replace function public.claim_chapter_memory(
  p_novel_id uuid,
  p_chapter_no int,
  p_summary text,
  p_events jsonb,
  p_state_deltas jsonb
) returns boolean
language plpgsql
security definer
set search_path = public
as $$
declare
  inserted bool;
begin
  -- atomic claim: first writer for (novel, chapter) inserts the summary row;
  -- everyone else gets false and must NOT re-apply memory for this chapter.
  insert into public.chapter_summaries (novel_id, chapter_no, summary, events, state_deltas)
  values (p_novel_id, p_chapter_no, p_summary, p_events, p_state_deltas)
  on conflict (novel_id, chapter_no) do nothing
  returning true into inserted;

  return coalesce(inserted, false);
end;
$$;
grant execute on function public.claim_chapter_memory(uuid, int, text, jsonb, jsonb) to service_role;

-- ---------------------------------------------------------------------------
-- P0-12) quality_scores — track attempts (each rewrite gets a fresh score)
-- ---------------------------------------------------------------------------
alter table public.quality_scores add column if not exists attempt_no int not null default 1;
-- backfill existing duplicates conservatively (keep first as attempt 1)
create unique index if not exists quality_scores_attempt_unique
  on public.quality_scores (novel_id, chapter_no, attempt_no);

-- ---------------------------------------------------------------------------
-- P0-1) chapters — quality gate outcome + generation attempt bookkeeping
-- ---------------------------------------------------------------------------
alter table public.chapters add column if not exists gate_status text;      -- approved|needs_review|null
alter table public.chapters add column if not exists rewrite_count int not null default 0;

-- ---------------------------------------------------------------------------
-- P0-13) story bible — permanent facts are never truncated away
--   data.permanent_facts: [{fact, scope, added_chapter}]  (unbounded, curated)
--   data.important_facts: rolling window (existing behavior, capped)
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- P0-9/11) safety nets
--   (credit_transactions already has unique(reference) — lock/settle/refund
--    idempotency is enforced in code against that constraint.)
-- ---------------------------------------------------------------------------
create index if not exists generation_tasks_novel_active_idx
  on public.generation_tasks (novel_id, status);

-- ---------------------------------------------------------------------------
-- RLS + grants for the new tables (same pattern as base schema)
-- ---------------------------------------------------------------------------
do $$
declare t text;
begin
  foreach t in array array['memory_candidates','character_state_history'] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists %I_owner on public.%I', t, t);
    execute format($f$create policy %I_owner on public.%I for all
      using (exists (select 1 from public.novels n where n.id = %I.novel_id and n.user_id = auth.uid()))
      with check (exists (select 1 from public.novels n where n.id = %I.novel_id and n.user_id = auth.uid()))$f$, t, t, t, t);
  end loop;
end $$;

grant all on all tables in schema public to service_role;
grant all on all sequences in schema public to service_role;
grant select, insert, update, delete on all tables in schema public to anon, authenticated;
grant select, usage on all sequences in schema public to anon, authenticated;

-- ---------------------------------------------------------------------------
-- Seed the new prompt registry rows (bodies live in api/_lib/prompts.js)
-- ---------------------------------------------------------------------------
insert into public.prompt_templates (key, name) values
  ('memory_validator',  'Memory Validator — fact validation before durable memory'),
  ('reader_simulator',  'Reader Simulator — 3-persona chapter reaction'),
  ('reviser',           'Quality Rewriter — gate repair pass'),
  ('action',            'Targeted chapter actions')
on conflict (key) do nothing;

-- ---------------------------------------------------------------------------
-- OPTIONAL (testing only): top up a test wallet.
-- update public.credit_wallets set balance = 500
--   where user_id = (select id from auth.users where email = 'probe.test.glint@gmail.com');
-- ---------------------------------------------------------------------------
