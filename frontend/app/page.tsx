'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function LandingPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Vérifier si l'utilisateur est déjà connecté
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
      <div className="landing-container" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-500"></div>
      </div>
    )
  }

  return (
    <div className="landing-container">
      <header className="landing-header">
        <div className="landing-logo">
          <div className="logo-seal">N</div>
          <h1>Notomai</h1>
        </div>
        <nav className="landing-nav">
          <a href="#features">Fonctionnalites</a>
          <a href="#securite">Securite</a>
          <Link href="/login">Connexion</Link>
          <Link href="/app" className="btn-primary">Demarrer</Link>
        </nav>
      </header>

      <main className="landing-hero">
        <div className="hero-content">
          <h2>L&apos;assistant <span>intelligent</span> pour les notaires</h2>
          <p>
            Creez vos actes notariaux en quelques minutes grace a l&apos;intelligence artificielle.
            Notomai comprend vos demandes en langage naturel et genere des documents conformes.
          </p>
          <div className="hero-cta">
            <Link href="/app" className="btn btn-primary">Essayer gratuitement</Link>
            <Link href="/login" className="btn btn-secondary">Se connecter</Link>
          </div>
          <div className="hero-features">
            <div className="hero-feature">
              <span className="icon">🔒</span>
              <span>Donnees chiffrees</span>
            </div>
            <div className="hero-feature">
              <span className="icon">🇪🇺</span>
              <span>Hebergement europeen</span>
            </div>
            <div className="hero-feature">
              <span className="icon">✓</span>
              <span>Conforme RGPD</span>
            </div>
          </div>
        </div>
      </main>

      <footer className="landing-footer">
        <p>2026 Notomai - Assistant Notarial Intelligent</p>
      </footer>

      <style jsx>{`
        .landing-container {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .landing-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1.5rem 2rem;
          background: #1a1a1a;
        }

        .landing-logo {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .landing-logo .logo-seal {
          width: 40px;
          height: 40px;
          background: linear-gradient(135deg, #c9a962 0%, #a68b4b 100%);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-family: 'Cormorant Garamond', serif;
          font-size: 1.2rem;
          font-weight: 700;
          color: #1a1a1a;
        }

        .landing-logo h1 {
          font-family: 'Cormorant Garamond', serif;
          font-size: 1.5rem;
          color: #f5f0e6;
          margin: 0;
        }

        .landing-nav {
          display: flex;
          gap: 1rem;
          align-items: center;
        }

        .landing-nav a, .landing-nav :global(a) {
          color: #a8a29e;
          text-decoration: none;
          font-size: 0.9rem;
          padding: 0.5rem 1rem;
          border-radius: 8px;
          transition: all 0.2s ease;
        }

        .landing-nav a:hover, .landing-nav :global(a):hover {
          color: #f5f0e6;
          background: rgba(255,255,255,0.1);
        }

        .landing-nav .btn-primary, .landing-nav :global(.btn-primary) {
          background: #c9a962;
          color: #1a1a1a;
          font-weight: 600;
        }

        .landing-nav .btn-primary:hover, .landing-nav :global(.btn-primary):hover {
          background: #d4b876;
        }

        .landing-hero {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
          padding: 2rem;
        }

        .hero-content {
          text-align: center;
          max-width: 800px;
        }

        .hero-content h2 {
          font-family: 'Cormorant Garamond', serif;
          font-size: 3rem;
          color: #f5f0e6;
          margin-bottom: 1.5rem;
          line-height: 1.2;
        }

        .hero-content h2 span {
          color: #c9a962;
        }

        .hero-content p {
          font-size: 1.2rem;
          color: #a8a29e;
          margin-bottom: 2rem;
          line-height: 1.6;
        }

        .hero-cta {
          display: flex;
          gap: 1rem;
          justify-content: center;
        }

        .hero-cta .btn, .hero-cta :global(.btn) {
          padding: 1rem 2rem;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: 600;
          text-decoration: none;
          transition: all 0.2s ease;
        }

        .hero-cta .btn-primary, .hero-cta :global(.btn-primary) {
          background: #c9a962;
          color: #1a1a1a;
        }

        .hero-cta .btn-primary:hover, .hero-cta :global(.btn-primary):hover {
          background: #d4b876;
          transform: translateY(-2px);
        }

        .hero-cta .btn-secondary, .hero-cta :global(.btn-secondary) {
          background: transparent;
          border: 2px solid #c9a962;
          color: #c9a962;
        }

        .hero-cta .btn-secondary:hover, .hero-cta :global(.btn-secondary):hover {
          background: rgba(201, 169, 98, 0.1);
        }

        .hero-features {
          display: flex;
          gap: 2rem;
          margin-top: 2rem;
          justify-content: center;
        }

        .hero-feature {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          color: #a8a29e;
          font-size: 0.9rem;
        }

        .hero-feature .icon {
          font-size: 1.2rem;
        }

        .landing-footer {
          padding: 1.5rem;
          background: #1a1a1a;
          border-top: 1px solid #333;
          text-align: center;
        }

        .landing-footer p {
          color: #666;
          font-size: 0.8rem;
          margin: 0;
        }

        @media (max-width: 768px) {
          .hero-content h2 {
            font-size: 2rem;
          }

          .hero-cta {
            flex-direction: column;
          }

          .hero-features {
            flex-direction: column;
            gap: 1rem;
          }

          .landing-header {
            flex-direction: column;
            gap: 1rem;
          }
        }
      `}</style>
    </div>
  )
}
