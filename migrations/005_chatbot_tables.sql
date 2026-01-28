-- ============================================================================
-- MIGRATION 005: Tables pour le Chatbot NotaireAI
-- Date: 2026-01-27
-- Description: Ajoute les tables conversations et feedbacks pour le chatbot
--              avec apprentissage continu (self-annealing)
-- ============================================================================

-- ============================================================================
-- TABLE 1: conversations
-- Stocke l'historique des conversations entre notaires et l'agent
-- ============================================================================

CREATE TABLE IF NOT EXISTS conversations (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    etude_id UUID NOT NULL REFERENCES etudes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

    -- Timestamps
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ,  -- NULL si conversation en cours

    -- Contenu
    -- Format messages: [{ "role": "user"|"assistant", "content": "...", "timestamp": "...", "metadata": {} }]
    messages JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- Contexte de la conversation (dossier actif, client sélectionné, etc.)
    context JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Statistiques
    message_count INT NOT NULL DEFAULT 0,
    feedback_count INT NOT NULL DEFAULT 0,
    positive_feedback_count INT NOT NULL DEFAULT 0,

    -- Métadonnées
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour recherche rapide
CREATE INDEX idx_conversations_etude ON conversations(etude_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_last_message ON conversations(last_message_at DESC);
CREATE INDEX idx_conversations_active ON conversations(etude_id, user_id) WHERE ended_at IS NULL;

-- Commentaire
COMMENT ON TABLE conversations IS 'Historique des conversations chatbot par utilisateur et étude';

-- ============================================================================
-- TABLE 2: feedbacks
-- Stocke les retours des notaires pour l'apprentissage continu
-- ============================================================================

CREATE TABLE IF NOT EXISTS feedbacks (
    -- Identifiants
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    etude_id UUID NOT NULL REFERENCES etudes(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    message_index INT NOT NULL,  -- Index du message dans la conversation

    -- Ce que l'agent a fait
    agent_intention TEXT,  -- 'CREER', 'MODIFIER', 'RECHERCHER', 'QUESTION'
    agent_response TEXT NOT NULL,  -- La réponse de l'agent
    agent_action JSONB,  -- L'action exécutée (si applicable)
    agent_confidence DECIMAL(3,2),  -- Score de confiance 0.00-1.00

    -- Feedback du notaire
    rating INT CHECK (rating BETWEEN -1 AND 5),  -- -1=négatif, 0=neutre, 1-5=positif
    correction TEXT,  -- Texte de correction libre
    correct_intention TEXT,  -- La bonne intention (si différente)
    correct_response TEXT,  -- Ce qu'il aurait fallu répondre

    -- Catégorisation pour l'apprentissage
    feedback_type TEXT CHECK (feedback_type IN (
        'vocabulaire',      -- Correction de terminologie
        'intention',        -- Mauvaise compréhension de l'intention
        'clause',           -- Nouvelle clause à ajouter
        'question',         -- Question mal formulée
        'erreur_donnees',   -- Erreur dans les données
        'erreur_logique',   -- Erreur de logique/workflow
        'suggestion',       -- Suggestion d'amélioration
        'compliment',       -- Feedback positif
        'autre'
    )),

    -- Tags pour filtrage (ex: ['vente', 'client', 'prix'])
    tags TEXT[] DEFAULT '{}',

    -- Suivi de l'apprentissage
    applied BOOLEAN NOT NULL DEFAULT false,  -- Feedback intégré dans le système ?
    applied_at TIMESTAMPTZ,
    applied_to TEXT,  -- Fichier modifié: 'clauses_catalogue.json', etc.
    applied_by UUID REFERENCES auth.users(id),
    application_notes TEXT,  -- Notes sur comment ça a été appliqué

    -- Priorité pour traitement (auto-calculée ou manuelle)
    priority INT DEFAULT 0,  -- 0=normal, 1=important, 2=critique

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index pour recherche et analyse
CREATE INDEX idx_feedbacks_conversation ON feedbacks(conversation_id);
CREATE INDEX idx_feedbacks_etude ON feedbacks(etude_id);
CREATE INDEX idx_feedbacks_type ON feedbacks(feedback_type);
CREATE INDEX idx_feedbacks_not_applied ON feedbacks(applied, created_at) WHERE applied = false;
CREATE INDEX idx_feedbacks_rating ON feedbacks(rating) WHERE rating IS NOT NULL;
CREATE INDEX idx_feedbacks_priority ON feedbacks(priority DESC, created_at DESC);

-- Commentaire
COMMENT ON TABLE feedbacks IS 'Retours des notaires pour apprentissage continu (self-annealing)';

-- ============================================================================
-- RLS: Row Level Security
-- Chaque utilisateur ne voit que les données de son étude
-- ============================================================================

-- Activer RLS
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedbacks ENABLE ROW LEVEL SECURITY;

-- Policies pour conversations
CREATE POLICY "Users can view their own conversations"
    ON conversations FOR SELECT
    USING (user_id = auth.uid() OR etude_id IN (
        SELECT etude_id FROM etude_users WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can create their own conversations"
    ON conversations FOR INSERT
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own conversations"
    ON conversations FOR UPDATE
    USING (user_id = auth.uid());

-- Policies pour feedbacks
CREATE POLICY "Users can view feedbacks from their etude"
    ON feedbacks FOR SELECT
    USING (etude_id IN (
        SELECT etude_id FROM etude_users WHERE user_id = auth.uid()
    ));

CREATE POLICY "Users can create feedbacks"
    ON feedbacks FOR INSERT
    WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own feedbacks"
    ON feedbacks FOR UPDATE
    USING (user_id = auth.uid());

-- Admin peut tout voir pour analyser les feedbacks
CREATE POLICY "Admins can view all feedbacks"
    ON feedbacks FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM etude_users
        WHERE user_id = auth.uid() AND role = 'admin'
    ));

-- ============================================================================
-- TRIGGERS: Mise à jour automatique
-- ============================================================================

-- Trigger pour updated_at sur conversations
CREATE OR REPLACE FUNCTION update_conversations_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_conversations_updated_at
    BEFORE UPDATE ON conversations
    FOR EACH ROW
    EXECUTE FUNCTION update_conversations_updated_at();

-- Trigger pour updated_at sur feedbacks
CREATE OR REPLACE FUNCTION update_feedbacks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_feedbacks_updated_at
    BEFORE UPDATE ON feedbacks
    FOR EACH ROW
    EXECUTE FUNCTION update_feedbacks_updated_at();

-- Trigger pour mettre à jour les compteurs dans conversations
CREATE OR REPLACE FUNCTION update_conversation_feedback_counts()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE conversations
        SET
            feedback_count = feedback_count + 1,
            positive_feedback_count = positive_feedback_count + CASE WHEN NEW.rating > 0 THEN 1 ELSE 0 END
        WHERE id = NEW.conversation_id;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Si le rating change
        IF OLD.rating IS DISTINCT FROM NEW.rating THEN
            UPDATE conversations
            SET positive_feedback_count = positive_feedback_count
                - CASE WHEN OLD.rating > 0 THEN 1 ELSE 0 END
                + CASE WHEN NEW.rating > 0 THEN 1 ELSE 0 END
            WHERE id = NEW.conversation_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE conversations
        SET
            feedback_count = feedback_count - 1,
            positive_feedback_count = positive_feedback_count - CASE WHEN OLD.rating > 0 THEN 1 ELSE 0 END
        WHERE id = OLD.conversation_id;
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_conversation_feedback_counts
    AFTER INSERT OR UPDATE OR DELETE ON feedbacks
    FOR EACH ROW
    EXECUTE FUNCTION update_conversation_feedback_counts();

-- ============================================================================
-- VUE: feedbacks_pending
-- Vue des feedbacks en attente d'application (pour le tableau de bord admin)
-- ============================================================================

CREATE OR REPLACE VIEW feedbacks_pending AS
SELECT
    f.id,
    f.feedback_type,
    f.rating,
    f.correction,
    f.agent_response,
    f.correct_response,
    f.tags,
    f.priority,
    f.created_at,
    c.messages->f.message_index AS original_message,
    e.nom AS etude_nom
FROM feedbacks f
JOIN conversations c ON f.conversation_id = c.id
JOIN etudes e ON f.etude_id = e.id
WHERE f.applied = false
ORDER BY f.priority DESC, f.created_at DESC;

COMMENT ON VIEW feedbacks_pending IS 'Feedbacks en attente d application pour amélioration continue';

-- ============================================================================
-- VUE: conversation_stats
-- Statistiques des conversations par étude
-- ============================================================================

CREATE OR REPLACE VIEW conversation_stats AS
SELECT
    etude_id,
    COUNT(*) AS total_conversations,
    SUM(message_count) AS total_messages,
    SUM(feedback_count) AS total_feedbacks,
    SUM(positive_feedback_count) AS positive_feedbacks,
    ROUND(
        SUM(positive_feedback_count)::DECIMAL / NULLIF(SUM(feedback_count), 0) * 100,
        1
    ) AS satisfaction_rate,
    MAX(last_message_at) AS last_activity
FROM conversations
GROUP BY etude_id;

COMMENT ON VIEW conversation_stats IS 'Statistiques des conversations par étude';
