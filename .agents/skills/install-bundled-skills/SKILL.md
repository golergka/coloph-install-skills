---
name: install-bundled-skills
description: Bundle agent skills with a Python package, install them in a repository, and check installed copies.
---

This skill is bundled with the `coloph-install-skills` package.

Keep these three roles separate:

- The installer package is `coloph-install-skills`.
- The provider package bundles skills. This example calls it `yak-shaving-example-package`.
- The consuming repository installs the provider package and receives its skills.

## Build your skills

Put each skill in the `bundled_agent_skills` directory of the Python import package:

```text
src/yak_shaving_example_package/bundled_agent_skills/shaving-yaks-example-skill/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

Add `coloph-install-skills` to the package dependencies:

```sh
uv add coloph-install-skills
```

It is recommended to put this line on the top of every `SKILL.md` file:

```text
This skill is bundled with the `yak-shaving-example-package` package.
```

## Recommendations on skill design

Skills are documentation for agents, not humans. The main advantage of skills is that their descriptions are automatically injected into context by agent's harness, so it's easier for them to remember and use them.

Look at your package's README file. This is something that agents read when they install the package, so detailed descriptions and installation instructions belong there. But agents do not remember to read it again when they maintain something related to your package. That's what you should move to skills.

Do not create too many skills. Most packages need one or two.  Give each skill a goal-oriented name and description. Make the situations that require the skill obvious.  Consider the files, systems, tasks, and keywords that occur in those situations. Use them to make automatic discovery reliable.  Keep internal implementation details out of the description. Put necessary details in the skill body or supporting references.

Many agent hosts provide a skill-authoring tool, such as `/create-skill`. Use one when it is available.

## Check your skills

Run this command in continuous integration to detect missing, changed, or broken installations:

```sh
uv run coloph-install-skills --check
```

Add `--root PATH` when the repository is not the current directory.

## Include your skills in your package's installation

In your package install documentation, instruct users to run `coloph-install-skills` command after installing your package:

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
The command updates skills that it installed before. It does not overwrite other files.
When several packages depend on `coloph-install-skills`, the skills of all packages will be installed/updated when this commadn is ran.
