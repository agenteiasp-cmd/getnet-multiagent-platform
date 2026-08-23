import type { Source } from '../../api/types'

export function SourcesList({ sources }: { sources: Source[] }) {
  return (
    <div className="px-1" data-testid="sources-list">
      <p className="text-[10px] font-semibold uppercase tracking-wide text-getnet-600">Fontes</p>
      <ul className="mt-1 space-y-0.5">
        {sources.map((source) => (
          <li key={source.url}>
            <a
              href={source.url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-getnet-600 underline decoration-getnet-300 hover:text-getnet-800"
            >
              {source.title || source.url}
            </a>
          </li>
        ))}
      </ul>
    </div>
  )
}
