-- ============================================================================
-- Glint AI 2.0 — Fiction Studio schema (V1 / P0)
-- Supabase → SQL Editor → paste all → Run  (idempotent: safe to re-run)
-- Privacy: every table is user-scoped; RLS isolates users; the serverless
-- API uses SERVICE_ROLE (bypasses RLS) only after verifying the caller JWT.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 0) helpers
-- ---------------------------------------------------------------------------
create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
  new.updated_at = now();
  return new;
end $$;

-- ---------------------------------------------------------------------------
-- 1) novels
-- ---------------------------------------------------------------------------
create table if not exists public.novels (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  title         text not null default 'Untitled Story',
  genre         text not null default 'romance',
  length_target int  not null default 30,          -- chapters
  pov           text not null default 'third_limited',
  tone          text not null default 'emotional',
  pacing        text not null default 'balanced',
  idea          text not null default '',
  status        text not null default 'blueprint', -- blueprint|writing|completed|archived
  blueprint     jsonb,                             -- Story Blueprint (approved version)
  chapter_count int  not null default 0,
  deleted_at    timestamptz,
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create index if not exists novels_user_idx on public.novels (user_id);
drop trigger if exists novels_touch on public.novels;
create trigger novels_touch before update on public.novels
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 2) story bible (one row per novel; structured JSON for V1 retrieval)
-- ---------------------------------------------------------------------------
create table if not exists public.story_bibles (
  novel_id   uuid primary key references public.novels(id) on delete cascade,
  data       jsonb not null default '{}'::jsonb, -- world, style_guide, forbidden_facts, important_facts, open_questions, premise...
  version    int not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
drop trigger if exists story_bibles_touch on public.story_bibles;
create trigger story_bibles_touch before update on public.story_bibles
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 3) characters + states + relationships
-- ---------------------------------------------------------------------------
create table if not exists public.characters (
  id             uuid primary key default gen_random_uuid(),
  novel_id       uuid not null references public.novels(id) on delete cascade,
  name           text not null,
  data           jsonb not null default '{}'::jsonb, -- age, appearance, personality[], goals[], fears[], secrets[], speech_style, arc...
  current_state  jsonb not null default '{}'::jsonb, -- {trust,love,anger,fear,suspicion,confidence,jealousy}
  first_chapter  int,
  last_chapter   int,
  active         boolean not null default true,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create index if not exists characters_novel_idx on public.characters (novel_id);
drop trigger if exists characters_touch on public.characters;
create trigger characters_touch before update on public.characters
  for each row execute function public.set_updated_at();

create table if not exists public.relationships (
  id               uuid primary key default gen_random_uuid(),
  novel_id         uuid not null references public.novels(id) on delete cascade,
  from_character_id uuid not null references public.characters(id) on delete cascade,
  to_character_id   uuid not null references public.characters(id) on delete cascade,
  data             jsonb not null default '{}'::jsonb, -- {type, trust, attraction, conflict, status}
  updated_at       timestamptz not null default now()
);
create index if not exists relationships_novel_idx on public.relationships (novel_id);
drop trigger if exists relationships_touch on public.relationships;
create trigger relationships_touch before update on public.relationships
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 4) world / timeline / plot threads / foreshadowing
-- ---------------------------------------------------------------------------
create table if not exists public.world_entities (
  id          uuid primary key default gen_random_uuid(),
  novel_id    uuid not null references public.novels(id) on delete cascade,
  name        text not null,
  type        text not null default 'location', -- location|organization|item|rule|faction
  description text not null default '',
  data        jsonb not null default '{}'::jsonb,
  created_at  timestamptz not null default now()
);
create index if not exists world_novel_idx on public.world_entities (novel_id);

create table if not exists public.timeline_events (
  id          uuid primary key default gen_random_uuid(),
  novel_id    uuid not null references public.novels(id) on delete cascade,
  chapter_no  int,
  event       text not null,
  description text not null default '',
  importance  text not null default 'normal', -- low|normal|critical
  data        jsonb not null default '{}'::jsonb, -- {date, location, characters[], causes[], consequences[]}
  created_at  timestamptz not null default now()
);
create index if not exists timeline_novel_idx on public.timeline_events (novel_id, chapter_no);

create table if not exists public.plot_threads (
  id                 uuid primary key default gen_random_uuid(),
  novel_id           uuid not null references public.novels(id) on delete cascade,
  title              text not null,
  kind               text not null default 'subplot', -- main|subplot|romance|character_arc|mystery|conflict
  status             text not null default 'open',   -- open|advancing|paused|resolved
  start_chapter      int,
  current_chapter    int,
  planned_resolution int,
  data               jsonb not null default '{}'::jsonb, -- {related_characters[], open_questions[]}
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);
create index if not exists plot_threads_novel_idx on public.plot_threads (novel_id, status);
drop trigger if exists plot_threads_touch on public.plot_threads;
create trigger plot_threads_touch before update on public.plot_threads
  for each row execute function public.set_updated_at();

create table if not exists public.foreshadowing (
  id                     uuid primary key default gen_random_uuid(),
  novel_id               uuid not null references public.novels(id) on delete cascade,
  title                  text not null,
  description            text not null default '',
  introduced_chapter     int,
  planned_reveal_chapter int,
  importance             text not null default 'normal', -- low|normal|major
  status                 text not null default 'planted', -- planted|reinforced|revealed|abandoned
  related_characters     text[] not null default '{}',
  resolution             text,
  created_at             timestamptz not null default now(),
  updated_at             timestamptz not null default now()
);
create index if not exists foreshadowing_novel_idx on public.foreshadowing (novel_id, status);
drop trigger if exists foreshadowing_touch on public.foreshadowing;
create trigger foreshadowing_touch before update on public.foreshadowing
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 5) chapters + summaries (memory backbone)
-- ---------------------------------------------------------------------------
create table if not exists public.chapters (
  id         uuid primary key default gen_random_uuid(),
  novel_id   uuid not null references public.novels(id) on delete cascade,
  chapter_no int  not null,
  title      text not null default '',
  content    text not null default '',
  status     text not null default 'draft', -- draft|final
  word_count int  not null default 0,
  version    int  not null default 1,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (novel_id, chapter_no)
);
create index if not exists chapters_novel_idx on public.chapters (novel_id, chapter_no);
drop trigger if exists chapters_touch on public.chapters;
create trigger chapters_touch before update on public.chapters
  for each row execute function public.set_updated_at();

create table if not exists public.chapter_summaries (
  novel_id   uuid not null references public.novels(id) on delete cascade,
  chapter_no int  not null,
  summary    text not null default '',
  events     jsonb not null default '[]'::jsonb,   -- [{event, characters[]}]
  state_deltas jsonb not null default '{}'::jsonb, -- per-character +trust/-fear etc.
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key (novel_id, chapter_no)
);
drop trigger if exists chapter_summaries_touch on public.chapter_summaries;
create trigger chapter_summaries_touch before update on public.chapter_summaries
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 6) generation tasks / outputs / feedback / quality
-- ---------------------------------------------------------------------------
create table if not exists public.generation_tasks (
  id             text primary key,                -- client-generated uuid (idempotency)
  user_id        uuid not null references auth.users(id) on delete cascade,
  novel_id       uuid not null references public.novels(id) on delete cascade,
  kind           text not null,                   -- blueprint|outline|draft|continuity|edit|score|memory|action
  step           text not null default 'queued',  -- current pipeline step
  status         text not null default 'queued',  -- queued|processing|completed|failed|cancelled
  request        jsonb not null default '{}'::jsonb,
  result         jsonb,
  locked_credits int  not null default 0,
  used_credits   int  not null default 0,
  error          text,
  created_at     timestamptz not null default now(),
  updated_at     timestamptz not null default now()
);
create index if not exists gen_tasks_novel_idx on public.generation_tasks (novel_id, status);
drop trigger if exists gen_tasks_touch on public.generation_tasks;
create trigger gen_tasks_touch before update on public.generation_tasks
  for each row execute function public.set_updated_at();

create table if not exists public.generation_outputs (
  id         uuid primary key default gen_random_uuid(),
  task_id    text references public.generation_tasks(id) on delete cascade,
  novel_id   uuid not null references public.novels(id) on delete cascade,
  chapter_no int,
  kind       text not null,                       -- outline|draft|continuity|edited|score|memory
  content    text not null default '',
  model      text,
  tokens     jsonb,
  created_at timestamptz not null default now()
);
create index if not exists gen_outputs_task_idx on public.generation_outputs (task_id);

create table if not exists public.generation_feedback (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users(id) on delete cascade,
  novel_id   uuid not null references public.novels(id) on delete cascade,
  chapter_no int,
  rating     text not null check (rating in ('good','needs_improvement')),
  categories text[] not null default '{}',        -- dialogue|emotion|pacing|plot|character|style
  note       text,
  created_at timestamptz not null default now()
);

create table if not exists public.quality_scores (
  id         uuid primary key default gen_random_uuid(),
  novel_id   uuid not null references public.novels(id) on delete cascade,
  chapter_no int  not null,
  scores     jsonb not null default '{}'::jsonb,  -- {plot,character,emotion,dialogue,pacing,continuity,originality,ai_likeness,reader_engagement}
  overall    numeric(4,1),
  created_at timestamptz not null default now()
);
create index if not exists quality_novel_idx on public.quality_scores (novel_id, chapter_no);

-- ---------------------------------------------------------------------------
-- 7) credits (wallet ledger; NEVER write profiles.ai_credits_* from fiction)
-- ---------------------------------------------------------------------------
create table if not exists public.credit_wallets (
  user_id         uuid primary key references auth.users(id) on delete cascade,
  balance         int not null default 0,
  lifetime_granted int not null default 0,
  lifetime_spent  int not null default 0,
  updated_at      timestamptz not null default now()
);
drop trigger if exists wallets_touch on public.credit_wallets;
create trigger wallets_touch before update on public.credit_wallets
  for each row execute function public.set_updated_at();

create table if not exists public.credit_transactions (
  id            bigserial primary key,
  user_id       uuid not null references auth.users(id) on delete cascade,
  type          text not null check (type in ('grant','lock','settle','refund','purchase','bonus')),
  amount        int  not null,                    -- signed; lock=-(n), settle=+unused, refund=+n
  balance_after int  not null,
  reference     text,                             -- idempotency key
  task_id       text,
  meta          jsonb,
  created_at    timestamptz not null default now(),
  constraint credit_tx_unique_ref unique (reference)
);
create index if not exists credit_tx_user_idx on public.credit_transactions (user_id, created_at);

-- ---------------------------------------------------------------------------
-- 8) model usage (cost accounting)
-- ---------------------------------------------------------------------------
create table if not exists public.model_usage (
  id                bigserial primary key,
  user_id           uuid references auth.users(id) on delete set null,
  novel_id          uuid references public.novels(id) on delete set null,
  task_id           text,
  agent             text,                          -- architect|character|planner|writer|continuity|editor|score|memory
  provider          text not null,                 -- deepseek|openai
  model             text not null,
  input_tokens      int not null default 0,
  output_tokens     int not null default 0,
  cached_tokens     int not null default 0,
  estimated_cost_usd numeric(10,6) not null default 0,
  credits_charged   int not null default 0,
  duration_ms       int not null default 0,
  success           boolean not null default true,
  created_at        timestamptz not null default now()
);
create index if not exists model_usage_user_idx on public.model_usage (user_id, created_at);
create index if not exists model_usage_novel_idx on public.model_usage (novel_id);

-- ---------------------------------------------------------------------------
-- 9) prompt registry (versioned; server-side only consumer)
-- ---------------------------------------------------------------------------
create table if not exists public.prompt_templates (
  id              uuid primary key default gen_random_uuid(),
  key             text not null unique,            -- architect|character_director|plot_planner|novel_writer|continuity_editor|literary_editor|quality_scorer|memory_updater
  name            text not null,
  current_version int not null default 1,
  created_at      timestamptz not null default now()
);

create table if not exists public.prompt_versions (
  id          uuid primary key default gen_random_uuid(),
  template_id uuid not null references public.prompt_templates(id) on delete cascade,
  version     int  not null,
  body        text not null,
  vars        jsonb not null default '[]'::jsonb,
  created_at  timestamptz not null default now(),
  unique (template_id, version)
);

-- ---------------------------------------------------------------------------
-- 10) skills registry (genre/anti-ai skills; versioned)
-- ---------------------------------------------------------------------------
create table if not exists public.skills (
  id              uuid primary key default gen_random_uuid(),
  key             text not null unique,            -- romance_dialogue|pacing|chapter_hook|...
  category        text not null,                   -- genre|character|dialogue|emotion|pacing|conflict|hook|foreshadowing|anti_ai|rewrite|reader
  name            text not null,
  current_version int not null default 1,
  status          text not null default 'active'
);

create table if not exists public.skill_versions (
  id        uuid primary key default gen_random_uuid(),
  skill_id  uuid not null references public.skills(id) on delete cascade,
  version   int  not null,
  body      jsonb not null default '{}'::jsonb,
  status    text not null default 'active',        -- draft|active|retired
  created_at timestamptz not null default now(),
  unique (skill_id, version)
);

create table if not exists public.skill_metrics (
  id                bigserial primary key,
  skill_key         text not null,
  skill_version     int  not null,
  window_start      date not null,
  acceptance_rate   numeric(5,2) not null default 0,
  rewrite_rate      numeric(5,2) not null default 0,
  regeneration_rate numeric(5,2) not null default 0,
  avg_quality       numeric(4,2) not null default 0,
  samples           int not null default 0,
  unique (skill_key, skill_version, window_start)
);

-- ---------------------------------------------------------------------------
-- 11) user preferences (User Memory)
-- ---------------------------------------------------------------------------
create table if not exists public.user_preferences (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  data       jsonb not null default '{}'::jsonb, -- preferred genres/pov/tone/pacing/tropes/editing prefs
  updated_at timestamptz not null default now()
);
drop trigger if exists user_prefs_touch on public.user_preferences;
create trigger user_prefs_touch before update on public.user_preferences
  for each row execute function public.set_updated_at();

-- ---------------------------------------------------------------------------
-- 12) RLS — hard isolation. UI never queries these tables directly
-- (all reads/writes go through api/fiction with verified JWT + ownership),
-- but RLS is enabled as defense-in-depth.
-- ---------------------------------------------------------------------------
do $$
declare t text;
begin
  foreach t in array array[
    'novels','story_bibles','characters','relationships','world_entities',
    'timeline_events','plot_threads','foreshadowing','chapters','chapter_summaries',
    'generation_tasks','generation_outputs','generation_feedback','quality_scores',
    'credit_wallets','credit_transactions','model_usage','user_preferences'
  ] loop
    execute format('alter table public.%I enable row level security', t);
    execute format('drop policy if exists %I_owner on public.%I', t, t);
    -- ownership column: novels/user_id for most; story_bibles/chapter_summaries via novel
    if t in ('story_bibles','chapter_summaries') then
      execute format($f$create policy %I_owner on public.%I for all
        using (exists (select 1 from public.novels n where n.id = %I.novel_id and n.user_id = auth.uid()))
        with check (exists (select 1 from public.novels n where n.id = %I.novel_id and n.user_id = auth.uid()))$f$, t, t, t, t);
    elsif t in ('relationships','world_entities','timeline_events','plot_threads','foreshadowing','generation_outputs','quality_scores') then
      execute format($f$create policy %I_owner on public.%I for all
        using (exists (select 1 from public.novels n where n.id = %I.novel_id and n.user_id = auth.uid()))
        with check (exists (select 1 from public.novels n where n.id = %I.novel_id and n.user_id = auth.uid()))$f$, t, t, t, t);
    else
      execute format($f$create policy %I_owner on public.%I for all
        using (%I.user_id = auth.uid()) with check (%I.user_id = auth.uid())$f$, t, t, t, t);
    end if;
  end loop;
end $$;

-- characters: ownership via novel
alter table public.characters enable row level security;
drop policy if exists characters_owner on public.characters;
create policy characters_owner on public.characters for all
  using (exists (select 1 from public.novels n where n.id = characters.novel_id and n.user_id = auth.uid()))
  with check (exists (select 1 from public.novels n where n.id = characters.novel_id and n.user_id = auth.uid()));

-- ---------------------------------------------------------------------------
-- 13) seed prompt templates registry (bodies live in api/_lib/prompts.js)
-- ---------------------------------------------------------------------------
insert into public.prompt_templates (key, name) values
  ('story_architect',    'Story Architect — blueprint generation'),
  ('character_director', 'Character Director — cast generation'),
  ('plot_planner',       'Plot Planner — chapter outline'),
  ('novel_writer',       'Novel Writer — chapter prose'),
  ('continuity_editor',  'Continuity Editor — consistency check'),
  ('literary_editor',    'Literary Editor — prose polish'),
  ('quality_scorer',     'Quality Scorer — 9-axis scoring'),
  ('memory_updater',     'Memory Updater — post-chapter extraction')
on conflict (key) do nothing;
