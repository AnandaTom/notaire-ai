'use client'

import { useState, useEffect, useMemo } from 'react'
import Link from 'next/link'
import { Plus, Search, Users, RefreshCw, Building2, User } from 'lucide-react'
import { supabase } from '@/lib/supabase'
import ClientCard from '@/components/ClientCard'
import type { Client } from '@/types'
import { getUserEtudeId } from '@/lib/auth'

const TYPE_OPTIONS = [
  { value: '', label: 'Tous les types' },
  { value: 'physique', label: 'Personnes physiques' },
  { value: 'morale', label: 'Personnes morales' },
]

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)
  const [etudeId, setEtudeId] = useState<string | null>(null)

  // Charger l'etude_id au montage
  useEffect(() => {
    getUserEtudeId().then(setEtudeId)
  }, [])

  // Charger les clients quand etudeId ou filtre change
  useEffect(() => {
    if (etudeId) {
      loadClients(etudeId)
    }
  }, [etudeId, typeFilter])

  async function loadClients(currentEtudeId: string) {
    setIsLoading(true)
    setError(null)

    try {
      let query = supabase
        .from('clients')
        .select('*')
        .eq('etude_id', currentEtudeId)
        .is('deleted_at', null)
        .order('created_at', { ascending: false })
        .limit(50)

      if (typeFilter) query = query.eq('type_personne', typeFilter)

      const { data, error: supabaseError } = await query

      if (supabaseError) throw supabaseError
      setClients(data || [])
    } catch (err) {
      setError('Impossible de charger les clients. Verifiez votre connexion.')

      // Donnees de demo en cas d'erreur
      setClients([
        {
          id: 'demo-1',
          type_personne: 'physique',
          civilite: 'M.',
          nom: 'Martin',
          prenom: 'Jean',
          email: 'jean.martin@email.com',
          telephone: '06 12 34 56 78',
          adresse: '12 rue de la Paix',
          ville: 'Paris',
          code_postal: '75002',
          profession: 'Ingenieur',
          situation_matrimoniale: 'Marie',
          dossiers_count: 2,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'demo-2',
          type_personne: 'morale',
          nom: 'SCI Immobiliere',
          raison_sociale: 'SCI Immobiliere du Parc',
          siret: '123 456 789 00012',
          email: 'contact@sci-parc.fr',
          telephone: '01 23 45 67 89',
          adresse: '5 avenue Victor Hugo',
          ville: 'Lyon',
          code_postal: '69002',
          representant: 'Pierre Bernard',
          dossiers_count: 3,
          created_at: new Date(Date.now() - 86400000 * 5).toISOString(),
          updated_at: new Date(Date.now() - 86400000 * 5).toISOString(),
        },
        {
          id: 'demo-3',
          type_personne: 'physique',
          civilite: 'Mme',
          nom: 'Dupont',
          prenom: 'Marie',
          email: 'marie.dupont@email.com',
          telephone: '06 98 76 54 32',
          profession: 'Medecin',
          situation_matrimoniale: 'Celibataire',
          dossiers_count: 1,
          created_at: new Date(Date.now() - 86400000 * 10).toISOString(),
          updated_at: new Date(Date.now() - 86400000 * 10).toISOString(),
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const filteredClients = useMemo(() => clients.filter((c) => {
    if (!searchQuery) return true
    const search = searchQuery.toLowerCase()
    const matchNom = c.nom?.toLowerCase().includes(search)
    const matchPrenom = c.prenom?.toLowerCase().includes(search)
    const matchRaisonSociale = c.raison_sociale?.toLowerCase().includes(search)
    const matchEmail = c.email?.toLowerCase().includes(search)
    const matchVille = c.ville?.toLowerCase().includes(search)
    return matchNom || matchPrenom || matchRaisonSociale || matchEmail || matchVille
  }), [clients, searchQuery])

  const physiquesCount = useMemo(() => clients.filter((c) => c.type_personne === 'physique').length, [clients])
  const moralesCount = useMemo(() => clients.filter((c) => c.type_personne === 'morale').length, [clients])

  return (
    <>
      {/* Stats */}
      <div className="bg-white border-b border-champagne px-8 py-4">
        <div className="max-w-6xl mx-auto flex items-center gap-6">
          <div className="flex items-center gap-3 px-4 py-2 bg-sand/50 rounded-xl">
            <User className="w-5 h-5 text-gold-dark" />
            <div>
              <p className="text-[0.7rem] text-slate uppercase">Personnes physiques</p>
              <p className="font-serif text-lg text-charcoal font-semibold">{physiquesCount}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 px-4 py-2 bg-navy/5 rounded-xl">
            <Building2 className="w-5 h-5 text-navy" />
            <div>
              <p className="text-[0.7rem] text-slate uppercase">Personnes morales</p>
              <p className="font-serif text-lg text-charcoal font-semibold">{moralesCount}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b border-champagne px-8 py-4">
        <div className="max-w-6xl mx-auto flex items-center gap-4 flex-wrap">
          {/* Search */}
          <div className="relative flex-1 min-w-[250px]">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate" />
            <input
              type="text"
              placeholder="Rechercher par nom, email ou ville..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-cream border border-champagne rounded-xl text-[0.85rem] focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/10"
            />
          </div>

          {/* Type filter */}
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

          {/* Refresh */}
          <button
            onClick={() => etudeId && loadClients(etudeId)}
            className="p-2.5 hover:bg-sand rounded-xl transition-colors"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 text-slate ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors font-medium text-[0.85rem]"
          >
            <Plus className="w-4 h-4" />
            Ajouter un client
          </button>
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="bg-cream border border-champagne rounded-2xl p-5 animate-pulse">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-sand rounded-xl" />
                  <div className="flex-1">
                    <div className="h-3 bg-sand rounded w-20 mb-2" />
                    <div className="h-5 bg-sand rounded w-32" />
                  </div>
                </div>
                <div className="h-4 bg-sand rounded w-full mb-2" />
                <div className="h-4 bg-sand rounded w-3/4" />
              </div>
            ))}
          </div>
        ) : filteredClients.length === 0 ? (
          <div className="text-center py-16">
            <Users className="w-16 h-16 text-champagne mx-auto mb-4" />
            <h2 className="font-serif text-xl text-charcoal mb-2">Aucun client trouve</h2>
            <p className="text-slate text-[0.9rem] mb-6">
              {searchQuery || typeFilter
                ? 'Modifiez vos filtres pour voir plus de resultats.'
                : 'Commencez par ajouter votre premier client.'}
            </p>
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center gap-2 px-5 py-3 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors font-medium"
            >
              <Plus className="w-4 h-4" />
              Ajouter un client
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredClients.map((client) => (
              <ClientCard key={client.id} client={client} />
            ))}
          </div>
        )}
      </div>

      {/* Add Client Modal (simple version) */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full">
            <h2 className="font-serif text-xl text-charcoal mb-4">Ajouter un client</h2>
            <p className="text-slate text-[0.9rem] mb-6">
              Pour ajouter un client, utilisez le chatbot et mentionnez les informations du client dans votre demande.
              Le systeme detectera automatiquement les parties et les ajoutera a votre base.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="flex-1 px-4 py-2.5 border border-champagne rounded-xl text-graphite hover:bg-sand transition-colors"
              >
                Fermer
              </button>
              <Link
                href="/app/chat"
                className="flex-1 px-4 py-2.5 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors text-center font-medium"
              >
                Aller au chatbot
              </Link>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
