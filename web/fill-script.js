/**
 * Script pour le formulaire acheteur sécurisé
 * Gère le chargement, la validation et l'envoi chiffré des données
 */

// État global
let submissionData = null;
let encryptionKey = null;

// Éléments DOM
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const formState = document.getElementById('formState');
const successState = document.getElementById('successState');
const errorMessage = document.getElementById('errorMessage');
const dossierInfo = document.getElementById('dossierInfo');
const dossierLabel = document.getElementById('dossierLabel');
const submitBtn = document.getElementById('submitBtn');

/**
 * Initialisation au chargement de la page
 */
async function init() {
    try {
        // Récupérer le token depuis l'URL
        const token = getTokenFromUrl();
        if (!token) {
            showError('Lien invalide. Le format de l\'URL est incorrect.');
            return;
        }

        // Récupérer la clé de chiffrement depuis le fragment
        const keyBase64 = CryptoModule.getKeyFromUrl();
        if (!keyBase64) {
            showError('Clé de sécurité manquante. Veuillez utiliser le lien complet fourni par votre notaire.');
            return;
        }

        // Importer la clé
        encryptionKey = await CryptoModule.importKey(keyBase64);

        // Vérifier la soumission dans Supabase
        submissionData = await SupabaseClient.getSubmissionByToken(token);

        if (!submissionData) {
            showError('Ce lien de formulaire est invalide ou a expiré.');
            return;
        }

        if (submissionData.status !== 'pending') {
            if (submissionData.status === 'submitted') {
                showError('Ce formulaire a déjà été soumis. Contactez votre notaire si vous devez le modifier.');
            } else if (submissionData.status === 'expired') {
                showError('Ce lien a expiré. Veuillez contacter votre notaire pour obtenir un nouveau lien.');
            } else {
                showError('Ce formulaire n\'est plus disponible.');
            }
            return;
        }

        // Vérifier l'expiration
        if (new Date(submissionData.expires_at) < new Date()) {
            showError('Ce lien a expiré. Veuillez contacter votre notaire pour obtenir un nouveau lien.');
            return;
        }

        // Afficher le label du dossier si disponible
        if (submissionData.label) {
            dossierLabel.textContent = submissionData.label;
            dossierInfo.classList.remove('hidden');
        }

        // Tout est OK, afficher le formulaire
        showForm();

    } catch (error) {
        console.error('Erreur d\'initialisation:', error);
        showError('Une erreur est survenue lors du chargement. Veuillez réessayer.');
    }
}

/**
 * Extrait le token de l'URL
 * Supporte /fill/{token} et ?token={token}
 */
function getTokenFromUrl() {
    // Essayer le format path: /fill/{token}
    const pathMatch = window.location.pathname.match(/\/fill\/([a-f0-9]{64})/i);
    if (pathMatch) return pathMatch[1];

    // Essayer le format query: ?token={token}
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    if (token && /^[a-f0-9]{64}$/i.test(token)) return token;

    return null;
}

/**
 * Affiche l'état d'erreur
 */
function showError(message) {
    loadingState.classList.add('hidden');
    formState.classList.add('hidden');
    successState.classList.add('hidden');
    errorMessage.textContent = message;
    errorState.classList.remove('hidden');
}

/**
 * Affiche le formulaire
 */
function showForm() {
    loadingState.classList.add('hidden');
    errorState.classList.add('hidden');
    successState.classList.add('hidden');
    formState.classList.remove('hidden');
}

/**
 * Affiche l'état de succès
 */
function showSuccess() {
    loadingState.classList.add('hidden');
    errorState.classList.add('hidden');
    formState.classList.add('hidden');
    successState.classList.remove('hidden');
}

// Gestion de l'affichage du formulaire conjoint
document.getElementById('regime_matrimonial').addEventListener('change', function(e) {
    const conjointSection = document.getElementById('conjoint_section');
    const value = e.target.value;

    if (value === 'marie' || value === 'pacs') {
        conjointSection.classList.remove('hidden');
        document.getElementById('conjoint_nom').required = true;
        document.getElementById('conjoint_prenoms').required = true;
        document.getElementById('date_mariage').required = true;
        document.getElementById('lieu_mariage').required = true;
        document.getElementById('type_regime').required = true;
    } else {
        conjointSection.classList.add('hidden');
        document.getElementById('conjoint_nom').required = false;
        document.getElementById('conjoint_prenoms').required = false;
        document.getElementById('date_mariage').required = false;
        document.getElementById('lieu_mariage').required = false;
        document.getElementById('type_regime').required = false;
    }
});

// Soumission du formulaire
document.getElementById('acheteurForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Désactiver le bouton
    submitBtn.disabled = true;
    submitBtn.textContent = 'Envoi en cours...';

    try {
        const formData = new FormData(e.target);

        // Construire l'objet de données
        const data = {
            acquereur: {
                personne_physique: {
                    civilite: formData.get('civilite'),
                    nom: formData.get('nom'),
                    nom_usage: formData.get('nom_usage') || null,
                    prenoms: formData.get('prenoms').split(',').map(p => p.trim()),
                    date_naissance: formData.get('date_naissance'),
                    lieu_naissance: formData.get('lieu_naissance'),
                    nationalite: formData.get('nationalite'),
                    profession: formData.get('profession') || null
                },
                adresse: {
                    adresse: formData.get('adresse'),
                    code_postal: formData.get('code_postal'),
                    ville: formData.get('ville')
                },
                situation_matrimoniale: {
                    regime: formData.get('regime_matrimonial')
                },
                pieces_identite: {
                    cni: {
                        numero: formData.get('cni_numero'),
                        date_emission: formData.get('cni_date_emission'),
                        date_expiration: formData.get('cni_date_expiration'),
                        autorite_emission: formData.get('cni_autorite')
                    }
                },
                coordonnees_bancaires: {
                    iban: formData.get('iban').replace(/\s/g, ''),
                    bic: formData.get('bic'),
                    nom_banque: formData.get('banque')
                },
                contact: {
                    telephone: formData.get('telephone'),
                    email: formData.get('email')
                }
            },
            metadata: {
                submitted_at: new Date().toISOString(),
                user_agent: navigator.userAgent,
                rgpd_consent: true,
                rgpd_consent_date: new Date().toISOString()
            }
        };

        // Ajouter les informations du conjoint si applicable
        const regime = formData.get('regime_matrimonial');
        if (regime === 'marie' || regime === 'pacs') {
            const conjointKey = regime === 'marie' ? 'conjoint' : 'partenaire';
            data.acquereur.situation_matrimoniale[conjointKey] = {
                nom: formData.get('conjoint_nom'),
                prenoms: formData.get('conjoint_prenoms').split(',').map(p => p.trim()),
                intervient_acte: formData.get('conjoint_intervient') === 'on'
            };
            data.acquereur.situation_matrimoniale.date_union = formData.get('date_mariage');
            data.acquereur.situation_matrimoniale.lieu_union = formData.get('lieu_mariage');
            data.acquereur.situation_matrimoniale.type_regime = formData.get('type_regime');
        }

        // Chiffrer les données
        const { encrypted, iv } = await CryptoModule.encrypt(data, encryptionKey);

        // Envoyer à Supabase
        const token = getTokenFromUrl();
        await SupabaseClient.submitEncryptedData(token, encrypted, iv);

        // Afficher le succès
        showSuccess();

    } catch (error) {
        console.error('Erreur lors de la soumission:', error);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Envoyer mes informations de manière sécurisée';
        showToast('Une erreur est survenue. Veuillez réessayer.', 'error');
    }
});

// Formatage automatique de l'IBAN
document.getElementById('iban').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\s/g, '').toUpperCase();
    let formatted = value.match(/.{1,4}/g)?.join(' ') || value;
    e.target.value = formatted;
});

// Formatage automatique du téléphone
document.getElementById('telephone').addEventListener('input', function(e) {
    let value = e.target.value.replace(/\s/g, '');
    let formatted = value.match(/.{1,2}/g)?.join(' ') || value;
    e.target.value = formatted;
});

// Afficher un toast
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;

    if (type === 'error') {
        toast.style.background = '#dc2626';
    }

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Lancer l'initialisation
init();
