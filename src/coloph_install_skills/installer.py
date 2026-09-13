"""Discover and install complete bundled agent skill directories."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from importlib.metadata import Distribution, distributions
from pathlib import Path

BUNDLE_DIRECTORY = "bundled_agent_skills"
MANIFEST = ".coloph-install-skills.json"


class InstallationError(ValueError):
    """A bundled skill cannot be installed safely."""


@dataclass(frozen=True)
class BundledSkill:
    name: str
    provider: str
    source: Path
    digest: str


def _digest(directory: Path) -> str:
    result = hashlib.sha256()
    for path in sorted(item for item in directory.rglob("*") if item.is_file()):
        result.update(path.relative_to(directory).as_posix().encode())
        result.update(b"\0")
        result.update(path.read_bytes())
        result.update(b"\0")
    return result.hexdigest()


def discover(installed: list[Distribution] | None = None) -> list[BundledSkill]:
    """Find valid skill directories in all installed distributions."""
    found: dict[str, BundledSkill] = {}
    selected = list(installed if installed is not None else distributions())
    roots_by_provider: dict[Path, str] = {}
    for distribution in selected:
        provider = distribution.metadata.get("Name", "unknown")
        for file in distribution.files or ():
            parts = file.parts
            if BUNDLE_DIRECTORY in parts:
                index = parts.index(BUNDLE_DIRECTORY)
                if index + 1 < len(parts):
                    root = Path(str(distribution.locate_file(Path(*parts[: index + 1])))).resolve()
                    roots_by_provider[root] = provider
    if installed is None:
        for entry in sys.path:
            directory = Path(entry)
            if directory.is_dir():
                for candidate in directory.glob(f"*/{BUNDLE_DIRECTORY}"):
                    root = candidate.resolve()
                    roots_by_provider.setdefault(root, root.parent.name.replace("_", "-"))
    for root, provider in roots_by_provider.items():
        if root.is_dir():
            for source in sorted(root.iterdir()):
                if not source.is_dir() or not (source / "SKILL.md").is_file():
                    continue
                skill = BundledSkill(source.name, provider, source, _digest(source))
                previous = found.get(skill.name)
                if previous and previous.digest != skill.digest:
                    raise InstallationError(
                        f"Skill {skill.name!r} is provided by both {previous.provider!r} and {provider!r}"
                    )
                found[skill.name] = skill
    return sorted(found.values(), key=lambda skill: skill.name)


def _manifest(root: Path) -> dict[str, dict[str, str]]:
    path = root / ".agents" / "skills" / MANIFEST
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise InstallationError(f"Invalid installer manifest: {path}")
    return value


def _claude_link(root: Path, name: str) -> tuple[Path, Path]:
    link = root / ".claude" / "skills" / name
    target = Path(os.path.relpath(root / ".agents" / "skills" / name, link.parent))
    return link, target


def install(root: Path, skills: list[BundledSkill] | None = None) -> list[Path]:
    """Install discovered skills into one repository."""
    root = root.resolve()
    selected = discover() if skills is None else skills
    manifest = _manifest(root)
    changed: list[Path] = []
    agents = root / ".agents" / "skills"
    agents.mkdir(parents=True, exist_ok=True)
    for skill in selected:
        destination = agents / skill.name
        owned = manifest.get(skill.name)
        if destination.exists() and not owned and _digest(destination) != skill.digest:
            raise InstallationError(f"Skill directory is not managed by this tool: {destination}")
        if not destination.exists() or _digest(destination) != skill.digest:
            temporary = Path(tempfile.mkdtemp(prefix=f".{skill.name}-", dir=agents))
            staged = temporary / skill.name
            shutil.copytree(skill.source, staged)
            if destination.exists():
                shutil.rmtree(destination)
            staged.replace(destination)
            temporary.rmdir()
            changed.append(destination)
        manifest[skill.name] = {"provider": skill.provider, "digest": skill.digest}

        link, target = _claude_link(root, skill.name)
        link.parent.mkdir(parents=True, exist_ok=True)
        if link.is_symlink() and Path(os.readlink(link)) == target:
            continue
        if link.exists() or link.is_symlink():
            raise InstallationError(f"Claude skill path is not the expected managed link: {link}")
        link.symlink_to(target, target_is_directory=True)
        changed.append(link)
    (agents / MANIFEST).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return changed


def check(root: Path, skills: list[BundledSkill] | None = None) -> None:
    """Check installed copies and Claude links without changing them."""
    root = root.resolve()
    selected = discover() if skills is None else skills
    manifest = _manifest(root)
    for skill in selected:
        destination = root / ".agents" / "skills" / skill.name
        if manifest.get(skill.name, {}).get("digest") != skill.digest or not destination.is_dir():
            raise InstallationError(f"Skill is missing or stale: {skill.name}")
        if _digest(destination) != skill.digest:
            raise InstallationError(f"Installed skill was changed: {skill.name}")
        link, target = _claude_link(root, skill.name)
        if not link.is_symlink() or Path(os.readlink(link)) != target:
            raise InstallationError(f"Claude skill link is missing or invalid: {skill.name}")
