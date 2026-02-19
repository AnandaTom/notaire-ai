'use client'

import type { Question } from '@/types/workflow'

interface ContactValue {
  nom?: string
  prenom?: string
  email?: string
  telephone?: string
}

interface ContactFieldProps {
  question: Question
  value: ContactValue
  onChange: (value: ContactValue) => void
  onBlur?: () => void
  error?: string
}

export default function ContactField({ question, value, onChange, onBlur, error }: ContactFieldProps) {
  const contact: ContactValue = value || {}

  const update = (field: keyof ContactValue, val: string) => {
    onChange({ ...contact, [field]: val })
  }

  return (
    <div className="space-y-2">
      <label className="block text-[0.82rem] font-medium text-charcoal">
        {question.question}
        {question.obligatoire && <span className="text-red-500 ml-0.5">*</span>}
      </label>

      <div className="grid grid-cols-2 gap-2">
        <input
          type="text"
          value={contact.nom || ''}
          onChange={(e) => update('nom', e.target.value)}
          onBlur={onBlur}
          placeholder="Nom"
          aria-label="Nom"
          className="px-4 py-3 bg-cream border border-champagne rounded-xl text-[0.85rem] text-charcoal focus:outline-none focus:ring-2 focus:border-gold focus:ring-gold/10 transition-all placeholder:text-slate/50"
        />
        <input
          type="text"
          value={contact.prenom || ''}
          onChange={(e) => update('prenom', e.target.value)}
          onBlur={onBlur}
          placeholder="Prénom"
          aria-label="Prénom"
          className="px-4 py-3 bg-cream border border-champagne rounded-xl text-[0.85rem] text-charcoal focus:outline-none focus:ring-2 focus:border-gold focus:ring-gold/10 transition-all placeholder:text-slate/50"
        />
        <input
          type="email"
          value={contact.email || ''}
          onChange={(e) => update('email', e.target.value)}
          onBlur={onBlur}
          placeholder="Email"
          aria-label="Adresse email"
          className="px-4 py-3 bg-cream border border-champagne rounded-xl text-[0.85rem] text-charcoal focus:outline-none focus:ring-2 focus:border-gold focus:ring-gold/10 transition-all placeholder:text-slate/50"
        />
        <input
          type="tel"
          value={contact.telephone || ''}
          onChange={(e) => update('telephone', e.target.value)}
          onBlur={onBlur}
          placeholder="Téléphone"
          aria-label="Numéro de téléphone"
          className="px-4 py-3 bg-cream border border-champagne rounded-xl text-[0.85rem] text-charcoal focus:outline-none focus:ring-2 focus:border-gold focus:ring-gold/10 transition-all placeholder:text-slate/50"
        />
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
