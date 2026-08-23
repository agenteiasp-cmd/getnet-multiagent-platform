import { NavLink } from 'react-router-dom'
import { useTheme } from '../../hooks/useTheme'

const NAV_ITEMS = [
  { to: '/', label: 'Chat', icon: '💬' },
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/settings', label: 'Configurações', icon: '⚙️' },
]

export function Sidebar() {
  const { theme, toggleTheme } = useTheme()

  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-getnet-100 bg-surface-card">
      <div className="flex items-center gap-2 px-6 py-6">
        <img src="/assets/getnet-logo-crop.png" alt="Getnet" className="h-7 w-auto" />
      </div>
      <p className="px-6 pb-4 text-xs text-getnet-600">Atendimento Multiagente</p>
      <nav className="flex flex-1 flex-col gap-1 px-3">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-getnet-500 text-white shadow-sm'
                  : 'text-getnet-800 hover:bg-getnet-50'
              }`
            }
          >
            <span aria-hidden="true">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-getnet-100 px-6 py-4">
        <button
          type="button"
          onClick={toggleTheme}
          aria-label="Alternar tema claro/escuro"
          className="mb-3 flex w-full items-center justify-between rounded-lg border border-getnet-100 px-3 py-2 text-xs font-medium text-getnet-800 hover:bg-getnet-50"
        >
          <span>{theme === 'dark' ? 'Tema escuro' : 'Tema claro'}</span>
          <span aria-hidden="true">{theme === 'dark' ? '🌙' : '☀️'}</span>
        </button>
        <p className="text-xs text-getnet-600">Plataforma de atendimento IA</p>
      </div>
    </aside>
  )
}
