'use client'

import { CheckCircle2, Info, AlertTriangle, XCircle, X } from 'lucide-react'
import { useUIStore, type Toast } from '@/stores/uiStore'

const ICONS: Record<Toast['type'], React.ComponentType<{ className?: string }>> = {
  success: CheckCircle2,
  info: Info,
  warning: AlertTriangle,
  error: XCircle,
}

const STYLES: Record<Toast['type'], string> = {
  success: 'bg-success-light border-success/30 text-success',
  info: 'bg-info-light border-info/30 text-info',
  warning: 'bg-warning-light border-warning/30 text-warning',
  error: 'bg-error-light border-error/30 text-error',
}

export function ToastContainer() {
  const { toasts, removeToast } = useUIStore()

  if (toasts.length === 0) return null

  return (
    <div
      className="fixed bottom-6 right-6 z-50 flex flex-col gap-2.5 max-w-sm"
      role="region"
      aria-label="Notifications"
    >
      {toasts.map((toast) => {
        const Icon = ICONS[toast.type]
        return (
          <div
            key={toast.id}
            className={`flex items-start gap-3 px-4 py-3 border rounded-xl shadow-lg animate-scale-in ${STYLES[toast.type]}`}
            role="alert"
            aria-live="assertive"
          >
            <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <p className="text-[0.85rem] flex-1">{toast.message}</p>
            <button
              onClick={() => removeToast(toast.id)}
              className="flex-shrink-0 p-0.5 opacity-60 hover:opacity-100 transition-opacity"
              aria-label="Fermer la notification"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )
      })}
    </div>
  )
}
