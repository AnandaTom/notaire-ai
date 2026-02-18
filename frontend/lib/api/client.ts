/**
 * Client HTTP centralise pour l'API Notomai.
 *
 * Responsabilites :
 * - Auth via X-API-Key (verifie cote backend contre Supabase agent_api_keys)
 * - Timeout configurable
 * - Erreurs typees et user-friendly (pas de stack traces backend exposees)
 * - SSE (Server-Sent Events) pour le streaming
 */

import { API_URL, API_KEY, FETCH_TIMEOUT } from '@/lib/config'

// ---------------------------------------------------------------------------
// Types d'erreur
// ---------------------------------------------------------------------------

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// ---------------------------------------------------------------------------
// Headers
// ---------------------------------------------------------------------------

function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (API_KEY) {
    headers['X-API-Key'] = API_KEY
  }

  return headers
}

// ---------------------------------------------------------------------------
// Fetch wrapper
// ---------------------------------------------------------------------------

/**
 * Fetch typee avec timeout, auth et gestion d'erreur.
 * Jamais appele directement par les composants — passer par les fonctions de api/index.ts.
 */
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT)

  try {
    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        ...getHeaders(),
        ...(options.headers as Record<string, string> | undefined),
      },
      signal: controller.signal,
    })

    if (!response.ok) {
      const body = await response.json().catch(() => ({}))
      const detail = body.detail || body.message || `Erreur serveur (${response.status})`

      throw new ApiError(
        mapErrorMessage(response.status, detail),
        response.status,
        body.code,
      )
    }

    return (await response.json()) as T
  } catch (err) {
    if (err instanceof ApiError) throw err

    if (err instanceof DOMException && err.name === 'AbortError') {
      throw new ApiError(
        'Le serveur met trop de temps a repondre. Reessayez.',
        408,
        'TIMEOUT',
      )
    }

    throw new ApiError(
      'Impossible de contacter le serveur. Verifiez votre connexion.',
      0,
      'NETWORK_ERROR',
    )
  } finally {
    clearTimeout(timeout)
  }
}

// ---------------------------------------------------------------------------
// SSE helper
// ---------------------------------------------------------------------------

export interface SSECallbacks<T> {
  onEvent: (event: T) => void
  onError: (error: string) => void
  onComplete?: () => void
}

/**
 * Ouvre une connexion EventSource vers un endpoint SSE.
 * Retourne une fonction cleanup pour fermer la connexion.
 */
export function apiSSE<T>(
  path: string,
  callbacks: SSECallbacks<T>,
): () => void {
  const url = new URL(`${API_URL}${path}`)

  // EventSource ne supporte pas les headers custom.
  // Le backend accepte l'API key en query param pour les SSE.
  if (API_KEY) {
    url.searchParams.set('api_key', API_KEY)
  }

  const source = new EventSource(url.toString())

  source.addEventListener('step', (e: MessageEvent) => {
    try {
      callbacks.onEvent(JSON.parse(e.data) as T)
    } catch { /* ignore parse errors */ }
  })

  source.addEventListener('complete', (e: MessageEvent) => {
    try {
      callbacks.onEvent(JSON.parse(e.data) as T)
    } catch { /* ignore parse errors */ }
    callbacks.onComplete?.()
    source.close()
  })

  source.addEventListener('error', (e: MessageEvent) => {
    if (e.data) {
      try {
        const parsed = JSON.parse(e.data)
        callbacks.onError(parsed.message || 'Erreur de generation')
      } catch {
        callbacks.onError('Erreur de generation')
      }
    }
    source.close()
  })

  source.onerror = () => {
    if (source.readyState === EventSource.CLOSED) {
      callbacks.onError('Connexion au serveur perdue.')
    }
    source.close()
  }

  return () => source.close()
}

// ---------------------------------------------------------------------------
// Error mapping — messages user-friendly en francais
// ---------------------------------------------------------------------------

function mapErrorMessage(status: number, detail: string): string {
  switch (status) {
    case 401:
      return 'Cle API invalide ou manquante. Contactez votre administrateur.'
    case 403:
      return 'Vous n\'avez pas les permissions pour cette action.'
    case 404:
      return 'Ressource introuvable. Le workflow a peut-etre expire.'
    case 422:
      return `Donnees invalides : ${detail}`
    case 429:
      return 'Trop de requetes. Patientez quelques secondes.'
    case 503:
      return 'Service temporairement indisponible. Reessayez dans un instant.'
    default:
      if (status >= 500) return 'Erreur serveur. Notre equipe est notifiee.'
      return detail
  }
}
