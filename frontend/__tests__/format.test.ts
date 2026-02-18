import { describe, it, expect } from 'vitest'
import { formatDate } from '@/lib/format'

describe('formatDate', () => {
  it('formats a valid ISO date string in French', () => {
    const result = formatDate('2026-02-18T10:00:00Z')
    expect(result).toMatch(/18/)
    expect(result).toMatch(/2026/)
  })

  it('returns em-dash for null', () => {
    expect(formatDate(null)).toBe('\u2014')
  })

  it('returns em-dash for undefined', () => {
    expect(formatDate(undefined)).toBe('\u2014')
  })

  it('returns em-dash for empty string', () => {
    expect(formatDate('')).toBe('\u2014')
  })

  it('returns em-dash for invalid date string', () => {
    expect(formatDate('not-a-date')).toBe('\u2014')
  })

  it('handles date-only strings', () => {
    const result = formatDate('2025-12-25')
    expect(result).toMatch(/25/)
    expect(result).toMatch(/2025/)
  })
})
