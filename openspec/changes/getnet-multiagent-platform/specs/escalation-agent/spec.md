## Purpose

Handles requests that need human intervention by performing a mocked handoff call and confirming the handoff to the user, serving as the challenge's fourth-agent differentiator.

## ADDED Requirements

### Requirement: Escalation Agent performs a mocked handoff call
The Escalation Agent SHALL invoke a mocked external handoff call whenever a request is classified with `escalation` intent.

#### Scenario: Escalation intent triggers a mock handoff call
- **WHEN** the Router dispatches a request with `escalation` intent
- **THEN** the Escalation Agent invokes a mock handoff tool/call and receives a mocked confirmation from it

### Requirement: Escalation response communicates next steps to the user
The Escalation Agent SHALL return a response confirming the user has been handed off, with `agent_used` set to escalation.

#### Scenario: User asking to speak with a human
- **WHEN** the user asks to speak with a human agent
- **THEN** the response confirms the user has been queued/handed off and `agent_used` is `escalation`

### Requirement: Escalation is observable like any other tool call
The mock handoff call SHALL be recorded the same way as other tool invocations.

#### Scenario: Handoff call appears in tools_used and logs
- **WHEN** the Escalation Agent completes a mock handoff call
- **THEN** the handoff call name appears in `tools_used` and is captured as a logged step
