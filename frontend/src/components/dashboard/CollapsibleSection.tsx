import type { ReactNode } from 'react'

interface CollapsibleSectionProps {
  title: string
  subtitle?: string
  children: ReactNode
}

/** Native <details>/<summary>: collapsed by default, no state management
 * needed, and children stay mounted (state preserved) while collapsed. */
export function CollapsibleSection({ title, subtitle, children }: CollapsibleSectionProps) {
  return (
    <details
      className="mt-6 rounded-xl border border-getnet-100 bg-surface-card"
      data-testid="collapsible-section"
    >
      <summary className="flex cursor-pointer list-none items-center justify-between px-4 py-4">
        <div>
          <span className="text-sm font-semibold text-getnet-900">{title}</span>
          {subtitle && <p className="text-xs text-getnet-700">{subtitle}</p>}
        </div>
        <span aria-hidden="true" className="text-xs text-getnet-700">
          ▾
        </span>
      </summary>
      <div className="border-t border-getnet-100 p-4">{children}</div>
    </details>
  )
}
