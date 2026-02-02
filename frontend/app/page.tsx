'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import ChatArea from '@/components/ChatArea'
import Header from '@/components/Header'
import ParagraphReview from '@/components/ParagraphReview'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://notaire-ai--fastapi-app.modal.run'
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || ''

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
}

interface DocumentSection {
  id: string
  index: number
  title: string
  content: string
  heading_level: number
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: `Bonjour,

Je suis votre assistant pour la rédaction d'actes notariaux. Je vous accompagne dans la création d'actes de vente et de promesses de vente conformes aux dispositions légales en vigueur.

Comment puis-je vous assister aujourd'hui ?`,
      timestamp: new Date(),
    },
  ])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'docx'>('docx')
  const [conversationId] = useState(() => crypto.randomUUID())

  // Review state
  const [reviewSections, setReviewSections] = useState<DocumentSection[] | null>(null)
  const [reviewWorkflowId, setReviewWorkflowId] = useState<string | null>(null)

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
          history: messages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
          context: {
            format: selectedFormat,
          },
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || `Erreur ${response.status}`)
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.content,
        timestamp: new Date(),
        section: data.section,
        suggestions: data.suggestions,
        metadata: {
          fichier_url: data.fichier_url,
          workflow_id: data.workflow_id,
          intention: data.intention,
          confiance: data.confiance,
          ...(data.contexte_mis_a_jour || {}),
        },
      }

      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Erreur:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: error instanceof Error
          ? `Erreur de communication avec le serveur : ${error.message}`
          : 'Désolé, une erreur est survenue. Veuillez réessayer.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleReviewRequest = async (workflowId: string) => {
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' }
      if (API_KEY) headers['X-API-Key'] = API_KEY

      const response = await fetch(`${API_URL}/document/${workflowId}/sections`, {
        headers,
      })

      if (!response.ok) throw new Error('Document non trouve')

      const data = await response.json()
      setReviewSections(data.sections)
      setReviewWorkflowId(workflowId)
    } catch (error) {
      console.error('Review error:', error)
    }
  }

  const handleReviewComplete = () => {
    setReviewSections(null)
    setReviewWorkflowId(null)
    sendMessage('La relecture du document est terminee. Merci.')
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-5">
      <div className="w-full max-w-[1100px] h-[92vh] max-h-[850px] bg-ivory rounded-[20px] shadow-lg grid grid-cols-[280px_1fr] overflow-hidden border border-gold/10">
        <Sidebar />
        <main className="flex flex-col bg-ivory">
          <Header />
          <ChatArea
            messages={messages}
            isLoading={isLoading}
            onSendMessage={sendMessage}
            selectedFormat={selectedFormat}
            onFormatChange={setSelectedFormat}
            onReviewRequest={handleReviewRequest}
          />
        </main>
      </div>

      {/* Paragraph Review Modal */}
      {reviewSections && reviewWorkflowId && (
        <ParagraphReview
          workflowId={reviewWorkflowId}
          sections={reviewSections}
          onComplete={handleReviewComplete}
          onClose={() => { setReviewSections(null); setReviewWorkflowId(null) }}
          apiUrl={API_URL}
          apiKey={API_KEY}
        />
      )}
    </div>
  )
}
