import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type {
  WorkflowState,
  WorkflowStep,
  TypeActe,
  Section,
  Detection,
  ValidationMessage,
  GenerationEvent,
  Progression,
} from '@/types/workflow'
import * as api from '@/lib/api'

interface WorkflowActions {
  // Navigation
  setStep: (step: WorkflowStep) => void
  goToSection: (index: number) => void

  // Demarrage
  startWorkflow: (typeActe: TypeActe, etudeId?: string, options?: { categorie_bien?: Detection['categorie_bien']; sous_type?: Detection['sous_type'] }) => Promise<void>

  // Donnees
  updateField: (chemin: string, valeur: unknown) => void
  submitCurrentSection: () => Promise<void>

  // Validation
  validateField: (chemin: string, valeur: unknown) => Promise<ValidationMessage[]>

  // Generation
  startGeneration: () => void
  addGenerationEvent: (event: GenerationEvent) => void
  setGenerationResult: (url: string, score: number) => void

  // Brouillon
  restoreDraft: () => Promise<boolean>

  // Reset
  reset: () => void
  setError: (error: string | null) => void
}

const initialProgression: Progression = {
  sections_total: 0,
  sections_completes: 0,
  champs_remplis: 0,
  champs_total: 0,
  pourcentage: 0,
}

const initialState: WorkflowState = {
  step: 'IDLE',
  workflowId: null,
  dossierId: null,
  typeActe: null,
  detection: null,
  sections: [],
  currentSectionIndex: 0,
  donnees: {},
  progression: initialProgression,
  validationMessages: [],
  generationEvents: [],
  fichierUrl: null,
  conformiteScore: null,
  error: null,
  isLoading: false,
}

// Helper: met a jour une valeur nested via chemin dot-path
function setNestedValue(obj: Record<string, unknown>, path: string, value: unknown): Record<string, unknown> {
  const copy = { ...obj }
  const parts = path.split('.')
  let current: Record<string, unknown> = copy

  for (let i = 0; i < parts.length - 1; i++) {
    const key = parts[i]
    if (!current[key] || typeof current[key] !== 'object') {
      current[key] = {}
    }
    current[key] = { ...(current[key] as Record<string, unknown>) }
    current = current[key] as Record<string, unknown>
  }

  current[parts[parts.length - 1]] = value
  return copy
}

export const useWorkflowStore = create<WorkflowState & WorkflowActions>()(
  persist(
    (set, get) => ({
  ...initialState,

  setStep: (step) => set({ step }),

  goToSection: (index) => {
    const { sections } = get()
    if (index >= 0 && index < sections.length) {
      set({ currentSectionIndex: index })
    }
  },

  startWorkflow: async (typeActe, etudeId, options) => {
    set({ isLoading: true, error: null, typeActe })
    try {
      const result = await api.startWorkflow({
        type_acte: typeActe,
        categorie_bien: options?.categorie_bien,
        sous_type: options?.sous_type,
        etude_id: etudeId,
        source: 'workflow_frontend',
      })

      const sections: Section[] = (result.sections || []).map((s) => ({
        id: s.id,
        titre: s.titre,
        description: s.description,
        questions: s.questions as Section['questions'],
      }))

      set({
        workflowId: result.workflow_id,
        dossierId: result.dossier_id,
        detection: result.detection as Detection,
        sections,
        currentSectionIndex: 0,
        step: 'COLLECTING',
        progression: {
          ...initialProgression,
          sections_total: sections.length,
        },
        isLoading: false,
      })
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Erreur de demarrage',
        isLoading: false,
      })
    }
  },

  updateField: (chemin, valeur) => {
    const { donnees } = get()
    const updated = setNestedValue(donnees, chemin, valeur)

    // Recalcul progression locale
    const filledCount = Object.keys(flattenObj(updated)).length
    const { progression } = get()

    set({
      donnees: updated,
      progression: {
        ...progression,
        champs_remplis: filledCount,
        pourcentage: progression.champs_total > 0
          ? Math.round((filledCount / progression.champs_total) * 100)
          : 0,
      },
    })

    // Sauvegarde auto geree par zustand persist
  },

  submitCurrentSection: async () => {
    const { workflowId, sections, currentSectionIndex, donnees } = get()
    if (!workflowId || !sections[currentSectionIndex]) return

    set({ isLoading: true, error: null })

    try {
      const section = sections[currentSectionIndex]
      const result = await api.submitAnswers(workflowId, section.id, donnees)

      const nextIndex = currentSectionIndex + 1
      const isLastSection = nextIndex >= sections.length

      set({
        currentSectionIndex: isLastSection ? currentSectionIndex : nextIndex,
        step: isLastSection ? 'REVIEW' : 'COLLECTING',
        progression: {
          ...get().progression,
          sections_completes: result.progression.sections_completes,
          pourcentage: result.progression.pourcentage,
        },
        validationMessages: (result.validation.messages || []).map((m) => ({
          niveau: m.niveau as ValidationMessage['niveau'],
          code: '',
          message: m.message,
        })),
        isLoading: false,
      })
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Erreur de soumission',
        isLoading: false,
      })
    }
  },

  validateField: async (chemin, valeur) => {
    const { typeActe } = get()
    if (!typeActe) return []

    try {
      const result = await api.validateField({
        type_acte: typeActe,
        chemin,
        valeur,
      })
      return result.messages.map((m) => ({
        niveau: m.niveau as ValidationMessage['niveau'],
        code: m.code,
        message: m.message,
        suggestion: m.suggestion,
        chemin,
      }))
    } catch {
      return []
    }
  },

  startGeneration: () => {
    const { workflowId } = get()
    if (!workflowId) return

    set({ step: 'GENERATING', generationEvents: [], isLoading: true })

    const cleanup = api.streamGeneration(
      workflowId,
      (event) => {
        const genEvent: GenerationEvent = {
          etape: event.etape,
          statut: event.statut as GenerationEvent['statut'],
          detail: event.detail,
          fichier: event.fichier,
          conformite: event.conformite,
        }

        set((state) => ({
          generationEvents: [...state.generationEvents, genEvent],
        }))

        if (event.fichier && event.conformite) {
          set({
            fichierUrl: event.fichier,
            conformiteScore: event.conformite,
            step: 'DONE',
            isLoading: false,
          })
        }
      },
      (error) => {
        set({ error, isLoading: false })
      }
    )

    // Stocker cleanup pour fermer le SSE si besoin
    return cleanup
  },

  addGenerationEvent: (event) => {
    set((state) => ({
      generationEvents: [...state.generationEvents, event],
    }))
  },

  setGenerationResult: (url, score) => {
    set({
      fichierUrl: url,
      conformiteScore: score,
      step: 'DONE',
      isLoading: false,
    })
  },

  // Restaurer un brouillon — zustand persist restaure l'etat auto,
  // mais restoreDraft re-fetch les sections depuis l'API si besoin
  restoreDraft: async () => {
    const { workflowId, typeActe, donnees, currentSectionIndex, sections } = get()
    if (!workflowId || !typeActe) return false
    // Si sections deja presentes (persist les a restaurees), rien a faire
    if (sections.length > 0) return true

    set({ isLoading: true, error: null })
    try {
      const result = await api.startWorkflow({
        type_acte: typeActe,
        source: 'workflow_restore',
      })
      const newSections: Section[] = (result.sections || []).map((s) => ({
        id: s.id,
        titre: s.titre,
        description: s.description,
        questions: s.questions as Section['questions'],
      }))
      const safeIndex = Math.min(currentSectionIndex, Math.max(newSections.length - 1, 0))
      set({
        workflowId: result.workflow_id,
        dossierId: result.dossier_id,
        detection: result.detection as Detection,
        sections: newSections,
        currentSectionIndex: safeIndex,
        donnees,
        step: 'COLLECTING',
        progression: {
          ...initialProgression,
          sections_total: newSections.length,
          champs_remplis: Object.keys(flattenObj(donnees)).length,
        },
        isLoading: false,
      })
      return true
    } catch {
      set({ isLoading: false, error: null })
      return false
    }
  },

  reset: () => {
    set(initialState)
    // Clear persisted state on explicit reset
    try { localStorage.removeItem('notomai-workflow') } catch {}
  },

  setError: (error) => set({ error }),
}),
    {
      name: 'notomai-workflow',
      partialize: (state) => ({
        step: state.step,
        workflowId: state.workflowId,
        dossierId: state.dossierId,
        typeActe: state.typeActe,
        detection: state.detection,
        sections: state.sections,
        currentSectionIndex: state.currentSectionIndex,
        donnees: state.donnees,
        progression: state.progression,
        fichierUrl: state.fichierUrl,
        conformiteScore: state.conformiteScore,
      }),
    },
  ),
)

// Helper: aplatir un objet nested
function flattenObj(obj: Record<string, unknown>, prefix = ''): Record<string, unknown> {
  const result: Record<string, unknown> = {}
  for (const key in obj) {
    const fullKey = prefix ? `${prefix}.${key}` : key
    const val = obj[key]
    if (val && typeof val === 'object' && !Array.isArray(val)) {
      Object.assign(result, flattenObj(val as Record<string, unknown>, fullKey))
    } else if (val !== undefined && val !== null && val !== '') {
      result[fullKey] = val
    }
  }
  return result
}
