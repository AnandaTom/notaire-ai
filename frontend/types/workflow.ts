// Types du moteur de workflow Notomai

export type WorkflowStep =
  | 'IDLE'
  | 'TYPE_SELECT'
  | 'COLLECTING'
  | 'VALIDATING'
  | 'REVIEW'
  | 'GENERATING'
  | 'DONE'

export type TypeActe =
  | 'promesse_vente'
  | 'vente'
  | 'reglement_copropriete'
  | 'modificatif_edd'

export type CategorieBien =
  | 'copropriete'
  | 'hors_copropriete'
  | 'terrain_a_batir'

export type SousType =
  | 'standard'
  | 'viager'
  | 'creation'
  | 'lotissement'
  | 'groupe_habitations'
  | 'avec_servitudes'

export type QuestionType =
  | 'texte'
  | 'nombre'
  | 'booleen'
  | 'choix'
  | 'date'
  | 'tableau'
  | 'contact'
  | 'texte_long'

export interface Question {
  id: string
  question: string
  type: QuestionType
  variable: string
  obligatoire: boolean
  options?: string[]
  placeholder?: string
  aide?: string
  condition_affichage?: string
  condition_categorie?: CategorieBien[]
  sous_questions?: Question[]
}

export interface Section {
  id: string
  titre: string
  description?: string
  questions: Question[]
}

export interface Detection {
  categorie_bien: CategorieBien
  type_promesse: string
  sous_type?: SousType
  confiance: number
  raison?: string
}

export interface Progression {
  sections_total: number
  sections_completes: number
  champs_remplis: number
  champs_total: number
  pourcentage: number
}

export interface ValidationMessage {
  niveau: 'erreur' | 'avertissement' | 'info'
  code: string
  message: string
  suggestion?: string
  chemin?: string
}

export interface GenerationEvent {
  etape: string
  statut: 'en_cours' | 'termine' | 'erreur'
  detail?: string
  fichier?: string
  conformite?: number
  duree_ms?: number
}

export type SectionStatus = 'todo' | 'current' | 'complete' | 'error'

export interface WorkflowState {
  // Etat
  step: WorkflowStep
  workflowId: string | null
  dossierId: string | null

  // Type d'acte
  typeActe: TypeActe | null
  detection: Detection | null

  // Sections et donnees
  sections: Section[]
  currentSectionIndex: number
  donnees: Record<string, unknown>

  // Progression
  progression: Progression

  // Validation
  validationMessages: ValidationMessage[]

  // Generation
  generationEvents: GenerationEvent[]
  fichierUrl: string | null
  conformiteScore: number | null

  // Erreur
  error: string | null
  isLoading: boolean
}
