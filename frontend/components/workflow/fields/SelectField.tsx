'use client'

import type { Question } from '@/types/workflow'

interface SelectFieldProps {
  question: Question
  value: string
  onChange: (value: string) => void
  error?: string
}

export default function SelectField({ question, value, onChange, error }: SelectFieldProps) {
  const options = question.options || []
  const useRadio = options.length <= 5

  return (
    <div className="space-y-2">
      <label className="block text-[0.82rem] font-medium text-charcoal">
        {question.question}
        {question.obligatoire && <span className="text-red-500 ml-0.5">*</span>}
      </label>

      {useRadio ? (
        <div className="flex flex-wrap gap-2">
          {options.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onChange(option)}
              className={`px-4 py-2.5 rounded-xl text-[0.82rem] font-medium border transition-all ${
                value === option
                  ? 'bg-gold/10 border-gold text-gold-dark'
                  : 'bg-cream border-champagne text-graphite hover:border-gold-light'
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      ) : (
        <select
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          className={`w-full px-4 py-3 bg-cream border rounded-xl text-[0.85rem] text-charcoal focus:outline-none focus:ring-2 transition-all ${
            error ? 'border-red-300 focus:ring-red-200' : 'border-champagne focus:border-gold focus:ring-gold/10'
          }`}
        >
          <option value="">Sélectionnez...</option>
          {options.map((option) => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      )}

      {question.aide && !error && (
        <p className="text-[0.75rem] text-slate">{question.aide}</p>
      )}
      {error && (
        <p className="text-[0.75rem] text-red-600">{error}</p>
      )}
    </div>
  )
}
