'use client'

import AppSidebar from '@/components/AppSidebar'
import AppHeader from '@/components/AppHeader'
import { ToastContainer } from '@/components/Toast'
import CommandPalette from '@/components/CommandPalette'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="h-screen w-screen overflow-hidden flex">
      <AppSidebar />
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        <AppHeader />
        <main className="flex-1 min-h-0 overflow-auto bg-ivory">
          {children}
        </main>
      </div>
      <ToastContainer />
      <CommandPalette />
    </div>
  )
}
