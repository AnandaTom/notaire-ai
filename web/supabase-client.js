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
    },

    // =========================================================================
    // GESTION DES DOCUMENTS (Supabase Storage)
    // =========================================================================

    /**
     * Upload un document vers Supabase Storage
     * @param {File} file - Fichier à uploader
     * @param {string} storagePath - Chemin dans le bucket (ex: 'submission-id/cni_timestamp_file.pdf')
     * @returns {Promise<{success: boolean, path?: string, error?: string}>}
     */
    async uploadDocument(file, storagePath) {
        try {
            const url = `${SUPABASE_URL}/storage/v1/object/documents-clients/${storagePath}`;

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'apikey': SUPABASE_ANON_KEY,
                    'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                    'Content-Type': file.type,
                    'x-upsert': 'true' // Remplace si existe déjà
                },
                body: file
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Upload error:', response.status, errorText);
                return { success: false, error: `Upload failed: ${response.status}` };
            }

            return { success: true, path: storagePath };
        } catch (error) {
            console.error('Upload exception:', error);
            return { success: false, error: error.message };
        }
    },

    /**
     * Enregistre les métadonnées d'un document dans la table documents_client
     * @param {object} metadata
     * @returns {Promise<object>}
     */
    async saveDocumentMetadata(metadata) {
        try {
            // Récupérer l'etude_id depuis la submission si on a un submission_id
            let etudeId = null;
            if (metadata.submission_id) {
                const submission = await this.getSubmissionByToken(metadata.submission_id);
                if (submission) {
                    etudeId = submission.etude_id;
                }
            }

            const data = await this.request(
                '/rest/v1/documents_client',
                {
                    method: 'POST',
                    body: JSON.stringify({
                        submission_id: metadata.submission_id || null,
                        etude_id: etudeId,
                        type_document: metadata.type_document,
                        nom_fichier: metadata.nom_fichier,
                        taille_octets: metadata.taille_octets,
                        type_mime: metadata.type_mime,
                        storage_path: metadata.storage_path,
                        statut: metadata.statut || 'uploaded'
                    })
                }
            );

            return data && data.length > 0 ? data[0] : null;
        } catch (error) {
            console.error('Error saving document metadata:', error);
            return null;
        }
    },

    /**
     * Supprime un document du storage et de la table documents_client
     * @param {string} documentId - ID dans documents_client
     * @param {string} storagePath - Chemin dans le storage
     * @returns {Promise<boolean>}
     */
    async deleteDocument(documentId, storagePath) {
        try {
            // Supprimer du storage
            if (storagePath) {
                const storageUrl = `${SUPABASE_URL}/storage/v1/object/documents-clients/${storagePath}`;
                await fetch(storageUrl, {
                    method: 'DELETE',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`
                    }
                });
            }

            // Supprimer de la table (si on a l'ID)
            if (documentId) {
                await this.request(
                    `/rest/v1/documents_client?id=eq.${documentId}`,
                    { method: 'DELETE' }
                );
            }

            return true;
        } catch (error) {
            console.error('Error deleting document:', error);
            return false;
        }
    },

    /**
     * Liste les documents d'une soumission
     * @param {string} submissionId
     * @returns {Promise<object[]>}
     */
    async listDocumentsBySubmission(submissionId) {
        return await this.request(
            `/rest/v1/documents_client?submission_id=eq.${submissionId}&order=created_at.desc`,
            { method: 'GET' }
        );
    },

    /**
     * Liste les documents d'une étude avec statut
     * @param {string} etudeId
     * @returns {Promise<object[]>}
     */
    async listDocumentsByEtude(etudeId) {
        return await this.request(
            `/rest/v1/documents_client?etude_id=eq.${etudeId}&order=created_at.desc`,
            { method: 'GET' }
        );
    },

    /**
     * Met à jour le statut d'un document (validation par le notaire)
     * @param {string} documentId
     * @param {string} statut - 'validated', 'rejected', 'pending_review'
     * @param {string} commentaire - Commentaire optionnel
     * @param {string} notaireId - ID du notaire qui valide
     * @returns {Promise<object>}
     */
    async updateDocumentStatus(documentId, statut, commentaire = null, notaireId = null) {
        const updateData = {
            statut,
            commentaire_notaire: commentaire
        };

        if (statut === 'validated') {
            updateData.validated_at = new Date().toISOString();
            updateData.validated_by = notaireId;
        }

        return await this.request(
            `/rest/v1/documents_client?id=eq.${documentId}`,
            {
                method: 'PATCH',
                body: JSON.stringify(updateData)
            }
        );
    },

    /**
     * Génère une URL signée temporaire pour télécharger un document
     * @param {string} storagePath
     * @param {number} expiresIn - Durée en secondes (défaut: 3600 = 1h)
     * @returns {Promise<string|null>}
     */
    async getSignedUrl(storagePath, expiresIn = 3600) {
        try {
            const response = await fetch(
                `${SUPABASE_URL}/storage/v1/object/sign/documents-clients/${storagePath}`,
                {
                    method: 'POST',
                    headers: {
                        'apikey': SUPABASE_ANON_KEY,
                        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ expiresIn })
                }
            );

            if (!response.ok) {
                console.error('Error getting signed URL:', response.status);
                return null;
            }

            const data = await response.json();
            return data.signedURL ? `${SUPABASE_URL}/storage/v1${data.signedURL}` : null;
        } catch (error) {
            console.error('Error getting signed URL:', error);
            return null;
        }
    },

    /**
     * Récupère le statut global des documents pour une soumission
     * (utilise la vue v_submissions_documents_status)
     * @param {string} submissionId
     * @returns {Promise<object|null>}
     */
    async getDocumentsStatusForSubmission(submissionId) {
        const data = await this.request(
            `/rest/v1/v_submissions_documents_status?submission_id=eq.${submissionId}`,
            { method: 'GET' }
        );

        return data && data.length > 0 ? data[0] : null;
    },

    /**
     * Liste les soumissions avec statut documents pour une étude
     * @param {string} etudeId
     * @returns {Promise<object[]>}
     */
    async listSubmissionsWithDocumentsStatus(etudeId) {
        return await this.request(
            `/rest/v1/v_submissions_documents_status?etude_id=eq.${etudeId}&order=submission_date.desc`,
            { method: 'GET' }
        );
    },

    // =========================================================================
    // KPIs & PILOTAGE (Dashboard ERP)
    // =========================================================================

    /**
     * Récupère les KPIs globaux d'une étude
     * @param {string} etudeId
     * @returns {Promise<object|null>}
     */
    async getKpisEtude(etudeId) {
        const data = await this.request(
            `/rest/v1/v_kpis_etude?etude_id=eq.${etudeId}`,
            { method: 'GET' }
        );
        return data && data.length > 0 ? data[0] : null;
    },

    /**
     * Récupère les KPIs par type d'acte
     * @param {string} etudeId
     * @returns {Promise<object[]>}
     */
    async getKpisParTypeActe(etudeId) {
        return await this.request(
            `/rest/v1/v_kpis_par_type_acte?etude_id=eq.${etudeId}`,
            { method: 'GET' }
        );
    },

    /**
     * Récupère l'évolution mensuelle des actes
     * @param {string} etudeId
     * @param {number} limit - Nombre de mois (défaut: 12)
     * @returns {Promise<object[]>}
     */
    async getEvolutionMensuelle(etudeId, limit = 12) {
        return await this.request(
            `/rest/v1/v_evolution_mensuelle?etude_id=eq.${etudeId}&order=mois.desc&limit=${limit}`,
            { method: 'GET' }
        );
    },

    /**
     * Récupère les dossiers avec détails pour le dashboard
     * @param {string} etudeId
     * @param {object} filters - Filtres optionnels
     * @returns {Promise<object[]>}
     */
    async getDossiersDashboard(etudeId, filters = {}) {
        let query = `/rest/v1/v_dossiers_dashboard?etude_id=eq.${etudeId}`;

        if (filters.statut) {
            query += `&statut=eq.${filters.statut}`;
        }
        if (filters.priorite) {
            query += `&priorite=eq.${filters.priorite}`;
        }

        query += '&order=created_at.desc';

        return await this.request(query, { method: 'GET' });
    },

    /**
     * Récupère les rappels pour le dashboard
     * @param {string} etudeId
     * @param {string} urgence - Filtre par urgence: 'en_retard', 'imminent', 'cette_semaine', 'a_venir'
     * @returns {Promise<object[]>}
     */
    async getRappelsDashboard(etudeId, urgence = null) {
        let query = `/rest/v1/v_rappels_dashboard?etude_id=eq.${etudeId}`;

        if (urgence) {
            query += `&urgence=eq.${urgence}`;
        }

        query += '&order=date_echeance.asc';

        return await this.request(query, { method: 'GET' });
    },

    /**
     * Crée un nouveau rappel
     * @param {object} rappel
     * @returns {Promise<object>}
     */
    async createRappel(rappel) {
        return await this.request(
            '/rest/v1/rappels',
            {
                method: 'POST',
                body: JSON.stringify(rappel)
            }
        );
    },

    /**
     * Met à jour un rappel (marquer comme terminé, etc.)
     * @param {string} rappelId
     * @param {object} updates
     * @returns {Promise<object>}
     */
    async updateRappel(rappelId, updates) {
        return await this.request(
            `/rest/v1/rappels?id=eq.${rappelId}`,
            {
                method: 'PATCH',
                body: JSON.stringify(updates)
            }
        );
    },

    /**
     * Marque un rappel comme terminé
     * @param {string} rappelId
     * @param {string} notaireId
     * @param {string} notes
     * @returns {Promise<object>}
     */
    async completeRappel(rappelId, notaireId, notes = null) {
        return await this.updateRappel(rappelId, {
            status: 'termine',
            completed_at: new Date().toISOString(),
            completed_by: notaireId,
            completion_notes: notes
        });
    },

    /**
     * Récupère les actes générés
     * @param {string} etudeId
     * @param {object} filters
     * @returns {Promise<object[]>}
     */
    async getActesGeneres(etudeId, filters = {}) {
        let query = `/rest/v1/actes_generes?etude_id=eq.${etudeId}`;

        if (filters.type_acte) {
            query += `&type_acte=eq.${filters.type_acte}`;
        }
        if (filters.status) {
            query += `&status=eq.${filters.status}`;
        }
        if (filters.dossier_id) {
            query += `&dossier_id=eq.${filters.dossier_id}`;
        }

        query += '&order=created_at.desc';

        return await this.request(query, { method: 'GET' });
    },

    /**
     * Récupère les templates disponibles
     * @param {string} etudeId - Si null, récupère les templates système uniquement
     * @returns {Promise<object[]>}
     */
    async getTemplates(etudeId = null) {
        let query = '/rest/v1/templates?is_active=eq.true';

        if (etudeId) {
            // Templates système OU templates de l'étude
            query += `&or=(is_system.eq.true,etude_id.eq.${etudeId})`;
        } else {
            query += '&is_system=eq.true';
        }

        query += '&order=type_acte,nom';

        return await this.request(query, { method: 'GET' });
    },

    /**
     * Récupère les événements d'un dossier (timeline)
     * @param {string} dossierId
     * @returns {Promise<object[]>}
     */
    async getEvenementsDossier(dossierId) {
        return await this.request(
            `/rest/v1/evenements_dossier?dossier_id=eq.${dossierId}&order=event_at.desc`,
            { method: 'GET' }
        );
    },

    /**
     * Ajoute un événement à un dossier
     * @param {object} evenement
     * @returns {Promise<object>}
     */
    async addEvenementDossier(evenement) {
        return await this.request(
            '/rest/v1/evenements_dossier',
            {
                method: 'POST',
                body: JSON.stringify(evenement)
            }
        );
    }
};

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SupabaseClient;
}
