-- =============================================================================
-- Migration: Fix conversations schema
-- Date: 11 fevrier 2026
-- Auteur: Claude Opus 4.5
--
-- Probleme: Le code Python utilise des colonnes qui n'existent pas:
--   - agent_state
--   - messages (JSONB)
--   - message_count
--   - last_message_at
--   - context (le code ecrit "context" mais la colonne s'appelle "contexte")
-- =============================================================================

-- 1. Ajouter les colonnes manquantes
ALTER TABLE conversations
  ADD COLUMN IF NOT EXISTS agent_state JSONB DEFAULT '{}';

ALTER TABLE conversations
  ADD COLUMN IF NOT EXISTS messages JSONB DEFAULT '[]';

ALTER TABLE conversations
  ADD COLUMN IF NOT EXISTS message_count INTEGER DEFAULT 0;

ALTER TABLE conversations
  ADD COLUMN IF NOT EXISTS last_message_at TIMESTAMPTZ;

-- 2. Ajouter colonne "context" comme alias (le code Python utilise "context")
-- On garde "contexte" pour compatibilite arriere et on ajoute "context"
ALTER TABLE conversations
  ADD COLUMN IF NOT EXISTS context JSONB DEFAULT '{}';

-- 3. Migrer les donnees existantes de "contexte" vers "context"
UPDATE conversations
SET context = contexte
WHERE context = '{}' AND contexte != '{}';

-- 4. Index pour performance sur les nouvelles colonnes
CREATE INDEX IF NOT EXISTS idx_conversations_last_message
  ON conversations(last_message_at DESC NULLS LAST);

-- 5. Trigger pour synchroniser contexte <-> context (optionnel, pour transition)
-- Quand on ecrit dans "context", ca met aussi a jour "contexte"
CREATE OR REPLACE FUNCTION sync_context_columns()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.context IS DISTINCT FROM OLD.context THEN
    NEW.contexte := NEW.context;
  ELSIF NEW.contexte IS DISTINCT FROM OLD.contexte THEN
    NEW.context := NEW.contexte;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sync_context ON conversations;
CREATE TRIGGER trg_sync_context
  BEFORE UPDATE ON conversations
  FOR EACH ROW
  EXECUTE FUNCTION sync_context_columns();

-- 6. Commentaires pour documentation
COMMENT ON COLUMN conversations.agent_state IS 'Etat de l''agent Anthropic (donnees_collectees, progress, etc.)';
COMMENT ON COLUMN conversations.messages IS 'Historique des messages JSONB (alternative a conversation_messages)';
COMMENT ON COLUMN conversations.message_count IS 'Nombre total de messages dans la conversation';
COMMENT ON COLUMN conversations.last_message_at IS 'Timestamp du dernier message';
COMMENT ON COLUMN conversations.context IS 'Contexte de la conversation (alias de contexte pour compatibilite code Python)';

-- =============================================================================
-- Verification: Afficher les colonnes apres migration
-- =============================================================================
-- SELECT column_name, data_type, column_default
-- FROM information_schema.columns
-- WHERE table_name = 'conversations'
-- ORDER BY ordinal_position;
