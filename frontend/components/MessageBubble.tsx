'use client'

import { Scale, Download, ClipboardCheck, ThumbsUp, ThumbsDown } from 'lucide-react'
import type { Message } from '@/types'
import ReactMarkdown from 'react-markdown'
import { API_URL } from '@/lib/config'

interface MessageBubbleProps {
  message: Message
  messageIndex: number
  quickActions?: { icon: React.ComponentType<{ className?: string }>; label: string }[]
  onQuickAction?: (label: string) => void
  showFormatSelector?: boolean
  selectedFormat?: 'pdf' | 'docx'
  onFormatChange?: (format: 'pdf' | 'docx') => void
  onReviewRequest?: (workflowId: string) => void
  onFeedback: (messageIndex: number, rating: number) => void
}

export default function MessageBubble({
  message,
  messageIndex,
  quickActions,
  onQuickAction,
  showFormatSelector,
  selectedFormat,
  onFormatChange,
  onReviewRequest,
  onFeedback,
}: MessageBubbleProps) {
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
              aria-label="Ce message est utile"
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
              aria-label="Ce message n'est pas utile"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
