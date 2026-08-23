## Why

The Getnet support challenge requires a working multiagent AI customer-service system: a backend that routes user messages through guardrails and a router agent to the right specialist (knowledge/RAG, support, escalation, or chitchat), plus a SaaS-style frontend that lets a reviewer chat with the system and inspect how the orchestration behaved (which agent ran, which tools fired, token/latency cost, and full traces). Today neither exists. Building both, backend first, gives the frontend a real API to observe instead of mocked data.

## What Changes

- Add a FastAPI backend exposing a single `POST /chat` endpoint (`message`, `user_id` in; `response`, `agent_used`, `intent`, `sources`, `tools_used`, `trace_id` out).
- Add a guardrails stage (regex-based input checks + moderation) that runs before any agent sees the message.
- Add a Router Agent that classifies intent via a forced tool call (`classify_intent`) into `knowledge`, `support`, `escalation`, or `chitchat`, and answers chitchat directly.
- Add a Knowledge Agent: RAG over an ingested Getnet knowledge base (Pinecone vector store, LangChain/LlamaIndex pipeline) for in-scope questions, falling back to Tavily web search for out-of-scope questions (e.g. weather).
- Add a Support Agent with 2+ tools operating on mocked per-user account/transaction data (deposit timing, Pix bank account, transaction status, installments, etc.).
- Add an Escalation Agent (the challenge's differentiator) that performs a mocked human-handoff call and returns a handoff confirmation.
- Add end-to-end observability: a unique `trace_id` per request, structured step-level records (router/agent/tool/LLM calls with timestamp, input, output, model, tokens, latency, status) persisted to SQLite/JSONL.
- Add read APIs consumed by the frontend: `GET /conversations`, `GET /conversations/{id}/trace`, `GET /metrics`, `GET /agents/usage`, `GET /tokens/usage`, all backed by the persisted logs.
- Add ingestion of the Getnet knowledge base (`https://www.getnet.net/en` plus 2-3 additional FAQ/blog/product pages covering Get Clássica, Get Smart, Payment Link, and antecipação de recebíveis), with ingested URLs and ingestion date documented in the README.
- Add pytest coverage: per-agent/tool unit tests (LLM mocked), Router integration test, guardrails test, and an end-to-end test running the challenge's 10 example cases.
- Add `Dockerfile` + `docker-compose.yml` so `docker compose up` runs the full backend.
- Add a React + TypeScript + Vite + Tailwind SaaS frontend (Getnet green/light visual identity) with a fixed sidebar: Chat, Dashboard, Logs & Observabilidade, Configurações, Testes.
- Add the Chat page: conversation history, differentiated user/AI messages with timestamps, processing/status indicators, sources display, and a live side panel showing per-request agent flow (status, elapsed time, tool used, tokens, active agent highlighted).
- Add the Dashboard page: period filter plus charted metrics for service volume, agent usage, and token/cost.
- Add the Logs & Observabilidade page: overview, conversation list by `conversation_id` with timeline, per-step visual trace, multi-filter search, a clickable error area that opens the related trace, and a performance section.
- Add the Configurações page: one card per agent (prompt, LLM, temperature, tools, enable/disable toggle) with a prompt editor supporting Save/Restore-default.
- Add the Testes page: a terminal-style UI that runs backend test categories and shows pass/fail, duration, and error per case.
- Add a complete README covering build/configure/run/test instructions, orchestration architecture, the message workflow, the RAG pipeline (ingestion → storage → retrieval → generation), how LLM tools were used, guardrails, and the reliability/observability and evaluation strategy.

Out of scope for this change: authentication/multi-tenancy, cloud deployment, CI/CD.

## Capabilities

### New Capabilities
- `chat-orchestration`: the `POST /chat` contract, guardrails stage, and Router Agent (forced-tool-call intent classification, chitchat direct-answer path, dispatch to the knowledge/support/escalation agents).
- `knowledge-agent`: RAG pipeline over the ingested Getnet knowledge base via Pinecone (ingestion → storage → retrieval → generation) with Tavily web-search fallback for out-of-scope questions.
- `support-agent`: Support Agent and its 2+ tools reading mocked per-user account/transaction data.
- `escalation-agent`: Escalation Agent performing a mocked handoff call and returning a handoff response.
- `observability`: trace_id generation, per-step structured logging and persistence (SQLite/JSONL), and the read APIs (`/conversations`, `/conversations/{id}/trace`, `/metrics`, `/agents/usage`, `/tokens/usage`) that expose them.
- `chat-ui`: the frontend Chat page (history, message rendering, sources, live agent-flow panel).
- `dashboard-ui`: the frontend Dashboard page (period filter, charted service/agent/token metrics).
- `logs-observability-ui`: the frontend Logs & Observabilidade page (conversation list, timelines, trace view, filters, error drill-down, performance section).
- `settings-ui`: the frontend Configurações page (per-agent config cards, prompt editor with save/restore).
- `tests-ui`: the frontend Testes page (terminal-style test runner and results view).

### Modified Capabilities
None — this is a greenfield build; no existing specs are being changed.

## Impact

- **New code**: a Python 3.12/FastAPI backend service (agents, tools, guardrails, RAG ingestion/query, persistence, read APIs) and a React/TypeScript/Vite frontend (5 pages + shared chat/observability components).
- **New external dependencies**: OpenAI API, Pinecone (vector store), Tavily (web search) — all configured via `pydantic-settings` env vars with a values-free `.env.example`.
- **New infra**: `Dockerfile` + `docker-compose.yml` for the backend; the frontend runs via its own dev/build tooling and talks to the backend over HTTP.
- **New data**: a persisted trace/log store (SQLite or JSONL) that both the backend and the frontend's read APIs depend on.
- **Docs**: a new top-level `README.md` covering setup, architecture, RAG pipeline, tool usage, guardrails, and the observability/evaluation strategy.
