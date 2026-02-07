'use client'

import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Check, Edit3, MessageSquare, X, ChevronDown, ChevronUp } from 'lucide-react'

// Types
interface DocumentSection {
  id: string
  index: number
  title: string
  content: string
  heading_level: number
}

type SectionStatus = 'pending' | 'approved' | 'corrected' | 'commented'

interface ParagraphReviewProps {
  workflowId: string
  sections: DocumentSection[]
  onComplete: () => void
  onClose: () => void
  apiUrl?: string
  apiKey?: string
}

// Composant principal
export default function ParagraphReview({
  workflowId,
  sections,
  onComplete,
  onClose,
  apiUrl = '',
  apiKey = '',
}: ParagraphReviewProps) {
  const [statuses, setStatuses] = useState<Record<string, SectionStatus>>({})
  const [editingSection, setEditingSection] = useState<string | null>(null)
  const [feedbackText, setFeedbackText] = useState('')
  const [feedbackRaison, setFeedbackRaison] = useState('')
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(sections.map(s => s.id))
  )
  const [submitting, setSubmitting] = useState(false)

  const reviewedCount = Object.keys(statuses).length
  const totalCount = sections.length
  const allReviewed = reviewedCount === totalCount

  const toggleExpand = (sectionId: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev)
      if (next.has(sectionId)) {
        next.delete(sectionId)
      } else {
        next.add(sectionId)
      }
      return next
    })
  }

  const submitFeedback = async (
    section: DocumentSection,
    action: string,
    contenu?: string,
    raison?: string
  ) => {
    setSubmitting(true)
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' }
      if (apiKey) headers['X-API-Key'] = apiKey

      await fetch(`${apiUrl}/feedback/paragraphe`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          workflow_id: workflowId,
          section_id: section.id,
          section_title: section.title,
          action,
          contenu: contenu || null,
          raison: raison || null,
        }),
      })

      // Mettre a jour le statut local
      setStatuses(prev => ({
        ...prev,
        [section.id]: action === 'approuver' ? 'approved' : action === 'corriger' ? 'corrected' : 'commented',
      }))

      // Reset du formulaire
      setEditingSection(null)
      setFeedbackText('')
      setFeedbackRaison('')
    } catch (error) {
      console.error('Feedback error:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const statusIcon = (sectionId: string) => {
    const status = statuses[sectionId]
    if (!status || status === 'pending') return null
    if (status === 'approved') return <Check className="w-4 h-4 text-green-600" />
    if (status === 'corrected') return <Edit3 className="w-4 h-4 text-amber-600" />
    if (status === 'commented') return <MessageSquare className="w-4 h-4 text-blue-600" />
    return null
  }

  const statusBg = (sectionId: string) => {
    const status = statuses[sectionId]
    if (status === 'approved') return 'border-l-green-500 bg-green-50'
    if (status === 'corrected') return 'border-l-amber-500 bg-amber-50'
    if (status === 'commented') return 'border-l-blue-500 bg-blue-50'
    return 'border-l-gray-300 bg-white'
  }

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center overflow-y-auto py-8">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-4xl mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gradient-to-r from-amber-50 to-white rounded-t-xl">
          <div>
            <h2 className="text-lg font-semibold text-gray-800">
              Relecture section par section
            </h2>
            <p className="text-sm text-gray-500">
              {reviewedCount}/{totalCount} sections relues
            </p>
          </div>
          <div className="flex items-center gap-3">
            {allReviewed && (
              <button
                onClick={onComplete}
                className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
              >
                Terminer la relecture
              </button>
            )}
            <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg">
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        {/* Progress bar */}
        <div className="h-1 bg-gray-200">
          <div
            className="h-full bg-amber-500 transition-all duration-300"
            style={{ width: `${totalCount > 0 ? (reviewedCount / totalCount) * 100 : 0}%` }}
          />
        </div>

        {/* Sections */}
        <div className="divide-y max-h-[70vh] overflow-y-auto">
          {sections.map(section => (
            <div
              key={section.id}
              className={`border-l-4 transition-colors ${statusBg(section.id)}`}
            >
              {/* Section header */}
              <div
                className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
                onClick={() => toggleExpand(section.id)}
              >
                <div className="flex items-center gap-3">
                  {statusIcon(section.id)}
                  <span className="font-medium text-gray-800">{section.title}</span>
                </div>
                {expandedSections.has(section.id) ? (
                  <ChevronUp className="w-4 h-4 text-gray-400" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                )}
              </div>

              {/* Section content */}
              {expandedSections.has(section.id) && (
                <div className="px-6 pb-4">
                  <div className="prose prose-sm max-w-none text-gray-700 mb-4 bg-gray-50 p-4 rounded-lg">
                    <ReactMarkdown>{section.content}</ReactMarkdown>
                  </div>

                  {/* Actions */}
                  {editingSection !== section.id ? (
                    <div className="flex gap-2">
                      <button
                        onClick={() => submitFeedback(section, 'approuver')}
                        disabled={submitting || statuses[section.id] === 'approved'}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-green-200 text-green-700 hover:bg-green-50 disabled:opacity-50"
                      >
                        <Check className="w-3.5 h-3.5" /> Approuver
                      </button>
                      <button
                        onClick={() => { setEditingSection(section.id); setFeedbackText('') }}
                        disabled={submitting}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-amber-200 text-amber-700 hover:bg-amber-50"
                      >
                        <Edit3 className="w-3.5 h-3.5" /> Corriger
                      </button>
                      <button
                        onClick={() => { setEditingSection(section.id); setFeedbackText('') }}
                        disabled={submitting}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-lg border border-blue-200 text-blue-700 hover:bg-blue-50"
                      >
                        <MessageSquare className="w-3.5 h-3.5" /> Commenter
                      </button>
                    </div>
                  ) : (
                    /* Inline editor */
                    <div className="space-y-3">
                      <textarea
                        value={feedbackText}
                        onChange={e => setFeedbackText(e.target.value)}
                        placeholder="Texte corrige ou commentaire..."
                        className="w-full p-3 border rounded-lg text-sm resize-y min-h-[80px] focus:ring-2 focus:ring-amber-300 focus:border-amber-300"
                        rows={3}
                      />
                      <input
                        value={feedbackRaison}
                        onChange={e => setFeedbackRaison(e.target.value)}
                        placeholder="Raison (optionnel)..."
                        className="w-full p-2 border rounded-lg text-sm focus:ring-2 focus:ring-amber-300 focus:border-amber-300"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => submitFeedback(section, 'corriger', feedbackText, feedbackRaison)}
                          disabled={submitting || !feedbackText.trim()}
                          className="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700 disabled:opacity-50"
                        >
                          {submitting ? 'Envoi...' : 'Envoyer la correction'}
                        </button>
                        <button
                          onClick={() => { setEditingSection(null); setFeedbackText(''); setFeedbackRaison('') }}
                          className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm hover:bg-gray-200"
                        >
                          Annuler
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
