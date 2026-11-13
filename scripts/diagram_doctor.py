#!/usr/bin/env python3
"""Check that the diagram toolchain can run here, and say how to fix what cannot.

    python3 scripts/diagram_doctor.py

Checks, in order: Node meets the floor, the pinned renderer packages are
installed at their pinned versions, Chromium is available for scripts/
export_diagram.mjs, and Python is recent enough for the checker and importer.

Reads the floor and the pins from the scripts that use them (the `Node X or
newer` line and the `npm i name@version` hint in render_diagram.mjs and
export_pdf.mjs), so this file carries no version of its own and works the same
in the repository and in an installed skill. Standard library only. Exit
status 1 when any check fails.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
MIN_PYTHON = (3, 10)
NODE_FLOOR_RE = re.compile(r"Node (\d+\.\d+\.\d+) or newer")
PIN_RE = re.compile(r"npm i ((?:@[\w.-]+/)?[\w.-]+)@(\d+\.\d+\.\d+)")
PIN_SOURCES = ("render_diagram.mjs", "export_pdf.mjs")


def version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(p) for p in re.findall(r"\d+", text)[:3])


def read_scripts() -> tuple[str | None, dict[str, str]]:
    """(node floor, {package: pinned version}) from the scripts' own headers."""
    floor, pins = None, {}
    for name in PIN_SOURCES:
        path = SCRIPTS / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        found = NODE_FLOOR_RE.search(text)
        if found and floor is None:
            floor = found.group(1)
        pins.update({pkg: ver for pkg, ver in PIN_RE.findall(text)})
    return floor, pins


def installed_version(package: str) -> str | None:
    for base in (ROOT, Path.cwd()):
        manifest = base / "node_modules" / package / "package.json"
        if manifest.is_file():
            try:
                return json.loads(manifest.read_text(encoding="utf-8")).get("version")
            except (OSError, ValueError):
                return None
    return None


def chromium_path() -> str | None:
    """Where Playwright expects its Chromium, or None when playwright cannot say."""
    node = shutil.which("node")
    if not node:
        return None
    try:
        out = subprocess.run(
            [node, "--input-type=module", "-e",
             "import('playwright').then((m) => console.log(m.chromium.executablePath()))"],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


class Report:
    def __init__(self) -> None:
        self.failed = 0

    def ok(self, message: str) -> None:
        print(f"ok    {message}")

    def fail(self, message: str, fix: str) -> None:
        self.failed += 1
        print(f"FAIL  {message}\n      fix: {fix}")


def main() -> int:
    report = Report()
    floor, pins = read_scripts()
    in_repo = (ROOT / "package.json").is_file()
    install = "npm ci" if in_repo else "npm i " + " ".join(f"{p}@{v}" for p, v in sorted(pins.items()))

    if sys.version_info >= MIN_PYTHON:
        report.ok(f"python {sys.version_info.major}.{sys.version_info.minor}")
    else:
        report.fail(f"python {sys.version_info.major}.{sys.version_info.minor} is older than {'.'.join(map(str, MIN_PYTHON))}",
                    "install a newer python3")

    node = shutil.which("node")
    if not node:
        report.fail("node is not on PATH", "install Node" + (f" {floor} or newer" if floor else ""))
    else:
        have = subprocess.run([node, "--version"], capture_output=True, text=True).stdout.strip()
        if floor and version_tuple(have) < version_tuple(floor):
            report.fail(f"node {have} is older than {floor}", f"install Node {floor} or newer")
        else:
            report.ok(f"node {have}" + (f" (floor {floor})" if floor else ""))

    if not pins:
        report.fail("no renderer pins found in render_diagram.mjs or export_pdf.mjs", "restore the scripts")
    for package, pinned in sorted(pins.items()):
        have = installed_version(package)
        if have is None:
            report.fail(f"{package} is not installed (pinned {pinned})", install)
        elif have != pinned:
            report.fail(f"{package} {have} is installed; the pin is {pinned}", install)
        else:
            report.ok(f"{package} {have}")

    if installed_version("playwright") is not None:
        path = chromium_path()
        if path and Path(path).exists():
            report.ok("chromium for playwright")
        else:
            report.fail("chromium is not installed for playwright", "npx playwright install chromium")

    if report.failed:
        print(f"\n{report.failed} check(s) failed", file=sys.stderr)
        return 1
    print("\ndiagram toolchain is ready", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
