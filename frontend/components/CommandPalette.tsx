'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import {
  Search,
  LayoutDashboard,
  MessageSquare,
  FolderOpen,
  FileText,
  Users,
  ClipboardList,
  Plus,
  ArrowRight,
} from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { useAppData } from '@/lib/hooks/useAppData'

interface CommandItem {
  id: string
  label: string
  description?: string
  icon: React.ComponentType<{ className?: string }>
  action: () => void
  section: string
}

export default function CommandPalette() {
  const router = useRouter()
  const { commandPaletteOpen, setCommandPaletteOpen } = useUIStore()
  const { conversations, selectConversation } = useAppData()
  const [query, setQuery] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)

  const navigate = useCallback((path: string) => {
    setCommandPaletteOpen(false)
    router.push(path)
  }, [router, setCommandPaletteOpen])

  // Navigation items
  const navItems: CommandItem[] = [
    { id: 'nav-dashboard', label: 'Dashboard', icon: LayoutDashboard, action: () => navigate('/app'), section: 'Navigation' },
    { id: 'nav-chat', label: 'Chat IA', icon: MessageSquare, action: () => navigate('/app/chat'), section: 'Navigation' },
    { id: 'nav-dossiers', label: 'Mes Dossiers', icon: FolderOpen, action: () => navigate('/app/dossiers'), section: 'Navigation' },
    { id: 'nav-documents', label: 'Mes Documents', icon: FileText, action: () => navigate('/app/documents'), section: 'Navigation' },
    { id: 'nav-clients', label: 'Mes Clients', icon: Users, action: () => navigate('/app/clients'), section: 'Navigation' },
    { id: 'nav-workflow', label: 'Workflow guide', icon: ClipboardList, action: () => navigate('/app/workflow'), section: 'Navigation' },
  ]

  // Action items
  const actionItems: CommandItem[] = [
    { id: 'act-promesse', label: 'Nouvelle promesse de vente', description: 'Copropriete, maison, terrain', icon: Plus, action: () => navigate('/app/workflow?type=promesse_vente'), section: 'Actions' },
    { id: 'act-vente', label: 'Nouvel acte de vente', description: 'Vente definitive', icon: Plus, action: () => navigate('/app/workflow?type=vente'), section: 'Actions' },
    { id: 'act-new-chat', label: 'Nouvelle conversation', icon: MessageSquare, action: () => navigate('/app/chat'), section: 'Actions' },
  ]

  // Recent conversations
  const conversationItems: CommandItem[] = conversations.slice(0, 5).map((conv) => ({
    id: `conv-${conv.id}`,
    label: conv.title,
    description: conv.type_acte || undefined,
    icon: MessageSquare,
    action: () => {
      selectConversation(conv.id)
      navigate('/app/chat')
    },
    section: 'Dossiers recents',
  }))

  const allItems = [...navItems, ...actionItems, ...conversationItems]

  const filtered = query.trim()
    ? allItems.filter((item) =>
        item.label.toLowerCase().includes(query.toLowerCase()) ||
        item.description?.toLowerCase().includes(query.toLowerCase())
      )
    : allItems

  // Group by section
  const sections: Record<string, CommandItem[]> = {}
  for (const item of filtered) {
    if (!sections[item.section]) sections[item.section] = []
    sections[item.section].push(item)
  }

  // Keyboard shortcut to open/close
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        setCommandPaletteOpen(!commandPaletteOpen)
      }
      if (e.key === 'Escape' && commandPaletteOpen) {
        setCommandPaletteOpen(false)
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [commandPaletteOpen, setCommandPaletteOpen])

  // Focus input when opened
  useEffect(() => {
    if (commandPaletteOpen) {
      setQuery('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 50)
    }
  }, [commandPaletteOpen])

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setSelectedIndex((prev) => Math.min(prev + 1, filtered.length - 1))
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setSelectedIndex((prev) => Math.max(prev - 1, 0))
    } else if (e.key === 'Enter' && filtered[selectedIndex]) {
      e.preventDefault()
      filtered[selectedIndex].action()
    }
  }

  // Reset selection when query changes
  useEffect(() => {
    setSelectedIndex(0)
  }, [query])

  if (!commandPaletteOpen) return null

  let flatIndex = -1

  return (
    <div
      className="fixed inset-0 z-50 bg-black/50 flex items-start justify-center pt-[15vh]"
      onClick={() => setCommandPaletteOpen(false)}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden animate-scale-in border border-champagne"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search input */}
        <div className="flex items-center gap-3 px-5 py-4 border-b border-champagne">
          <Search className="w-5 h-5 text-slate flex-shrink-0" />
          <input
            ref={inputRef}
            type="text"
            placeholder="Rechercher une page, un dossier, une action..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 text-[0.9rem] text-charcoal placeholder:text-slate/50 focus:outline-none bg-transparent"
            aria-label="Recherche rapide"
          />
          <kbd className="px-2 py-1 bg-sand rounded text-[0.65rem] text-slate font-mono">
            Esc
          </kbd>
        </div>

        {/* Results */}
        <div className="max-h-[50vh] overflow-y-auto py-2">
          {filtered.length === 0 ? (
            <div className="px-5 py-8 text-center">
              <p className="text-slate text-[0.85rem]">Aucun resultat pour "{query}"</p>
            </div>
          ) : (
            Object.entries(sections).map(([section, items]) => (
              <div key={section}>
                <p className="px-5 py-1.5 text-[0.65rem] text-slate/70 uppercase tracking-widest font-medium">
                  {section}
                </p>
                {items.map((item) => {
                  flatIndex++
                  const isSelected = flatIndex === selectedIndex
                  const currentIndex = flatIndex
                  return (
                    <button
                      key={item.id}
                      onClick={item.action}
                      onMouseEnter={() => setSelectedIndex(currentIndex)}
                      className={`flex items-center gap-3 w-full px-5 py-2.5 text-left transition-colors ${
                        isSelected ? 'bg-gold/10' : 'hover:bg-sand/50'
                      }`}
                    >
                      <item.icon className={`w-4 h-4 flex-shrink-0 ${isSelected ? 'text-gold-dark' : 'text-slate'}`} />
                      <div className="flex-1 min-w-0">
                        <p className={`text-[0.85rem] truncate ${isSelected ? 'text-gold-dark font-medium' : 'text-charcoal'}`}>
                          {item.label}
                        </p>
                        {item.description && (
                          <p className="text-[0.72rem] text-slate truncate">{item.description}</p>
                        )}
                      </div>
                      {isSelected && <ArrowRight className="w-3.5 h-3.5 text-gold-dark flex-shrink-0" />}
                    </button>
                  )
                })}
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-5 py-2.5 border-t border-champagne bg-cream/50 flex items-center gap-4 text-[0.65rem] text-slate">
          <span><kbd className="px-1.5 py-0.5 bg-sand rounded font-mono">↑↓</kbd> naviguer</span>
          <span><kbd className="px-1.5 py-0.5 bg-sand rounded font-mono">Enter</kbd> ouvrir</span>
          <span><kbd className="px-1.5 py-0.5 bg-sand rounded font-mono">Esc</kbd> fermer</span>
        </div>
      </div>
    </div>
  )
}
