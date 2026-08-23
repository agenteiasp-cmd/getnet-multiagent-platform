export function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-getnet-100 bg-surface-card p-4 shadow-sm" data-testid="stat-card">
      <p className="text-xs font-medium uppercase tracking-wide text-getnet-700">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-getnet-900">{value}</p>
    </div>
  )
}
