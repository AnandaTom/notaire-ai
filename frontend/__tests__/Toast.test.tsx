import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ToastContainer } from '@/components/Toast'
import { useUIStore } from '@/stores/uiStore'

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  CheckCircle2: ({ className }: { className?: string }) => <span data-testid="icon-success" className={className} />,
  Info: ({ className }: { className?: string }) => <span data-testid="icon-info" className={className} />,
  AlertTriangle: ({ className }: { className?: string }) => <span data-testid="icon-warning" className={className} />,
  XCircle: ({ className }: { className?: string }) => <span data-testid="icon-error" className={className} />,
  X: ({ className }: { className?: string }) => <span data-testid="icon-close" className={className} />,
}))

describe('ToastContainer', () => {
  beforeEach(() => {
    // Reset store between tests
    useUIStore.setState({ toasts: [] })
  })

  it('renders nothing when no toasts', () => {
    const { container } = render(<ToastContainer />)
    expect(container.innerHTML).toBe('')
  })

  it('renders a success toast', () => {
    useUIStore.setState({
      toasts: [{ id: '1', type: 'success', message: 'Acte genere avec succes' }],
    })
    render(<ToastContainer />)
    expect(screen.getByText('Acte genere avec succes')).toBeInTheDocument()
    expect(screen.getByTestId('icon-success')).toBeInTheDocument()
  })

  it('renders an error toast', () => {
    useUIStore.setState({
      toasts: [{ id: '2', type: 'error', message: 'Erreur de connexion' }],
    })
    render(<ToastContainer />)
    expect(screen.getByText('Erreur de connexion')).toBeInTheDocument()
    expect(screen.getByTestId('icon-error')).toBeInTheDocument()
  })

  it('renders multiple toasts', () => {
    useUIStore.setState({
      toasts: [
        { id: '1', type: 'success', message: 'Premier toast' },
        { id: '2', type: 'warning', message: 'Second toast' },
      ],
    })
    render(<ToastContainer />)
    expect(screen.getByText('Premier toast')).toBeInTheDocument()
    expect(screen.getByText('Second toast')).toBeInTheDocument()
  })

  it('removes toast on close button click', () => {
    const removeToast = vi.fn()
    useUIStore.setState({
      toasts: [{ id: '42', type: 'info', message: 'Info toast' }],
      removeToast,
    })
    render(<ToastContainer />)
    const closeBtn = screen.getByLabelText('Fermer la notification')
    fireEvent.click(closeBtn)
    expect(removeToast).toHaveBeenCalledWith('42')
  })

  it('has correct aria attributes', () => {
    useUIStore.setState({
      toasts: [{ id: '1', type: 'success', message: 'Test aria' }],
    })
    render(<ToastContainer />)
    expect(screen.getByRole('region')).toHaveAttribute('aria-label', 'Notifications')
    expect(screen.getByRole('alert')).toBeInTheDocument()
  })
})
