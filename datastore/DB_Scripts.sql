-- In Supabase → PostgreSQL backend → you already have:
-- public schema → (default schema, managed by you)
-- By default, everything you create (tables/views/functions) unless you specify goes into public schema.

-- 📌 You should create this users table in public schema.
-- Supabase auth tables (like auth.users) are in auth schema → you should NOT use or modify that.

-- → It will by default go into public.users

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  full_name text,
  provider text,
  avatar_url text,
  last_login timestamp default now()
);

-------------------------------------
-- USE POLICY based on NEEDS
-------------------------------------
create policy "Policy_for_ALL"
on "public"."users"
as PERMISSIVE
for ALL
to public
WITH CHECK (true);

CREATE POLICY "Allow insert for all"
ON public.users
FOR INSERT
TO public
WITH CHECK (true);


CREATE POLICY "Allow insert for service_role"
ON public.users
FOR INSERT
TO service_role
WITH CHECK (true);

