-- Migration: Ajout de la catégorie de bien et support workflow Q&R
-- Date: 2026-01-30
-- Description: Ajoute categorie_bien aux dossiers et promesses,
--              crée la table qr_sessions pour persister les sessions Q&R

-- =============================================================================
-- ALTER: Ajouter categorie_bien aux tables existantes
-- =============================================================================

-- Dossiers: catégorie du bien pour chaque dossier
ALTER TABLE dossiers
    ADD COLUMN IF NOT EXISTS categorie_bien VARCHAR(30)
    DEFAULT 'copropriete'
    CHECK (categorie_bien IN ('copropriete', 'hors_copropriete', 'terrain_a_batir'));

COMMENT ON COLUMN dossiers.categorie_bien IS
    'Catégorie de bien: copropriete, hors_copropriete, terrain_a_batir (v1.7.0)';

-- Promesses générées: catégorie utilisée lors de la génération
ALTER TABLE promesses_generees
    ADD COLUMN IF NOT EXISTS categorie_bien VARCHAR(30)
    DEFAULT 'copropriete'
    CHECK (categorie_bien IN ('copropriete', 'hors_copropriete', 'terrain_a_batir'));

ALTER TABLE promesses_generees
    ADD COLUMN IF NOT EXISTS workflow_id VARCHAR(100);

COMMENT ON COLUMN promesses_generees.categorie_bien IS
    'Catégorie de bien utilisée pour la sélection du template (v1.7.0)';

-- =============================================================================
-- Table: qr_sessions
-- Sessions Q&R persistées pour le workflow frontend
-- =============================================================================

CREATE TABLE IF NOT EXISTS qr_sessions (
    id VARCHAR(100) PRIMARY KEY,
    etude_id UUID NOT NULL REFERENCES etudes(id),

    -- Type et catégorie
    type_acte VARCHAR(50) NOT NULL DEFAULT 'promesse_vente',
    categorie_bien VARCHAR(30) NOT NULL DEFAULT 'copropriete'
        CHECK (categorie_bien IN ('copropriete', 'hors_copropriete', 'terrain_a_batir')),

    -- Données collectées (JSONB)
    donnees JSONB NOT NULL DEFAULT '{}',

    -- Progression
    questions_posees INTEGER DEFAULT 0,
    questions_preremplies INTEGER DEFAULT 0,
    questions_ignorees INTEGER DEFAULT 0,
    pourcentage_completion INTEGER DEFAULT 0,

    -- État workflow
    workflow_status VARCHAR(30) DEFAULT 'collecting'
        CHECK (workflow_status IN (
            'collecting', 'ready_to_generate', 'generating',
            'completed', 'validation_failed', 'generation_failed'
        )),
    steps_completed TEXT[] DEFAULT '{}',

    -- Fichier généré
    fichier_path VARCHAR(500),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),

    -- Audit
    titre_source_id UUID REFERENCES titres_propriete(id)
);

-- Index pour recherche rapide par étude
CREATE INDEX IF NOT EXISTS idx_qr_sessions_etude
    ON qr_sessions(etude_id);

CREATE INDEX IF NOT EXISTS idx_qr_sessions_status
    ON qr_sessions(workflow_status);

-- RLS (Row Level Security)
ALTER TABLE qr_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "qr_sessions_etude_isolation" ON qr_sessions
    FOR ALL
    USING (etude_id = current_setting('app.etude_id')::UUID);

-- Trigger updated_at
CREATE OR REPLACE FUNCTION update_qr_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_qr_sessions_updated_at
    BEFORE UPDATE ON qr_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_qr_sessions_updated_at();

-- =============================================================================
-- Index sur categorie_bien pour les tables existantes
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_dossiers_categorie_bien
    ON dossiers(categorie_bien);

CREATE INDEX IF NOT EXISTS idx_promesses_categorie_bien
    ON promesses_generees(categorie_bien);
