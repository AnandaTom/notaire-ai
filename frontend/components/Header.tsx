'use client'

import { FileText, Download } from 'lucide-react'

interface HeaderProps {
  progressPct: number | null
}

export default function Header({ progressPct }: HeaderProps) {
  return (
    <header className="px-7 py-5 flex flex-col gap-3 border-b border-champagne bg-ivory">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="font-serif text-xl font-semibold text-charcoal">
            Création d'acte
          </h2>
          <div className="flex items-center gap-1.5 px-3 py-1 bg-sand rounded-full text-[0.7rem] text-slate">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
            Session active
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button className="flex items-center gap-2 px-4 py-2.5 bg-cream border border-champagne rounded-xl text-[0.8rem] text-graphite hover:border-gold hover:bg-sand transition-all">
            <FileText className="w-4 h-4" />
            Brouillons
          </button>
          <button className="flex items-center gap-2 px-4 py-2.5 bg-gold border border-gold rounded-xl text-[0.8rem] text-white hover:bg-gold-dark transition-all">
            <Download className="w-4 h-4" />
            Exporter
          </button>
        </div>
      </div>

      {progressPct != null && progressPct > 0 && (
        <div className="flex items-center gap-3">
          <span className="text-[0.72rem] text-slate whitespace-nowrap">
            Collecte des informations
          </span>
          <div className="flex-1 h-1.5 bg-sand rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-gold to-gold-dark rounded-full transition-all duration-700 ease-out"
              style={{ width: `${Math.min(progressPct, 100)}%` }}
            />
          </div>
          <span className="text-[0.72rem] font-medium text-gold-dark whitespace-nowrap">
            {Math.round(progressPct)}%
          </span>
        </div>
      )}
    </header>
  )
}
