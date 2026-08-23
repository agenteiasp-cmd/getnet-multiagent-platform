## Purpose

Captures a unique trace per request with per-step structured records, persists them, and exposes them through read APIs so the frontend can display conversations, traces, aggregate metrics, and per-agent user feedback ratings.

## ADDED Requirements

### Requirement: Every request gets a unique trace_id
The system SHALL generate a unique `trace_id` for each `POST /chat` request.

#### Scenario: Two concurrent requests receive different trace_ids
- **WHEN** two `POST /chat` requests are processed at the same time
- **THEN** each response contains a distinct `trace_id`

### Requirement: Each pipeline step is recorded
The system SHALL record a step entry for every router decision, agent invocation, tool call, and LLM call, each with timestamp, input, output, model, tokens, latency, and status.

#### Scenario: Router step recorded
- **WHEN** the Router classifies intent for a request
- **THEN** a step record is stored with timestamp, input, output, model, tokens, latency, and status for that classification

#### Scenario: Agent step recorded
- **WHEN** a specialist agent (knowledge/support/escalation) handles a request
- **THEN** a step record is stored with the same fields for that agent invocation

#### Scenario: Tool call step recorded
- **WHEN** any tool (retrieval, web search, support tool, escalation call) is invoked
- **THEN** a step record is stored with the same fields for that tool call

#### Scenario: LLM call step recorded
- **WHEN** any LLM call is made during the request
- **THEN** a step record is stored with the same fields for that LLM call

### Requirement: Step records persist across restarts
The system SHALL persist step records to durable storage (SQLite or JSONL) rather than only in memory.

#### Scenario: Records survive a process restart
- **WHEN** the backend process restarts after handling requests
- **THEN** previously recorded steps are still readable from the persisted store

### Requirement: GET /conversations lists past conversations
The system SHALL expose `GET /conversations` returning stored conversations with `conversation_id`, `user_id`, timestamps, and a summary.

#### Scenario: Listing returns stored conversations
- **WHEN** a client calls `GET /conversations`
- **THEN** the response lists each stored conversation with its `conversation_id`, `user_id`, timestamps, and a summary field

### Requirement: GET /conversations/{id}/trace returns the full step trace
The system SHALL expose `GET /conversations/{id}/trace` returning the ordered list of step records for that conversation.

#### Scenario: Trace returned for a known conversation_id
- **WHEN** a client calls `GET /conversations/{id}/trace` with a valid `conversation_id`
- **THEN** the response returns the ordered steps with all captured fields (timestamp, input, output, model, tokens, latency, status)

#### Scenario: Unknown conversation_id
- **WHEN** a client calls `GET /conversations/{id}/trace` with a `conversation_id` that does not exist
- **THEN** the system returns a not-found response

### Requirement: GET /metrics returns aggregate service metrics
The system SHALL expose `GET /metrics`, filterable by period, returning aggregate counts, latency, and error-rate metrics.

#### Scenario: Metrics filtered by period
- **WHEN** a client calls `GET /metrics` with a date-range/period filter
- **THEN** the response returns aggregate counts, latency, and error-rate metrics computed over that period only

### Requirement: GET /agents/usage returns per-agent usage
The system SHALL expose `GET /agents/usage` returning invocation counts broken down by agent for a given period.

#### Scenario: Usage broken down by agent
- **WHEN** a client calls `GET /agents/usage` for a given period
- **THEN** the response returns the invocation count for each of router/knowledge/support/escalation within that period

### Requirement: GET /tokens/usage returns token and cost usage
The system SHALL expose `GET /tokens/usage` returning token counts and estimated cost aggregated by period and by agent/model.

#### Scenario: Token usage broken down by period and agent/model
- **WHEN** a client calls `GET /tokens/usage` for a given period
- **THEN** the response returns token counts and estimated cost aggregated for that period, broken down by agent and model

### Requirement: Users can submit feedback on an agent response
The system SHALL expose `POST /feedback` accepting a rating tied to a `trace_id` and `agent_used`, and persist it.

#### Scenario: Submitted feedback is persisted
- **WHEN** a client calls `POST /feedback` with a `trace_id`, `agent_used`, and rating
- **THEN** the rating is persisted and associated with that `trace_id` and `agent_used`

#### Scenario: Feedback survives a process restart
- **WHEN** the backend process restarts after feedback has been submitted
- **THEN** previously submitted feedback is still readable from the persisted store

### Requirement: GET /agents/feedback returns per-agent rating aggregates
The system SHALL expose `GET /agents/feedback` returning aggregate rating metrics (e.g. % positive, average score) per agent, period-filterable.

#### Scenario: Aggregates reflect submitted feedback
- **WHEN** a client calls `GET /agents/feedback` for a given period
- **THEN** the response returns an aggregate rating for each agent that received feedback in that period
