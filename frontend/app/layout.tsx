import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NotaireAI | Assistant Notarial',
  description: 'Assistant IA pour la création et modification d\'actes notariaux',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body className="font-sans bg-cream min-h-screen">
        {children}
      </body>
    </html>
  )
}
