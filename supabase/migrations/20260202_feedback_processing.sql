-- =============================================================================
-- Migration: Colonnes pour le tracking du self-anneal
-- Date: 2026-02-02
-- Description: Ajoute les colonnes processed, processed_at, pr_url,
--              correction_type a feedbacks_promesse pour le pipeline
--              d'auto-correction (self_anneal.py).
-- =============================================================================

ALTER TABLE feedbacks_promesse
ADD COLUMN IF NOT EXISTS processed BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS pr_url TEXT,
ADD COLUMN IF NOT EXISTS correction_type VARCHAR(50);

-- Index partiel: seuls les feedbacks non traites et approuves
-- sont lus par le job self-anneal (query rapide)
CREATE INDEX IF NOT EXISTS idx_feedbacks_unprocessed
ON feedbacks_promesse(processed)
WHERE processed = FALSE AND approuve = TRUE;
