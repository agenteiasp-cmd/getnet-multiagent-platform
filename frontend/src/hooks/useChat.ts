import { useCallback, useState } from 'react'
import { fetchConversationTrace, sendChatMessage } from '../api/client'
import type { ConversationTrace, Source } from '../api/types'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  timestamp: string
  sources?: Source[]
  agentUsed?: string
  toolsUsed?: string[]
  traceId?: string
}

export function useChat(userId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isProcessing, setIsProcessing] = useState(false)
  const [activeTrace, setActiveTrace] = useState<ConversationTrace | null>(null)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(
    async (text: string) => {
      const userMessage: ChatMessage = {
        id: `${Date.now()}-user`,
        role: 'user',
        text,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, userMessage])
      setIsProcessing(true)
      setError(null)
      setActiveTrace(null)

      try {
        const response = await sendChatMessage({ message: text, user_id: userId })
        const assistantMessage: ChatMessage = {
          id: response.trace_id,
          role: 'assistant',
          text: response.response,
          timestamp: new Date().toISOString(),
          sources: response.sources,
          agentUsed: response.agent_used,
          toolsUsed: response.tools_used,
          traceId: response.trace_id,
        }
        setMessages((prev) => [...prev, assistantMessage])

        try {
          const trace = await fetchConversationTrace(response.trace_id)
          setActiveTrace(trace)
        } catch {
          // Best-effort: the side panel just stays empty if the trace fetch fails.
        }
      } catch {
        setError('Não foi possível enviar sua mensagem. Tente novamente.')
      } finally {
        setIsProcessing(false)
      }
    },
    [userId],
  )

  return { messages, isProcessing, activeTrace, error, sendMessage }
}
