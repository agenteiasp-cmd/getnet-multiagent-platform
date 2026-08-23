import { useCallback, useState } from 'react'
import { runTestCategory } from '../api/client'
import type { TestRunResult } from '../api/types'

export function useTestRun() {
  const [isRunning, setIsRunning] = useState(false)
  const [result, setResult] = useState<TestRunResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  const run = useCallback(async (category: string) => {
    setIsRunning(true)
    setError(null)
    setResult(null)
    try {
      const data = await runTestCategory(category)
      setResult(data)
    } catch {
      setError('Falha ao executar os testes.')
    } finally {
      setIsRunning(false)
    }
  }, [])

  return { isRunning, result, error, run }
}
