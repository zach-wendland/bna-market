-- ============================================================================
-- BNA Market: User Authentication and Features Migration
-- ============================================================================
-- This migration adds support for:
-- - User profiles (extends Supabase Auth)
-- - Multiple named property lists
-- - Saved search filters
-- - Row Level Security (RLS) for data isolation
-- ============================================================================

-- ============================================================================
-- 1. USER PROFILES TABLE
-- ============================================================================
-- Extends Supabase Auth's auth.users table with additional profile information

CREATE TABLE IF NOT EXISTS public.user_profiles (
  id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email TEXT NOT NULL,
  display_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);

-- Enable Row Level Security
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_profiles
CREATE POLICY "Users can view own profile"
  ON public.user_profiles
  FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
  ON public.user_profiles
  FOR UPDATE
  USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile"
  ON public.user_profiles
  FOR INSERT
  WITH CHECK (auth.uid() = id);

-- ============================================================================
-- 2. USER PROPERTY LISTS TABLE
-- ============================================================================
-- Users can create multiple named lists (e.g., "Downtown Condos", "Investment Properties")

CREATE TABLE IF NOT EXISTS public.user_property_lists (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL CHECK (char_length(name) > 0 AND char_length(name) <= 100),
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  CONSTRAINT unique_user_list_name UNIQUE(user_id, name)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_property_lists_user_id ON public.user_property_lists(user_id);
CREATE INDEX IF NOT EXISTS idx_property_lists_updated_at ON public.user_property_lists(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE public.user_property_lists ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_property_lists
CREATE POLICY "Users can manage own lists"
  ON public.user_property_lists
  FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- 3. USER PROPERTY LIST ITEMS TABLE
-- ============================================================================
-- Properties saved to each list

CREATE TABLE IF NOT EXISTS public.user_property_list_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  list_id UUID NOT NULL REFERENCES public.user_property_lists(id) ON DELETE CASCADE,
  zpid TEXT NOT NULL CHECK (char_length(zpid) > 0),
  property_type TEXT NOT NULL CHECK (property_type IN ('forsale', 'rental')),
  notes TEXT,
  added_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  CONSTRAINT unique_list_property UNIQUE(list_id, zpid)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_list_items_list_id ON public.user_property_list_items(list_id);
CREATE INDEX IF NOT EXISTS idx_list_items_zpid ON public.user_property_list_items(zpid);
CREATE INDEX IF NOT EXISTS idx_list_items_added_at ON public.user_property_list_items(added_at DESC);

-- Enable Row Level Security
ALTER TABLE public.user_property_list_items ENABLE ROW LEVEL SECURITY;

-- RLS Policy for user_property_list_items (check ownership via list)
CREATE POLICY "Users can manage items in own lists"
  ON public.user_property_list_items
  FOR ALL
  USING (
    list_id IN (
      SELECT id FROM public.user_property_lists WHERE user_id = auth.uid()
    )
  );

-- ============================================================================
-- 4. USER SAVED SEARCHES TABLE
-- ============================================================================
-- Users can save search filter configurations for quick recall

CREATE TABLE IF NOT EXISTS public.user_saved_searches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name TEXT NOT NULL CHECK (char_length(name) > 0 AND char_length(name) <= 100),
  property_type TEXT NOT NULL CHECK (property_type IN ('forsale', 'rental')),
  filters JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  CONSTRAINT unique_user_search_name UNIQUE(user_id, name)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id ON public.user_saved_searches(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_searches_updated_at ON public.user_saved_searches(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_saved_searches_filters ON public.user_saved_searches USING GIN(filters);

-- Enable Row Level Security
ALTER TABLE public.user_saved_searches ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_saved_searches
CREATE POLICY "Users can manage own searches"
  ON public.user_saved_searches
  FOR ALL
  USING (auth.uid() = user_id);

-- ============================================================================
-- 5. TRIGGERS AND FUNCTIONS
-- ============================================================================

-- Function to auto-create user profile when a new user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO public.user_profiles (id, email, display_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1))
  );
  RETURN NEW;
END;
$$;

-- Trigger to automatically create profile on user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

-- Triggers to auto-update updated_at timestamps
DROP TRIGGER IF EXISTS update_user_profiles_updated_at ON public.user_profiles;
CREATE TRIGGER update_user_profiles_updated_at
  BEFORE UPDATE ON public.user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_property_lists_updated_at ON public.user_property_lists;
CREATE TRIGGER update_property_lists_updated_at
  BEFORE UPDATE ON public.user_property_lists
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

DROP TRIGGER IF EXISTS update_saved_searches_updated_at ON public.user_saved_searches;
CREATE TRIGGER update_saved_searches_updated_at
  BEFORE UPDATE ON public.user_saved_searches
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- 6. COMMENTS (Documentation)
-- ============================================================================

COMMENT ON TABLE public.user_profiles IS 'Extended user profile information for authenticated users';
COMMENT ON TABLE public.user_property_lists IS 'Named property lists created by users (e.g., "Downtown Condos")';
COMMENT ON TABLE public.user_property_list_items IS 'Properties saved to user lists';
COMMENT ON TABLE public.user_saved_searches IS 'Saved search filter configurations';

COMMENT ON COLUMN public.user_profiles.display_name IS 'User display name (defaults to email username)';
COMMENT ON COLUMN public.user_property_lists.name IS 'List name (max 100 chars, unique per user)';
COMMENT ON COLUMN public.user_property_list_items.zpid IS 'Zillow Property ID';
COMMENT ON COLUMN public.user_saved_searches.filters IS 'JSONB object with filter parameters (minPrice, maxPrice, minBeds, etc.)';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- To apply this migration:
-- 1. Go to Supabase Dashboard → SQL Editor
-- 2. Paste and run this script
-- 3. Verify tables and RLS policies are created
-- 4. Test with: SELECT * FROM user_profiles; (should return empty or your data)
-- ============================================================================
