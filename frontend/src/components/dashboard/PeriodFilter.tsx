import { PERIOD_OPTIONS } from '../../lib/period'

interface PeriodFilterProps {
  value: string
  onChange: (value: string) => void
}

export function PeriodFilter({ value, onChange }: PeriodFilterProps) {
  return (
    <select
      aria-label="Período"
      value={value}
      onChange={(event) => onChange(event.target.value)}
      className="rounded-lg border border-getnet-200 bg-surface-card px-3 py-2 text-sm text-getnet-900 outline-none focus:border-getnet-500"
    >
      {PERIOD_OPTIONS.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  )
}
