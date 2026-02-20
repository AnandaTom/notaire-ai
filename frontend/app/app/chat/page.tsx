'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
import ChatArea from '@/components/ChatArea'
import ParagraphReview from '@/components/ParagraphReview'
import type { Message, DocumentSection } from '@/types'
import { API_URL, API_KEY } from '@/lib/config'
import { useAppData } from '@/lib/hooks/useAppData'
import { useUIStore } from '@/stores/uiStore'
import {
  sendChatFeedback,
  loadDocumentSections,
} from '@/lib/api'

const WELCOME_MESSAGE: Message = {
  id: '1',
  role: 'assistant',
  content: `Bonjour,

Je suis votre assistant pour la rédaction d'actes notariaux. Je vous accompagne dans la création d'actes de vente et de promesses de vente conformes aux dispositions légales en vigueur.

Comment puis-je vous assister aujourd'hui ?`,
  timestamp: new Date(),
}

export default function ChatPage() {
  const { userId, etudeId, activeConversationId, loadConversations, loadConversation } = useAppData()
  const setAiPanelOpen = useUIStore((s) => s.setAiPanelOpen)

  // Close AI side panel on chat page (avoid double chat)
  useEffect(() => {
    setAiPanelOpen(false)
    return () => setAiPanelOpen(true)
  }, [setAiPanelOpen])

  const [messages, setMessages] = useState<Message[]>([WELCOME_MESSAGE])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'docx'>('docx')
  const [progressPct, setProgressPct] = useState<number | null>(null)
  const [statusText, setStatusText] = useState<string | null>(null)
  const [toastError, setToastError] = useState<string | null>(null)
  const toastTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const showToast = useCallback((msg: string) => {
    setToastError(msg)
    if (toastTimerRef.current) clearTimeout(toastTimerRef.current)
    toastTimerRef.current = setTimeout(() => setToastError(null), 5000)
  }, [])

  // Review state (Tom)
  const [reviewSections, setReviewSections] = useState<DocumentSection[] | null>(null)
  const [reviewWorkflowId, setReviewWorkflowId] = useState<string | null>(null)

  // Load conversation when activeConversationId changes
  useEffect(() => {
    if (!activeConversationId) return
    const restore = async () => {
      const data = await loadConversation(activeConversationId)
      if (data && data.messages && data.messages.length > 0) {
        const restored: Message[] = [WELCOME_MESSAGE]
        data.messages.forEach((m, idx) => {
          restored.push({
            id: `restored-${idx}`,
            role: m.role as 'user' | 'assistant',
            content: m.content,
            timestamp: new Date(),
            suggestions: m.suggestions,
          })
        })
        setMessages(restored)
        if (data.context?.progress_pct) {
          setProgressPct(data.context.progress_pct)
        }
      } else {
        setMessages([WELCOME_MESSAGE])
        setProgressPct(null)
      }
    }
    restore()
  }, [activeConversationId, loadConversation])

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
        headers: {
          'Content-Type': 'application/json',
          ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
        },
        body: JSON.stringify({
          message: content,
          user_id: userId,
          etude_id: etudeId,
          conversation_id: activeConversationId,
          context: { format: selectedFormat },
        }),
      })

      if (!response.ok || !response.body) {
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

      if (eventType && eventData) {
        handleSSEEvent(eventType, eventData)
      }

      setStatusText(null)
      loadConversations()
    } catch (error) {
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
    const previousRating = messages[messageIndex]?.feedbackRating
    setMessages((prev) =>
      prev.map((m, idx) =>
        idx === messageIndex ? { ...m, feedbackRating: rating } : m
      )
    )

    try {
      await sendChatFeedback({
        conversation_id: activeConversationId,
        message_index: messageIndex,
        rating,
      })
    } catch {
      setMessages((prev) =>
        prev.map((m, idx) =>
          idx === messageIndex ? { ...m, feedbackRating: previousRating } : m
        )
      )
      showToast('Erreur lors de l\'envoi du feedback.')
    }
  }

  // ================================================================
  // Review section par section (Tom)
  // ================================================================

  const handleReviewRequest = async (workflowId: string) => {
    try {
      const data = await loadDocumentSections(workflowId)
      setReviewSections(data.sections)
      setReviewWorkflowId(workflowId)
    } catch {
      showToast('Impossible de charger le document pour relecture.')
    }
  }

  const handleReviewComplete = () => {
    setReviewSections(null)
    setReviewWorkflowId(null)
    sendMessage('La relecture du document est terminee. Merci.')
  }

  return (
    <div className="flex flex-col h-full min-h-0 overflow-hidden">
      {/* Progress bar */}
      {progressPct != null && progressPct > 0 && (
        <div className="flex items-center gap-3 px-6 py-2.5 border-b border-champagne bg-cream/50">
          <span className="text-[0.72rem] text-slate whitespace-nowrap">
            Collecte des informations
          </span>
          <div className="flex-1 h-1.5 bg-sand rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-gold to-gold-dark rounded-full transition-all duration-700 ease-out"
              style={{ width: `${Math.min(progressPct, 100)}%` }}
            />
          </div>
          <span className="text-[0.72rem] font-medium text-gold-dark whitespace-nowrap">
            {Math.round(progressPct)}%
          </span>
        </div>
      )}

      {toastError && (
        <div className="mx-4 mt-2 px-4 py-2.5 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg flex items-center justify-between">
          <span>{toastError}</span>
          <button onClick={() => setToastError(null)} className="ml-3 text-red-400 hover:text-red-600 font-bold">✕</button>
        </div>
      )}

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
