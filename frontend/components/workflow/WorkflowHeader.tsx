'use client'

import { ArrowLeft, Shield } from 'lucide-react'
import { useWorkflowStore } from '@/stores/workflowStore'
import { TYPE_ACTE_LABELS, CATEGORIE_LABELS, SOUS_TYPE_LABELS, STEP_LABELS } from '@/lib/constants'

interface WorkflowHeaderProps {
  onBack?: () => void
}

export default function WorkflowHeader({ onBack }: WorkflowHeaderProps) {
  const typeActe = useWorkflowStore((s) => s.typeActe)
  const detection = useWorkflowStore((s) => s.detection)
  const progression = useWorkflowStore((s) => s.progression)
  const step = useWorkflowStore((s) => s.step)

  const typeLabel = typeActe ? TYPE_ACTE_LABELS[typeActe]?.label : ''
  const categorieLabel = detection?.categorie_bien ? CATEGORIE_LABELS[detection.categorie_bien] : ''
  const sousTypeLabel = detection?.sous_type ? SOUS_TYPE_LABELS[detection.sous_type] : ''

  return (
    <div className="px-6 py-3.5 bg-cream border-b border-champagne flex items-center gap-4">
      {/* Retour */}
      {onBack && (
        <button
          onClick={onBack}
          className="p-2 text-slate hover:text-charcoal hover:bg-sand rounded-lg transition-all"
          aria-label="Retour au chat"
        >
          <ArrowLeft className="w-4.5 h-4.5" />
        </button>
      )}

      {/* Info acte */}
      <div className="flex items-center gap-3 flex-1 min-w-0">
        {typeLabel && (
          <span className="text-[0.82rem] font-semibold text-charcoal truncate">
            {typeLabel}
          </span>
        )}

        {categorieLabel && (
          <>
            <span className="text-champagne">|</span>
            <span className="px-2.5 py-1 bg-sand border border-champagne rounded-lg text-[0.72rem] font-medium text-graphite">
              {categorieLabel}
            </span>
          </>
        )}

        {sousTypeLabel && sousTypeLabel !== 'Standard' && (
          <span className="px-2.5 py-1 bg-amber-50 border border-amber-200 rounded-lg text-[0.72rem] font-medium text-amber-700">
            {sousTypeLabel}
          </span>
        )}

        {detection?.confiance && (
          <>
            <span className="text-champagne">|</span>
            <div className="flex items-center gap-1">
              <Shield className={`w-3.5 h-3.5 ${
                detection.confiance >= 85 ? 'text-emerald-500' : detection.confiance >= 70 ? 'text-amber-500' : 'text-red-500'
              }`} />
              <span className="text-[0.72rem] text-slate">
                {detection.confiance}%
              </span>
            </div>
          </>
        )}
      </div>

      {/* Progression + Etape */}
      <div className="flex items-center gap-3">
        <span className="text-[0.72rem] text-slate">
          {STEP_LABELS[step]}
        </span>
        <div className="flex items-center gap-2">
          <div className="w-20 h-1.5 bg-sand rounded-full overflow-hidden">
            <div
              className="h-full bg-gold rounded-full transition-all duration-500"
              style={{ width: `${progression.pourcentage}%` }}
            />
          </div>
          <span className="text-[0.75rem] font-semibold text-gold-dark">
            {progression.pourcentage}%
          </span>
        </div>
      </div>
    </div>
  )
}
