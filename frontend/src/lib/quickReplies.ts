export interface QuickReply {
  label: string
  message: string
}

// Configurable list - edit here, not in the rendering component, to
// change what shows up in the Chat page's quick-reply row.
export const QUICK_REPLIES: QuickReply[] = [
  { label: 'Diferença entre maquininhas', message: 'Qual a diferença entre a Get Clássica e a Get Smart?' },
  { label: 'Status do meu depósito', message: 'Quando cai o dinheiro das minhas vendas?' },
  { label: 'Minha maquininha não conecta', message: 'Minha maquininha está sem internet, o que eu faço?' },
  { label: 'Como funciona o Pix', message: 'Qual conta bancária está cadastrada para receber via Pix?' },
]
