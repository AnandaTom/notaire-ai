'use client'

import { useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import type { Question } from '@/types/workflow'

interface ArrayFieldProps {
  question: Question
  value: string[]
  onChange: (value: string[]) => void
  error?: string
}

export default function ArrayField({ question, value, onChange, error }: ArrayFieldProps) {
  const items = Array.isArray(value) ? value : []
  const [newItem, setNewItem] = useState('')

  const addItem = () => {
    if (newItem.trim()) {
      onChange([...items, newItem.trim()])
      setNewItem('')
    }
  }

  const removeItem = (index: number) => {
    onChange(items.filter((_, i) => i !== index))
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addItem()
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-[0.82rem] font-medium text-charcoal">
        {question.question}
        {question.obligatoire && <span className="text-red-500 ml-0.5">*</span>}
      </label>

      {items.length > 0 && (
        <div className="space-y-1.5">
          {items.map((item, index) => (
            <div key={index} className="flex items-center gap-2 px-4 py-2.5 bg-cream border border-champagne rounded-xl">
              <span className="flex-1 text-[0.85rem] text-charcoal">{item}</span>
              <button
                type="button"
                onClick={() => removeItem(index)}
                aria-label={`Supprimer l'élément : ${item}`}
                className="p-1 text-slate hover:text-red-500 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <input
          type="text"
          value={newItem}
          onChange={(e) => setNewItem(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={question.placeholder || 'Ajouter un élément...'}
          aria-label={question.question}
          className="flex-1 px-4 py-3 bg-cream border border-champagne rounded-xl text-[0.85rem] text-charcoal focus:outline-none focus:ring-2 focus:border-gold focus:ring-gold/10 transition-all placeholder:text-slate/50"
        />
        <button
          type="button"
          onClick={addItem}
          disabled={!newItem.trim()}
          aria-label="Ajouter l'élément"
          className="px-4 py-3 bg-gold/10 border border-gold/30 text-gold-dark rounded-xl hover:bg-gold/20 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <Plus className="w-4 h-4" />
        </button>
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
