#!/usr/bin/env python3
"""The authoring toolchain's exact versions, read from one place.

    python3 scripts/pins.py            # print every pin and the install hints

`package.json` pins the Node renderers and `requirements-authoring.txt` pins the
Python screenshot tools. Every other mention of a version — the install hints
the scripts print, the skill references, the README, the license table — must
agree with those two files, and `scripts/validate_repository.py` fails when one
does not.

Scripts that are vendored into a skill cannot import this module (a skill
installed on its own has no package.json beside it), so they carry their hint
as a literal string. The validator checks that literal against these pins.

Standard library only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PACKAGE_JSON = "package.json"
REQUIREMENTS = "requirements-authoring.txt"

# What a contributor runs inside the repository. The lockfile and the
# requirements file carry the versions, so these never name one.
REPO_NPM_HINT = "npm ci"
REPO_PYTHON_HINT = (
    "uv venv && uv pip install -r requirements-authoring.txt "
    "&& uv run playwright install chromium"
)

REQUIREMENT_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;#]+)$")


def npm_pins(root: Path = ROOT) -> dict[str, str]:
    """package.json dependencies, which must be exact versions (no ranges)."""
    data = json.loads((root / PACKAGE_JSON).read_text(encoding="utf-8"))
    deps = dict(data.get("dependencies", {}))
    deps.update(data.get("devDependencies", {}))
    loose = sorted(name for name, ver in deps.items() if not re.fullmatch(r"\d+\.\d+\.\d+", ver))
    if loose:
        raise ValueError(f"{PACKAGE_JSON}: not an exact version: {', '.join(loose)}")
    return deps


def python_pins(root: Path = ROOT) -> dict[str, str]:
    """requirements-authoring.txt entries, which must be `name==version`."""
    pins: dict[str, str] = {}
    for number, raw in enumerate((root / REQUIREMENTS).read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = REQUIREMENT_RE.match(line)
        if not m:
            raise ValueError(f"{REQUIREMENTS}:{number}: expected name==version, got {line!r}")
        pins[m.group(1).lower()] = m.group(2)
    return pins


def pins(root: Path = ROOT) -> dict[str, dict[str, str]]:
    """{"npm": {name: version}, "pypi": {name: version}}."""
    return {"npm": npm_pins(root), "pypi": python_pins(root)}


def npm_hint(*packages: str, root: Path = ROOT) -> str:
    """The exact install line for a skill installed outside the repository."""
    versions = npm_pins(root)
    return "npm i " + " ".join(f"{name}@{versions[name]}" for name in packages)


def python_hint(*packages: str, root: Path = ROOT) -> str:
    """The exact install line for a skill installed outside the repository."""
    versions = python_pins(root)
    return "uv pip install " + " ".join(f"{name}=={versions[name]}" for name in packages)


def main() -> None:
    try:
        found = pins()
    except (OSError, ValueError) as exc:
        sys.exit(str(exc))
    for registry, entries in found.items():
        for name, version in sorted(entries.items()):
            print(f"{registry:5} {name}=={version}" if registry == "pypi" else f"{registry:5} {name}@{version}")
    print(f"\nin the repository:  {REPO_NPM_HINT}")
    print(f"                    {REPO_PYTHON_HINT}")
    print(f"standalone (node):  {npm_hint(*sorted(found['npm']))}")
    print(f"standalone (py):    {python_hint(*sorted(found['pypi']))}")


if __name__ == "__main__":
    main()
