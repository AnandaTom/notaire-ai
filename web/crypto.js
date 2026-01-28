/**
 * Module de chiffrement E2E (End-to-End) pour NotaireAI
 * Utilise Web Crypto API (AES-256-GCM)
 *
 * La clé de chiffrement est dans le fragment d'URL (#key=...)
 * Le fragment n'est JAMAIS envoyé au serveur (sécurité côté client)
 */

const CryptoModule = {
    /**
     * Génère une clé de chiffrement aléatoire (256 bits)
     * @returns {Promise<{key: CryptoKey, keyBase64: string}>}
     */
    async generateKey() {
        const key = await crypto.subtle.generateKey(
            { name: 'AES-GCM', length: 256 },
            true, // extractable
            ['encrypt', 'decrypt']
        );

        const rawKey = await crypto.subtle.exportKey('raw', key);
        const keyBase64 = this.arrayBufferToBase64(rawKey);

        return { key, keyBase64 };
    },

    /**
     * Importe une clé depuis une chaîne base64
     * @param {string} keyBase64
     * @returns {Promise<CryptoKey>}
     */
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

    /**
     * Chiffre des données avec AES-256-GCM
     * @param {object} data - Données à chiffrer (sera converti en JSON)
     * @param {CryptoKey} key - Clé de chiffrement
     * @returns {Promise<{encrypted: string, iv: string}>}
     */
    async encrypt(data, key) {
        const iv = crypto.getRandomValues(new Uint8Array(12)); // 96 bits IV pour GCM
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

    /**
     * Déchiffre des données
     * @param {string} encryptedBase64
     * @param {string} ivBase64
     * @param {CryptoKey} key
     * @returns {Promise<object>}
     */
    async decrypt(encryptedBase64, ivBase64, key) {
        const encryptedBuffer = this.base64ToArrayBuffer(encryptedBase64);
        const iv = this.base64ToArrayBuffer(ivBase64);

        const decryptedBuffer = await crypto.subtle.decrypt(
            { name: 'AES-GCM', iv },
            key,
            encryptedBuffer
        );

        const decryptedText = new TextDecoder().decode(decryptedBuffer);
        return JSON.parse(decryptedText);
    },

    /**
     * Génère un token unique pour l'URL (64 caractères hex)
     * @returns {string}
     */
    generateToken() {
        const bytes = crypto.getRandomValues(new Uint8Array(32));
        return Array.from(bytes)
            .map(b => b.toString(16).padStart(2, '0'))
            .join('');
    },

    /**
     * Extrait la clé du fragment d'URL
     * @returns {string|null}
     */
    getKeyFromUrl() {
        const hash = window.location.hash;
        if (!hash) return null;

        const params = new URLSearchParams(hash.substring(1));
        return params.get('key');
    },

    /**
     * Extrait le token de l'URL
     * @returns {string|null}
     */
    getTokenFromUrl() {
        const path = window.location.pathname;
        const match = path.match(/\/fill\/([a-f0-9]{64})/);
        return match ? match[1] : null;
    },

    // Utilitaires de conversion
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

// Export pour utilisation dans d'autres scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CryptoModule;
}
