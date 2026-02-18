'use client'

import { FileText, FileCheck, Building, FilePen, Download, Award } from 'lucide-react'
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

  const handleSelectType = async (type: TypeActe) => {
    await startWorkflow(type)
  }

  const handleBack = () => {
    reset()
    onBack?.()
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
