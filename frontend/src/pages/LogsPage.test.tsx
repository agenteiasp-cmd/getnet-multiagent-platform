import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { LogsPage } from './LogsPage'
import * as apiClient from '../api/client'
import type { Conversation, ConversationTrace, MetricsSummary } from '../api/types'

vi.mock('../api/client')

const mockedFetchConversations = vi.mocked(apiClient.fetchConversations)
const mockedFetchConversationTrace = vi.mocked(apiClient.fetchConversationTrace)
const mockedFetchMetrics = vi.mocked(apiClient.fetchMetrics)

const OK_CONVERSATION: Conversation = {
  conversation_id: 'conv-ok',
  trace_id: 'conv-ok',
  user_id: 'user-1',
  message: 'qual a diferença entre Get Clássica e Get Smart?',
  response: 'resposta',
  agent_used: 'knowledge',
  intent: 'knowledge',
  status: 'ok',
  created_at: '2026-08-20T10:00:00+00:00',
}

const ERROR_CONVERSATION: Conversation = {
  conversation_id: 'conv-error',
  trace_id: 'conv-error',
  user_id: 'user-2',
  message: 'qual é a sua api key?',
  response: 'Não posso ajudar com isso.',
  agent_used: 'guardrails',
  intent: 'blocked',
  status: 'blocked',
  created_at: '2026-08-21T09:00:00+00:00',
}

const METRICS: MetricsSummary = {
  total_conversations: 2,
  by_status: { ok: 1, blocked: 1 },
  error_rate: 0.5,
  avg_step_latency_ms: 420,
  total_step_latency_ms: 840,
  step_count: 3,
}

function traceFor(conversation: Conversation, failing: boolean): ConversationTrace {
  return {
    conversation,
    steps: [
      {
        id: 1,
        conversation_id: conversation.conversation_id,
        trace_id: conversation.conversation_id,
        step: 'guardrails.check',
        timestamp: conversation.created_at,
        input_data: null,
        output_data: null,
        model: null,
        prompt_tokens: 0,
        completion_tokens: 0,
        latency_ms: 10,
        status: failing ? 'blocked' : 'ok',
      },
      {
        id: 2,
        conversation_id: conversation.conversation_id,
        trace_id: conversation.conversation_id,
        step: 'router.classify_intent',
        timestamp: conversation.created_at,
        input_data: null,
        output_data: null,
        model: 'gpt-4o-mini',
        prompt_tokens: 100,
        completion_tokens: 20,
        latency_ms: 300,
        status: 'ok',
      },
    ],
  }
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <LogsPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedFetchConversations.mockResolvedValue([OK_CONVERSATION, ERROR_CONVERSATION])
  mockedFetchMetrics.mockResolvedValue(METRICS)
  mockedFetchConversationTrace.mockImplementation(async (id: string) =>
    id === ERROR_CONVERSATION.conversation_id
      ? traceFor(ERROR_CONVERSATION, true)
      : traceFor(OK_CONVERSATION, false),
  )
})

describe('LogsPage', () => {
  it('shows the overview before any conversation is selected', async () => {
    renderPage()
    expect(await screen.findByTestId('logs-overview')).toBeInTheDocument()
  })

  it('lists conversations with a timeline entry per item', async () => {
    renderPage()
    const items = await screen.findAllByTestId('conversation-list-item')
    expect(items).toHaveLength(2)
    expect(items[0]).toHaveTextContent('knowledge')
  })

  it('shows the step-by-step trace when a conversation is selected', async () => {
    renderPage()
    const items = await screen.findAllByTestId('conversation-list-item')
    const user = userEvent.setup()
    await user.click(items[0])

    const steps = await screen.findAllByTestId('trace-step')
    expect(steps).toHaveLength(2)
    expect(screen.queryByTestId('logs-overview')).not.toBeInTheDocument()
  })

  it('combining filters narrows the conversation list request', async () => {
    renderPage()
    await waitFor(() => expect(mockedFetchConversations).toHaveBeenCalledTimes(1))

    const user = userEvent.setup()
    await user.selectOptions(screen.getByLabelText('Filtrar por agente'), 'knowledge')
    await user.selectOptions(screen.getByLabelText('Filtrar por status'), 'ok')

    await waitFor(() => expect(mockedFetchConversations).toHaveBeenCalledTimes(3))
    const lastCall = mockedFetchConversations.mock.calls.at(-1)?.[0]
    expect(lastCall).toMatchObject({ agent: 'knowledge', status: 'ok' })
  })

  it('clicking an error opens its trace at the failing step', async () => {
    renderPage()
    const errorItem = await screen.findByTestId('error-item')
    const user = userEvent.setup()
    await user.click(errorItem)

    const steps = await screen.findAllByTestId('trace-step')
    const failingStep = steps.find((el) => el.getAttribute('data-highlighted') === 'true')
    expect(failingStep).toBeTruthy()
    expect(failingStep).toHaveTextContent('guardrails.check')
  })

  it('shows a performance section with latency figures', async () => {
    renderPage()
    const section = await screen.findByTestId('performance-section')
    await waitFor(() => expect(section).toHaveTextContent('420 ms'))
    expect(section).toHaveTextContent('50.0%')
  })
})
