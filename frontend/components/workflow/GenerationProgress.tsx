'use client'

import { useEffect } from 'react'
import { Check, Loader2, AlertCircle, Download, Award } from 'lucide-react'
import { useWorkflowStore } from '@/stores/workflowStore'
import { GENERATION_STEPS } from '@/lib/constants'
import { API_URL } from '@/lib/config'

export default function GenerationProgress() {
  const generationEvents = useWorkflowStore((s) => s.generationEvents)
  const startGeneration = useWorkflowStore((s) => s.startGeneration)
  const fichierUrl = useWorkflowStore((s) => s.fichierUrl)
  const conformiteScore = useWorkflowStore((s) => s.conformiteScore)
  const error = useWorkflowStore((s) => s.error)

  useEffect(() => {
    startGeneration()
  }, [startGeneration])

  const getStepStatus = (stepId: string) => {
    const event = generationEvents.find((e) => e.etape === stepId)
    if (!event) return 'pending'
    return event.statut
  }

  const completedSteps = generationEvents.filter((e) => e.statut === 'termine').length
  const progressPct = Math.round((completedSteps / GENERATION_STEPS.length) * 100)

  return (
    <div className="max-w-xl mx-auto py-10 px-6">
      <h2 className="text-xl font-serif font-semibold text-charcoal mb-2">
        Génération en cours
      </h2>
      <p className="text-[0.85rem] text-slate mb-8">
        Votre document est en cours de création. Veuillez patienter...
      </p>

      {/* Barre de progression globale */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          <span className="text-[0.75rem] text-slate">Progression</span>
          <span className="text-[0.82rem] font-semibold text-gold-dark">{progressPct}%</span>
        </div>
        <div className="w-full h-3 bg-sand rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-gold to-gold-dark rounded-full transition-all duration-700 ease-out"
            style={{ width: `${progressPct}%` }}
          />
        </div>
      </div>

      {/* Liste etapes */}
      <div className="space-y-3">
        {GENERATION_STEPS.map((step, index) => {
          const status = getStepStatus(step.id)
          return (
            <div
              key={step.id}
              className={`flex items-center gap-4 px-5 py-3.5 rounded-xl border transition-all duration-300 ${
                status === 'termine'
                  ? 'bg-emerald-50 border-emerald-200'
                  : status === 'en_cours'
                  ? 'bg-blue-50 border-blue-200'
                  : status === 'erreur'
                  ? 'bg-red-50 border-red-200'
                  : 'bg-cream border-champagne opacity-50'
              }`}
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0">
                {status === 'termine' ? (
                  <Check className="w-5 h-5 text-emerald-600" />
                ) : status === 'en_cours' ? (
                  <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                ) : status === 'erreur' ? (
                  <AlertCircle className="w-5 h-5 text-red-500" />
                ) : (
                  <div className="w-2.5 h-2.5 bg-champagne rounded-full" />
                )}
              </div>

              <span className={`text-[0.85rem] font-medium ${
                status === 'termine'
                  ? 'text-emerald-700'
                  : status === 'en_cours'
                  ? 'text-blue-700'
                  : status === 'erreur'
                  ? 'text-red-700'
                  : 'text-slate'
              }`}>
                {step.label}
              </span>
            </div>
          )
        })}
      </div>

      {/* Erreur */}
      {error && (
        <div className="mt-6 px-5 py-4 bg-red-50 border border-red-200 rounded-xl">
          <p className="text-[0.85rem] text-red-700">{error}</p>
        </div>
      )}

      {/* Resultat final */}
      {fichierUrl && (
        <div className="mt-8 p-6 bg-emerald-50 border border-emerald-200 rounded-2xl animate-fade-in">
          {conformiteScore && (
            <div className="flex items-center gap-3 mb-4">
              <Award className="w-6 h-6 text-emerald-600" />
              <div>
                <p className="text-[0.85rem] font-semibold text-emerald-700">
                  Score de conformité : {conformiteScore}%
                </p>
                <p className="text-[0.75rem] text-emerald-600">
                  Document conforme à la trame notariale
                </p>
              </div>
            </div>
          )}

          <a
            href={`${API_URL}${fichierUrl}`}
            download
            className="inline-flex items-center gap-2.5 px-6 py-3 bg-emerald-600 text-white rounded-xl text-[0.88rem] font-medium hover:bg-emerald-700 transition-all shadow-md shadow-emerald-200"
          >
            <Download className="w-5 h-5" />
            Télécharger le DOCX
          </a>
        </div>
      )}
    </div>
  )
}
