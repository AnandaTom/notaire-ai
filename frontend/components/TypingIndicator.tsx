'use client'

import { Scale } from 'lucide-react'

interface TypingIndicatorProps {
  statusText?: string | null
}

export default function TypingIndicator({ statusText }: TypingIndicatorProps) {
  return (
    <div className="flex gap-3.5 max-w-[85%] self-start animate-fade-in">
      <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-sand border border-champagne">
        <Scale className="w-[18px] h-[18px] text-gold-dark" />
      </div>
      <div className="px-5 py-4 bg-cream border border-champagne rounded-2xl rounded-bl-md">
        {statusText ? (
          <p className="text-[0.8rem] text-slate italic">{statusText}</p>
        ) : (
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
            <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
            <span className="w-2 h-2 bg-slate rounded-full typing-dot" />
          </div>
        )}
      </div>
    </div>
  )
}
