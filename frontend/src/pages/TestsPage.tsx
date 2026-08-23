import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchTestCategories } from '../api/client'
import { TerminalOutput } from '../components/tests/TerminalOutput'
import { TestResultsList } from '../components/tests/TestResultsList'
import { useTestRun } from '../hooks/useTestRun'

export function TestsPage() {
  const categoriesQuery = useQuery({ queryKey: ['test-categories'], queryFn: fetchTestCategories })
  const [selectedCategory, setSelectedCategory] = useState('')
  const { isRunning, result, error, run } = useTestRun()

  const categories = categoriesQuery.data ?? []

  return (
    <div data-testid="tests-page">
      <p className="text-xs text-getnet-700">Rode categorias de teste do backend e veja o resultado</p>

      <div className="mt-4 flex items-center gap-2">
        <select
          aria-label="Categoria de teste"
          value={selectedCategory}
          onChange={(event) => setSelectedCategory(event.target.value)}
          className="rounded-lg border border-getnet-200 bg-surface-card px-3 py-2 text-sm text-getnet-900"
        >
          <option value="">Selecione uma categoria</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
        <button
          type="button"
          disabled={!selectedCategory || isRunning}
          onClick={() => run(selectedCategory)}
          className="rounded-lg bg-getnet-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
        >
          {isRunning ? 'Executando...' : 'Rodar testes'}
        </button>
        <button
          type="button"
          disabled={isRunning}
          onClick={() => run('all')}
          className="rounded-lg border border-getnet-500 px-4 py-2 text-sm font-semibold text-getnet-500 disabled:opacity-50"
        >
          {isRunning ? 'Executando...' : 'Executar todos os testes'}
        </button>
      </div>

      <TerminalOutput category={selectedCategory} isRunning={isRunning} result={result} error={error} />

      {result && <TestResultsList result={result} />}
    </div>
  )
}
