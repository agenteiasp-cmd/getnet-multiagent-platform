export const PERIOD_OPTIONS = [
  { value: '7d', label: 'Últimos 7 dias' },
  { value: '30d', label: 'Últimos 30 dias' },
  { value: '90d', label: 'Últimos 90 dias' },
  { value: 'all', label: 'Todo o período' },
] as const

export type PeriodValue = (typeof PERIOD_OPTIONS)[number]['value']

export function periodToRange(period: string): { start?: string; end?: string } {
  if (period === 'all') return {}
  const days = period === '7d' ? 7 : period === '30d' ? 30 : 90
  const end = new Date()
  const start = new Date(end.getTime() - days * 24 * 60 * 60 * 1000)
  return { start: start.toISOString(), end: end.toISOString() }
}
