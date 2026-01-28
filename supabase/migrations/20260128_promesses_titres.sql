-- Migration: Tables pour la gestion des promesses et titres de propriété
-- Date: 2026-01-28
-- Description: Création des tables pour stocker les titres extraits et les promesses générées

-- =============================================================================
-- Table: titres_propriete
-- Stocke les titres de propriété extraits (PDF/DOCX)
-- =============================================================================

CREATE TABLE IF NOT EXISTS titres_propriete (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etude_id UUID NOT NULL REFERENCES etudes(id),

    -- Référence et identification
    reference VARCHAR(100),
    nom_fichier_source VARCHAR(255),
    type_extraction VARCHAR(50) DEFAULT 'auto', -- 'auto', 'manuel', 'ocr'
    confiance_extraction DECIMAL(5,2), -- Score de confiance 0-100

    -- Propriétaires actuels (JSONB pour flexibilité)
    proprietaires JSONB NOT NULL DEFAULT '[]',
    -- Structure: [{nom, prenoms, date_naissance, adresse, situation_matrimoniale, quotite}]

    -- Bien immobilier
    bien JSONB NOT NULL DEFAULT '{}',
    -- Structure: {adresse, code_postal, ville, cadastre: {section, numero, surface}, lots: [...]}

    -- Origine de propriété
    origine JSONB DEFAULT '{}',
    -- Structure: {type_acte, date, notaire, reference, details}

    -- Copropriété
    copropriete JSONB DEFAULT '{}',
    -- Structure: {syndic: {nom, adresse}, edd: {date, notaire}, immatriculation}

    -- Servitudes et charges
    servitudes JSONB DEFAULT '[]',
    -- Structure: [{type, description, beneficiaire}]

    -- Métadonnées
    metadata JSONB DEFAULT '{}',
    -- Structure: {pages, date_extraction, version_extracteur}

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT titres_proprietaires_not_empty CHECK (jsonb_array_length(proprietaires) > 0)
);

-- Index pour recherche rapide
CREATE INDEX idx_titres_etude ON titres_propriete(etude_id);
CREATE INDEX idx_titres_reference ON titres_propriete(reference);
CREATE INDEX idx_titres_bien_adresse ON titres_propriete USING GIN ((bien->'adresse'));
CREATE INDEX idx_titres_proprietaires ON titres_propriete USING GIN (proprietaires);

-- RLS (Row Level Security)
ALTER TABLE titres_propriete ENABLE ROW LEVEL SECURITY;

CREATE POLICY "titres_etude_policy" ON titres_propriete
    FOR ALL USING (etude_id = auth.uid() OR etude_id IN (
        SELECT etude_id FROM utilisateurs WHERE user_id = auth.uid()
    ));


-- =============================================================================
-- Table: promesses_generees
-- Stocke les promesses de vente générées
-- =============================================================================

CREATE TABLE IF NOT EXISTS promesses_generees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etude_id UUID NOT NULL REFERENCES etudes(id),

    -- Type et référence
    type_promesse VARCHAR(50) NOT NULL, -- 'standard', 'premium', 'avec_mobilier', 'multi_biens'
    reference VARCHAR(100),
    titre_source_id UUID REFERENCES titres_propriete(id), -- Lien vers titre si généré depuis titre

    -- Parties
    promettants JSONB NOT NULL DEFAULT '[]',
    beneficiaires JSONB NOT NULL DEFAULT '[]',

    -- Bien(s)
    bien JSONB, -- Pour standard/premium/avec_mobilier
    biens JSONB, -- Pour multi_biens (array)

    -- Prix et financement
    prix JSONB NOT NULL,
    -- Structure: {montant, mobilier, frais_notaire, ventilation: [...]}
    financement JSONB DEFAULT '{}',
    -- Structure: {pret: bool, montant, taux_max, duree, organisme}

    -- Conditions
    conditions_suspensives JSONB DEFAULT '{}',
    indemnite JSONB DEFAULT '{}',
    sequestre JSONB DEFAULT '{}',

    -- Dates importantes
    date_promesse DATE,
    delai_realisation DATE,
    date_signature_prevue DATE,

    -- Fichiers générés
    fichier_md VARCHAR(500),
    fichier_docx VARCHAR(500),
    fichier_pdf VARCHAR(500),

    -- Sections incluses
    sections_incluses JSONB DEFAULT '[]',

    -- Statut
    statut VARCHAR(50) DEFAULT 'brouillon', -- 'brouillon', 'finalise', 'signe', 'caduque'

    -- Métadonnées
    metadata JSONB DEFAULT '{}',
    -- Structure: {duree_generation, template_version, profil_utilise}

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Contraintes
    CONSTRAINT promesses_type_valid CHECK (
        type_promesse IN ('standard', 'premium', 'avec_mobilier', 'multi_biens')
    ),
    CONSTRAINT promesses_statut_valid CHECK (
        statut IN ('brouillon', 'finalise', 'signe', 'caduque', 'annule')
    )
);

-- Index
CREATE INDEX idx_promesses_etude ON promesses_generees(etude_id);
CREATE INDEX idx_promesses_type ON promesses_generees(type_promesse);
CREATE INDEX idx_promesses_statut ON promesses_generees(statut);
CREATE INDEX idx_promesses_titre_source ON promesses_generees(titre_source_id);
CREATE INDEX idx_promesses_date ON promesses_generees(date_promesse DESC);

-- RLS
ALTER TABLE promesses_generees ENABLE ROW LEVEL SECURITY;

CREATE POLICY "promesses_etude_policy" ON promesses_generees
    FOR ALL USING (etude_id = auth.uid() OR etude_id IN (
        SELECT etude_id FROM utilisateurs WHERE user_id = auth.uid()
    ));


-- =============================================================================
-- Table: feedbacks_promesse
-- Retours notaires pour amélioration continue
-- =============================================================================

CREATE TABLE IF NOT EXISTS feedbacks_promesse (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    promesse_id UUID REFERENCES promesses_generees(id),
    etude_id UUID NOT NULL REFERENCES etudes(id),

    -- Feedback
    section_id VARCHAR(100), -- Section concernée
    action VARCHAR(50) NOT NULL, -- 'ajouter', 'modifier', 'supprimer', 'suggerer'
    contenu TEXT,
    raison TEXT,

    -- Validation
    approuve BOOLEAN DEFAULT FALSE,
    approuve_par UUID REFERENCES utilisateurs(id),
    approuve_at TIMESTAMPTZ,

    -- Métadonnées
    metadata JSONB DEFAULT '{}',

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_feedbacks_promesse ON feedbacks_promesse(promesse_id);
CREATE INDEX idx_feedbacks_etude ON feedbacks_promesse(etude_id);
CREATE INDEX idx_feedbacks_section ON feedbacks_promesse(section_id);
CREATE INDEX idx_feedbacks_approuve ON feedbacks_promesse(approuve);

-- RLS
ALTER TABLE feedbacks_promesse ENABLE ROW LEVEL SECURITY;

CREATE POLICY "feedbacks_etude_policy" ON feedbacks_promesse
    FOR ALL USING (etude_id = auth.uid() OR etude_id IN (
        SELECT etude_id FROM utilisateurs WHERE user_id = auth.uid()
    ));


-- =============================================================================
-- Fonctions utilitaires
-- =============================================================================

-- Fonction: Recherche titre par adresse (fuzzy)
CREATE OR REPLACE FUNCTION rechercher_titre_adresse(
    p_etude_id UUID,
    p_adresse TEXT
)
RETURNS TABLE (
    id UUID,
    reference VARCHAR,
    proprietaires JSONB,
    bien JSONB,
    score FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id,
        t.reference,
        t.proprietaires,
        t.bien,
        similarity(t.bien->>'adresse', p_adresse) as score
    FROM titres_propriete t
    WHERE t.etude_id = p_etude_id
    AND similarity(t.bien->>'adresse', p_adresse) > 0.3
    ORDER BY score DESC
    LIMIT 10;
END;
$$ LANGUAGE plpgsql;


-- Fonction: Convertir titre en promesse (données de base)
CREATE OR REPLACE FUNCTION titre_vers_promesse_data(
    p_titre_id UUID
)
RETURNS JSONB AS $$
DECLARE
    v_titre titres_propriete%ROWTYPE;
    v_result JSONB;
BEGIN
    SELECT * INTO v_titre FROM titres_propriete WHERE id = p_titre_id;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    v_result := jsonb_build_object(
        'titre_source_id', v_titre.id,
        'promettants', v_titre.proprietaires,
        'bien', v_titre.bien,
        'copropriete', v_titre.copropriete,
        'origine_propriete', v_titre.origine,
        'servitudes', v_titre.servitudes,
        '_a_completer', jsonb_build_array(
            'beneficiaires',
            'prix',
            'financement',
            'conditions_suspensives',
            'indemnite',
            'delai_realisation'
        )
    );

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;


-- Trigger: Mise à jour automatique de updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER titres_updated_at
    BEFORE UPDATE ON titres_propriete
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER promesses_updated_at
    BEFORE UPDATE ON promesses_generees
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();


-- =============================================================================
-- Vues utiles
-- =============================================================================

-- Vue: Promesses avec infos titre source
CREATE OR REPLACE VIEW v_promesses_avec_titre AS
SELECT
    p.*,
    t.reference as titre_reference,
    t.proprietaires as titre_proprietaires,
    t.bien as titre_bien
FROM promesses_generees p
LEFT JOIN titres_propriete t ON p.titre_source_id = t.id;


-- Vue: Statistiques par étude
CREATE OR REPLACE VIEW v_stats_promesses_etude AS
SELECT
    etude_id,
    COUNT(*) as total_promesses,
    COUNT(CASE WHEN type_promesse = 'standard' THEN 1 END) as promesses_standard,
    COUNT(CASE WHEN type_promesse = 'premium' THEN 1 END) as promesses_premium,
    COUNT(CASE WHEN type_promesse = 'avec_mobilier' THEN 1 END) as promesses_mobilier,
    COUNT(CASE WHEN type_promesse = 'multi_biens' THEN 1 END) as promesses_multi,
    COUNT(CASE WHEN statut = 'signe' THEN 1 END) as promesses_signees,
    COUNT(CASE WHEN titre_source_id IS NOT NULL THEN 1 END) as promesses_depuis_titre
FROM promesses_generees
GROUP BY etude_id;


-- =============================================================================
-- Commentaires
-- =============================================================================

COMMENT ON TABLE titres_propriete IS 'Titres de propriété extraits (source pour génération promesses/ventes)';
COMMENT ON TABLE promesses_generees IS 'Promesses de vente générées par Notomai';
COMMENT ON TABLE feedbacks_promesse IS 'Retours notaires pour amélioration continue du système';

COMMENT ON COLUMN titres_propriete.confiance_extraction IS 'Score de confiance de l''extraction automatique (0-100)';
COMMENT ON COLUMN promesses_generees.type_promesse IS 'Type: standard, premium, avec_mobilier, multi_biens';
COMMENT ON COLUMN promesses_generees.titre_source_id IS 'Référence au titre si promesse générée depuis extraction';
