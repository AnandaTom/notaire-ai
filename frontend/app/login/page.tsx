'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { supabase } from '@/lib/supabase'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  // Verifier si deja connecte
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser()
        if (user) {
          router.push('/app')
        } else {
          setIsCheckingAuth(false)
        }
      } catch {
        setIsCheckingAuth(false)
      }
    }
    checkAuth()
  }, [router])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setIsLoading(true)

    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        setError(error.message === 'Invalid login credentials'
          ? 'Email ou mot de passe incorrect'
          : error.message)
        setIsLoading(false)
        return
      }

      // Connexion reussie
      router.push('/app')
    } catch {
      setError('Une erreur est survenue. Veuillez reessayer.')
      setIsLoading(false)
    }
  }

  const handleMagicLink = async () => {
    if (!email) {
      setError('Veuillez entrer votre adresse email')
      return
    }

    setError('')
    setSuccess('')
    setIsLoading(true)

    try {
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: `${window.location.origin}/app`
        }
      })

      if (error) {
        setError(error.message)
        setIsLoading(false)
        return
      }

      setSuccess(`Un lien de connexion a ete envoye a ${email}`)
      setIsLoading(false)
    } catch {
      setError('Une erreur est survenue. Veuillez reessayer.')
      setIsLoading(false)
    }
  }

  if (isCheckingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] p-4">
        <div className="bg-[#1f1f1f] rounded-2xl p-10 w-full max-w-[400px] shadow-lg border border-[#333] text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gold mx-auto" />
          <p className="mt-4 text-stone-400">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] p-4">
      <div className="bg-[#1f1f1f] rounded-2xl p-10 w-full max-w-[400px] shadow-lg border border-[#333]">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-[60px] h-[60px] bg-gradient-to-br from-gold to-gold-dark rounded-full flex items-center justify-center font-serif text-3xl font-bold text-[#1a1a1a] mx-auto mb-4">
            N
          </div>
          <h1 className="font-serif text-3xl text-ivory mb-1">Notomai</h1>
          <p className="text-stone-400 text-[0.9rem]">Assistant Notarial Intelligent</p>
        </div>

        {/* Form */}
        <form className="flex flex-col gap-4" onSubmit={handleLogin}>
          <div className="flex flex-col gap-2">
            <label htmlFor="email" className="text-ivory text-[0.9rem] font-medium">
              Adresse email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="notaire@etude.fr"
              required
              className="px-4 py-3 border border-[#444] rounded-lg bg-[#2a2a2a] text-ivory text-base transition-colors focus:outline-none focus:border-gold placeholder:text-[#666]"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label htmlFor="password" className="text-ivory text-[0.9rem] font-medium">
              Mot de passe
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Votre mot de passe"
              required
              className="px-4 py-3 border border-[#444] rounded-lg bg-[#2a2a2a] text-ivory text-base transition-colors focus:outline-none focus:border-gold placeholder:text-[#666]"
            />
          </div>

          {error && <p className="text-red-500 text-[0.85rem] mb-1">{error}</p>}

          <button
            type="submit"
            className="w-full py-3 bg-gold text-[#1a1a1a] rounded-lg text-base font-semibold cursor-pointer transition-colors mt-1 hover:bg-gold-light disabled:opacity-70 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            {isLoading ? 'Connexion en cours...' : 'Se connecter'}
          </button>
        </form>

        {/* Divider */}
        <div className="flex items-center gap-4 my-6">
          <div className="flex-1 h-px bg-[#444]" />
          <span className="text-[#666] text-sm">ou</span>
          <div className="flex-1 h-px bg-[#444]" />
        </div>

        {/* Magic link */}
        <button
          className="w-full py-3 bg-transparent text-gold border-2 border-gold rounded-lg text-[0.9rem] font-semibold cursor-pointer transition-all hover:bg-gold/10 disabled:opacity-70 disabled:cursor-not-allowed"
          onClick={handleMagicLink}
          disabled={isLoading}
        >
          Recevoir un lien de connexion par email
        </button>

        {success && <p className="text-green-500 text-[0.85rem] mt-4 text-center">{success}</p>}

        {/* Footer */}
        <div className="mt-6 text-center">
          <p className="text-stone-400 text-[0.85rem]">
            Pas encore de compte ? <a href="#" className="text-gold hover:underline">Demander un acces</a>
          </p>
          <p className="text-stone-400 text-[0.85rem] mt-2">
            <Link href="/" className="text-gold hover:underline">Retour a l&apos;accueil</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
