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
