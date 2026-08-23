import { useEffect, useState } from 'react'
import type { AgentConfigMap } from '../../api/types'

const AGENT_LABELS: Record<string, string> = {
  router: 'Router',
  knowledge: 'Knowledge',
  support: 'Support',
  escalation: 'Escalation',
}

interface PromptsTabProps {
  configs: AgentConfigMap
  onSave: (agent: string, prompt: string) => void
  onRestoreDefault: (agent: string) => void
}

export function PromptsTab({ configs, onSave, onRestoreDefault }: PromptsTabProps) {
  return (
    <div className="space-y-4" data-testid="prompts-tab">
      {Object.entries(configs).map(([agent, config]) => (
        <PromptRow key={agent} agent={agent} prompt={config.prompt} onSave={onSave} onRestoreDefault={onRestoreDefault} />
      ))}
    </div>
  )
}

function PromptRow({
  agent,
  prompt,
  onSave,
  onRestoreDefault,
}: {
  agent: string
  prompt: string
  onSave: (agent: string, prompt: string) => void
  onRestoreDefault: (agent: string) => void
}) {
  const [draft, setDraft] = useState(prompt)

  useEffect(() => setDraft(prompt), [prompt])

  return (
    <div className="rounded-xl border border-getnet-100 bg-surface-card p-4">
      <p className="text-sm font-semibold text-getnet-900">{AGENT_LABELS[agent] ?? agent}</p>
      <textarea
        value={draft}
        onChange={(event) => setDraft(event.target.value)}
        rows={3}
        className="mt-2 w-full rounded-lg border border-getnet-200 p-2 text-xs text-getnet-900"
      />
      <div className="mt-2 flex gap-2">
        <button
          type="button"
          onClick={() => onSave(agent, draft)}
          className="rounded-lg bg-getnet-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-[#c1080f]"
        >
          Salvar
        </button>
        <button
          type="button"
          onClick={() => onRestoreDefault(agent)}
          className="rounded-lg border border-getnet-200 px-3 py-1.5 text-xs font-semibold text-getnet-700 hover:bg-getnet-50"
        >
          Restaurar padrão
        </button>
      </div>
    </div>
  )
}
