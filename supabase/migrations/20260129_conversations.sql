-- Migration: Tables pour la persistance conversationnelle du chat
-- Date: 2026-01-29
-- Description: Conversations et messages pour le chatbot notaire

-- =============================================================================
-- Table: conversations
-- Une conversation = un échange multi-tours avec un notaire
-- =============================================================================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etude_id UUID NOT NULL REFERENCES etudes(id),
    user_id TEXT,
    titre TEXT,
    type_acte TEXT,
    statut TEXT DEFAULT 'active' CHECK (statut IN ('active', 'terminee', 'abandonnee')),
    contexte JSONB DEFAULT '{}',
    donnees_collectees JSONB DEFAULT '{}',
    dossier_id UUID REFERENCES dossiers(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- Table: conversation_messages
-- Messages individuels dans une conversation
-- =============================================================================

CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    intention TEXT,
    confiance FLOAT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- RLS (Row Level Security)
-- =============================================================================

ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "conversations_etude_isolation" ON conversations
    FOR ALL USING (etude_id = current_setting('app.etude_id', true)::UUID);

CREATE POLICY "messages_via_conversation" ON conversation_messages
    FOR ALL USING (
        conversation_id IN (
            SELECT id FROM conversations
            WHERE etude_id = current_setting('app.etude_id', true)::UUID
        )
    );

-- =============================================================================
-- Index
-- =============================================================================

CREATE INDEX idx_conversations_etude ON conversations(etude_id);
CREATE INDEX idx_conversations_statut ON conversations(statut) WHERE statut = 'active';
CREATE INDEX idx_messages_conversation ON conversation_messages(conversation_id);
CREATE INDEX idx_messages_created ON conversation_messages(created_at);

-- =============================================================================
-- Trigger: updated_at auto-update
-- =============================================================================

CREATE OR REPLACE FUNCTION update_conversation_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_conversation_timestamp
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_timestamp();
