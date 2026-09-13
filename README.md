# coloph-install-skills

Use this package to bundle agent skills with another Python package and install them in a repository.

Python 3.12 or later is required. The license is GPL-3.0-only.

## Install and integrate

Install the package. Then run the installer:

```sh
uv add coloph-install-skills
uv run coloph-install-skills
```

Then use the `$install-bundled-skills` skill in Codex or `/install-bundled-skills` in Claude Code.

## Development

```sh
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```
