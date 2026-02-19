'use client'

import { ChevronLeft, ChevronRight, Loader2 } from 'lucide-react'
import type { Section } from '@/types/workflow'
import { useWorkflowStore } from '@/stores/workflowStore'
import DynamicQuestion from './DynamicQuestion'

interface DynamicFormProps {
  section: Section
  onPrevious?: () => void
  onNext?: () => void
  isFirst?: boolean
  isLast?: boolean
}

export default function DynamicForm({ section, onPrevious, onNext, isFirst, isLast }: DynamicFormProps) {
  const donnees = useWorkflowStore((s) => s.donnees)
  const updateField = useWorkflowStore((s) => s.updateField)
  const submitCurrentSection = useWorkflowStore((s) => s.submitCurrentSection)
  const isLoading = useWorkflowStore((s) => s.isLoading)

  const handleNext = async () => {
    await submitCurrentSection()
    onNext?.()
  }

  return (
    <div className="flex flex-col h-full">
      {/* Section header */}
      <div className="px-6 py-5 border-b border-champagne">
        <h2 className="text-lg font-serif font-semibold text-charcoal">{section.titre}</h2>
        {section.description && (
          <p className="text-[0.82rem] text-slate mt-1">{section.description}</p>
        )}
      </div>

      {/* Questions */}
      <div className="flex-1 overflow-y-auto px-6 py-5 space-y-5">
        {section.questions.map((question) => (
          <DynamicQuestion
            key={question.id}
            question={question}
            value={getValueByPath(donnees, question.variable)}
            onChange={(val) => updateField(question.variable, val)}
            allValues={donnees}
          />
        ))}
      </div>

      {/* Navigation */}
      <nav className="px-6 py-4 border-t border-champagne bg-ivory flex justify-between items-center" aria-label="Navigation du formulaire">
        <button
          type="button"
          onClick={onPrevious}
          disabled={isFirst}
          aria-label="Section précédente"
          className="flex items-center gap-2 px-5 py-2.5 text-[0.85rem] text-graphite border border-champagne rounded-xl hover:bg-sand disabled:opacity-30 disabled:cursor-not-allowed transition-all"
        >
          <ChevronLeft className="w-4 h-4" aria-hidden="true" />
          Précédent
        </button>

        <button
          type="button"
          onClick={handleNext}
          disabled={isLoading}
          aria-label={isLast ? 'Vérifier et générer le document' : 'Section suivante'}
          aria-busy={isLoading}
          className="flex items-center gap-2 px-6 py-2.5 text-[0.85rem] font-medium text-white bg-gold rounded-xl hover:bg-gold-dark disabled:opacity-50 transition-all shadow-sm shadow-gold/20"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
          ) : isLast ? (
            'Vérifier et générer'
          ) : (
            <>
              Suivant
              <ChevronRight className="w-4 h-4" aria-hidden="true" />
            </>
          )}
        </button>
      </nav>
    </div>
  )
}

function getValueByPath(obj: Record<string, unknown>, path: string): unknown {
  if (!path) return undefined
  return path.split('.').reduce((acc: unknown, key) => {
    if (acc && typeof acc === 'object') return (acc as Record<string, unknown>)[key]
    return undefined
  }, obj)
}
