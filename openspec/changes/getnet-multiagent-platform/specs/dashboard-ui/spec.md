## Purpose

Gives operators an at-a-glance, period-filterable view of service volume, agent usage, feedback ratings, and token/cost metrics backed by charts, plus (as an embedded section) the full Logs & Observabilidade deep-dive view.

## ADDED Requirements

### Requirement: Period filter controls displayed data
The Dashboard page SHALL provide a period filter that determines the date range for all displayed metrics.

#### Scenario: Changing the period re-renders all metrics
- **WHEN** the user changes the period filter
- **THEN** all dashboard metrics and charts re-fetch and re-render for the newly selected range

### Requirement: Service metrics are charted
The Dashboard page SHALL show a chart of service/request volume for the selected period, backed by `GET /metrics`.

#### Scenario: Volume chart reflects the selected period
- **WHEN** the dashboard loads with a given period
- **THEN** a chart shows request volume (and related service metrics) for that period

### Requirement: Agent-usage metrics are charted
The Dashboard page SHALL show a chart breaking down invocations by agent for the selected period, backed by `GET /agents/usage`.

#### Scenario: Agent-usage chart reflects the selected period
- **WHEN** the dashboard loads with a given period
- **THEN** a chart shows invocation counts broken down by agent for that period

### Requirement: Token/cost metrics are charted
The Dashboard page SHALL show a chart of token usage and estimated cost for the selected period, backed by `GET /tokens/usage`.

#### Scenario: Token/cost chart reflects the selected period
- **WHEN** the dashboard loads with a given period
- **THEN** a chart shows token usage and estimated cost for that period

### Requirement: Per-agent feedback ratings are shown
The Dashboard page SHALL show a per-agent rating metric (e.g. % positive, average score) alongside the agent-usage metrics, backed by `GET /agents/feedback`.

#### Scenario: Rating metric reflects submitted feedback
- **WHEN** users have submitted ratings on AI messages for a given agent
- **THEN** the dashboard shows that agent's aggregate rating for the selected period

### Requirement: Logs & Observabilidade is embedded as a section at the end of the page
The Dashboard page SHALL include the Logs & Observabilidade capability's full UI (overview, conversation list, trace view, filters, errors area, performance section) as a collapsible section at the end of the page, rather than as a separate sidebar route.

#### Scenario: Section is collapsed by default
- **WHEN** the Dashboard page loads
- **THEN** the Logs & Observabilidade section is present but collapsed, so it doesn't dominate the page by default

#### Scenario: Expanding reveals the full Logs & Observabilidade UI
- **WHEN** the user expands the Logs & Observabilidade section
- **THEN** the conversation list, trace view, filters, errors area, and performance section all behave exactly as specified in the `logs-observability-ui` capability
