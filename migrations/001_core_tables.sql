-- =============================================================================
-- MIGRATION 001: Core Tables with Multi-tenant Security
-- Date: 2026-01-21
-- Description: Tables de base pour gestion clients NotaireAI avec chiffrement
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- ETUDES (Law Firms/Offices) - Multi-tenant anchor
-- =============================================================================
CREATE TABLE IF NOT EXISTS etudes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nom TEXT NOT NULL,
    siret TEXT UNIQUE,
    adresse TEXT,
    email_contact TEXT,
    telephone TEXT,

    -- Supabase Auth integration
    owner_user_id UUID REFERENCES auth.users(id),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- RGPD / DPA
    dpa_signed_at TIMESTAMPTZ,
    rgpd_consent BOOLEAN DEFAULT false
);

COMMENT ON TABLE etudes IS 'Etudes notariales - Ancre multi-tenant pour isolation des donnees';
COMMENT ON COLUMN etudes.dpa_signed_at IS 'Date de signature du DPA Supabase (Art. 28 RGPD)';

-- =============================================================================
-- ETUDE_USERS - Users within an etude (notaires, clerks, agents)
-- =============================================================================
CREATE TABLE IF NOT EXISTS etude_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    etude_id UUID REFERENCES etudes(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('notaire', 'clerc', 'agent_ia', 'admin')),

    -- Security
    permissions JSONB DEFAULT '{}',
    last_login_at TIMESTAMPTZ,
    mfa_enabled BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(user_id, etude_id)
);

COMMENT ON TABLE etude_users IS 'Association utilisateurs-etudes avec roles';
COMMENT ON COLUMN etude_users.role IS 'Role: notaire, clerc, agent_ia, admin';

-- =============================================================================
-- CLIENTS - Table principale avec champs chiffres
-- =============================================================================
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    etude_id UUID NOT NULL REFERENCES etudes(id) ON DELETE CASCADE,

    -- GenApi sync
    genapi_id TEXT,
    genapi_data JSONB,
    last_genapi_sync TIMESTAMPTZ,

    -- Champs PII chiffres (stockent JSON chiffre AES-256-GCM)
    nom_encrypted TEXT NOT NULL,
    prenom_encrypted TEXT,
    email_encrypted TEXT,
    telephone_encrypted TEXT,
    adresse_encrypted TEXT,

    -- Hash pour recherche (non-reversible)
    nom_hash TEXT,

    -- Donnees non-sensibles (en clair)
    type_personne TEXT CHECK (type_personne IN ('physique', 'morale')) DEFAULT 'physique',
    civilite TEXT,
    date_naissance DATE,
    lieu_naissance TEXT,
    nationalite TEXT,
    profession TEXT,
    situation_matrimoniale TEXT,

    -- Enrichissements Agent IA
    ai_enrichments JSONB DEFAULT '{}',
    ai_summary TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),
    source TEXT CHECK (source IN ('genapi_import', 'agent_ia', 'manual', 'conversation')) DEFAULT 'manual',

    -- RGPD soft delete
    deleted_at TIMESTAMPTZ,
    anonymized BOOLEAN DEFAULT false,
    anonymized_at TIMESTAMPTZ,
    data_retention_until DATE
);

COMMENT ON TABLE clients IS 'Clients avec PII chiffre - Conforme RGPD';
COMMENT ON COLUMN clients.nom_encrypted IS 'Nom chiffre AES-256-GCM (JSON avec nonce, ciphertext, key_id)';
COMMENT ON COLUMN clients.nom_hash IS 'Hash SHA-256 normalise pour recherche sans dechiffrement';
COMMENT ON COLUMN clients.source IS 'Source des donnees: genapi_import, agent_ia, manual, conversation';
COMMENT ON COLUMN clients.anonymized IS 'True si donnees anonymisees suite demande effacement RGPD';

-- =============================================================================
-- DOSSIERS (Cases/Files)
-- =============================================================================
CREATE TABLE IF NOT EXISTS dossiers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    etude_id UUID NOT NULL REFERENCES etudes(id) ON DELETE CASCADE,
    numero TEXT NOT NULL,

    type_acte TEXT NOT NULL,
    statut TEXT DEFAULT 'brouillon' CHECK (statut IN ('brouillon', 'en_cours', 'termine', 'archive')),

    -- Parties (references to clients with roles)
    parties JSONB DEFAULT '[]',  -- [{client_id: uuid, role: "vendeur"}]

    -- Structured data
    biens JSONB DEFAULT '[]',
    donnees_metier JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id),

    -- Soft delete
    deleted_at TIMESTAMPTZ,

    UNIQUE(etude_id, numero)
);

COMMENT ON TABLE dossiers IS 'Dossiers notariaux avec parties liees aux clients';
COMMENT ON COLUMN dossiers.parties IS 'JSON Array: [{client_id: UUID, role: "vendeur"|"acquereur"|...}]';

-- =============================================================================
-- INDEXES
-- =============================================================================

-- Clients
CREATE INDEX IF NOT EXISTS idx_clients_etude ON clients(etude_id);
CREATE INDEX IF NOT EXISTS idx_clients_nom_hash ON clients(nom_hash);
CREATE INDEX IF NOT EXISTS idx_clients_source ON clients(source);
CREATE INDEX IF NOT EXISTS idx_clients_active ON clients(etude_id) WHERE deleted_at IS NULL AND anonymized = false;
CREATE INDEX IF NOT EXISTS idx_clients_genapi ON clients(genapi_id) WHERE genapi_id IS NOT NULL;

-- Dossiers
CREATE INDEX IF NOT EXISTS idx_dossiers_etude ON dossiers(etude_id);
CREATE INDEX IF NOT EXISTS idx_dossiers_numero ON dossiers(numero);
CREATE INDEX IF NOT EXISTS idx_dossiers_statut ON dossiers(statut);
CREATE INDEX IF NOT EXISTS idx_dossiers_active ON dossiers(etude_id) WHERE deleted_at IS NULL;

-- Etude users
CREATE INDEX IF NOT EXISTS idx_etude_users_user ON etude_users(user_id);
CREATE INDEX IF NOT EXISTS idx_etude_users_etude ON etude_users(etude_id);

-- =============================================================================
-- UPDATED_AT TRIGGER
-- =============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dossiers_updated_at
    BEFORE UPDATE ON dossiers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_etudes_updated_at
    BEFORE UPDATE ON etudes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
