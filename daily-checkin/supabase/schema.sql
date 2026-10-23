-- Same tables as server/checkin/store.py, for Supabase (Postgres).
-- Run in the Supabase SQL editor. Turn on row level security before real
-- families use it; the policies below let each family see only their own
-- senior, assuming a family_members link table filled at sign-up.

create table people (
  id text primary key,
  name text not null,
  birth_date date not null,
  timezone text not null,
  checkin_time time not null,
  place_keywords jsonb not null default '[]',
  family_name text,
  family_phone text,
  senior_push_token text,
  family_push_token text,
  created_date date not null,
  evening_checkin boolean not null default false,
  evening_time time not null default '19:00',
  share_recordings boolean not null default true
);

create table checkins (
  id text primary key,
  person_id text not null references people(id) on delete cascade,
  local_date date not null,
  completed_at timestamptz not null,
  local_hour real not null,
  result jsonb not null,
  features jsonb,
  family_says_different boolean,
  duration_s real,
  ease integer,
  session text not null default 'morning' check (session in ('morning', 'evening')),
  listen_key text,  -- secret part of the family's link to hear this check-in
  unique (person_id, local_date, session)
);

create table days_off (
  person_id text not null references people(id) on delete cascade,
  date date not null,
  primary key (person_id, date)
);

create table alerts (
  person_id text not null references people(id) on delete cascade,
  date date not null,
  kind text not null,
  sent_at timestamptz not null,
  delivered boolean not null default false,
  message text,
  primary key (person_id, date, kind)
);

create table family_members (
  user_id uuid not null references auth.users(id) on delete cascade,
  person_id text not null references people(id) on delete cascade,
  primary key (user_id, person_id)
);

alter table people enable row level security;
alter table checkins enable row level security;
alter table days_off enable row level security;
alter table alerts enable row level security;
alter table family_members enable row level security;

create policy "family reads their person" on people for select
  using (id in (select person_id from family_members where user_id = auth.uid()));
create policy "family reads check-ins" on checkins for select
  using (person_id in (select person_id from family_members where user_id = auth.uid()));
create policy "family reads alerts" on alerts for select
  using (person_id in (select person_id from family_members where user_id = auth.uid()));
create policy "family manages days off" on days_off for all
  using (person_id in (select person_id from family_members where user_id = auth.uid()));
create policy "members see own links" on family_members for select
  using (user_id = auth.uid());

-- Recordings live in a private storage bucket, one folder per check-in id.
insert into storage.buckets (id, name, public) values ('recordings', 'recordings', false);

-- Run the missed check-in job every 10 minutes (needs pg_cron and pg_net).
-- select cron.schedule('missed-checkins', '*/10 * * * *',
--   $$select net.http_post(url := 'https://YOUR-API/jobs/missed-checkins',
--     headers := '{"Authorization": "Bearer YOUR_API_TOKEN"}'::jsonb)$$);
