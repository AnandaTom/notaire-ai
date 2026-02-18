import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ChatArea from '@/components/ChatArea'
import type { Message } from '@/types'

// Mock next/link
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: { children: React.ReactNode; href: string; [key: string]: unknown }) => (
    <a href={href} {...props}>{children}</a>
  ),
}))

// Mock react-markdown
vi.mock('react-markdown', () => ({
  default: ({ children }: { children: string }) => <div>{children}</div>,
}))

// Mock config
vi.mock('@/lib/config', () => ({
  API_URL: 'http://localhost:8000',
}))

const baseMessages: Message[] = [
  {
    id: '1',
    role: 'assistant',
    content: 'Bienvenue',
    timestamp: new Date(),
  },
]

const defaultProps = {
  messages: baseMessages,
  isLoading: false,
  onSendMessage: vi.fn(),
  selectedFormat: 'docx' as const,
  onFormatChange: vi.fn(),
  onFeedback: vi.fn(),
}

describe('ChatArea', () => {
  it('renders messages', () => {
    render(<ChatArea {...defaultProps} />)
    expect(screen.getByText('Bienvenue')).toBeInTheDocument()
  })

  it('renders the input textarea', () => {
    render(<ChatArea {...defaultProps} />)
    expect(screen.getByPlaceholderText('Rédigez votre message...')).toBeInTheDocument()
  })

  it('calls onSendMessage when form is submitted', () => {
    const onSendMessage = vi.fn()
    render(<ChatArea {...defaultProps} onSendMessage={onSendMessage} />)

    const textarea = screen.getByPlaceholderText('Rédigez votre message...')
    fireEvent.change(textarea, { target: { value: 'Generer un acte' } })
    fireEvent.submit(textarea.closest('form')!)

    expect(onSendMessage).toHaveBeenCalledWith('Generer un acte')
  })

  it('clears input after submitting', () => {
    render(<ChatArea {...defaultProps} />)
    const textarea = screen.getByPlaceholderText('Rédigez votre message...') as HTMLTextAreaElement
    fireEvent.change(textarea, { target: { value: 'Hello' } })
    fireEvent.submit(textarea.closest('form')!)
    expect(textarea.value).toBe('')
  })

  it('does not submit empty messages', () => {
    const onSendMessage = vi.fn()
    render(<ChatArea {...defaultProps} onSendMessage={onSendMessage} />)
    const textarea = screen.getByPlaceholderText('Rédigez votre message...')
    fireEvent.submit(textarea.closest('form')!)
    expect(onSendMessage).not.toHaveBeenCalled()
  })

  it('shows typing indicator when loading and last message is from user', () => {
    const messages: Message[] = [
      ...baseMessages,
      { id: '2', role: 'user', content: 'Hello', timestamp: new Date() },
    ]
    const { container } = render(<ChatArea {...defaultProps} messages={messages} isLoading={true} />)
    // TypingIndicator renders animated dots (span.typing-dot)
    const dots = container.querySelectorAll('.typing-dot')
    expect(dots.length).toBe(3)
  })

  it('shows "Mode guide" link to workflow', () => {
    render(<ChatArea {...defaultProps} />)
    const link = screen.getByText('Mode guide')
    expect(link).toBeInTheDocument()
    expect(link.closest('a')).toHaveAttribute('href', '/app/workflow')
  })

  it('disables submit button when input is empty', () => {
    render(<ChatArea {...defaultProps} />)
    const buttons = screen.getAllByRole('button')
    const submitBtn = buttons.find(b => b.getAttribute('type') === 'submit')
    expect(submitBtn).toBeDisabled()
  })

  it('hides empty assistant placeholder during streaming', () => {
    const messages: Message[] = [
      ...baseMessages,
      { id: '3', role: 'assistant', content: '', timestamp: new Date() },
    ]
    const { container } = render(<ChatArea {...defaultProps} messages={messages} />)
    // The empty message should be skipped (returns null)
    // Only the welcome message should render
    const messageElements = container.querySelectorAll('[class*="animate-fade-in"]')
    expect(messageElements.length).toBe(1)
  })
})
