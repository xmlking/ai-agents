# agno-adventures

This module consist example AI Agents build with [Agno](https://docs.agno.com/introduction)

## Setup

```shell
# adding new app module to monorepo
cd apps
uv init --app  --description "agno adventures" agno-adventures
cd agno-adventures

## (optional) add needed deps. `uv sync` automatically install them for you

# Deps for playground.py
uv add openai duckduckgo-search yfinance sqlalchemy 'fastapi[standard]' agno
# Deps for agentic_rag_with_reranking.py
uv add agno cohere lancedb tantivy sqlalchemy pylance
# Deps for agent_with_knowledge.py
uv add pypdf
# Azure AI
uv add azure-ai-inference
```

## Development

### Format

```shell
cd apps/agno-adventures
# or run from root
uv run --package agno-adventures ruff format
```

### Run

1. Run the Chat UI

    ```shell
    cd agent-ui
    pnpm i # first time only
    # start UI app
    pnpm dev
    ```

2. Run **playground** example agent

    ```shell
    cd apps/agno-adventures
    export OPENAI_API_KEY=sk-proj-XXXXX
    uv run --package agno-adventures playground.py
    ```

3. Run **agent_with_knowledge** example agent

    ```shell
    cd apps/agno-adventures
    export OPENAI_API_KEY=sk-proj-XXXXX
    uv run --package agno-adventures agent_with_knowledge.py
    ```

4. Run **agentic_rag_with_reranking** example agent

    ```shell
    cd apps/agno-adventures
    export OPENAI_API_KEY=sk-proj-XXXXX
    export CO_API_KEY=XXXXX
    uv run --package agno-adventures agentic_rag_with_reranking.py
    ```

5. Run **playground_teams** example agent

    ```shell
    cd apps/agno-adventures
    export OPENAI_API_KEY=sk-proj-XXXXX
    uv run --package agno-adventures playground_teams.py
    ```
