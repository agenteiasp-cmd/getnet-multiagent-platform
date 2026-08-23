import { useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchAgentConfigs, restoreAgentConfigDefault, updateAgentConfig } from '../api/client'
import type { AgentConfigUpdate } from '../api/types'
import { AgentConfigCard } from '../components/settings/AgentConfigCard'
import { LlmsTab } from '../components/settings/LlmsTab'
import { PromptsTab } from '../components/settings/PromptsTab'
import { SettingsTabs, type SettingsTab } from '../components/settings/SettingsTabs'
import { TestsPage } from './TestsPage'

export function SettingsPage() {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<SettingsTab>('Agentes')
  const configsQuery = useQuery({ queryKey: ['agent-configs'], queryFn: fetchAgentConfigs })

  async function handleSave(agent: string, prompt: string) {
    await updateAgentConfig(agent, { prompt })
    queryClient.invalidateQueries({ queryKey: ['agent-configs'] })
  }

  async function handleRestoreDefault(agent: string) {
    await restoreAgentConfigDefault(agent)
    queryClient.invalidateQueries({ queryKey: ['agent-configs'] })
  }

  async function handleUpdate(agent: string, updates: AgentConfigUpdate) {
    await updateAgentConfig(agent, updates)
    queryClient.invalidateQueries({ queryKey: ['agent-configs'] })
  }

  const configs = configsQuery.data ?? {}

  return (
    <div className="p-8">
      <h1 className="text-lg font-semibold text-getnet-900">Configurações</h1>
      <p className="text-xs text-getnet-700">
        Ajuste prompt, LLM, temperatura, tools, uso de tokens e status de cada agente
      </p>

      <SettingsTabs active={tab} onChange={setTab} />

      <div className="mt-6">
        {tab === 'Agentes' && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {Object.entries(configs).map(([agent, config]) => (
              <AgentConfigCard
                key={agent}
                agent={agent}
                config={config}
                onSave={handleSave}
                onRestoreDefault={handleRestoreDefault}
                onUpdate={handleUpdate}
              />
            ))}
          </div>
        )}

        {tab === 'Prompts' && (
          <PromptsTab configs={configs} onSave={handleSave} onRestoreDefault={handleRestoreDefault} />
        )}

        {tab === 'LLMs' && <LlmsTab configs={configs} onUpdate={handleUpdate} />}

        {tab === 'Testes' && <TestsPage />}
      </div>
    </div>
  )
}
