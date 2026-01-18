'use client'

import { FileText, Download } from 'lucide-react'

export default function Header() {
  return (
    <header className="px-7 py-5 flex items-center justify-between border-b border-champagne bg-ivory">
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
    </header>
  )
}
