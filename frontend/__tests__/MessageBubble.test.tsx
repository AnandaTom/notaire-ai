import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import MessageBubble from '@/components/MessageBubble'
import type { Message } from '@/types'

// Mock react-markdown to avoid ESM issues in test env
vi.mock('react-markdown', () => ({
  default: ({ children }: { children: string }) => <div data-testid="markdown">{children}</div>,
}))

// Mock config
vi.mock('@/lib/config', () => ({
  API_URL: 'http://localhost:8000',
}))

function makeMessage(overrides: Partial<Message> = {}): Message {
  return {
    id: 'msg-1',
    role: 'assistant',
    content: 'Bonjour, comment puis-je vous aider ?',
    timestamp: new Date(),
    ...overrides,
  }
}

describe('MessageBubble', () => {
  const defaultProps = {
    messageIndex: 0,
    onFeedback: vi.fn(),
  }

  it('renders assistant message with markdown', () => {
    render(
      <MessageBubble
        message={makeMessage()}
        {...defaultProps}
      />
    )
    expect(screen.getByTestId('markdown')).toHaveTextContent('Bonjour')
  })

  it('renders user message as plain text', () => {
    render(
      <MessageBubble
        message={makeMessage({ role: 'user', content: 'Generer une promesse' })}
        {...defaultProps}
      />
    )
    expect(screen.getByText('Generer une promesse')).toBeInTheDocument()
  })

  it('shows feedback buttons for non-welcome assistant messages', () => {
    render(
      <MessageBubble
        message={makeMessage({ id: 'msg-2' })}
        {...defaultProps}
      />
    )
    expect(screen.getByTitle('Utile')).toBeInTheDocument()
    expect(screen.getByTitle('Pas utile')).toBeInTheDocument()
  })

  it('does not show feedback buttons for user messages', () => {
    render(
      <MessageBubble
        message={makeMessage({ role: 'user' })}
        {...defaultProps}
      />
    )
    expect(screen.queryByTitle('Utile')).not.toBeInTheDocument()
  })

  it('calls onFeedback with positive rating', () => {
    const onFeedback = vi.fn()
    render(
      <MessageBubble
        message={makeMessage({ id: 'msg-2' })}
        messageIndex={3}
        onFeedback={onFeedback}
      />
    )
    fireEvent.click(screen.getByTitle('Utile'))
    expect(onFeedback).toHaveBeenCalledWith(3, 1)
  })

  it('calls onFeedback with negative rating', () => {
    const onFeedback = vi.fn()
    render(
      <MessageBubble
        message={makeMessage({ id: 'msg-2' })}
        messageIndex={3}
        onFeedback={onFeedback}
      />
    )
    fireEvent.click(screen.getByTitle('Pas utile'))
    expect(onFeedback).toHaveBeenCalledWith(3, -1)
  })

  it('shows download link when fichier_url is present', () => {
    render(
      <MessageBubble
        message={makeMessage({
          metadata: { fichier_url: '/download/acte.docx' },
        })}
        {...defaultProps}
      />
    )
    const link = screen.getByText('Télécharger le document')
    expect(link).toBeInTheDocument()
    expect(link.closest('a')).toHaveAttribute(
      'href',
      'http://localhost:8000/download/acte.docx'
    )
  })

  it('shows section badge when section is provided', () => {
    render(
      <MessageBubble
        message={makeMessage({ section: 'Vendeur' })}
        {...defaultProps}
      />
    )
    expect(screen.getByText('Vendeur')).toBeInTheDocument()
  })

  it('shows quick actions when provided', () => {
    const onQuickAction = vi.fn()
    const DummyIcon = ({ className }: { className?: string }) => <span className={className}>icon</span>
    render(
      <MessageBubble
        message={makeMessage({ id: '1' })}
        quickActions={[{ icon: DummyIcon, label: 'Acte de vente' }]}
        onQuickAction={onQuickAction}
        {...defaultProps}
      />
    )
    const btn = screen.getByText('Acte de vente')
    expect(btn).toBeInTheDocument()
    fireEvent.click(btn)
    expect(onQuickAction).toHaveBeenCalledWith('Acte de vente')
  })

  it('shows legal reference on welcome message', () => {
    render(
      <MessageBubble
        message={makeMessage({ id: '1' })}
        {...defaultProps}
      />
    )
    expect(screen.getByText(/Art\. 1582/)).toBeInTheDocument()
  })

  it('does not show feedback for welcome message', () => {
    render(
      <MessageBubble
        message={makeMessage({ id: '1' })}
        {...defaultProps}
      />
    )
    expect(screen.queryByTitle('Utile')).not.toBeInTheDocument()
  })
})
