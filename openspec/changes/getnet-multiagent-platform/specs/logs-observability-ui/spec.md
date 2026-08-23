## Purpose

Gives operators a detailed observability view for inspecting individual conversation traces and system-wide errors and performance. Embedded within the Dashboard page (see `dashboard-ui`) rather than its own top-level route.

## ADDED Requirements

### Requirement: Not a standalone sidebar route
The Logs & Observabilidade UI SHALL be reachable only as a section within the Dashboard page (see `dashboard-ui`'s embedding requirement), not via its own sidebar entry or route.

#### Scenario: No dedicated sidebar entry
- **WHEN** the user views the sidebar
- **THEN** there is no "Logs & Observabilidade" entry separate from "Dashboard"

### Requirement: Overview summarizes system observability state
The Logs & Observabilidade section SHALL open on an overview showing high-level counts/health before a specific conversation is selected.

#### Scenario: Section opens on overview
- **WHEN** the user expands the Logs & Observabilidade section
- **THEN** an overview of high-level counts/health is shown before any conversation is selected

### Requirement: Conversations are listed by conversation_id with timeline
The section SHALL list conversations by `conversation_id`, each with a timeline of its steps, backed by `GET /conversations`.

#### Scenario: Conversation list shows a timeline per entry
- **WHEN** the conversation list loads
- **THEN** each conversation is shown by `conversation_id` with a timeline summarizing its steps

### Requirement: Trace view visualizes each step
Selecting a conversation SHALL show a step-by-step visual trace, backed by `GET /conversations/{id}/trace`.

#### Scenario: Selecting a conversation shows its trace
- **WHEN** the user selects a conversation from the list
- **THEN** the page shows a step-by-step visual trace of its agent, tool, and LLM calls with timing and status

### Requirement: Multiple filters narrow the conversation list
The section SHALL support combining multiple filters (e.g. agent, status, date range) to narrow the displayed conversations.

#### Scenario: Combined filters narrow results
- **WHEN** the user applies more than one filter at once
- **THEN** the conversation list shows only conversations matching all applied filters

### Requirement: Errors are surfaced and clickable
The section SHALL show an errors area listing failed steps, and clicking an error SHALL open that conversation's trace at the failing step.

#### Scenario: Clicking an error opens its trace
- **WHEN** the user clicks an entry in the errors area
- **THEN** the page opens that conversation's trace, scrolled/highlighted to the failing step

### Requirement: Performance section summarizes latency
The section SHALL show a performance section summarizing latency, e.g. broken down per agent or step.

#### Scenario: Performance section shows latency breakdown
- **WHEN** the user views the performance section
- **THEN** latency is shown broken down by agent and/or step for the selected period
