# agno-adventures

## Setup

```shell
# adding new app module to monorepo
cd apps
uv init --app  --description "agno adventures" agno-adventures
cd agno-adventures

## add needed deps

# Deps for playground.py
uv add openai duckduckgo-search yfinance sqlalchemy 'fastapi[standard]' agno
# Deps for agentic_rag_with_reranking.py
uv add agno cohere lancedb tantivy sqlalchemy pylance
```

## Development

### Format

```shell
cd apps/agno-adventures
uv run --package agno-adventures ruff format
```

### Run

```shell
export OPENAI_API_KEY=sk-proj-XXXXX
uv run --package agno-adventures playground.py
uv run --package agno-adventures apps/agno-adventures/playground.py
```

```shell
export OPENAI_API_KEY=sk-proj-XXXXX
uv run --package agno-adventures agentic_rag_with_reranking.py
```
