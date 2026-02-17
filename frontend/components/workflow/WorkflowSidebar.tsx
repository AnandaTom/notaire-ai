'use client'

import { Check, Circle, AlertCircle } from 'lucide-react'
import { useWorkflowStore } from '@/stores/workflowStore'
import type { SectionStatus } from '@/types/workflow'
import { SECTION_STATUS_COLORS } from '@/lib/constants'

export default function WorkflowSidebar() {
  const sections = useWorkflowStore((s) => s.sections)
  const currentSectionIndex = useWorkflowStore((s) => s.currentSectionIndex)
  const progression = useWorkflowStore((s) => s.progression)
  const goToSection = useWorkflowStore((s) => s.goToSection)
  const step = useWorkflowStore((s) => s.step)

  const getSectionStatus = (index: number): SectionStatus => {
    if (index < currentSectionIndex) return 'complete'
    if (index === currentSectionIndex && step === 'COLLECTING') return 'current'
    return 'todo'
  }

  const StatusIcon = ({ status }: { status: SectionStatus }) => {
    switch (status) {
      case 'complete':
        return <Check className="w-4 h-4" />
      case 'current':
        return <Circle className="w-4 h-4 fill-current" />
      case 'error':
        return <AlertCircle className="w-4 h-4" />
      default:
        return <Circle className="w-4 h-4" />
    }
  }

  return (
    <div className="w-[260px] bg-cream border-r border-champagne flex flex-col h-full">
      {/* Progression globale */}
      <div className="px-5 py-5 border-b border-champagne">
        <div className="flex items-center justify-between mb-2">
          <span className="text-[0.75rem] font-semibold text-graphite uppercase tracking-wider">Progression</span>
          <span className="text-[0.82rem] font-semibold text-gold-dark">
            {progression.pourcentage}%
          </span>
        </div>
        <div className="w-full h-2 bg-sand rounded-full overflow-hidden">
          <div
            className="h-full bg-gold rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progression.pourcentage}%` }}
          />
        </div>
        <p className="text-[0.72rem] text-slate mt-1.5">
          {progression.sections_completes}/{progression.sections_total} sections
        </p>
      </div>

      {/* Liste sections */}
      <div className="flex-1 overflow-y-auto py-2">
        {sections.map((section, index) => {
          const status = getSectionStatus(index)
          const colors = SECTION_STATUS_COLORS[status]
          const isClickable = status === 'complete' || status === 'current'

          return (
            <button
              key={section.id}
              onClick={() => isClickable && goToSection(index)}
              disabled={!isClickable}
              className={`w-full flex items-center gap-3 px-5 py-3 text-left transition-all ${
                status === 'current'
                  ? 'bg-blue-50/50 border-r-2 border-blue-500'
                  : 'hover:bg-sand/50'
              } ${!isClickable ? 'cursor-default opacity-50' : 'cursor-pointer'}`}
            >
              <div className={`w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 ${colors.bg} ${colors.text} border ${colors.border}`}>
                <StatusIcon status={status} />
              </div>
              <div className="min-w-0">
                <p className={`text-[0.8rem] font-medium truncate ${
                  status === 'current' ? 'text-blue-700' : status === 'complete' ? 'text-emerald-700' : 'text-slate'
                }`}>
                  {section.titre}
                </p>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
