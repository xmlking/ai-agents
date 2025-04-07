# CLI

```shell
cd apps/cli

uv run poe fmt
# or run from root
uv run --package cli poe fmt

# example: add dependency to individual package
uv add --package cli typer

uv run src/sumo/cli/main.py hello sumo
uv run src/sumo/cli/main.py goodbye sumo

# or run from root
uv run --package cli ai_agents_cli
```
