from __future__ import annotations

import os
from pathlib import Path

import pytest

from coloph_install_skills.installer import BundledSkill, InstallationError, check, install


def skill(tmp_path: Path, name: str = "example") -> BundledSkill:
    source = tmp_path / "source" / name
    (source / "references").mkdir(parents=True)
    (source / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Example skill.\n---\n")
    (source / "references" / "contract.md").write_text("Complete contract.\n")
    return BundledSkill(name, "example-package", source, "ignored")


def with_digest(value: BundledSkill) -> BundledSkill:
    from coloph_install_skills.installer import _digest

    return BundledSkill(value.name, value.provider, value.source, _digest(value.source))


def test_installs_complete_folder_and_relative_claude_link(tmp_path: Path) -> None:
    bundled = with_digest(skill(tmp_path))
    root = tmp_path / "project"

    changed = install(root, [bundled])

    installed = root / ".agents" / "skills" / "example"
    link = root / ".claude" / "skills" / "example"
    assert changed == [installed, link]
    assert (installed / "references" / "contract.md").read_text() == "Complete contract.\n"
    assert link.is_symlink()
    assert not Path(os.readlink(link)).is_absolute()
    assert link.resolve() == installed.resolve()
    check(root, [bundled])
    assert install(root, [bundled]) == []


def test_rejects_unmanaged_conflict(tmp_path: Path) -> None:
    bundled = with_digest(skill(tmp_path))
    destination = tmp_path / "project" / ".agents" / "skills" / "example"
    destination.mkdir(parents=True)
    (destination / "SKILL.md").write_text("User skill\n")

    with pytest.raises(InstallationError, match="not managed"):
        install(tmp_path / "project", [bundled])


def test_updates_managed_skill_and_detects_local_change(tmp_path: Path) -> None:
    bundled = with_digest(skill(tmp_path))
    root = tmp_path / "project"
    install(root, [bundled])
    (bundled.source / "references" / "contract.md").write_text("New contract.\n")
    updated = with_digest(bundled)

    install(root, [updated])
    check(root, [updated])
    (root / ".agents" / "skills" / "example" / "SKILL.md").write_text("Changed\n")
    with pytest.raises(InstallationError, match="changed"):
        check(root, [updated])
