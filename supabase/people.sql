-- Finding other users in Chats. Safe to run more than once.
-- Run in Supabase: SQL Editor → New query → paste → Run.

-- 1) Every account gets a profile (accounts created before schema.sql ran had none).
insert into public.profiles (id, full_name, avatar_url)
select u.id,
       coalesce(nullif(btrim(u.raw_user_meta_data ->> 'full_name'), ''),
                nullif(btrim(u.raw_user_meta_data ->> 'name'), ''),
                split_part(u.email, '@', 1)),
       u.raw_user_meta_data ->> 'avatar_url'
from auth.users u
where not exists (select 1 from public.profiles p where p.id = u.id);

insert into public.user_settings (user_id)
select u.id from auth.users u
where not exists (select 1 from public.user_settings s where s.user_id = u.id);

-- 2) Profiles without a name get the part of the email before the @, so they can be found.
update public.profiles p
set full_name = split_part(u.email, '@', 1)
from auth.users u
where u.id = p.id and (p.full_name is null or btrim(p.full_name) = '');

-- 3) New sign-ups: same rule (name from the form / Google, otherwise the email prefix).
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (
    new.id,
    coalesce(nullif(btrim(new.raw_user_meta_data ->> 'full_name'), ''),
             nullif(btrim(new.raw_user_meta_data ->> 'name'), ''),
             split_part(new.email, '@', 1)),
    new.raw_user_meta_data ->> 'avatar_url'
  )
  on conflict (id) do nothing;
  insert into public.user_settings (user_id) values (new.id) on conflict (user_id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- 4) Search people by name, @username, or their full email address.
--    The email itself is never returned to the app – only an exact match finds someone.
create or replace function public.search_people(q text)
returns table (id uuid, full_name text, username text, avatar_url text)
language sql stable security definer set search_path = '' as $$
  select p.id, p.full_name, p.username, p.avatar_url
  from public.profiles p
  join auth.users u on u.id = p.id
  where auth.uid() is not null
    and p.id <> auth.uid()
    and length(btrim(q)) >= 2
    and (
      p.full_name ilike '%' || btrim(q) || '%'
      or p.username ilike '%' || ltrim(btrim(q), '@') || '%'
      or lower(u.email) = lower(btrim(q))
    )
  order by p.full_name nulls last
  limit 30;
$$;

revoke all on function public.search_people(text) from public, anon;
grant execute on function public.search_people(text) to authenticated;

-- 5) Check: every account should appear here with a name.
select u.email, p.full_name, p.username, u.email_confirmed_at is not null as email_confirmed, u.created_at
from auth.users u
left join public.profiles p on p.id = u.id
order by u.created_at;
