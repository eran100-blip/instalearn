-- InstaLearn chat: private messages + groups, text / shared videos / images.
-- Safe to run more than once. Run in Supabase: SQL Editor → New query → paste → Run.
-- (Run schema.sql first – this file uses the profiles table.)

-- ---------------------------------------------------------------- tables
create table if not exists public.conversations (
  id                   uuid primary key default gen_random_uuid(),
  is_group             boolean not null default false,
  name                 text,
  created_by           uuid references auth.users (id) on delete set null,
  created_at           timestamptz not null default now(),
  last_message_at      timestamptz not null default now(),
  last_message_preview text
);

create table if not exists public.conversation_members (
  conversation_id uuid not null references public.conversations (id) on delete cascade,
  user_id         uuid not null references auth.users (id) on delete cascade,
  joined_at       timestamptz not null default now(),
  last_read_at    timestamptz not null default now(),
  primary key (conversation_id, user_id)
);
create index if not exists conversation_members_user_idx on public.conversation_members (user_id);

create table if not exists public.messages (
  id              bigint generated always as identity primary key,
  conversation_id uuid not null references public.conversations (id) on delete cascade,
  sender_id       uuid not null default auth.uid() references auth.users (id) on delete cascade,
  kind            text not null default 'text' check (kind in ('text', 'video', 'image', 'system')),
  body            text,
  video_id        text,
  image_path      text,
  created_at      timestamptz not null default now()
);
create index if not exists messages_conversation_idx on public.messages (conversation_id, created_at desc);

-- ---------------------------------------------------------------- helper
-- "Am I a member of this conversation?" (security definer avoids RLS recursion)
create or replace function public.is_member(conv uuid)
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (
    select 1 from public.conversation_members m
    where m.conversation_id = conv and m.user_id = auth.uid()
  );
$$;

-- ---------------------------------------------------------------- RLS
alter table public.conversations enable row level security;
alter table public.conversation_members enable row level security;
alter table public.messages enable row level security;

drop policy if exists "members see conversation" on public.conversations;
create policy "members see conversation" on public.conversations
  for select to authenticated using (public.is_member(id));

drop policy if exists "members rename group" on public.conversations;
create policy "members rename group" on public.conversations
  for update to authenticated using (public.is_member(id)) with check (public.is_member(id));

drop policy if exists "members see members" on public.conversation_members;
create policy "members see members" on public.conversation_members
  for select to authenticated using (public.is_member(conversation_id));

drop policy if exists "update own read marker" on public.conversation_members;
create policy "update own read marker" on public.conversation_members
  for update to authenticated using (user_id = auth.uid()) with check (user_id = auth.uid());

-- Any member can remove people from a group (and anyone can leave).
drop policy if exists "members remove members" on public.conversation_members;
create policy "members remove members" on public.conversation_members
  for delete to authenticated using (public.is_member(conversation_id));

drop policy if exists "members read messages" on public.messages;
create policy "members read messages" on public.messages
  for select to authenticated using (public.is_member(conversation_id));

drop policy if exists "members send messages" on public.messages;
create policy "members send messages" on public.messages
  for insert to authenticated
  with check (sender_id = auth.uid() and public.is_member(conversation_id));

-- ---------------------------------------------------------------- functions the app calls
-- Start a private chat (returns the existing one if it already exists).
create or replace function public.start_direct_chat(other uuid)
returns uuid language plpgsql security definer set search_path = '' as $$
declare conv uuid;
begin
  if other = auth.uid() then raise exception 'cannot chat with yourself'; end if;
  select c.id into conv
  from public.conversations c
  join public.conversation_members a on a.conversation_id = c.id and a.user_id = auth.uid()
  join public.conversation_members b on b.conversation_id = c.id and b.user_id = other
  where not c.is_group
  limit 1;
  if conv is null then
    insert into public.conversations (is_group, created_by) values (false, auth.uid()) returning id into conv;
    insert into public.conversation_members (conversation_id, user_id) values (conv, auth.uid()), (conv, other);
  end if;
  return conv;
end;
$$;

-- Create a group with a name and members.
create or replace function public.create_group(group_name text, member_ids uuid[])
returns uuid language plpgsql security definer set search_path = '' as $$
declare conv uuid;
begin
  insert into public.conversations (is_group, name, created_by)
  values (true, nullif(trim(group_name), ''), auth.uid()) returning id into conv;
  insert into public.conversation_members (conversation_id, user_id)
  select conv, u from unnest(array_append(member_ids, auth.uid())) as u
  on conflict do nothing;
  insert into public.messages (conversation_id, sender_id, kind, body)
  values (conv, auth.uid(), 'system', 'created the group');
  return conv;
end;
$$;

-- Add people to a group (any member can).
create or replace function public.add_group_members(conv uuid, member_ids uuid[])
returns void language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_member(conv) then raise exception 'not a member'; end if;
  if not (select is_group from public.conversations where id = conv) then raise exception 'not a group'; end if;
  insert into public.conversation_members (conversation_id, user_id)
  select conv, u from unnest(member_ids) as u on conflict do nothing;
  insert into public.messages (conversation_id, sender_id, kind, body)
  values (conv, auth.uid(), 'system', 'added ' || array_length(member_ids, 1) || ' people');
end;
$$;

-- My chats list, with the other person (for private chats) and unread counts.
create or replace function public.my_conversations()
returns table (
  id uuid, is_group boolean, name text, last_message_at timestamptz, last_message_preview text,
  unread int, member_count int, other_id uuid, other_name text, other_username text, other_avatar text
) language sql stable security definer set search_path = '' as $$
  select c.id, c.is_group, c.name, c.last_message_at, c.last_message_preview,
    (select count(*)::int from public.messages msg
       where msg.conversation_id = c.id and msg.created_at > me.last_read_at and msg.sender_id <> auth.uid()),
    (select count(*)::int from public.conversation_members x where x.conversation_id = c.id),
    o.user_id, p.full_name, p.username, p.avatar_url
  from public.conversation_members me
  join public.conversations c on c.id = me.conversation_id
  left join lateral (
    select m2.user_id from public.conversation_members m2
    where m2.conversation_id = c.id and m2.user_id <> auth.uid() and not c.is_group
    limit 1
  ) o on true
  left join public.profiles p on p.id = o.user_id
  where me.user_id = auth.uid()
  order by c.last_message_at desc;
$$;

-- Keep the chats list preview up to date.
create or replace function public.on_new_message()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  update public.conversations
  set last_message_at = new.created_at,
      last_message_preview = case new.kind
        when 'video' then '🎬 Video'
        when 'image' then '📷 Photo'
        when 'system' then null
        else left(new.body, 120) end
  where id = new.conversation_id and new.kind <> 'system';
  return new;
end;
$$;
drop trigger if exists messages_after_insert on public.messages;
create trigger messages_after_insert after insert on public.messages
  for each row execute function public.on_new_message();

-- ---------------------------------------------------------------- realtime
do $$
begin
  begin alter publication supabase_realtime add table public.messages; exception when duplicate_object then null; end;
  begin alter publication supabase_realtime add table public.conversation_members; exception when duplicate_object then null; end;
end $$;

-- ---------------------------------------------------------------- images (Storage)
insert into storage.buckets (id, name, public)
values ('chat-images', 'chat-images', false)
on conflict (id) do nothing;

-- Files are stored as <conversation id>/<file name>; only members can upload / view.
drop policy if exists "chat members upload images" on storage.objects;
create policy "chat members upload images" on storage.objects
  for insert to authenticated
  with check (bucket_id = 'chat-images' and public.is_member(((storage.foldername(name))[1])::uuid));

drop policy if exists "chat members view images" on storage.objects;
create policy "chat members view images" on storage.objects
  for select to authenticated
  using (bucket_id = 'chat-images' and public.is_member(((storage.foldername(name))[1])::uuid));
