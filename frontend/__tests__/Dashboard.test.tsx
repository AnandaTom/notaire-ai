import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import DashboardPage from '@/app/app/page'

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string; [key: string]: unknown }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

// Mock lucide-react
vi.mock('lucide-react', () => {
  const Stub = ({ className }: { className?: string }) => <span className={className} />
  return {
    MessageSquare: Stub,
    ClipboardList: Stub,
    FileText: Stub,
    FolderOpen: Stub,
    ArrowRight: Stub,
    TrendingUp: Stub,
    Clock: Stub,
    CheckCircle2: Stub,
  }
})

// Mock useAppData
vi.mock('@/lib/hooks/useAppData', () => ({
  useAppData: () => ({
    userInfo: { prenom: 'Jean', nom: 'Dupont', role: 'notaire' },
  }),
}))

// Mock getDashboardStats
const mockGetDashboardStats = vi.fn()
vi.mock('@/lib/api', () => ({
  getDashboardStats: (...args: unknown[]) => mockGetDashboardStats(...args),
}))

describe('DashboardPage', () => {
  beforeEach(() => {
    mockGetDashboardStats.mockReset()
  })

  it('shows greeting with user name', async () => {
    mockGetDashboardStats.mockResolvedValue({
      total_dossiers: 0,
      dossiers_en_cours: 0,
      dossiers_termines: 0,
      actes_generes: 0,
      recent_dossiers: [],
    })
    render(<DashboardPage />)
    // Greeting depends on time, but name should always appear
    await waitFor(() => {
      expect(screen.getByText(/Maitre Jean/)).toBeInTheDocument()
    })
  })

  it('shows quick actions', async () => {
    mockGetDashboardStats.mockResolvedValue({
      total_dossiers: 0,
      dossiers_en_cours: 0,
      dossiers_termines: 0,
      actes_generes: 0,
      recent_dossiers: [],
    })
    render(<DashboardPage />)
    expect(screen.getByText('Promesse de vente')).toBeInTheDocument()
    expect(screen.getByText('Acte de vente')).toBeInTheDocument()
    expect(screen.getByText('Chat IA')).toBeInTheDocument()
    expect(screen.getByText('Workflow guide')).toBeInTheDocument()
  })

  it('displays stats from API', async () => {
    mockGetDashboardStats.mockResolvedValue({
      total_dossiers: 12,
      dossiers_en_cours: 5,
      dossiers_termines: 7,
      actes_generes: 23,
      recent_dossiers: [],
    })
    render(<DashboardPage />)
    await waitFor(() => {
      expect(screen.getByText('12')).toBeInTheDocument()
      expect(screen.getByText('5')).toBeInTheDocument()
      expect(screen.getByText('7')).toBeInTheDocument()
      expect(screen.getByText('23')).toBeInTheDocument()
    })
  })

  it('renders recent dossiers', async () => {
    mockGetDashboardStats.mockResolvedValue({
      total_dossiers: 1,
      dossiers_en_cours: 1,
      dossiers_termines: 0,
      actes_generes: 0,
      recent_dossiers: [
        {
          id: 'dos-1',
          numero: 'DOS-2026-001',
          type_acte: 'promesse_vente',
          statut: 'en_cours',
          parties: [{ nom: 'Martin', prenom: 'Pierre' }],
          biens: [{ adresse: '12 rue de la Paix', ville: 'Paris' }],
          updated_at: '2026-02-20T10:00:00Z',
        },
      ],
    })
    render(<DashboardPage />)
    await waitFor(() => {
      expect(screen.getByText('Pierre Martin')).toBeInTheDocument()
      expect(screen.getByText(/12 rue de la Paix/)).toBeInTheDocument()
      expect(screen.getByText('DOS-2026-001')).toBeInTheDocument()
    })
  })

  it('shows empty state when no dossiers', async () => {
    mockGetDashboardStats.mockResolvedValue({
      total_dossiers: 0,
      dossiers_en_cours: 0,
      dossiers_termines: 0,
      actes_generes: 0,
      recent_dossiers: [],
    })
    render(<DashboardPage />)
    await waitFor(() => {
      expect(screen.getByText('Aucun dossier pour le moment')).toBeInTheDocument()
    })
  })

  it('handles API error gracefully', async () => {
    mockGetDashboardStats.mockRejectedValue(new Error('Network error'))
    render(<DashboardPage />)
    // Should show empty state, not crash
    await waitFor(() => {
      expect(screen.getByText('Aucun dossier pour le moment')).toBeInTheDocument()
    })
  })

  it('has a link to dossiers page', async () => {
    mockGetDashboardStats.mockResolvedValue({
      total_dossiers: 0,
      dossiers_en_cours: 0,
      dossiers_termines: 0,
      actes_generes: 0,
      recent_dossiers: [],
    })
    render(<DashboardPage />)
    const voirTout = screen.getByText('Voir tout')
    expect(voirTout.closest('a')).toHaveAttribute('href', '/app/dossiers')
  })
})
