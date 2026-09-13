"""Build and smoke-test versioned artifacts."""

import argparse
import subprocess
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["build", "publish"])
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    if args.tag != f"v{version}":
        raise SystemExit("Release tag does not match pyproject.toml")
    subprocess.run(["uv", "build", "--no-sources"], cwd=ROOT, check=True)
    artifacts = [
        *list((ROOT / "dist").glob(f"coloph_install_skills-{version}-*.whl")),
        *list((ROOT / "dist").glob(f"coloph_install_skills-{version}.tar.gz")),
    ]
    if len(artifacts) != 2:
        raise SystemExit("Expected one wheel and one source distribution")
    if args.command == "build":
        for artifact in artifacts:
            with tempfile.TemporaryDirectory(prefix="coloph-install-skills-smoke-") as directory:
                subprocess.run(
                    [
                        "uv",
                        "run",
                        "--isolated",
                        "--no-project",
                        "--refresh-package",
                        "coloph-install-skills",
                        "--with",
                        str(artifact),
                        "coloph-install-skills",
                    ],
                    cwd=directory,
                    check=True,
                )
                root = Path(directory)
                assert (root / ".agents/skills/install-bundled-skills/SKILL.md").is_file()
                assert (root / ".claude/skills/install-bundled-skills").is_symlink()
    else:
        subprocess.run(["uv", "publish", "--trusted-publishing", "always", *map(str, artifacts)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
