'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import {
  Plus,
  MessageSquare,
  Scale,
  HelpCircle,
  Book,
  Shield,
  FolderOpen,
  Users,
  FileText,
  ClipboardList,
  LayoutDashboard,
  LogOut,
  X,
} from 'lucide-react'
import { useAppData } from '@/lib/hooks/useAppData'
import { useUIStore } from '@/stores/uiStore'
import { supabase } from '@/lib/supabase'

function timeAgo(dateStr: string): string {
  const now = new Date()
  const date = new Date(dateStr)
  const diff = Math.floor((now.getTime() - date.getTime()) / 1000)
  if (diff < 60) return "a l'instant"
  if (diff < 3600) return `il y a ${Math.floor(diff / 60)}min`
  if (diff < 86400) return `il y a ${Math.floor(diff / 3600)}h`
  if (diff < 604800) return `il y a ${Math.floor(diff / 86400)}j`
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

export default function AppSidebar() {
  const pathname = usePathname()
  const router = useRouter()
  const { conversations, activeConversationId, selectConversation, startNewConversation, userInfo } = useAppData()
  const { mobileSidebarOpen, setMobileSidebarOpen } = useUIStore()

  const handleLogout = async () => {
    await supabase.auth.signOut()
    router.push('/login')
  }

  const handleNewConversation = () => {
    startNewConversation()
    router.push('/app/chat')
  }

  const handleSelectConversation = (id: string) => {
    selectConversation(id)
    router.push('/app/chat')
    setMobileSidebarOpen(false)
  }

  const sidebarContent = (
    <>
      {/* Pattern background */}
      <div className="absolute inset-0 opacity-[0.02]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
      }} />

      {/* Header */}
      <div className="p-6 border-b border-white/10 relative z-10">
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3.5">
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
          {/* Close button — mobile only */}
          <button
            onClick={() => setMobileSidebarOpen(false)}
            className="lg:hidden p-1.5 text-white/50 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            aria-label="Fermer le menu"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="bg-white/5 rounded-xl p-3.5 border border-white/10">
          <p className="text-[0.65rem] text-white/40 uppercase tracking-wider mb-1">
            Connecte en tant que
          </p>
          <h3 className="font-serif text-base text-white font-medium">
            {userInfo ? `Me ${userInfo.prenom} ${userInfo.nom}` : 'Chargement...'}
          </h3>
        </div>
      </div>

      {/* New conversation button + conversations list */}
      <div className="p-4 flex-1 relative z-10 flex flex-col min-h-0 overflow-y-auto">
        <button
          onClick={handleNewConversation}
          className="flex items-center gap-2.5 w-full px-3.5 py-3 mb-3 bg-gold/15 text-gold-light rounded-xl cursor-pointer hover:bg-gold/25 transition-all text-[0.85rem] font-medium"
        >
          <Plus className="w-[18px] h-[18px]" />
          Nouveau dossier
        </button>

        {/* Conversations */}
        {conversations.length > 0 && (
          <div className="mb-4">
            <p className="text-[0.65rem] text-white/35 uppercase tracking-widest px-2 mb-2.5">
              Dossiers en cours
            </p>
            <div className="flex flex-col gap-0.5 overflow-y-auto max-h-[200px] scrollbar-thin">
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`flex items-start gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all text-left w-full ${
                    conv.id === activeConversationId && pathname === '/app/chat'
                      ? 'bg-gold/15 text-gold-light'
                      : 'text-white/70 hover:bg-white/10 hover:text-white'
                  }`}
                >
                  <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0 opacity-70" />
                  <div className="flex-1 min-w-0">
                    <p className="text-[0.8rem] truncate">{conv.title}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[0.65rem] opacity-50">
                        {timeAgo(conv.updated_at)}
                      </span>
                      {conv.progress_pct != null && conv.progress_pct > 0 && (
                        <span className="text-[0.6rem] text-gold/80">
                          {Math.round(conv.progress_pct)}%
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Espace Notaire */}
        <div className="mb-4">
          <p className="text-[0.65rem] text-white/35 uppercase tracking-widest px-2 mb-2.5">
            Espace Notaire
          </p>
          <NavLink href="/app" icon={LayoutDashboard} label="Dashboard" exact />
          <NavLink href="/app/chat" icon={MessageSquare} label="Chat IA" />
          <NavLink href="/app/dossiers" icon={FolderOpen} label="Mes Dossiers" />
          <NavLink href="/app/documents" icon={FileText} label="Mes Documents" />
          <NavLink href="/app/clients" icon={Users} label="Mes Clients" />
          <NavLink href="/app/workflow" icon={ClipboardList} label="Workflow guide" />
        </div>

        {/* References */}
        <div className="mb-4">
          <p className="text-[0.65rem] text-white/35 uppercase tracking-widest px-2 mb-2.5">
            References
          </p>
          <NavItem icon={HelpCircle} label="Code civil" disabled />
          <NavItem icon={Book} label="Modeles" disabled />
        </div>
      </div>

      {/* Footer */}
      <div className="p-5 border-t border-white/10 relative z-10">
        <button
          onClick={handleLogout}
          className="flex items-center gap-2.5 w-full px-3.5 py-3 rounded-xl text-white/60 hover:bg-white/10 hover:text-white transition-all text-[0.85rem] mb-3"
        >
          <LogOut className="w-[18px] h-[18px]" />
          Deconnexion
        </button>
        <div className="flex items-center gap-2.5 p-3 bg-white/[0.03] rounded-xl border border-white/5">
          <Shield className="w-5 h-5 text-gold" />
          <div className="text-[0.7rem] text-white/50 leading-tight">
            <strong className="text-white/80 block">Conforme RGPD</strong>
            Donnees chiffrees AES-256
          </div>
        </div>
      </div>
    </>
  )

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className="hidden lg:flex bg-navy w-[280px] flex-col relative overflow-hidden flex-shrink-0"
        role="navigation"
        aria-label="Navigation principale"
      >
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {mobileSidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-black/50"
          onClick={() => setMobileSidebarOpen(false)}
        >
          <aside
            className="bg-navy w-[280px] h-full flex flex-col relative overflow-hidden animate-slide-in-right"
            onClick={(e) => e.stopPropagation()}
            role="navigation"
            aria-label="Navigation principale"
          >
            {sidebarContent}
          </aside>
        </div>
      )}
    </>
  )
}

function NavItem({
  icon: Icon,
  label,
  disabled,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  disabled?: boolean
}) {
  return (
    <div
      className={`flex items-center gap-3 px-3.5 py-3 rounded-xl transition-all mb-1 ${
        disabled
          ? 'text-white/30 cursor-not-allowed'
          : 'text-white/70 cursor-pointer hover:bg-white/10 hover:text-white'
      }`}
      title={disabled ? 'Bientot disponible' : undefined}
    >
      <Icon className="w-[18px] h-[18px] opacity-70" />
      <span className="text-[0.85rem]">{label}</span>
    </div>
  )
}

function NavLink({
  href,
  icon: Icon,
  label,
  exact,
}: {
  href: string
  icon: React.ComponentType<{ className?: string }>
  label: string
  exact?: boolean
}) {
  const pathname = usePathname()
  const isActive = exact ? pathname === href : (pathname?.startsWith(href) ?? false)

  return (
    <Link
      href={href}
      className={`flex items-center gap-3 px-3.5 py-3 rounded-xl transition-all mb-1 ${
        isActive
          ? 'bg-gold/15 text-gold-light'
          : 'text-white/70 hover:bg-white/10 hover:text-white'
      }`}
    >
      <Icon className="w-[18px] h-[18px] opacity-70" />
      <span className="text-[0.85rem]">{label}</span>
    </Link>
  )
}
