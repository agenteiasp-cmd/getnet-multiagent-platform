# Getnet Multiagent Support Platform

A multiagent AI customer-support platform for Getnet: a FastAPI orchestration
backend (guardrails → router → knowledge/support/escalation agents) plus a
React/TypeScript SaaS frontend for chatting with it and observing how the
orchestration behaved.

- **Backend**: `backend/` — Python 3.12, FastAPI, LangChain, Pinecone, Tavily, OpenAI.
- **Frontend**: `frontend/` — React 19, TypeScript, Vite, Tailwind CSS v4.

---

## 1. Quick start

### 1.1 With Docker (backend only)

```bash
cp backend/.env.example backend/.env
# fill in OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENVIRONMENT,
# PINECONE_INDEX_NAME, TAVILY_API_KEY in backend/.env

docker compose up --build
```

This builds and starts the backend at `http://localhost:8000`. Try it:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "oi, tudo bem?", "user_id": "user-1"}'
```

The `docker` image includes the `tests/` suite and dev dependencies, so the
frontend's **Testes** page (which triggers `POST /tests/run`, a real `pytest`
subprocess) also works against the containerized backend, not just a local
dev setup.

### 1.2 Frontend

The frontend is not part of `docker-compose.yml` (only the backend is, per
scope) — run it with Node/npm, pointed at the backend:

```bash
cd frontend
cp .env.example .env   # VITE_API_BASE_URL=http://localhost:8000
npm install
npm run dev
```

Open `http://localhost:5173`.

---

## 2. Local development (without Docker)

### 2.1 Backend

Requires Python 3.12 (a 3.13 venv also works for local dev/tests; the Docker
image pins 3.12 exactly, per the challenge's stack requirement).

```bash
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt   # includes requirements.txt + pytest tooling
cp .env.example .env                  # fill in real credentials
uvicorn app.main:app --reload
```

Run the RAG ingestion once (creates the Pinecone index if it doesn't exist,
embeds and upserts the Getnet corpus - see §4):

```bash
python -m app.rag.ingest
```

### 2.2 Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 3. Testing

### 3.1 Backend (pytest)

```bash
cd backend
source .venv/bin/activate
pytest                 # full suite
pytest tests/test_guardrails.py tests/test_router.py   # a subset
```

The suite covers, per agent/tool with the LLM mocked, plus real integration
paths:

- Guardrails (regex rules + moderation, both blocking and pass-through)
- Router (forced `classify_intent` tool call, chitchat direct-reply, dispatch)
- Knowledge Agent (RAG path, web-search fallback, no-answer fallback)
- Support Agent (each of its 5 tools, per-user data scoping, unknown-user fallback)
- Escalation Agent (mock handoff call, response, observability capture)
- `POST /chat` contract (validation, envelope consistency)
- Observability (JSONL logger, SQLite store/index, end-to-end trace coherence)
- Observability read APIs (`/conversations`, `/conversations/{id}/trace`, `/metrics`, `/agents/usage`, `/tokens/usage`)
- Agent config store + its read/write/restore-default API
- The test-runner API itself (`/tests/run`)
- **An end-to-end test against all 10 challenge example cases, run live against real OpenAI/Pinecone/Tavily** (skipped automatically if `backend/.env` has no credentials configured)

The same suite is also runnable from the frontend's **Testes** page, which
calls `POST /tests/run` and shows results in a terminal-style UI.

### 3.2 Frontend (Vitest + Testing Library)

```bash
cd frontend
npm test        # vitest run
```

Every page has component tests with the API client mocked (message
rendering, processing states, conditional sources, the live agent-flow
panel, period-filter refetching, multi-filter conversation search, the
clickable errors-to-trace flow, prompt save/restore, and the test-runner UI).

---

## 4. Architecture

### 4.1 Message workflow

```
POST /chat { message, user_id }
        │
        ▼
  Guardrails (regex rules, then OpenAI moderation)
        │  blocked? ──► refusal response (trace_id present, no agent ran)
        ▼ safe
  Router Agent
        │  forced tool call: classify_intent → knowledge | support | escalation | chitchat
        │
        ├─ chitchat ──────────────► Router answers directly
        ├─ knowledge ─────────────► Knowledge Agent (RAG or web search)
        ├─ support ───────────────► Support Agent (tool-calling over mocked user data)
        └─ escalation ────────────► Escalation Agent (mock human handoff)
        │
        ▼
  { response, agent_used, intent, sources, tools_used, trace_id }
```

Every request gets a unique `trace_id` (generated before guardrails run, so
it's present even on a rejection) and every step along the way - guardrail
check, router classification, agent generation, every tool/LLM call - is
captured as an observability step under that same `trace_id` (§8).

### 4.2 Why a 5th "guardrails" pseudo-agent

`agent_used` can be `"guardrails"` when a message is blocked before reaching
the Router - this keeps the response contract uniform (always has an
`agent_used`/`intent` pair) instead of a special-cased error shape.

### 4.3 Visual identity

Dark-first "tech/neon" theme (default; toggle in the sidebar switches to a
light variant, persisted in `localStorage`), replacing an earlier
light-green draft. Base surfaces are black/dark-gray/white; Getnet red
(`#EC0000`, confirmed from the brand guide) is a restrained accent for the
logo and primary actions, not the dominant color; a neon accent set
(`frontend/src/lib/theme.ts`) differentiates chart series and badges - only
`--color-neon-yellow` is confirmed from the brand guide, the other four
(pink/purple/cyan/lime) are estimated to match and clearly labeled as such
in `frontend/src/index.css`, ready to swap for exact values. All colors are
CSS custom properties (`@theme` tokens), never hardcoded per-component.

### 4.4 Frontend structure (3-page sidebar)

The sidebar has three items, not five - two of the original five pages are
embedded as sections/tabs of another page instead of separate routes:

- **Chat**: history, quick-reply suggestions (`lib/quickReplies.ts`,
  configurable), 👍/👎 feedback per AI message, and the live agent-flow
  panel - friendly Portuguese labels by default (`lib/stepLabels.ts`), with
  an opt-in "detalhes técnicos" toggle for the raw step name/model/tokens.
- **Dashboard**: period-filterable metrics/agent-usage/token-cost/rating
  charts, plus the full **Logs & Observabilidade** view as a collapsible
  section at the bottom of the page (collapsed by default).
- **Configurações**: tabs for **Agentes** (full per-agent cards: prompt,
  LLM/model selector, max token usage, tools with per-tool disable toggles,
  enable/disable), **Prompts** (a focused all-prompts editor),
  **LLMs** (a compact agent→model/max-tokens table), and **Testes** (the
  terminal-style test runner, embedded rather than its own route).

### 4.5 Code layout

```
backend/app/
  main.py             FastAPI app + router registration
  config.py           pydantic-settings (the 5 required env vars)
  orchestrator.py      guardrails → router → dispatch, ties everything together
  guardrails/          regex rules, OpenAI moderation, pipeline
  agents/               router.py, knowledge.py, support.py, escalation.py
  llm/                   thin LangChain ChatOpenAI wrappers per agent
  tools/                 classify_intent, retrieval, web_search, support_tools, escalation_tool
  rag/                   corpus_sources.py, fetch.py, chunk.py, ingest.py, manifest.py
  data/                  mocked per-user dataset (mock_users.py)
  observability/         StepRecord model, JSONL logger, SQLite store, recorder, pricing
  config_store/          JSON-file agent config store (Settings page)
  api/                    chat.py, conversations.py, metrics.py, agents_config.py, test_runner.py, feedback.py
  models/                 Pydantic v2 request/response + internal pipeline dataclasses

frontend/src/
  api/                   typed client + types for every backend endpoint
  components/             chat/, dashboard/, logs/, settings/, tests/, layout/
  pages/                   ChatPage, DashboardPage, SettingsPage (embeds LogsPage/TestsPage)
  hooks/                   useChat, useTestRun, useTheme
  lib/                     quickReplies.ts, stepLabels.ts, theme.ts (neon accent hex), period.ts
```

---

## 5. RAG pipeline

**Ingestion → storage → retrieval → generation**, all in `backend/app/rag/`
and `backend/app/agents/knowledge.py`.

1. **Ingestion** (`rag/ingest.py`, run via `python -m app.rag.ingest`): fetches
   each corpus URL (`rag/corpus_sources.py`) with `httpx`, strips
   nav/script/style noise with BeautifulSoup (`rag/fetch.py`), and splits the
   remaining text into ~1000-character chunks with 150-character overlap
   using LangChain's `RecursiveCharacterTextSplitter` (`rag/chunk.py`).
2. **Storage**: chunks are embedded with OpenAI `text-embedding-3-small` and
   upserted into a Pinecone serverless index (auto-created with
   `cloud="aws", region="us-east-1"` if it doesn't exist yet) via
   `langchain-pinecone`'s `PineconeVectorStore`, tagged with `source_url` and
   `topic` metadata.
3. **Retrieval** (`tools/retrieval.py`): the Knowledge Agent runs a top-k
   similarity search (`asimilarity_search_with_score`) against the same
   vector store for every knowledge-intent question.
4. **Generation** (`agents/knowledge.py`): if any retrieved passage clears a
   relevance-score threshold, the agent generates an answer grounded only in
   those passages (`RAG_SYSTEM_PROMPT`), citing each source's URL. If nothing
   clears the threshold - i.e. the question is judged out of the corpus's
   scope (weather, general trivia, etc.) - the agent instead calls the
   Tavily web-search tool (`tools/web_search.py`) and grounds the answer in
   those results instead. If even web search returns nothing useful, the
   agent says it can't answer rather than fabricating one.

### 5.1 Ingested sources (manifest)

Produced by `rag/manifest.py`, written to `backend/data_store/rag_manifest.json`
on every ingestion run. Current contents:

| URL | Topic | Ingested | Chunks |
|---|---|---|---|
| https://www.getnet.net/en | institutional (mandatory source) | 2026-08-23 | 5 |
| https://site.getnet.com.br/maquininha/get-classica/ | Get Clássica | 2026-08-23 | 5 |
| https://site.getnet.com.br/get-ajuda-maquininha/solucoes-get-smart/ | Get Smart | 2026-08-23 | 3 |
| https://site.getnet.com.br/link-de-pagamento/ | Payment Link | 2026-08-23 | 5 |
| https://site.getnet.com.br/get-ajuda-antecipacao-de-venda/como-antecipar-sua-vendas-pelo-app/ | Antecipação de recebíveis | 2026-08-23 | 3 |
| https://site.getnet.com.br/duvidas/ | FAQ | 2026-08-23 | 75 |
| https://site.getnet.com.br/link-de-pagamento-getnet/ | Blog (Payment Link / WhatsApp selling) | 2026-08-23 | 5 |

Re-run `python -m app.rag.ingest` any time to refresh this table (both the
JSON file and the Pinecone index are updated).

---

## 6. How LLM tools were used

| Tool | Used by | Forced? | Purpose |
|---|---|---|---|
| `classify_intent` | Router | **Yes** (`tool_choice`) | Intent is always read from this tool's structured output, never parsed from free text |
| `pinecone_retrieval` | Knowledge Agent | No (always attempted first) | Top-k passage lookup against the ingested corpus |
| `tavily_web_search` | Knowledge Agent | No (fallback) | Live web search when retrieval isn't relevant enough |
| `get_settlement_schedule`, `get_transaction_status`, `get_device_status`, `get_account_info`, `get_installment_plan` | Support Agent | No (LLM picks 0+ of these) | Real function-calling: the model decides which mocked-data lookups the question needs, results are scoped server-side to the request's `user_id` (never LLM-supplied) |
| `mock_handoff_call` | Escalation Agent | N/A (always called, not an LLM tool) | Mocked external handoff, deterministic confirmation (no LLM call, to avoid hallucinated ticket details) |

The Support Agent is the clearest example of open-ended tool-calling: it
binds all 5 tools to one `ChatOpenAI` call, lets the model choose which
(if any) apply to the question, executes them, then feeds the results back
as `ToolMessage`s in a second call to produce the final answer.

### 6.1 Per-agent `max_tokens` and `disabled_features` (Configurações page)

Each agent's config (`GET/PUT /agents/config/{agent}`) has a `max_tokens`
ceiling and a `disabled_features` list, both **enforced at request time**,
not just displayed:

- **`max_tokens`** is passed straight through as the underlying
  `ChatOpenAI` call's own max-output-tokens parameter - but **only on
  open-ended generation calls** (chitchat reply, RAG/web answer, Support's
  final answer), never on a forced or tool-selection call. A tool call's
  output is small, structured JSON; capping it too aggressively can
  truncate the arguments mid-JSON and break parsing entirely instead of
  just shortening an answer - this was a real bug caught by live testing
  (`tests/test_llm_enforcement.py::test_router_classify_intent_call_is_never_capped`).
  When a call does hit its cap, its observability step status becomes
  `"truncated"` instead of `"ok"`, so it's visible in Logs/Dashboard.
- **`disabled_features`** holds tool names (the same names shown in each
  agent's card, e.g. `tavily_web_search`, `get_installment_plan`) that the
  agent must not use. The Knowledge Agent skips Tavily entirely when
  `tavily_web_search` is disabled (falling through to its no-answer
  response if RAG also finds nothing); the Support Agent excludes any
  disabled tool from the schemas bound to its LLM call, so the model can
  never select it in the first place.

Saving either field clears the cached orchestrator (`get_orchestrator.cache_clear()`
in `api/agents_config.py`) so the change applies on the very next request,
no restart needed.

---

## 7. Guardrails

`backend/app/guardrails/` - runs before the Router, on every message:

1. **Regex rules** (`regex_rules.py`): a small curated set (prompt-injection
   phrasing, requests for credentials/API keys, raw card-number patterns).
   Cheap, no network call, checked first.
2. **OpenAI moderation** (`moderation.py`): only reached if regex passes, to
   avoid paying for a moderation call on already-blocked input.

Either check failing short-circuits the request with a refusal response
that still carries a fresh `trace_id` and a `guardrails.check` observability
step - the Router and every agent are skipped entirely (verified by
`tests/test_orchestrator.py`).

This is a challenge-scope guardrail stage, not a hardened content-safety
system (see `openspec/changes/getnet-multiagent-platform/design.md` for the
explicit non-goal).

---

## 8. Reliability & observability

Every `/chat` request is traced end-to-end under one `trace_id`:

- **Capture** (`observability/models.py`, `jsonl_logger.py`): each pipeline
  stage - guardrail check, router classification, agent generation, every
  tool/LLM call - becomes a `StepRecord` (timestamp, input, output, model,
  prompt/completion tokens, latency, status), appended to
  `data_store/events.jsonl` as the source-of-truth audit log.
- **Indexing** (`observability/store.py`): the same records are upserted
  into SQLite (`data_store/observability.db`, tables `conversations` and
  `steps`) so the read APIs can do simple, fast SQL aggregation instead of
  scanning JSONL per request.
- **Read APIs** (`api/conversations.py`, `api/metrics.py`):
  - `GET /conversations` - list with filters (`start`, `end`, `agent`, `status`)
  - `GET /conversations/{id}/trace` - full ordered step trace (404 if unknown)
  - `GET /metrics` - aggregate counts, latency, error rate, period-filterable
  - `GET /agents/usage` - invocation counts per agent
  - `GET /tokens/usage` - token counts **and estimated cost** (see `observability/pricing.py`), broken down by model/agent
- **User feedback** (`api/feedback.py`): `POST /feedback` persists a 👍/👎 rating
  tied to a message's `trace_id`/`agent_used` (a new `feedback` table in the
  same SQLite database); `GET /agents/feedback` returns per-agent aggregate
  ratings (% positive, average score), period-filterable, for the Dashboard's
  "Avaliação por agente" chart.

### 8.1 Evaluation / observability strategy

The frontend is the primary way to *judge* orchestration quality, not just
observe it:

- **Chat** page's live agent-flow panel makes the routing decision and tool
  usage visible per message, immediately, in plain language by default (an
  opt-in toggle reveals the technical step/model/token detail) - useful for
  spot-checking whether a given message was classified/handled correctly.
  Per-message 👍/👎 feedback lets a reviewer (or a real user) flag a bad
  answer right where it happened.
- **Dashboard** gives an aggregate, period-filterable read on service health
  (volume by status, usage by agent, token cost, and per-agent feedback
  ratings) - useful for judging whether the system is behaving consistently
  over many requests, not just one.
- **Logs & Observabilidade**, embedded as a collapsible section at the
  bottom of the Dashboard, is the deep-dive tool: every conversation's full
  step trace, multi-filter search (agent/status/date), and a clickable
  errors area that jumps straight to the failing step - this is where a
  reviewer would go to understand *why* a specific answer was wrong.
- **Testes**, embedded as a tab inside Configurações, runs the real backend
  pytest suite (including the 10 challenge example cases against live APIs)
  from inside the product, so correctness can be checked without leaving
  the browser or touching a terminal.

Together these cover the three things worth judging: *did this one message
get handled right* (Chat), *is the system healthy in aggregate* (Dashboard),
and *can I prove the whole suite still passes* (Testes tab) - with the
embedded Logs section as the bridge between the aggregate and the
single-message view.

---

## 9. The fourth agent: Escalation

The Escalation Agent (`agents/escalation.py`) is this challenge's
differentiator: when the Router classifies a message as `escalation`
(explicit request for a human), it performs a mocked human-handoff call
(`tools/escalation_tool.py` - a swappable async function, easy to point at a
real handoff/CRM system later) and returns a deterministic confirmation
(ticket id, queue position, estimated wait) with `agent_used="escalation"`.
The handoff call is captured in `tools_used` and as an observability step
exactly like any other tool call.

---

## 10. Environment variables

`backend/.env.example` documents all five required variables (no real
values committed): `OPENAI_API_KEY`, `PINECONE_API_KEY`,
`PINECONE_ENVIRONMENT`, `PINECONE_INDEX_NAME`, `TAVILY_API_KEY`, plus
optional per-agent model overrides. Copy it to `backend/.env` (git-ignored)
and fill in real values before running anything that hits a live API.

`frontend/.env.example` documents `VITE_API_BASE_URL` (defaults to
`http://localhost:8000`).

---

## 11. Out of scope

Per the challenge brief: authentication/multi-tenancy, cloud deployment,
and CI/CD are explicitly out of scope for this project.
