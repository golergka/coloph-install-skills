# coloph-install-skills

When writing agent-first packages, you want to bundle it with skills to be installed alongside it. Use this utilty to do this automatically.

Python 3.12 or later is required. The license is GPL-3.0-only.

## Install and integrate

Install the package. Then run the installer:

```sh
uv add coloph-install-skills
uv run coloph-install-skills
```

Then use the `/install-bundled-skills` to integrate it.

## Development

```sh
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
```
