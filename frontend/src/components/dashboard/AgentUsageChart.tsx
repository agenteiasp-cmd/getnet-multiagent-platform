import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import type { AgentUsage } from '../../api/types'
import { chartColorForIndex } from '../../lib/theme'

export function AgentUsageChart({ data }: { data?: AgentUsage }) {
  const chartData = data ? Object.entries(data).map(([agent, count]) => ({ agent, count })) : []

  return (
    <div className="rounded-xl border border-getnet-100 bg-surface-card p-4 shadow-sm" data-testid="agent-usage-chart">
      <h3 className="text-sm font-semibold text-getnet-900">Uso por agente</h3>
      <div className="mt-4 h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--color-getnet-100)" />
            <XAxis dataKey="agent" tick={{ fontSize: 12, fill: 'var(--color-getnet-700)' }} />
            <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: 'var(--color-getnet-700)' }} />
            <Tooltip />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={entry.agent} fill={chartColorForIndex(index)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
