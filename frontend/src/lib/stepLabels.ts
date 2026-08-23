// One friendly, non-technical label per technical step name the backend
// emits (see backend/app/observability - every UsageRecord.step value).
export const STEP_LABELS: Record<string, string> = {
  'guardrails.check': 'Verificando sua mensagem',
  'router.classify_intent': 'Entendendo o que você precisa',
  'router.chitchat_reply': 'Preparando resposta',
  'knowledge.rag_generate': 'Buscando nas informações da Getnet',
  'knowledge.web_generate': 'Pesquisando na web',
  'support.decide_tools': 'Consultando seus dados',
  'support.generate_answer': 'Organizando a resposta',
  'escalation.mock_handoff_call': 'Abrindo chamado para um atendente',
  'escalation.mock_phone_transfer': 'Preparando transferência por telefone',
}

export function friendlyStepLabel(step: string): string {
  return STEP_LABELS[step] ?? step
}
