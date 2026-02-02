/**
 * Client Supabase pour NotaireAI
 * Gère les interactions avec la base de données
 */

const SUPABASE_URL = 'https://wcklvjckzktijtgakdrk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indja2x2amNremt0aWp0Z2FrZHJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwMDI1NzksImV4cCI6MjA4NDU3ODU3OX0.lyfrGeuVSkivopQVWlq3tf6Uo5k4Z6BqOEPt5WuYXS4';

const SupabaseClient = {
    /**
     * Effectue une requête à l'API Supabase
     * @param {string} endpoint - Endpoint (ex: '/rest/v1/form_submissions')
     * @param {object} options - Options fetch
     * @returns {Promise<object>}
     */
    async request(endpoint, options = {}) {
        const url = `${SUPABASE_URL}${endpoint}`;

        const headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json',
            'Prefer': options.prefer || 'return=representation',
            ...options.headers
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Supabase error: ${response.status} - ${error}`);
        }

        // Certaines requêtes ne retournent pas de JSON
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }

        return null;
    },

    /**
     * Récupère une soumission par son token
     * @param {string} token
     * @returns {Promise<object|null>}
     */
    async getSubmissionByToken(token) {
        const data = await this.request(
            `/rest/v1/form_submissions?token=eq.${token}&select=*`,
            { method: 'GET' }
        );

        return data && data.length > 0 ? data[0] : null;
    },

    /**
     * Soumet les données chiffrées
     * @param {string} token
     * @param {string} encryptedData - Données chiffrées (base64)
     * @param {string} iv - IV de chiffrement (base64)
     * @returns {Promise<object>}
     */
    async submitEncryptedData(token, encryptedData, iv) {
        return await this.request(
            `/rest/v1/form_submissions?token=eq.${token}`,
            {
                method: 'PATCH',
                body: JSON.stringify({
                    data_encrypted: encryptedData,
                    encryption_iv: iv,
                    status: 'submitted',
                    submitted_at: new Date().toISOString()
                })
            }
        );
    },

    /**
     * Crée une nouvelle soumission (côté notaire)
     * @param {object} params
     * @param {string} params.etudeId - ID de l'étude
     * @param {string} params.dossierId - ID du dossier (optionnel)
     * @param {string} params.notaireId - ID du notaire responsable
     * @param {string} params.clientId - ID de la fiche client à enrichir (optionnel)
     * @param {string} params.typePartie - Type de partie (vendeur, acquereur, etc.)
     * @param {string} params.label - Libellé du formulaire
     * @param {string} params.token - Token unique du formulaire
     * @returns {Promise<object>}
     */
    async createSubmission({ etudeId, dossierId, notaireId, clientId, typePartie, label, token, notaireEmail, typeQuestionnaire, clientEmail }) {
        return await this.request(
            '/rest/v1/form_submissions',
            {
                method: 'POST',
                body: JSON.stringify({
                    token,
                    etude_id: etudeId,
                    dossier_id: dossierId || null,
                    notaire_id: notaireId,
                    client_id: clientId || null,
                    type_partie: typePartie,
                    label,
                    status: 'pending',
                    notaire_email: notaireEmail || null,
                    type_questionnaire: typeQuestionnaire || null,
                    client_email: clientEmail || null
                })
            }
        );
    },

    /**
     * Liste les soumissions pour une étude
     * @param {string} etudeId
     * @returns {Promise<object[]>}
     */
    async listSubmissions(etudeId) {
        return await this.request(
            `/rest/v1/form_submissions?etude_id=eq.${etudeId}&order=created_at.desc`,
            { method: 'GET' }
        );
    },

    /**
     * Met à jour le statut d'une soumission
     * @param {string} id
     * @param {string} status
     * @returns {Promise<object>}
     */
    async updateSubmissionStatus(id, status) {
        return await this.request(
            `/rest/v1/form_submissions?id=eq.${id}`,
            {
                method: 'PATCH',
                body: JSON.stringify({
                    status,
                    processed_at: status === 'processed' ? new Date().toISOString() : null
                })
            }
        );
    },

    /**
     * Liste les soumissions pour un notaire spécifique
     * @param {string} notaireId - ID du notaire
     * @returns {Promise<object[]>}
     */
    async listSubmissionsByNotaire(notaireId) {
        return await this.request(
            `/rest/v1/form_submissions?notaire_id=eq.${notaireId}&order=created_at.desc`,
            { method: 'GET' }
        );
    },

    /**
     * Liste les notaires d'une étude
     * @param {string} etudeId - ID de l'étude
     * @returns {Promise<object[]>}
     */
    async listNotairesByEtude(etudeId) {
        return await this.request(
            `/rest/v1/etude_users?etude_id=eq.${etudeId}&role=in.(notaire,clerc)&select=*`,
            { method: 'GET' }
        );
    },

    /**
     * Envoie le lien du questionnaire au client par email
     * @param {object} payload
     * @param {string} payload.client_email - Email du client
     * @param {string} payload.client_nom - Nom du client
     * @param {string} payload.client_prenom - Prénom du client
     * @param {string} payload.questionnaire_url - URL complète du questionnaire
     * @param {string} payload.type_questionnaire - Type de questionnaire
     * @param {string} payload.etude_nom - Nom de l'étude notariale
     * @param {string} payload.notaire_email - Email du notaire
     * @returns {Promise<object>}
     */
    async sendLinkToClient(payload) {
        const response = await fetch(`${SUPABASE_URL}/functions/v1/send-questionnaire-link`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Email sending failed: ${error}`);
        }

        return await response.json();
    },

    /**
     * Enrichit une fiche client avec les données d'un formulaire soumis
     * Appelle la fonction PostgreSQL enrich_client_from_submission
     * @param {string} submissionId - ID de la soumission
     * @param {object} decryptedData - Données déchiffrées
     * @returns {Promise<object>}
     */
    async enrichClientFromSubmission(submissionId, decryptedData) {
        return await this.request(
            '/rest/v1/rpc/enrich_client_from_submission',
            {
                method: 'POST',
                body: JSON.stringify({
                    p_submission_id: submissionId,
                    p_decrypted_data: decryptedData
                })
            }
        );
    },

    /**
     * Authentifie un notaire par email/mot de passe
     * @param {string} email
     * @param {string} password
     * @returns {Promise<object|null>} Notaire user object with étude info
     */
    async authenticateNotaire(email, password) {
        // Hash password client-side with SHA-256
        const encoder = new TextEncoder();
        const data = encoder.encode(password);
        const hashBuffer = await crypto.subtle.digest('SHA-256', data);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const passwordHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

        // Query notaire_users with email and check hash
        const users = await this.request(
            `/rest/v1/notaire_users?email=eq.${encodeURIComponent(email)}&password_hash=eq.${passwordHash}&is_active=eq.true&select=*,etudes(*)`,
            { method: 'GET' }
        );

        if (!users || users.length === 0) {
            return null;
        }

        const user = users[0];

        // Update last login
        await this.request(
            `/rest/v1/notaire_users?id=eq.${user.id}`,
            {
                method: 'PATCH',
                body: JSON.stringify({ last_login_at: new Date().toISOString() })
            }
        );

        return user;
    },

    /**
     * Liste les dossiers d'une étude
     * @param {string} etudeId
     * @returns {Promise<object[]>}
     */
    async listDossiers(etudeId) {
        return await this.request(
            `/rest/v1/dossiers?etude_id=eq.${etudeId}&order=created_at.desc&select=id,numero,type_acte,statut,parties`,
            { method: 'GET' }
        );
    }
};

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupabaseClient;
}
