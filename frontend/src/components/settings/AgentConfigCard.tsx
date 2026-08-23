import { useEffect, useState } from 'react'
import { AVAILABLE_MODELS, type AgentConfig, type AgentConfigUpdate } from '../../api/types'

const AGENT_LABELS: Record<string, string> = {
  router: 'Router',
  knowledge: 'Knowledge',
  support: 'Support',
  escalation: 'Escalation',
}

interface AgentConfigCardProps {
  agent: string
  config: AgentConfig
  onSave: (agent: string, prompt: string) => void
  onRestoreDefault: (agent: string) => void
  onUpdate: (agent: string, updates: AgentConfigUpdate) => void
}

export function AgentConfigCard({ agent, config, onSave, onRestoreDefault, onUpdate }: AgentConfigCardProps) {
  const [promptDraft, setPromptDraft] = useState(config.prompt)
  const [maxTokensDraft, setMaxTokensDraft] = useState(config.max_tokens?.toString() ?? '')

  useEffect(() => {
    setPromptDraft(config.prompt)
  }, [config.prompt])

  useEffect(() => {
    setMaxTokensDraft(config.max_tokens?.toString() ?? '')
  }, [config.max_tokens])

  function toggleFeature(feature: string, disable: boolean) {
    const current = config.disabled_features ?? []
    const next = disable ? [...current, feature] : current.filter((f) => f !== feature)
    onUpdate(agent, { disabled_features: next })
  }

  function commitMaxTokens() {
    const parsed = Number(maxTokensDraft)
    if (maxTokensDraft.trim() !== '' && Number.isFinite(parsed) && parsed > 0) {
      onUpdate(agent, { max_tokens: parsed })
    }
  }

  return (
    <div
      className="rounded-xl border border-getnet-100 bg-surface-card p-4 shadow-sm"
      data-testid="agent-config-card"
      data-agent={agent}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-getnet-900">{AGENT_LABELS[agent] ?? agent}</h3>
        <label className="flex items-center gap-2 text-xs text-getnet-600">
          <span data-testid="agent-enabled-state">{config.enabled ? 'Ativado' : 'Desativado'}</span>
          <input
            type="checkbox"
            aria-label={`Ativar/desativar ${AGENT_LABELS[agent] ?? agent}`}
            checked={config.enabled}
            onChange={(event) => onUpdate(agent, { enabled: event.target.checked })}
            className="h-4 w-4 accent-getnet-500"
          />
        </label>
      </div>

      <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-getnet-600">
        <div>
          <label htmlFor={`model-${agent}`} className="uppercase text-getnet-400">
            LLM
          </label>
          <select
            id={`model-${agent}`}
            value={config.model ?? ''}
            onChange={(event) => onUpdate(agent, { model: event.target.value })}
            className="mt-1 w-full rounded-lg border border-getnet-200 bg-surface-card px-2 py-1 text-xs text-getnet-900"
          >
            <option value="" disabled>
              —
            </option>
            {AVAILABLE_MODELS.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor={`max-tokens-${agent}`} className="uppercase text-getnet-400">
            Uso máximo de tokens
          </label>
          <input
            id={`max-tokens-${agent}`}
            type="number"
            min={1}
            placeholder="Sem limite"
            value={maxTokensDraft}
            onChange={(event) => setMaxTokensDraft(event.target.value)}
            onBlur={commitMaxTokens}
            className="mt-1 w-full rounded-lg border border-getnet-200 bg-surface-card px-2 py-1 text-xs text-getnet-900"
          />
        </div>
      </div>

      {config.tools.length > 0 && (
        <div className="mt-3 text-xs text-getnet-600">
          <p className="uppercase text-getnet-400">Tools</p>
          <ul className="mt-1 space-y-1">
            {config.tools.map((tool) => {
              const isDisabled = (config.disabled_features ?? []).includes(tool)
              return (
                <li key={tool} className="flex items-center justify-between">
                  <span className={isDisabled ? 'text-getnet-400 line-through' : ''}>{tool}</span>
                  <label className="flex items-center gap-1 text-[10px]">
                    <span>Desabilitar</span>
                    <input
                      type="checkbox"
                      aria-label={`Desabilitar ${tool}`}
                      checked={isDisabled}
                      onChange={(event) => toggleFeature(tool, event.target.checked)}
                      className="h-3 w-3 accent-getnet-500"
                    />
                  </label>
                </li>
              )
            })}
          </ul>
        </div>
      )}

      <div className="mt-3">
        <label htmlFor={`prompt-${agent}`} className="text-xs font-medium uppercase text-getnet-700">
          Prompt
        </label>
        <textarea
          id={`prompt-${agent}`}
          value={promptDraft}
          onChange={(event) => setPromptDraft(event.target.value)}
          rows={4}
          className="mt-1 w-full rounded-lg border border-getnet-200 p-2 text-xs text-getnet-900 outline-none focus:border-getnet-500"
        />
      </div>

      <div className="mt-3 flex gap-2">
        <button
          type="button"
          onClick={() => onSave(agent, promptDraft)}
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
