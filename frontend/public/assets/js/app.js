// ============================================
// NOTOMAI - Application JavaScript
// ============================================

// ============================================
// CONFIGURATION
// ============================================
const SUPABASE_URL = 'https://wcklvjckzktijtgakdrk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indja2x2amNremt0aWp0Z2FrZHJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwMDI1NzksImV4cCI6MjA4NDU3ODU3OX0.lyfrGeuVSkivopQVWlq3tf6Uo5k4Z6BqOEPt5WuYXS4';

// API Modal NotaireAI
// Production: https://paulannes-pro--notaire-ai-fastapi-app.modal.run
// Local: http://localhost:8000
const API_BASE_URL = 'https://paulannes-pro--notaire-ai-fastapi-app.modal.run';

// Mode de fonctionnement
// - 'api': Utilise l'API Modal (nécessite une clé API)
// - 'demo': Mode démonstration avec réponses simulées
const API_MODE = localStorage.getItem('notomai_api_mode') || 'demo';

// Clé API (stockée dans localStorage après connexion)
let API_KEY = localStorage.getItem('notomai_api_key') || null;

// ============================================
// INITIALISATION SUPABASE
// ============================================
let supabaseClient = null;
try {
    if (window.supabase) {
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    } else {
        console.warn('Supabase non chargé - mode démo uniquement');
    }
} catch (e) {
    console.warn('Erreur init Supabase:', e);
}

// ============================================
// ETAT DE L'APPLICATION
// ============================================
let state = {
    user: null,
    etude: null,
    conversationId: null,
    messages: [],
    currentFeedbackIndex: null,
    uploadedFiles: [],
    isRecording: false,
    recognition: null,
    lastExtractedTitre: null,  // Dernier titre extrait via l'API
    apiConnected: false        // Statut de connexion à l'API
};

// ============================================
// DONNÉES NOTAIRE (par défaut Charlotte Diaz)
// ============================================
const DEFAULT_NOTAIRE = {
    prenom: 'Charlotte',
    nom: 'Diaz',
    titre: 'Me',
    role: 'Notaire',
    etude: 'Étude Diaz & Associés'
};

// ============================================
// INITIALISATION
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Charger l'utilisateur (ou mode demo)
        await initUser();
    } catch (error) {
        console.warn('Erreur initUser, mode démo activé:', error);
        // Utiliser les valeurs par défaut
        state.user = { ...DEFAULT_NOTAIRE, id: 'demo-user' };
        state.etude = { id: 'demo-etude', nom: DEFAULT_NOTAIRE.etude };
        const userNameEl = document.getElementById('userName');
        if (userNameEl) userNameEl.textContent = `${state.user.titre} ${state.user.prenom} ${state.user.nom}`;
    }

    // Charger les suggestions intelligentes (si sur page chat)
    if (typeof loadSmartSuggestions === 'function') {
        loadSmartSuggestions();
    }

    // Afficher message de bienvenue (si sur page chat)
    if (typeof addAssistantMessage === 'function' && state.user) {
        addAssistantMessage(
            `Bonjour ${state.user.titre} ${state.user.nom}, comment puis-je vous aider aujourd'hui ?\n\nJe peux vous aider à :\n- Créer des actes (vente, promesse, règlement)\n- Rechercher des dossiers ou clients\n- Répondre à vos questions`,
            ['Créer un acte de vente', 'Voir mes dossiers en cours', 'Rechercher un client']
        );
    }

    // Auto-resize du textarea
    const input = document.getElementById('chatInput');
    if (input) {
        input.addEventListener('input', autoResize);
        input.addEventListener('keydown', handleKeyDown);
    }

    // Drag & drop pour fichiers
    if (typeof setupDragDrop === 'function') {
        setupDragDrop();
    }

    // Initialiser la reconnaissance vocale
    if (typeof initVoiceRecognition === 'function') {
        initVoiceRecognition();
    }

    console.log('Notomai initialisé OK');
});

async function initUser() {
    // Essayer de récupérer l'utilisateur connecté
    let user = null;
    try {
        if (supabaseClient) {
            const { data } = await supabaseClient.auth.getUser();
            user = data?.user;
        }
    } catch (e) {
        console.warn('Erreur auth Supabase:', e);
    }

    if (user) {
        // Utilisateur connecté - charger ses infos
        const { data: etudeUser } = await supabaseClient
            .from('etude_users')
            .select('role, etude_id, etudes(nom)')
            .eq('user_id', user.id)
            .single();

        // Extraire prenom/nom depuis l'email ou metadata
        const emailParts = user.email.split('@')[0].split('.');
        const prenom = capitalize(emailParts[0] || 'Utilisateur');
        const nom = capitalize(emailParts[1] || '');

        state.user = {
            id: user.id,
            email: user.email,
            prenom: user.user_metadata?.prenom || prenom,
            nom: user.user_metadata?.nom || nom,
            titre: etudeUser?.role === 'notaire' ? 'Me' : '',
            role: etudeUser?.role || 'notaire'
        };
        state.etude = {
            id: etudeUser?.etude_id,
            nom: etudeUser?.etudes?.nom || 'Mon étude'
        };
    } else {
        // Mode démo avec Charlotte Diaz
        state.user = {
            id: 'demo-user',
            ...DEFAULT_NOTAIRE
        };
        state.etude = {
            id: 'demo-etude',
            nom: DEFAULT_NOTAIRE.etude
        };
    }

    // Mettre à jour l'UI
    updateUserUI();
}

function updateUserUI() {
    if (!state.user) return;

    const fullName = `${state.user.titre} ${state.user.prenom} ${state.user.nom}`.trim();

    const userNameEl = document.getElementById('userName');
    const userRoleEl = document.getElementById('userRole');
    const userEtudeEl = document.getElementById('userEtude');
    const userAvatarEl = document.getElementById('userAvatar');
    const headerTitleEl = document.getElementById('headerTitle');

    if (userNameEl) userNameEl.textContent = fullName;
    if (userRoleEl) userRoleEl.textContent = state.user.role;
    if (userEtudeEl) userEtudeEl.textContent = state.etude.nom;
    if (userAvatarEl) userAvatarEl.textContent = state.user.prenom[0].toUpperCase();
    if (headerTitleEl) headerTitleEl.textContent = `Bonjour, ${fullName}`;
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

// ============================================
// SUGGESTIONS INTELLIGENTES
// ============================================
function loadSmartSuggestions() {
    const container = document.getElementById('smartSuggestions');
    if (!container) return;

    const suggestions = [
        {
            icon: '📄',
            text: 'Continuer le dossier Dupont',
            badge: 'En cours',
            action: 'continuer_dossier_dupont'
        },
        {
            icon: '✍️',
            text: 'Nouvelle vente',
            action: 'creer_vente'
        },
        {
            icon: '📋',
            text: 'Promesse Martin',
            badge: 'Brouillon',
            action: 'continuer_promesse_martin'
        },
        {
            icon: '🔍',
            text: 'Rechercher un client',
            action: 'rechercher'
        }
    ];

    container.innerHTML = suggestions.map(s => `
        <div class="smart-suggestion" onclick="handleSmartSuggestion('${s.action}')">
            <span class="icon">${s.icon}</span>
            <span class="text">${s.text}</span>
            ${s.badge ? `<span class="badge">${s.badge}</span>` : ''}
        </div>
    `).join('');
}

function handleSmartSuggestion(action) {
    const actions = {
        'continuer_dossier_dupont': 'Je souhaite continuer le dossier Dupont',
        'creer_vente': 'Je veux créer un acte de vente',
        'continuer_promesse_martin': 'Je souhaite reprendre la promesse Martin',
        'rechercher': 'Je veux rechercher un client'
    };

    const message = actions[action];
    if (message) {
        const input = document.getElementById('chatInput');
        if (input) {
            input.value = message;
            sendMessage();
        }
    }
}

// ============================================
// GESTION DES MESSAGES
// ============================================
function addMessage(role, content, suggestions = []) {
    const messagesDiv = document.getElementById('messages');
    if (!messagesDiv) return;

    const messageIndex = state.messages.length;
    state.messages.push({ role, content, timestamp: new Date(), data: null });

    const avatarContent = role === 'assistant' ? 'N' : state.user.prenom[0].toUpperCase();

    const messageHtml = `
        <div class="message ${role}">
            <div class="message-avatar">${avatarContent}</div>
            <div class="message-content">
                <div class="message-bubble">${formatMessage(content)}</div>
                <div class="message-time">${formatTime(new Date())}</div>
                ${role === 'assistant' ? `
                    <div class="message-feedback">
                        <button class="feedback-btn positive" onclick="handleFeedback(${messageIndex}, 1)">
                            👍 Utile
                        </button>
                        <button class="feedback-btn negative" onclick="handleFeedback(${messageIndex}, -1)">
                            👎 À améliorer
                        </button>
                    </div>
                    ${suggestions.length > 0 ? `
                        <div class="suggestions">
                            ${suggestions.map(s => `
                                <button class="suggestion-btn" onclick="sendSuggestion('${s}')">${s}</button>
                            `).join('')}
                        </div>
                    ` : ''}
                ` : ''}
            </div>
        </div>
    `;

    messagesDiv.insertAdjacentHTML('beforeend', messageHtml);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function addUserMessage(content) {
    addMessage('user', content);
}

function addAssistantMessage(content, suggestions = []) {
    addMessage('assistant', content, suggestions);
}

function formatMessage(content) {
    // Detect questionnaire progress pattern: [XX%] Section: Name — Question
    let html = content;

    // Replace progress indicator [XX%] **Label** with a visual progress bar
    html = html.replace(/\[(\d+)%\]\s*\*\*(.+?)\*\*/g, (match, pct, label) => {
        const percent = parseInt(pct);
        return `<div class="questionnaire-progress">` +
            `<div class="progress-bar"><div class="progress-fill" style="width:${percent}%"></div></div>` +
            `<div class="progress-label">${percent}% — <span class="section-name">${label.trim()}</span></div>` +
            `</div>`;
    });

    // Replace [100%] standalone (completion message)
    html = html.replace(/\[100%\]/g,
        `<div class="questionnaire-progress">` +
        `<div class="progress-bar"><div class="progress-fill" style="width:100%"></div></div>` +
        `<div class="progress-label">100% — Collecte terminee</div></div>`
    );

    // Standard markdown formatting
    html = html
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    return html;
}

function formatTime(date) {
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

// ============================================
// ENVOI DE MESSAGE
// ============================================
async function sendMessage() {
    console.log('sendMessage appelé');
    const input = document.getElementById('chatInput');
    if (!input) return;

    const content = input.value.trim();
    console.log('Contenu:', content);

    if (!content && state.uploadedFiles.length === 0) {
        console.log('Pas de contenu, retour');
        return;
    }

    // Construire le message avec fichiers si présents
    let messageContent = content;
    if (state.uploadedFiles.length > 0) {
        const fileNames = state.uploadedFiles.map(f => f.name).join(', ');
        messageContent += content ? `\n\n📎 Fichiers joints : ${fileNames}` : `📎 Fichiers joints : ${fileNames}`;
    }

    // Ajouter le message utilisateur
    addUserMessage(messageContent);
    input.value = '';
    state.uploadedFiles = [];

    const uploadedFilesEl = document.getElementById('uploadedFiles');
    if (uploadedFilesEl) uploadedFilesEl.innerHTML = '';

    const fileUploadArea = document.getElementById('fileUploadArea');
    if (fileUploadArea) fileUploadArea.classList.remove('visible');

    autoResize.call(input);

    // Afficher l'indicateur de frappe
    showTyping(true);

    try {
        // Appeler l'API (Modal ou mode demo)
        const response = await callChatAPI(content);

        // Cacher l'indicateur
        showTyping(false);

        // Afficher la réponse
        addAssistantMessage(response.content, response.suggestions || []);

        // Stocker les métadonnées API sur le dernier message (pour téléchargement)
        if (response.data || response.fichier_url || response.fichier_genere) {
            const lastMsg = state.messages[state.messages.length - 1];
            if (lastMsg) {
                lastMsg.data = response.data || {
                    fichier_url: response.fichier_url,
                    fichier_genere: response.fichier_genere
                };
            }
        }

        // Mettre à jour les suggestions intelligentes
        updateSmartSuggestions(response);

        // Sauvegarder la conversation dans Supabase
        await saveConversation();

    } catch (error) {
        console.error('Erreur:', error);
        showTyping(false);

        // Contextualized error message
        let errorMsg = "Desole, une erreur s'est produite.";
        let suggestions = ['Reessayer', 'Aide'];

        if (error.message && error.message.includes('credits') || error.message && error.message.includes('balance')) {
            errorMsg = "Le service IA n'est pas disponible (credits insuffisants). Contactez l'administrateur.";
            suggestions = ['Aide'];
        } else if (error.message && (error.message.includes('401') || error.message.includes('403'))) {
            errorMsg = "Acces refuse. Verifiez votre cle API dans les parametres.";
            suggestions = ['Parametres'];
        } else if (error.message && error.message.includes('429')) {
            errorMsg = "Trop de requetes. Veuillez patienter quelques instants.";
            suggestions = ['Reessayer'];
        } else if (error.message && (error.message.includes('fetch') || error.message.includes('network') || error.message.includes('Failed'))) {
            errorMsg = "Connexion au serveur impossible. Verifiez votre connexion internet.";
            suggestions = ['Reessayer'];
        }

        addAssistantMessage(errorMsg, suggestions);
        showNotification(errorMsg, 'error');
    }
}

async function callChatAPI(message) {
    // Mode API: utilise l'API Modal avec Claude (anonymisation intégrée)
    if (API_MODE === 'api' && API_KEY) {
        try {
            // Préparer le contexte (titre chargé, dossier en cours, etc.)
            const context = {};
            if (state.lastExtractedTitre) {
                context.titre_charge = {
                    reference: state.lastExtractedTitre.reference,
                    vendeurs: state.lastExtractedTitre.donnees?.proprietaires_actuels,
                    bien: state.lastExtractedTitre.donnees?.bien
                };
            }
            if (state.currentDossier) {
                context.dossier = state.currentDossier;
            }

            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': API_KEY
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: state.conversationId || null,
                    context: Object.keys(context).length > 0 ? context : null
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erreur API');
            }

            const data = await response.json();

            // Mettre à jour le conversation_id pour maintenir le contexte
            if (data.conversation_id) {
                state.conversationId = data.conversation_id;
            }

            // Afficher un indicateur si l'anonymisation a été appliquée
            if (data.anonymisation_appliquee) {
                console.log('🔒 Données anonymisées avant envoi à Claude');
            }

            // Transformer la réponse API en format chatbot
            return {
                content: data.message,
                suggestions: getSuggestionsFromResponse(data),
                data: data,
                anonymized: data.anonymisation_appliquee
            };
        } catch (error) {
            console.error('Erreur API Chat:', error);

            // Fallback en mode démo si l'API échoue
            if (error.message.includes('401') || error.message.includes('403')) {
                showNotification('Clé API invalide. Passage en mode démo.', 'warning');
                localStorage.setItem('notomai_api_mode', 'demo');
            }

            return simulateResponse(message);
        }
    } else {
        // Mode démo - réponses simulées
        return simulateResponse(message);
    }
}

// Génère des suggestions basées sur la réponse de l'API
function getSuggestionsFromResponse(data) {
    // Utiliser les suggestions du backend si fournies
    if (data.suggestions && data.suggestions.length > 0) {
        return data.suggestions;
    }

    const suggestions = [];
    const message = (data.message || '').toLowerCase();
    const intention = data.analyse?.intention || data.intention;

    // Analyser le contenu de la réponse pour suggérer des actions pertinentes
    if (message.includes('promesse') || message.includes('prépare')) {
        suggestions.push('Générer le document', 'Modifier les données', 'Annuler');
    } else if (message.includes('vente') || intention === 'creer_acte') {
        suggestions.push('Confirmer', 'Modifier', 'Annuler');
    } else if (message.includes('recherch') || intention === 'rechercher') {
        suggestions.push('Affiner la recherche', 'Nouveau dossier');
    } else if (message.includes('titre') || message.includes('propriété')) {
        suggestions.push('Créer une promesse depuis ce titre', 'Voir les détails');
    } else if (data.fichier_genere) {
        suggestions.push('Télécharger le document', 'Modifier', 'Nouveau dossier');
    } else {
        suggestions.push('Créer un acte', 'Voir mes dossiers', 'Aide');
    }

    return suggestions;
}

// Upload de fichier vers l'API (titre de propriété)
async function uploadTitreToAPI(file) {
    if (API_MODE !== 'api' || !API_KEY) {
        return { success: false, message: 'Mode démo - upload simulé' };
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('reference', `UPLOAD-${Date.now()}`);

    try {
        const response = await fetch(`${API_BASE_URL}/titres/upload`, {
            method: 'POST',
            headers: {
                'X-API-Key': API_KEY
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erreur upload');
        }

        const data = await response.json();
        return {
            success: true,
            data: data,
            message: `Titre extrait avec ${Math.round(data.confiance_extraction * 100)}% de confiance`
        };
    } catch (error) {
        console.error('Erreur upload titre:', error);
        return { success: false, message: error.message };
    }
}

// Configuration de la clé API
function setAPIKey(key) {
    API_KEY = key;
    localStorage.setItem('notomai_api_key', key);
    localStorage.setItem('notomai_api_mode', 'api');
    showNotification('Clé API configurée. Mode production activé.', 'success');
}

// Passer en mode démo
function setDemoMode() {
    localStorage.setItem('notomai_api_mode', 'demo');
    localStorage.removeItem('notomai_api_key');
    API_KEY = null;
    showNotification('Mode démonstration activé.', 'info');
}

// Vérifier la connexion à l'API
async function checkAPIConnection() {
    if (!API_KEY) return { connected: false, reason: 'Pas de clé API' };

    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET'
        });

        if (response.ok) {
            const data = await response.json();
            return {
                connected: true,
                status: data.status,
                version: data.version
            };
        }
        return { connected: false, reason: 'API indisponible' };
    } catch (error) {
        return { connected: false, reason: error.message };
    }
}

// Afficher une notification
function showNotification(message, type = 'info') {
    // Créer l'élément de notification s'il n'existe pas
    let notifContainer = document.getElementById('notifications');
    if (!notifContainer) {
        notifContainer = document.createElement('div');
        notifContainer.id = 'notifications';
        notifContainer.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 10000;';
        document.body.appendChild(notifContainer);
    }

    const colors = {
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
        info: '#3b82f6'
    };

    const notif = document.createElement('div');
    notif.style.cssText = `
        background: ${colors[type] || colors.info};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        animation: slideIn 0.3s ease;
        max-width: 350px;
    `;
    notif.textContent = message;

    notifContainer.appendChild(notif);

    // Supprimer après 4 secondes
    setTimeout(() => {
        notif.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notif.remove(), 300);
    }, 4000);
}

function simulateResponse(message) {
    const msgLower = message.toLowerCase();

    if (msgLower.includes('vente') || msgLower.includes('creer')) {
        return {
            content: `Je vais vous aider à créer un acte de vente, ${state.user.titre} ${state.user.nom}.\n\nPour commencer, j'ai besoin de quelques informations :\n\n1. **Quel est le nom du vendeur ?**\n2. **Quel type de bien s'agit-il ?** (appartement, maison, terrain)`,
            suggestions: ['Appartement en copropriété', 'Maison individuelle', 'Annuler']
        };
    }

    if (msgLower.includes('dossier') || msgLower.includes('dupont')) {
        return {
            content: `Voici vos dossiers en cours :\n\n- **Dossier 2026-001** - Vente Dupont (en cours)\n- **Dossier 2026-002** - Promesse Martin (brouillon)\n- **Dossier 2025-089** - Succession Leroy (terminé)\n\nQue souhaitez-vous faire ?`,
            suggestions: ['Ouvrir Dossier 2026-001', 'Créer un nouveau dossier', 'Rechercher']
        };
    }

    if (msgLower.includes('client') || msgLower.includes('rechercher')) {
        return {
            content: `Quel client recherchez-vous ? Vous pouvez me donner :\n\n- Un nom (ex: Dupont)\n- Un numéro de dossier\n- Une adresse de bien`,
            suggestions: []
        };
    }

    if (msgLower.includes('aide') || msgLower.includes('help')) {
        return {
            content: `Je peux vous aider à :\n\n📄 **Créer des actes** - vente, promesse, règlement de copropriété\n📁 **Gérer vos dossiers** - créer, modifier, rechercher\n👥 **Gérer vos clients** - ajouter, rechercher, modifier\n🔍 **Rechercher** - dossiers, clients, actes\n\nQue souhaitez-vous faire ?`,
            suggestions: ['Créer un acte', 'Voir mes dossiers', 'Rechercher un client']
        };
    }

    if (msgLower.includes('fichier') || msgLower.includes('joint')) {
        return {
            content: `J'ai bien reçu vos fichiers. Je vais les analyser.\n\n🔒 **Sécurité** : Vos documents sont chiffrés et ne quittent jamais nos serveurs européens.`,
            suggestions: ['Extraire les informations', 'Créer un acte à partir du document']
        };
    }

    // Réponse par défaut
    return {
        content: `J'ai bien compris votre demande, ${state.user.titre} ${state.user.nom}.\n\nEn mode démonstration, mes capacités sont limitées. En production, je pourrai :\n- Comprendre vos demandes en langage naturel\n- Accéder à vos dossiers et clients\n- Créer et modifier des actes\n- Apprendre de vos corrections`,
        suggestions: ['Créer une vente', 'Voir mes dossiers', 'Aide']
    };
}

function updateSmartSuggestions(response) {
    // Mettre à jour les suggestions basées sur la conversation
    // En production, cela serait plus sophistiqué
}

// ============================================
// ACTIONS RAPIDES
// ============================================
function quickAction(action) {
    const actions = {
        'creer_vente': 'Je souhaite créer un acte de vente',
        'creer_promesse': 'Je souhaite créer une promesse de vente',
        'mes_dossiers': 'Montre-moi mes dossiers en cours',
        'rechercher': 'Je veux rechercher un client',
        'aide': 'Aide-moi à comprendre ce que tu peux faire'
    };

    const message = actions[action];
    if (message) {
        const input = document.getElementById('chatInput');
        if (input) {
            input.value = message;
            sendMessage();
        }
    }
}

function sendSuggestion(text) {
    // Intercepter les suggestions de téléchargement
    if (text === 'Télécharger le document') {
        downloadGeneratedDocument();
        return;
    }
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = text;
        sendMessage();
    }
}

// ============================================
// TÉLÉCHARGEMENT DE DOCUMENTS
// ============================================
async function downloadGeneratedDocument() {
    // Chercher le dernier message avec fichier_url ou fichier_genere
    let fichierUrl = null;
    for (let i = state.messages.length - 1; i >= 0; i--) {
        const msg = state.messages[i];
        if (msg.role === 'assistant' && msg.data) {
            if (msg.data.fichier_url) {
                fichierUrl = msg.data.fichier_url;
                break;
            }
            if (msg.data.fichier_genere) {
                fichierUrl = `/files/${msg.data.fichier_genere}`;
                break;
            }
        }
    }

    if (!fichierUrl) {
        showNotification("Aucun document disponible au téléchargement.", 'warning');
        return;
    }

    try {
        showNotification("Téléchargement en cours...", 'info');

        const fullUrl = fichierUrl.startsWith('http')
            ? fichierUrl
            : `${API_BASE_URL}${fichierUrl}`;

        const response = await fetch(fullUrl, {
            method: 'GET',
            headers: API_KEY ? { 'X-API-Key': API_KEY } : {}
        });

        if (!response.ok) {
            throw new Error(`Erreur ${response.status}: ${response.statusText}`);
        }

        const blob = await response.blob();
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'acte_genere.docx';

        if (contentDisposition) {
            const match = contentDisposition.match(/filename="?(.+?)"?$/);
            if (match) filename = match[1];
        }

        // Déclencher le téléchargement
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        showNotification(`Document "${filename}" téléchargé !`, 'success');
    } catch (error) {
        console.error('Erreur téléchargement:', error);
        showNotification(`Erreur: ${error.message}`, 'error');
    }
}

// ============================================
// UPLOAD DE FICHIERS
// ============================================
function toggleUpload() {
    const area = document.getElementById('fileUploadArea');
    if (!area) return;

    area.classList.toggle('visible');
    if (area.classList.contains('visible')) {
        const fileInput = document.getElementById('fileInput');
        if (fileInput) fileInput.click();
    }
}

function setupDragDrop() {
    const area = document.getElementById('fileUploadArea');
    if (!area) return;

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        area.addEventListener(eventName, () => {
            area.classList.add('dragover');
            area.classList.add('visible');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        area.addEventListener(eventName, () => {
            area.classList.remove('dragover');
        }, false);
    });

    area.addEventListener('drop', handleDrop, false);
    area.addEventListener('click', () => {
        const fileInput = document.getElementById('fileInput');
        if (fileInput) fileInput.click();
    });
}

function handleDrop(e) {
    const files = e.dataTransfer.files;
    handleFiles(files);
}

function handleFileSelect(e) {
    handleFiles(e.target.files);
}

async function handleFiles(files) {
    const maxSize = 10 * 1024 * 1024; // 10 Mo
    const titreExtensions = ['.pdf', '.docx', '.doc'];

    for (const file of Array.from(files)) {
        if (file.size > maxSize) {
            showNotification(`Le fichier ${file.name} dépasse la taille maximale de 10 Mo`, 'error');
            continue;
        }

        const ext = '.' + file.name.split('.').pop().toLowerCase();
        const isTitre = titreExtensions.includes(ext);

        // En mode API, proposer d'extraire les titres automatiquement
        if (API_MODE === 'api' && API_KEY && isTitre) {
            const shouldExtract = confirm(
                `Voulez-vous extraire automatiquement les données du titre "${file.name}" ?\n\n` +
                `Cliquez OK pour extraire, ou Annuler pour simplement joindre le fichier.`
            );

            if (shouldExtract) {
                showNotification(`Extraction en cours pour ${file.name}...`, 'info');

                const result = await uploadTitreToAPI(file);

                if (result.success) {
                    showNotification(result.message, 'success');

                    // Afficher les données extraites dans le chat
                    const titreData = result.data.donnees;
                    let extractionSummary = `📄 **Titre extrait : ${file.name}**\n\n`;

                    if (titreData.proprietaires_actuels?.length > 0) {
                        const proprio = titreData.proprietaires_actuels[0];
                        extractionSummary += `👤 **Propriétaire** : ${proprio.civilite || ''} ${proprio.prenoms || ''} ${proprio.nom || ''}\n`;
                    }

                    if (titreData.bien?.adresse) {
                        const addr = titreData.bien.adresse;
                        extractionSummary += `🏠 **Bien** : ${addr.numero || ''} ${addr.voie || ''}, ${addr.code_postal || ''} ${addr.ville || ''}\n`;
                    }

                    if (titreData.bien?.lots?.length > 0) {
                        extractionSummary += `📋 **Lots** : ${titreData.bien.lots.length} lot(s)\n`;
                    }

                    extractionSummary += `\n✅ Confiance d'extraction : ${Math.round(result.data.confiance_extraction * 100)}%`;

                    addAssistantMessage(extractionSummary, [
                        'Créer une promesse depuis ce titre',
                        'Créer un acte de vente',
                        'Voir les détails complets'
                    ]);

                    // Stocker les données extraites pour usage ultérieur
                    state.lastExtractedTitre = result.data;
                    continue;
                } else {
                    showNotification(`Échec extraction: ${result.message}`, 'warning');
                }
            }
        }

        // Ajouter le fichier normalement
        state.uploadedFiles.push(file);
    }

    renderUploadedFiles();
}

function renderUploadedFiles() {
    const container = document.getElementById('uploadedFiles');
    if (!container) return;

    container.innerHTML = state.uploadedFiles.map((f, i) => `
        <div class="uploaded-file">
            <span>📄 ${f.name}</span>
            <span class="remove" onclick="removeFile(${i})">✕</span>
        </div>
    `).join('');
}

function removeFile(index) {
    state.uploadedFiles.splice(index, 1);
    renderUploadedFiles();
}

// ============================================
// DICTEE VOCALE
// ============================================
function initVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        state.recognition = new SpeechRecognition();
        state.recognition.lang = 'fr-FR';
        state.recognition.continuous = true;
        state.recognition.interimResults = true;

        state.recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                transcript += event.results[i][0].transcript;
            }
            const input = document.getElementById('chatInput');
            if (input) {
                input.value = transcript;
                autoResize.call(input);
            }
        };

        state.recognition.onerror = (event) => {
            console.error('Erreur reconnaissance vocale:', event.error);
            stopRecording();
        };

        state.recognition.onend = () => {
            if (state.isRecording) {
                state.recognition.start();
            }
        };
    }
}

function toggleVoice() {
    if (!state.recognition) {
        alert('La reconnaissance vocale n\'est pas supportée par votre navigateur');
        return;
    }

    if (state.isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

function startRecording() {
    state.isRecording = true;
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) voiceBtn.classList.add('recording');
    state.recognition.start();
}

function stopRecording() {
    state.isRecording = false;
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) voiceBtn.classList.remove('recording');
    if (state.recognition) {
        state.recognition.stop();
    }
}

// ============================================
// FEEDBACK (APPRENTISSAGE CONTINU)
// ============================================
function handleFeedback(messageIndex, rating) {
    if (rating === 1) {
        saveFeedback(messageIndex, rating, null, null);
        markFeedbackGiven(messageIndex, 'positive');
    } else {
        state.currentFeedbackIndex = messageIndex;
        const modal = document.getElementById('feedbackModal');
        if (modal) modal.classList.add('visible');
    }
}

function closeFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    if (modal) modal.classList.remove('visible');
    state.currentFeedbackIndex = null;
}

async function submitFeedback() {
    const typeEl = document.getElementById('feedbackType');
    const correctionEl = document.getElementById('feedbackCorrection');

    const type = typeEl ? typeEl.value : null;
    const correction = correctionEl ? correctionEl.value : null;

    await saveFeedback(state.currentFeedbackIndex, -1, type, correction);
    markFeedbackGiven(state.currentFeedbackIndex, 'negative');

    closeFeedbackModal();

    addAssistantMessage(
        `Merci pour votre retour, ${state.user.titre} ${state.user.nom} ! Il m'aidera à m'améliorer.`,
        []
    );
}

async function saveFeedback(messageIndex, rating, type, correction) {
    if (!state.conversationId || !supabaseClient) return;

    try {
        await supabaseClient.from('feedbacks').insert({
            conversation_id: state.conversationId,
            etude_id: state.etude.id,
            user_id: state.user.id,
            message_index: messageIndex,
            agent_response: state.messages[messageIndex]?.content,
            rating,
            feedback_type: type,
            correction
        });
    } catch (error) {
        console.error('Erreur sauvegarde feedback:', error);
    }
}

function markFeedbackGiven(messageIndex, type) {
    const messages = document.querySelectorAll('.message.assistant');
    const message = messages[Math.floor(messageIndex / 2)];
    if (message) {
        const btn = message.querySelector(`.feedback-btn.${type}`);
        if (btn) btn.classList.add('selected');
    }
}

// ============================================
// SAUVEGARDE CONVERSATION
// ============================================
async function saveConversation() {
    if (state.user.id === 'demo-user' || !supabaseClient) return;

    try {
        if (!state.conversationId) {
            const { data, error } = await supabaseClient
                .from('conversations')
                .insert({
                    etude_id: state.etude.id,
                    user_id: state.user.id,
                    messages: state.messages,
                    message_count: state.messages.length
                })
                .select('id')
                .single();

            if (data) state.conversationId = data.id;
        } else {
            await supabaseClient
                .from('conversations')
                .update({
                    messages: state.messages,
                    message_count: state.messages.length,
                    last_message_at: new Date().toISOString()
                })
                .eq('id', state.conversationId);
        }
    } catch (error) {
        console.error('Erreur sauvegarde conversation:', error);
    }
}

// ============================================
// UTILITAIRES UI
// ============================================
function showTyping(show) {
    const indicator = document.getElementById('typingIndicator');
    const sendBtn = document.getElementById('sendBtn');

    if (indicator) {
        indicator.classList.toggle('visible', show);
        // Use skeleton loader when typing
        if (show) {
            indicator.innerHTML = `
                <div class="skeleton-loader">
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                    <div class="skeleton-line"></div>
                </div>
                <span>L'assistant redige...</span>
            `;
        }
    }
    if (sendBtn) sendBtn.disabled = show;
}

function autoResize() {
    this.style.height = 'auto';
    this.style.height = Math.min(this.scrollHeight, 120) + 'px';
}

function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

// ============================================
// AUTHENTIFICATION
// ============================================
async function login(email, password) {
    if (!supabaseClient) {
        console.error('Supabase non initialisé');
        return { error: 'Service non disponible' };
    }

    const { data, error } = await supabaseClient.auth.signInWithPassword({
        email,
        password
    });

    if (error) {
        return { error: error.message };
    }

    // Rediriger vers le chat
    window.location.href = 'pages/chat.html';
    return { data };
}

async function loginWithMagicLink(email) {
    if (!supabaseClient) {
        console.error('Supabase non initialisé');
        return { error: 'Service non disponible' };
    }

    const { data, error } = await supabaseClient.auth.signInWithOtp({
        email,
        options: {
            emailRedirectTo: window.location.origin + '/frontend/pages/chat.html'
        }
    });

    if (error) {
        return { error: error.message };
    }

    return { data, message: 'Vérifiez votre boîte mail !' };
}

async function logout() {
    if (supabaseClient) {
        await supabaseClient.auth.signOut();
    }
    window.location.href = '../index.html';
}

async function checkAuth() {
    if (!supabaseClient) return null;

    const { data } = await supabaseClient.auth.getUser();
    return data?.user;
}

// ============================================
// GÉNÉRATION DEPUIS TITRE EXTRAIT
// ============================================
async function createPromesseFromTitre() {
    if (!state.lastExtractedTitre) {
        showNotification('Aucun titre extrait. Veuillez d\'abord uploader un titre de propriété.', 'warning');
        return;
    }

    if (API_MODE !== 'api' || !API_KEY) {
        // Mode démo - simuler
        addAssistantMessage(
            `📝 **Création de promesse depuis le titre**\n\n` +
            `En mode production, je créerais automatiquement une promesse avec :\n` +
            `- Les propriétaires comme promettants\n` +
            `- Le bien pré-rempli\n` +
            `- L'origine de propriété documentée\n\n` +
            `Passez en mode API pour activer cette fonctionnalité.`,
            ['Configurer l\'API', 'Mode démo']
        );
        return;
    }

    showTyping(true);

    try {
        const titreId = state.lastExtractedTitre.id;

        // Demander les informations manquantes
        addAssistantMessage(
            `📋 **Création de promesse depuis le titre ${state.lastExtractedTitre.reference}**\n\n` +
            `J'ai besoin de quelques informations complémentaires :\n\n` +
            `1. **Qui sont les bénéficiaires (acquéreurs) ?**\n` +
            `2. **Quel est le prix de vente ?**\n` +
            `3. **Y a-t-il un financement par prêt ?**`,
            ['Prix : 300 000 €', 'Prix : 450 000 €', 'Autre prix']
        );

        // Stocker l'intention de créer une promesse
        state.pendingPromesse = {
            titreId: titreId,
            step: 'beneficiaires'
        };

    } catch (error) {
        console.error('Erreur création promesse:', error);
        showNotification('Erreur lors de la création de la promesse', 'error');
    }

    showTyping(false);
}

// ============================================
// PANNEAU DE CONFIGURATION API
// ============================================
function showSettingsModal() {
    // Supprimer le modal existant s'il y en a un
    const existingModal = document.getElementById('settingsModal');
    if (existingModal) existingModal.remove();

    const currentMode = API_MODE === 'api' ? 'Production (API)' : 'Démonstration';
    const apiKeyDisplay = API_KEY ? API_KEY.substring(0, 12) + '...' : 'Non configurée';

    const modalHtml = `
        <div id="settingsModal" class="modal-overlay visible" onclick="closeSettingsModal(event)">
            <div class="modal-content" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h3>⚙️ Configuration</h3>
                    <button class="modal-close" onclick="closeSettingsModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="setting-group">
                        <label>Mode actuel</label>
                        <div class="setting-value">${currentMode}</div>
                    </div>

                    <div class="setting-group">
                        <label>Clé API</label>
                        <div class="setting-value">${apiKeyDisplay}</div>
                    </div>

                    <div class="setting-group">
                        <label for="apiKeyInput">Nouvelle clé API</label>
                        <input type="password" id="apiKeyInput" placeholder="nai_xxxxxxxxxxxx" class="setting-input">
                        <small>Format : nai_... (obtenue depuis votre espace admin)</small>
                    </div>

                    <div class="setting-actions">
                        <button class="btn btn-primary" onclick="saveAPISettings()">
                            Activer le mode Production
                        </button>
                        <button class="btn btn-secondary" onclick="setDemoMode(); closeSettingsModal();">
                            Passer en mode Démo
                        </button>
                    </div>

                    <div class="setting-group" style="margin-top: 20px;">
                        <label>Statut de l'API</label>
                        <div id="apiStatus" class="setting-value">Vérification...</div>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Vérifier le statut de l'API
    checkAndDisplayAPIStatus();
}

async function checkAndDisplayAPIStatus() {
    const statusEl = document.getElementById('apiStatus');
    if (!statusEl) return;

    const result = await checkAPIConnection();

    if (result.connected) {
        statusEl.innerHTML = `<span style="color: #10b981;">✅ Connecté (v${result.version})</span>`;
        state.apiConnected = true;
    } else {
        statusEl.innerHTML = `<span style="color: #ef4444;">❌ ${result.reason}</span>`;
        state.apiConnected = false;
    }
}

function closeSettingsModal(event) {
    if (event && event.target.id !== 'settingsModal') return;
    const modal = document.getElementById('settingsModal');
    if (modal) modal.remove();
}

function saveAPISettings() {
    const input = document.getElementById('apiKeyInput');
    if (!input) return;

    const key = input.value.trim();

    if (!key) {
        showNotification('Veuillez entrer une clé API', 'warning');
        return;
    }

    if (!key.startsWith('nai_')) {
        showNotification('La clé API doit commencer par "nai_"', 'warning');
        return;
    }

    setAPIKey(key);
    closeSettingsModal();

    // Vérifier la connexion
    setTimeout(async () => {
        const result = await checkAPIConnection();
        if (result.connected) {
            showNotification(`Connecté à l'API NotaireAI v${result.version}`, 'success');
        } else {
            showNotification(`Impossible de se connecter: ${result.reason}`, 'error');
        }
    }, 500);
}

// ============================================
// INITIALISATION API AU CHARGEMENT
// ============================================
async function initAPI() {
    // Vérifier si une clé API est configurée
    if (API_KEY) {
        const result = await checkAPIConnection();
        state.apiConnected = result.connected;

        if (result.connected) {
            console.log(`✅ API NotaireAI connectée (v${result.version})`);
        } else {
            console.warn(`⚠️ API non accessible: ${result.reason}`);
        }
    }

    // Afficher le mode actuel dans la console
    console.log(`Mode: ${API_MODE === 'api' ? 'Production' : 'Démonstration'}`);
}

// Appeler initAPI au chargement
if (typeof window !== 'undefined') {
    window.addEventListener('load', initAPI);
}
