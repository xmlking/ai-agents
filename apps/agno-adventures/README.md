# agno-adventures

## Setup

```shell
cd apps
uv init --app  --description "agno adventures" agno-adventures
cd agno-adventures
uv add openai duckduckgo-search yfinance sqlalchemy 'fastapi[standard]' agno
# uv add openai duckduckgo-search          sqlalchemy agno lancedb psycopg-binary tantivy pypdf pandas
```


## Development

```shell
uv run --package agno-adventures ruff format

cd apps/agno-adventures
exportexport OPENAI_API_KEY=sk-proj-XXXXX
uv run --package agno-adventures playground.py
uv run --package agno-adventures apps/agno-adventures/playground.py
```
