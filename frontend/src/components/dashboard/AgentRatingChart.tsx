import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { AgentFeedback } from '../../api/types'
import { chartColorForIndex } from '../../lib/theme'

export function AgentRatingChart({ data }: { data?: AgentFeedback }) {
  const chartData = data
    ? Object.entries(data).map(([agent, entry]) => ({
        agent,
        positive_pct: Math.round(entry.positive_rate * 100),
      }))
    : []

  return (
    <div className="rounded-xl border border-getnet-100 bg-surface-card p-4 shadow-sm" data-testid="agent-rating-chart">
      <h3 className="text-sm font-semibold text-getnet-900">Avaliação por agente</h3>
      <div className="mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-getnet-100)" />
            <XAxis dataKey="agent" tick={{ fontSize: 12, fill: 'var(--color-getnet-700)' }} />
            <YAxis
              allowDecimals={false}
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
              tick={{ fontSize: 12, fill: 'var(--color-getnet-700)' }}
            />
            <Tooltip formatter={(value) => [`${value}%`, '% positiva']} />
            <Bar dataKey="positive_pct" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={entry.agent} fill={chartColorForIndex(index)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      {chartData.length === 0 && (
        <p className="mt-2 text-xs text-getnet-700">Nenhuma avaliação recebida ainda.</p>
      )}
    </div>
  )
}
