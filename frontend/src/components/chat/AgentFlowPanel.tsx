import { useEffect, useState } from 'react'
import type { ConversationTrace } from '../../api/types'
import { friendlyStepLabel } from '../../lib/stepLabels'

// These two steps always run first, before the router hands off to a
// specific agent - we know their friendly labels ahead of time and can
// reveal them progressively while waiting for the real trace. Which agent
// answers is only known once the response arrives, so the last step stays
// a generic "consulting" spinner until then (see design.md "Agent flow
// panel real-time reveal").
const SIMULATED_STEPS = [
  { label: 'Verificando sua mensagem', delayMs: 450 },
  { label: 'Entendendo o que você precisa', delayMs: 1250 },
]

const AGENT_LABELS: Record<string, string> = {
  router: 'Router',
  knowledge: 'Knowledge',
  support: 'Support',
  escalation: 'Escalation',
  guardrails: 'Guardrails',
}

function statusIcon(status: string): string {
  if (status === 'ok') return '✅'
  if (status === 'truncated') return '⚠️'
  return '❌'
}

interface AgentFlowPanelProps {
  isProcessing: boolean
  trace: ConversationTrace | null
  agentUsed?: string
}

export function AgentFlowPanel({ isProcessing, trace, agentUsed }: AgentFlowPanelProps) {
  const [showTechnical, setShowTechnical] = useState(false)
  const [simulatedDone, setSimulatedDone] = useState(0)

  useEffect(() => {
    if (!isProcessing) {
      setSimulatedDone(0)
      return
    }
    const timers = SIMULATED_STEPS.map((step, index) =>
      setTimeout(() => setSimulatedDone((done) => Math.max(done, index + 1)), step.delayMs),
    )
    return () => timers.forEach(clearTimeout)
  }, [isProcessing])

  return (
    <aside
      className="w-80 shrink-0 overflow-y-auto border-l border-getnet-100 bg-surface-card p-4"
      data-testid="agent-flow-panel"
    >
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-getnet-900">Fluxo do agente</h2>
        {trace && !isProcessing && (
          <button
            type="button"
            onClick={() => setShowTechnical((v) => !v)}
            aria-pressed={showTechnical}
            className="text-[10px] font-medium text-getnet-700 underline hover:text-getnet-700"
          >
            {showTechnical ? 'Ocultar detalhes técnicos' : 'Detalhes técnicos'}
          </button>
        )}
      </div>

      {isProcessing && (
        <div data-testid="processing-indicator">
          <div className="mt-3 flex items-center gap-2 text-xs text-getnet-600">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-getnet-500" />
            Processando sua mensagem...
          </div>

          <ul className="mt-3 space-y-2" data-testid="agent-flow-steps-live">
            {SIMULATED_STEPS.map((step, index) => {
              const done = index < simulatedDone
              return (
                <li key={step.label} className="rounded-lg border border-getnet-100 p-3 text-xs">
                  <p className="flex items-center gap-2 font-semibold text-getnet-900">
                    {done ? (
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden="true">
                        <path d="M20 6 9 17l-5-5" />
                      </svg>
                    ) : (
                      <span className="inline-block h-3.5 w-3.5 rounded-full border-2 border-getnet-200" aria-hidden="true" />
                    )}
                    {step.label}
                  </p>
                </li>
              )
            })}
            <li className="rounded-lg border border-getnet-500 bg-getnet-50 p-3 text-xs">
              <p className="flex items-center gap-2 font-semibold text-getnet-900">
                {simulatedDone >= SIMULATED_STEPS.length ? (
                  <svg
                    className="animate-spin text-getnet-500"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.4"
                    strokeLinecap="round"
                    aria-hidden="true"
                  >
                    <path d="M12 2a10 10 0 0 1 10 10" />
                  </svg>
                ) : (
                  <span className="inline-block h-3.5 w-3.5 rounded-full border-2 border-getnet-200" aria-hidden="true" />
                )}
                Consultando o agente responsável...
              </p>
              <p className="mt-0.5 text-getnet-600">
                {simulatedDone >= SIMULATED_STEPS.length ? 'em andamento' : ''}
              </p>
            </li>
          </ul>

          <p className="mt-4 text-xs text-getnet-700">
            Agente ativo: <span className="font-semibold text-getnet-700">aguardando…</span>
          </p>
        </div>
      )}

      {!isProcessing && !trace && (
        <p className="mt-4 text-sm text-getnet-700">
          Envie uma mensagem para ver o fluxo dos agentes aqui.
        </p>
      )}

      {!isProcessing && trace && (
        <ul className="mt-4 space-y-3" data-testid="agent-flow-steps">
          {trace.steps.map((step) => {
            const isActiveAgent = Boolean(agentUsed && step.step.startsWith(agentUsed))
            const totalTokens = step.prompt_tokens + step.completion_tokens
            return (
              <li
                key={step.id}
                data-testid="agent-flow-step"
                data-active={isActiveAgent}
                className={`rounded-lg border p-3 text-xs ${
                  isActiveAgent ? 'border-getnet-500 bg-getnet-50' : 'border-getnet-100'
                }`}
              >
                <p className="flex items-center gap-1.5 font-semibold text-getnet-900">
                  <span aria-hidden="true">{statusIcon(step.status)}</span>
                  <span data-testid="agent-flow-step-label">{friendlyStepLabel(step.step)}</span>
                </p>
                <p className="mt-0.5 text-getnet-600">{(step.latency_ms / 1000).toFixed(1)}s</p>

                {showTechnical && (
                  <p className="mt-1 text-getnet-700" data-testid="agent-flow-step-technical">
                    {step.step}
                    {step.model ? ` · ${step.model}` : ''}
                    {totalTokens > 0 ? ` · ${totalTokens} tokens` : ''}
                    {step.status !== 'ok' ? ` · ${step.status}` : ''}
                  </p>
                )}
              </li>
            )
          })}
        </ul>
      )}

      {agentUsed && (
        <p className="mt-4 text-xs text-getnet-700" data-testid="active-agent-label">
          Agente ativo:{' '}
          <span className="font-semibold text-getnet-900">
            {AGENT_LABELS[agentUsed] ?? agentUsed}
          </span>
        </p>
      )}
    </aside>
  )
}
