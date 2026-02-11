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
