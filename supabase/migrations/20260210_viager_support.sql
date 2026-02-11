-- Migration: Support viager complet (v2.0.0)
-- Date: 2026-02-10
-- Description: Ajoute sous_type, viager au CHECK constraint, viager analytics columns,
--              et met à jour la vue statistiques

-- =============================================================================
-- 1. ALTER promesses_generees: Ajouter sous_type + viager fields
-- =============================================================================

-- Sous-type conditionnel (viager, creation, lotissement, etc.)
ALTER TABLE promesses_generees
    ADD COLUMN IF NOT EXISTS sous_type VARCHAR(50);

COMMENT ON COLUMN promesses_generees.sous_type IS
    'Sous-type conditionnel: viager, creation, lotissement, groupe_habitations, avec_servitudes (v2.0.0)';

-- Viager analytics: bouquet et rente pour dashboard
ALTER TABLE promesses_generees
    ADD COLUMN IF NOT EXISTS viager_bouquet NUMERIC(12, 2),
    ADD COLUMN IF NOT EXISTS viager_rente_mensuelle NUMERIC(10, 2),
    ADD COLUMN IF NOT EXISTS viager_valeur_venale NUMERIC(12, 2);

COMMENT ON COLUMN promesses_generees.viager_bouquet IS
    'Montant du bouquet pour ventes en viager (EUR)';
COMMENT ON COLUMN promesses_generees.viager_rente_mensuelle IS
    'Montant mensuel de la rente viagère (EUR)';
COMMENT ON COLUMN promesses_generees.viager_valeur_venale IS
    'Valeur vénale du bien en pleine propriété (EUR)';

-- =============================================================================
-- 2. ALTER CHECK constraint: Ajouter viager au type_promesse
-- =============================================================================

-- Drop l'ancien constraint
ALTER TABLE promesses_generees
    DROP CONSTRAINT IF EXISTS promesses_type_valid;

-- Nouveau constraint avec viager
ALTER TABLE promesses_generees
    ADD CONSTRAINT promesses_type_valid CHECK (
        type_promesse IN ('standard', 'premium', 'avec_mobilier', 'multi_biens', 'viager')
    );

-- =============================================================================
-- 3. ALTER qr_sessions: Ajouter sous_type
-- =============================================================================

ALTER TABLE qr_sessions
    ADD COLUMN IF NOT EXISTS sous_type VARCHAR(50);

COMMENT ON COLUMN qr_sessions.sous_type IS
    'Sous-type détecté pour filtrage des questions (viager, creation, etc.)';

-- =============================================================================
-- 4. Index sur sous_type
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_promesses_sous_type
    ON promesses_generees(sous_type)
    WHERE sous_type IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_qr_sessions_sous_type
    ON qr_sessions(sous_type)
    WHERE sous_type IS NOT NULL;

-- =============================================================================
-- 5. Vue statistiques mise à jour avec viager
-- =============================================================================

CREATE OR REPLACE VIEW v_stats_promesses_etude AS
SELECT
    etude_id,
    COUNT(*) as total_promesses,
    COUNT(CASE WHEN type_promesse = 'standard' THEN 1 END) as promesses_standard,
    COUNT(CASE WHEN type_promesse = 'premium' THEN 1 END) as promesses_premium,
    COUNT(CASE WHEN type_promesse = 'avec_mobilier' THEN 1 END) as promesses_mobilier,
    COUNT(CASE WHEN type_promesse = 'multi_biens' THEN 1 END) as promesses_multi,
    COUNT(CASE WHEN sous_type = 'viager' THEN 1 END) as promesses_viager,
    COUNT(CASE WHEN sous_type = 'creation' THEN 1 END) as promesses_creation_copro,
    COUNT(CASE WHEN statut = 'signe' THEN 1 END) as promesses_signees,
    COUNT(CASE WHEN titre_source_id IS NOT NULL THEN 1 END) as promesses_depuis_titre,
    -- Viager analytics
    AVG(viager_bouquet) FILTER (WHERE sous_type = 'viager') as avg_bouquet_viager,
    AVG(viager_rente_mensuelle) FILTER (WHERE sous_type = 'viager') as avg_rente_viager
FROM promesses_generees
GROUP BY etude_id;

-- =============================================================================
-- 6. Mettre à jour le commentaire de la table
-- =============================================================================

COMMENT ON COLUMN promesses_generees.type_promesse IS
    'Type: standard, premium, avec_mobilier, multi_biens, viager (v2.0.0)';
