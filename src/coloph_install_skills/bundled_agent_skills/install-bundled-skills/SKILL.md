---
name: install-bundled-skills
description: Bundle agent skills with a Python package, install them in a repository, and check installed copies.
---

This skill is bundled with the `coloph-install-skills` package.

## Build your skills

Put each skill in the `bundled_agent_skills` directory of the Python import package:

```text
src/yak_shaving_example_package/bundled_agent_skills/shaving-yaks-example-skill/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

Do not add empty resource directories because Python wheels do not contain empty directories.

Add `coloph-install-skills` to the package dependencies:

```sh
uv add coloph-install-skills
```

After the frontmatter, identify the package that provides the skill:

```text
This skill is bundled with the `yak-shaving-example-package` package.
```

## Check your skills

Run this command in continuous integration to detect missing, changed, or broken installations:

```sh
uv run coloph-install-skills --check
```

Add `--root PATH` when the repository is not the current directory.

## Include your skills in your package's installation

Tell users to run the installer after they add or update your package:

> To install yak-shaving-example-package and its skills, run the following commands:

```sh
uv add yak-shaving-example-package
uv run coloph-install-skills
```

> When updating yak-shaving-example-package, run the following command to update its skills:

```sh
uv run coloph-install-skills
```

The command copies each complete skill to `.agents/skills/`. It creates a relative link in `.claude/skills/`.
The command updates skills that it installed before. It does not overwrite skills that another tool or user owns.
When several packages provide skills, one command installs or updates all of them.
