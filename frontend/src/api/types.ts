export interface ChatRequest {
  message: string
  user_id: string
}

export interface Source {
  url: string
  title: string
}

export interface ChatResponse {
  response: string
  agent_used: string
  intent: string
  sources: Source[]
  tools_used: string[]
  trace_id: string
}

export interface Conversation {
  conversation_id: string
  trace_id: string
  user_id: string
  message: string
  response: string
  agent_used: string
  intent: string
  status: string
  created_at: string
}

export interface StepRecord {
  id: number
  conversation_id: string
  trace_id: string
  step: string
  timestamp: string
  input_data: string | null
  output_data: string | null
  model: string | null
  prompt_tokens: number
  completion_tokens: number
  latency_ms: number
  status: string
}

export interface ConversationTrace {
  conversation: Conversation
  steps: StepRecord[]
}

export interface MetricsSummary {
  total_conversations: number
  by_status: Record<string, number>
  error_rate: number
  avg_step_latency_ms: number
  total_step_latency_ms: number
  step_count: number
}

export type AgentUsage = Record<string, number>

export interface TokenUsageBreakdownEntry {
  model: string | null
  agent_used: string
  prompt_tokens: number
  completion_tokens: number
  estimated_cost_usd: number
}

export interface TokenUsage {
  total_prompt_tokens: number
  total_completion_tokens: number
  total_estimated_cost_usd: number
  breakdown: TokenUsageBreakdownEntry[]
}

export interface AgentConfig {
  prompt: string
  model: string | null
  temperature: number | null
  tools: string[]
  enabled: boolean
  max_tokens: number | null
  disabled_features: string[]
}

export type AgentConfigMap = Record<string, AgentConfig>

export interface AgentConfigUpdate {
  prompt?: string
  model?: string
  temperature?: number
  tools?: string[]
  enabled?: boolean
  max_tokens?: number
  disabled_features?: string[]
}

export const AVAILABLE_MODELS = ['gpt-4o-mini', 'gpt-4o'] as const

export interface TestCaseResult {
  name: string
  outcome: 'passed' | 'failed' | 'skipped' | string
  duration_seconds: number
  error: string | null
}

export interface TestRunResult {
  category: string
  passed: number
  failed: number
  total: number
  duration_seconds: number
  tests: TestCaseResult[]
}

export interface DateRangeFilter {
  start?: string
  end?: string
}

export interface FeedbackRequest {
  trace_id: string
  agent_used: string
  rating: 1 | -1
}

export interface AgentFeedbackEntry {
  total: number
  positive_rate: number
  avg_score: number
}

export type AgentFeedback = Record<string, AgentFeedbackEntry>
