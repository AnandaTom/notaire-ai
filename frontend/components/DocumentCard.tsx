'use client'

import { FileText, Download, Calendar, Clock, CheckCircle, FileWarning } from 'lucide-react'
import type { ActeGenere } from '@/types'
import { formatDate } from '@/lib/format'
import { API_URL, API_KEY } from '@/lib/config'

interface DocumentCardProps {
  document: ActeGenere
}

const TYPE_LABELS: Record<string, string> = {
  vente: 'Acte de vente',
  promesse_vente: 'Promesse de vente',
  reglement_copropriete: 'Reglement copropriete',
  modificatif_edd: 'Modificatif EDD',
  autre: 'Autre',
}

const STATUS_CONFIG: Record<string, { bg: string; text: string; label: string }> = {
  brouillon: { bg: 'bg-slate/20', text: 'text-slate', label: 'Brouillon' },
  genere: { bg: 'bg-blue-500/20', text: 'text-blue-600', label: 'Genere' },
  valide: { bg: 'bg-green-500/20', text: 'text-green-600', label: 'Valide' },
  signe: { bg: 'bg-emerald-500/20', text: 'text-emerald-700', label: 'Signe' },
  archive: { bg: 'bg-gray-500/20', text: 'text-gray-500', label: 'Archive' },
  annule: { bg: 'bg-red-500/20', text: 'text-red-500', label: 'Annule' },
}

export default function DocumentCard({ document: doc }: DocumentCardProps) {
  const statusStyle = STATUS_CONFIG[doc.status] || STATUS_CONFIG.genere

  const handleDownload = (e: React.MouseEvent, format: 'docx' | 'pdf') => {
    e.stopPropagation()
    const filePath = format === 'docx' ? doc.fichier_docx : doc.fichier_pdf
    if (!filePath) return
    const filename = filePath.split('/').pop() || `acte.${format}`
    const url = `${API_URL}/download/${encodeURIComponent(filename)}${API_KEY ? `?api_key=${API_KEY}` : ''}`
    window.open(url, '_blank')
  }

  return (
    <div className="bg-cream border border-champagne rounded-2xl p-5 hover:border-gold hover:shadow-md transition-all group">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-sand rounded-xl flex items-center justify-center">
            <FileText className="w-5 h-5 text-gold-dark" />
          </div>
          <div>
            <p className="text-[0.7rem] text-slate uppercase tracking-wider">
              {TYPE_LABELS[doc.type_acte] || doc.type_acte}
            </p>
            <p className="font-serif text-base text-charcoal font-semibold leading-tight">
              {doc.nom || doc.reference_interne || `Acte #${doc.id.slice(0, 8)}`}
            </p>
          </div>
        </div>
        <span className={`px-2.5 py-1 rounded-lg text-[0.7rem] font-medium ${statusStyle.bg} ${statusStyle.text}`}>
          {statusStyle.label}
        </span>
      </div>

      {/* Completion bar */}
      {doc.taux_completion != null && (
        <div className="mb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[0.7rem] text-slate">Completion</span>
            <span className="text-[0.7rem] font-medium text-charcoal">{Math.round(doc.taux_completion)}%</span>
          </div>
          <div className="h-1.5 bg-sand rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-gold to-gold-dark rounded-full transition-all"
              style={{ width: `${Math.min(doc.taux_completion, 100)}%` }}
            />
          </div>
        </div>
      )}

      {/* Meta */}
      <div className="flex items-center gap-4 text-[0.75rem] text-slate mb-4">
        <span className="flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5" />
          {formatDate(doc.created_at)}
        </span>
        {doc.temps_generation_ms != null && (
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            {doc.temps_generation_ms < 1000
              ? `${doc.temps_generation_ms}ms`
              : `${(doc.temps_generation_ms / 1000).toFixed(1)}s`}
          </span>
        )}
        {doc.prix_bien != null && (
          <span className="font-medium text-charcoal">
            {doc.prix_bien.toLocaleString('fr-FR')} EUR
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="flex items-center gap-2 pt-3 border-t border-champagne/50">
        {doc.fichier_docx ? (
          <button
            onClick={(e) => handleDownload(e, 'docx')}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gold/10 text-gold-dark rounded-lg text-[0.8rem] font-medium hover:bg-gold/20 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            DOCX
          </button>
        ) : (
          <span className="flex items-center gap-1.5 px-3 py-1.5 text-slate/50 text-[0.8rem]">
            <FileWarning className="w-3.5 h-3.5" />
            Pas de fichier
          </span>
        )}
        {doc.fichier_pdf && (
          <button
            onClick={(e) => handleDownload(e, 'pdf')}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-500/10 text-blue-600 rounded-lg text-[0.8rem] font-medium hover:bg-blue-500/20 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            PDF
          </button>
        )}
        {doc.status === 'valide' || doc.status === 'signe' ? (
          <CheckCircle className="w-4 h-4 text-green-500 ml-auto" />
        ) : null}
      </div>
    </div>
  )
}
