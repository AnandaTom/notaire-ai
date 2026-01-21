-- =============================================================================
-- MIGRATION 003: Comprehensive Audit Trail
-- Date: 2026-01-21
-- Description: Logs d'audit avec retention 3 ans (conformite RGPD)
-- =============================================================================

-- =============================================================================
-- AUDIT_LOGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Qui ?
    user_id UUID REFERENCES auth.users(id),
    user_email TEXT,
    etude_id UUID REFERENCES etudes(id),
    user_role TEXT,

    -- Quoi ?
    action TEXT NOT NULL,  -- 'create', 'read', 'update', 'delete', 'export', 'import', 'search', 'anonymize'
    resource_type TEXT NOT NULL,  -- 'client', 'dossier', 'acte', 'file'
    resource_id UUID,

    -- Details
    details JSONB DEFAULT '{}',  -- {old_values: {}, new_values: {}, reason: ""}
    sensitive_fields_accessed TEXT[],  -- ['nom', 'email'] pour tracking RGPD

    -- Context
    ip_address INET,
    user_agent TEXT,
    session_id TEXT,

    -- Quand ?
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Retention (3 ans pour conformite legale)
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '3 years'
);

COMMENT ON TABLE audit_logs IS 'Logs d audit securite - Retention 3 ans (Art. 30 RGPD)';
COMMENT ON COLUMN audit_logs.action IS 'Type d action: create, read, update, delete, export, import, search, anonymize';
COMMENT ON COLUMN audit_logs.sensitive_fields_accessed IS 'Liste des champs PII accedes (pour reporting RGPD)';
COMMENT ON COLUMN audit_logs.expires_at IS 'Date d expiration - suppression automatique apres 3 ans';

-- =============================================================================
-- INDEXES FOR AUDIT QUERIES
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_etude ON audit_logs(etude_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_expires ON audit_logs(expires_at);
CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_logs(created_at DESC);

-- =============================================================================
-- RLS POLICIES FOR AUDIT_LOGS
-- =============================================================================
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Only admins and notaires can view audit logs of their etude
CREATE POLICY "audit_logs_select"
    ON audit_logs FOR SELECT
    TO authenticated
    USING (
        etude_id = get_user_etude_id()
        AND user_has_any_role(ARRAY['admin', 'notaire'])
    );

-- Insert allowed for all authenticated users (via application)
CREATE POLICY "audit_logs_insert"
    ON audit_logs FOR INSERT
    TO authenticated
    WITH CHECK (etude_id = get_user_etude_id());

-- Service role can do everything
CREATE POLICY "audit_logs_service_role"
    ON audit_logs FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- AUTOMATIC AUDIT LOGGING TRIGGER
-- =============================================================================
CREATE OR REPLACE FUNCTION log_data_change()
RETURNS TRIGGER AS $$
DECLARE
    v_action TEXT;
    v_old_data JSONB;
    v_new_data JSONB;
    v_user_id UUID;
    v_etude_id UUID;
BEGIN
    -- Determine action
    IF TG_OP = 'INSERT' THEN
        v_action := 'create';
        v_new_data := to_jsonb(NEW);
        v_etude_id := NEW.etude_id;
    ELSIF TG_OP = 'UPDATE' THEN
        v_action := 'update';
        v_old_data := to_jsonb(OLD);
        v_new_data := to_jsonb(NEW);
        v_etude_id := COALESCE(NEW.etude_id, OLD.etude_id);

        -- Detect anonymization
        IF OLD.anonymized = false AND NEW.anonymized = true THEN
            v_action := 'anonymize';
        END IF;

        -- Detect soft delete
        IF OLD.deleted_at IS NULL AND NEW.deleted_at IS NOT NULL THEN
            v_action := 'delete';
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        v_action := 'delete';
        v_old_data := to_jsonb(OLD);
        v_etude_id := OLD.etude_id;
    END IF;

    -- Get current user
    v_user_id := auth.uid();

    -- Insert audit record
    INSERT INTO audit_logs (
        user_id,
        etude_id,
        action,
        resource_type,
        resource_id,
        details
    ) VALUES (
        v_user_id,
        v_etude_id,
        v_action,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        jsonb_build_object(
            'old_values', v_old_data,
            'new_values', v_new_data,
            'trigger', TG_NAME
        )
    );

    RETURN COALESCE(NEW, OLD);
EXCEPTION
    WHEN OTHERS THEN
        -- Don't fail the main operation if audit logging fails
        RAISE WARNING 'Audit logging failed: %', SQLERRM;
        RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply audit triggers to tables
DROP TRIGGER IF EXISTS audit_clients_changes ON clients;
CREATE TRIGGER audit_clients_changes
    AFTER INSERT OR UPDATE OR DELETE ON clients
    FOR EACH ROW EXECUTE FUNCTION log_data_change();

DROP TRIGGER IF EXISTS audit_dossiers_changes ON dossiers;
CREATE TRIGGER audit_dossiers_changes
    AFTER INSERT OR UPDATE OR DELETE ON dossiers
    FOR EACH ROW EXECUTE FUNCTION log_data_change();

-- =============================================================================
-- MANUAL AUDIT LOGGING FUNCTION (for reads, searches, exports)
-- =============================================================================
CREATE OR REPLACE FUNCTION log_audit_event(
    p_action TEXT,
    p_resource_type TEXT,
    p_resource_id UUID DEFAULT NULL,
    p_details JSONB DEFAULT '{}',
    p_sensitive_fields TEXT[] DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO audit_logs (
        user_id,
        etude_id,
        action,
        resource_type,
        resource_id,
        details,
        sensitive_fields_accessed
    ) VALUES (
        auth.uid(),
        get_user_etude_id(),
        p_action,
        p_resource_type,
        p_resource_id,
        p_details,
        p_sensitive_fields
    )
    RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION log_audit_event IS 'Log manuel d un evenement d audit (lectures, recherches, exports)';

-- =============================================================================
-- CLEANUP FUNCTION FOR EXPIRED LOGS
-- =============================================================================
CREATE OR REPLACE FUNCTION cleanup_expired_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM audit_logs WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    -- Log the cleanup itself
    PERFORM log_audit_event(
        'cleanup',
        'audit_logs',
        NULL,
        jsonb_build_object('deleted_count', deleted_count)
    );

    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION cleanup_expired_audit_logs IS 'Supprime les logs expires (executer via cron Supabase)';

-- =============================================================================
-- AUDIT SUMMARY VIEW
-- =============================================================================
CREATE OR REPLACE VIEW audit_summary AS
SELECT
    etude_id,
    resource_type,
    action,
    DATE_TRUNC('day', created_at) as day,
    COUNT(*) as count
FROM audit_logs
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY etude_id, resource_type, action, DATE_TRUNC('day', created_at)
ORDER BY day DESC, count DESC;

COMMENT ON VIEW audit_summary IS 'Resume des actions d audit des 30 derniers jours';
