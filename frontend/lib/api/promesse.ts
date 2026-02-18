/**
 * API client pour les promesses de vente — detection, questions, validation.
 *
 * Consomme :
 *   POST /promesses/detecter-type   (api/main.py:1462)
 *   GET  /questions/promesse         (api/main.py:1641)
 *   POST /promesses/valider          (api/main.py:1499)
 */

import { apiFetch } from './client'
import type { CategorieBien, SousType } from '@/types/workflow'

// ---------------------------------------------------------------------------
// Types exportes (utilises par ViagerBadge, useViagerDetection)
// ---------------------------------------------------------------------------

export interface DetectionResult {
  categorie_bien: CategorieBien
  type_promesse: string
  sous_type?: SousType
  confiance: number
  marqueurs_detectes: string[]
  avertissement?: string
}

export interface QuestionItem {
  id: string
  question: string
  type: string
  variable: string
  obligatoire: boolean
  options?: string[]
  placeholder?: string
  aide?: string
  condition_affichage?: string
}

export interface Section {
  id: string
  titre: string
  description?: string
  questions: QuestionItem[]
}

export interface ValidationResult {
  valide: boolean
  erreurs: string[]
  avertissements: string[]
  champs_manquants: string[]
}

// ---------------------------------------------------------------------------
// API functions
// ---------------------------------------------------------------------------

/**
 * Detecte la categorie de bien et le sous-type (viager, lotissement, etc.)
 * a partir des donnees partielles saisies.
 *
 * Backend : POST /promesses/detecter-type
 */
export async function detecterType(
  donnees: Record<string, unknown>,
): Promise<DetectionResult> {
  const raw = await apiFetch<Record<string, unknown>>('/promesses/detecter-type', {
    method: 'POST',
    body: JSON.stringify({ donnees }),
  })

  return {
    categorie_bien: (raw.categorie_bien as CategorieBien) || 'copropriete',
    type_promesse: (raw.type_promesse as string) || 'standard',
    sous_type: raw.sous_type as SousType | undefined,
    confiance: (raw.confiance as number) || 0,
    marqueurs_detectes: (raw.marqueurs_detectes as string[]) || [],
    avertissement: raw.avertissement as string | undefined,
  }
}

/**
 * Recupere les questions filtrees par categorie, sous-type et section.
 *
 * Backend : GET /questions/promesse?categorie=X&sous_type=Y&section=Z
 */
export async function getQuestions(
  categorie: string,
  sousType?: string,
  section?: string,
): Promise<{ sections: Section[] }> {
  const params = new URLSearchParams({ categorie })
  if (sousType) params.set('sous_type', sousType)
  if (section) params.set('section', section)

  return apiFetch<{ sections: Section[] }>(
    `/questions/promesse?${params.toString()}`,
  )
}

/**
 * Valide les donnees d'une promesse (regles metier : bouquet viager, etc.)
 *
 * Backend : POST /promesses/valider
 */
export async function validerPromesse(
  donnees: Record<string, unknown>,
): Promise<ValidationResult> {
  return apiFetch<ValidationResult>('/promesses/valider', {
    method: 'POST',
    body: JSON.stringify({ donnees }),
  })
}
