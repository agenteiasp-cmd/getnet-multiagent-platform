import { useState } from 'react'
import { submitFeedback } from '../../api/client'

interface FeedbackControlProps {
  traceId: string
  agentUsed: string
}

export function FeedbackControl({ traceId, agentUsed }: FeedbackControlProps) {
  const [submitted, setSubmitted] = useState<1 | -1 | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function rate(rating: 1 | -1) {
    if (submitted !== null || isSubmitting) return
    setIsSubmitting(true)
    try {
      await submitFeedback({ trace_id: traceId, agent_used: agentUsed, rating })
      setSubmitted(rating)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="flex items-center gap-2" data-testid="feedback-control">
      <button
        type="button"
        aria-label="Avaliar positivamente"
        aria-pressed={submitted === 1}
        disabled={submitted !== null}
        onClick={() => rate(1)}
        className={`rounded-full px-1.5 py-0.5 text-xs transition-opacity ${
          submitted === 1 ? 'opacity-100' : 'opacity-50 hover:opacity-80'
        }`}
      >
        👍
      </button>
      <button
        type="button"
        aria-label="Avaliar negativamente"
        aria-pressed={submitted === -1}
        disabled={submitted !== null}
        onClick={() => rate(-1)}
        className={`rounded-full px-1.5 py-0.5 text-xs transition-opacity ${
          submitted === -1 ? 'opacity-100' : 'opacity-50 hover:opacity-80'
        }`}
      >
        👎
      </button>
      {submitted !== null && (
        <span className="text-[10px] text-getnet-700" data-testid="feedback-submitted">
          Obrigado pelo feedback!
        </span>
      )}
    </div>
  )
}
