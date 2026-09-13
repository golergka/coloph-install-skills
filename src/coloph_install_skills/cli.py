"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .installer import InstallationError, check, install


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install agent skills bundled with local Python dependencies")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.check:
            check(args.root)
            print("Bundled agent skills are installed")
        else:
            changed = install(args.root)
            for path in changed:
                print(f"Installed {path.relative_to(args.root.resolve())}")
            if not changed:
                print("Bundled agent skills are already installed")
    except (InstallationError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0
