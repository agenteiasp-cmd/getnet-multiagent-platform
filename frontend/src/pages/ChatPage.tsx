import { useEffect, useRef, useState } from 'react'
import { AgentFlowPanel } from '../components/chat/AgentFlowPanel'
import { ChatComposer } from '../components/chat/ChatComposer'
import { MessageBubble } from '../components/chat/MessageBubble'
import { QuickReplies } from '../components/chat/QuickReplies'
import { useChat } from '../hooks/useChat'

const DEFAULT_USER_ID = 'user-1'

export function ChatPage() {
  const [userId] = useState(DEFAULT_USER_ID)
  const { messages, isProcessing, activeTrace, error, sendMessage } = useChat(userId)
  const lastAssistantMessage = [...messages].reverse().find((m) => m.role === 'assistant')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages.length, isProcessing])

  return (
    <div className="flex h-full">
      <div className="flex flex-1 flex-col">
        <header className="border-b border-getnet-100 bg-surface-card px-6 py-4">
          <h1 className="text-lg font-semibold text-getnet-900">Chat</h1>
          <p className="text-xs text-getnet-700">Usuário: {userId}</p>
        </header>

        <div className="flex-1 space-y-3 overflow-y-auto bg-surface p-6" data-testid="message-list">
          {messages.length === 0 && (
            <p className="text-sm text-getnet-700">Envie uma mensagem para começar a conversa.</p>
          )}
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
          {isProcessing && (
            <p className="text-xs text-getnet-700" data-testid="chat-processing-indicator">
              Assistente está digitando...
            </p>
          )}
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div ref={bottomRef} />
        </div>

        <QuickReplies onSelect={sendMessage} disabled={isProcessing} />

        <ChatComposer onSend={sendMessage} disabled={isProcessing} />
      </div>

      <AgentFlowPanel
        isProcessing={isProcessing}
        trace={activeTrace}
        agentUsed={lastAssistantMessage?.agentUsed}
      />
    </div>
  )
}
