## Purpose

Answers account-specific questions for the requesting user by calling tools over mocked per-user account, transaction, and device data.

## ADDED Requirements

### Requirement: Support Agent exposes at least two distinct tools
The Support Agent SHALL have two or more tools it can call to look up different categories of mocked user data (e.g. account/settlement info, transaction/device info).

#### Scenario: Deposit-timing question invokes the settlement-lookup tool
- **WHEN** the user asks when their sales deposit will be available
- **THEN** the agent calls the tool that reads the mocked settlement/deposit-schedule data and answers from its result

#### Scenario: Transaction-status question invokes the transaction-lookup tool
- **WHEN** the user asks about a specific transaction (e.g. why it was declined)
- **THEN** the agent calls the tool that reads the mocked transaction data and answers from its result

### Requirement: Tool results are scoped to the requesting user
The Support Agent's tools SHALL use the `user_id` from the request to fetch only that user's mocked data.

#### Scenario: Lookup is scoped by user_id
- **WHEN** a support tool is called during a request with a given `user_id`
- **THEN** the tool returns data belonging only to that `user_id`, not another user's data

### Requirement: Support Agent handles the challenge's example account cases
The Support Agent SHALL produce a grounded answer for each of the challenge's mocked-data example cases.

#### Scenario: Pix bank-account question
- **WHEN** the user asks which bank account is linked for receiving Pix payments
- **THEN** the agent answers using the mocked account data for that user

#### Scenario: Maquininha sem internet
- **WHEN** the user reports their card machine has no internet connection
- **THEN** the agent answers using guidance derived from the mocked device/connectivity data for that user

#### Scenario: Declined transaction
- **WHEN** the user asks why a transaction was declined
- **THEN** the agent answers with the decline reason from the mocked transaction data

#### Scenario: Installment / crediário question
- **WHEN** the user asks about installment terms for a crediário purchase
- **THEN** the agent answers using the mocked installment data for that user

### Requirement: Unknown user_id is handled without failure
The Support Agent SHALL respond gracefully when the requesting `user_id` has no matching mocked data.

#### Scenario: user_id not present in mocked dataset
- **WHEN** a support-intent request arrives with a `user_id` absent from the mocked data set
- **THEN** the agent returns a graceful fallback response instead of an error or crash

### Requirement: Individual tools can be disabled per configuration
The Support Agent SHALL exclude any tool named in its configured `disabled_features` from the set of tools offered to the LLM, so a disabled tool can never be selected.

#### Scenario: A disabled tool is never called
- **WHEN** a tool name is present in the Support Agent's `disabled_features`
- **THEN** that tool is not included in the tool schemas bound to the LLM call, and it never appears in `tools_used` for any request

#### Scenario: Other tools remain available
- **WHEN** one tool is disabled via `disabled_features`
- **THEN** the Support Agent's other tools continue to work exactly as before for questions that need them
