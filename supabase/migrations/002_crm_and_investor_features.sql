-- ============================================================================
-- BNA Market: CRM and Investor Features Migration
-- ============================================================================
-- This migration adds support for:
-- - CRM lead management
-- - Search alerts (email/SMS notifications)
-- - Property comparisons (comps)
-- - Investment portfolios
-- - Row Level Security (RLS) for data isolation
-- ============================================================================

-- ============================================================================
-- 1. CRM LEADS TABLE
-- ============================================================================
-- Lead capture and management for property inquiries

CREATE TABLE IF NOT EXISTS public.crm_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  property_zpid VARCHAR(20) NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  phone VARCHAR(50),
  message TEXT,
  status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'lost')),
  assigned_to UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  tags TEXT[],
  next_follow_up_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_crm_leads_user_id ON public.crm_leads(user_id);
CREATE INDEX IF NOT EXISTS idx_crm_leads_status ON public.crm_leads(status);
CREATE INDEX IF NOT EXISTS idx_crm_leads_zpid ON public.crm_leads(property_zpid);
CREATE INDEX IF NOT EXISTS idx_crm_leads_updated_at ON public.crm_leads(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE public.crm_leads ENABLE ROW LEVEL SECURITY;

-- RLS Policies for crm_leads
CREATE POLICY "Users can manage own leads"
  ON public.crm_leads
  FOR ALL
  USING (auth.uid() = user_id);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_crm_leads_updated_at ON public.crm_leads;
CREATE TRIGGER update_crm_leads_updated_at
  BEFORE UPDATE ON public.crm_leads
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- 2. SEARCH ALERTS TABLE
-- ============================================================================
-- Email/SMS notifications for saved searches

CREATE TABLE IF NOT EXISTS public.search_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  saved_search_id UUID REFERENCES public.user_saved_searches(id) ON DELETE CASCADE,
  alert_type VARCHAR(20) NOT NULL CHECK (alert_type IN ('email', 'sms', 'both')),
  enabled BOOLEAN DEFAULT true,
  frequency VARCHAR(20) DEFAULT 'daily' CHECK (frequency IN ('instant', 'daily', 'weekly')),
  last_sent_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  CONSTRAINT unique_search_alert UNIQUE(saved_search_id, alert_type)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_search_alerts_user_id ON public.search_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_search_alerts_saved_search ON public.search_alerts(saved_search_id);

-- Enable Row Level Security
ALTER TABLE public.search_alerts ENABLE ROW LEVEL SECURITY;

-- RLS Policies for search_alerts
CREATE POLICY "Users can manage own alerts"
  ON public.search_alerts
  FOR ALL
  USING (auth.uid() = user_id);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_search_alerts_updated_at ON public.search_alerts;
CREATE TRIGGER update_search_alerts_updated_at
  BEFORE UPDATE ON public.search_alerts
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- 3. PROPERTY COMPS TABLE
-- ============================================================================
-- Property comparison analyses

CREATE TABLE IF NOT EXISTS public.property_comps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  subject_zpid VARCHAR(20) NOT NULL,
  comp_zpids TEXT[] NOT NULL,
  filters JSONB,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  CONSTRAINT unique_user_comp_name UNIQUE(user_id, name)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_property_comps_user_id ON public.property_comps(user_id);
CREATE INDEX IF NOT EXISTS idx_property_comps_subject ON public.property_comps(subject_zpid);
CREATE INDEX IF NOT EXISTS idx_property_comps_updated_at ON public.property_comps(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE public.property_comps ENABLE ROW LEVEL SECURITY;

-- RLS Policies for property_comps
CREATE POLICY "Users can manage own comps"
  ON public.property_comps
  FOR ALL
  USING (auth.uid() = user_id);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_property_comps_updated_at ON public.property_comps;
CREATE TRIGGER update_property_comps_updated_at
  BEFORE UPDATE ON public.property_comps
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- 4. USER PORTFOLIOS TABLE
-- ============================================================================
-- Investment portfolio management

CREATE TABLE IF NOT EXISTS public.user_portfolios (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  target_return NUMERIC(5, 2),
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  CONSTRAINT unique_user_portfolio_name UNIQUE(user_id, name)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_user_portfolios_user_id ON public.user_portfolios(user_id);
CREATE INDEX IF NOT EXISTS idx_user_portfolios_updated_at ON public.user_portfolios(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE public.user_portfolios ENABLE ROW LEVEL SECURITY;

-- RLS Policies for user_portfolios
CREATE POLICY "Users can manage own portfolios"
  ON public.user_portfolios
  FOR ALL
  USING (auth.uid() = user_id);

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_user_portfolios_updated_at ON public.user_portfolios;
CREATE TRIGGER update_user_portfolios_updated_at
  BEFORE UPDATE ON public.user_portfolios
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- 5. PORTFOLIO PROPERTIES TABLE
-- ============================================================================
-- Properties in investment portfolios

CREATE TABLE IF NOT EXISTS public.portfolio_properties (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  portfolio_id UUID NOT NULL REFERENCES public.user_portfolios(id) ON DELETE CASCADE,
  zpid VARCHAR(20) NOT NULL,
  purchase_price NUMERIC(12, 2),
  purchase_date DATE,
  current_value NUMERIC(12, 2),
  monthly_rent NUMERIC(10, 2),
  monthly_expenses NUMERIC(10, 2),
  is_vacant BOOLEAN DEFAULT false,
  lease_end_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
  CONSTRAINT unique_portfolio_property UNIQUE(portfolio_id, zpid)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_portfolio_properties_portfolio_id ON public.portfolio_properties(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_properties_zpid ON public.portfolio_properties(zpid);
CREATE INDEX IF NOT EXISTS idx_portfolio_properties_updated_at ON public.portfolio_properties(updated_at DESC);

-- Enable Row Level Security
ALTER TABLE public.portfolio_properties ENABLE ROW LEVEL SECURITY;

-- RLS Policy for portfolio_properties (check ownership via portfolio)
CREATE POLICY "Users can manage portfolio properties"
  ON public.portfolio_properties
  FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.user_portfolios
      WHERE id = portfolio_id AND user_id = auth.uid()
    )
  );

-- Trigger for updated_at
DROP TRIGGER IF EXISTS update_portfolio_properties_updated_at ON public.portfolio_properties;
CREATE TRIGGER update_portfolio_properties_updated_at
  BEFORE UPDATE ON public.portfolio_properties
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- ============================================================================
-- 6. COMMENTS (Documentation)
-- ============================================================================

COMMENT ON TABLE public.crm_leads IS 'CRM lead management for property inquiries';
COMMENT ON TABLE public.search_alerts IS 'Email/SMS notifications for saved searches';
COMMENT ON TABLE public.property_comps IS 'Property comparison analyses';
COMMENT ON TABLE public.user_portfolios IS 'User investment portfolios';
COMMENT ON TABLE public.portfolio_properties IS 'Properties in investment portfolios';

COMMENT ON COLUMN public.crm_leads.status IS 'Lead status: new, contacted, qualified, converted, lost';
COMMENT ON COLUMN public.crm_leads.tags IS 'Array of tag strings for categorization';
COMMENT ON COLUMN public.search_alerts.frequency IS 'Notification frequency: instant, daily, weekly';
COMMENT ON COLUMN public.property_comps.comp_zpids IS 'Array of comparable property Zillow IDs';
COMMENT ON COLUMN public.property_comps.filters IS 'JSONB with similarity filters used';
COMMENT ON COLUMN public.portfolio_properties.is_vacant IS 'Whether property is currently vacant';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- To apply this migration:
-- 1. Go to Supabase Dashboard -> SQL Editor
-- 2. Paste and run this script
-- 3. Verify tables and RLS policies are created
-- ============================================================================
