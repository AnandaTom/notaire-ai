import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import CommandPalette from '@/components/CommandPalette'
import { useUIStore } from '@/stores/uiStore'

// Mock next/navigation
const mockPush = vi.fn()
vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}))

// Mock useAppData
vi.mock('@/lib/hooks/useAppData', () => ({
  useAppData: () => ({
    conversations: [
      { id: 'conv-1', title: 'Dossier Martin', type_acte: 'promesse_vente' },
      { id: 'conv-2', title: 'Dossier Dupont', type_acte: 'vente' },
    ],
    selectConversation: vi.fn(),
  }),
}))

// Mock lucide-react with minimal stubs
vi.mock('lucide-react', () => {
  const Stub = ({ className }: { className?: string }) => <span className={className} />
  return {
    Search: Stub,
    LayoutDashboard: Stub,
    MessageSquare: Stub,
    FolderOpen: Stub,
    FileText: Stub,
    Users: Stub,
    ClipboardList: Stub,
    Plus: Stub,
    ArrowRight: Stub,
  }
})

describe('CommandPalette', () => {
  beforeEach(() => {
    mockPush.mockClear()
    useUIStore.setState({ commandPaletteOpen: false })
  })

  it('renders nothing when closed', () => {
    const { container } = render(<CommandPalette />)
    expect(container.innerHTML).toBe('')
  })

  it('renders when open', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    expect(screen.getByPlaceholderText(/Rechercher une page/)).toBeInTheDocument()
  })

  it('shows navigation items', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
    expect(screen.getByText('Chat IA')).toBeInTheDocument()
    expect(screen.getByText('Mes Dossiers')).toBeInTheDocument()
    expect(screen.getByText('Mes Clients')).toBeInTheDocument()
  })

  it('shows action items', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    expect(screen.getByText('Nouvelle promesse de vente')).toBeInTheDocument()
    expect(screen.getByText('Nouvel acte de vente')).toBeInTheDocument()
  })

  it('shows recent conversations', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    expect(screen.getByText('Dossier Martin')).toBeInTheDocument()
    expect(screen.getByText('Dossier Dupont')).toBeInTheDocument()
  })

  it('filters items by query', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    const input = screen.getByPlaceholderText(/Rechercher une page/)
    fireEvent.change(input, { target: { value: 'Martin' } })
    expect(screen.getByText('Dossier Martin')).toBeInTheDocument()
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
  })

  it('shows empty state for no results', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    const input = screen.getByPlaceholderText(/Rechercher une page/)
    fireEvent.change(input, { target: { value: 'zzzznonexistent' } })
    expect(screen.getByText(/Aucun resultat/)).toBeInTheDocument()
  })

  it('navigates on Enter key', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    const input = screen.getByPlaceholderText(/Rechercher une page/)
    // First item is Dashboard — press Enter to navigate
    fireEvent.keyDown(input, { key: 'Enter' })
    expect(mockPush).toHaveBeenCalledWith('/app')
  })

  it('closes on backdrop click', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    // The backdrop is the outermost div
    const backdrop = screen.getByPlaceholderText(/Rechercher une page/).closest('.fixed')!
    fireEvent.click(backdrop)
    expect(useUIStore.getState().commandPaletteOpen).toBe(false)
  })

  it('has keyboard shortcut hints in footer', () => {
    useUIStore.setState({ commandPaletteOpen: true })
    render(<CommandPalette />)
    expect(screen.getByText('naviguer')).toBeInTheDocument()
    expect(screen.getByText('ouvrir')).toBeInTheDocument()
    expect(screen.getByText('fermer')).toBeInTheDocument()
  })
})
