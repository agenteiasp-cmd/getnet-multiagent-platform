import { useState, type FormEvent } from 'react'

interface ChatComposerProps {
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatComposer({ onSend, disabled }: ChatComposerProps) {
  const [value, setValue] = useState('')

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-center gap-2 border-t border-getnet-100 bg-surface-card p-4"
    >
      <input
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Digite sua mensagem..."
        aria-label="Mensagem"
        className="flex-1 rounded-full border border-getnet-200 px-4 py-2 text-sm outline-none focus:border-getnet-500"
        disabled={disabled}
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="rounded-full bg-getnet-500 px-5 py-2 text-sm font-semibold text-white transition-opacity disabled:opacity-50"
      >
        Enviar
      </button>
    </form>
  )
}
