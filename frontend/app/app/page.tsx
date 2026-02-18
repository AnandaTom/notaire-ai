'use client'

import { useState, useEffect, useCallback } from 'react'
import Sidebar from '@/components/Sidebar'
import ChatArea from '@/components/ChatArea'
import Header from '@/components/Header'
import ParagraphReview from '@/components/ParagraphReview'
import type { Message, ConversationSummary, DocumentSection } from '@/types'
import { supabase } from '@/lib/supabase'
import { API_URL, API_KEY } from '@/lib/config'

function getOrCreateUserId(): string {
  if (typeof window === 'undefined') return ''
  let userId = localStorage.getItem('notaire_user_id')
  if (!userId) {
    userId = crypto.randomUUID()
    localStorage.setItem('notaire_user_id', userId)
  }
  return userId
}

const WELCOME_MESSAGE: Message = {
  id: '1',
  role: 'assistant',
  content: `Bonjour,

Je suis votre assistant pour la rédaction d'actes notariaux. Je vous accompagne dans la création d'actes de vente et de promesses de vente conformes aux dispositions légales en vigueur.

Comment puis-je vous assister aujourd'hui ?`,
  timestamp: new Date(),
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'docx'>('docx')
  const [conversationId, setConversationId] = useState('')
  const [userId, setUserId] = useState('')
  const [progressPct, setProgressPct] = useState<number | null>(null)
  const [conversations, setConversations] = useState<ConversationSummary[]>([])
  const [statusText, setStatusText] = useState<string | null>(null)

  // Review state (Tom)
  const [reviewSections, setReviewSections] = useState<DocumentSection[] | null>(null)
  const [reviewWorkflowId, setReviewWorkflowId] = useState<string | null>(null)

  // User info state
  const [userInfo, setUserInfo] = useState<{ nom: string; prenom: string } | null>(null)

  // Init: load userId + conversationId from localStorage + user info
  useEffect(() => {
    const uid = getOrCreateUserId()
    setUserId(uid)

    const savedConvId = localStorage.getItem('notaire_active_conversation')
    if (savedConvId) {
      setConversationId(savedConvId)
      loadConversation(savedConvId)
    } else {
      const newId = crypto.randomUUID()
      setConversationId(newId)
      localStorage.setItem('notaire_active_conversation', newId)
    }

    loadConversations()

    // Charger les infos utilisateur depuis Supabase
    const loadUserInfo = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) {
        const { data } = await supabase
          .from('notaire_users')
          .select('nom, prenom')
          .eq('auth_user_id', user.id)
          .single()
        if (data) {
          setUserInfo(data)
        }
      }
    }
    loadUserInfo()
  }, [])

  const loadConversations = useCallback(async () => {
    try {
      const resp = await fetch(`${API_URL}/chat/conversations`)
      if (resp.ok) {
        const data = await resp.json()
        setConversations(data.conversations || [])
      }
    } catch {
      // silently fail
    }
  }, [])

  const loadConversation = async (convId: string) => {
    try {
      const resp = await fetch(`${API_URL}/chat/conversations/${convId}`)
      if (resp.ok) {
        const data = await resp.json()
        if (data.messages && data.messages.length > 0) {
          const restored: Message[] = [WELCOME_MESSAGE]
          data.messages.forEach((m: { role: string; content: string; suggestions?: string[] }, idx: number) => {
            restored.push({
              id: `restored-${idx}`,
              role: m.role as 'user' | 'assistant',
              content: m.content,
              timestamp: new Date(),
              suggestions: m.suggestions,
            })
          })
          setMessages(restored)
        }
        if (data.context?.progress_pct) {
          setProgressPct(data.context.progress_pct)
        }
      }
    } catch {
      // Conversation not found - start fresh
    }
  }

  const selectConversation = (convId: string) => {
    setConversationId(convId)
    localStorage.setItem('notaire_active_conversation', convId)
    setMessages([WELCOME_MESSAGE])
    setProgressPct(null)
    loadConversation(convId)
  }

  const startNewConversation = () => {
    const newId = crypto.randomUUID()
    setConversationId(newId)
    localStorage.setItem('notaire_active_conversation', newId)
    setMessages([WELCOME_MESSAGE])
    setProgressPct(null)
  }

  // ================================================================
  // Envoi de message avec SSE streaming (Paul)
  // ================================================================

  const sendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    }

    const assistantId = (Date.now() + 1).toString()

    setMessages((prev) => [...prev, userMessage])
    setIsLoading(true)
    setStatusText(null)

    try {
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: content,
          user_id: userId,
          etude_id: '',
          conversation_id: conversationId,
          context: { format: selectedFormat },
        }),
      })

      if (!response.ok || !response.body) {
        // Fallback au endpoint non-streaming
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || `Erreur ${response.status}`)
      }

      // Ajouter le message assistant vide (placeholder pour streaming)
      setMessages((prev) => [
        ...prev,
        { id: assistantId, role: 'assistant', content: '', timestamp: new Date() },
      ])

      // Lire le stream SSE
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let sseBuffer = ''
      let eventType = ''
      let eventData = ''

      // Fonction locale pour traiter un event SSE complet
      const handleSSEEvent = (type: string, data: string) => {
        try {
          if (type === 'token' && data) {
            const { text } = JSON.parse(data)
            setStatusText(null)
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: m.content + text } : m
              )
            )
          } else if (type === 'status' && data) {
            const { message } = JSON.parse(data)
            setStatusText(message)
          } else if (type === 'done' && data) {
            const meta = JSON.parse(data)
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? {
                      ...m,
                      suggestions: meta.suggestions,
                      section: meta.section,
                      metadata: {
                        fichier_url: meta.fichier_url,
                        workflow_id: meta.workflow_id,
                        intention: meta.intention,
                        confiance: meta.confiance,
                      },
                    }
                  : m
              )
            )
            if (meta.progress_pct) setProgressPct(meta.progress_pct)
          } else if (type === 'error' && data) {
            const { message } = JSON.parse(data)
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId
                  ? { ...m, content: `Erreur : ${message}` }
                  : m
              )
            )
          }
        } catch {
          // Ignore parse errors on individual events
        }
      }

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        sseBuffer += decoder.decode(value, { stream: true })
        // Normaliser \r\n -> \n (le protocole SSE utilise \r\n)
        const normalized = sseBuffer.replace(/\r\n/g, '\n').replace(/\r/g, '\n')
        const lines = normalized.split('\n')
        sseBuffer = lines.pop()!

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim()
          } else if (line.startsWith('data: ')) {
            eventData = line.slice(6)
          } else if (line === '' && eventType) {
            handleSSEEvent(eventType, eventData)
            eventType = ''
            eventData = ''
          }
        }
      }

      // Traiter le dernier event si le stream se ferme sans ligne vide finale
      if (eventType && eventData) {
        handleSSEEvent(eventType, eventData)
      }

      setStatusText(null)
      loadConversations()
    } catch (error) {
      console.error('Erreur streaming:', error)
      // Si le message assistant placeholder existe avec contenu vide, le remplir
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        if (last && last.id === assistantId && last.content === '') {
          return prev.map((m) =>
            m.id === assistantId
              ? {
                  ...m,
                  content:
                    error instanceof Error
                      ? `Erreur de communication : ${error.message}`
                      : 'Une erreur est survenue. Veuillez réessayer.',
                }
              : m
          )
        }
        // Sinon ajouter un nouveau message d'erreur
        return [
          ...prev,
          {
            id: assistantId,
            role: 'assistant' as const,
            content:
              error instanceof Error
                ? `Erreur de communication : ${error.message}`
                : 'Une erreur est survenue. Veuillez réessayer.',
            timestamp: new Date(),
          },
        ]
      })
    } finally {
      setIsLoading(false)
      setStatusText(null)
    }
  }

  // ================================================================
  // Feedback thumbs up/down (Paul)
  // ================================================================

  const sendFeedback = async (messageIndex: number, rating: number) => {
    // Optimistic update
    setMessages((prev) =>
      prev.map((m, idx) =>
        idx === messageIndex ? { ...m, feedbackRating: rating } : m
      )
    )

    try {
      await fetch(`${API_URL}/chat/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          conversation_id: conversationId,
          message_index: messageIndex,
          rating,
        }),
      })
    } catch {
      // silently fail
    }
  }

  // ================================================================
  // Review section par section (Tom)
  // ================================================================

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
    <div className="h-screen w-screen overflow-hidden">
      <div className="w-full h-full bg-ivory grid grid-cols-[280px_1fr] overflow-hidden">
        <Sidebar
          conversations={conversations}
          activeConversationId={conversationId}
          onSelectConversation={selectConversation}
          onNewConversation={startNewConversation}
          userInfo={userInfo}
        />
        <main className="flex flex-col bg-ivory min-h-0 overflow-hidden">
          <Header progressPct={progressPct} />
          <ChatArea
            messages={messages}
            isLoading={isLoading}
            onSendMessage={sendMessage}
            selectedFormat={selectedFormat}
            onFormatChange={setSelectedFormat}
            onReviewRequest={handleReviewRequest}
            onFeedback={sendFeedback}
            statusText={statusText}
          />
        </main>
      </div>

      {/* Paragraph Review Modal (Tom) */}
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
