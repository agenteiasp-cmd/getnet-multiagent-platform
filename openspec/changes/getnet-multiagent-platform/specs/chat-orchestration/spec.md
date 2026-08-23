## Purpose

Defines the single `POST /chat` entry point, the guardrails stage that runs before any agent, and the Router Agent that classifies intent and dispatches to (or directly answers) the request.

## ADDED Requirements

### Requirement: Chat endpoint contract
The system SHALL expose `POST /chat` accepting `{ "message": string, "user_id": string }` and returning `{ "response": string, "agent_used": string, "intent": string, "sources": array, "tools_used": array, "trace_id": string }`.

#### Scenario: Valid chat request returns full response envelope
- **WHEN** a client sends a well-formed `POST /chat` with a non-empty `message` and `user_id`
- **THEN** the response includes all of `response`, `agent_used`, `intent`, `sources`, `tools_used`, and `trace_id`

#### Scenario: Missing required field is rejected
- **WHEN** a client sends `POST /chat` without `message` or without `user_id`
- **THEN** the system returns a validation error and does not invoke any agent

### Requirement: Guardrails reject unsafe input before agent dispatch
The system SHALL run regex-based checks and a moderation check on the incoming message before any router or agent logic executes.

#### Scenario: Input matching a blocked pattern is rejected
- **WHEN** the message matches a guardrail regex rule (e.g. attempts to exfiltrate secrets or inject instructions)
- **THEN** the system returns a refusal response with a `trace_id` and does not invoke the Router or any agent

#### Scenario: Input flagged by moderation is rejected
- **WHEN** the message is flagged by the moderation check
- **THEN** the system returns a refusal response with a `trace_id` and does not invoke the Router or any agent

#### Scenario: Guardrail-safe input proceeds to routing
- **WHEN** the message passes both the regex checks and moderation
- **THEN** the message is passed to the Router Agent for intent classification

### Requirement: Router classifies intent via a forced tool call
The Router Agent SHALL classify every guardrail-safe message into exactly one of `knowledge`, `support`, `escalation`, or `chitchat` by forcing a `classify_intent` tool call (not free-text parsing).

#### Scenario: Router selects knowledge intent for a Getnet product question
- **WHEN** the message asks about a Getnet product or policy (e.g. difference between Get Clássica and Get Smart)
- **THEN** `classify_intent` returns `knowledge` and the message is dispatched to the Knowledge Agent

#### Scenario: Router selects support intent for an account-specific question
- **WHEN** the message asks about the requesting user's own account, transactions, or device (e.g. deposit timing, declined transaction)
- **THEN** `classify_intent` returns `support` and the message is dispatched to the Support Agent

#### Scenario: Router selects escalation intent for a request to speak to a human
- **WHEN** the message explicitly asks for a human agent or escalation
- **THEN** `classify_intent` returns `escalation` and the message is dispatched to the Escalation Agent

#### Scenario: Router classification always uses the tool call
- **WHEN** the Router processes any guardrail-safe message
- **THEN** the resulting intent always comes from the `classify_intent` tool call result, never from parsing the model's free-text reply

### Requirement: Chitchat is answered by the Router directly
The system SHALL let the Router Agent answer `chitchat`-classified messages itself, without dispatching to a specialist agent.

#### Scenario: Greeting message gets a direct conversational reply
- **WHEN** the message is small talk or a greeting with no product/account/escalation intent
- **THEN** `classify_intent` returns `chitchat`, the Router replies directly, and no specialist agent or tool is invoked

### Requirement: Response envelope reflects the actual execution path
The system SHALL populate `agent_used`, `intent`, `sources`, and `tools_used` to accurately describe what happened during the request.

#### Scenario: agent_used and intent are consistent with the specialist invoked
- **WHEN** a request is dispatched to the Knowledge, Support, or Escalation agent
- **THEN** `agent_used` names that agent and `intent` matches the classified intent

#### Scenario: sources is empty when no retrieval or web search occurred
- **WHEN** the request is handled as chitchat or by the Support/Escalation agent without a retrieval step
- **THEN** `sources` is an empty array

#### Scenario: tools_used lists every tool invoked during the request
- **WHEN** the request triggers one or more tool calls (classification, retrieval, support tools, escalation call)
- **THEN** `tools_used` lists each invoked tool by name, in the order invoked

#### Scenario: trace_id is unique per request and present even on guardrail rejection
- **WHEN** any `POST /chat` request is processed, including one rejected by guardrails
- **THEN** the response includes a `trace_id` that is unique to that request

### Requirement: Agent LLM calls respect a configured max-token ceiling
Every LLM call made by the Router, Knowledge, or Support agent SHALL be capped by that agent's configured `max_tokens`, and a call that hits the cap SHALL be recorded with a distinct status rather than silently reported as `"ok"`.

#### Scenario: A configured ceiling caps generation
- **WHEN** an agent with a configured `max_tokens` value makes an LLM call
- **THEN** that call is made with the model's own max-output-tokens parameter set to the configured value

#### Scenario: A truncated call is flagged, not hidden
- **WHEN** an LLM call stops because it hit the configured `max_tokens` ceiling
- **THEN** the observability step recorded for that call has a `"truncated"` status instead of `"ok"`
