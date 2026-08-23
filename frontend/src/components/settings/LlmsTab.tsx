import { AVAILABLE_MODELS, type AgentConfigMap, type AgentConfigUpdate } from '../../api/types'

const AGENT_LABELS: Record<string, string> = {
  router: 'Router',
  knowledge: 'Knowledge',
  support: 'Support',
  escalation: 'Escalation',
}

interface LlmsTabProps {
  configs: AgentConfigMap
  onUpdate: (agent: string, updates: AgentConfigUpdate) => void
}

export function LlmsTab({ configs, onUpdate }: LlmsTabProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-getnet-100 bg-surface-card" data-testid="llms-tab">
      <table className="w-full text-left text-xs">
        <thead>
          <tr className="border-b border-getnet-100 text-getnet-700">
            <th className="p-3">Agente</th>
            <th className="p-3">Modelo</th>
            <th className="p-3">Uso máximo de tokens</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(configs).map(([agent, config]) => (
            <tr key={agent} className="border-b border-getnet-50 last:border-0">
              <td className="p-3 font-medium text-getnet-900">{AGENT_LABELS[agent] ?? agent}</td>
              <td className="p-3">
                <select
                  aria-label={`Modelo de ${AGENT_LABELS[agent] ?? agent}`}
                  value={config.model ?? ''}
                  onChange={(event) => onUpdate(agent, { model: event.target.value })}
                  className="rounded-lg border border-getnet-200 bg-surface-card px-2 py-1 text-getnet-900"
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
              </td>
              <td className="p-3 text-getnet-600">{config.max_tokens ?? 'Sem limite'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
