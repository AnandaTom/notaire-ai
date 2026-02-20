'use client'

import { usePathname } from 'next/navigation'
import { FileText, Download, Search, Menu } from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'

const ROUTE_TITLES: Record<string, { title: string; subtitle?: string }> = {
  '/app': { title: 'Dashboard', subtitle: 'Vue d\'ensemble' },
  '/app/chat': { title: 'Chat IA', subtitle: 'Assistant de redaction' },
  '/app/dossiers': { title: 'Mes Dossiers', subtitle: 'Gestion des dossiers' },
  '/app/documents': { title: 'Mes Documents', subtitle: 'Actes generes' },
  '/app/clients': { title: 'Mes Clients', subtitle: 'Repertoire clients' },
  '/app/workflow': { title: 'Workflow guide', subtitle: 'Generation pas a pas' },
}

export default function AppHeader() {
  const pathname = usePathname()
  const { toggleMobileSidebar, setCommandPaletteOpen } = useUIStore()

  const routeInfo = (pathname && ROUTE_TITLES[pathname]) || { title: 'NotaireAI' }

  return (
    <header className="px-6 py-4 flex items-center justify-between border-b border-champagne bg-ivory flex-shrink-0">
      <div className="flex items-center gap-3">
        {/* Hamburger — mobile only */}
        <button
          onClick={toggleMobileSidebar}
          className="lg:hidden p-2 hover:bg-sand rounded-xl transition-colors"
          aria-label="Ouvrir le menu"
        >
          <Menu className="w-5 h-5 text-graphite" />
        </button>

        <div>
          <h2 className="font-serif text-xl font-semibold text-charcoal">
            {routeInfo.title}
          </h2>
          {routeInfo.subtitle && (
            <p className="text-[0.72rem] text-slate">
              {routeInfo.subtitle}
            </p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        {/* Search shortcut */}
        <button
          onClick={() => setCommandPaletteOpen(true)}
          className="hidden sm:flex items-center gap-2 px-3.5 py-2 bg-cream border border-champagne rounded-xl text-[0.8rem] text-slate hover:border-gold/50 transition-colors"
          aria-label="Recherche rapide"
        >
          <Search className="w-4 h-4" />
          <span>Rechercher...</span>
          <kbd className="hidden md:inline-flex items-center px-1.5 py-0.5 bg-sand rounded text-[0.65rem] text-graphite font-mono">
            Ctrl+K
          </kbd>
        </button>

        <button
          disabled
          title="Bientot disponible"
          className="flex items-center gap-2 px-4 py-2.5 bg-cream border border-champagne rounded-xl text-[0.8rem] text-graphite opacity-50 cursor-not-allowed"
        >
          <FileText className="w-4 h-4" />
          <span className="hidden sm:inline">Brouillons</span>
        </button>
        <button
          disabled
          title="Bientot disponible"
          className="flex items-center gap-2 px-4 py-2.5 bg-gold border border-gold rounded-xl text-[0.8rem] text-white opacity-50 cursor-not-allowed"
        >
          <Download className="w-4 h-4" />
          <span className="hidden sm:inline">Exporter</span>
        </button>
      </div>
    </header>
  )
}
