"""Repository invariants.

    python -m unittest discover -s tests -v

Standard library only, so CI needs no install step.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CORE = ROOT / "core"

EXPECTED_SKILLS = {
    "analytical-document-design",
    "chart-design",
    "diagram-design",
    "longform-document-design",
    "presentation-design",
}


def strip_comments(css: str) -> str:
    """base.css discusses tokens in prose; those are not declarations."""
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def relative_luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a: str, b: str) -> float:
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


class TestValidator(unittest.TestCase):
    def test_repository_validates(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_repository.py"), str(ROOT)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"validate_repository.py failed:\n{result.stdout}\n{result.stderr}",
        )


class TestSkills(unittest.TestCase):
    def test_expected_skills_present(self):
        self.assertEqual({p.name for p in skill_dirs()}, EXPECTED_SKILLS)

    def test_every_skill_has_skill_md(self):
        for skill in skill_dirs():
            with self.subTest(skill=skill.name):
                self.assertTrue((skill / "SKILL.md").is_file())

    def test_referenced_files_exist(self):
        """A SKILL.md pointing at a missing reference silently loses its depth."""
        for skill in skill_dirs():
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            for ref in re.findall(r"`(references/[a-z0-9-]+\.md)`", text):
                with self.subTest(skill=skill.name, ref=ref):
                    self.assertTrue(
                        (skill / ref).is_file(), f"{skill.name} references missing {ref}"
                    )

    def test_no_orphan_references(self):
        """Every reference file is reachable from its SKILL.md."""
        for skill in skill_dirs():
            ref_dir = skill / "references"
            if not ref_dir.is_dir():
                continue
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            for ref in sorted(ref_dir.glob("*.md")):
                with self.subTest(skill=skill.name, ref=ref.name):
                    self.assertIn(
                        ref.name,
                        text,
                        f"{skill.name}/references/{ref.name} is never referenced "
                        "from SKILL.md, so it will never be loaded",
                    )


class TestTokenContract(unittest.TestCase):
    def required_tokens(self) -> set[str]:
        tokens: set[str] = set()
        optional = False
        for line in (CORE / "tokens.md").read_text(encoding="utf-8").split("\n"):
            if line.startswith("### "):
                optional = "optional" in line.lower()
            if optional:
                continue
            m = re.match(r"\|\s*`(--[a-z0-9-]+)`\s*\|", line)
            if m:
                tokens.add(m.group(1))
        return tokens

    def test_contract_is_not_empty(self):
        self.assertGreater(len(self.required_tokens()), 15)

    def test_every_theme_defines_every_token(self):
        required = self.required_tokens()
        themes = sorted((CORE / "themes").glob("*.css"))
        self.assertTrue(themes, "no themes found")
        for theme in themes:
            css = strip_comments(theme.read_text(encoding="utf-8"))
            defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", css))
            with self.subTest(theme=theme.name):
                self.assertEqual(
                    required - defined,
                    set(),
                    f"{theme.name} is missing required tokens",
                )

    def test_dark_themes_define_print_overrides(self):
        """A dark theme that skips print overrides prints white on white.

        core/print.css flattens the surfaces to white but leaves the ink ramp
        alone — correct for a light theme, fatal for a dark one. The knowledge
        belongs with the theme that needs it, so the theme file must carry it.
        """
        for theme in sorted((CORE / "themes").glob("*.css")):
            css = theme.read_text(encoding="utf-8")
            m = re.search(r"--paper:\s*(#[0-9a-fA-F]{3,8})", strip_comments(css))
            if not m:
                continue
            with self.subTest(theme=theme.name):
                if relative_luminance(m.group(1)) < 0.5:
                    self.assertIn(
                        "@media print",
                        css,
                        f"{theme.name} is a dark theme and must restore a dark "
                        "ink ramp for print, or it prints invisibly",
                    )

    def test_theme_print_overrides_are_readable_on_paper(self):
        """Whatever a dark theme restores for print must clear AA on white."""
        for theme in sorted((CORE / "themes").glob("*.css")):
            css = strip_comments(theme.read_text(encoding="utf-8"))
            block = re.search(r"@media print\s*\{(.*)\}\s*\}", css, re.S)
            if not block:
                continue
            for token in ("--ink", "--muted"):
                m = re.search(rf"{token}:\s*(#[0-9a-fA-F]{{3,8}})", block.group(1))
                if not m:
                    continue
                with self.subTest(theme=theme.name, token=token):
                    self.assertGreaterEqual(
                        contrast(m.group(1), "#ffffff"),
                        4.5,
                        f"{theme.name} print {token} is unreadable on white paper",
                    )

    def test_base_css_has_no_hex(self):
        """base.css maps components to tokens; a hex there is a theme leak."""
        css = (CORE / "base.css").read_text(encoding="utf-8")
        found = [h for h in re.findall(r"#[0-9a-fA-F]{3,8}\b", css)]
        self.assertEqual(found, [], f"base.css contains color literals: {found}")

    def test_renderer_aliases_exist(self):
        """render_diagram.mjs maps a renderer's namespace onto --dds-* aliases.

        Without them, `--accent: var(--accent)` on the embedded <svg> is a
        self-reference, which is invalid at computed-value time and silently
        drops the diagram's colors.
        """
        css = strip_comments((CORE / "base.css").read_text(encoding="utf-8"))
        script = (ROOT / "scripts" / "render_diagram.mjs").read_text(encoding="utf-8")
        defined = set(re.findall(r"(--dds-[a-z-]+)\s*:", css))
        used = set(re.findall(r"var\((--dds-[a-z-]+)\)", script))
        self.assertEqual(
            used - defined,
            set(),
            "aliases used by render_diagram.mjs but not defined in core/base.css",
        )


class TestPackaging(unittest.TestCase):
    def test_plugin_and_marketplace_agree(self):
        import json

        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        names = [p["name"] for p in market["plugins"]]
        self.assertIn(
            plugin["name"],
            names,
            "plugin.json name is not listed in marketplace.json",
        )

    def test_plugin_skills_path_resolves(self):
        import json

        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        path = (ROOT / plugin["skills"].lstrip("./")).resolve()
        self.assertTrue(path.is_dir(), f"plugin.json skills path does not exist: {path}")


class TestAssets(unittest.TestCase):
    BANNER = ROOT / "assets" / "banner.svg"

    def test_banner_exists_and_parses(self):
        self.assertTrue(self.BANNER.is_file(), "assets/banner.svg is missing")
        import xml.dom.minidom

        xml.dom.minidom.parse(str(self.BANNER))  # raises on malformed XML

    def test_banner_is_accessible_and_scalable(self):
        svg = self.BANNER.read_text(encoding="utf-8")
        self.assertIn("<title", svg)
        self.assertIn("<desc", svg)
        self.assertIn("viewBox", svg)

    def test_banner_is_self_contained(self):
        """A banner renders through <img>, an isolated document.

        var() references resolve to nothing there, and an external font or
        image request fails closed — so it carries literals and handles its own
        light/dark. See skills/diagram-design/SKILL.md.
        """
        svg = self.BANNER.read_text(encoding="utf-8")
        self.assertNotIn("var(--", svg, "banner cannot use tokens; <img> is isolated")
        self.assertIn("prefers-color-scheme", svg, "banner needs a dark-mode branch")

        # Check for constructs that actually fetch, rather than for the string
        # "http" — the xmlns declaration contains a URL and is required.
        for construct in ("@import", "xlink:href", "<image", "src="):
            self.assertNotIn(construct, svg, f"banner must not use {construct}")
        remote = [u for u in re.findall(r"url\(([^)]*)\)", svg) if "http" in u]
        self.assertEqual(remote, [], "banner must not reference remote urls")

    def test_readme_shows_the_banner(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("assets/banner.svg", readme)

    def test_readme_images_all_exist(self):
        """A README <img>/<source> pointing at a missing file renders as a
        broken-image icon on GitHub, which the markdown link checker never
        sees because these are HTML attributes, not markdown links."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        refs = set(re.findall(r'(?:src|srcset)="(docs/screenshots/[^"]+)"', readme))
        refs |= set(re.findall(r"\]\((docs/screenshots/[^)]+)\)", readme))
        self.assertTrue(refs, "README references no screenshots")
        for ref in sorted(refs):
            with self.subTest(image=ref):
                self.assertTrue((ROOT / ref).is_file(), f"README references missing {ref}")

    def test_dark_mode_sources_are_paired(self):
        """Every <picture> dark source needs a light <img> fallback beside it."""
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for block in re.findall(r"<picture>(.*?)</picture>", readme, re.S):
            with self.subTest(block=block[:60]):
                self.assertIn("prefers-color-scheme: dark", block)
                self.assertRegex(block, r"<img[^>]+src=", "no light fallback")


class TestTemplates(unittest.TestCase):
    def test_inline_markers_resolve(self):
        """Every @@INLINE marker points at a file that exists."""
        marker = re.compile(r"/\* *@@INLINE +([^ ]+) +@@ *\*/")
        for tpl in sorted((ROOT / "templates").glob("*.html")):
            text = tpl.read_text(encoding="utf-8")
            targets = marker.findall(text)
            with self.subTest(template=tpl.name):
                self.assertTrue(targets, f"{tpl.name} has no @@INLINE markers")
            for target in targets:
                resolved = ROOT / target.replace("${THEME}", "editorial-coral")
                with self.subTest(template=tpl.name, target=target):
                    self.assertTrue(resolved.is_file(), f"missing: {target}")

    def test_print_css_is_inlined_last(self):
        """Print rules must come after the responsive rules they override."""
        marker = re.compile(r"/\* *@@INLINE +([^ ]+) +@@ *\*/")
        for tpl in sorted((ROOT / "templates").glob("*.html")):
            targets = marker.findall(tpl.read_text(encoding="utf-8"))
            if "core/print.css" in targets:
                with self.subTest(template=tpl.name):
                    self.assertEqual(
                        targets[-1],
                        "core/print.css",
                        f"{tpl.name} must inline core/print.css last, or print "
                        "rendering can match a narrow-viewport media query and "
                        "collapse the layout",
                    )

    def test_every_template_assembles(self):
        """Each template must build under a real theme with nothing unresolved.

        Only document.html was covered before, so a template added later could
        ship broken — it would assemble into an unstyled page rather than fail.
        """
        for tpl in sorted((ROOT / "templates").glob("*.html")):
            with self.subTest(template=tpl.name):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts" / "build_document.py"),
                        str(tpl),
                        "--theme",
                        "field-notes",
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("@@INLINE", result.stdout)

    def test_build_document_produces_clean_output(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_document.py"),
                str(ROOT / "templates" / "document.html"),
                "--theme",
                "executive-navy",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("@@INLINE", result.stdout, "unresolved build marker in output")
        self.assertIn('data-theme="executive-navy"', result.stdout)

    def test_build_document_rejects_unknown_theme(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "build_document.py"),
                str(ROOT / "templates" / "document.html"),
                "--theme",
                "does-not-exist",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
