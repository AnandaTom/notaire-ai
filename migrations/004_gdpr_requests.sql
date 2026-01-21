-- =============================================================================
-- MIGRATION 004: GDPR Rights Management
-- Date: 2026-01-21
-- Description: Gestion des demandes de droits RGPD (Art. 15-22)
-- =============================================================================

-- =============================================================================
-- RGPD_REQUESTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS rgpd_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Subject
    client_id UUID REFERENCES clients(id),
    etude_id UUID REFERENCES etudes(id),

    -- Request details
    request_type TEXT NOT NULL CHECK (request_type IN (
        'access',        -- Art. 15 - Droit d'acces
        'rectification', -- Art. 16 - Droit de rectification
        'erasure',       -- Art. 17 - Droit a l'effacement
        'portability',   -- Art. 20 - Droit a la portabilite
        'opposition'     -- Art. 21 - Droit d'opposition
    )),
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending',
        'processing',
        'completed',
        'rejected'
    )),

    -- Tracking
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    deadline_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '30 days',  -- RGPD 1-month deadline

    -- Contacts
    requested_by TEXT NOT NULL,  -- Email of requester
    processed_by UUID REFERENCES auth.users(id),

    -- Response
    response_data JSONB,
    rejection_reason TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    notes TEXT
);

COMMENT ON TABLE rgpd_requests IS 'Demandes de droits RGPD avec suivi des delais (30 jours max)';
COMMENT ON COLUMN rgpd_requests.request_type IS 'Type de demande: access (Art.15), rectification (Art.16), erasure (Art.17), portability (Art.20), opposition (Art.21)';
COMMENT ON COLUMN rgpd_requests.deadline_at IS 'Date limite de reponse (30 jours selon RGPD)';
COMMENT ON COLUMN rgpd_requests.rejection_reason IS 'Motif de refus (ex: obligation legale de conservation)';

-- =============================================================================
-- INDEXES
-- =============================================================================
CREATE INDEX IF NOT EXISTS idx_rgpd_deadline ON rgpd_requests(deadline_at) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_rgpd_client ON rgpd_requests(client_id);
CREATE INDEX IF NOT EXISTS idx_rgpd_etude ON rgpd_requests(etude_id);
CREATE INDEX IF NOT EXISTS idx_rgpd_status ON rgpd_requests(status);
CREATE INDEX IF NOT EXISTS idx_rgpd_type ON rgpd_requests(request_type);

-- =============================================================================
-- RLS POLICIES
-- =============================================================================
ALTER TABLE rgpd_requests ENABLE ROW LEVEL SECURITY;

-- Only notaires and admins can view GDPR requests
CREATE POLICY "rgpd_requests_select"
    ON rgpd_requests FOR SELECT
    TO authenticated
    USING (
        etude_id = get_user_etude_id()
        AND user_has_any_role(ARRAY['admin', 'notaire'])
    );

-- Only notaires and admins can create/update GDPR requests
CREATE POLICY "rgpd_requests_insert"
    ON rgpd_requests FOR INSERT
    TO authenticated
    WITH CHECK (
        etude_id = get_user_etude_id()
        AND user_has_any_role(ARRAY['admin', 'notaire'])
    );

CREATE POLICY "rgpd_requests_update"
    ON rgpd_requests FOR UPDATE
    TO authenticated
    USING (
        etude_id = get_user_etude_id()
        AND user_has_any_role(ARRAY['admin', 'notaire'])
    )
    WITH CHECK (
        etude_id = get_user_etude_id()
        AND user_has_any_role(ARRAY['admin', 'notaire'])
    );

-- Service role
CREATE POLICY "rgpd_requests_service_role"
    ON rgpd_requests FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- =============================================================================
-- VIEWS FOR MONITORING
-- =============================================================================

-- Overdue requests (need immediate attention)
CREATE OR REPLACE VIEW rgpd_overdue_requests AS
SELECT
    r.*,
    c.nom_hash,
    e.nom as etude_nom,
    NOW() - r.deadline_at as days_overdue
FROM rgpd_requests r
LEFT JOIN clients c ON r.client_id = c.id
LEFT JOIN etudes e ON r.etude_id = e.id
WHERE r.status = 'pending'
AND r.deadline_at < NOW();

COMMENT ON VIEW rgpd_overdue_requests IS 'Demandes RGPD en retard - Action immediate requise';

-- Pending requests dashboard
CREATE OR REPLACE VIEW rgpd_pending_dashboard AS
SELECT
    etude_id,
    request_type,
    COUNT(*) as pending_count,
    MIN(deadline_at) as earliest_deadline,
    COUNT(*) FILTER (WHERE deadline_at < NOW() + INTERVAL '7 days') as due_soon
FROM rgpd_requests
WHERE status = 'pending'
GROUP BY etude_id, request_type;

COMMENT ON VIEW rgpd_pending_dashboard IS 'Tableau de bord des demandes RGPD en attente';

-- =============================================================================
-- ANONYMIZATION FUNCTION (for erasure requests)
-- =============================================================================
CREATE OR REPLACE FUNCTION anonymize_client(p_client_id UUID, p_reason TEXT DEFAULT 'GDPR erasure request')
RETURNS BOOLEAN AS $$
DECLARE
    v_etude_id UUID;
BEGIN
    -- Get etude_id for RLS check
    SELECT etude_id INTO v_etude_id FROM clients WHERE id = p_client_id;

    -- Check if user has permission
    IF v_etude_id != get_user_etude_id() OR NOT user_has_any_role(ARRAY['admin', 'notaire']) THEN
        RAISE EXCEPTION 'Permission denied for anonymization';
    END IF;

    -- Check for legal hold (active dossiers)
    IF EXISTS (
        SELECT 1 FROM dossiers
        WHERE etude_id = v_etude_id
        AND parties @> jsonb_build_array(jsonb_build_object('client_id', p_client_id::text))
        AND statut IN ('en_cours', 'termine')
        AND deleted_at IS NULL
    ) THEN
        RAISE EXCEPTION 'Client has active dossiers - cannot anonymize (Art. 17.3.b RGPD)';
    END IF;

    -- Perform anonymization
    UPDATE clients SET
        nom_encrypted = 'ANONYMISE',
        prenom_encrypted = 'ANONYMISE',
        email_encrypted = NULL,
        telephone_encrypted = NULL,
        adresse_encrypted = NULL,
        nom_hash = encode(sha256('ANONYMISE'::bytea), 'hex'),
        genapi_id = NULL,
        genapi_data = NULL,
        ai_enrichments = jsonb_build_object('anonymized_reason', p_reason),
        ai_summary = NULL,
        anonymized = true,
        anonymized_at = NOW(),
        deleted_at = NOW()
    WHERE id = p_client_id;

    -- Log the anonymization
    PERFORM log_audit_event(
        'anonymize',
        'client',
        p_client_id,
        jsonb_build_object('reason', p_reason)
    );

    RETURN true;
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Anonymization failed: %', SQLERRM;
        RETURN false;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION anonymize_client IS 'Anonymise un client (Art. 17 RGPD) - Verifie les contraintes legales';

-- =============================================================================
-- EXPORT FUNCTION (for portability requests)
-- =============================================================================
CREATE OR REPLACE FUNCTION export_client_data(p_client_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_client JSONB;
    v_dossiers JSONB;
    v_audit JSONB;
    v_result JSONB;
BEGIN
    -- Get client data
    SELECT to_jsonb(c.*) INTO v_client
    FROM clients c
    WHERE c.id = p_client_id
    AND c.etude_id = get_user_etude_id();

    IF v_client IS NULL THEN
        RAISE EXCEPTION 'Client not found or access denied';
    END IF;

    -- Get related dossiers
    SELECT COALESCE(jsonb_agg(to_jsonb(d.*)), '[]'::jsonb) INTO v_dossiers
    FROM dossiers d
    WHERE d.etude_id = get_user_etude_id()
    AND d.parties @> jsonb_build_array(jsonb_build_object('client_id', p_client_id::text));

    -- Get audit history (limited to non-sensitive)
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'action', action,
        'resource_type', resource_type,
        'created_at', created_at
    )), '[]'::jsonb) INTO v_audit
    FROM audit_logs
    WHERE resource_type = 'client'
    AND resource_id = p_client_id
    ORDER BY created_at DESC
    LIMIT 100;

    -- Build result
    v_result := jsonb_build_object(
        'format', 'JSON',
        'version', '1.0',
        'export_date', NOW(),
        'gdpr_article', 'Art. 20 - Droit a la portabilite',
        'client', v_client,
        'dossiers', v_dossiers,
        'audit_history', v_audit
    );

    -- Log the export
    PERFORM log_audit_event(
        'export',
        'client',
        p_client_id,
        jsonb_build_object('type', 'portability_request'),
        ARRAY['nom', 'prenom', 'email', 'telephone', 'adresse']
    );

    RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION export_client_data IS 'Exporte les donnees d un client (Art. 20 RGPD - Portabilite)';

-- =============================================================================
-- SCHEDULED JOB: Check overdue requests (to be called via Supabase cron)
-- =============================================================================
CREATE OR REPLACE FUNCTION check_rgpd_deadlines()
RETURNS TABLE (
    request_id UUID,
    etude_id UUID,
    request_type TEXT,
    days_overdue INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.etude_id,
        r.request_type,
        EXTRACT(DAY FROM NOW() - r.deadline_at)::INTEGER
    FROM rgpd_requests r
    WHERE r.status = 'pending'
    AND r.deadline_at < NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION check_rgpd_deadlines IS 'Retourne les demandes RGPD en retard (pour alertes)';
