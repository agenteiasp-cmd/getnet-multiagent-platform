## 1. Backend Project Setup

- [x] 1.1 Scaffold the Python 3.12 FastAPI project (`backend/`) with `pyproject.toml`/`requirements.txt`, and verify `uvicorn` boots an empty app locally
- [x] 1.2 Add `pydantic-settings` config module reading `OPENAI_API_KEY`, `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`, `PINECONE_INDEX_NAME`, `TAVILY_API_KEY`, and verify it raises a clear error when a required var is missing
- [x] 1.3 Add `.env.example` with the five variable names and no real values, and verify no real secret is committed
- [x] 1.4 Set up the project's module layout (agents/, tools/, rag/, observability/, api/) and verify `pytest` collects zero tests without error

## 2. Guardrails

- [x] 2.1 Implement the regex-based guardrail rule set (blocked patterns, e.g. prompt-injection/secret-exfiltration attempts) and verify unit tests confirm each rule blocks its target input and passes safe input
- [x] 2.2 Implement the OpenAI moderation check call and verify a unit test (mocked LLM) confirms flagged content is blocked
- [x] 2.3 Wire guardrails as the first stage of the chat pipeline, short-circuiting with a refusal response (including a fresh `trace_id`) before the Router runs, and verify an integration test shows no Router/agent call happens on a blocked message

## 3. Router Agent

- [x] 3.1 Define the `classify_intent` tool schema (`Literal["knowledge","support","escalation","chitchat"]`) and implement the Router's forced tool-call classification, verified by a unit test (LLM mocked) asserting the tool is always called with `tool_choice` forced
- [x] 3.2 Implement the Router's direct chitchat reply path, verified by a unit test (LLM mocked) that chitchat-classified input returns a direct answer with no specialist dispatch
- [x] 3.3 Implement Router → specialist dispatch (knowledge/support/escalation), verified by an integration test asserting each intent routes to the corresponding agent module

## 4. Knowledge Agent — RAG Ingestion

- [x] 4.1 Write the ingestion script that fetches `https://www.getnet.net/en` plus 2-3 additional Getnet FAQ/blog/product pages (covering Get Clássica, Get Smart, Payment Link, antecipação de recebíveis), chunks the content, and verify it produces non-empty chunks for each source URL
- [x] 4.2 Implement embedding + upsert of chunks into the Pinecone index (via `PINECONE_INDEX_NAME`), and verify a test run against a test/mock index confirms the expected vector count is upserted
- [x] 4.3 Record each ingested URL with its ingestion date to a manifest file consumed by the README, and verify the manifest lists every ingested source with a date

## 5. Knowledge Agent — Retrieval & Web Search Fallback

- [x] 5.1 Implement the Pinecone retrieval tool (top-k passage lookup) and verify a unit test (mocked vector store) returns passages with source URLs
- [x] 5.2 Implement the Tavily web-search tool and verify a unit test (mocked Tavily client) returns results with source URLs
- [x] 5.3 Implement the Knowledge Agent's in-scope-vs-out-of-scope decision (RAG vs web search) and generation step, verified by unit tests (LLM mocked) covering: Get Clássica vs Get Smart, antecipação de recebíveis (RAG path), and a weather question (web-search path)
- [x] 5.4 Implement the no-relevant-knowledge fallback response, verified by a unit test asserting no answer is fabricated when retrieval and web search both return nothing useful

## 6. Support Agent

- [x] 6.1 Create the mocked per-user dataset (accounts, Pix bank account, transactions, device/connectivity status, installment plans) keyed by `user_id`, and verify it includes fixtures covering every example case in the proposal
- [x] 6.2 Implement the settlement/deposit-schedule lookup tool and verify a unit test (mocked LLM) confirms it's called for a deposit-timing question and returns the correct mocked value
- [x] 6.3 Implement the transaction/device lookup tool (transaction status, decline reason, device connectivity, installments) and verify a unit test confirms it's called for a transaction/device question and returns the correct mocked value — implemented as separate `get_transaction_status` and `get_device_status` tools (plus `get_account_info`/`get_installment_plan`) rather than one merged tool, so the LLM can pick the right one per question; same behavior, finer granularity
- [x] 6.4 Implement the Support Agent's generation step tying tool output to a natural-language answer, verified by unit tests (LLM mocked) covering: Pix bank account, maquininha sem internet, declined transaction, and crediário installments
- [x] 6.5 Implement the unknown-`user_id` graceful fallback, verified by a unit test asserting no error/crash when `user_id` has no mocked data

## 7. Escalation Agent

- [x] 7.1 Implement the mock handoff call as a swappable async function returning a canned confirmation, and verify a unit test confirms it's invoked and its result is captured
- [x] 7.2 Implement the Escalation Agent's response generation confirming handoff to the user with `agent_used="escalation"`, verified by a unit test — implemented as a deterministic templated confirmation (no LLM call) rather than an LLM-generated reply, since a critical handoff confirmation should not risk hallucinated ticket details; behavior required by the spec (confirmation text, `agent_used="escalation"`) is unaffected
- [x] 7.3 Verify the handoff call name appears in `tools_used` and is captured as an observability step (integration test) — verified at agent level now (`tools_used` + `UsageRecord`); full persisted-trace wiring completes in section 9.3

## 8. Chat Orchestration Endpoint

- [x] 8.1 Implement `POST /chat` request/response Pydantic v2 models matching the contract (`message`, `user_id` in; `response`, `agent_used`, `intent`, `sources`, `tools_used`, `trace_id` out), verified by a schema/unit test rejecting a request missing `message` or `user_id`
- [x] 8.2 Wire the full pipeline (guardrails → router → knowledge/support/escalation/chitchat) behind `POST /chat`, generating a unique `trace_id` per request, verified by an integration test asserting `agent_used`/`intent`/`sources`/`tools_used` are consistent with the path taken
- [x] 8.3 Run the end-to-end pytest suite against the 10 challenge example cases (Get Clássica x Get Smart, weather, deposit timing, Pix bank account, maquininha sem internet, antecipação de recebíveis, transação recusada, parcelamento crediário, venda via WhatsApp com Payment Link, plus one escalation case) and verify every case returns a well-formed response with the expected `intent`/`agent_used` — run live against real OpenAI/Pinecone/Tavily (backend/.env); found and fixed a real router misclassification (weather → chitchat instead of knowledge) by sharpening the classify_intent tool description and Router system prompt; all 10/10 pass live

## 9. Observability — Capture & Persistence

- [x] 9.1 Implement the step-record model (timestamp, input, output, model, tokens, latency, status) and a logger that writes one JSONL line per step, verified by a unit test asserting each pipeline stage (guardrail, router, agent, tool, LLM) emits a record
- [x] 9.2 Implement the SQLite schema (`conversations`, `steps`) and an indexer that upserts each JSONL record into it, verified by a test asserting records written in one process run are readable from SQLite after a fresh process start
- [x] 9.3 Wire the observability logger into the guardrails/router/agents/tools code paths from sections 2-8, verified by an integration test asserting a single `/chat` call produces a coherent multi-step trace under one `trace_id` — also smoke-tested live through the real wired app (real trace_id, tokens, latency written to JSONL + SQLite)

## 10. Observability — Read APIs

- [x] 10.1 Implement `GET /conversations` (list with `conversation_id`, `user_id`, timestamps, summary), verified by an integration test against seeded SQLite data
- [x] 10.2 Implement `GET /conversations/{id}/trace` (ordered steps; 404 on unknown id), verified by integration tests for both the found and not-found cases
- [x] 10.3 Implement `GET /metrics` with period/date-range filtering (counts, latency, error rate), verified by an integration test asserting the filter changes the returned aggregate
- [x] 10.4 Implement `GET /agents/usage` (invocation counts per agent per period), verified by an integration test
- [x] 10.5 Implement `GET /tokens/usage` (token counts + estimated cost per period, by agent/model), verified by an integration test

## 11. Agent Configuration Store (for Settings UI)

- [x] 11.1 Implement a JSON-file-backed config store for per-agent settings (prompt, LLM, temperature, tools, enabled) with sane defaults for Router/Knowledge/Support/Escalation
- [x] 11.2 Implement `GET /agents/config` and `PUT /agents/config/{agent}` (save) plus a restore-default action, verified by an integration test asserting save persists and restore reverts to the original default

## 12. Backend Test Runner API (for Testes UI)

- [x] 12.1 Implement an endpoint that runs a selected pytest category/marker as a subprocess (e.g. `--json-report`) and returns/streams per-test results (name, passed/failed, duration, error), verified by an integration test triggering a small marked test subset and asserting the parsed result shape

## 13. Backend Test Suite Completeness Check

- [x] 13.1 Verify `pytest` (full suite) passes locally covering: per-agent/tool unit tests with LLM mocked, Router integration test, guardrails test, and the 10-case end-to-end test from 8.3 — 75/75 passed (60s), including the live e2e cases

## 14. Docker

- [x] 14.1 Write `backend/Dockerfile` (Python 3.12 slim, installs deps, runs `uvicorn`), and verify `docker build` succeeds — image built successfully
- [x] 14.2 Write `docker-compose.yml` wiring the backend service and env file, and verify `docker compose up` serves `POST /chat` and returns a valid response for a chitchat message — verified live (hit a host disk-space issue during image export, fixed with `docker builder prune`, unrelated to the app code)

## 15. Frontend Project Setup

- [x] 15.1 Scaffold the React + TypeScript + Vite project (`frontend/`) with Tailwind configured with a Getnet-green light theme (primary color, card styles), and verify `npm run dev` renders a blank shell — Tailwind v4 via `@tailwindcss/vite`, custom `getnet-*` green palette in `src/index.css`
- [x] 15.2 Implement the fixed sidebar with the five routes (Chat, Dashboard, Logs & Observabilidade, Configurações, Testes) and verify navigating each route renders its (placeholder) page — Vitest + Testing Library set up for the whole frontend; routing test covers all 5 routes
- [x] 15.3 Implement a typed API client for the backend endpoints (`/chat`, `/conversations`, `/conversations/{id}/trace`, `/metrics`, `/agents/usage`, `/tokens/usage`, `/agents/config`, test-runner endpoint) with a configurable base URL, and verify a smoke call against the running backend from section 14.2 succeeds

## 16. Chat Page

- [x] 16.1 Implement message history rendering with differentiated user/AI bubbles and timestamps, verified by a component test rendering a mixed conversation
- [x] 16.2 Implement send-message flow calling `POST /chat` with a processing indicator shown while in flight and cleared on response, verified by a component test simulating a pending then resolved request
- [x] 16.3 Implement conditional sources rendering (shown only when `sources` is non-empty), verified by component tests for both cases
- [x] 16.4 Implement the live agent-flow side panel (active agent highlighted, elapsed time, tool used, tokens) updating during and after a request, verified by a component test asserting panel state before/after response resolution
- [x] 16.5 Manually verify in a browser against the running backend: send at least 3 of the challenge example messages and confirm history, sources, and the agent-flow panel behave correctly — verified with a real Chromium browser (Playwright) against the live Docker backend: knowledge/support/escalation all confirmed working, including a markdown-rendering fix for AI responses

## 17. Dashboard Page

- [x] 17.1 Implement the period filter control and data re-fetch on change, verified by a component test asserting the API is called with the new range — this test caught a real infinite-refetch bug (unmemoized `new Date()` in the query key), fixed with `useMemo`
- [x] 17.2 Implement the service-volume chart backed by `GET /metrics`, verified by a component test with mocked API data
- [x] 17.3 Implement the agent-usage chart backed by `GET /agents/usage`, verified by a component test with mocked API data
- [x] 17.4 Implement the token/cost chart backed by `GET /tokens/usage`, verified by a component test with mocked API data
- [x] 17.5 Manually verify in a browser against the running backend: generate a few chat requests, then confirm the Dashboard reflects them after a period change — verified live with Playwright/Chromium against the Docker backend

## 18. Logs & Observabilidade Page

- [x] 18.1 Implement the overview section shown before a conversation is selected, verified by a component test
- [x] 18.2 Implement the conversation list (by `conversation_id`, with timeline) backed by `GET /conversations`, verified by a component test with mocked API data
- [x] 18.3 Implement the step-by-step visual trace view backed by `GET /conversations/{id}/trace`, verified by a component test with mocked API data
- [x] 18.4 Implement multi-filter support (agent, status, date range) narrowing the conversation list, verified by a component test combining filters
- [x] 18.5 Implement the clickable errors area that opens the related conversation's trace at the failing step, verified by a component test
- [x] 18.6 Implement the performance section (latency breakdown per agent/step), verified by a component test with mocked API data
- [x] 18.7 Manually verify in a browser against the running backend: locate a real conversation's trace end to end through the UI — verified live with Playwright/Chromium; also found/fixed missing jsdom `scrollIntoView` stub needed for the tests

## 19. Configurações Page

- [x] 19.1 Implement the per-agent configuration cards (prompt, LLM, temperature, tools, enable/disable) backed by `GET /agents/config`, verified by a component test
- [x] 19.2 Implement the prompt editor's Save action calling `PUT /agents/config/{agent}`, verified by a component test asserting the persisted value is reflected after save
- [x] 19.3 Implement the Restore Default action, verified by a component test asserting the prompt reverts
- [x] 19.4 Implement the enable/disable toggle's visible state update, verified by a component test

## 20. Testes Page

- [x] 20.1 Implement the terminal-style test-run UI triggering the backend test-runner endpoint (12.1) and streaming/polling output, verified by a component test with mocked API data — implemented as progressive reveal of the full result (no SSE/websockets, per design.md's Non-Goals)
- [x] 20.2 Implement the per-test result list (passed/failed, duration, error), verified by a component test
- [x] 20.3 Manually verify in a browser against the running backend: run a real test category and confirm results render correctly — verified live; found and fixed a real gap where the Docker image excluded `tests/` and dev dependencies, so `/tests/run` failed in the container (Dockerfile/.dockerignore now include them)

## 21. Documentation

- [x] 21.1 Write `README.md` covering build/configure/run/test instructions (local and Docker) for both backend and frontend, and verify each documented command runs successfully as written
- [x] 21.2 Document the orchestration architecture and message workflow (guardrails → router → knowledge/support/escalation/chitchat) with the response contract
- [x] 21.3 Document the RAG pipeline (ingestion → storage → retrieval → generation), including the ingested URLs with ingestion dates from the manifest (4.3)
- [x] 21.4 Document how LLM tools were used (forced `classify_intent`, retrieval tool, web-search tool, support tools, escalation mock call)
- [x] 21.5 Document guardrails (regex rules + moderation) and the reliability/observability implementation (trace_id, step logging, persistence, read APIs)
- [x] 21.6 Document the evaluation/observability strategy (what the Dashboard, Logs & Observabilidade, and Testes pages show, and how they support judging quality) and note the Escalation Agent as the challenge's fourth-agent differentiator

## 22. Final End-to-End Verification

- [x] 22.1 Run `docker compose up`, then execute all 9 non-escalation challenge example cases plus one escalation-triggering message against the running stack, and verify each returns the expected `intent`/`agent_used` with a non-empty `trace_id` — 10/10 passed live over HTTP against the Docker container
- [x] 22.2 With the backend running, start the frontend and manually walk all five sidebar pages against live data (not mocks), confirming no page errors and that Chat-generated activity appears in Dashboard and Logs & Observabilidade — verified live with Playwright: zero console errors across all 5 pages, Dashboard/Logs both reflect the 18 real conversations generated during this session

---

**Revision 1** (sections 23-28 below): visual identity, chat quick replies/feedback, friendly agent-flow panel, Dashboard/Settings IA consolidation, and new Settings fields — added after sections 1-22 above were already fully implemented and verified live. See design.md's "Decisions (Revision 1 ...)" for the rationale behind each choice.

## 23. Visual Identity Revamp (Dark/Neon Theme)

- [x] 23.1 Replace the Tailwind theme tokens in `frontend/src/index.css` with a dark-first tech/neon palette (black/dark-gray/white base; `--color-brand-red`/`-2`/`-3` and `--color-neon-yellow` from the confirmed brand-guide values; estimated `--color-neon-pink`/`-purple`/`-cyan`/`-lime` clearly labeled as estimates; subtle gradients on card/header backgrounds), defined as reusable `@theme` tokens, and verify `npm run build` succeeds
- [x] 23.2 Add a light-theme override (`[data-theme="light"]`) using the same token set, if it can be done without component-level branching, and verify both themes render with legible contrast — implemented as theme-aware CSS variables (dark default, `prefers-color-scheme`/`data-theme` overrides) plus a Sidebar toggle button persisted to localStorage; no component branching needed
- [x] 23.3 Update every existing component/page's `getnet-*` color classes to the new token names — kept the `getnet-*` class names but made their underlying values theme-aware (avoids touching every file's class strings); did touch `bg-white` literals (→ `bg-surface-card`) and chart fill colors (→ neon accents) across the affected files; all existing Vitest component tests pass
- [x] 23.4 Manually verify in a browser: Chat, Dashboard, Configurações all render in the new dark theme with neon accents visible in charts/badges/status indicators — verified live with Playwright/Chromium in both dark and light themes; found and fixed a real contrast bug (`text-getnet-500`/`600` collided with the new brand-red token, making most secondary/muted text red) across ~20 components before it looked right

## 24. Chat Quick Replies & Per-Message Feedback

- [x] 24.1 Add a configurable quick-reply suggestion list (e.g. `frontend/src/lib/quickReplies.ts`, not hardcoded inline) and render it as clickable buttons that fill/send the associated message, verified by a component test
- [x] 24.2 Backend: add a `feedback` table (trace_id, agent_used, rating, created_at) to the SQLite observability store and a `POST /feedback` endpoint to persist a rating, verified by an integration test
- [x] 24.3 Backend: add `GET /agents/feedback` returning per-agent rating aggregates (% positive, average score), period-filterable, verified by an integration test
- [x] 24.4 Frontend: add a 👍/👎 control on each AI message wired to `POST /feedback` with that message's `trace_id`/`agent_used`, verified by a component test asserting the correct payload and that the control reflects submitted state
- [x] 24.5 Frontend: add the per-agent rating metric to the Dashboard backed by `GET /agents/feedback`, verified by a component test with mocked API data
- [x] 24.6 Manually verify in a browser against the running backend: send a message, submit a rating, and confirm it shows up in the Dashboard's rating metric — verified live: 👍 on a knowledge-agent response, "Obrigado pelo feedback!" shown, Dashboard's "Avaliação por agente" chart reflects it

## 25. Friendly Agent-Flow Panel

- [x] 25.1 Add a technical-step → friendly-label dictionary covering every step name the backend emits (guardrails.check, router.classify_intent, router.chitchat_reply, knowledge.rag_generate/web_generate, support.decide_tools/generate_answer, escalation.mock_handoff_call) and use it as the panel's default display, verified by a component test
- [x] 25.2 Add a status icon per step (done ✅/truncated ⚠️/error ❌ - "waiting/processing" is the existing panel-level processing indicator, since steps only arrive once the full response resolves, per design.md's no-streaming Non-Goal) and duration formatted in seconds, verified by a component test
- [x] 25.3 Add an optional "detalhes técnicos" toggle revealing technical step name, model, and token counts only when expanded, verified by a component test for both collapsed and expanded states
- [x] 25.4 Manually verify in a browser against the running backend: send a message and confirm friendly labels show by default, technical details only when expanded — verified live: friendly Portuguese labels + ✅ icons + seconds by default, "guardrails.check"/model/token counts only appear after clicking "Detalhes técnicos"

## 26. Dashboard/Logs Consolidation

- [x] 26.1 Remove the "Logs & Observabilidade" sidebar entry and its `/logs` route; move its existing components (overview, conversation list, trace view, filters, errors panel, performance section) into a collapsible section at the end of `DashboardPage`, collapsed by default, styled consistently with the rest of the page, verified by a component test — reused the existing `LogsPage` component wrapped in a new `CollapsibleSection` (native `<details>`), rather than duplicating its internals
- [x] 26.2 Update `App.test.tsx`'s route-coverage test to reflect the new 3-route sidebar (Chat, Dashboard, Configurações) instead of 5, and verify it passes
- [x] 26.3 Verify all existing Logs component tests (conversation list, trace view, filters, errors, performance) still pass unchanged against their relocated components — `LogsPage.test.tsx` (6 tests) unaffected since it still renders `LogsPage` directly
- [x] 26.4 Manually verify in a browser against the running backend: open Dashboard, expand the Logs & Observabilidade section, confirm conversation list/trace/filters/errors/performance all still work end-to-end — verified live: section collapsed by default, expands with real conversation list on click

## 27. Configurações: Additional Fields & Embedded Testes

- [x] 27.1 Backend: extend the agent config model/store and `AgentConfigUpdate` schema to accept `model`, `max_tokens`, and `disabled_features` — `model` was already present; added the other two to `DEFAULT_AGENT_CONFIGS` and `AgentConfigUpdate`; the store's shallow-merge `update()` needed no changes
- [x] 27.2 Backend: wire `max_tokens` into each agent's LLM wrapper (`RouterLLM`, `GroundedGenerator`, `SupportLLM`) so it's passed as the underlying `ChatOpenAI` call's max-output-tokens parameter, and mark a truncated call's observability step status `"truncated"` instead of `"ok"`, verified by a unit test (LLM mocked to return a truncated `finish_reason`) asserting both the cap is passed through and the status is set — also confirmed `max_tokens=None` (default) doesn't break real live calls (10/10 e2e cases still pass)
- [x] 27.3 Backend: wire `disabled_features` enforcement — Knowledge Agent skips the Tavily tool entirely when `"web_search"` is disabled (falls through to the existing no-answer response if RAG also finds nothing), Support Agent excludes any disabled tool name from the tool schemas bound to its LLM call — verified by unit tests for both agents asserting the disabled feature/tool is never invoked while others still work; `get_orchestrator`'s cache is now cleared on every `PUT`/`restore-default` config change so enforcement takes effect on the next request without a restart
- [x] 27.4 Frontend: add an LLM/model selector (dropdown), a max-token-usage field, and per-feature disable toggles to each agent's configuration card, persisted via the existing `PUT /agents/config/{agent}`, verified by a component test
- [x] 27.5 Remove the "Testes" sidebar entry and its `/tests` route; move its existing components (category selector, terminal output, results list) into a "Testes" tab within `SettingsPage`, alongside new "Agentes"/"Prompts"/"LLMs" tabs, verified by a component test — Prompts/LLMs tabs are lightweight focused views (all-prompts list; agent→model/max-tokens table) reusing the same handlers as the Agentes tab, not new data
- [x] 27.6 Update `App.test.tsx`'s route-coverage test for the final 3-route sidebar (if not already done in 26.2) and verify it passes — done together with 26.2
- [x] 27.7 Manually verify in a browser against the running backend: set a low max-token ceiling on an agent and confirm a truncated step shows up in Logs; disable the Knowledge Agent's web search and confirm an out-of-scope question now gets the no-answer response instead of a web result; then open the Testes tab and run a real test category — verified live; found and fixed two real bugs in the process: (1) a low `max_tokens` on the Router crashed the forced `classify_intent` tool call with a 500 (fixed: the ceiling now applies only to open-ended generation, never to forced/tool-selection calls, for Router and Support alike), (2) the disable-feature check compared against the wrong string (`"web_search"` vs the tool's real name `"tavily_web_search"`) so it silently never triggered (fixed, plus the stale test that only passed because it used the same wrong string on both sides)

## 28. Final Re-verification

- [x] 28.1 Run the full backend pytest suite and confirm no regressions from the feedback/config-model changes — 87/87 passed, including live e2e
- [x] 28.2 Run the full frontend Vitest suite and confirm no regressions from the theme/consolidation changes — 34/34 passed, build clean
- [x] 28.3 Rebuild and restart `docker compose`, then manually walk the new 3-item sidebar (Chat, Dashboard, Configurações) against the live backend, confirming quick replies, feedback, the friendly agent-flow panel, the embedded Logs section, and the embedded Testes tab all work with real data — verified live, zero console errors
- [x] 28.4 Update `README.md` to reflect the new 3-page sidebar structure, the new visual identity, and the feedback/config additions
