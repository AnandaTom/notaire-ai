'use client'

import { FileText, Users, Calendar, ChevronRight, Clock } from 'lucide-react'
import type { Dossier } from '@/types'
import Link from 'next/link'
import { formatDate } from '@/lib/format'

interface DossierCardProps {
  dossier: Dossier
}

const TYPE_LABELS: Record<string, string> = {
  vente: 'Acte de vente',
  promesse_vente: 'Promesse de vente',
  reglement_copropriete: 'Reglement copropriete',
  modificatif_edd: 'Modificatif EDD',
  autre: 'Autre',
}

const STATUT_COLORS: Record<string, { bg: string; text: string }> = {
  brouillon: { bg: 'bg-slate/20', text: 'text-slate' },
  en_cours: { bg: 'bg-amber-500/20', text: 'text-amber-600' },
  termine: { bg: 'bg-green-500/20', text: 'text-green-600' },
  archive: { bg: 'bg-gray-500/20', text: 'text-gray-500' },
}

export default function DossierCard({ dossier }: DossierCardProps) {
  const statusStyle = STATUT_COLORS[dossier.statut] || STATUT_COLORS.brouillon
  const vendeurs = dossier.parties?.filter((p) => p.role === 'vendeur' || p.role === 'promettant') || []
  const acquereurs = dossier.parties?.filter((p) => p.role === 'acquereur' || p.role === 'beneficiaire') || []

  return (
    <Link href={`/app/dossiers/${dossier.id}`}>
      <div className="bg-cream border border-champagne rounded-2xl p-5 hover:border-gold hover:shadow-md transition-all cursor-pointer group">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-sand rounded-xl flex items-center justify-center">
              <FileText className="w-5 h-5 text-gold-dark" />
            </div>
            <div>
              <p className="text-[0.7rem] text-slate uppercase tracking-wider">
                {TYPE_LABELS[dossier.type_acte] || dossier.type_acte}
              </p>
              <p className="font-serif text-lg text-charcoal font-semibold">
                {dossier.numero || `Dossier #${dossier.id.slice(0, 8)}`}
              </p>
            </div>
          </div>
          <span className={`px-2.5 py-1 rounded-lg text-[0.7rem] font-medium ${statusStyle.bg} ${statusStyle.text}`}>
            {dossier.statut.replace('_', ' ')}
          </span>
        </div>

        {/* Parties */}
        <div className="flex items-center gap-2 mb-3 text-[0.8rem] text-graphite">
          <Users className="w-4 h-4 text-slate" />
          <span>
            {vendeurs.length > 0
              ? vendeurs.map((v) => v.prenom ? `${v.prenom} ${v.nom}` : v.nom).join(', ')
              : 'Vendeur non defini'}
          </span>
          <span className="text-slate mx-1">→</span>
          <span>
            {acquereurs.length > 0
              ? acquereurs.map((a) => a.prenom ? `${a.prenom} ${a.nom}` : a.nom).join(', ')
              : 'Acquereur non defini'}
          </span>
        </div>

        {/* Bien */}
        {dossier.biens && dossier.biens[0] && (
          <div className="text-[0.8rem] text-slate mb-3">
            {dossier.biens[0].adresse && `${dossier.biens[0].adresse}, `}
            {dossier.biens[0].ville}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-champagne/50">
          <div className="flex items-center gap-4 text-[0.75rem] text-slate">
            <span className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              {formatDate(dossier.created_at)}
            </span>
            {dossier.progress_pct != null && (
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" />
                {Math.round(dossier.progress_pct)}%
              </span>
            )}
            {dossier.prix_vente && (
              <span className="font-medium text-charcoal">
                {dossier.prix_vente.toLocaleString('fr-FR')} EUR
              </span>
            )}
          </div>
          <ChevronRight className="w-5 h-5 text-slate group-hover:text-gold transition-colors" />
        </div>
      </div>
    </Link>
  )
}
