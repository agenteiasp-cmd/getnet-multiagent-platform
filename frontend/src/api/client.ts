import axios from 'axios'
import type {
  AgentConfigMap,
  AgentConfigUpdate,
  AgentFeedback,
  AgentUsage,
  ChatRequest,
  ChatResponse,
  Conversation,
  ConversationTrace,
  DateRangeFilter,
  FeedbackRequest,
  MetricsSummary,
  TestRunResult,
  TokenUsage,
} from './types'

export const API_BASE_URL: string =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

function toParams(filter?: DateRangeFilter) {
  if (!filter) return undefined
  const params: Record<string, string> = {}
  if (filter.start) params.start = filter.start
  if (filter.end) params.end = filter.end
  return params
}

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const { data } = await apiClient.post<ChatResponse>('/chat', request)
  return data
}

export async function fetchConversations(
  filter?: DateRangeFilter & { agent?: string; status?: string; limit?: number },
): Promise<Conversation[]> {
  const { data } = await apiClient.get<Conversation[]>('/conversations', {
    params: { ...toParams(filter), agent: filter?.agent, status: filter?.status, limit: filter?.limit },
  })
  return data
}

export async function fetchConversationTrace(conversationId: string): Promise<ConversationTrace> {
  const { data } = await apiClient.get<ConversationTrace>(`/conversations/${conversationId}/trace`)
  return data
}

export async function fetchMetrics(filter?: DateRangeFilter): Promise<MetricsSummary> {
  const { data } = await apiClient.get<MetricsSummary>('/metrics', { params: toParams(filter) })
  return data
}

export async function fetchAgentsUsage(filter?: DateRangeFilter): Promise<AgentUsage> {
  const { data } = await apiClient.get<AgentUsage>('/agents/usage', { params: toParams(filter) })
  return data
}

export async function fetchTokensUsage(filter?: DateRangeFilter): Promise<TokenUsage> {
  const { data } = await apiClient.get<TokenUsage>('/tokens/usage', { params: toParams(filter) })
  return data
}

export async function fetchAgentConfigs(): Promise<AgentConfigMap> {
  const { data } = await apiClient.get<AgentConfigMap>('/agents/config')
  return data
}

export async function updateAgentConfig(
  agent: string,
  update: AgentConfigUpdate,
): Promise<AgentConfigMap[string]> {
  const { data } = await apiClient.put(`/agents/config/${agent}`, update)
  return data
}

export async function restoreAgentConfigDefault(agent: string): Promise<AgentConfigMap[string]> {
  const { data } = await apiClient.post(`/agents/config/${agent}/restore-default`)
  return data
}

export async function fetchTestCategories(): Promise<string[]> {
  const { data } = await apiClient.get<string[]>('/tests/categories')
  return data
}

export async function runTestCategory(category: string): Promise<TestRunResult> {
  const { data } = await apiClient.post<TestRunResult>('/tests/run', { category })
  return data
}

export async function submitFeedback(request: FeedbackRequest): Promise<void> {
  await apiClient.post('/feedback', request)
}

export async function fetchAgentsFeedback(filter?: DateRangeFilter): Promise<AgentFeedback> {
  const { data } = await apiClient.get<AgentFeedback>('/agents/feedback', { params: toParams(filter) })
  return data
}
