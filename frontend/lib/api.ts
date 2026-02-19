// Client API Modal/FastAPI pour le workflow Notomai

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://notomai--notaire-ai-fastapi-app.modal.run'

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `Erreur ${res.status}` }))
    throw new Error(err.detail || `Erreur ${res.status}`)
  }
  return res.json()
}

// Demarrer un workflow
export async function startWorkflow(params: {
  etude_id?: string
  type_acte: string
  source?: string
  donnees_initiales?: Record<string, unknown>
}) {
  return fetchAPI<{
    workflow_id: string
    dossier_id: string
    detection: { categorie_bien: string; type_promesse: string; sous_type?: string; confiance: number }
    sections: { id: string; titre: string; description?: string; questions: unknown[] }[]
  }>('/workflow/promesse/start', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// Soumettre les reponses d'une section
export async function submitAnswers(workflowId: string, section: string, reponses: Record<string, unknown>) {
  return fetchAPI<{
    next_section?: string
    progression: { pourcentage: number; sections_completes: number; sections_total: number }
    validation: { valide: boolean; messages: { niveau: string; message: string }[] }
  }>(`/workflow/promesse/${workflowId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ section, reponses }),
  })
}

// Valider un champ en temps reel
export async function validateField(params: {
  type_acte: string
  chemin: string
  valeur: unknown
  contexte?: Record<string, unknown>
}) {
  return fetchAPI<{
    valide: boolean
    messages: { niveau: string; code: string; message: string; suggestion?: string }[]
  }>('/validation/champ', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

// Recuperer les questions
export async function getQuestions(params?: {
  section?: string
  categorie?: string
  sous_type?: string
}) {
  const query = new URLSearchParams()
  if (params?.section) query.set('section', params.section)
  if (params?.categorie) query.set('categorie', params.categorie)
  if (params?.sous_type) query.set('sous_type', params.sous_type)
  const qs = query.toString()
  return fetchAPI<{
    sections: { id: string; titre: string; description?: string; questions: unknown[] }[]
  }>(`/questions/promesse${qs ? `?${qs}` : ''}`)
}

// Statut du workflow
export async function getWorkflowStatus(workflowId: string) {
  return fetchAPI<{
    step: string
    progression: { pourcentage: number }
    donnees: Record<string, unknown>
  }>(`/workflow/promesse/${workflowId}/status`)
}

// Generer le document
export async function generateDocument(workflowId: string) {
  return fetchAPI<{
    fichier_url: string
    conformite: number
  }>(`/workflow/promesse/${workflowId}/generate`, {
    method: 'POST',
  })
}

// Stream SSE de generation
export function streamGeneration(
  workflowId: string,
  onEvent: (event: { etape: string; statut: string; detail?: string; fichier?: string; conformite?: number }) => void,
  onError: (error: string) => void
): () => void {
  const eventSource = new EventSource(`${API_URL}/workflow/promesse/${workflowId}/generate-stream`)

  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data)
      onEvent(data)
      if (data.etape === 'done' || data.statut === 'erreur') {
        eventSource.close()
      }
    } catch {
      // ignore parse errors
    }
  }

  eventSource.onerror = () => {
    onError('Connexion perdue avec le serveur')
    eventSource.close()
  }

  return () => eventSource.close()
}

// Envoyer un feedback
export async function sendFeedback(params: {
  workflow_id?: string
  section: string
  type: 'erreur' | 'suggestion' | 'question'
  contenu: string
}) {
  return fetchAPI<{ ok: boolean }>('/api/feedback', {
    method: 'POST',
    body: JSON.stringify(params),
  })
}
