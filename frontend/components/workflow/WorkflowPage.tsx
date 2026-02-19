'use client'

import { useState, useEffect } from 'react'
import { FileText, FileCheck, Building, FilePen, Download, Award, RotateCcw, Plus } from 'lucide-react'
import { useWorkflowStore } from '@/stores/workflowStore'
import type { TypeActe } from '@/types/workflow'
import WorkflowHeader from './WorkflowHeader'
import WorkflowSidebar from './WorkflowSidebar'
import DynamicForm from './DynamicForm'
import DocumentReview from './DocumentReview'
import GenerationProgress from './GenerationProgress'
import FeedbackPanel from './FeedbackPanel'
import { API_URL } from '@/lib/config'

const TYPE_CARDS: { type: TypeActe; label: string; description: string; icon: typeof FileText }[] = [
  {
    type: 'promesse_vente',
    label: 'Promesse de vente',
    description: 'Promesse unilatérale de vente (copropriété, maison, terrain, viager)',
    icon: FileText,
  },
  {
    type: 'vente',
    label: 'Acte de vente',
    description: 'Acte de vente définitif de lots de copropriété',
    icon: FileCheck,
  },
  {
    type: 'reglement_copropriete',
    label: 'Règlement de copropriété',
    description: 'État descriptif de division et règlement de copropriété',
    icon: Building,
  },
  {
    type: 'modificatif_edd',
    label: 'Modificatif EDD',
    description: 'Modification de l\'état descriptif de division',
    icon: FilePen,
  },
]

const TYPE_LABELS: Record<string, string> = {
  promesse_vente: 'Promesse de vente',
  vente: 'Acte de vente',
  reglement_copropriete: 'Règlement de copropriété',
  modificatif_edd: 'Modificatif EDD',
}

interface WorkflowPageProps {
  onBack?: () => void
  initialType?: TypeActe
}

export default function WorkflowPage({ onBack, initialType }: WorkflowPageProps) {
  const step = useWorkflowStore((s) => s.step)
  const sections = useWorkflowStore((s) => s.sections)
  const currentSectionIndex = useWorkflowStore((s) => s.currentSectionIndex)
  const startWorkflow = useWorkflowStore((s) => s.startWorkflow)
  const goToSection = useWorkflowStore((s) => s.goToSection)
  const setStep = useWorkflowStore((s) => s.setStep)
  const isLoading = useWorkflowStore((s) => s.isLoading)
  const error = useWorkflowStore((s) => s.error)
  const fichierUrl = useWorkflowStore((s) => s.fichierUrl)
  const conformiteScore = useWorkflowStore((s) => s.conformiteScore)
  const workflowId = useWorkflowStore((s) => s.workflowId)
  const reset = useWorkflowStore((s) => s.reset)
  const typeActe = useWorkflowStore((s) => s.typeActe)
  const restoreFromDraft = useWorkflowStore((s) => s.restoreDraft)

  const [showRecovery, setShowRecovery] = useState(false)

  // Warn before leaving with unsaved data
  useEffect(() => {
    if (step !== 'COLLECTING' && step !== 'VALIDATING' && step !== 'REVIEW') return

    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault()
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [step])

  // Check for recoverable draft from localStorage on mount
  useEffect(() => {
    if (step !== 'IDLE') return
    const hasDraft = typeof window !== 'undefined' && !!localStorage.getItem('notomai_workflow_draft')
    if (hasDraft) {
      restoreFromDraft().then((restored) => {
        if (restored) setShowRecovery(true)
      })
    } else if (initialType) {
      // Auto-demarrage si type passe via URL (?type=promesse_vente)
      startWorkflow(initialType)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const handleSelectType = async (type: TypeActe) => {
    await startWorkflow(type)
  }

  const handleBack = () => {
    reset()
    onBack?.()
  }

  const handleDismissRecovery = () => {
    setShowRecovery(false)
  }

  const handleDiscardRecovery = () => {
    reset()
    setShowRecovery(false)
  }

  // ========================================
  // Recovery banner (persisted workflow found)
  // ========================================
  if (showRecovery && (step === 'COLLECTING' || step === 'REVIEW')) {
    return (
      <div className="h-full flex flex-col bg-ivory">
        <WorkflowHeader onBack={handleBack} />
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="max-w-md w-full text-center">
            <div className="w-14 h-14 bg-amber-50 border border-amber-200 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <RotateCcw className="w-7 h-7 text-amber-600" />
            </div>

            <h2 className="text-xl font-serif font-semibold text-charcoal mb-2">
              Workflow en cours
            </h2>
            <p className="text-[0.88rem] text-slate mb-8">
              Un{' '}
              <span className="font-medium text-charcoal">
                {TYPE_LABELS[typeActe || ''] || 'acte'}
              </span>{' '}
              était en cours de saisie. Souhaitez-vous le reprendre ?
            </p>

            <div className="flex gap-3 justify-center">
              <button
                onClick={handleDismissRecovery}
                className="inline-flex items-center gap-2 px-6 py-3 bg-gold text-white rounded-xl text-[0.88rem] font-semibold hover:bg-gold-dark transition-all"
              >
                <RotateCcw className="w-4 h-4" />
                Reprendre
              </button>
              <button
                onClick={handleDiscardRecovery}
                className="inline-flex items-center gap-2 px-6 py-3 bg-cream border border-champagne text-charcoal rounded-xl text-[0.88rem] font-medium hover:bg-sand transition-all"
              >
                <Plus className="w-4 h-4" />
                Nouveau
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // ========================================
  // ECRAN 1 : Selection du type d'acte
  // ========================================
  if (step === 'IDLE' || step === 'TYPE_SELECT') {
    return (
      <div className="h-full flex flex-col bg-ivory">
        <WorkflowHeader onBack={handleBack} />
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="max-w-2xl w-full">
            <h1 className="text-2xl font-serif font-semibold text-charcoal mb-2 text-center">
              Créer un nouvel acte
            </h1>
            <p className="text-[0.88rem] text-slate text-center mb-10">
              Sélectionnez le type d&apos;acte notarial à générer
            </p>

            <div className="grid grid-cols-2 gap-4">
              {TYPE_CARDS.map(({ type, label, description, icon: Icon }) => (
                <button
                  key={type}
                  onClick={() => handleSelectType(type)}
                  disabled={isLoading}
                  className="flex flex-col items-start gap-3 p-6 bg-cream border border-champagne rounded-2xl hover:border-gold hover:bg-sand transition-all text-left group disabled:opacity-50"
                >
                  <div className="w-11 h-11 bg-sand border border-champagne rounded-xl flex items-center justify-center group-hover:bg-gold/10 group-hover:border-gold/30 transition-all">
                    <Icon className="w-5 h-5 text-gold-dark" />
                  </div>
                  <div>
                    <h3 className="text-[0.9rem] font-semibold text-charcoal mb-1">{label}</h3>
                    <p className="text-[0.78rem] text-slate leading-relaxed">{description}</p>
                  </div>
                </button>
              ))}
            </div>

            {error && (
              <div className="mt-6 px-5 py-4 bg-red-50 border border-red-200 rounded-xl text-center">
                <p className="text-[0.85rem] text-red-700">{error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // ========================================
  // ECRAN 2 : Formulaire avec sidebar
  // ========================================
  if (step === 'COLLECTING') {
    const currentSection = sections[currentSectionIndex]

    return (
      <div className="h-full flex flex-col bg-ivory">
        <WorkflowHeader onBack={handleBack} />
        <div className="flex-1 flex min-h-0 overflow-hidden">
          <WorkflowSidebar />
          <div className="flex-1 min-h-0 overflow-hidden">
            {currentSection ? (
              <DynamicForm
                section={currentSection}
                onPrevious={() => goToSection(currentSectionIndex - 1)}
                onNext={() => {}}
                isFirst={currentSectionIndex === 0}
                isLast={currentSectionIndex === sections.length - 1}
              />
            ) : (
              <div className="flex items-center justify-center h-full">
                <p className="text-slate">Chargement des questions...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // ========================================
  // ECRAN 2b : Validation semantique en cours
  // ========================================
  if (step === 'VALIDATING') {
    return (
      <div className="h-full flex flex-col bg-ivory">
        <WorkflowHeader onBack={handleBack} />
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gold mx-auto mb-4" />
            <p className="text-slate text-[0.9rem]">Validation des données en cours...</p>
          </div>
        </div>
      </div>
    )
  }

  // ========================================
  // ECRAN 3 : Relecture
  // ========================================
  if (step === 'REVIEW') {
    return (
      <div className="h-full flex flex-col bg-ivory">
        <WorkflowHeader onBack={handleBack} />
        <div className="flex-1 overflow-y-auto">
          <DocumentReview />
        </div>
      </div>
    )
  }

  // ========================================
  // ECRAN 4 : Generation en cours
  // ========================================
  if (step === 'GENERATING') {
    return (
      <div className="h-full flex flex-col bg-ivory">
        <WorkflowHeader />
        <div className="flex-1 overflow-y-auto">
          <GenerationProgress />
        </div>
      </div>
    )
  }

  // ========================================
  // ECRAN 5 : Termine
  // ========================================
  if (step === 'DONE') {
    return (
      <div className="h-full flex flex-col bg-ivory">
        <WorkflowHeader />
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="max-w-md w-full text-center">
            <div className="w-16 h-16 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Award className="w-8 h-8 text-emerald-600" />
            </div>

            <h2 className="text-xl font-serif font-semibold text-charcoal mb-2">
              Document généré avec succès
            </h2>

            {conformiteScore && (
              <p className="text-[0.9rem] text-emerald-600 font-medium mb-6">
                Conformité : {conformiteScore}%
              </p>
            )}

            {fichierUrl && (
              <a
                href={`${API_URL}${fichierUrl}`}
                download
                className="inline-flex items-center gap-2.5 px-8 py-3.5 bg-gold text-white rounded-xl text-[0.9rem] font-semibold hover:bg-gold-dark transition-all shadow-lg shadow-gold/25 mb-6"
              >
                <Download className="w-5 h-5" />
                Télécharger le DOCX
              </a>
            )}

            <div className="mt-6">
              <FeedbackPanel workflowId={workflowId || undefined} />
            </div>

            <button
              onClick={handleBack}
              className="mt-6 text-[0.82rem] text-slate hover:text-charcoal transition-colors underline"
            >
              Retour à l&apos;accueil
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Fallback
  return null
}
