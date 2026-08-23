import type { TestRunResult } from '../../api/types'

export function TestResultsList({ result }: { result: TestRunResult }) {
  return (
    <div
      data-testid="test-results-list"
      className="mt-4 rounded-xl border border-getnet-100 bg-surface-card"
    >
      <div className="flex items-center justify-between border-b border-getnet-100 p-4">
        <h2 className="text-sm font-semibold text-getnet-900">Resultados: {result.category}</h2>
        <p className="text-xs text-getnet-600">
          {result.passed} passou · {result.failed} falhou · {result.total} total
        </p>
      </div>
      <ul>
        {result.tests.map((test) => (
          <li key={test.name} data-testid="test-result-item" className="border-b border-getnet-50 p-3 text-xs">
            <div className="flex items-center justify-between gap-2">
              <span className="font-mono text-getnet-900">{test.name}</span>
              <span
                className={
                  test.outcome === 'passed' ? 'font-semibold text-getnet-600' : 'font-semibold text-red-600'
                }
              >
                {test.outcome}
              </span>
            </div>
            <p className="text-getnet-400">{test.duration_seconds.toFixed(2)}s</p>
            {test.error && (
              <pre className="mt-1 whitespace-pre-wrap text-[10px] text-red-600">{test.error}</pre>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
