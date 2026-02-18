import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock supabase before importing auth
vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      getUser: vi.fn(),
    },
    from: vi.fn(),
  },
}))

import { getUserEtudeId } from '@/lib/auth'
import { supabase } from '@/lib/supabase'

const mockGetUser = supabase.auth.getUser as ReturnType<typeof vi.fn>
const mockFrom = supabase.from as ReturnType<typeof vi.fn>

describe('getUserEtudeId', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns etude_id when user is authenticated', async () => {
    mockGetUser.mockResolvedValue({
      data: { user: { id: 'user-123' } },
    })
    mockFrom.mockReturnValue({
      select: vi.fn().mockReturnValue({
        eq: vi.fn().mockReturnValue({
          single: vi.fn().mockResolvedValue({
            data: { etude_id: 'etude-abc' },
          }),
        }),
      }),
    })

    const result = await getUserEtudeId()
    expect(result).toBe('etude-abc')
    expect(mockFrom).toHaveBeenCalledWith('notaire_users')
  })

  it('returns null when no user is logged in', async () => {
    mockGetUser.mockResolvedValue({
      data: { user: null },
    })

    const result = await getUserEtudeId()
    expect(result).toBeNull()
  })

  it('returns null when etude_id is missing', async () => {
    mockGetUser.mockResolvedValue({
      data: { user: { id: 'user-123' } },
    })
    mockFrom.mockReturnValue({
      select: vi.fn().mockReturnValue({
        eq: vi.fn().mockReturnValue({
          single: vi.fn().mockResolvedValue({
            data: null,
          }),
        }),
      }),
    })

    const result = await getUserEtudeId()
    expect(result).toBeNull()
  })

  it('returns null on error', async () => {
    mockGetUser.mockRejectedValue(new Error('network error'))

    const result = await getUserEtudeId()
    expect(result).toBeNull()
  })
})
