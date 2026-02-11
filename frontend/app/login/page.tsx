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
      <div className="login-container">
        <div className="login-card">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-500 mx-auto"></div>
            <p style={{ marginTop: '1rem', color: '#a8a29e' }}>Chargement...</p>
          </div>
        </div>
        <style jsx>{styles}</style>
      </div>
    )
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-logo">
          <div className="logo-seal">N</div>
          <h1>Notomai</h1>
          <p>Assistant Notarial Intelligent</p>
        </div>

        <form className="login-form" onSubmit={handleLogin}>
          <div className="form-group">
            <label htmlFor="email">Adresse email</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="notaire@etude.fr"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Votre mot de passe"
              required
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="login-btn" disabled={isLoading}>
            {isLoading ? 'Connexion en cours...' : 'Se connecter'}
          </button>
        </form>

        <div className="login-divider">ou</div>

        <button className="magic-link-btn" onClick={handleMagicLink} disabled={isLoading}>
          Recevoir un lien de connexion par email
        </button>

        {success && <div className="success-message">{success}</div>}

        <div className="login-footer">
          <p>Pas encore de compte ? <a href="#">Demander un acces</a></p>
          <p style={{ marginTop: '0.5rem' }}><Link href="/">Retour a l&apos;accueil</Link></p>
        </div>
      </div>

      <style jsx>{styles}</style>
    </div>
  )
}

const styles = `
  .login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a1a1a 0%, #0d0d0d 100%);
    padding: 1rem;
  }

  .login-card {
    background: #1f1f1f;
    border-radius: 16px;
    padding: 2.5rem;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    border: 1px solid #333;
  }

  .login-logo {
    text-align: center;
    margin-bottom: 2rem;
  }

  .login-logo .logo-seal {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, #c9a962 0%, #a68b4b 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a1a1a;
    margin: 0 auto 1rem;
  }

  .login-logo h1 {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.8rem;
    color: #f5f0e6;
    margin: 0 0 0.25rem;
  }

  .login-logo p {
    color: #a8a29e;
    font-size: 0.9rem;
    margin: 0;
  }

  .login-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-group label {
    color: #f5f0e6;
    font-size: 0.9rem;
    font-weight: 500;
  }

  .form-group input {
    padding: 0.75rem 1rem;
    border: 1px solid #444;
    border-radius: 8px;
    background: #2a2a2a;
    color: #f5f0e6;
    font-size: 1rem;
    transition: border-color 0.2s;
  }

  .form-group input:focus {
    outline: none;
    border-color: #c9a962;
  }

  .form-group input::placeholder {
    color: #666;
  }

  .error-message {
    color: #ef4444;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
  }

  .success-message {
    color: #22c55e;
    font-size: 0.85rem;
    margin-top: 1rem;
    text-align: center;
  }

  .login-btn {
    width: 100%;
    padding: 0.75rem;
    background: #c9a962;
    color: #1a1a1a;
    border: none;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
    margin-top: 0.5rem;
  }

  .login-btn:hover:not(:disabled) {
    background: #d4b876;
  }

  .login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .login-divider {
    text-align: center;
    color: #666;
    margin: 1.5rem 0;
    position: relative;
  }

  .login-divider::before,
  .login-divider::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 40%;
    height: 1px;
    background: #444;
  }

  .login-divider::before {
    left: 0;
  }

  .login-divider::after {
    right: 0;
  }

  .magic-link-btn {
    width: 100%;
    padding: 0.75rem;
    background: transparent;
    color: #c9a962;
    border: 2px solid #c9a962;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .magic-link-btn:hover:not(:disabled) {
    background: rgba(201, 169, 98, 0.1);
  }

  .magic-link-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .login-footer {
    margin-top: 1.5rem;
    text-align: center;
  }

  .login-footer p {
    color: #a8a29e;
    font-size: 0.85rem;
    margin: 0;
  }

  .login-footer a {
    color: #c9a962;
    text-decoration: none;
  }

  .login-footer a:hover {
    text-decoration: underline;
  }
`
