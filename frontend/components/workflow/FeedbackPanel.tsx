'use client'

import { useState } from 'react'
import { Send, MessageSquare } from 'lucide-react'
import * as api from '@/lib/api'

interface FeedbackPanelProps {
  workflowId?: string
  section?: string
  onSubmitted?: () => void
}

export default function FeedbackPanel({ workflowId, section, onSubmitted }: FeedbackPanelProps) {
  const [type, setType] = useState<'erreur' | 'suggestion' | 'question'>('suggestion')
  const [contenu, setContenu] = useState('')
  const [sending, setSending] = useState(false)
  const [sent, setSent] = useState(false)

  const handleSubmit = async () => {
    if (!contenu.trim()) return
    setSending(true)
    try {
      await api.sendFeedback({
        workflow_id: workflowId,
        section: section || 'general',
        type,
        contenu: contenu.trim(),
      })
      setSent(true)
      setContenu('')
      onSubmitted?.()
      setTimeout(() => setSent(false), 3000)
    } catch {
      // Silently fail
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="bg-ivory border border-champagne rounded-xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <MessageSquare className="w-4 h-4 text-gold-dark" />
        <h3 className="text-[0.85rem] font-semibold text-charcoal">Donner un retour</h3>
      </div>

      {/* Type */}
      <div className="flex gap-2 mb-3">
        {[
          { value: 'erreur' as const, label: 'Erreur', color: 'red' },
          { value: 'suggestion' as const, label: 'Suggestion', color: 'amber' },
          { value: 'question' as const, label: 'Question', color: 'blue' },
        ].map((opt) => (
          <button
            key={opt.value}
            onClick={() => setType(opt.value)}
            className={`px-3 py-1.5 rounded-lg text-[0.78rem] font-medium border transition-all ${
              type === opt.value
                ? opt.color === 'red'
                  ? 'bg-red-50 border-red-300 text-red-700'
                  : opt.color === 'amber'
                  ? 'bg-amber-50 border-amber-300 text-amber-700'
                  : 'bg-blue-50 border-blue-300 text-blue-700'
                : 'bg-cream border-champagne text-slate hover:border-gold-light'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Contenu */}
      <textarea
        value={contenu}
        onChange={(e) => setContenu(e.target.value)}
        placeholder="Décrivez le problème ou votre suggestion..."
        rows={3}
        className="w-full px-4 py-3 bg-cream border border-champagne rounded-xl text-[0.85rem] text-charcoal resize-none focus:outline-none focus:ring-2 focus:border-gold focus:ring-gold/10 transition-all placeholder:text-slate/50 mb-3"
      />

      {/* Bouton */}
      <div className="flex items-center justify-between">
        {sent ? (
          <span className="text-[0.82rem] text-emerald-600 font-medium">Merci pour votre retour !</span>
        ) : (
          <span />
        )}
        <button
          onClick={handleSubmit}
          disabled={!contenu.trim() || sending}
          className="flex items-center gap-2 px-4 py-2 bg-gold text-white rounded-lg text-[0.82rem] font-medium hover:bg-gold-dark disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <Send className="w-3.5 h-3.5" />
          Envoyer
        </button>
      </div>
    </div>
  )
}
