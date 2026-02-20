import { create } from 'zustand'

export interface Toast {
  id: string
  type: 'success' | 'info' | 'warning' | 'error'
  message: string
  duration?: number
}

interface UIState {
  sidebarCollapsed: boolean
  mobileSidebarOpen: boolean
  commandPaletteOpen: boolean
  aiPanelOpen: boolean
  aiPanelContext: string | null
  toasts: Toast[]

  toggleSidebar: () => void
  toggleMobileSidebar: () => void
  setMobileSidebarOpen: (open: boolean) => void
  setCommandPaletteOpen: (open: boolean) => void
  toggleAiPanel: () => void
  setAiPanelOpen: (open: boolean) => void
  setAiPanelContext: (ctx: string | null) => void
  addToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
}

const TOAST_DURATIONS: Record<Toast['type'], number> = {
  success: 4000,
  info: 5000,
  warning: 6000,
  error: 8000,
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  mobileSidebarOpen: false,
  commandPaletteOpen: false,
  aiPanelOpen: true,
  aiPanelContext: null,
  toasts: [],

  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  toggleMobileSidebar: () => set((s) => ({ mobileSidebarOpen: !s.mobileSidebarOpen })),
  setMobileSidebarOpen: (open) => set({ mobileSidebarOpen: open }),
  setCommandPaletteOpen: (open) => set({ commandPaletteOpen: open }),
  toggleAiPanel: () => set((s) => ({ aiPanelOpen: !s.aiPanelOpen })),
  setAiPanelOpen: (open) => set({ aiPanelOpen: open }),
  setAiPanelContext: (ctx) => set({ aiPanelContext: ctx }),

  addToast: (toast) => {
    const id = crypto.randomUUID()
    const duration = toast.duration ?? TOAST_DURATIONS[toast.type]
    set((s) => ({ toasts: [...s.toasts, { ...toast, id }] }))
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
    }, duration)
  },

  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))
