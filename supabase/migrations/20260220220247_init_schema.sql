-- Enable the pgvector extension to work with embeddings
create extension if not exists vector;

-- Create user_profiles table
create table if not exists public.user_profiles (
  id uuid references auth.users on delete cascade not null primary key,
  full_name text,
  avatar_url text,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS on user_profiles
alter table public.user_profiles enable row level security;

-- Create cloud_files table for metadata
create table if not exists public.cloud_files (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references auth.users on delete cascade not null,
  file_name text not null,
  provider text not null, -- 'google_drive', 'onedrive', etc.
  remote_id text not null,
  mime_type text,
  size bigint,
  metadata jsonb,
  embedding vector(1536), -- Default size for OpenAI embeddings
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS on cloud_files
alter table public.cloud_files enable row level security;

-- Policies for user_profiles
create policy "Users can view their own profiles"
  on public.user_profiles for select
  using ( auth.uid() = id );

create policy "Users can update their own profiles"
  on public.user_profiles for update
  using ( auth.uid() = id );

-- Policies for cloud_files
create policy "Users can view their own cloud files"
  on public.cloud_files for select
  using ( auth.uid() = user_id );

create policy "Users can insert their own cloud files"
  on public.cloud_files for insert
  with check ( auth.uid() = user_id );

create policy "Users can update their own cloud files"
  on public.cloud_files for update
  using ( auth.uid() = user_id );

create policy "Users can delete their own cloud files"
  on public.cloud_files for delete
  using ( auth.uid() = user_id );
