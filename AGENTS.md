# Working on coloph-install-skills

Keep this package small and independent of agent hosts and package managers.
Bundled skills live in `bundled_agent_skills` inside an installed Python package.
Copy complete skill directories. Never copy only `SKILL.md`.
The `.agents` copy is canonical. The `.claude` entry is a relative symbolic link.
Never overwrite a skill that this tool does not own.

Before a release, run Ruff, mypy, pytest, and the artifact smoke test.
Keep the package version only in `pyproject.toml`.
