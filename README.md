# AI Agents

This is an example repo of how to use a [uv Workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/) effectively.

## Structure

There are three packages split into libs and apps:

* **libs**: importable packages, never run independently, do not have entry points
* **apps**: have entry points, never imported
* **webui**: UI app as frontend for AI ChatBot

> Note that neither of these definitions are enforced by anything in Python or uv.

## Development

```shell
gh repo clone xmlking/ai-agents
cd ai-agents
# Install dependencies:
uv sync --all-packages
```

### Tasks

```shell
uv run poe fmt
uv run poe lint
uv run poe check
uv run poe test

# or to run them all
uv run poe all
```

#### Format

```shell
uv run poe fmt
uv run poe lint
# or
uvx ruff check   # Lint all files in the current directory.
uvx ruff format  # Format all files in the current directory.
uvx ruff check --fix
```

#### Testing

```shell
uv sync --all-packages
uv run poe test
```

To test a single package:

```shell
cd apps/server
uv sync
uv run poe test
```

#### Pyright

The following needs to be included with every package `pyproject.toml`:

```toml
[tool.pyright]
venvPath = "../.."       # point to the workspace root where the venv is
venv = ".venv"
strict = ["**/*.py"]
pythonVersion = "3.12"
```

Then you can run `uv run poe check` as for tests.
