'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import { Search, Filter, FileText, RefreshCw } from 'lucide-react'
import { supabase } from '@/lib/supabase'
import DocumentCard from '@/components/DocumentCard'
import type { ActeGenere } from '@/types'
import { getUserEtudeId } from '@/lib/auth'

const TYPE_OPTIONS = [
  { value: '', label: 'Tous les types' },
  { value: 'vente', label: 'Acte de vente' },
  { value: 'promesse_vente', label: 'Promesse de vente' },
  { value: 'reglement_copropriete', label: 'Reglement copropriete' },
  { value: 'modificatif_edd', label: 'Modificatif EDD' },
]

const STATUS_OPTIONS = [
  { value: '', label: 'Tous les statuts' },
  { value: 'genere', label: 'Genere' },
  { value: 'valide', label: 'Valide' },
  { value: 'signe', label: 'Signe' },
  { value: 'archive', label: 'Archive' },
]

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<ActeGenere[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [etudeId, setEtudeId] = useState<string | null>(null)

  useEffect(() => {
    getUserEtudeId().then(setEtudeId)
  }, [])

  useEffect(() => {
    if (etudeId) {
      loadDocuments(etudeId)
    }
  }, [etudeId, typeFilter, statusFilter])

  async function loadDocuments(currentEtudeId: string) {
    setIsLoading(true)
    setError(null)

    try {
      let query = supabase
        .from('actes_generes')
        .select('*')
        .eq('etude_id', currentEtudeId)
        .eq('is_demo', false)
        .order('created_at', { ascending: false })
        .limit(50)

      if (typeFilter) query = query.eq('type_acte', typeFilter)
      if (statusFilter) query = query.eq('status', statusFilter)

      const { data, error: supabaseError } = await query

      if (supabaseError) throw supabaseError
      setDocuments(data || [])
    } catch {
      setError('Impossible de charger les documents. Verifiez votre connexion.')
      setDocuments([])
    } finally {
      setIsLoading(false)
    }
  }

  const filteredDocuments = useMemo(() => documents.filter((doc) => {
    if (!searchQuery) return true
    const search = searchQuery.toLowerCase()
    return (
      doc.nom?.toLowerCase().includes(search) ||
      doc.reference_interne?.toLowerCase().includes(search) ||
      doc.type_acte?.toLowerCase().includes(search)
    )
  }), [documents, searchQuery])

  return (
    <>
      {/* Filters */}
      <div className="bg-white border-b border-champagne px-8 py-4">
        <div className="max-w-6xl mx-auto flex items-center gap-4 flex-wrap">
          <p className="text-[0.8rem] text-slate">
            {filteredDocuments.length} document{filteredDocuments.length > 1 ? 's' : ''}
            {searchQuery && filteredDocuments.length !== documents.length && ` sur ${documents.length}`}
          </p>

          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate" />
            <input
              type="text"
              placeholder="Rechercher par nom ou reference..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-cream border border-champagne rounded-xl text-[0.85rem] focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/10"
            />
          </div>

          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2.5 bg-cream border border-champagne rounded-xl text-[0.85rem] focus:outline-none focus:border-gold"
            >
              {TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2.5 bg-cream border border-champagne rounded-xl text-[0.85rem] focus:outline-none focus:border-gold"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>

          <button
            onClick={() => etudeId && loadDocuments(etudeId)}
            className="p-2.5 hover:bg-sand rounded-xl transition-colors"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 text-slate ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          <Link
            href="/app/chat"
            className="flex items-center gap-2 px-4 py-2.5 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors font-medium text-[0.85rem]"
          >
            Generer un acte
          </Link>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-6xl mx-auto px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 text-[0.85rem]">
            {error}
          </div>
        )}

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-cream border border-champagne rounded-2xl p-5 animate-pulse">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-sand rounded-xl" />
                  <div className="flex-1">
                    <div className="h-3 bg-sand rounded w-24 mb-2" />
                    <div className="h-5 bg-sand rounded w-40" />
                  </div>
                </div>
                <div className="h-4 bg-sand rounded w-full mb-2" />
                <div className="h-4 bg-sand rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : filteredDocuments.length === 0 ? (
          <div className="text-center py-16">
            <FileText className="w-16 h-16 text-champagne mx-auto mb-4" />
            <h2 className="font-serif text-xl text-charcoal mb-2">Aucun document trouve</h2>
            <p className="text-slate text-[0.9rem] mb-6">
              {searchQuery || typeFilter || statusFilter
                ? 'Modifiez vos filtres pour voir plus de resultats.'
                : 'Les actes que vous generez apparaitront ici.'}
            </p>
            <Link
              href="/app/chat"
              className="inline-flex items-center gap-2 px-5 py-3 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors font-medium"
            >
              Generer un acte
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {filteredDocuments.map((doc) => (
              <DocumentCard key={doc.id} document={doc} />
            ))}
          </div>
        )}
      </div>
    </>
  )
}
