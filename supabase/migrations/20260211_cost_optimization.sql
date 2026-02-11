-- Migration: Tier 1 Cost Optimization Tracking
-- Date: 2026-02-11
-- Version: 2.1.0
--
-- Ajoute tracking des coûts API pour monitoring des optimisations:
-- - Smart model selection (Opus vs Sonnet)
-- - Max tokens utilisés
-- - Prompt caching effectiveness
-- - Coûts par agent/workflow

-- =============================================================================
-- Table: api_costs_tracking
-- =============================================================================

CREATE TABLE IF NOT EXISTS api_costs_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  agent_name TEXT NOT NULL,
  model_used TEXT NOT NULL CHECK (model_used IN ('claude-opus-4-6', 'claude-sonnet-4-5', 'claude-haiku-4-5')),

  -- Token usage
  tokens_input INTEGER NOT NULL CHECK (tokens_input >= 0),
  tokens_output INTEGER NOT NULL CHECK (tokens_output >= 0),
  tokens_cached INTEGER DEFAULT 0 CHECK (tokens_cached >= 0),

  -- Cost
  cost_usd DECIMAL(10,6) NOT NULL CHECK (cost_usd >= 0),

  -- Performance
  duration_ms INTEGER,

  -- Context
  workflow_id TEXT,  -- Link to workflow if part of orchestrated generation
  type_acte TEXT,    -- Type d'acte généré

  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE api_costs_tracking IS 'Tracking coûts API Anthropic pour optimisations Tier 1+2';
COMMENT ON COLUMN api_costs_tracking.tokens_cached IS 'Tokens en cache (réduction 90% coût)';
COMMENT ON COLUMN api_costs_tracking.workflow_id IS 'ID du workflow complet (si orchestrated)';

-- Indexes pour queries rapides
CREATE INDEX idx_api_costs_date ON api_costs_tracking(date DESC);
CREATE INDEX idx_api_costs_agent ON api_costs_tracking(agent_name);
CREATE INDEX idx_api_costs_workflow ON api_costs_tracking(workflow_id) WHERE workflow_id IS NOT NULL;
CREATE INDEX idx_api_costs_model ON api_costs_tracking(model_used);
CREATE INDEX idx_api_costs_type_acte ON api_costs_tracking(type_acte) WHERE type_acte IS NOT NULL;

-- =============================================================================
-- Vue: v_daily_costs (dashboard coûts journaliers)
-- =============================================================================

CREATE OR REPLACE VIEW v_daily_costs AS
SELECT
  date,
  SUM(cost_usd) as total_cost,
  SUM(CASE WHEN tokens_cached > 0 THEN cost_usd ELSE 0 END) as cost_with_cache,
  SUM(CASE WHEN tokens_cached = 0 THEN cost_usd ELSE 0 END) as cost_without_cache,
  SUM(tokens_input + tokens_output) as total_tokens,
  SUM(tokens_cached) as total_cached,
  ROUND(100.0 * SUM(tokens_cached) / NULLIF(SUM(tokens_input + tokens_output), 0), 2) as cache_hit_rate_pct,
  COUNT(*) as num_calls,
  jsonb_object_agg(model_used, COUNT(*)) FILTER (WHERE model_used IS NOT NULL) as models_distribution
FROM api_costs_tracking
GROUP BY date
ORDER BY date DESC;

COMMENT ON VIEW v_daily_costs IS 'Coûts journaliers agrégés avec métriques de caching';

-- =============================================================================
-- Vue: v_agent_costs (répartition par agent, 7 derniers jours)
-- =============================================================================

CREATE OR REPLACE VIEW v_agent_costs AS
SELECT
  agent_name,
  COUNT(*) as num_calls,
  ROUND(AVG(cost_usd)::numeric, 6) as avg_cost,
  ROUND(SUM(cost_usd)::numeric, 4) as total_cost,
  ROUND(AVG(duration_ms)::numeric, 2) as avg_duration_ms,
  ROUND(AVG(tokens_input)::numeric, 0) as avg_tokens_input,
  ROUND(AVG(tokens_output)::numeric, 0) as avg_tokens_output,
  ROUND(AVG(tokens_cached)::numeric, 0) as avg_tokens_cached,
  -- Model distribution for this agent
  jsonb_object_agg(model_used, COUNT(*)) FILTER (WHERE model_used IS NOT NULL) as models_used
FROM api_costs_tracking
WHERE date > CURRENT_DATE - INTERVAL '7 days'
GROUP BY agent_name
ORDER BY total_cost DESC;

COMMENT ON VIEW v_agent_costs IS 'Coûts par agent (7 derniers jours) pour identifier agents coûteux';

-- =============================================================================
-- Vue: v_model_distribution (distribution Opus vs Sonnet vs Haiku)
-- =============================================================================

CREATE OR REPLACE VIEW v_model_distribution AS
SELECT
  date,
  model_used,
  COUNT(*) as num_calls,
  ROUND(SUM(cost_usd)::numeric, 4) as total_cost,
  ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY date), 2) as pct_of_calls
FROM api_costs_tracking
GROUP BY date, model_used
ORDER BY date DESC, total_cost DESC;

COMMENT ON VIEW v_model_distribution IS 'Distribution Opus/Sonnet/Haiku par jour (objectif: 60% Sonnet)';

-- =============================================================================
-- Vue: v_tier1_savings (économies Tier 1 vs baseline)
-- =============================================================================

CREATE OR REPLACE VIEW v_tier1_savings AS
WITH daily_costs AS (
  SELECT
    date,
    SUM(cost_usd) as actual_cost,
    COUNT(*) as num_calls,
    -- Baseline: 100% Opus, no caching
    SUM(
      (tokens_input / 1000000.0 * 15.0) +  -- Opus input
      (tokens_output / 1000000.0 * 75.0)   -- Opus output
    ) as baseline_cost
  FROM api_costs_tracking
  GROUP BY date
)
SELECT
  date,
  num_calls,
  ROUND(baseline_cost::numeric, 4) as baseline_cost_usd,
  ROUND(actual_cost::numeric, 4) as actual_cost_usd,
  ROUND((baseline_cost - actual_cost)::numeric, 4) as savings_usd,
  ROUND(100.0 * (baseline_cost - actual_cost) / NULLIF(baseline_cost, 0), 2) as savings_pct
FROM daily_costs
WHERE baseline_cost > 0
ORDER BY date DESC;

COMMENT ON VIEW v_tier1_savings IS 'Économies Tier 1 vs baseline (100% Opus, no cache). Objectif: -68%';

-- =============================================================================
-- Vue: v_cost_alerts (alertes coûts anormaux)
-- =============================================================================

CREATE OR REPLACE VIEW v_cost_alerts AS
WITH agent_stats AS (
  SELECT
    agent_name,
    AVG(cost_usd) as avg_cost,
    STDDEV(cost_usd) as stddev_cost
  FROM api_costs_tracking
  WHERE date > CURRENT_DATE - INTERVAL '7 days'
  GROUP BY agent_name
)
SELECT
  act.id,
  act.agent_name,
  act.cost_usd,
  act.duration_ms,
  act.tokens_output,
  act.created_at,
  CASE
    WHEN act.cost_usd > stats.avg_cost + 2 * COALESCE(stats.stddev_cost, 0) THEN 'HIGH_COST'
    WHEN act.tokens_output > get_max_tokens(act.agent_name) THEN 'EXCEEDED_MAX_TOKENS'
    WHEN act.duration_ms > 60000 THEN 'SLOW'
    ELSE 'OK'
  END as alert_type
FROM api_costs_tracking act
LEFT JOIN agent_stats stats ON act.agent_name = stats.agent_name
WHERE
  date >= CURRENT_DATE - INTERVAL '1 day'
  AND (
    act.cost_usd > stats.avg_cost + 2 * COALESCE(stats.stddev_cost, 0)
    OR act.duration_ms > 60000
  )
ORDER BY act.created_at DESC;

-- Fonction helper pour get_max_tokens (utilisée dans v_cost_alerts)
CREATE OR REPLACE FUNCTION get_max_tokens(agent_name TEXT) RETURNS INTEGER AS $$
BEGIN
  RETURN CASE agent_name
    WHEN 'workflow-orchestrator' THEN 4096
    WHEN 'clause-suggester' THEN 2048
    WHEN 'post-generation-reviewer' THEN 1024
    WHEN 'template-auditor' THEN 1024
    WHEN 'data-collector-qr' THEN 512
    WHEN 'cadastre-enricher' THEN 512
    WHEN 'schema-validator' THEN 512
    ELSE 2048
  END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON VIEW v_cost_alerts IS 'Alertes coûts anormaux (>2σ, >60s) pour monitoring';

-- =============================================================================
-- Fonction: insert_cost_tracking (helper pour API)
-- =============================================================================

CREATE OR REPLACE FUNCTION insert_cost_tracking(
  p_agent_name TEXT,
  p_model_used TEXT,
  p_tokens_input INTEGER,
  p_tokens_output INTEGER,
  p_tokens_cached INTEGER DEFAULT 0,
  p_cost_usd DECIMAL DEFAULT NULL,
  p_duration_ms INTEGER DEFAULT NULL,
  p_workflow_id TEXT DEFAULT NULL,
  p_type_acte TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
  v_cost_usd DECIMAL;
  v_id UUID;
BEGIN
  -- Auto-calculate cost if not provided
  IF p_cost_usd IS NULL THEN
    v_cost_usd := CASE p_model_used
      WHEN 'claude-opus-4-6' THEN
        ((p_tokens_input - p_tokens_cached) / 1000000.0 * 15.0) +
        (p_tokens_cached / 1000000.0 * 1.5) +
        (p_tokens_output / 1000000.0 * 75.0)
      WHEN 'claude-sonnet-4-5' THEN
        ((p_tokens_input - p_tokens_cached) / 1000000.0 * 3.0) +
        (p_tokens_cached / 1000000.0 * 0.3) +
        (p_tokens_output / 1000000.0 * 15.0)
      WHEN 'claude-haiku-4-5' THEN
        ((p_tokens_input - p_tokens_cached) / 1000000.0 * 0.25) +
        (p_tokens_cached / 1000000.0 * 0.025) +
        (p_tokens_output / 1000000.0 * 1.25)
      ELSE 0
    END;
  ELSE
    v_cost_usd := p_cost_usd;
  END IF;

  -- Insert
  INSERT INTO api_costs_tracking (
    agent_name, model_used, tokens_input, tokens_output, tokens_cached,
    cost_usd, duration_ms, workflow_id, type_acte
  ) VALUES (
    p_agent_name, p_model_used, p_tokens_input, p_tokens_output, p_tokens_cached,
    v_cost_usd, p_duration_ms, p_workflow_id, p_type_acte
  )
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION insert_cost_tracking IS 'Helper pour insérer tracking coût (auto-calcul si cost_usd NULL)';

-- =============================================================================
-- Grants (RLS à configurer selon politique sécurité)
-- =============================================================================

-- À adapter selon votre politique RLS existante
-- GRANT SELECT, INSERT ON api_costs_tracking TO authenticated;
-- GRANT SELECT ON v_daily_costs TO authenticated;
-- GRANT SELECT ON v_agent_costs TO authenticated;
-- GRANT SELECT ON v_model_distribution TO authenticated;
-- GRANT SELECT ON v_tier1_savings TO authenticated;
-- GRANT SELECT ON v_cost_alerts TO authenticated;

-- =============================================================================
-- Exemples de queries utiles
-- =============================================================================

-- Query 1: Coûts aujourd'hui
-- SELECT * FROM v_daily_costs WHERE date = CURRENT_DATE;

-- Query 2: Agent le plus coûteux (7j)
-- SELECT agent_name, total_cost FROM v_agent_costs ORDER BY total_cost DESC LIMIT 1;

-- Query 3: Économies Tier 1 ce mois
-- SELECT SUM(savings_usd) as total_savings_month, AVG(savings_pct) as avg_savings_pct
-- FROM v_tier1_savings
-- WHERE date >= DATE_TRUNC('month', CURRENT_DATE);

-- Query 4: Alertes coûts aujourd'hui
-- SELECT * FROM v_cost_alerts WHERE created_at::date = CURRENT_DATE;

-- Query 5: Distribution modèles cette semaine
-- SELECT model_used, SUM(num_calls) as total_calls, SUM(total_cost) as total_cost
-- FROM v_model_distribution
-- WHERE date > CURRENT_DATE - INTERVAL '7 days'
-- GROUP BY model_used
-- ORDER BY total_cost DESC;

-- =============================================================================
-- Tests post-migration
-- =============================================================================

-- Test 1: Insertion manuelle
-- SELECT insert_cost_tracking(
--   'workflow-orchestrator',
--   'claude-sonnet-4-5',
--   10000,  -- tokens_input
--   3000,   -- tokens_output
--   8000,   -- tokens_cached
--   NULL,   -- cost_usd (auto-calculated)
--   5432,   -- duration_ms
--   'WF-20260211-143052',
--   'promesse_vente'
-- );

-- Test 2: Vérifier vues
-- SELECT * FROM v_daily_costs LIMIT 1;
-- SELECT * FROM v_agent_costs LIMIT 5;
-- SELECT * FROM v_tier1_savings LIMIT 1;

-- =============================================================================
-- Rollback (si nécessaire)
-- =============================================================================

-- DROP VIEW IF EXISTS v_cost_alerts CASCADE;
-- DROP VIEW IF EXISTS v_tier1_savings CASCADE;
-- DROP VIEW IF EXISTS v_model_distribution CASCADE;
-- DROP VIEW IF EXISTS v_agent_costs CASCADE;
-- DROP VIEW IF EXISTS v_daily_costs CASCADE;
-- DROP FUNCTION IF EXISTS insert_cost_tracking CASCADE;
-- DROP FUNCTION IF EXISTS get_max_tokens CASCADE;
-- DROP TABLE IF EXISTS api_costs_tracking CASCADE;
