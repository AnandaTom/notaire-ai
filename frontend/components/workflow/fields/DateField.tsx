'use client'

import type { Question } from '@/types/workflow'

interface DateFieldProps {
  question: Question
  value: string
  onChange: (value: string) => void
  onBlur?: () => void
  error?: string
}

export default function DateField({ question, value, onChange, onBlur, error }: DateFieldProps) {
  return (
    <div className="space-y-1.5">
      <label className="block text-[0.82rem] font-medium text-charcoal">
        {question.question}
        {question.obligatoire && <span className="text-red-500 ml-0.5">*</span>}
      </label>

      <input
        type="date"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        onBlur={onBlur}
        className={`w-full px-4 py-3 bg-cream border rounded-xl text-[0.85rem] text-charcoal focus:outline-none focus:ring-2 transition-all ${
          error ? 'border-red-300 focus:ring-red-200' : 'border-champagne focus:border-gold focus:ring-gold/10'
        }`}
      />

      {question.aide && !error && (
        <p className="text-[0.75rem] text-slate">{question.aide}</p>
      )}
      {error && (
        <p className="text-[0.75rem] text-red-600">{error}</p>
      )}
    </div>
  )
}
