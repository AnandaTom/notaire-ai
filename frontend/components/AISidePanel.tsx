'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import { X, Send, Sparkles } from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { useAppData } from '@/lib/hooks/useAppData'
import { API_URL, API_KEY } from '@/lib/config'

interface PanelMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
}

const WELCOME: PanelMessage = {
  id: 'welcome',
  role: 'assistant',
  content:
    'Bonjour, je suis votre assistant IA. Posez-moi une question sur le dossier en cours ou la section active.',
}

export default function AISidePanel() {
  const { aiPanelOpen, aiPanelContext, setAiPanelOpen, toggleAiPanel } = useUIStore()
  const { userId, etudeId } = useAppData()

  const [messages, setMessages] = useState<PanelMessage[]>([WELCOME])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const panelConvId = useRef(`panel-${crypto.randomUUID()}`)

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Focus input when panel opens
  useEffect(() => {
    if (aiPanelOpen) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [aiPanelOpen])

  // Ctrl+Shift+I keyboard shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'I') {
        e.preventDefault()
        toggleAiPanel()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [toggleAiPanel])

  const sendMessage = useCallback(async () => {
    const text = input.trim()
    if (!text || isStreaming) return

    const userMsg: PanelMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
    }
    const assistantId = `assistant-${Date.now()}`

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsStreaming(true)

    // Add empty assistant message for streaming
    setMessages((prev) => [
      ...prev,
      { id: assistantId, role: 'assistant', content: '' },
    ])

    try {
      const response = await fetch(`${API_URL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
        },
        body: JSON.stringify({
          message: text,
          user_id: userId,
          etude_id: etudeId,
          conversation_id: panelConvId.current,
          context: {
            source: 'ai_panel',
            section: aiPanelContext,
          },
        }),
      })

      if (!response.ok || !response.body) {
        const errorData = await response.json().catch(() => null)
        throw new Error(errorData?.detail || `Erreur ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let sseBuffer = ''
      let eventType = ''
      let eventData = ''

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
            if (eventType === 'token' && eventData) {
              try {
                const { text: token } = JSON.parse(eventData)
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId
                      ? { ...m, content: m.content + token }
                      : m
                  )
                )
              } catch { /* ignore parse errors */ }
            } else if (eventType === 'error' && eventData) {
              try {
                const { message } = JSON.parse(eventData)
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId
                      ? { ...m, content: `Erreur : ${message}` }
                      : m
                  )
                )
              } catch { /* ignore */ }
            }
            eventType = ''
            eventData = ''
          }
        }
      }

      // Handle any remaining event
      if (eventType === 'token' && eventData) {
        try {
          const { text: token } = JSON.parse(eventData)
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId
                ? { ...m, content: m.content + token }
                : m
            )
          )
        } catch { /* ignore */ }
      }
    } catch (error) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content:
                  error instanceof Error
                    ? `Erreur : ${error.message}`
                    : 'Une erreur est survenue.',
              }
            : m
        )
      )
    } finally {
      setIsStreaming(false)
    }
  }, [input, isStreaming, userId, etudeId, aiPanelContext])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div
      className={`border-l border-champagne bg-ivory flex flex-col transition-all duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] overflow-hidden
        ${aiPanelOpen
          ? 'w-[380px] min-w-[380px] max-lg:fixed max-lg:inset-0 max-lg:w-full max-lg:min-w-full max-lg:z-40 max-lg:border-l-0'
          : 'w-0 min-w-0 border-l-0'
        }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-champagne flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <span className="w-2 h-2 rounded-full bg-gold animate-pulse" />
          <span className="text-[0.85rem] font-semibold text-charcoal">
            Assistant IA
          </span>
        </div>
        <button
          onClick={() => setAiPanelOpen(false)}
          className="w-7 h-7 flex items-center justify-center rounded-lg text-slate hover:bg-sand hover:text-charcoal transition-colors"
          aria-label="Fermer l'assistant"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Messages */}
      <div
        className="flex-1 overflow-y-auto px-5 py-4 flex flex-col gap-3"
        role="log"
        aria-live="polite"
        aria-label="Messages de l'assistant IA"
      >
        {/* Context hint */}
        {aiPanelContext && (
          <div className="text-[0.7rem] text-slate text-center px-3 py-2 bg-cream rounded-lg border border-dashed border-champagne">
            <Sparkles className="w-3 h-3 inline mr-1 -mt-0.5" />
            L&apos;assistant analyse : <strong className="text-charcoal">{aiPanelContext}</strong>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={
              msg.role === 'assistant'
                ? 'bg-cream border border-champagne rounded-xl px-4 py-3 animate-scale-in'
                : 'bg-navy text-white/90 rounded-xl px-4 py-2.5 self-end max-w-[85%] animate-scale-in'
            }
          >
            <p className="text-[0.85rem] leading-relaxed whitespace-pre-wrap">
              {msg.content}
              {msg.role === 'assistant' && isStreaming && msg.content === '' && (
                <span className="inline-flex gap-1 ml-1">
                  <span className="w-1.5 h-1.5 bg-gold rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-1.5 h-1.5 bg-gold rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-1.5 h-1.5 bg-gold rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </span>
              )}
            </p>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-5 py-3.5 border-t border-champagne flex-shrink-0">
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              aiPanelContext
                ? `Question sur ${aiPanelContext}...`
                : 'Une question sur cette section ?'
            }
            disabled={isStreaming}
            className="flex-1 px-3.5 py-2.5 bg-cream border border-champagne rounded-xl text-[0.85rem] text-charcoal placeholder:text-slate/50 focus:outline-none focus:border-gold transition-colors disabled:opacity-50"
            aria-label="Message a l'assistant"
          />
          <button
            onClick={sendMessage}
            disabled={isStreaming || !input.trim()}
            className="w-9 h-9 flex items-center justify-center bg-navy rounded-lg text-gold-light hover:bg-navy-light transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
            aria-label="Envoyer"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center gap-3 mt-2 text-[0.6rem] text-slate/60">
          <span><kbd className="px-1 py-0.5 bg-sand rounded font-mono text-[0.55rem]">Ctrl+Shift+I</kbd> toggle</span>
          <span><kbd className="px-1 py-0.5 bg-sand rounded font-mono text-[0.55rem]">Enter</kbd> envoyer</span>
        </div>
      </div>
    </div>
  )
}
