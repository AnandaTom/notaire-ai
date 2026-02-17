'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import WorkflowPage from '@/components/workflow/WorkflowPage'
import type { TypeActe } from '@/types/workflow'

function WorkflowContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const typeParam = searchParams?.get('type') as TypeActe | null

  return (
    <div className="h-screen w-screen overflow-hidden bg-ivory">
      <WorkflowPage
        onBack={() => router.push('/app')}
        initialType={typeParam || undefined}
      />
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
