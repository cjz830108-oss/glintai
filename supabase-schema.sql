-- ============================================================================
-- Glint AI — Supabase 建表 SQL（一次性执行）
-- 位置：Supabase 后台 → SQL Editor → 粘贴全文 → Run
-- ============================================================================
-- 作用：
--   1) 建 profiles 表，PayPal webhook 把订阅状态写进这张表
--   2) 用户注册（Supabase Auth）时自动建一行 profile
--   3) 开启 RLS 行级安全，用户只能读写自己的行
--
-- ⚠️ 前提（重要）：webhook 是按【邮箱】匹配用户的
--    PayPal 订阅邮箱 必须 = Supabase 注册邮箱
--    否则付款成功后 profiles.plan 翻不成 pro。
--    让用户「用同一个邮箱注册/登录」即可（onApprove 提示里已写明）。

-- ---------------------------------------------------------------------------
-- 1) profiles 表
-- ---------------------------------------------------------------------------
create table if not exists public.profiles (
  id            uuid        primary key references auth.users(id) on delete cascade,
  email         text,                                   -- 用于 webhook 匹配
  plan          text        not null default 'free',    -- 'free' | 'pro' | 'team'
  sub_status    text,                                   -- 'active' | 'canceled' | 'past_due' | null
  paypal_email  text,
  created_at    timestamptz not null default now()
);

create index if not exists profiles_email_idx on public.profiles (email);

-- ---------------------------------------------------------------------------
-- 2) 新用户注册时，自动建一行 profile（填 id + email）
-- ---------------------------------------------------------------------------
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------------------
-- 3) 行级安全（RLS）
-- ---------------------------------------------------------------------------
alter table public.profiles enable row level security;

-- 登录用户只能读自己的行（前端用 anon key 读 plan）
drop policy if exists profiles_select_own on public.profiles;
create policy profiles_select_own on public.profiles
  for select using (auth.uid() = id);

-- 登录用户只能改自己的行
drop policy if exists profiles_update_own on public.profiles;
create policy profiles_update_own on public.profiles
  for update using (auth.uid() = id);

-- ⚠️ PayPal webhook 用的是 SERVICE_ROLE key，会【绕过 RLS】，
--    所以 webhook 写表不需要额外策略，上面两条只管前端读。

-- ---------------------------------------------------------------------------
-- 4) 用量 / 订阅周期字段（升级用，幂等添加，可重复执行）
-- ---------------------------------------------------------------------------
-- 免费档用量优先在客户端 localStorage 计数 + 月度重置；
-- Pro 由 webhook 把 plan 置为 'pro' + 写入 subscription_end 来解锁无限。
-- 这些字段由前端/服务端在每次 AI 调用后累加，月度到期时归零：
--   if profiles.period_start < now() - interval '1 month' then
--     ai_credits_used := 0; period_start := now(); end if;
do $$
begin
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='ai_credits_used') then
    alter table public.profiles add column ai_credits_used  int  not null default 0;
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='ai_credits_limit') then
    alter table public.profiles add column ai_credits_limit int  not null default 50;   -- 免费档月度额度
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='pdf_pages_used') then
    alter table public.profiles add column pdf_pages_used   int  not null default 0;
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='pdf_pages_limit') then
    alter table public.profiles add column pdf_pages_limit  int  not null default 20;
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='exports_used') then
    alter table public.profiles add column exports_used     int  not null default 0;
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='period_start') then
    alter table public.profiles add column period_start     timestamptz not null default now();
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='subscription_period') then
    alter table public.profiles add column subscription_period text;   -- 'monthly' | 'yearly' | null
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='subscription_end') then
    alter table public.profiles add column subscription_end timestamptz;  -- 到期日（续费/降级判断）
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='google_id') then
    alter table public.profiles add column google_id        text;
  end if;
  if not exists (select 1 from information_schema.columns where table_name='profiles' and column_name='last_seen') then
    alter table public.profiles add column last_seen        timestamptz;
  end if;
end $$;

-- 注册时顺便初始化用量字段（沿用 handle_new_user）
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email, ai_credits_used, ai_credits_limit, pdf_pages_used, pdf_pages_limit, exports_used, period_start)
  values (new.id, new.email, 0, 50, 0, 20, 0, now())
  on conflict (id) do nothing;
  return new;
end;
$$;

