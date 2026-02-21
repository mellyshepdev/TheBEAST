-- Create activity_log table for real-time monitoring
create table if not exists public.activity_log (
  id uuid default gen_random_uuid() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  level text not null default 'info', -- 'info', 'warn', 'error'
  category text not null default 'SYSTEM', -- 'SCOUT', 'SEO', 'MESH', 'PERSONALITY', etc.
  message text not null,
  metadata jsonb default '{}'::jsonb
);

-- Enable RLS
alter table public.activity_log enable row level security;

-- Policies
create policy "Anyone can view activity logs"
  on public.activity_log for select
  using ( true );

-- Only service role or specific authenticated users should insert, but for simplicity in development:
create policy "Authenticated users can insert activity logs"
  on public.activity_log for insert
  with check ( auth.role() = 'authenticated' );

-- Optional: Enable real-time for this table
-- This is usually done via the Supabase dashboard or a specific SQL command if extensions allow
-- alter publication supabase_realtime add table activity_log;
