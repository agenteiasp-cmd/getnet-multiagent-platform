import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MessageBubble } from './MessageBubble'
import type { ChatMessage } from '../../hooks/useChat'

function assistantMessage(text: string): ChatMessage {
  return {
    id: '1',
    role: 'assistant',
    text,
    timestamp: new Date().toISOString(),
  }
}

describe('MessageBubble', () => {
  it('never lets the bubble grow past its max width, even with one unbroken long word', () => {
    render(<MessageBubble message={{ ...assistantMessage('a'.repeat(300)), role: 'user' } as ChatMessage} />)

    const bubble = screen.getByTestId('message-bubble')
    // the flex item wrapping the bubble must be able to shrink to respect
    // max-w-lg - without min-w-0 a flex item's default min-width:auto lets
    // long unbreakable content push it wider than its max-width.
    expect(bubble.querySelector('.max-w-lg')?.className).toContain('min-w-0')
  })

  it('forces long code blocks in an assistant answer to wrap instead of scrolling horizontally', () => {
    const longLine = 'x'.repeat(300)
    render(<MessageBubble message={assistantMessage('```\n' + longLine + '\n```')} />)

    const proseContainer = screen.getByTestId('message-bubble').querySelector('.prose')
    expect(proseContainer?.className).toContain('[&_pre]:whitespace-pre-wrap')
    expect(proseContainer?.className).toContain('[&_pre]:break-words')
    expect(proseContainer?.querySelector('pre')).toBeInTheDocument()
  })

  it('forces long inline code and links to wrap too', () => {
    render(<MessageBubble message={assistantMessage('veja `' + 'x'.repeat(200) + '` para mais detalhes')} />)

    const proseContainer = screen.getByTestId('message-bubble').querySelector('.prose')
    expect(proseContainer?.className).toContain('[&_code]:break-words')
    expect(proseContainer?.className).toContain('[&_a]:break-words')
  })
})
