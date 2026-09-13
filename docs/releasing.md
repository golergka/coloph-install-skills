# Releases

The version in `pyproject.toml` is the single version source.
Each release tag identifies the tested commit on the public `main` branch.

Run these commands before a release:

```sh
uv run ruff check .
uv run ruff format --check .
uv run mypy
uv run pytest
uv run python scripts/release.py build --tag v0.1.0
```

Publish each version once. Never replace a release or tag.
