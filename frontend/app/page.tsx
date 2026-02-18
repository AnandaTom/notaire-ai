'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function LandingPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser()
        if (user) {
          router.push('/app')
        } else {
          setIsLoading(false)
        }
      } catch {
        setIsLoading(false)
      }
    }
    checkAuth()
  }, [router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gold" />
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="flex justify-between items-center px-8 py-6 bg-[#1a1a1a] max-md:flex-col max-md:gap-4">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-gradient-to-br from-gold to-gold-dark rounded-full flex items-center justify-center font-serif text-xl font-bold text-[#1a1a1a]">
            N
          </div>
          <h1 className="font-serif text-2xl text-ivory m-0">Notomai</h1>
        </div>
        <nav className="flex gap-4 items-center">
          <a href="#features" className="text-stone-400 no-underline text-[0.9rem] px-4 py-2 rounded-lg transition-all hover:text-ivory hover:bg-white/10">
            Fonctionnalites
          </a>
          <a href="#securite" className="text-stone-400 no-underline text-[0.9rem] px-4 py-2 rounded-lg transition-all hover:text-ivory hover:bg-white/10">
            Securite
          </a>
          <Link href="/login" className="text-stone-400 no-underline text-[0.9rem] px-4 py-2 rounded-lg transition-all hover:text-ivory hover:bg-white/10">
            Connexion
          </Link>
          <Link href="/app" className="bg-gold text-[#1a1a1a] no-underline text-[0.9rem] px-4 py-2 rounded-lg font-semibold transition-all hover:bg-gold-light">
            Demarrer
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <main className="flex-1 flex items-center justify-center bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] p-8">
        <div className="text-center max-w-[800px]">
          <h2 className="font-serif text-5xl text-ivory mb-6 leading-tight max-md:text-3xl">
            L&apos;assistant <span className="text-gold">intelligent</span> pour les notaires
          </h2>
          <p className="text-xl text-stone-400 mb-8 leading-relaxed">
            Creez vos actes notariaux en quelques minutes grace a l&apos;intelligence artificielle.
            Notomai comprend vos demandes en langage naturel et genere des documents conformes.
          </p>
          <div className="flex gap-4 justify-center max-md:flex-col">
            <Link
              href="/app"
              className="px-8 py-4 rounded-lg text-base font-semibold no-underline transition-all bg-gold text-[#1a1a1a] hover:bg-gold-light hover:-translate-y-0.5"
            >
              Essayer gratuitement
            </Link>
            <Link
              href="/login"
              className="px-8 py-4 rounded-lg text-base font-semibold no-underline transition-all bg-transparent border-2 border-gold text-gold hover:bg-gold/10"
            >
              Se connecter
            </Link>
          </div>
          <div className="flex gap-8 mt-8 justify-center max-md:flex-col max-md:gap-4">
            <div className="flex items-center gap-2 text-stone-400 text-[0.9rem]">
              <span className="text-xl">&#x1f512;</span>
              <span>Donnees chiffrees</span>
            </div>
            <div className="flex items-center gap-2 text-stone-400 text-[0.9rem]">
              <span className="text-xl">&#x1f1ea;&#x1f1fa;</span>
              <span>Hebergement europeen</span>
            </div>
            <div className="flex items-center gap-2 text-stone-400 text-[0.9rem]">
              <span className="text-xl">&#x2713;</span>
              <span>Conforme RGPD</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 bg-[#1a1a1a] border-t border-[#333] text-center">
        <p className="text-[#666] text-[0.8rem] m-0">2026 Notomai - Assistant Notarial Intelligent</p>
      </footer>
    </div>
  )
}
