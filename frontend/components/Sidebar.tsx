'use client'

import { FileText, Book, FolderOpen, Scale, HelpCircle, Shield } from 'lucide-react'

export default function Sidebar() {
  return (
    <aside className="bg-navy flex flex-col relative overflow-hidden">
      {/* Pattern background */}
      <div className="absolute inset-0 opacity-[0.02]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
      }} />

      {/* Header */}
      <div className="p-6 border-b border-white/10 relative z-10">
        <div className="flex items-center gap-3.5 mb-5">
          <div className="w-11 h-11 bg-gradient-to-br from-gold to-gold-dark rounded-xl flex items-center justify-center shadow-lg shadow-gold/30">
            <Scale className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-serif text-xl font-semibold text-white tracking-tight">
              NotaireAI
            </h1>
            <p className="text-[0.7rem] text-white/50 uppercase tracking-widest">
              Assistant juridique
            </p>
          </div>
        </div>

        <div className="bg-white/5 rounded-xl p-3.5 border border-white/10">
          <p className="text-[0.65rem] text-white/40 uppercase tracking-wider mb-1">
            Connecté en tant que
          </p>
          <h3 className="font-serif text-base text-white font-medium">
            Me Charlotte Diaz
          </h3>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 flex-1 relative z-10">
        <div className="mb-6">
          <p className="text-[0.65rem] text-white/35 uppercase tracking-widest px-2 mb-2.5">
            Actions
          </p>
          <NavItem icon={FileText} label="Nouvel acte" active />
          <NavItem icon={FolderOpen} label="Mes actes" />
          <NavItem icon={Book} label="Modèles" />
        </div>

        <div className="mb-6">
          <p className="text-[0.65rem] text-white/35 uppercase tracking-widest px-2 mb-2.5">
            Références
          </p>
          <NavItem icon={HelpCircle} label="Code civil" />
          <NavItem icon={FolderOpen} label="Clauses types" />
        </div>
      </nav>

      {/* Footer */}
      <div className="p-5 border-t border-white/10 relative z-10">
        <div className="flex items-center gap-2.5 p-3 bg-white/[0.03] rounded-xl border border-white/5">
          <Shield className="w-5 h-5 text-gold" />
          <div className="text-[0.7rem] text-white/50 leading-tight">
            <strong className="text-white/80 block">Conforme RGPD</strong>
            Données chiffrées AES-256
          </div>
        </div>
      </div>
    </aside>
  )
}

function NavItem({
  icon: Icon,
  label,
  active = false
}: {
  icon: any
  label: string
  active?: boolean
}) {
  return (
    <div className={`
      flex items-center gap-3 px-3.5 py-3 rounded-xl cursor-pointer transition-all mb-1
      ${active
        ? 'bg-gold/15 text-gold-light'
        : 'text-white/70 hover:bg-white/10 hover:text-white'
      }
    `}>
      <Icon className={`w-[18px] h-[18px] ${active ? 'opacity-100' : 'opacity-70'}`} />
      <span className="text-[0.85rem]">{label}</span>
    </div>
  )
}
