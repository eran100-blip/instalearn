-- InstaLearn database schema (users stage).
-- Safe to run more than once. Run in Supabase: Dashboard → SQL Editor → New query → paste → Run.

-- ---------------------------------------------------------------- profiles
-- One row per user. Created automatically when someone signs up.
create table if not exists public.profiles (
  id          uuid primary key references auth.users (id) on delete cascade,
  full_name   text,
  username    text unique,
  university  text,
  avatar_url  text,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

alter table public.profiles enable row level security;

-- Any signed-in user can see profiles (needed later to find people to chat with).
drop policy if exists "profiles are visible to signed-in users" on public.profiles;
create policy "profiles are visible to signed-in users"
  on public.profiles for select to authenticated using (true);

-- Users can only change their own profile.
drop policy if exists "users update their own profile" on public.profiles;
create policy "users update their own profile"
  on public.profiles for update to authenticated
  using (auth.uid() = id) with check (auth.uid() = id);

-- Create the profile row on sign-up (name comes from the sign-up form or from Google).
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'full_name', new.raw_user_meta_data ->> 'name'),
    new.raw_user_meta_data ->> 'avatar_url'
  );
  insert into public.user_settings (user_id) values (new.id);
  return new;
end;
$$;

-- ---------------------------------------------------------------- settings
-- The "Courses" page choices, so they follow the user to any device.
create table if not exists public.user_settings (
  user_id         uuid primary key references auth.users (id) on delete cascade,
  selected_courses text[] not null default '{}',
  levels          jsonb   not null default '{}'::jsonb,
  question_every  int     not null default 3,
  updated_at      timestamptz not null default now()
);

alter table public.user_settings enable row level security;

drop policy if exists "users read their own settings" on public.user_settings;
create policy "users read their own settings"
  on public.user_settings for select to authenticated using (auth.uid() = user_id);
drop policy if exists "users insert their own settings" on public.user_settings;
create policy "users insert their own settings"
  on public.user_settings for insert to authenticated with check (auth.uid() = user_id);
drop policy if exists "users update their own settings" on public.user_settings;
create policy "users update their own settings"
  on public.user_settings for update to authenticated
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------- attempts
-- Every answered question. Later used to find each student's weak topics.
create table if not exists public.attempts (
  id          bigint generated always as identity primary key,
  user_id     uuid not null references auth.users (id) on delete cascade,
  question_id text not null,
  video_id    text,
  course_id   text,
  correct     boolean not null,
  created_at  timestamptz not null default now()
);

create index if not exists attempts_user_idx on public.attempts (user_id, created_at desc);

alter table public.attempts enable row level security;

drop policy if exists "users read their own attempts" on public.attempts;
create policy "users read their own attempts"
  on public.attempts for select to authenticated using (auth.uid() = user_id);
drop policy if exists "users add their own attempts" on public.attempts;
create policy "users add their own attempts"
  on public.attempts for insert to authenticated with check (auth.uid() = user_id);
