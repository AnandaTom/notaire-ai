'use client'

import type { Question } from '@/types/workflow'

interface NumberFieldProps {
  question: Question
  value: number | string
  onChange: (value: number | string) => void
  onBlur?: () => void
  error?: string
}

export default function NumberField({ question, value, onChange, onBlur, error }: NumberFieldProps) {
  const isCurrency = question.variable?.includes('prix') || question.variable?.includes('montant') || question.variable?.includes('loyer')
  const isSurface = question.variable?.includes('superficie') || question.variable?.includes('surface')

  return (
    <div className="space-y-1.5">
      <label className="block text-[0.82rem] font-medium text-charcoal">
        {question.question}
        {question.obligatoire && <span className="text-red-500 ml-0.5">*</span>}
      </label>

      <div className="relative">
        <input
          type="number"
          value={value ?? ''}
          onChange={(e) => onChange(e.target.value === '' ? '' : Number(e.target.value))}
          onBlur={onBlur}
          placeholder={question.placeholder}
          step={isCurrency ? '0.01' : isSurface ? '0.01' : '1'}
          min="0"
          className={`w-full px-4 py-3 bg-cream border rounded-xl text-[0.85rem] text-charcoal focus:outline-none focus:ring-2 transition-all placeholder:text-slate/50 ${
            isCurrency || isSurface ? 'pr-12' : ''
          } ${
            error ? 'border-red-300 focus:ring-red-200' : 'border-champagne focus:border-gold focus:ring-gold/10'
          }`}
        />
        {isCurrency && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[0.8rem] text-slate">€</span>
        )}
        {isSurface && (
          <span className="absolute right-4 top-1/2 -translate-y-1/2 text-[0.8rem] text-slate">m²</span>
        )}
      </div>

      {question.aide && !error && (
        <p className="text-[0.75rem] text-slate">{question.aide}</p>
      )}
      {error && (
        <p className="text-[0.75rem] text-red-600">{error}</p>
      )}
    </div>
  )
}
