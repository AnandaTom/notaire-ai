'use client'

import { useRef, useEffect, useState } from 'react'
import Link from 'next/link'
import { Paperclip, Mic, Send, FileText, FilePlus, Edit, ListChecks } from 'lucide-react'
import type { Message } from '@/types'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

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
      <div className="px-7 pt-3 pb-0 bg-ivory border-t border-champagne flex justify-end">
        <Link
          href="/app/workflow"
          className="flex items-center gap-1.5 px-3 py-1.5 text-[0.78rem] text-gold-dark hover:bg-gold/10 rounded-lg transition-colors font-medium"
        >
          <ListChecks className="w-4 h-4" />
          Mode guide
        </Link>
      </div>
      <form onSubmit={handleSubmit} className="px-7 pb-5 pt-2 bg-ivory">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={handleTextareaChange}
              onKeyDown={handleKeyDown}
              placeholder="Rédigez votre message..."
              aria-label="Message"
              rows={1}
              className="w-full px-5 py-4 pr-24 bg-cream border border-champagne rounded-2xl text-[0.88rem] text-charcoal resize-none min-h-[52px] max-h-[130px] focus:outline-none focus:border-gold focus:bg-ivory focus:ring-2 focus:ring-gold/10 transition-all placeholder:text-slate placeholder:font-light"
            />
            <div className="absolute right-3 bottom-2.5 flex gap-1.5">
              <button
                type="button"
                aria-label="Joindre un fichier"
                className="w-8 h-8 flex items-center justify-center text-slate hover:text-gold-dark hover:bg-sand rounded-lg transition-all"
              >
                <Paperclip className="w-[18px] h-[18px]" />
              </button>
              <button
                type="button"
                aria-label="Enregistrer un message vocal"
                className="w-8 h-8 flex items-center justify-center text-slate hover:text-gold-dark hover:bg-sand rounded-lg transition-all"
              >
                <Mic className="w-[18px] h-[18px]" />
              </button>
            </div>
          </div>
          <button
            type="submit"
            aria-label="Envoyer le message"
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
