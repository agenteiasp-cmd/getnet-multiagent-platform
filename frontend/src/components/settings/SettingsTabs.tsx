export const SETTINGS_TABS = ['Agentes', 'Prompts', 'LLMs', 'Testes'] as const
export type SettingsTab = (typeof SETTINGS_TABS)[number]

interface SettingsTabsProps {
  active: SettingsTab
  onChange: (tab: SettingsTab) => void
}

export function SettingsTabs({ active, onChange }: SettingsTabsProps) {
  return (
    <div className="mt-4 flex gap-1 border-b border-getnet-100" data-testid="settings-tabs">
      {SETTINGS_TABS.map((tab) => (
        <button
          key={tab}
          type="button"
          onClick={() => onChange(tab)}
          aria-pressed={active === tab}
          className={`px-4 py-2 text-sm font-medium transition-colors ${
            active === tab
              ? 'border-b-2 border-getnet-500 text-getnet-900'
              : 'text-getnet-700 hover:text-getnet-700'
          }`}
        >
          {tab}
        </button>
      ))}
    </div>
  )
}
