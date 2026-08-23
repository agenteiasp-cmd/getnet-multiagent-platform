## Purpose

Answers in-scope Getnet questions using retrieval-augmented generation over an ingested Getnet knowledge base, and falls back to live web search for questions outside that scope.

## ADDED Requirements

### Requirement: In-scope questions are answered from the Getnet knowledge base
The Knowledge Agent SHALL answer questions about Getnet products, policies, and services by retrieving relevant passages from the ingested corpus and generating a grounded answer.

#### Scenario: Question about Get Clássica vs Get Smart differences
- **WHEN** the user asks what differentiates Get Clássica from Get Smart
- **THEN** the agent retrieves passages from the ingested Getnet corpus and returns an answer describing the difference, with `sources` populated

#### Scenario: Question about antecipação de recebíveis
- **WHEN** the user asks how receivables anticipation works
- **THEN** the agent retrieves passages from the ingested corpus and returns an answer grounded in that content, with `sources` populated

### Requirement: Out-of-scope questions fall back to web search
The Knowledge Agent SHALL use Tavily web search instead of RAG retrieval when the question is unrelated to the ingested Getnet corpus.

#### Scenario: Weather question triggers web search
- **WHEN** the user asks for a weather forecast
- **THEN** the agent performs a Tavily web search rather than RAG retrieval, and the response is generated from the search results with web `sources` populated

### Requirement: Sources are returned for every knowledge answer
The Knowledge Agent SHALL always populate `sources` with the origin of the information used to answer.

#### Scenario: RAG answer includes corpus source citations
- **WHEN** an answer is generated from retrieved passages
- **THEN** `sources` includes the URL(s) of the ingested document(s) the passages came from

#### Scenario: Web-search answer includes search result sources
- **WHEN** an answer is generated from a Tavily web search
- **THEN** `sources` includes the URL(s) of the web results used

### Requirement: Knowledge base covers the required Getnet content
The ingested corpus SHALL contain content sufficient to answer questions about Get Clássica, Get Smart, Payment Link, and antecipação de recebíveis.

#### Scenario: Retrieval returns relevant passages for each required topic
- **WHEN** a query is issued for each of Get Clássica, Get Smart, Payment Link, and antecipação de recebíveis
- **THEN** retrieval returns at least one passage relevant to that topic from the ingested corpus

### Requirement: No relevant knowledge is handled gracefully
The Knowledge Agent SHALL avoid fabricating an answer when neither retrieval nor web search returns useful information.

#### Scenario: No matching passages and no useful web results
- **WHEN** a query returns no relevant passages from the corpus and no useful web search results
- **THEN** the agent returns a response stating it cannot answer the question, instead of inventing an answer

### Requirement: Web search can be disabled per configuration
The Knowledge Agent SHALL skip the Tavily web-search fallback entirely when `"web_search"` is in its configured `disabled_features`, while RAG retrieval stays unaffected.

#### Scenario: Web search disabled, RAG finds nothing relevant
- **WHEN** `"web_search"` is in the Knowledge Agent's `disabled_features` and RAG retrieval finds no sufficiently relevant passage
- **THEN** the agent does not call Tavily and instead returns the same graceful no-answer response used when web search itself finds nothing useful

#### Scenario: Web search disabled does not affect RAG
- **WHEN** `"web_search"` is in the Knowledge Agent's `disabled_features` and RAG retrieval does find a sufficiently relevant passage
- **THEN** the agent answers from that passage exactly as it would with web search enabled
