-- =============================================================================
-- MIGRATION 002: Row Level Security Policies
-- Date: 2026-01-21
-- Description: Politiques RLS pour isolation multi-tenant
-- =============================================================================

-- =============================================================================
-- HELPER FUNCTIONS
-- =============================================================================

-- Get user's etude_id from JWT claims or etude_users table
CREATE OR REPLACE FUNCTION get_user_etude_id()
RETURNS UUID AS $$
BEGIN
    -- First try JWT claim (faster)
    IF current_setting('request.jwt.claims', true)::json->>'etude_id' IS NOT NULL THEN
        RETURN (current_setting('request.jwt.claims', true)::json->>'etude_id')::UUID;
    END IF;

    -- Fallback to etude_users table
    RETURN (
        SELECT etude_id
        FROM etude_users
        WHERE user_id = auth.uid()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION get_user_etude_id() IS 'Retourne l etude_id de l utilisateur connecte';

-- Check if user has specific role
CREATE OR REPLACE FUNCTION user_has_role(required_role TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM etude_users
        WHERE user_id = auth.uid()
        AND role = required_role
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION user_has_role(TEXT) IS 'Verifie si l utilisateur a le role specifie';

-- Check if user has any of the specified roles
CREATE OR REPLACE FUNCTION user_has_any_role(required_roles TEXT[])
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM etude_users
        WHERE user_id = auth.uid()
        AND role = ANY(required_roles)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

-- =============================================================================
-- ENABLE RLS ON ALL TABLES
-- =============================================================================

ALTER TABLE etudes ENABLE ROW LEVEL SECURITY;
ALTER TABLE etude_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE dossiers ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- ETUDES POLICIES
-- =============================================================================

-- Users can view their own etude
CREATE POLICY "etudes_select_own"
    ON etudes FOR SELECT
    TO authenticated
    USING (id = get_user_etude_id());

-- Only admins can update etude settings
CREATE POLICY "etudes_update_admin"
    ON etudes FOR UPDATE
    TO authenticated
    USING (id = get_user_etude_id() AND user_has_role('admin'))
    WITH CHECK (id = get_user_etude_id() AND user_has_role('admin'));

-- Service role can do everything (for migrations/admin)
CREATE POLICY "etudes_service_role"
    ON etudes FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- ETUDE_USERS POLICIES
-- =============================================================================

-- Users can view colleagues in same etude
CREATE POLICY "etude_users_select_colleagues"
    ON etude_users FOR SELECT
    TO authenticated
    USING (etude_id = get_user_etude_id());

-- Only admins can manage users
CREATE POLICY "etude_users_admin_insert"
    ON etude_users FOR INSERT
    TO authenticated
    WITH CHECK (etude_id = get_user_etude_id() AND user_has_role('admin'));

CREATE POLICY "etude_users_admin_update"
    ON etude_users FOR UPDATE
    TO authenticated
    USING (etude_id = get_user_etude_id() AND user_has_role('admin'))
    WITH CHECK (etude_id = get_user_etude_id() AND user_has_role('admin'));

CREATE POLICY "etude_users_admin_delete"
    ON etude_users FOR DELETE
    TO authenticated
    USING (etude_id = get_user_etude_id() AND user_has_role('admin'));

-- Service role
CREATE POLICY "etude_users_service_role"
    ON etude_users FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- CLIENTS POLICIES
-- =============================================================================

-- Users can view active (non-deleted, non-anonymized) clients in their etude
CREATE POLICY "clients_select_active"
    ON clients FOR SELECT
    TO authenticated
    USING (
        etude_id = get_user_etude_id()
        AND deleted_at IS NULL
        AND anonymized = false
    );

-- Users can insert clients in their etude
CREATE POLICY "clients_insert"
    ON clients FOR INSERT
    TO authenticated
    WITH CHECK (etude_id = get_user_etude_id());

-- Users can update clients in their etude (except anonymized ones)
CREATE POLICY "clients_update"
    ON clients FOR UPDATE
    TO authenticated
    USING (
        etude_id = get_user_etude_id()
        AND anonymized = false
    )
    WITH CHECK (etude_id = get_user_etude_id());

-- Soft delete policy: only notaires/admins can delete (set deleted_at)
CREATE POLICY "clients_soft_delete"
    ON clients FOR UPDATE
    TO authenticated
    USING (
        etude_id = get_user_etude_id()
        AND user_has_any_role(ARRAY['notaire', 'admin'])
    )
    WITH CHECK (
        etude_id = get_user_etude_id()
        AND deleted_at IS NOT NULL  -- Only allows setting deleted_at
    );

-- Service role (for GDPR anonymization, imports)
CREATE POLICY "clients_service_role"
    ON clients FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- DOSSIERS POLICIES
-- =============================================================================

-- Users can view active dossiers in their etude
CREATE POLICY "dossiers_select_active"
    ON dossiers FOR SELECT
    TO authenticated
    USING (
        etude_id = get_user_etude_id()
        AND deleted_at IS NULL
    );

-- Users can insert dossiers in their etude
CREATE POLICY "dossiers_insert"
    ON dossiers FOR INSERT
    TO authenticated
    WITH CHECK (etude_id = get_user_etude_id());

-- Users can update dossiers in their etude
CREATE POLICY "dossiers_update"
    ON dossiers FOR UPDATE
    TO authenticated
    USING (etude_id = get_user_etude_id() AND deleted_at IS NULL)
    WITH CHECK (etude_id = get_user_etude_id());

-- Only notaires/admins can archive/delete dossiers
CREATE POLICY "dossiers_archive"
    ON dossiers FOR UPDATE
    TO authenticated
    USING (
        etude_id = get_user_etude_id()
        AND user_has_any_role(ARRAY['notaire', 'admin'])
    )
    WITH CHECK (
        etude_id = get_user_etude_id()
        AND (deleted_at IS NOT NULL OR statut = 'archive')
    );

-- Service role
CREATE POLICY "dossiers_service_role"
    ON dossiers FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- VIEWS FOR CONVENIENCE
-- =============================================================================

-- Active clients view (commonly used)
CREATE OR REPLACE VIEW clients_active AS
SELECT *
FROM clients
WHERE deleted_at IS NULL
AND anonymized = false;

COMMENT ON VIEW clients_active IS 'Vue des clients actifs (non supprimes, non anonymises)';

-- Active dossiers view
CREATE OR REPLACE VIEW dossiers_active AS
SELECT *
FROM dossiers
WHERE deleted_at IS NULL;

COMMENT ON VIEW dossiers_active IS 'Vue des dossiers actifs (non supprimes)';
