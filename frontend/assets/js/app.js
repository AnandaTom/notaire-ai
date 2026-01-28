// ============================================
// NOTOMAI - Application JavaScript
// ============================================

// ============================================
// CONFIGURATION
// ============================================
const SUPABASE_URL = 'https://wcklvjckzktijtgakdrk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indja2x2amNremt0aWp0Z2FrZHJrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkwMDI1NzksImV4cCI6MjA4NDU3ODU3OX0.lyfrGeuVSkivopQVWlq3tf6Uo5k4Z6BqOEPt5WuYXS4';

// Pour le prototype, on simule Modal avec un endpoint local
// En production: MODAL_ENDPOINT = 'https://votre-app--chat.modal.run'
const MODAL_ENDPOINT = null; // null = mode demo

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
    recognition: null
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
    state.messages.push({ role, content, timestamp: new Date() });

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
    return content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
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

        // Mettre à jour les suggestions intelligentes
        updateSmartSuggestions(response);

        // Sauvegarder la conversation dans Supabase
        await saveConversation();

    } catch (error) {
        console.error('Erreur:', error);
        showTyping(false);
        addAssistantMessage(
            "Désolé, une erreur s'est produite. Pouvez-vous reformuler votre demande ?",
            ['Réessayer', 'Aide']
        );
    }
}

async function callChatAPI(message) {
    if (MODAL_ENDPOINT) {
        // Appel réel à Modal
        const response = await fetch(MODAL_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                user_id: state.user.id,
                etude_id: state.etude.id,
                conversation_id: state.conversationId,
                history: state.messages.slice(-10)
            })
        });
        return await response.json();
    } else {
        // Mode démo - réponses simulées
        return simulateResponse(message);
    }
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
    const input = document.getElementById('chatInput');
    if (input) {
        input.value = text;
        sendMessage();
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

function handleFiles(files) {
    const maxSize = 10 * 1024 * 1024; // 10 Mo

    Array.from(files).forEach(file => {
        if (file.size > maxSize) {
            alert(`Le fichier ${file.name} dépasse la taille maximale de 10 Mo`);
            return;
        }

        state.uploadedFiles.push(file);
    });

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

    if (indicator) indicator.classList.toggle('visible', show);
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
