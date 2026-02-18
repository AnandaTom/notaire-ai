'use client'

import { User, Building2, Mail, Phone, FolderOpen, ChevronRight } from 'lucide-react'
import type { Client } from '@/types'
import Link from 'next/link'
import { formatDate } from '@/lib/format'

interface ClientCardProps {
  client: Client
}

export default function ClientCard({ client }: ClientCardProps) {
  const isPersonneMorale = client.type_personne === 'morale'
  const displayName = isPersonneMorale
    ? client.raison_sociale || client.nom
    : client.prenom
      ? `${client.civilite || ''} ${client.prenom} ${client.nom}`.trim()
      : client.nom

  return (
    <Link href={`/app/clients/${client.id}`}>
      <div className="bg-cream border border-champagne rounded-2xl p-5 hover:border-gold hover:shadow-md transition-all cursor-pointer group">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              isPersonneMorale ? 'bg-navy/10' : 'bg-sand'
            }`}>
              {isPersonneMorale ? (
                <Building2 className="w-5 h-5 text-navy" />
              ) : (
                <User className="w-5 h-5 text-gold-dark" />
              )}
            </div>
            <div>
              <p className="text-[0.7rem] text-slate uppercase tracking-wider">
                {isPersonneMorale ? 'Personne morale' : 'Personne physique'}
              </p>
              <p className="font-serif text-lg text-charcoal font-semibold">
                {displayName}
              </p>
            </div>
          </div>
          {client.dossiers_count != null && client.dossiers_count > 0 && (
            <span className="flex items-center gap-1.5 px-2.5 py-1 bg-gold/10 rounded-lg text-[0.7rem] font-medium text-gold-dark">
              <FolderOpen className="w-3.5 h-3.5" />
              {client.dossiers_count} dossier{client.dossiers_count > 1 ? 's' : ''}
            </span>
          )}
        </div>

        {/* Contact info */}
        <div className="space-y-2 mb-4">
          {client.email && (
            <div className="flex items-center gap-2 text-[0.8rem] text-graphite">
              <Mail className="w-4 h-4 text-slate" />
              <span>{client.email}</span>
            </div>
          )}
          {client.telephone && (
            <div className="flex items-center gap-2 text-[0.8rem] text-graphite">
              <Phone className="w-4 h-4 text-slate" />
              <span>{client.telephone}</span>
            </div>
          )}
          {client.adresse && (
            <div className="text-[0.8rem] text-slate">
              {client.adresse}
              {client.code_postal && `, ${client.code_postal}`}
              {client.ville && ` ${client.ville}`}
            </div>
          )}
        </div>

        {/* Details for personne physique */}
        {!isPersonneMorale && (client.profession || client.situation_matrimoniale) && (
          <div className="flex items-center gap-3 text-[0.75rem] text-slate mb-3">
            {client.profession && <span>{client.profession}</span>}
            {client.profession && client.situation_matrimoniale && <span>•</span>}
            {client.situation_matrimoniale && <span>{client.situation_matrimoniale}</span>}
          </div>
        )}

        {/* Details for personne morale */}
        {isPersonneMorale && client.siret && (
          <div className="text-[0.75rem] text-slate mb-3">
            SIRET: {client.siret}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-champagne/50">
          <span className="text-[0.75rem] text-slate">
            Ajoute le {formatDate(client.created_at)}
          </span>
          <ChevronRight className="w-5 h-5 text-slate group-hover:text-gold transition-colors" />
        </div>
      </div>
    </Link>
  )
}
