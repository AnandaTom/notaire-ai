'use client'

import { useState } from 'react'
import { ChevronDown, ChevronUp, Edit3, AlertTriangle, CheckCircle } from 'lucide-react'
import { useWorkflowStore } from '@/stores/workflowStore'
import type { Section } from '@/types/workflow'

export default function DocumentReview() {
  const sections = useWorkflowStore((s) => s.sections)
  const donnees = useWorkflowStore((s) => s.donnees)
  const validationMessages = useWorkflowStore((s) => s.validationMessages)
  const goToSection = useWorkflowStore((s) => s.goToSection)
  const setStep = useWorkflowStore((s) => s.setStep)
  const startGeneration = useWorkflowStore((s) => s.startGeneration)

  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(sections.map((s) => s.id))
  )

  const erreurs = validationMessages.filter((m) => m.niveau === 'erreur')
  const avertissements = validationMessages.filter((m) => m.niveau === 'avertissement')
  const hasBlockingErrors = erreurs.length > 0

  const toggleSection = (id: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const goEditSection = (index: number) => {
    goToSection(index)
    setStep('COLLECTING')
  }

  const handleGenerate = () => {
    startGeneration()
  }

  return (
    <div className="max-w-2xl mx-auto py-8 px-6">
      <h2 className="text-xl font-serif font-semibold text-charcoal mb-2">
        Relecture avant génération
      </h2>
      <p className="text-[0.85rem] text-slate mb-6">
        Vérifiez les informations saisies avant de générer le document.
      </p>

      {/* Alertes */}
      {(erreurs.length > 0 || avertissements.length > 0) && (
        <div className="space-y-2 mb-6">
          {erreurs.map((e, i) => (
            <div key={`err-${i}`} className="flex items-start gap-2 px-4 py-3 bg-red-50 border border-red-200 rounded-xl">
              <AlertTriangle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
              <p className="text-[0.82rem] text-red-700">{e.message}</p>
            </div>
          ))}
          {avertissements.map((a, i) => (
            <div key={`warn-${i}`} className="flex items-start gap-2 px-4 py-3 bg-amber-50 border border-amber-200 rounded-xl">
              <AlertTriangle className="w-4 h-4 text-amber-500 mt-0.5 flex-shrink-0" />
              <p className="text-[0.82rem] text-amber-700">{a.message}</p>
            </div>
          ))}
        </div>
      )}

      {/* Sections */}
      <div className="space-y-3">
        {sections.map((section, index) => (
          <ReviewSection
            key={section.id}
            section={section}
            index={index}
            donnees={donnees}
            expanded={expandedSections.has(section.id)}
            onToggle={() => toggleSection(section.id)}
            onEdit={() => goEditSection(index)}
          />
        ))}
      </div>

      {/* Bouton generer */}
      <div className="mt-8 flex justify-center">
        <button
          onClick={handleGenerate}
          disabled={hasBlockingErrors}
          className="px-8 py-3.5 bg-gold text-white rounded-xl text-[0.9rem] font-semibold hover:bg-gold-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-gold/25"
        >
          {hasBlockingErrors
            ? 'Corrigez les erreurs avant de générer'
            : 'Générer le document'
          }
        </button>
      </div>
    </div>
  )
}

function ReviewSection({
  section,
  index,
  donnees,
  expanded,
  onToggle,
  onEdit,
}: {
  section: Section
  index: number
  donnees: Record<string, unknown>
  expanded: boolean
  onToggle: () => void
  onEdit: () => void
}) {
  const filledQuestions = section.questions.filter(
    (q) => getNestedValue(donnees, q.variable) !== undefined && getNestedValue(donnees, q.variable) !== ''
  )
  const allFilled = filledQuestions.length === section.questions.filter((q) => q.obligatoire).length

  return (
    <div className="border border-champagne rounded-xl overflow-hidden bg-ivory">
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 px-5 py-3.5 hover:bg-sand/50 transition-all"
      >
        <div className={`w-5 h-5 rounded-md flex items-center justify-center flex-shrink-0 ${
          allFilled ? 'bg-emerald-100 text-emerald-600' : 'bg-sand text-slate'
        }`}>
          {allFilled ? <CheckCircle className="w-3.5 h-3.5" /> : <span className="text-[0.65rem] font-bold">{index + 1}</span>}
        </div>
        <span className="flex-1 text-left text-[0.85rem] font-medium text-charcoal">
          {section.titre}
        </span>
        <span className="text-[0.72rem] text-slate mr-2">
          {filledQuestions.length}/{section.questions.length}
        </span>
        {expanded ? <ChevronUp className="w-4 h-4 text-slate" /> : <ChevronDown className="w-4 h-4 text-slate" />}
      </button>

      {/* Content */}
      {expanded && (
        <div className="px-5 pb-4 border-t border-champagne/50">
          <div className="pt-3 space-y-2">
            {section.questions.map((q) => {
              const val = getNestedValue(donnees, q.variable)
              return (
                <div key={q.id} className="flex justify-between items-baseline py-1.5">
                  <span className="text-[0.8rem] text-slate">{q.question}</span>
                  <span className={`text-[0.82rem] font-medium ml-4 text-right ${
                    val ? 'text-charcoal' : 'text-slate/40 italic'
                  }`}>
                    {formatValue(val)}
                  </span>
                </div>
              )
            })}
          </div>
          <button
            onClick={onEdit}
            className="mt-3 flex items-center gap-1.5 text-[0.78rem] text-gold-dark hover:text-gold font-medium transition-colors"
          >
            <Edit3 className="w-3.5 h-3.5" />
            Modifier
          </button>
        </div>
      )}
    </div>
  )
}

function getNestedValue(obj: Record<string, unknown>, path: string): unknown {
  if (!path) return undefined
  return path.split('.').reduce((acc: unknown, key) => {
    if (acc && typeof acc === 'object') return (acc as Record<string, unknown>)[key]
    return undefined
  }, obj)
}

function formatValue(val: unknown): string {
  if (val === undefined || val === null || val === '') return 'Non renseigné'
  if (typeof val === 'boolean') return val ? 'Oui' : 'Non'
  if (Array.isArray(val)) return val.length > 0 ? val.join(', ') : 'Aucun'
  if (typeof val === 'object') return Object.values(val).filter(Boolean).join(' ')
  return String(val)
}
