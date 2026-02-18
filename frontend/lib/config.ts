/**
 * Configuration centralisee de l'application Notomai.
 *
 * Toutes les constantes d'environnement passent par ce fichier.
 * Aucun composant ne doit hardcoder d'URL ou de cle.
 */

// --- API Backend (Modal) ---
export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'https://notomai--notaire-ai-fastapi-app.modal.run'

export const API_KEY = process.env.NEXT_PUBLIC_API_KEY || ''

// --- Timeouts (ms) ---
export const FETCH_TIMEOUT = 30_000
export const SSE_RECONNECT_DELAY = 2_000

// --- Feature flags ---
export const WORKFLOW_SUPPORTED_TYPES = ['promesse_vente'] as const
