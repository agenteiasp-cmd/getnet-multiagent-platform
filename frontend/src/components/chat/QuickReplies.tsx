import { QUICK_REPLIES } from '../../lib/quickReplies'

interface QuickRepliesProps {
  onSelect: (message: string) => void
  disabled?: boolean
}

export function QuickReplies({ onSelect, disabled }: QuickRepliesProps) {
  return (
    <div className="bg-surface px-6 pt-3" data-testid="quick-replies">
      <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-getnet-700">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true">
          <path d="M9 18h6M10 22h4M12 2a6 6 0 0 0-4 10.47c.55.5.86 1.2.86 1.93V15h6.28v-.6c0-.73.31-1.43.86-1.93A6 6 0 0 0 12 2Z" />
        </svg>
        Sugestões
      </div>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {QUICK_REPLIES.map((reply) => (
          <button
            key={reply.label}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(reply.message)}
            className="whitespace-nowrap rounded-lg border border-getnet-200 bg-transparent px-3.5 py-1.5 text-xs font-medium text-getnet-700 transition-colors hover:border-getnet-500 hover:text-getnet-500 disabled:opacity-50"
          >
            {reply.label}
          </button>
        ))}
      </div>
    </div>
  )
}
