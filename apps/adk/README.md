# Google ADK

Exploring [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)

## Setup

```shell
# adding new app module to monorepo
cd apps
uv init --app  --description "google ADK adventures" adk
cd adk

## (optional) add needed deps. `uv sync` automatically install them for you.

# Deps for sample1
uv add google-adk litellm
```

## Development

### Format

```shell
cd apps/adk
# or run from root
uv run --package adk ruff format
```

### Run

1. Run the Chat UI

    ```shell
    cd apps/adk
    adk web
    ```

## References

- [Making Sense of Google's A2A Protocol](https://maximilian-schwarzmueller.com/articles/googles-agent-to-agent-a2a-protocol/)
- Agent Development Kit ([ADK](https://github.com/google/adk-python))
