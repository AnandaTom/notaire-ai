/**
 * Script commun pour les questionnaires notariaux
 * Gère la navigation, validation, chiffrement et envoi
 */

// Configuration Supabase
const SUPABASE_URL = 'https://wcklvjckzktijtgakdrk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indja2x2amNremt0aWp0Z2FrZHJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwMDI1NzksImV4cCI6MjA4NDU3ODU3OX0.lyfrGeuVSkivopQVWlq3tf6Uo5k4Z6BqOEPt5WuYXS4';

// État global
let currentSection = 1;
let formData = {};

// Éléments DOM
const form = document.getElementById('questionnaireForm');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const submitBtn = document.getElementById('submitBtn');
const loadingOverlay = document.getElementById('loadingOverlay');
const successPage = document.getElementById('successPage');

// ============================================
// MODULE DE CHIFFREMENT
// ============================================
const CryptoModule = {
    async generateKey() {
        const key = await crypto.subtle.generateKey(
            { name: 'AES-GCM', length: 256 },
            true,
            ['encrypt', 'decrypt']
        );
        const rawKey = await crypto.subtle.exportKey('raw', key);
        return {
            key,
            keyBase64: this.arrayBufferToBase64(rawKey)
        };
    },

    async importKey(keyBase64) {
        const rawKey = this.base64ToArrayBuffer(keyBase64);
        return await crypto.subtle.importKey(
            'raw',
            rawKey,
            { name: 'AES-GCM', length: 256 },
            false,
            ['encrypt', 'decrypt']
        );
    },

    async encrypt(data, key) {
        const iv = crypto.getRandomValues(new Uint8Array(12));
        const encodedData = new TextEncoder().encode(JSON.stringify(data));
        const encryptedBuffer = await crypto.subtle.encrypt(
            { name: 'AES-GCM', iv },
            key,
            encodedData
        );
        return {
            encrypted: this.arrayBufferToBase64(encryptedBuffer),
            iv: this.arrayBufferToBase64(iv)
        };
    },

    async decrypt(encryptedBase64, ivBase64, key) {
        const encryptedBuffer = this.base64ToArrayBuffer(encryptedBase64);
        const iv = this.base64ToArrayBuffer(ivBase64);
        const decryptedBuffer = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv },
            key,
            encryptedBuffer
        );
        return JSON.parse(new TextDecoder().decode(decryptedBuffer));
    },

    generateToken() {
        const bytes = crypto.getRandomValues(new Uint8Array(32));
        return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
    },

    getKeyFromUrl() {
        const hash = window.location.hash;
        if (!hash) return null;
        const params = new URLSearchParams(hash.substring(1));
        return params.get('key');
    },

    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    },

    base64ToArrayBuffer(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }
};

// ============================================
// CLIENT SUPABASE
// ============================================
const SupabaseClient = {
    async request(endpoint, options = {}) {
        const url = `${SUPABASE_URL}${endpoint}`;
        const headers = {
            'apikey': SUPABASE_ANON_KEY,
            'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
            'Content-Type': 'application/json',
            'Prefer': options.prefer || 'return=representation',
            ...options.headers
        };

        const response = await fetch(url, { ...options, headers });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(`Supabase error: ${response.status} - ${error}`);
        }

        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        return null;
    },

    async createSubmission(data) {
        return await this.request('/rest/v1/form_submissions', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async getSubmissionByToken(token) {
        const data = await this.request(
            `/rest/v1/form_submissions?token=eq.${token}&select=*`,
            { method: 'GET' }
        );
        return data && data.length > 0 ? data[0] : null;
    },

    async sendNotification(payload) {
        const response = await fetch(`${SUPABASE_URL}/functions/v1/send-questionnaire-notification`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        return await response.json();
    }
};

// ============================================
// NAVIGATION
// ============================================
function showSection(sectionNum) {
    // Masquer toutes les sections
    document.querySelectorAll('.form-section').forEach(section => {
        section.classList.remove('active');
    });

    // Afficher la section courante
    const currentSectionEl = document.querySelector(`[data-section="${sectionNum}"]`);
    if (currentSectionEl) {
        currentSectionEl.classList.add('active');
    }

    // Mettre à jour la barre de progression
    document.querySelectorAll('.progress-step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');
        if (stepNum < sectionNum) {
            step.classList.add('completed');
        } else if (stepNum === sectionNum) {
            step.classList.add('active');
        }
    });

    // Gérer les boutons
    prevBtn.style.visibility = sectionNum === 1 ? 'hidden' : 'visible';

    if (sectionNum === CONFIG.totalSections) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'inline-flex';
    } else {
        nextBtn.style.display = 'inline-flex';
        submitBtn.style.display = 'none';
    }

    // Scroll en haut
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function validateCurrentSection() {
    const currentSectionEl = document.querySelector(`[data-section="${currentSection}"]`);
    const requiredFields = currentSectionEl.querySelectorAll('[required]');

    let isValid = true;
    requiredFields.forEach(field => {
        if (!field.value || (field.type === 'checkbox' && !field.checked)) {
            isValid = false;
            field.classList.add('error');
            field.addEventListener('input', () => field.classList.remove('error'), { once: true });
        }
    });

    // Vérifier les groupes radio obligatoires
    const radioGroups = currentSectionEl.querySelectorAll('.radio-group');
    radioGroups.forEach(group => {
        const name = group.querySelector('input[type="radio"]')?.name;
        if (name) {
            const checked = currentSectionEl.querySelector(`input[name="${name}"]:checked`);
            const required = currentSectionEl.querySelector(`input[name="${name}"][required]`);
            if (required && !checked) {
                isValid = false;
                group.classList.add('error');
            }
        }
    });

    if (!isValid) {
        showToast('Veuillez remplir tous les champs obligatoires', 'error');
    }

    return isValid;
}

// Boutons navigation
prevBtn.addEventListener('click', () => {
    if (currentSection > 1) {
        currentSection--;
        showSection(currentSection);
    }
});

nextBtn.addEventListener('click', () => {
    if (validateCurrentSection() && currentSection < CONFIG.totalSections) {
        currentSection++;
        showSection(currentSection);
    }
});

// ============================================
// CHAMPS CONDITIONNELS
// ============================================
function setupConditionalFields() {
    // Situation matrimoniale vendeur 1
    document.querySelectorAll('input[name="vendeur1_situation"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const mariageDetails = document.getElementById('v1_mariage_details');
            const divorceDetails = document.getElementById('v1_divorce_details');

            mariageDetails?.classList.remove('visible');
            divorceDetails?.classList.remove('visible');

            if (e.target.value === 'marie' || e.target.value === 'pacse') {
                mariageDetails?.classList.add('visible');
            } else if (e.target.value === 'divorce') {
                divorceDetails?.classList.add('visible');
            }
        });
    });

    // Vendeur 2
    document.getElementById('hasVendeur2')?.addEventListener('change', (e) => {
        const vendeur2Section = document.getElementById('vendeur2Section');
        if (vendeur2Section) {
            vendeur2Section.style.display = e.target.checked ? 'block' : 'none';
        }
    });

    // Syndic
    document.querySelectorAll('input[name="syndic"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const details = document.getElementById('syndic_details');
            details?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Lotissement -> association syndicale
    document.querySelectorAll('input[name="lotissement"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const details = document.getElementById('association_syndicale');
            details?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Difficultés copropriété
    document.querySelectorAll('input[name="difficultes_copro"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const details = document.getElementById('difficultes_details');
            details?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Dégât des eaux
    document.querySelectorAll('input[name="degat_eaux"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const details = document.getElementById('degat_eaux_details');
            details?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Travaux parties communes
    document.querySelectorAll('input[name="travaux_parties_communes"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const details = document.getElementById('travaux_details');
            details?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Prêts hypothécaires
    document.querySelectorAll('input[name="prets_hypothecaires"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const details = document.getElementById('prets_details');
            details?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Résidence principale
    document.querySelectorAll('input[name="residence_principale"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            document.getElementById('residence_principale_oui')?.classList.toggle('visible', e.target.value === 'oui');
            document.getElementById('residence_principale_non')?.classList.toggle('visible', e.target.value === 'non');
        });
    });

    // Avantage fiscal
    document.querySelectorAll('input[name="avantage_fiscal"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const details = document.getElementById('avantage_fiscal_details');
            details?.classList.toggle('visible', e.target.value === 'oui');
        });
    });

    // Bien libre
    document.querySelectorAll('input[name="bien_libre"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            const details = document.getElementById('bien_occupe');
            details?.classList.toggle('visible', e.target.value === 'non');
        });
    });

    // Motivation autre
    document.querySelectorAll('input[name="motivation_vente"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            const autreChecked = document.querySelector('input[name="motivation_vente"][value="autre"]:checked');
            document.getElementById('motivation_autre')?.classList.toggle('visible', !!autreChecked);
        });
    });

    // Boutons Yes/No stylisés
    document.querySelectorAll('.yes-no-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const group = this.closest('.yes-no-group');
            group.querySelectorAll('.yes-no-btn').forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            this.querySelector('input').checked = true;
            this.querySelector('input').dispatchEvent(new Event('change', { bubbles: true }));
        });
    });
}

// ============================================
// FORMATAGE
// ============================================
function setupFormatting() {
    // IBAN
    document.getElementById('iban')?.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\s/g, '').toUpperCase();
        let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
        e.target.value = formatted;
    });

    // Téléphones
    ['tel_domicile', 'tel_portable', 'tel_travail'].forEach(id => {
        document.getElementById(id)?.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\s/g, '');
            let formatted = value.match(/.{1,2}/g)?.join(' ') || value;
            e.target.value = formatted;
        });
    });

    // Code postal
    document.getElementById('code_postal')?.addEventListener('input', function(e) {
        e.target.value = e.target.value.replace(/\D/g, '').slice(0, 5);
    });
}

// ============================================
// COLLECTE DES DONNÉES
// ============================================
function collectFormData() {
    const formEl = document.getElementById('questionnaireForm');
    const formDataObj = new FormData(formEl);
    const data = {
        type_questionnaire: CONFIG.type,
        date_soumission: new Date().toISOString(),
        vendeurs: [],
        coordonnees: {},
        copropriete: {},
        travaux: {},
        prets: {},
        fiscal: {},
        observations: ''
    };

    // Vendeur 1
    const vendeur1 = {
        civilite: formDataObj.get('vendeur1_civilite'),
        nom: formDataObj.get('vendeur1_nom'),
        prenoms: formDataObj.get('vendeur1_prenoms'),
        date_naissance: formDataObj.get('vendeur1_date_naissance'),
        lieu_naissance: formDataObj.get('vendeur1_lieu_naissance'),
        nationalite: formDataObj.get('vendeur1_nationalite'),
        profession: formDataObj.get('vendeur1_profession'),
        situation_matrimoniale: formDataObj.get('vendeur1_situation'),
        date_mariage: formDataObj.get('vendeur1_date_mariage'),
        lieu_mariage: formDataObj.get('vendeur1_lieu_mariage'),
        regime_matrimonial: formDataObj.get('vendeur1_regime_matrimonial'),
        residence_fiscale: formDataObj.get('vendeur1_residence_fiscale'),
        pacs_vigueur: formDataObj.get('vendeur1_pacs_vigueur') === 'oui',
        commercant: formDataObj.get('vendeur1_commercant') === 'oui',
        redressement: formDataObj.get('vendeur1_redressement') === 'oui',
        surendettement: formDataObj.get('vendeur1_surendettement') === 'oui'
    };
    data.vendeurs.push(vendeur1);

    // Vendeur 2 si présent
    if (formDataObj.get('has_vendeur2')) {
        const vendeur2 = {
            civilite: formDataObj.get('vendeur2_civilite'),
            nom: formDataObj.get('vendeur2_nom'),
            prenoms: formDataObj.get('vendeur2_prenoms'),
            date_naissance: formDataObj.get('vendeur2_date_naissance'),
            lieu_naissance: formDataObj.get('vendeur2_lieu_naissance'),
            nationalite: formDataObj.get('vendeur2_nationalite'),
            profession: formDataObj.get('vendeur2_profession'),
            situation_matrimoniale: formDataObj.get('vendeur2_situation'),
            residence_fiscale: formDataObj.get('vendeur2_residence_fiscale')
        };
        data.vendeurs.push(vendeur2);
    }

    // Coordonnées
    data.coordonnees = {
        adresse: formDataObj.get('adresse'),
        code_postal: formDataObj.get('code_postal'),
        ville: formDataObj.get('ville'),
        tel_domicile: formDataObj.get('tel_domicile'),
        tel_portable: formDataObj.get('tel_portable'),
        tel_travail: formDataObj.get('tel_travail'),
        email: formDataObj.get('email'),
        iban: formDataObj.get('iban')?.replace(/\s/g, ''),
        bic: formDataObj.get('bic'),
        banque: formDataObj.get('banque')
    };

    // Copropriété
    data.copropriete = {
        division_volume: formDataObj.get('division_volume'),
        lotissement: formDataObj.get('lotissement'),
        association_syndicale: formDataObj.get('association_syndicale'),
        president_association: formDataObj.get('president_association'),
        syndic: formDataObj.get('syndic'),
        nom_syndic: formDataObj.get('nom_syndic'),
        fonds_travaux: formDataObj.get('fonds_travaux'),
        reglement_copro: formDataObj.get('reglement_copro'),
        difficultes_copro: formDataObj.get('difficultes_copro'),
        details_difficultes: formDataObj.get('details_difficultes'),
        procedure_copro: formDataObj.get('procedure_copro'),
        degat_eaux: formDataObj.get('degat_eaux'),
        accord_degat_eaux: formDataObj.get('accord_degat_eaux')
    };

    // Travaux
    data.travaux = {
        travaux_parties_communes: formDataObj.get('travaux_parties_communes'),
        details_travaux: formDataObj.get('details_travaux'),
        autorisation_travaux: formDataObj.get('autorisation_travaux'),
        modification_affectation: formDataObj.get('modification_affectation'),
        division_lots: formDataObj.get('division_lots'),
        sanibroyeur: formDataObj.get('sanibroyeur'),
        declaration_h: formDataObj.get('declaration_h'),
        parties_non_visitees: formDataObj.get('parties_non_visitees')
    };

    // Prêts
    data.prets = {
        saisie_immobiliere: formDataObj.get('saisie_immobiliere'),
        prets_hypothecaires: formDataObj.get('prets_hypothecaires'),
        details_prets: formDataObj.get('details_prets'),
        credit_relais: formDataObj.get('credit_relais'),
        garantie_tresor: formDataObj.get('garantie_tresor')
    };

    // Fiscal
    data.fiscal = {
        residence_principale: formDataObj.get('residence_principale'),
        depuis_quand_residence: formDataObj.get('depuis_quand_residence'),
        remploi_residence: formDataObj.get('remploi_residence'),
        retraite_invalide: formDataObj.get('retraite_invalide'),
        travaux_amelioration: formDataObj.get('travaux_amelioration'),
        droits_mutation: formDataObj.get('droits_mutation'),
        avantage_fiscal: formDataObj.get('avantage_fiscal'),
        type_avantage_fiscal: formDataObj.get('type_avantage_fiscal'),
        engagement_termine: formDataObj.get('engagement_termine'),
        recuperation_tva: formDataObj.get('recuperation_tva'),
        deficit_foncier: formDataObj.get('deficit_foncier'),
        bien_libre: formDataObj.get('bien_libre'),
        loue_precedemment: formDataObj.get('loue_precedemment'),
        contrat_alarme: formDataObj.get('contrat_alarme'),
        autres_contrats: formDataObj.get('autres_contrats'),
        sinistre_avant: formDataObj.get('sinistre_avant'),
        sinistre_apres: formDataObj.get('sinistre_apres'),
        motivation_vente: formDataObj.getAll('motivation_vente'),
        motivation_precision: formDataObj.get('motivation_precision')
    };

    // Observations
    data.observations = formDataObj.get('observations');

    // Métadonnées
    data.metadata = {
        user_agent: navigator.userAgent,
        rgpd_consent: formDataObj.get('rgpd_consent') === 'on',
        rgpd_consent_date: new Date().toISOString()
    };

    return data;
}

// ============================================
// SOUMISSION
// ============================================

// Récupérer le token depuis l'URL (lien envoyé par le notaire)
function getTokenFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('token') || null;
}

// Récupérer la clé de chiffrement depuis le fragment URL
function getKeyFromUrl() {
    const hash = window.location.hash;
    if (!hash) return null;
    const params = new URLSearchParams(hash.substring(1));
    return params.get('key') || null;
}

async function submitForm(e) {
    e.preventDefault();

    if (!validateCurrentSection()) {
        return;
    }

    // Afficher le loading
    loadingOverlay.classList.add('visible');

    try {
        // Collecter les données (peut être overridé par le script spécifique)
        const data = typeof window.collectFormData === 'function'
            ? window.collectFormData()
            : collectFormData();

        // Extraire nom/prénom du client selon le type de questionnaire
        let clientNom = '';
        let clientPrenom = '';

        if (data.vendeurs && data.vendeurs[0]) {
            clientNom = data.vendeurs[0].nom || '';
            clientPrenom = data.vendeurs[0].prenoms || '';
        } else if (data.acheteurs && data.acheteurs[0]) {
            clientNom = data.acheteurs[0].nom || '';
            clientPrenom = data.acheteurs[0].prenoms || '';
        }

        // Vérifier si on a un token existant (lien envoyé par le notaire)
        const existingToken = getTokenFromUrl();
        const existingKeyBase64 = getKeyFromUrl();

        let token, keyBase64, key;

        if (existingToken && existingKeyBase64) {
            // MODE LIEN NOTAIRE : PATCH la submission existante
            token = existingToken;
            keyBase64 = existingKeyBase64;
            key = await CryptoModule.importKey(keyBase64);
        } else {
            // MODE AUTONOME : Créer une nouvelle submission
            const generated = await CryptoModule.generateKey();
            key = generated.key;
            keyBase64 = generated.keyBase64;
            token = CryptoModule.generateToken();
        }

        // Chiffrer les données
        const { encrypted, iv } = await CryptoModule.encrypt(data, key);

        // Déterminer le type_partie selon le questionnaire
        let typePartie = 'vendeur';
        if (CONFIG.type === 'achat_bien') {
            typePartie = 'acheteur';
        } else if (CONFIG.type === 'vente_appartement') {
            typePartie = 'vendeur_appartement';
        } else if (CONFIG.type === 'vente_maison') {
            typePartie = 'vendeur_maison';
        }

        if (existingToken) {
            // PATCH la submission existante (créée par le notaire)
            // Récupérer d'abord les infos existantes pour avoir notaire_email et etude_id
            const existingSubmission = await SupabaseClient.getSubmissionByToken(existingToken);

            await SupabaseClient.request(
                `/rest/v1/form_submissions?token=eq.${existingToken}`,
                {
                    method: 'PATCH',
                    body: JSON.stringify({
                        data_encrypted: encrypted,
                        encryption_iv: iv,
                        encryption_key_wrapped: keyBase64,
                        status: 'submitted',
                        submitted_at: new Date().toISOString(),
                        client_nom: clientNom || undefined,
                        client_prenom: clientPrenom || undefined,
                        user_agent: navigator.userAgent
                    })
                }
            );

            // Envoyer la notification email au notaire
            const notaireEmail = existingSubmission?.notaire_email;
            if (notaireEmail) {
                try {
                    await SupabaseClient.sendNotification({
                        submission_id: existingSubmission.id,
                        token: existingToken,
                        type_questionnaire: existingSubmission.type_questionnaire || CONFIG.type,
                        notaire_email: notaireEmail,
                        client_nom: clientNom,
                        client_prenom: clientPrenom,
                        etude_id: existingSubmission.etude_id,
                        dossier_id: existingSubmission.dossier_id
                    });
                } catch (emailError) {
                    console.warn('Email notification failed:', emailError);
                }
            }
        } else {
            // Créer une nouvelle submission (mode autonome)
            const urlParams = new URLSearchParams(window.location.search);
            const notaireEmail = urlParams.get('notaire') || CONFIG.notaireEmail || '';

            const submissionData = {
                token: token,
                type_questionnaire: CONFIG.type,
                type_partie: typePartie,
                data_encrypted: encrypted,
                encryption_iv: iv,
                encryption_key_wrapped: keyBase64,
                status: 'submitted',
                submitted_at: new Date().toISOString(),
                client_nom: clientNom,
                client_prenom: clientPrenom,
                notaire_email: notaireEmail,
                user_agent: navigator.userAgent,
                label: `${clientPrenom} ${clientNom} - ${CONFIG.title}`.trim()
            };

            await SupabaseClient.createSubmission(submissionData);

            if (notaireEmail) {
                try {
                    await SupabaseClient.sendNotification({
                        submission_id: token,
                        token: token,
                        type_questionnaire: CONFIG.type,
                        notaire_email: notaireEmail,
                        client_nom: clientNom,
                        client_prenom: clientPrenom
                    });
                } catch (emailError) {
                    console.warn('Email notification failed:', emailError);
                }
            }
        }

        // Afficher succès
        loadingOverlay.classList.remove('visible');
        document.querySelector('.form-body').style.display = 'none';
        successPage.style.display = 'block';

    } catch (error) {
        console.error('Erreur soumission:', error);
        loadingOverlay.classList.remove('visible');
        showToast('Une erreur est survenue. Veuillez réessayer.', 'error');
    }
}

// ============================================
// UTILITAIRES
// ============================================
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// INITIALISATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    setupConditionalFields();
    setupFormatting();
    showSection(1);

    // Gestionnaire de soumission
    form.addEventListener('submit', submitForm);
});
