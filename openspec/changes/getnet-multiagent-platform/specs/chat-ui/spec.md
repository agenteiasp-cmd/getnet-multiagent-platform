## Purpose

Gives users a chat interface to converse with the backend assistant while observing, in real time, which agent and tools are handling their request.

## ADDED Requirements

### Requirement: Conversation history is displayed
The Chat page SHALL display the message history with user and AI messages visually differentiated, each showing a timestamp.

#### Scenario: User and AI messages are differentiated
- **WHEN** a conversation contains both user and AI messages
- **THEN** the two roles are visually distinguishable and each message shows the time it was sent/received

### Requirement: Message sending shows processing state
The Chat page SHALL show a processing indicator while a request is in flight and clear it once a response or error arrives.

#### Scenario: Processing indicator while waiting for a response
- **WHEN** the user sends a message and the `/chat` request has not yet resolved
- **THEN** a processing indicator is shown

#### Scenario: Indicator clears on response
- **WHEN** the `/chat` response arrives
- **THEN** the processing indicator clears and the AI message with its status is displayed

### Requirement: Sources are shown when present
The Chat page SHALL render the `sources` returned with an AI message when that array is non-empty.

#### Scenario: Response with sources renders them
- **WHEN** an AI response has a non-empty `sources` array
- **THEN** the sources are displayed alongside that message

#### Scenario: Response without sources renders none
- **WHEN** an AI response has an empty `sources` array
- **THEN** no sources section is displayed for that message

### Requirement: Live agent-flow panel reflects the current request in plain language
The Chat page SHALL show a side panel with the live orchestration flow for the in-flight or most recent request, described in friendly, non-technical language by default: each step shows a natural-language label (e.g. "Verificando sua mensagem" for the guardrail check, "Entendendo o que você precisa" for intent classification - one friendly label per technical step name the backend emits), a status icon (waiting/processing/done/error), and its duration in seconds. Technical details (exact step name, model, token counts) are hidden by default and only shown if the user expands an explicit "detalhes técnicos" toggle.

#### Scenario: Panel reflects an in-flight request
- **WHEN** a `/chat` request is being processed
- **THEN** the panel highlights the currently active agent using its friendly label and shows elapsed time, without technical step names or token counts visible

#### Scenario: Panel reflects the final state in friendly language by default
- **WHEN** the `/chat` response arrives
- **THEN** the panel shows every step that ran with its friendly label, a done/error status icon, and its duration in seconds

#### Scenario: Technical details are opt-in
- **WHEN** the user expands the "detalhes técnicos" toggle
- **THEN** each step additionally shows its technical step name, the model used, and prompt/completion token counts
- **WHEN** the toggle is collapsed
- **THEN** none of those technical fields are visible

### Requirement: Quick-reply suggestions are available
The Chat page SHALL show a configurable list of quick-reply suggestions (not hardcoded inline in the component) as clickable buttons that fill in and/or send the associated message.

#### Scenario: Clicking a quick reply sends its message
- **WHEN** the user clicks a quick-reply suggestion button
- **THEN** the associated message is sent as if the user had typed and submitted it themselves

#### Scenario: The suggestion list is configurable
- **WHEN** the quick-reply list is changed at its configuration source
- **THEN** the rendered buttons reflect that list without requiring a change to the button-rendering component itself

### Requirement: Users can rate an agent response
The Chat page SHALL let the user submit a 👍/👎 (or equivalent) rating on each AI message, associated with that message's `trace_id` and `agent_used`.

#### Scenario: Submitting a rating persists it
- **WHEN** the user clicks a rating control on an AI message
- **THEN** the rating is submitted with that message's `trace_id` and `agent_used`, and the control reflects the submitted state

#### Scenario: Each AI message has its own independent rating control
- **WHEN** a conversation contains multiple AI messages
- **THEN** rating one message does not affect the rating control shown on any other message
