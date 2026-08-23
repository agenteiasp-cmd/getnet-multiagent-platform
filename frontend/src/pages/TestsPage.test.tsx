import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TestsPage } from './TestsPage'
import * as apiClient from '../api/client'
import type { TestRunResult } from '../api/types'

vi.mock('../api/client')

const mockedFetchTestCategories = vi.mocked(apiClient.fetchTestCategories)
const mockedRunTestCategory = vi.mocked(apiClient.runTestCategory)

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>((r) => {
    resolve = r
  })
  return { promise, resolve }
}

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <QueryClientProvider client={queryClient}>
      <TestsPage />
    </QueryClientProvider>,
  )
}

beforeEach(() => {
  vi.clearAllMocks()
  mockedFetchTestCategories.mockResolvedValue(['guardrails', 'escalation'])
})

describe('TestsPage', () => {
  it('shows terminal-style output updating as a run progresses', async () => {
    const pending = deferred<TestRunResult>()
    mockedRunTestCategory.mockReturnValue(pending.promise)

    renderPage()
    const user = userEvent.setup()
    await screen.findByRole('option', { name: 'escalation' })
    await user.selectOptions(screen.getByLabelText('Categoria de teste'), 'escalation')
    await user.click(screen.getByRole('button', { name: 'Rodar testes' }))

    expect(screen.getByTestId('terminal-output')).toHaveTextContent('Executando testes...')

    pending.resolve({
      category: 'escalation',
      passed: 3,
      failed: 0,
      total: 3,
      duration_seconds: 0.12,
      tests: [
        { name: 'tests/test_escalation_agent.py::test_a', outcome: 'passed', duration_seconds: 0.03, error: null },
      ],
    })

    await waitFor(() => {
      expect(screen.getByTestId('terminal-output')).toHaveTextContent('PASS')
    })
    expect(screen.getByTestId('terminal-output')).toHaveTextContent('3 passou, 0 falhou, 3 total')
  })

  it('lists per-test results with passed/failed status, duration, and error message', async () => {
    mockedRunTestCategory.mockResolvedValue({
      category: 'guardrails',
      passed: 1,
      failed: 1,
      total: 2,
      duration_seconds: 0.2,
      tests: [
        { name: 'tests/test_guardrails.py::test_ok', outcome: 'passed', duration_seconds: 0.05, error: null },
        {
          name: 'tests/test_guardrails.py::test_bad',
          outcome: 'failed',
          duration_seconds: 0.09,
          error: 'AssertionError: expected True, got False',
        },
      ],
    })

    renderPage()
    const user = userEvent.setup()
    await screen.findByRole('option', { name: 'guardrails' })
    await user.selectOptions(screen.getByLabelText('Categoria de teste'), 'guardrails')
    await user.click(screen.getByRole('button', { name: 'Rodar testes' }))

    const items = await screen.findAllByTestId('test-result-item')
    expect(items).toHaveLength(2)
    expect(items[0]).toHaveTextContent('passed')
    expect(items[1]).toHaveTextContent('failed')
    expect(items[1]).toHaveTextContent('AssertionError: expected True, got False')
  })
})
