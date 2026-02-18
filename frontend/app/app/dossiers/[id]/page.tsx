'use client'

import Link from 'next/link'
import { ArrowLeft, FolderOpen } from 'lucide-react'

export default function DossierDetailPage() {
  return (
    <div className="min-h-screen bg-ivory">
      <header className="bg-white border-b border-champagne px-8 py-5">
        <div className="max-w-4xl mx-auto flex items-center gap-4">
          <Link href="/app/dossiers" className="p-2 hover:bg-sand rounded-xl transition-colors">
            <ArrowLeft className="w-5 h-5 text-slate" />
          </Link>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sand rounded-xl flex items-center justify-center">
              <FolderOpen className="w-5 h-5 text-gold-dark" />
            </div>
            <h1 className="font-serif text-2xl text-charcoal font-semibold">Detail du dossier</h1>
          </div>
        </div>
      </header>
      <main className="max-w-4xl mx-auto px-8 py-16 text-center">
        <FolderOpen className="w-16 h-16 text-champagne mx-auto mb-4" />
        <h2 className="font-serif text-xl text-charcoal mb-2">Page en cours de construction</h2>
        <p className="text-slate text-[0.9rem] mb-6">
          Le detail du dossier sera disponible prochainement.
        </p>
        <Link
          href="/app/dossiers"
          className="inline-flex items-center gap-2 px-5 py-3 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors font-medium"
        >
          <ArrowLeft className="w-4 h-4" />
          Retour aux dossiers
        </Link>
      </main>
    </div>
  )
}
