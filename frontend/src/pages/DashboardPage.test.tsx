import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { DashboardPage } from './DashboardPage'
import * as apiClient from '../api/client'
import type { AgentFeedback, AgentUsage, MetricsSummary, TokenUsage } from '../api/types'

vi.mock('../api/client')

const mockedFetchMetrics = vi.mocked(apiClient.fetchMetrics)
const mockedFetchAgentsUsage = vi.mocked(apiClient.fetchAgentsUsage)
const mockedFetchTokensUsage = vi.mocked(apiClient.fetchTokensUsage)
const mockedFetchAgentsFeedback = vi.mocked(apiClient.fetchAgentsFeedback)
const mockedFetchConversations = vi.mocked(apiClient.fetchConversations)

const AGENTS_FEEDBACK: AgentFeedback = {
  knowledge: { total: 4, positive_rate: 0.75, avg_score: 0.5 },
}

const METRICS: MetricsSummary = {
  total_conversations: 42,
  by_status: { ok: 40, blocked: 2 },
  error_rate: 0.05,
  avg_step_latency_ms: 350,
  total_step_latency_ms: 14000,
  step_count: 120,
}

const AGENTS_USAGE: AgentUsage = { router: 10, knowledge: 15, support: 12, escalation: 5 }

const TOKENS_USAGE: TokenUsage = {
  total_prompt_tokens: 5000,
  total_completion_tokens: 1200,
  total_estimated_cost_usd: 0.0234,
  breakdown: [
    { model: 'gpt-4o-mini', agent_used: 'knowledge', prompt_tokens: 3000, completion_tokens: 800, estimated_cost_usd: 0.012 },
  ],
}

function renderWithQueryClient() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <DashboardPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedFetchMetrics.mockResolvedValue(METRICS)
  mockedFetchAgentsUsage.mockResolvedValue(AGENTS_USAGE)
  mockedFetchTokensUsage.mockResolvedValue(TOKENS_USAGE)
  mockedFetchAgentsFeedback.mockResolvedValue(AGENTS_FEEDBACK)
  mockedFetchConversations.mockResolvedValue([])
})

describe('DashboardPage', () => {
  it('changing the period filter re-fetches metrics with a new range', async () => {
    // fetchMetrics is shared with the embedded Logs & Observabilidade
    // section (its own independent date filter), so identify Dashboard's
    // own calls by their (defined) period-driven args instead of raw count.
    renderWithQueryClient()
    await waitFor(() => expect(mockedFetchAgentsUsage).toHaveBeenCalledTimes(1))
    const dashboardMetricsCalls = () =>
      mockedFetchMetrics.mock.calls.filter(([arg]) => arg?.start !== undefined)
    await waitFor(() => expect(dashboardMetricsCalls().length).toBeGreaterThanOrEqual(1))
    const firstCallRange = dashboardMetricsCalls()[0][0]

    const user = userEvent.setup()
    await user.selectOptions(screen.getByLabelText('Período'), '7d')

    await waitFor(() => expect(mockedFetchAgentsUsage).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(dashboardMetricsCalls().length).toBeGreaterThanOrEqual(2))
    const secondCallRange = dashboardMetricsCalls().at(-1)![0]
    expect(secondCallRange).not.toEqual(firstCallRange)
    expect(mockedFetchTokensUsage).toHaveBeenCalledTimes(2)
  })

  it('renders the service volume chart from GET /metrics', async () => {
    renderWithQueryClient()
    expect(await screen.findByTestId('service-volume-chart')).toHaveTextContent(
      'Volume de atendimentos por status',
    )
  })

  it('renders the agent usage chart from GET /agents/usage', async () => {
    renderWithQueryClient()
    expect(await screen.findByTestId('agent-usage-chart')).toHaveTextContent('Uso por agente')
  })

  it('renders the token/cost chart from GET /tokens/usage', async () => {
    renderWithQueryClient()
    const chart = await screen.findByTestId('token-cost-chart')
    expect(chart).toHaveTextContent('Tokens por agente/modelo')
    await waitFor(() => {
      expect(screen.getByTestId('token-cost-total')).toHaveTextContent('0.0234')
    })
  })

  it('renders the per-agent rating chart from GET /agents/feedback', async () => {
    renderWithQueryClient()
    expect(await screen.findByTestId('agent-rating-chart')).toHaveTextContent('Avaliação por agente')
  })

  it('embeds Logs & Observabilidade as a section collapsed by default that expands on toggle', async () => {
    renderWithQueryClient()
    const section = (await screen.findByTestId('collapsible-section')) as HTMLDetailsElement
    expect(section.open).toBe(false)
    expect(section).toHaveTextContent('Logs & Observabilidade')

    const user = userEvent.setup()
    await user.click(screen.getByText('Logs & Observabilidade'))

    expect(section.open).toBe(true)
    expect(within(section).getByTestId('logs-page')).toBeInTheDocument()
  })
})
