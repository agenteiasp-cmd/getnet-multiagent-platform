## Context

See proposal.md - Why/What Changes for motivation and scope. This is a greenfield build (no existing code, no existing specs) split into two dependent parts: a Python/FastAPI backend implementing the agent orchestration, and a React/Vite frontend that consumes it. Both parts must ship in this change because the frontend's Dashboard, Logs, and Testes pages have no data to show without the backend's read APIs and persisted trace store.

Key external constraints from the proposal: OpenAI for LLM calls, Pinecone for the vector store, Tavily for web search, all configured through `pydantic-settings` with a values-free `.env.example`. No auth/multi-tenancy, no cloud deploy, no CI/CD.

## Goals / Non-Goals

**Goals:**
- A single orchestration pipeline (guardrails → router → specialist) that is easy to trace end-to-end via one `trace_id`.
- A RAG pipeline whose ingestion step is reproducible (a script, not a manual one-off) so the README's "ingested URLs + date" claim stays true.
- A persistence layer simple enough to run with zero external infra (SQLite/JSONL) yet expressive enough to power five different frontend pages.
- A frontend that reads exclusively through the backend's HTTP API — no direct DB access from the browser.

**Non-Goals:**
- Streaming token-by-token responses (the spec's response contract is a single JSON envelope per request; the "processing indicator" in the UI is satisfied by request-in-flight state, not SSE/websocket streaming). This also bounds the friendly agent-flow panel (Revision 1): its "live" feel comes from step-by-step reveal after the fact, not a real push/streaming channel.
- Enforcing the Configurações page's `prompt`, `temperature`, `model`, and overall `enabled` fields against the live orchestration - these are still captured and displayed only, per the original decision. **Exception (confirmed by the user for Revision 1):** `max_tokens` and `disabled_features` ARE enforced at request time - see the new Decision below. The overall per-agent `enabled` toggle deliberately stays display-only in this revision; only the two fields the user explicitly reconfirmed got real enforcement, to keep the blast radius scoped to what was asked.
- Real moderation/regex guardrail tuning for production traffic — this is a challenge-scope guardrail stage (OpenAI moderation endpoint + a small curated regex list), not a hardened content-safety system.

## Decisions (Revision 1 — visual identity, chat feedback, friendly panel, IA consolidation, settings fields)

The decisions in this subsection were added after the change was already fully implemented and delivered (see Risks/Trade-offs note at the end); they describe a second implementation pass over the same frontend/backend, not a greenfield addition.

### Dark-first "tech/neon" theme, as swappable design tokens
Replaces the original light Getnet-green theme. Base surfaces are black/dark-gray/white; Getnet red becomes a restrained accent (logo, primary CTAs) instead of the dominant color; a neon accent set differentiates status/badges/chart series. Confirmed from the public brand guide search results (site.getnet.com.br/guia-digital-marca - the page itself and its PDF brandbook both returned HTTP 403 to direct fetch, so these are the values a search engine's index surfaced, not a full manual read):
- `--color-brand-red: #EC0000` (primary red)
- `--color-brand-red-2: #C1080F`, `--color-brand-red-3: #95101E` (secondary reds)
- `--color-neon-yellow: #FFE53B` (confirmed neon)

The guide states the palette includes six neon colors and that red "loses strength" while gray/black/white "gain prominence" - consistent with the request. Only one neon (yellow) and the three reds could be confirmed; the remaining neons are chosen to visually match that confirmed set (same saturation/brightness family) and are marked as **estimated, not brand-confirmed** so they're easy to swap for exact values later:
- `--color-neon-pink: #FF3DAE` (estimated)
- `--color-neon-purple: #A259FF` (estimated)
- `--color-neon-cyan: #2FE6E6` (estimated)
- `--color-neon-lime: #B4FF3D` (estimated)

All of these become Tailwind v4 `@theme` tokens (CSS custom properties) in `frontend/src/index.css`, replacing the `getnet-*` scale - never hardcoded per-component - so a future pass can drop in exact brand hex values by editing one place. Dark is the default; a light variant is provided via the same token set under a `[data-theme="light"]` override rather than a second component tree, since Tailwind v4's `@theme` + CSS variables make that a token-only change (see design's existing pattern in `artifact-design`-style token architecture). Neon colors are used only for accents (status dots, badges, chart series, subtle gradient stops on card/header backgrounds) - never as a large-area text or background color, per the request.
Alternative considered: keep the light green theme and only add neon accents. Rejected - the request explicitly asks for a dark-first base.

### Chat quick replies: a configurable constant, not backend-driven (yet)
The quick-reply suggestion list lives as a typed constant/config module in the frontend (`frontend/src/lib/quickReplies.ts` or similar) rather than inline JSX, satisfying "não hardcoded no componente." It's not backend-configurable in this revision (no new endpoint) - that would only be worth it if the Configurações page needed to edit it, which wasn't requested.

### Per-message feedback: new `feedback` table + dedicated read endpoint
Feedback (👍/👎) is captured per AI message and tied to that message's `trace_id`/`agent_used` - both already returned by `POST /chat`, so the frontend has everything it needs to submit a rating without extra round-trips. Persisted in a new SQLite `feedback` table (trace_id, agent_used, rating, created_at) alongside `conversations`/`steps`, written via a new `POST /feedback` endpoint.
For reading aggregates, a **new** `GET /agents/feedback` endpoint (per-agent % positive / average score) is added instead of folding ratings into the existing `GET /agents/usage` - that endpoint's shape (`Record<string, count>`) is already consumed by the Dashboard's agent-usage chart and its tests; changing its shape would be a breaking change for no benefit when a sibling endpoint is just as easy to add.

### Agent-flow panel: friendly-label dictionary, technical details opt-in
A `STEP_LABELS: Record<string, string>` dictionary (one entry per technical step name the backend emits - `guardrails.check`, `router.classify_intent`, `router.chitchat_reply`, `knowledge.rag_generate`/`knowledge.web_generate`, `support.decide_tools`/`support.generate_answer`, `escalation.mock_handoff_call`) maps each to natural-language Portuguese. The panel shows friendly label + a status icon (waiting/processing/done/error, derived from whether the step exists yet in the trace and its `status` field) + duration in seconds by default. An explicit "detalhes técnicos" toggle reveals the raw step name, model, and token counts - hidden, not removed, so the existing observability data model needs no changes.

### IA consolidation: Logs and Testes become embedded sections, not routes
Both `logs-observability-ui` and `tests-ui` keep their existing requirements (conversation list, trace view, filters, errors, performance / terminal test runner, results list) unchanged in substance - only where they render changes. `LogsPage`'s content moves into a collapsible section at the end of `DashboardPage`; `TestsPage`'s content moves into a "Testes" tab inside `SettingsPage`, alongside new "Agentes"/"Prompts"/"LLMs" tabs (the agent-config cards already covered these three; grouping them into tabs is a UI reorganization, not a new requirement). The `/logs` and `/tests` routes and their sidebar entries are removed - not kept as redundant duplicates. This is why the affected capability spec files gained one placement-describing requirement each rather than being merged into `dashboard-ui`/`settings-ui` wholesale: they still describe a coherent, independently testable slice of behavior, just embedded rather than top-level.

### Settings: `model` is config-only; `max_tokens` and `disabled_features` are enforced (confirmed)
`AgentConfigUpdate` (backend) and the `AgentConfig` type (frontend) all gain `model`, `max_tokens`, and `disabled_features` fields, persisted through the existing `PUT /agents/config/{agent}`. `model` stays display-only in this revision (see Non-Goals) - swapping the live model per agent touches every agent's LLM wrapper construction and isn't part of what was reconfirmed. The other two are read by the orchestrator/agents at request time:

- **`max_tokens` enforcement**: each agent's LLM wrapper (`RouterLLM`, `GroundedGenerator`, `SupportLLM`) is constructed with the agent's configured `max_tokens` and passes it straight through as the underlying `ChatOpenAI` call's own `max_tokens` parameter. This is the standard, low-risk way to cap generation: the API stops generating once the cap is hit (`finish_reason == "length"`) rather than the request failing outright - a truncated-but-present answer beats no answer. When a call is truncated, its `UsageRecord`/`StepRecord` status is set to `"truncated"` instead of `"ok"`, so it surfaces as a visible flag in Logs/Dashboard (the "alerta" from the request) without needing new UI beyond what section 24/26 already builds.
- **`disabled_features` enforcement**: each agent checks its own `disabled_features` list (a list of feature/tool identifiers meaningful to that agent) before using the corresponding capability. Concretely: the Knowledge Agent skips the Tavily web-search fallback entirely when `"web_search"` is in its `disabled_features` - if RAG also finds nothing relevant, it falls through to the existing no-answer graceful response (§ knowledge-agent spec) instead of ever calling Tavily. The Support Agent excludes any tool name present in its `disabled_features` from the tool schemas bound to its LLM call, so the model can never choose a disabled tool in the first place (cleaner than filtering after the fact).

Alternative considered for `max_tokens`: pre-counting the prompt+expected-completion tokens and rejecting the request before calling the LLM at all. Rejected - more complex (needs a tokenizer per model), and rejecting a request outright is a worse user experience than a capped-but-real answer for a challenge-scope config knob.

## Decisions (original)

### Single FastAPI service, in-process agent orchestration (no separate agent microservices)
The challenge scope (4 agents, 1 endpoint) doesn't justify service-per-agent. Each agent is a Python module with a `run(message, context) -> AgentResult` shape, called directly by the orchestrator. Simpler to trace, test, and Dockerize as one container.

### LangChain for orchestration + tool calling; LlamaIndex-style ingestion kept simple
LangChain's tool-calling (`bind_tools`) covers the Router's forced `classify_intent` call and the Support Agent's multi-tool calls with one consistent pattern. For RAG, a thin custom ingestion script (chunk → embed → upsert to Pinecone) is used rather than pulling in LlamaIndex's higher-level abstractions — the corpus is ~4-5 pages, so LlamaIndex's extra machinery isn't earning its complexity. LangChain's `PineconeVectorStore` handles retrieval.
Alternative considered: LlamaIndex end-to-end. Rejected — better suited to larger/more heterogeneous corpora than this challenge's scope.

### Forced tool call for routing via OpenAI `tool_choice`
The Router calls the LLM with a single `classify_intent(intent: Literal[...])` tool and `tool_choice` forcing that tool, so intent always comes from structured tool-call output, never free-text parsing (per the chat-orchestration spec's requirement). Chitchat is a valid `classify_intent` output, not a separate code path — the Router then answers directly instead of dispatching.

### SQLite for observability persistence, JSONL as the raw append log
Every step writes an append-only JSONL line (cheap, crash-safe, trivial to tail) and is also upserted into SQLite tables (`conversations`, `steps`) so the read APIs (`/conversations`, `/conversations/{id}/trace`, `/metrics`, `/agents/usage`, `/tokens/usage`) can do simple SQL aggregation instead of scanning JSONL on every request. JSONL is the source of truth for replay/debugging; SQLite is a derived index.
Alternative considered: SQLite only. Rejected — JSONL gives a human-diffable audit trail and a fallback if the SQLite index ever needs rebuilding.

### Guardrails as a synchronous pre-router stage
Regex checks run first (cheap, no API call), then OpenAI's moderation endpoint. Either failing short-circuits the request with a refusal response that still carries a fresh `trace_id` and a logged (single) guardrail step, per the chat-orchestration spec.

### Escalation Agent's "mock handoff call" as an injected async function
Implemented as a swappable function (default: sleep + canned confirmation payload) so it's easy to point at a real handoff system later without touching the agent's control flow, and easy to mock in tests.

### Frontend state/data-fetching: React Query over the backend REST API
Chosen for its built-in caching, refetch-on-filter-change, and loading/error states, which map directly onto the Dashboard/Logs pages' period filters and the Chat page's in-flight processing state, without hand-rolling fetch/loading logic per page.

### Settings UI persistence: a small backend config store, separate from agent runtime wiring
Agent config (prompt/LLM/temperature/tools/enabled) is persisted via simple `GET/PUT` endpoints backed by a JSON file, independent from the live orchestration's hardcoded agent definitions (see Non-Goals). This keeps the settings-ui spec's save/restore-default behavior real and testable without expanding this change's blast radius into making the router/agents dynamically reconfigurable.

### Tests-ui runs pytest as a subprocess, streamed to the frontend
The Testes page triggers a backend endpoint that runs `pytest --json-report` (or equivalent) for a selected marker/category and streams/polls results back, reusing the same pytest suite required by the proposal rather than re-implementing test logic in TypeScript.

## Risks / Trade-offs

- [Pinecone/Tavily/OpenAI quota or outage during grading] → Mitigation: all three clients are wrapped with clear error surfaces that turn into a graceful `sources: []` / "can't answer" response (per knowledge-agent spec) rather than a 500; README documents required env vars and how to re-run ingestion.
- [RAG corpus staleness if Getnet pages change after ingestion] → Mitigation: ingestion script is re-runnable on demand; README documents the ingested URLs with the ingestion date so staleness is visible, not silent.
- [SQLite write contention under concurrent requests] → Mitigation: challenge-scale traffic (manual/demo testing, not production load) makes this a non-issue; noted here only so it isn't mistaken for an oversight.
- [Running pytest as a subprocess from an HTTP endpoint is unusual for production systems] → Mitigation: acceptable because the Testes page is an explicit challenge requirement for a reviewer-facing demo tool, not a production feature; the endpoint is local-only (no auth is in scope) and out of scope for hardening per the proposal's Out of Scope section.
- [Guardrails regex + moderation may over- or under-block] → Mitigation: guardrail rules and moderation-call behavior are covered by their own pytest suite (per proposal's Testing section) so blocking behavior is verifiable, not just eyeballed.
- [Revision 1] Brand guide colors mostly unconfirmed - only 4 of the ~10 tokens (3 reds + 1 neon) come from the actual guide; the rest are estimated to match → Mitigation: every neon token is named and isolated in one `@theme` block specifically so swapping in exact values later touches one file, not every component.
- [Revision 1] `POST /feedback` has no correctness signal to validate against (unlike the classify_intent/RAG scenarios, there's no "right answer" for a subjective rating) → Mitigation: tested for persistence and correct trace_id/agent_used association, not for "correct" ratings.
- [Revision 1] Moving Logs/Testes from routes to embedded sections changes existing frontend navigation tests (App.test.tsx asserts 5 routes) → Mitigation: that test gets updated as part of this revision's tasks, not left broken.
- [Revision 1] `max_tokens` enforcement via truncation means a capped agent can return a visibly cut-off answer (e.g. mid-sentence) → Mitigation: this is the deliberate, disclosed trade-off vs. rejecting the request outright (see the new Decision's "Alternative considered"); the `"truncated"` step status makes it diagnosable in Logs rather than a silent quality regression.

## Open Questions

None — all decisions above are resolved for this change; nothing here would change the specs, the approach, or the task breakdown if answered later.

**Revision 1 note:** the sections above marked "Revision 1" were added after the original scope (Context, Goals, and the un-labeled Decisions/Risks) was already fully implemented, tested live, and delivered. They describe a second pass over the same codebase, not a greenfield addition - see `tasks.md` sections 23-28.
