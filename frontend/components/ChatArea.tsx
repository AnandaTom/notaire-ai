'use client'

import { useRef, useEffect, useState } from 'react'
import { Scale, Paperclip, Mic, Send, FileText, FilePlus, Edit, Download, ClipboardCheck, ThumbsUp, ThumbsDown } from 'lucide-react'
import type { Message } from '@/types'
import ReactMarkdown from 'react-markdown'
import ParagraphReview from './ParagraphReview'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://notaire-ai--fastapi-app.modal.run'

interface ChatAreaProps {
  messages: Message[]
  isLoading: boolean
  onSendMessage: (content: string) => void
  selectedFormat: 'pdf' | 'docx'
  onFormatChange: (format: 'pdf' | 'docx') => void
  onReviewRequest?: (workflowId: string) => void
  onFeedback: (messageIndex: number, rating: number) => void
  statusText?: string | null
}

export default function ChatArea({
  messages,
  isLoading,
  onSendMessage,
  selectedFormat,
  onFormatChange,
  onReviewRequest,
  onFeedback,
  statusText,
}: ChatAreaProps) {
  const [input, setInput] = useState('')
  const chatRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTop = chatRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 130) + 'px'
  }

  const quickActions = [
    { icon: FilePlus, label: 'Acte de vente' },
    { icon: FileText, label: 'Promesse de vente' },
    { icon: Edit, label: 'Modifier un acte' },
  ]

  return (
    <>
      {/* Messages Area */}
      <div ref={chatRef} className="flex-1 overflow-y-auto p-7 flex flex-col gap-5 bg-ivory">
        {messages.map((message, idx) => {
          // Masquer le placeholder vide pendant le streaming
          if (message.role === 'assistant' && message.content === '' && idx === messages.length - 1) {
            return null
          }
          return (
            <MessageBubble
              key={message.id}
              message={message}
              messageIndex={idx}
              quickActions={message.id === '1' ? quickActions : undefined}
              onQuickAction={(label) => onSendMessage(label)}
              showFormatSelector={message.content.includes('format')}
              selectedFormat={selectedFormat}
              onFormatChange={onFormatChange}
              suggestions={message.suggestions}
              metadata={message.metadata}
              onReviewRequest={onReviewRequest}
              onFeedback={onFeedback}
            />
          )
        })}

        {isLoading && (messages.length === 0 || messages[messages.length - 1].role === 'user' || messages[messages.length - 1].content === '') && (
          <TypingIndicator statusText={statusText} />
        )}
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="px-7 py-5 bg-ivory border-t border-champagne">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder="Rédigez votre message..."
              rows={1}
              className="w-full px-5 py-4 pr-24 bg-cream border border-champagne rounded-2xl text-[0.88rem] text-charcoal resize-none min-h-[52px] max-h-[130px] focus:outline-none focus:border-gold focus:bg-ivory focus:ring-2 focus:ring-gold/10 transition-all placeholder:text-slate placeholder:font-light"
            />
            <div className="absolute right-3 bottom-2.5 flex gap-1.5">
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-slate hover:text-gold-dark hover:bg-sand rounded-lg transition-all"
              >
                <Paperclip className="w-[18px] h-[18px]" />
              </button>
              <button
                type="button"
                className="w-8 h-8 flex items-center justify-center text-slate hover:text-gold-dark hover:bg-sand rounded-lg transition-all"
              >
                <Mic className="w-[18px] h-[18px]" />
              </button>
            </div>
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="w-[52px] h-[52px] bg-gold text-white rounded-2xl flex items-center justify-center hover:bg-gold-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-gold/25 hover:-translate-y-0.5"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </>
  )
}

function MessageBubble({
  message,
  messageIndex,
  quickActions,
  onQuickAction,
  showFormatSelector,
  selectedFormat,
  onFormatChange,
  suggestions,
  metadata,
  onReviewRequest,
  onFeedback,
}: {
  message: Message
  messageIndex: number
  quickActions?: { icon: React.ComponentType<{ className?: string }>; label: string }[]
  onQuickAction?: (label: string) => void
  showFormatSelector?: boolean
  selectedFormat?: 'pdf' | 'docx'
  onFormatChange?: (format: 'pdf' | 'docx') => void
  suggestions?: string[]
  metadata?: { fichier_url?: string; workflow_id?: string; [key: string]: unknown }
  onReviewRequest?: (workflowId: string) => void
  onFeedback: (messageIndex: number, rating: number) => void
}) {
  const isAssistant = message.role === 'assistant'
  const isWelcome = message.id === '1'

  return (
    <div
      className={`flex gap-3.5 max-w-[85%] animate-fade-in ${
        isAssistant ? 'self-start' : 'self-end flex-row-reverse'
      }`}
    >
      {/* Avatar */}
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 text-sm font-medium ${
          isAssistant
            ? 'bg-sand border border-champagne'
            : 'bg-gold text-white'
        }`}
      >
        {isAssistant ? (
          <Scale className="w-[18px] h-[18px] text-gold-dark" />
        ) : (
          'CD'
        )}
      </div>

      {/* Content */}
      <div
        className={`p-4 px-5 rounded-2xl ${
          isAssistant
            ? 'bg-cream border border-champagne rounded-bl-md'
            : 'bg-charcoal rounded-br-md'
        }`}
      >
        {message.section && (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-sand text-gold-dark rounded-md text-[0.68rem] font-semibold uppercase tracking-wider border border-champagne mb-2.5">
            {message.section}
          </span>
        )}

        <div
          className={`text-[0.88rem] leading-relaxed ${
            isAssistant ? 'text-graphite' : 'text-white'
          }`}
        >
          {isAssistant ? (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
          ) : (
            message.content
          )}
        </div>

        {/* Quick Actions */}
        {quickActions && onQuickAction && (
          <div className="flex flex-wrap gap-2.5 mt-4">
            {quickActions.map(({ icon: Icon, label }) => (
              <button
                key={label}
                onClick={() => onQuickAction(label)}
                className="flex items-center gap-2 px-4 py-2.5 bg-ivory border border-champagne rounded-xl text-[0.82rem] text-graphite hover:border-gold hover:bg-sand transition-all"
              >
                <Icon className="w-4 h-4 text-slate" />
                {label}
              </button>
            ))}
          </div>
        )}

        {/* Format Selector */}
        {showFormatSelector && onFormatChange && (
          <div className="flex gap-2.5 mt-4">
            <button
              onClick={() => onFormatChange('pdf')}
              className={`flex items-center gap-2.5 px-4 py-3 bg-ivory border-2 rounded-xl flex-1 transition-all ${
                selectedFormat === 'pdf'
                  ? 'border-gold bg-gold/5'
                  : 'border-champagne hover:border-gold-light'
              }`}
            >
              <div className="w-6 h-6 bg-red-500 rounded flex items-center justify-center text-white text-[0.5rem] font-bold">
                PDF
              </div>
              <div className="text-left">
                <p className="text-[0.85rem] font-semibold text-charcoal">PDF</p>
                <p className="text-[0.7rem] text-slate">Document figé</p>
              </div>
            </button>
            <button
              onClick={() => onFormatChange('docx')}
              className={`flex items-center gap-2.5 px-4 py-3 bg-ivory border-2 rounded-xl flex-1 transition-all ${
                selectedFormat === 'docx'
                  ? 'border-gold bg-gold/5'
                  : 'border-champagne hover:border-gold-light'
              }`}
            >
              <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center text-white text-[0.45rem] font-bold">
                DOCX
              </div>
              <div className="text-left">
                <p className="text-[0.85rem] font-semibold text-charcoal">Word</p>
                <p className="text-[0.7rem] text-slate">Modifiable</p>
              </div>
            </button>
          </div>
        )}

        {/* Download Link + Review Button */}
        {isAssistant && message.metadata?.fichier_url && (
          <div className="flex flex-wrap gap-2 mt-3">
            <a
              href={`${API_URL}${message.metadata.fichier_url}`}
              download
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-gold text-white rounded-xl text-[0.82rem] font-medium hover:bg-gold-dark transition-all shadow-sm"
            >
              <Download className="w-4 h-4" />
              Télécharger le document
            </a>
            {message.metadata?.workflow_id && onReviewRequest && (
              <button
                onClick={() => onReviewRequest(message.metadata!.workflow_id!)}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-white border border-amber-300 text-amber-700 rounded-xl text-[0.82rem] font-medium hover:bg-amber-50 transition-all shadow-sm"
              >
                <ClipboardCheck className="w-4 h-4" />
                Relire section par section
              </button>
            )}
          </div>
        )}

        {/* Suggestions */}
        {isAssistant && message.suggestions && message.suggestions.length > 0 && onQuickAction && (
          <div className="flex flex-wrap gap-2 mt-3">
            {message.suggestions.map((suggestion, idx) => (
              <button
                key={idx}
                onClick={() => onQuickAction(suggestion)}
                className="px-3.5 py-2 bg-ivory border border-champagne rounded-xl text-[0.8rem] text-graphite hover:border-gold hover:bg-sand transition-all"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}

        {/* Legal Reference */}
        {isAssistant && isWelcome && (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-navy/5 rounded-md text-[0.7rem] text-navy font-medium mt-3">
            <Scale className="w-3 h-3" />
            Art. 1582 et s. Code civil
          </div>
        )}

        {/* Feedback Buttons */}
        {isAssistant && !isWelcome && (
          <div className="flex items-center gap-1.5 mt-3 pt-2.5 border-t border-champagne/50">
            <button
              onClick={() => onFeedback(messageIndex, 1)}
              className={`p-1.5 rounded-lg transition-all ${
                message.feedbackRating === 1
                  ? 'text-green-600 bg-green-50'
                  : 'text-slate/40 hover:text-green-600 hover:bg-green-50'
              }`}
              title="Utile"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onFeedback(messageIndex, -1)}
              className={`p-1.5 rounded-lg transition-all ${
                message.feedbackRating === -1
                  ? 'text-red-500 bg-red-50'
                  : 'text-slate/40 hover:text-red-500 hover:bg-red-50'
              }`}
              title="Pas utile"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

function TypingIndicator({ statusText }: { statusText?: string | null }) {
  return (
    <div className="flex gap-3.5 max-w-[85%] self-start animate-fade-in">
      <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-sand border border-champagne">
        <Scale className="w-[18px] h-[18px] text-gold-dark" />
      </div>
      <div className="px-5 py-4 bg-cream border border-champagne rounded-2xl rounded-bl-md">
        {statusText ? (
          <p className="text-[0.8rem] text-slate italic">{statusText}</p>
        ) : (
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
            <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
            <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
          </div>
        )}
      </div>
    </div>
  )
}
