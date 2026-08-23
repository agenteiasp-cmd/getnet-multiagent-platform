import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { SettingsPage } from './SettingsPage'
import * as apiClient from '../api/client'
import type { AgentConfigMap } from '../api/types'

vi.mock('../api/client')

const mockedFetchAgentConfigs = vi.mocked(apiClient.fetchAgentConfigs)
const mockedUpdateAgentConfig = vi.mocked(apiClient.updateAgentConfig)
const mockedRestoreAgentConfigDefault = vi.mocked(apiClient.restoreAgentConfigDefault)
const mockedFetchTestCategories = vi.mocked(apiClient.fetchTestCategories)

const BASE_CONFIGS: AgentConfigMap = {
  router: {
    prompt: 'prompt do router',
    model: 'gpt-4o-mini',
    temperature: 0,
    tools: ['classify_intent'],
    enabled: true,
    max_tokens: null,
    disabled_features: [],
  },
  knowledge: {
    prompt: 'prompt do knowledge',
    model: 'gpt-4o-mini',
    temperature: 0.3,
    tools: ['pinecone_retrieval', 'tavily_web_search'],
    enabled: true,
    max_tokens: null,
    disabled_features: [],
  },
  support: {
    prompt: 'prompt do support',
    model: 'gpt-4o-mini',
    temperature: 0,
    tools: ['get_account_info'],
    enabled: true,
    max_tokens: null,
    disabled_features: [],
  },
  escalation: {
    prompt: '',
    model: null,
    temperature: null,
    tools: ['mock_handoff_call'],
    enabled: true,
    max_tokens: null,
    disabled_features: [],
  },
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <SettingsPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedFetchAgentConfigs.mockResolvedValue(structuredClone(BASE_CONFIGS))
  mockedFetchTestCategories.mockResolvedValue(['guardrails', 'escalation'])
})

describe('SettingsPage', () => {
  it('shows one config card per agent with prompt, LLM, temperature, tools, and enabled state', async () => {
    renderPage()
    const cards = await screen.findAllByTestId('agent-config-card')
    expect(cards).toHaveLength(4)

    const routerCard = cards.find((card) => card.getAttribute('data-agent') === 'router')!
    expect(within(routerCard).getByLabelText('LLM')).toHaveValue('gpt-4o-mini')
    expect(within(routerCard).getByText('classify_intent')).toBeInTheDocument()
    expect(within(routerCard).getByText('Ativado')).toBeInTheDocument()
  })

  it('saving an edited prompt persists it via PUT and reflects the new value', async () => {
    mockedUpdateAgentConfig.mockResolvedValue({ ...BASE_CONFIGS.support, prompt: 'novo prompt de teste' })
    mockedFetchAgentConfigs
      .mockResolvedValueOnce(structuredClone(BASE_CONFIGS))
      .mockResolvedValueOnce({ ...structuredClone(BASE_CONFIGS), support: { ...BASE_CONFIGS.support, prompt: 'novo prompt de teste' } })

    renderPage()
    const cards = await screen.findAllByTestId('agent-config-card')
    const supportCard = cards.find((card) => card.getAttribute('data-agent') === 'support')!
    const textarea = within(supportCard).getByLabelText('Prompt') as HTMLTextAreaElement

    const user = userEvent.setup()
    await user.clear(textarea)
    await user.type(textarea, 'novo prompt de teste')
    await user.click(within(supportCard).getByRole('button', { name: 'Salvar' }))

    await waitFor(() => {
      expect(mockedUpdateAgentConfig).toHaveBeenCalledWith('support', { prompt: 'novo prompt de teste' })
    })
    await waitFor(() => {
      expect((within(supportCard).getByLabelText('Prompt') as HTMLTextAreaElement).value).toBe(
        'novo prompt de teste',
      )
    })
  })

  it('restoring default reverts the prompt to the original default value', async () => {
    mockedRestoreAgentConfigDefault.mockResolvedValue(BASE_CONFIGS.support)
    mockedFetchAgentConfigs
      .mockResolvedValueOnce({ ...structuredClone(BASE_CONFIGS), support: { ...BASE_CONFIGS.support, prompt: 'prompt temporário' } })
      .mockResolvedValueOnce(structuredClone(BASE_CONFIGS))

    renderPage()
    const cards = await screen.findAllByTestId('agent-config-card')
    const supportCard = cards.find((card) => card.getAttribute('data-agent') === 'support')!
    await waitFor(() => {
      expect((within(supportCard).getByLabelText('Prompt') as HTMLTextAreaElement).value).toBe('prompt temporário')
    })

    const user = userEvent.setup()
    await user.click(within(supportCard).getByRole('button', { name: 'Restaurar padrão' }))

    await waitFor(() => expect(mockedRestoreAgentConfigDefault).toHaveBeenCalledWith('support'))
    await waitFor(() => {
      expect((within(supportCard).getByLabelText('Prompt') as HTMLTextAreaElement).value).toBe('prompt do support')
    })
  })

  it('toggling an agent off updates the card visible enabled/disabled state', async () => {
    mockedUpdateAgentConfig.mockResolvedValue({ ...BASE_CONFIGS.knowledge, enabled: false })
    mockedFetchAgentConfigs
      .mockResolvedValueOnce(structuredClone(BASE_CONFIGS))
      .mockResolvedValueOnce({ ...structuredClone(BASE_CONFIGS), knowledge: { ...BASE_CONFIGS.knowledge, enabled: false } })

    renderPage()
    const cards = await screen.findAllByTestId('agent-config-card')
    const knowledgeCard = cards.find((card) => card.getAttribute('data-agent') === 'knowledge')!
    expect(within(knowledgeCard).getByTestId('agent-enabled-state')).toHaveTextContent('Ativado')

    const user = userEvent.setup()
    await user.click(within(knowledgeCard).getByLabelText('Ativar/desativar Knowledge'))

    await waitFor(() => {
      expect(mockedUpdateAgentConfig).toHaveBeenCalledWith('knowledge', { enabled: false })
    })
    await waitFor(() => {
      expect(within(knowledgeCard).getByTestId('agent-enabled-state')).toHaveTextContent('Desativado')
    })
  })

  it('changing the model selector persists the new model', async () => {
    mockedUpdateAgentConfig.mockResolvedValue({ ...BASE_CONFIGS.knowledge, model: 'gpt-4o' })
    mockedFetchAgentConfigs
      .mockResolvedValueOnce(structuredClone(BASE_CONFIGS))
      .mockResolvedValueOnce({ ...structuredClone(BASE_CONFIGS), knowledge: { ...BASE_CONFIGS.knowledge, model: 'gpt-4o' } })

    renderPage()
    const cards = await screen.findAllByTestId('agent-config-card')
    const knowledgeCard = cards.find((card) => card.getAttribute('data-agent') === 'knowledge')!
    const user = userEvent.setup()
    await user.selectOptions(within(knowledgeCard).getByLabelText('LLM'), 'gpt-4o')

    await waitFor(() => {
      expect(mockedUpdateAgentConfig).toHaveBeenCalledWith('knowledge', { model: 'gpt-4o' })
    })
  })

  it('setting max token usage persists it', async () => {
    mockedUpdateAgentConfig.mockResolvedValue({ ...BASE_CONFIGS.support, max_tokens: 256 })
    mockedFetchAgentConfigs
      .mockResolvedValueOnce(structuredClone(BASE_CONFIGS))
      .mockResolvedValueOnce({ ...structuredClone(BASE_CONFIGS), support: { ...BASE_CONFIGS.support, max_tokens: 256 } })

    renderPage()
    const cards = await screen.findAllByTestId('agent-config-card')
    const supportCard = cards.find((card) => card.getAttribute('data-agent') === 'support')!
    const input = within(supportCard).getByLabelText('Uso máximo de tokens')

    const user = userEvent.setup()
    await user.type(input, '256')
    await user.tab()

    await waitFor(() => {
      expect(mockedUpdateAgentConfig).toHaveBeenCalledWith('support', { max_tokens: 256 })
    })
  })

  it('disabling a specific tool/feature persists it independent of the enabled toggle', async () => {
    mockedUpdateAgentConfig.mockResolvedValue({
      ...BASE_CONFIGS.knowledge,
      disabled_features: ['tavily_web_search'],
    })
    mockedFetchAgentConfigs
      .mockResolvedValueOnce(structuredClone(BASE_CONFIGS))
      .mockResolvedValueOnce({
        ...structuredClone(BASE_CONFIGS),
        knowledge: { ...BASE_CONFIGS.knowledge, disabled_features: ['tavily_web_search'] },
      })

    renderPage()
    const cards = await screen.findAllByTestId('agent-config-card')
    const knowledgeCard = cards.find((card) => card.getAttribute('data-agent') === 'knowledge')!
    const user = userEvent.setup()
    await user.click(within(knowledgeCard).getByLabelText('Desabilitar tavily_web_search'))

    await waitFor(() => {
      expect(mockedUpdateAgentConfig).toHaveBeenCalledWith('knowledge', {
        disabled_features: ['tavily_web_search'],
      })
    })
    await waitFor(() => {
      expect(within(knowledgeCard).getByTestId('agent-enabled-state')).toHaveTextContent('Ativado')
    })
  })

  it('the Testes tab runs the real test-runner UI embedded in Configurações', async () => {
    renderPage()
    await screen.findAllByTestId('agent-config-card')

    const user = userEvent.setup()
    await user.click(screen.getByRole('button', { name: 'Testes' }))

    expect(await screen.findByTestId('tests-page')).toBeInTheDocument()
    expect(screen.getByLabelText('Categoria de teste')).toBeInTheDocument()
  })
})
