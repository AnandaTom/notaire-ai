/**
 * Constantes partagees par les composants frontend.
 */

import type { TypeActe, CategorieBien, SousType, WorkflowStep, SectionStatus } from '@/types/workflow'

// ---------------------------------------------------------------------------
// Labels affichage
// ---------------------------------------------------------------------------

export const TYPE_ACTE_LABELS: Record<TypeActe, { label: string; short: string }> = {
  promesse_vente: { label: 'Promesse de vente', short: 'Promesse' },
  vente: { label: 'Acte de vente', short: 'Vente' },
  reglement_copropriete: { label: 'Reglement de copropriete', short: 'Reglement' },
  modificatif_edd: { label: 'Modificatif EDD', short: 'Modificatif' },
}

export const CATEGORIE_LABELS: Record<CategorieBien, string> = {
  copropriete: 'Copropriete',
  hors_copropriete: 'Hors copropriete',
  terrain_a_batir: 'Terrain a batir',
}

export const SOUS_TYPE_LABELS: Record<SousType, string> = {
  standard: 'Standard',
  viager: 'Viager',
  creation: 'Creation copropriete',
  lotissement: 'Lotissement',
  groupe_habitations: 'Groupe d\'habitations',
  avec_servitudes: 'Avec servitudes',
}

export const STEP_LABELS: Record<WorkflowStep, string> = {
  IDLE: '',
  TYPE_SELECT: 'Selection du type',
  COLLECTING: 'Collecte des informations',
  VALIDATING: 'Validation',
  REVIEW: 'Verification',
  GENERATING: 'Generation',
  DONE: 'Termine',
}

// ---------------------------------------------------------------------------
// Couleurs par statut de section (WorkflowSidebar)
// ---------------------------------------------------------------------------

export const SECTION_STATUS_COLORS: Record<SectionStatus, { bg: string; text: string; border: string }> = {
  todo: { bg: 'bg-sand', text: 'text-slate', border: 'border-champagne' },
  current: { bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-300' },
  complete: { bg: 'bg-emerald-100', text: 'text-emerald-600', border: 'border-emerald-300' },
  error: { bg: 'bg-red-100', text: 'text-red-600', border: 'border-red-300' },
}

// ---------------------------------------------------------------------------
// Etapes de generation (GenerationProgress)
// ---------------------------------------------------------------------------

export const GENERATION_STEPS = [
  { id: 'validation', label: 'Validation des donnees' },
  { id: 'detection', label: 'Detection du type de bien' },
  { id: 'assembly', label: 'Assemblage du document' },
  { id: 'export', label: 'Export DOCX' },
] as const
