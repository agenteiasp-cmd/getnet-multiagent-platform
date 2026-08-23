import type { ReactNode } from 'react'
import { Sidebar } from './Sidebar'

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen w-full overflow-hidden bg-surface">
      <Sidebar />
      <main data-testid="page-content" className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
