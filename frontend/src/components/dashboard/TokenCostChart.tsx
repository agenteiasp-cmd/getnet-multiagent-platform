import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { TokenUsage } from '../../api/types'
import { BRAND_RED, INK } from '../../lib/theme'

export function TokenCostChart({ data }: { data?: TokenUsage }) {
  const chartData = data
    ? data.breakdown.map((entry) => ({
        label: `${entry.agent_used}${entry.model ? ` (${entry.model})` : ''}`,
        prompt_tokens: entry.prompt_tokens,
        completion_tokens: entry.completion_tokens,
      }))
    : []

  return (
    <div className="rounded-xl border border-getnet-100 bg-surface-card p-4 shadow-sm" data-testid="token-cost-chart">
      <h3 className="text-sm font-semibold text-getnet-900">Tokens por agente/modelo</h3>
      <div className="mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-getnet-100)" />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: 'var(--color-getnet-700)' }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: 'var(--color-getnet-700)' }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="prompt_tokens" name="Prompt" stackId="tokens" fill={BRAND_RED} />
            <Bar dataKey="completion_tokens" name="Completion" stackId="tokens" fill={INK} radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {data && (
        <p className="mt-2 text-xs text-getnet-600" data-testid="token-cost-total">
          Custo estimado total: US$ {data.total_estimated_cost_usd.toFixed(4)}
        </p>
      )}
    </div>
  )
}
