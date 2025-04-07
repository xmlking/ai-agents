# Server

```shell
cd apps/server

uv run poe fmt
uv run poe test
# or run from root
uv run --package server poe test
# uv run --package server pytest .

uv run src/sumo/server/main.py
# or run from root
uv run --package server ai_agents_server
```
