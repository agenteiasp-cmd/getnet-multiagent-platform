import type { TestRunResult } from '../../api/types'

interface TerminalOutputProps {
  category: string
  isRunning: boolean
  result: TestRunResult | null
  error: string | null
}

export function TerminalOutput({ category, isRunning, result, error }: TerminalOutputProps) {
  const lines: string[] = []
  if (category) lines.push(`$ pytest ${category === 'all' ? '.' : category} -q`)
  if (isRunning) lines.push('Executando testes...')
  if (error) lines.push(`ERRO: ${error}`)
  if (result) {
    for (const test of result.tests) {
      const tag = test.outcome === 'passed' ? 'PASS' : test.outcome === 'failed' ? 'FAIL' : 'SKIP'
      lines.push(`${tag}  ${test.name}  (${test.duration_seconds.toFixed(2)}s)`)
    }
    lines.push(
      `${result.passed} passou, ${result.failed} falhou, ${result.total} total em ${result.duration_seconds.toFixed(2)}s`,
    )
  }

  return (
    <div
      data-testid="terminal-output"
      className="mt-4 rounded-xl bg-[#0b0b0e] p-4 font-mono text-xs text-[#f5f5f7]"
    >
      {lines.length === 0 && (
        <p className="text-[#6b6b78]">Selecione uma categoria e clique em "Rodar testes".</p>
      )}
      {lines.map((line, index) => (
        <p key={index} className="whitespace-pre-wrap">
          {line}
        </p>
      ))}
    </div>
  )
}
