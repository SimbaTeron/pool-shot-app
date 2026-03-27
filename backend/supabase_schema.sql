-- ============================================================
-- Pool Shot App — Supabase Database Schema
-- Run this in: Supabase Dashboard → SQL Editor
-- ============================================================

-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- ============================================================
-- PROFILES TABLE
-- One row per user, linked to auth.users
-- ============================================================
create table if not exists public.profiles (
  id uuid references auth.users(id) on delete cascade primary key,
  email text not null,
  subscription_tier text not null default 'free' 
    check (subscription_tier in ('free', 'pro', 'pool_hall')),
  shots_used_today integer not null default 0,
  created_at timestamptz not null default now()
);

-- Auto-create profile on user signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email);
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ============================================================
-- SHOTS TABLE (optional — stores shot history)
-- ============================================================
create table if not exists public.shots (
  id uuid default uuid_generate_v4() primary key,
  user_id uuid references public.profiles(id) on delete cascade not null,
  table_size text not null check (table_size in ('7ft', '9ft')),
  game_type text not null check (game_type in ('8ball', '9ball', 'straight')),
  skill_level text not null check (skill_level in ('beginner', 'intermediate', 'pro')),
  shot_angle numeric(5,2),
  shot_power numeric(3,2),
  shot_english numeric(3,2),
  target_ball integer,
  target_pocket text,
  shot_score numeric(5,2),
  confidence numeric(3,2),
  shot_quality text,
  diagram_svg text,  -- stored as text for now; consider moving to Supabase Storage
  created_at timestamptz not null default now()
);

-- Row Level Security (RLS)
alter table public.profiles enable row level security;
alter table public.shots enable row level security;

-- Profiles: users can only see/edit their own row
create policy "Users can view own profile" on public.profiles
  for select using (auth.uid() = id);
create policy "Users can update own profile" on public.profiles
  for update using (auth.uid() = id);
create policy "Users can insert own profile" on public.profiles
  for insert with check (auth.uid() = id);

-- Shots: users can only see/edit their own shots
create policy "Users can view own shots" on public.shots
  for select using (auth.uid() = user_id);
create policy "Users can insert own shots" on public.shots
  for insert with check (auth.uid() = user_id);

-- ============================================================
-- USAGE EXAMPLE
-- ============================================================
--
-- Sign up: handled by Supabase Auth (no SQL needed)
--
-- Check quota:
--   SELECT shots_used_today FROM profiles WHERE id = auth.uid();
--
-- Increment shot count (after each shot):
--   UPDATE profiles SET shots_used_today = shots_used_today + 1 WHERE id = auth.uid();
--
-- Reset daily shots (run via Supabase Cron or Edge Function daily):
--   UPDATE profiles SET shots_used_today = 0;
--
-- Upgrade subscription (via Edge Function or direct admin update):
--   UPDATE profiles SET subscription_tier = 'pro' WHERE id = auth.uid();
