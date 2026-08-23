import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchConversationTrace, fetchConversations, fetchMetrics } from '../api/client'
import { ConversationFilters, type LogFilters } from '../components/logs/ConversationFilters'
import { ConversationList } from '../components/logs/ConversationList'
import { ErrorsPanel } from '../components/logs/ErrorsPanel'
import { PerformanceSection } from '../components/logs/PerformanceSection'
import { TraceView } from '../components/logs/TraceView'

export function LogsPage() {
  const [filters, setFilters] = useState<LogFilters>({})
  const [selectedId, setSelectedId] = useState<string | null>(null)

  const conversationsQuery = useQuery({
    queryKey: ['conversations', filters],
    queryFn: () => fetchConversations({ ...filters, limit: 50 }),
  })

  const traceQuery = useQuery({
    queryKey: ['conversation-trace', selectedId],
    queryFn: () => fetchConversationTrace(selectedId as string),
    enabled: selectedId !== null,
  })

  const metricsQuery = useQuery({
    queryKey: ['logs-metrics', filters.start, filters.end],
    queryFn: () => fetchMetrics({ start: filters.start, end: filters.end }),
  })

  const conversations = conversationsQuery.data ?? []
  const errorConversations = conversations.filter((c) => c.status !== 'ok')
  const failingStep = traceQuery.data?.steps.find((step) => step.status !== 'ok')

  useEffect(() => {
    if (selectedId && failingStep) {
      document.getElementById(`trace-step-${failingStep.id}`)?.scrollIntoView({ block: 'center' })
    }
  }, [selectedId, failingStep])

  function openErrorTrace(conversationId: string) {
    setSelectedId(conversationId)
  }

  return (
    <div className="flex flex-col gap-4" data-testid="logs-page">
      <ConversationFilters value={filters} onChange={setFilters} />

      <div className="flex h-[420px] gap-4">
        <ConversationList
          conversations={conversations}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
        <div className="flex-1 space-y-4 overflow-y-auto">
          {selectedId ? (
            <div>
              <button
                type="button"
                onClick={() => setSelectedId(null)}
                className="mb-3 text-xs font-medium text-getnet-600 hover:underline"
              >
                ← Voltar para visão geral
              </button>
              <TraceView
                trace={traceQuery.data}
                isLoading={traceQuery.isLoading}
                highlightStepId={failingStep?.id}
              />
            </div>
          ) : (
            <ErrorsPanel errorConversations={errorConversations} onOpenTrace={openErrorTrace} />
          )}
        </div>
      </div>

      <PerformanceSection metrics={metricsQuery.data} />
    </div>
  )
}
