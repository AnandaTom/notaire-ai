'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import {
  MessageSquare,
  ClipboardList,
  FileText,
  FolderOpen,
  ArrowRight,
  TrendingUp,
  Clock,
  CheckCircle2,
} from 'lucide-react'
import { useAppData } from '@/lib/hooks/useAppData'
import { getDashboardStats } from '@/lib/api'

const QUICK_ACTIONS = [
  {
    title: 'Promesse de vente',
    description: 'Copropriete, maison, terrain',
    href: '/app/workflow?type=promesse_vente',
    icon: FileText,
    color: 'bg-gold/10 text-gold-dark',
  },
  {
    title: 'Acte de vente',
    description: 'Vente definitive',
    href: '/app/workflow?type=vente',
    icon: FileText,
    color: 'bg-navy/10 text-navy',
  },
  {
    title: 'Chat IA',
    description: 'Assistant libre',
    href: '/app/chat',
    icon: MessageSquare,
    color: 'bg-success/10 text-success',
  },
  {
    title: 'Workflow guide',
    description: 'Pas a pas',
    href: '/app/workflow',
    icon: ClipboardList,
    color: 'bg-info/10 text-info',
  },
]

interface DashboardStats {
  totalDossiers: number
  dossiersEnCours: number
  dossiersTermines: number
  actesGeneres: number
}

interface RecentDossier {
  id: string
  numero: string
  type_acte: string
  statut: string
  parties: { nom: string; prenom?: string }[] | null
  biens: { adresse?: string; ville?: string }[] | null
  updated_at: string
}

export default function DashboardPage() {
  const { userInfo } = useAppData()
  const [recentDossiers, setRecentDossiers] = useState<RecentDossier[]>([])
  const [stats, setStats] = useState<DashboardStats>({
    totalDossiers: 0,
    dossiersEnCours: 0,
    dossiersTermines: 0,
    actesGeneres: 0,
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadDashboardData = async () => {
      setIsLoading(true)
      try {
        const data = await getDashboardStats()
        setStats({
          totalDossiers: data.total_dossiers,
          dossiersEnCours: data.dossiers_en_cours,
          dossiersTermines: data.dossiers_termines,
          actesGeneres: data.actes_generes,
        })
        setRecentDossiers(data.recent_dossiers)
      } catch {
        // Silently fail — dashboard shows empty state
      } finally {
        setIsLoading(false)
      }
    }

    loadDashboardData()
  }, [])

  const greeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Bonjour'
    if (hour < 18) return 'Bon apres-midi'
    return 'Bonsoir'
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Greeting */}
      <div className="mb-8">
        <h1 className="font-serif text-3xl text-charcoal font-semibold mb-1">
          {greeting()}, {userInfo ? `Maitre ${userInfo.prenom}` : '...'}
        </h1>
        <p className="text-slate text-[0.9rem]">
          Que souhaitez-vous faire aujourd'hui ?
        </p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {QUICK_ACTIONS.map((action) => (
          <Link
            key={action.href}
            href={action.href}
            className="group bg-white border border-champagne rounded-2xl p-5 hover:border-gold/50 hover:shadow-md transition-all"
          >
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${action.color}`}>
              <action.icon className="w-5 h-5" />
            </div>
            <h3 className="font-serif text-base text-charcoal font-semibold mb-1 group-hover:text-gold-dark transition-colors">
              {action.title}
            </h3>
            <p className="text-[0.78rem] text-slate">
              {action.description}
            </p>
          </Link>
        ))}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <StatCard
          icon={FolderOpen}
          label="Total dossiers"
          value={stats.totalDossiers}
          isLoading={isLoading}
        />
        <StatCard
          icon={Clock}
          label="En cours"
          value={stats.dossiersEnCours}
          color="text-warning"
          isLoading={isLoading}
        />
        <StatCard
          icon={CheckCircle2}
          label="Termines"
          value={stats.dossiersTermines}
          color="text-success"
          isLoading={isLoading}
        />
        <StatCard
          icon={TrendingUp}
          label="Actes generes"
          value={stats.actesGeneres}
          color="text-info"
          isLoading={isLoading}
        />
      </div>

      {/* Recent Dossiers */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-serif text-lg text-charcoal font-semibold">
            Dossiers recents
          </h2>
          <Link
            href="/app/dossiers"
            className="flex items-center gap-1.5 text-[0.8rem] text-gold-dark hover:text-gold transition-colors"
          >
            Voir tout
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white border border-champagne rounded-2xl p-5 animate-shimmer h-28" />
            ))}
          </div>
        ) : recentDossiers.length === 0 ? (
          <div className="bg-white border border-champagne rounded-2xl p-10 text-center">
            <FolderOpen className="w-12 h-12 text-champagne mx-auto mb-3" />
            <p className="text-slate text-[0.9rem] mb-4">
              Aucun dossier pour le moment
            </p>
            <Link
              href="/app/chat"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-gold text-white rounded-xl hover:bg-gold-dark transition-colors font-medium text-[0.85rem]"
            >
              <MessageSquare className="w-4 h-4" />
              Commencer avec le chat
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recentDossiers.map((dossier) => (
              <Link
                key={dossier.id}
                href={`/app/dossiers/${dossier.id}`}
                className="bg-white border border-champagne rounded-2xl p-5 hover:border-gold/50 hover:shadow-sm transition-all group"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <p className="text-[0.7rem] text-slate uppercase tracking-wider">
                      {dossier.numero}
                    </p>
                    <p className="font-serif text-base text-charcoal font-medium group-hover:text-gold-dark transition-colors">
                      {dossier.parties?.map((p) => `${p.prenom || ''} ${p.nom}`).join(' / ') || 'Sans parties'}
                    </p>
                  </div>
                  <span className={`text-[0.7rem] px-2.5 py-1 rounded-full font-medium ${
                    dossier.statut === 'en_cours'
                      ? 'bg-warning-light text-warning'
                      : dossier.statut === 'termine'
                        ? 'bg-success-light text-success'
                        : 'bg-sand text-slate'
                  }`}>
                    {dossier.statut === 'en_cours' ? 'En cours' :
                     dossier.statut === 'termine' ? 'Termine' :
                     dossier.statut === 'brouillon' ? 'Brouillon' : dossier.statut}
                  </span>
                </div>
                {dossier.biens?.[0] && (
                  <p className="text-[0.78rem] text-slate">
                    {dossier.biens[0].adresse}{dossier.biens[0].ville ? `, ${dossier.biens[0].ville}` : ''}
                  </p>
                )}
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function StatCard({
  icon: Icon,
  label,
  value,
  color,
  isLoading,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: number
  color?: string
  isLoading: boolean
}) {
  return (
    <div className="bg-white border border-champagne rounded-2xl p-5">
      <div className="flex items-center gap-3 mb-2">
        <Icon className={`w-5 h-5 ${color || 'text-gold-dark'}`} />
        <span className="text-[0.75rem] text-slate uppercase tracking-wider">{label}</span>
      </div>
      {isLoading ? (
        <div className="h-8 w-12 bg-sand rounded animate-shimmer" />
      ) : (
        <p className="font-serif text-2xl text-charcoal font-semibold">{value}</p>
      )}
    </div>
  )
}
