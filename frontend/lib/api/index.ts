/**
 * API workflow Notomai — point d'entree principal.
 *
 * Importe par :
 *   - frontend/stores/workflowStore.ts  → import * as api from '@/lib/api'
 *   - frontend/components/workflow/FeedbackPanel.tsx  → import * as api from '@/lib/api'
 *
 * Consomme les endpoints backend (api/main.py) :
 *   POST /workflow/promesse/start            (ligne 1884)
 *   POST /workflow/promesse/{id}/submit      (ligne 1968)
 *   GET  /workflow/promesse/{id}/generate-stream (ligne 2134, SSE)
 *   POST /feedback/paragraphe                (ligne 2582)
 *
 * Note : la validation champ-par-champ est faite localement (pas d'endpoint backend).
 */

import { apiFetch, apiSSE } from './client'
import type {
  TypeActe,
  CategorieBien,
  SousType,
  Section,
  Detection,
  Progression,
  ValidationMessage,
} from '@/types/workflow'
import { WORKFLOW_SUPPORTED_TYPES } from '@/lib/config'

// ---------------------------------------------------------------------------
// Response types (mapping backend → frontend)
// ---------------------------------------------------------------------------

export interface StartWorkflowResponse {
  workflow_id: string
  dossier_id: string | null
  detection: Detection | null
  sections: Section[]
}

export interface SubmitAnswersResponse {
  progression: Pick<Progression, 'sections_completes' | 'pourcentage'>
  validation: { messages: { niveau: string; message: string }[] }
}

interface ValidateFieldResponse {
  messages: {
    niveau: string
    code: string
    message: string
    suggestion?: string
  }[]
}

interface SSEStepEvent {
  step?: string
  etape?: string
  statut?: string
  message?: string
  detail?: string
  fichier?: string
  fichier_url?: string
  conformite?: number
}

// ---------------------------------------------------------------------------
// 1. startWorkflow
// ---------------------------------------------------------------------------

/**
 * Demarre un workflow de generation guide.
 *
 * Mapping :
 *   Store envoie  { type_acte, categorie_bien?, sous_type?, etude_id, source }
 *   Backend attend { categorie_bien, sous_type?, titre_id?, prefill? }
 *
 * categorie_bien est passe tel quel au backend (defaut 'copropriete').
 * Les autres types d'acte ne sont pas encore supportes en mode workflow.
 */
export async function startWorkflow(request: {
  type_acte: TypeActe
  categorie_bien?: CategorieBien
  sous_type?: SousType
  titre_id?: string
  prefill?: Record<string, unknown>
  etude_id?: string
  source?: string
}): Promise<StartWorkflowResponse> {
  // Seules les promesses ont un workflow backend pour l'instant
  if (!WORKFLOW_SUPPORTED_TYPES.includes(request.type_acte as typeof WORKFLOW_SUPPORTED_TYPES[number])) {
    throw new Error(
      `Le workflow guide n'est pas encore disponible pour "${request.type_acte}". ` +
      `Utilisez le chat pour ce type d'acte.`,
    )
  }

  const raw = await apiFetch<Record<string, unknown>>(
    '/workflow/promesse/start',
    {
      method: 'POST',
      body: JSON.stringify({
        categorie_bien: request.categorie_bien || 'copropriete',
        sous_type: request.sous_type || null,
        titre_id: request.titre_id || null,
        prefill: request.prefill || null,
      }),
    },
  )

  // Adapter la reponse backend au format attendu par le store
  const rawSections = (raw.sections || []) as {
    key: string
    title: string
    description?: string
    questions?: unknown[]
    complete?: boolean
  }[]

  const sections: Section[] = rawSections.map((s) => ({
    id: s.key,
    titre: s.title,
    description: s.description,
    questions: (s.questions || []) as Section['questions'],
  }))

  return {
    workflow_id: raw.workflow_id as string,
    dossier_id: (raw.dossier_id as string) || null,
    detection: raw.categorie_bien
      ? {
          categorie_bien: raw.categorie_bien as Detection['categorie_bien'],
          type_promesse: (raw.type_promesse as string) || 'standard',
          sous_type: raw.sous_type as Detection['sous_type'],
          confiance: (raw.confiance as number) || 80,
        }
      : null,
    sections,
  }
}

// ---------------------------------------------------------------------------
// 2. submitAnswers
// ---------------------------------------------------------------------------

/**
 * Soumet les reponses de la section courante.
 *
 * Mapping :
 *   Store envoie  (workflowId, sectionId, donnees)
 *   Backend attend { answers: Dict }
 *
 * Le sectionId n'est pas utilise par le backend (il track sa propre progression).
 */
export async function submitAnswers(
  workflowId: string,
  _sectionId: string,
  donnees: Record<string, unknown>,
): Promise<SubmitAnswersResponse> {
  const raw = await apiFetch<Record<string, unknown>>(
    `/workflow/promesse/${encodeURIComponent(workflowId)}/submit`,
    {
      method: 'POST',
      body: JSON.stringify({ answers: donnees }),
    },
  )

  const progress = (raw.progress || {}) as Record<string, unknown>
  const validation = (raw.validation || {}) as Record<string, unknown>
  const messages = (validation.messages || validation.avertissements || []) as {
    niveau: string
    message: string
  }[]

  return {
    progression: {
      sections_completes: (progress.sections_completes as number) || 0,
      pourcentage: (progress.pourcentage as number) || 0,
    },
    validation: { messages },
  }
}

// ---------------------------------------------------------------------------
// 3. validateField — validation locale, pas d'appel reseau
// ---------------------------------------------------------------------------

const REQUIRED_PATTERNS: Record<string, RegExp> = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  telephone: /^[\d\s+().-]{6,20}$/,
  code_postal: /^\d{5}$/,
}

/**
 * Valide un champ individuellement. Regles appliquees localement :
 * - Champ obligatoire vide
 * - Format email, telephone, code postal
 * - Prix > 0
 *
 * Pas de requete reseau — instantane pour le notaire.
 */
export async function validateField(request: {
  type_acte: TypeActe
  chemin: string
  valeur: unknown
}): Promise<ValidateFieldResponse> {
  const messages: ValidateFieldResponse['messages'] = []
  const { chemin, valeur } = request

  // Valeur vide
  if (valeur === null || valeur === undefined || valeur === '') {
    messages.push({
      niveau: 'avertissement',
      code: 'CHAMP_VIDE',
      message: 'Ce champ est recommande pour la generation.',
    })
    return { messages }
  }

  // Prix coherent
  if (chemin.includes('prix') && chemin.includes('montant')) {
    const num = Number(valeur)
    if (isNaN(num) || num <= 0) {
      messages.push({
        niveau: 'erreur',
        code: 'PRIX_INVALIDE',
        message: 'Le montant doit etre un nombre positif.',
      })
    }
  }

  // Patterns specifiques
  const fieldName = chemin.split('.').pop() || ''
  const pattern = REQUIRED_PATTERNS[fieldName]
  if (pattern && typeof valeur === 'string' && !pattern.test(valeur)) {
    messages.push({
      niveau: 'avertissement',
      code: 'FORMAT_INVALIDE',
      message: `Le format de "${fieldName}" semble incorrect.`,
      suggestion: fieldName === 'email' ? 'Ex: notaire@etude.fr' : undefined,
    })
  }

  return { messages }
}

// ---------------------------------------------------------------------------
// 4. streamGeneration — SSE
// ---------------------------------------------------------------------------

/**
 * Demarre la generation du document via Server-Sent Events.
 * Le backend envoie des events : step, complete, error.
 *
 * Retourne une fonction cleanup pour fermer la connexion.
 */
export function streamGeneration(
  workflowId: string,
  onEvent: (event: {
    etape: string
    statut: string
    detail?: string
    fichier?: string
    conformite?: number
  }) => void,
  onError: (error: string) => void,
): () => void {
  const path = `/workflow/promesse/${encodeURIComponent(workflowId)}/generate-stream`

  return apiSSE<SSEStepEvent>(path, {
    onEvent: (raw) => {
      // Les events "step" arrivent pendant la generation
      if (raw.step || raw.etape) {
        onEvent({
          etape: raw.step || raw.etape || '',
          statut: 'en_cours',
          detail: raw.message || raw.detail,
        })
      }

      // L'event "complete" contient le lien fichier
      if (raw.fichier_url || raw.fichier) {
        onEvent({
          etape: 'export',
          statut: 'termine',
          fichier: raw.fichier_url || raw.fichier,
          conformite: raw.conformite,
        })
      }
    },
    onError,
  })
}

// ---------------------------------------------------------------------------
// 5. sendFeedback
// ---------------------------------------------------------------------------

/**
 * Envoie un feedback du notaire (erreur, suggestion, question).
 *
 * Reutilise POST /feedback/paragraphe (api/main.py:2582) qui insere
 * dans feedbacks_promesse via Supabase.
 */
export async function sendFeedback(request: {
  workflow_id?: string
  section: string
  type: 'erreur' | 'suggestion' | 'question'
  contenu: string
}): Promise<void> {
  await apiFetch<unknown>('/feedback/paragraphe', {
    method: 'POST',
    body: JSON.stringify({
      workflow_id: request.workflow_id || 'general',
      section_id: request.section,
      section_title: '',
      action: request.type === 'erreur' ? 'corriger' : 'commenter',
      contenu: request.contenu,
      raison: request.type,
    }),
  })
}

// ---------------------------------------------------------------------------
// Re-export promesse-specific API (detection, questions filtrees, validation)
// ---------------------------------------------------------------------------
export { detecterType, getQuestions, validerPromesse } from './promesse'
