#!/usr/bin/env python3
"""Vendor the shared design-system files into each skill that uses them.

    python3 scripts/sync_skill_assets.py          # rewrite skills/<name>/{core,scripts,templates}
    python3 scripts/sync_skill_assets.py --check  # exit 1 if any vendored copy has drifted

A skill installed on its own (for example with `npx skills add`) receives only
its own directory, so it cannot reach the repository's core/, scripts/ and
templates/. Each skill therefore carries the subset it needs, in the same
relative layout. The scripts locate their root from their own path, and the
templates inline `core/...` relative to that root, so the vendored tree works
without changes.

The repository-level core/, scripts/ and templates/ stay canonical. Edit those,
then run this script; never edit a vendored copy.

Standard library only.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
VENDORED_DIRS = ("core", "scripts", "templates")

# Root-relative files or directories each skill needs. A directory entry copies
# every file beneath it.
MANIFEST: dict[str, tuple[str, ...]] = {
    "analytical-document-design": (
        "core/a11y.md",
        "core/base.css",
        "core/print.css",
        "core/tokens.md",
        "core/themes",
        "templates/document.html",
        "scripts/export_pdf.mjs",
        "scripts/inline_fonts.py",
        "scripts/build_document.py",
        "scripts/render_chart.mjs",
        "scripts/render_diagram.mjs",
    ),
    "brand-theme-design": (
        "core/a11y.md",
        "core/base.css",
        "core/print.css",
        "core/tokens.md",
        "core/themes",
        "templates/document.html",
        "templates/themes.html",
        "scripts/audit_theme.py",
        "scripts/build_document.py",
        "scripts/export_pdf.mjs",
        "scripts/extract_site_theme.py",
    ),
    "chart-design": (
        "core/base.css",
        "core/tokens.md",
        "scripts/render_chart.mjs",
    ),
    "diagram-design": (
        "core/a11y.md",
        "core/base.css",
        "core/print.css",
        "core/tokens.md",
        "templates/diagram.svg",
        "scripts/render_diagram.mjs",
    ),
    "presentation-design": (
        "core/a11y.md",
        "core/base.css",
        "core/print.css",
        "core/tokens.md",
        "core/themes",
        "templates/deck.html",
        "scripts/build_document.py",
        "scripts/export_pdf.mjs",
        "scripts/inline_fonts.py",
    ),
    "writing-documents": (
        "core/a11y.md",
        "core/base.css",
        "core/document-patterns.css",
        "core/document-patterns.md",
        "core/print.css",
        "core/themes",
        "templates/longform.html",
        "scripts/build_document.py",
        "scripts/export_pdf.mjs",
        "scripts/inline_fonts.py",
        "scripts/render_diagram.mjs",
    ),
}


def expand(root: Path, entries: tuple[str, ...]) -> list[str]:
    """Resolve manifest entries to a sorted list of root-relative file paths."""
    files: set[str] = set()
    for entry in entries:
        source = root / entry
        if source.is_dir():
            files.update(p.relative_to(root).as_posix() for p in source.rglob("*") if p.is_file())
        elif source.is_file():
            files.add(entry)
        else:
            sys.exit(f"manifest entry does not exist: {entry}")
    return sorted(files)


def vendored_files(skill: Path) -> list[str]:
    """Every file currently under a skill's vendored directories."""
    found: list[str] = []
    for name in VENDORED_DIRS:
        base = skill / name
        if base.is_dir():
            found.extend(p.relative_to(skill).as_posix() for p in base.rglob("*") if p.is_file())
    return sorted(found)


def sync(root: Path, skill: Path, files: list[str]) -> None:
    for name in VENDORED_DIRS:
        shutil.rmtree(skill / name, ignore_errors=True)
    for rel in files:
        target = skill / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / rel, target)


def drift(root: Path, skill: Path, files: list[str]) -> list[str]:
    """Differences between a skill's vendored tree and what the manifest implies."""
    problems: list[str] = []
    present = set(vendored_files(skill))
    for rel in files:
        copy = skill / rel
        if rel not in present:
            problems.append(f"missing  {copy.relative_to(root)}")
        elif copy.read_bytes() != (root / rel).read_bytes():
            problems.append(f"stale    {copy.relative_to(root)}")
    for rel in sorted(present - set(files)):
        problems.append(f"unlisted {(skill / rel).relative_to(root)}")
    return problems


def check_all(root: Path) -> list[str]:
    """Drift across every skill, plus a skills/ vs MANIFEST mismatch."""
    on_disk = {p.name for p in (root / "skills").iterdir() if p.is_dir()}
    if on_disk != set(MANIFEST):
        return [
            "skills/ and MANIFEST disagree: "
            f"only on disk {sorted(on_disk - set(MANIFEST))}, "
            f"only in manifest {sorted(set(MANIFEST) - on_disk)}"
        ]
    problems: list[str] = []
    for name, entries in sorted(MANIFEST.items()):
        problems.extend(drift(root, root / "skills" / name, expand(root, entries)))
    return problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="report drift instead of writing")
    args = parser.parse_args()

    if args.check:
        problems = check_all(ROOT)
        if problems:
            print("\n".join(problems), file=sys.stderr)
            sys.exit(
                "vendored skill assets are out of date — "
                "run 'python3 scripts/sync_skill_assets.py' and commit"
            )
        return

    on_disk = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    if on_disk != set(MANIFEST):
        sys.exit(
            "skills/ and MANIFEST disagree: "
            f"only on disk {sorted(on_disk - set(MANIFEST))}, "
            f"only in manifest {sorted(set(MANIFEST) - on_disk)}"
        )
    for name, entries in sorted(MANIFEST.items()):
        files = expand(ROOT, entries)
        sync(ROOT, SKILLS / name, files)
        print(f"{name}: {len(files)} files", file=sys.stderr)


if __name__ == "__main__":
    main()
