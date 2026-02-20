'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Plus, Search, Filter, FolderOpen, RefreshCw } from 'lucide-react'
import { supabase } from '@/lib/supabase'
import DossierCard from '@/components/DossierCard'
import type { Dossier } from '@/types'
import { API_URL } from '@/lib/config'
import { getUserEtudeId } from '@/lib/auth'

const TYPE_OPTIONS = [
  { value: '', label: 'Tous les types' },
  { value: 'vente', label: 'Acte de vente' },
  { value: 'promesse_vente', label: 'Promesse de vente' },
  { value: 'reglement_copropriete', label: 'Reglement copropriete' },
  { value: 'modificatif_edd', label: 'Modificatif EDD' },
]

const STATUT_OPTIONS = [
  { value: '', label: 'Tous les statuts' },
  { value: 'brouillon', label: 'Brouillon' },
  { value: 'en_cours', label: 'En cours' },
  { value: 'termine', label: 'Termine' },
  { value: 'archive', label: 'Archive' },
]

export default function DossiersPage() {
  const router = useRouter()
  const [dossiers, setDossiers] = useState<Dossier[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [statutFilter, setStatutFilter] = useState('')
  const [etudeId, setEtudeId] = useState<string | null>(null)

  // Charger l'etude_id au montage
  useEffect(() => {
    getUserEtudeId().then(setEtudeId)
  }, [])

  // Charger les dossiers quand etudeId ou filtres changent
  useEffect(() => {
    if (etudeId) {
      loadDossiers(etudeId)
    }
  }, [etudeId, typeFilter, statutFilter])

  async function loadDossiers(currentEtudeId: string) {
    setIsLoading(true)
    setError(null)

    try {
      // Essayer d'abord l'API Modal
      const params = new URLSearchParams()
      if (typeFilter) params.set('type_acte', typeFilter)
      if (statutFilter) params.set('statut', statutFilter)
      params.set('etude_id', currentEtudeId)
      params.set('limit', '50')

      const response = await fetch(`${API_URL}/dossiers?${params}`, {
        headers: { 'Content-Type': 'application/json' },
      })

      if (response.ok) {
        const data = await response.json()
        setDossiers(data.dossiers || data || [])
      } else {
        // Fallback vers Supabase direct avec filtre etude_id
        let query = supabase
          .from('dossiers')
          .select('*')
          .eq('etude_id', currentEtudeId)
          .is('deleted_at', null)
          .order('created_at', { ascending: false })
          .limit(50)

        if (typeFilter) query = query.eq('type_acte', typeFilter)
        if (statutFilter) query = query.eq('statut', statutFilter)

        const { data, error: supabaseError } = await query

        if (supabaseError) throw supabaseError
        setDossiers(data || [])
      }
    } catch (err) {
      setError('Impossible de charger les dossiers. Verifiez votre connexion.')

      // Donnees de demo en cas d'erreur
      setDossiers([
        {
          id: 'demo-1',
          numero: 'DOS-2026-001',
          type_acte: 'promesse_vente',
          statut: 'en_cours',
          parties: [
            { nom: 'Martin', prenom: 'Jean', type: 'physique', role: 'vendeur' },
            { nom: 'Dupont', prenom: 'Marie', type: 'physique', role: 'acquereur' },
          ],
          biens: [{ adresse: '12 rue de la Paix', ville: 'Paris' }],
          prix_vente: 450000,
          progress_pct: 65,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'demo-2',
          numero: 'DOS-2026-002',
          type_acte: 'vente',
          statut: 'termine',
          parties: [
            { nom: 'Bernard', prenom: 'Pierre', type: 'physique', role: 'vendeur' },
            { nom: 'SCI Immobiliere', type: 'morale', role: 'acquereur' },
          ],
          biens: [{ adresse: '5 avenue Victor Hugo', ville: 'Lyon' }],
          prix_vente: 780000,
          created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
          updated_at: new Date(Date.now() - 86400000 * 3).toISOString(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const filteredDossiers = useMemo(() => dossiers.filter((d) => {
    if (!searchQuery) return true
    const search = searchQuery.toLowerCase()
    const matchNumero = d.numero?.toLowerCase().includes(search)
    const matchParties = d.parties?.some(
      (p) =>
        p.nom.toLowerCase().includes(search) ||
        p.prenom?.toLowerCase().includes(search)
    )
    const matchBien = d.biens?.some(
      (b) =>
        b.adresse?.toLowerCase().includes(search) ||
        b.ville?.toLowerCase().includes(search)
    )
    return matchNumero || matchParties || matchBien
  }), [dossiers, searchQuery])

  return (
    <>
      {/* Filters */}
      <div className="bg-white border-b border-champagne px-8 py-4">
        <div className="max-w-6xl mx-auto flex items-center gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <p className="text-[0.8rem] text-slate">
              {filteredDossiers.length} dossier{filteredDossiers.length > 1 ? 's' : ''}
              {searchQuery && filteredDossiers.length !== dossiers.length && ` sur ${dossiers.length}`}
            </p>
          </div>

          {/* Search */}
          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate" />
            <input
              type="text"
              placeholder="Rechercher par numero, nom ou adresse..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-cream border border-champagne rounded-xl text-[0.85rem] focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/10"
            />
          </div>

          {/* Type filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-3 py-2.5 bg-cream border border-champagne rounded-xl text-[0.85rem] focus:outline-none focus:border-gold"
            >
              {TYPE_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Statut filter */}
          <select
            value={statutFilter}
            onChange={(e) => setStatutFilter(e.target.value)}
            className="px-3 py-2.5 bg-cream border border-champagne rounded-xl text-[0.85rem] focus:outline-none focus:border-gold"
          >
            {STATUT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          {/* Refresh */}
          <button
            onClick={() => etudeId && loadDossiers(etudeId)}
            className="p-2.5 hover:bg-sand rounded-xl transition-colors"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 text-slate ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          <Link
            href="/app/chat"
            className="flex items-center gap-2 px-4 py-2.5 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors font-medium text-[0.85rem]"
          >
            <Plus className="w-4 h-4" />
            Nouveau dossier
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
        ) : filteredDossiers.length === 0 ? (
          <div className="text-center py-16">
            <FolderOpen className="w-16 h-16 text-champagne mx-auto mb-4" />
            <h2 className="font-serif text-xl text-charcoal mb-2">Aucun dossier trouve</h2>
            <p className="text-slate text-[0.9rem] mb-6">
              {searchQuery || typeFilter || statutFilter
                ? 'Modifiez vos filtres pour voir plus de resultats.'
                : 'Commencez par creer votre premier dossier.'}
            </p>
            <Link
              href="/app/chat"
              className="inline-flex items-center gap-2 px-5 py-3 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors font-medium"
            >
              <Plus className="w-4 h-4" />
              Creer un dossier
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {filteredDossiers.map((dossier) => (
              <DossierCard key={dossier.id} dossier={dossier} />
            ))}
          </div>
        )}
      </div>
    </>
  )
}
