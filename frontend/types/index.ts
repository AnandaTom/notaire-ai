// Types partagés pour l'application Notomai

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  section?: string
  suggestions?: string[]
  metadata?: {
    fichier_url?: string
    workflow_id?: string
    intention?: string
    confiance?: number
    [key: string]: unknown
  }
  feedbackRating?: number
}

export interface ConversationSummary {
  id: string
  title: string
  type_acte?: string
  message_count: number
  progress_pct?: number
  created_at: string
  updated_at: string
}

export interface DocumentSection {
  id: string
  index: number
  title: string
  content: string
  heading_level: number
}

export interface User {
  id: string
  email: string
  etude_id?: string
  role?: 'notaire' | 'clerc' | 'admin'
}

// Types pour la gestion des dossiers
export interface Partie {
  nom: string
  prenom?: string
  type: 'physique' | 'morale'
  role: 'vendeur' | 'acquereur' | 'promettant' | 'beneficiaire'
}

export interface Dossier {
  id: string
  numero: string
  type_acte: 'vente' | 'promesse_vente' | 'reglement_copropriete' | 'modificatif_edd' | 'autre'
  statut: 'brouillon' | 'en_cours' | 'termine' | 'archive'
  parties: Partie[]
  biens?: {
    adresse?: string
    ville?: string
    type?: string
  }[]
  prix_vente?: number
  date_signature_prevue?: string
  progress_pct?: number
  created_at: string
  updated_at: string
}

// Types pour la gestion des clients
export interface Client {
  id: string
  type_personne: 'physique' | 'morale'
  civilite?: string
  nom: string
  prenom?: string
  email?: string
  telephone?: string
  adresse?: string
  ville?: string
  code_postal?: string
  date_naissance?: string
  lieu_naissance?: string
  nationalite?: string
  profession?: string
  situation_matrimoniale?: string
  // Pour les personnes morales
  raison_sociale?: string
  siret?: string
  representant?: string
  // Metadata
  dossiers_count?: number
  created_at: string
  updated_at: string
}
