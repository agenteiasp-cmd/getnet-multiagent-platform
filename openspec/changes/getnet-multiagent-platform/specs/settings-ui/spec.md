## Purpose

Lets an operator inspect and adjust each agent's configuration — prompt, LLM/model, temperature, max token usage, tools, per-feature enable state, and overall enabled state — plus run the backend test suite, from a single settings screen organized into tabs/sections (Agentes, Prompts, LLMs, Testes).

## ADDED Requirements

### Requirement: Each agent has a configuration card
The Configurações page SHALL show one card per agent (Router, Knowledge, Support, Escalation) displaying its prompt, LLM/model selector, temperature, max token usage, tools, per-feature disable toggles (for agents with more than one distinct feature, e.g. Knowledge Agent's RAG vs. web search), and overall enable/disable toggle.

#### Scenario: All agent cards are shown with their configuration
- **WHEN** the user opens Configurações
- **THEN** a card is shown for each of Router, Knowledge, Support, and Escalation with its current prompt, model, temperature, max token usage, tools, feature toggles, and enabled state

#### Scenario: Model selection is persisted
- **WHEN** the user picks a different model from an agent's model selector
- **THEN** the new model selection is persisted and shown on subsequent visits to the page

#### Scenario: Max token usage is persisted
- **WHEN** the user sets an agent's max token usage field and saves
- **THEN** the new value is persisted and shown on subsequent visits to the page

#### Scenario: Per-feature disable is persisted
- **WHEN** the user toggles off one of an agent's specific features (e.g. Knowledge Agent's web search)
- **THEN** that feature's disabled state is persisted and reflected on subsequent visits, independent of the agent's overall enabled state

### Requirement: Prompt editor supports save and restore-default
Each agent card SHALL include a prompt editor with Save and Restore Default actions.

#### Scenario: Saving an edited prompt persists it
- **WHEN** the user edits an agent's prompt and clicks Save
- **THEN** the new prompt is persisted and shown on subsequent visits to the page

#### Scenario: Restoring default reverts the prompt
- **WHEN** the user clicks Restore Default on an agent's prompt editor
- **THEN** the prompt reverts to that agent's original default value

### Requirement: Disabling an agent is reflected in its card state
Toggling an agent's enable/disable control SHALL update that card's visible state.

#### Scenario: Toggling off updates the card
- **WHEN** the user toggles an agent's enable/disable control off
- **THEN** the card visibly shows that agent as disabled

### Requirement: Configurações includes a Testes tab
The Configurações page SHALL include a "Testes" tab/section, alongside Agentes/Prompts/LLMs, embedding the full `tests-ui` capability.

#### Scenario: Testes tab runs the real backend suite
- **WHEN** the user opens the Testes tab within Configurações and runs a test category
- **THEN** the terminal-style output and per-test results behave exactly as specified in the `tests-ui` capability
