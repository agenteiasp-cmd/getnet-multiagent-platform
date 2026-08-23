import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatPage } from './ChatPage'
import * as apiClient from '../api/client'
import type { ChatResponse, ConversationTrace } from '../api/types'

vi.mock('../api/client')

const mockedSendChatMessage = vi.mocked(apiClient.sendChatMessage)
const mockedFetchConversationTrace = vi.mocked(apiClient.fetchConversationTrace)
const mockedSubmitFeedback = vi.mocked(apiClient.submitFeedback)

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((r) => {
    resolve = r
  })
  return { promise, resolve }
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedFetchConversationTrace.mockResolvedValue({
    conversation: {
      conversation_id: 'trace-1',
      trace_id: 'trace-1',
      user_id: 'user-1',
      message: 'oi',
      response: 'Olá!',
      agent_used: 'router',
      intent: 'chitchat',
      status: 'ok',
      created_at: new Date().toISOString(),
    },
    steps: [],
  } satisfies ConversationTrace)
})

describe('ChatPage', () => {
  it('renders differentiated user and AI messages with timestamps', async () => {
    mockedSendChatMessage.mockResolvedValue({
      response: 'Olá! Como posso ajudar?',
      agent_used: 'router',
      intent: 'chitchat',
      sources: [],
      tools_used: ['classify_intent'],
      trace_id: 'trace-1',
    } satisfies ChatResponse)

    render(<ChatPage />)
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('Mensagem'), 'oi, tudo bem?')
    await user.click(screen.getByRole('button', { name: 'Enviar' }))

    await waitFor(() => {
      expect(screen.getAllByTestId('message-bubble')).toHaveLength(2)
    })

    const bubbles = screen.getAllByTestId('message-bubble')
    expect(bubbles[0]).toHaveAttribute('data-role', 'user')
    expect(bubbles[0]).toHaveTextContent('oi, tudo bem?')
    expect(bubbles[1]).toHaveAttribute('data-role', 'assistant')
    expect(bubbles[1]).toHaveTextContent('Olá! Como posso ajudar?')
    // Timestamp rendered in HH:MM format for both messages.
    expect(bubbles[0].textContent).toMatch(/\d{2}:\d{2}/)
    expect(bubbles[1].textContent).toMatch(/\d{2}:\d{2}/)
  })

  it('shows a processing indicator while the request is in flight and clears it on response', async () => {
    const pending = deferred<ChatResponse>()
    mockedSendChatMessage.mockReturnValue(pending.promise)

    render(<ChatPage />)
    const user = userEvent.setup()

    await user.type(screen.getByLabelText('Mensagem'), 'oi')
    await user.click(screen.getByRole('button', { name: 'Enviar' }))

    expect(await screen.findByTestId('chat-processing-indicator')).toBeInTheDocument()
    expect(screen.getByTestId('processing-indicator')).toBeInTheDocument()

    pending.resolve({
      response: 'Olá!',
      agent_used: 'router',
      intent: 'chitchat',
      sources: [],
      tools_used: ['classify_intent'],
      trace_id: 'trace-1',
    })

    await waitFor(() => {
      expect(screen.queryByTestId('chat-processing-indicator')).not.toBeInTheDocument()
    })
    expect(screen.queryByTestId('processing-indicator')).not.toBeInTheDocument()
  })

  it('renders sources only when the response includes them', async () => {
    mockedSendChatMessage.mockResolvedValue({
      response: 'A Get Clássica custa R$ 79,90/mês.',
      agent_used: 'knowledge',
      intent: 'knowledge',
      sources: [{ url: 'https://site.getnet.com.br/maquininha/get-classica/', title: 'get-classica' }],
      tools_used: ['pinecone_retrieval'],
      trace_id: 'trace-2',
    } satisfies ChatResponse)

    render(<ChatPage />)
    const user = userEvent.setup()
    await user.type(screen.getByLabelText('Mensagem'), 'qual o preço da get classica?')
    await user.click(screen.getByRole('button', { name: 'Enviar' }))

    const sourcesList = await screen.findByTestId('sources-list')
    expect(within(sourcesList).getByText('get-classica')).toBeInTheDocument()
  })

  it('renders no sources section when the response has an empty sources array', async () => {
    mockedSendChatMessage.mockResolvedValue({
      response: 'Olá!',
      agent_used: 'router',
      intent: 'chitchat',
      sources: [],
      tools_used: ['classify_intent'],
      trace_id: 'trace-3',
    } satisfies ChatResponse)

    render(<ChatPage />)
    const user = userEvent.setup()
    await user.type(screen.getByLabelText('Mensagem'), 'oi')
    await user.click(screen.getByRole('button', { name: 'Enviar' }))

    await waitFor(() => {
      expect(screen.getAllByTestId('message-bubble')).toHaveLength(2)
    })
    expect(screen.queryByTestId('sources-list')).not.toBeInTheDocument()
  })

  it('updates the agent-flow panel during and after a request', async () => {
    const pending = deferred<ChatResponse>()
    mockedSendChatMessage.mockReturnValue(pending.promise)
    mockedFetchConversationTrace.mockResolvedValue({
      conversation: {
        conversation_id: 'trace-4',
        trace_id: 'trace-4',
        user_id: 'user-1',
        message: 'quero falar com humano',
        response: 'Encaminhando...',
        agent_used: 'escalation',
        intent: 'escalation',
        status: 'ok',
        created_at: new Date().toISOString(),
      },
      steps: [
        {
          id: 1,
          conversation_id: 'trace-4',
          trace_id: 'trace-4',
          step: 'guardrails.check',
          timestamp: new Date().toISOString(),
          input_data: null,
          output_data: null,
          model: null,
          prompt_tokens: 0,
          completion_tokens: 0,
          latency_ms: 12.3,
          status: 'ok',
        },
        {
          id: 2,
          conversation_id: 'trace-4',
          trace_id: 'trace-4',
          step: 'escalation.mock_handoff_call',
          timestamp: new Date().toISOString(),
          input_data: null,
          output_data: null,
          model: null,
          prompt_tokens: 0,
          completion_tokens: 0,
          latency_ms: 5.0,
          status: 'ok',
        },
      ],
    })

    render(<ChatPage />)
    const user = userEvent.setup()
    await user.type(screen.getByLabelText('Mensagem'), 'quero falar com humano')
    await user.click(screen.getByRole('button', { name: 'Enviar' }))

    expect(screen.getByTestId('agent-flow-panel')).toHaveTextContent('Processando')

    pending.resolve({
      response: 'Encaminhando para um atendente.',
      agent_used: 'escalation',
      intent: 'escalation',
      sources: [],
      tools_used: ['mock_handoff_call'],
      trace_id: 'trace-4',
    })

    await waitFor(() => {
      expect(screen.getByTestId('active-agent-label')).toHaveTextContent('Escalation')
    })
    const steps = screen.getAllByTestId('agent-flow-step')
    expect(steps).toHaveLength(2)
    expect(steps[1]).toHaveAttribute('data-active', 'true')
  })

  it('shows friendly step labels by default and technical details only when expanded', async () => {
    mockedSendChatMessage.mockResolvedValue({
      response: 'A Get Clássica...',
      agent_used: 'knowledge',
      intent: 'knowledge',
      sources: [],
      tools_used: ['pinecone_retrieval'],
      trace_id: 'trace-7',
    })
    mockedFetchConversationTrace.mockResolvedValue({
      conversation: {
        conversation_id: 'trace-7',
        trace_id: 'trace-7',
        user_id: 'user-1',
        message: 'qual a diferença?',
        response: 'A Get Clássica...',
        agent_used: 'knowledge',
        intent: 'knowledge',
        status: 'ok',
        created_at: new Date().toISOString(),
      },
      steps: [
        {
          id: 1,
          conversation_id: 'trace-7',
          trace_id: 'trace-7',
          step: 'guardrails.check',
          timestamp: new Date().toISOString(),
          input_data: null,
          output_data: null,
          model: null,
          prompt_tokens: 0,
          completion_tokens: 0,
          latency_ms: 500,
          status: 'ok',
        },
        {
          id: 2,
          conversation_id: 'trace-7',
          trace_id: 'trace-7',
          step: 'knowledge.rag_generate',
          timestamp: new Date().toISOString(),
          input_data: null,
          output_data: null,
          model: 'gpt-4o-mini',
          prompt_tokens: 300,
          completion_tokens: 80,
          latency_ms: 1500,
          status: 'ok',
        },
      ],
    })

    render(<ChatPage />)
    const user = userEvent.setup()
    await user.type(screen.getByLabelText('Mensagem'), 'qual a diferença?')
    await user.click(screen.getByRole('button', { name: 'Enviar' }))

    const labels = await screen.findAllByTestId('agent-flow-step-label')
    expect(labels.map((el) => el.textContent)).toEqual([
      'Verificando sua mensagem',
      'Buscando nas informações da Getnet',
    ])
    // Duration is shown in seconds, not milliseconds, and no technical
    // name/model/tokens are visible by default.
    expect(screen.getByTestId('agent-flow-panel')).toHaveTextContent('1.5s')
    expect(screen.queryByText('guardrails.check')).not.toBeInTheDocument()
    expect(screen.queryByText(/gpt-4o-mini/)).not.toBeInTheDocument()
    expect(screen.queryByTestId('agent-flow-step-technical')).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'Detalhes técnicos' }))

    const technicalDetails = screen.getAllByTestId('agent-flow-step-technical')
    expect(technicalDetails[1]).toHaveTextContent('knowledge.rag_generate')
    expect(technicalDetails[1]).toHaveTextContent('gpt-4o-mini')
    expect(technicalDetails[1]).toHaveTextContent('380 tokens')
  })

  it('clicking a quick reply sends its associated message', async () => {
    mockedSendChatMessage.mockResolvedValue({
      response: 'Resposta',
      agent_used: 'knowledge',
      intent: 'knowledge',
      sources: [],
      tools_used: [],
      trace_id: 'trace-5',
    })

    render(<ChatPage />)
    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: 'Diferença entre maquininhas' }))

    await waitFor(() => {
      expect(mockedSendChatMessage).toHaveBeenCalledWith(
        expect.objectContaining({ message: expect.stringContaining('Get Clássica') }),
      )
    })
  })

  it('submitting feedback posts the trace_id/agent_used and reflects submitted state', async () => {
    mockedSendChatMessage.mockResolvedValue({
      response: 'A Get Clássica...',
      agent_used: 'knowledge',
      intent: 'knowledge',
      sources: [],
      tools_used: ['pinecone_retrieval'],
      trace_id: 'trace-6',
    })
    mockedSubmitFeedback.mockResolvedValue(undefined)

    render(<ChatPage />)
    const user = userEvent.setup()
    await user.type(screen.getByLabelText('Mensagem'), 'qual a diferença?')
    await user.click(screen.getByRole('button', { name: 'Enviar' }))

    const thumbsUp = await screen.findByLabelText('Avaliar positivamente')
    await user.click(thumbsUp)

    await waitFor(() => {
      expect(mockedSubmitFeedback).toHaveBeenCalledWith({
        trace_id: 'trace-6',
        agent_used: 'knowledge',
        rating: 1,
      })
    })
    expect(await screen.findByTestId('feedback-submitted')).toBeInTheDocument()
    expect(thumbsUp).toBeDisabled()
  })
})
