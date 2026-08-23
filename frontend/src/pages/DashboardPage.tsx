import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchAgentsFeedback, fetchAgentsUsage, fetchMetrics, fetchTokensUsage } from '../api/client'
import { AgentRatingChart } from '../components/dashboard/AgentRatingChart'
import { AgentUsageChart } from '../components/dashboard/AgentUsageChart'
import { CollapsibleSection } from '../components/dashboard/CollapsibleSection'
import { PeriodFilter } from '../components/dashboard/PeriodFilter'
import { ServiceVolumeChart } from '../components/dashboard/ServiceVolumeChart'
import { StatCard } from '../components/dashboard/StatCard'
import { TokenCostChart } from '../components/dashboard/TokenCostChart'
import { periodToRange } from '../lib/period'
import { LogsPage } from './LogsPage'

export function DashboardPage() {
  const [period, setPeriod] = useState('30d')
  // Memoized so `range` (and the query keys derived from it) only change
  // when the user picks a different period, not on every render - an
  // unmemoized `new Date()` in periodToRange would otherwise produce a
  // new queryKey on every render and refetch in an infinite loop.
  const range = useMemo(() => periodToRange(period), [period])

  const metricsQuery = useQuery({
    queryKey: ['metrics', range.start, range.end],
    queryFn: () => fetchMetrics(range),
  })
  const agentsUsageQuery = useQuery({
    queryKey: ['agents-usage', range.start, range.end],
    queryFn: () => fetchAgentsUsage(range),
  })
  const tokensUsageQuery = useQuery({
    queryKey: ['tokens-usage', range.start, range.end],
    queryFn: () => fetchTokensUsage(range),
  })
  const agentsFeedbackQuery = useQuery({
    queryKey: ['agents-feedback', range.start, range.end],
    queryFn: () => fetchAgentsFeedback(range),
  })

  const metrics = metricsQuery.data
  const tokens = tokensUsageQuery.data
  const avgTokensPerConversation =
    tokens && metrics?.total_conversations
      ? Math.round((tokens.total_prompt_tokens + tokens.total_completion_tokens) / metrics.total_conversations)
      : null

  return (
    <div className="p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-getnet-900">Dashboard</h1>
          <p className="text-xs text-getnet-700">Visão geral do atendimento multiagente</p>
        </div>
        <PeriodFilter value={period} onChange={setPeriod} />
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard label="Conversas" value={String(metrics?.total_conversations ?? '—')} />
        <StatCard
          label="Taxa de erro"
          value={metrics ? `${(metrics.error_rate * 100).toFixed(1)}%` : '—'}
        />
        <StatCard
          label="Latência média"
          value={metrics ? `${metrics.avg_step_latency_ms.toFixed(0)} ms` : '—'}
        />
        <StatCard
          label="Tokens médios/conversa"
          value={avgTokensPerConversation !== null ? String(avgTokensPerConversation) : '—'}
        />
        <StatCard
          label="Custo estimado"
          value={tokens ? `US$ ${tokens.total_estimated_cost_usd.toFixed(4)}` : '—'}
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ServiceVolumeChart data={metricsQuery.data} />
        <AgentUsageChart data={agentsUsageQuery.data} />
        <AgentRatingChart data={agentsFeedbackQuery.data} />
        <div className="lg:col-span-2">
          <TokenCostChart data={tokensUsageQuery.data} />
        </div>
      </div>

      <CollapsibleSection
        title="Logs & Observabilidade"
        subtitle="Conversas, traces, erros e performance detalhados"
      >
        <LogsPage />
      </CollapsibleSection>
    </div>
  )
}
