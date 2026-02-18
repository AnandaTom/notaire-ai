'use client'

import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import { MessageSquare } from 'lucide-react'
import WorkflowPage from '@/components/workflow/WorkflowPage'
import type { TypeActe } from '@/types/workflow'

function WorkflowContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const typeParam = searchParams?.get('type') as TypeActe | null

  return (
    <div className="h-screen w-screen overflow-hidden bg-ivory relative">
      <WorkflowPage
        onBack={() => router.push('/app')}
        initialType={typeParam || undefined}
      />
      <Link
        href="/app"
        className="fixed bottom-6 right-6 flex items-center gap-2 px-4 py-2.5 bg-navy text-white rounded-xl text-[0.85rem] font-medium shadow-lg hover:bg-navy/90 transition-all hover:-translate-y-0.5 z-50"
      >
        <MessageSquare className="w-4 h-4" />
        Retour au chat
      </Link>
    </div>
  )
}

export default function WorkflowRoute() {
  return (
    <Suspense fallback={
      <div className="h-screen w-screen flex items-center justify-center bg-ivory">
        <p className="text-slate text-[0.88rem]">Chargement...</p>
      </div>
    }>
      <WorkflowContent />
    </Suspense>
  )
}
