import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../../hooks/useChat'
import { FeedbackControl } from './FeedbackControl'
import { SourcesList } from './SourcesList'

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'
  const time = new Date(message.timestamp).toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}
      data-testid="message-bubble"
      data-role={message.role}
    >
      <div className={`flex min-w-0 max-w-lg flex-col gap-1.5 ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`w-full break-words rounded-2xl px-4 py-3 text-sm shadow-sm ${
            isUser
              ? 'bg-getnet-500 text-white'
              : 'border border-getnet-100 bg-surface-card text-getnet-900'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap break-words">{message.text}</p>
          ) : (
            <div
              className="prose prose-sm max-w-none break-words prose-p:my-1 prose-ul:my-1 prose-headings:my-1
                [&_pre]:whitespace-pre-wrap [&_pre]:break-words [&_code]:break-words [&_a]:break-words"
            >
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
            </div>
          )}
          {isUser && <p className="mt-1 text-[10px] text-white/70">{time}</p>}
        </div>
        {!isUser && message.sources && message.sources.length > 0 && (
          <SourcesList sources={message.sources} />
        )}
        {!isUser && (
          <div className="flex items-center gap-3 px-1">
            {message.traceId && message.agentUsed && (
              <FeedbackControl traceId={message.traceId} agentUsed={message.agentUsed} />
            )}
            <span className="text-[10px] text-getnet-700">{time}</span>
          </div>
        )}
      </div>
    </div>
  )
}
