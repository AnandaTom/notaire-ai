'use client'

import type { Question } from '@/types/workflow'

interface BooleanFieldProps {
  question: Question
  value: boolean | null
  onChange: (value: boolean) => void
  error?: string
}

export default function BooleanField({ question, value, onChange, error }: BooleanFieldProps) {
  return (
    <div className="space-y-2">
      <label className="block text-[0.82rem] font-medium text-charcoal">
        {question.question}
        {question.obligatoire && <span className="text-red-500 ml-0.5" aria-hidden="true">*</span>}
      </label>

      <div className="flex gap-3" role="radiogroup" aria-label={question.question}>
        <button
          type="button"
          role="radio"
          aria-checked={value === true}
          onClick={() => onChange(true)}
          className={`flex-1 px-4 py-3 rounded-xl text-[0.85rem] font-medium border transition-all ${
            value === true
              ? 'bg-emerald-50 border-emerald-300 text-emerald-700'
              : 'bg-cream border-champagne text-graphite hover:border-gold-light'
          }`}
        >
          Oui
        </button>
        <button
          type="button"
          role="radio"
          aria-checked={value === false}
          onClick={() => onChange(false)}
          className={`flex-1 px-4 py-3 rounded-xl text-[0.85rem] font-medium border transition-all ${
            value === false
              ? 'bg-red-50 border-red-300 text-red-700'
              : 'bg-cream border-champagne text-graphite hover:border-gold-light'
          }`}
        >
          Non
        </button>
      </div>

      {question.aide && !error && (
        <p id={`${question.variable}-aide`} className="text-[0.75rem] text-slate">{question.aide}</p>
      )}
      {error && (
        <p id={`${question.variable}-error`} role="alert" className="text-[0.75rem] text-red-600">{error}</p>
      )}
    </div>
  )
}
