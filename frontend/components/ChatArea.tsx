'use client'

import { useRef, useEffect, useState } from 'react'
import { Scale, Paperclip, Mic, Send, FileText, FilePlus, Edit } from 'lucide-react'
import type { Message } from '@/app/page'
import ReactMarkdown from 'react-markdown'

interface ChatAreaProps {
  messages: Message[]
  isLoading: boolean
  onSendMessage: (content: string) => void
  selectedFormat: 'pdf' | 'docx'
  onFormatChange: (format: 'pdf' | 'docx') => void
}

export default function ChatArea({
  messages,
  isLoading,
  onSendMessage,
  selectedFormat,
  onFormatChange,
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
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            quickActions={message.id === '1' ? quickActions : undefined}
            onQuickAction={(label) => onSendMessage(label)}
            showFormatSelector={message.content.includes('format')}
            selectedFormat={selectedFormat}
            onFormatChange={onFormatChange}
          />
        ))}

        {isLoading && <TypingIndicator />}
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
  quickActions,
  onQuickAction,
  showFormatSelector,
  selectedFormat,
  onFormatChange,
}: {
  message: Message
  quickActions?: { icon: any; label: string }[]
  onQuickAction?: (label: string) => void
  showFormatSelector?: boolean
  selectedFormat?: 'pdf' | 'docx'
  onFormatChange?: (format: 'pdf' | 'docx') => void
}) {
  const isAssistant = message.role === 'assistant'

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

        {/* Legal Reference */}
        {isAssistant && message.id === '1' && (
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-navy/5 rounded-md text-[0.7rem] text-navy font-medium mt-3">
            <Scale className="w-3 h-3" />
            Art. 1582 et s. Code civil
          </div>
        )}
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex gap-3.5 max-w-[85%] self-start animate-fade-in">
      <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-sand border border-champagne">
        <Scale className="w-[18px] h-[18px] text-gold-dark" />
      </div>
      <div className="px-5 py-4 bg-cream border border-champagne rounded-2xl rounded-bl-md">
        <div className="flex gap-1">
          <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
          <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
          <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
        </div>
      </div>
    </div>
  )
}
