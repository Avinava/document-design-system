"""Repository invariants.

    python -m unittest discover -s tests -v

Standard library only, so CI needs no install step.
"""

from __future__ import annotations

import contextlib
import io
import re
import html as html_lib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
CORE = ROOT / "core"

# The colour maths lives in scripts/audit_theme.py, which the skill and CI also
# use. Importing it here rather than keeping a second copy is the point — two
# implementations of a contrast formula drift, and the drift is invisible.
sys.path.insert(0, str(ROOT / "scripts"))
from audit_theme import contrast, relative_luminance, strip_comments  # noqa: E402

EXPECTED_SKILLS = {
    "analytical-document-design",
    "chart-design",
    "diagram-design",
    "writing-documents",
    "presentation-design",
    "brand-theme-design",
}

import catalog  # noqa: E402
from catalog import COMPATIBILITY_PROFILES, NON_TYPE_COMMANDS  # noqa: E402

# Independent intent guards. The full slug -> pattern map lives only in the
# type references (scripts/catalog.py derives it); these pin the decisions that
# should never change silently: how many types and patterns there are, which
# patterns exist, and a hand-picked sample of type -> (theme, pattern).
EXPECTED_TYPE_COUNT = 34
EXPECTED_PATTERN_NAMES = (
    "decision", "record", "contract", "procedure", "learning", "system",
    "incident", "suite", "plan", "assurance", "brief",
)
SPOT_CHECK = {
    "design-doc": ("field-notes", "decision"),
    "adr": ("field-notes", "record"),
    "api-contract": ("console-violet", "contract"),
    "runbook": ("console-violet", "procedure"),
    "postmortem": ("console-violet", "incident"),
    "status-report": ("executive-navy", "brief"),
}

# The class each pattern's examples must carry (one per pattern).
CHARACTERISTIC_CLASS = {
    "decision": "decision-rail",
    "record": "decision-statement",
    "contract": "contract-layout",
    "procedure": "procedure-steps",
    "learning": "takeaway",
    "system": "system-map",
    "incident": "impact-strip",
    "suite": "document-map",
    "plan": "milestone-rail",
    "assurance": "assurance-verdict",
    "brief": "brief-status",
}


def skill_dirs() -> list[Path]:
    return sorted(p for p in SKILLS.iterdir() if p.is_dir())


# Tokens that must agree between an example's Markdown and its HTML body.
FACT_TOKEN = re.compile(
    r"(?:\b(?:ADR|RFC|REQ|INC|NWI)-[A-Z0-9-]+\b|"
    r"/v\d+/[a-z0-9_/{}/-]+|\b\d{4}-\d{2}-\d{2}\b|"
    r"\b\d+(?:\.\d+)?(?:%|ms|s|m|h|×)\b)",
    re.I,
)


def parity_problems(markdown: str, source: str) -> tuple[str, str, list[str]]:
    """(Markdown title, HTML title, fact tokens present only in Markdown)."""
    markdown_title = re.search(r"(?m)^# (.+)$", markdown).group(1).strip()
    html_title = re.search(r"<h1>(.*?)</h1>", source, re.S).group(1)
    html_title = html_lib.unescape(re.sub(r"<[^>]+>", "", html_title)).strip()
    visible = html_lib.unescape(re.sub(r"<[^>]+>", " ", source))
    missing = sorted({token for token in FACT_TOKEN.findall(markdown) if token not in visible})
    return markdown_title, html_title, missing


def front_matter(markdown: str) -> dict[str, str]:
    """Flat `key: value` front matter of a composed example."""
    m = re.match(r"---\n(.*?)\n---\n", markdown, re.S)
    if not m:
        return {}
    return {
        key.strip(): value.strip()
        for key, _, value in (line.partition(":") for line in m.group(1).splitlines())
    }


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


class TestWritingTypes(unittest.TestCase):
    def test_type_slugs_match_filenames(self):
        ref_dir = SKILLS / "writing-documents" / "references"
        for path in sorted(ref_dir.glob("type-*.md")):
            if path.name == "type-index.md":
                continue
            with self.subTest(ref=path.name):
                expected = path.name[len("type-") : -len(".md")]
                text = path.read_text(encoding="utf-8")
                self.assertIn(f"slug: {expected}", text)
                self.assertIn("Reader's question", text)
                self.assertIn(f"/document-design-system:{expected}", text)

    def test_type_index_lists_every_shipped_type(self):
        ref_dir = SKILLS / "writing-documents" / "references"
        index = (ref_dir / "type-index.md").read_text(encoding="utf-8")
        for path in sorted(ref_dir.glob("type-*.md")):
            if path.name == "type-index.md":
                continue
            slug = path.name[len("type-") : -len(".md")]
            with self.subTest(slug=slug):
                self.assertIn(f"`{slug}`", index)

    def test_gallery_lists_every_type(self):
        from build_examples import LONGFORM, PATTERN_PROMISES, TYPE_QUESTIONS

        self.assertEqual(set(LONGFORM), set(catalog.TYPES))
        self.assertEqual(set(TYPE_QUESTIONS), set(catalog.TYPES), "gallery copy and catalog disagree")
        self.assertEqual(set(PATTERN_PROMISES), set(catalog.PATTERNS), "gallery copy and catalog disagree")
        index = ROOT / "examples" / "index.html"
        if index.is_file():
            text = index.read_text(encoding="utf-8")
            for slug in LONGFORM:
                with self.subTest(slug=slug):
                    self.assertIn(f'href="{slug}.html"', text)

    def test_gallery_covers_every_skill(self):
        from build_examples import SKILL_GALLERY

        listed = {name for name, *_ in SKILL_GALLERY}
        self.assertEqual(listed, EXPECTED_SKILLS)
        index = ROOT / "examples" / "index.html"
        if index.is_file():
            text = index.read_text(encoding="utf-8")
            for name, href, shot, _ in SKILL_GALLERY:
                with self.subTest(skill=name):
                    self.assertIn(name, text)
                    self.assertIn(href, text)
                    self.assertIn(shot, text)

    def test_example_html_exists_for_every_type(self):
        ref_dir = SKILLS / "writing-documents" / "references"
        for path in sorted(ref_dir.glob("type-*.md")):
            if path.name == "type-index.md":
                continue
            slug = path.name[len("type-") : -len(".md")]
            with self.subTest(slug=slug):
                self.assertTrue(
                    (ROOT / "examples" / f"{slug}.html").is_file(),
                    f"missing examples/{slug}.html",
                )
                self.assertTrue(
                    (ROOT / "templates" / "types" / f"{slug}.html").is_file(),
                    f"missing templates/types/{slug}.html",
                )
                self.assertTrue(
                    (ROOT / "examples" / f"{slug}.md").is_file(),
                    f"missing examples/{slug}.md",
                )
                self.assertTrue(
                    (ROOT / "docs" / "screenshots" / "thumbs" / f"{slug}.png").is_file(),
                    f"missing docs/screenshots/thumbs/{slug}.png",
                )

    def test_command_exists_for_every_type(self):
        ref_dir = SKILLS / "writing-documents" / "references"
        commands = ROOT / "commands"
        for path in sorted(ref_dir.glob("type-*.md")):
            if path.name == "type-index.md":
                continue
            slug = path.name[len("type-") : -len(".md")]
            with self.subTest(slug=slug):
                cmd = commands / f"{slug}.md"
                self.assertTrue(cmd.is_file(), f"missing commands/{slug}.md")
                body = cmd.read_text(encoding="utf-8")
                self.assertTrue(body.startswith("---\n"), f"{slug} missing frontmatter")
                self.assertIn("description:", body)
                self.assertIn(f"Type slug: {slug}", body)
                self.assertIn("Markdown", body)

    def test_proposal_variants_share_a_body(self):
        from build_examples import LONGFORM_VARIANTS

        self.assertIn("proposal-horizon", LONGFORM_VARIANTS)
        self.assertIn("proposal-coral", LONGFORM_VARIANTS)
        for out_slug, (body_slug, theme, _) in LONGFORM_VARIANTS.items():
            if out_slug in COMPATIBILITY_PROFILES:
                continue
            with self.subTest(out=out_slug):
                self.assertEqual(body_slug, "proposal")
                html = (ROOT / "examples" / f"{out_slug}.html").read_text(
                    encoding="utf-8"
                )
                self.assertIn(f'data-theme="{theme}"', html)
                self.assertIn('data-pattern="decision"', html)
                self.assertIn("Two engineers for one quarter", html)

    def test_catalog_size_and_patterns_are_intended(self):
        self.assertEqual(len(catalog.TYPES), EXPECTED_TYPE_COUNT)
        self.assertEqual(tuple(catalog.PATTERNS), EXPECTED_PATTERN_NAMES)
        for slug, (theme, pattern) in SPOT_CHECK.items():
            with self.subTest(slug=slug):
                self.assertEqual(
                    (catalog.TYPES[slug].default_theme, catalog.TYPES[slug].pattern), (theme, pattern)
                )

    def test_catalog_agrees_with_itself(self):
        self.assertEqual(
            catalog.problems(catalog.TYPES, catalog.PATTERNS, catalog.theme_names(ROOT)), []
        )

    def test_pattern_contract_is_complete_and_consistent(self):
        from build_examples import LONGFORM

        self.assertEqual(
            LONGFORM, {slug: (t.default_theme, t.pattern) for slug, t in catalog.TYPES.items()}
        )
        for slug, (theme, pattern) in LONGFORM.items():
            with self.subTest(slug=slug):
                generated = (ROOT / "examples" / f"{slug}.html").read_text(encoding="utf-8")
                self.assertIn(f'data-pattern="{pattern}"', generated)
                self.assertIn(f'data-theme="{theme}"', generated)

    def test_every_pattern_uses_its_characteristic_module(self):
        self.assertEqual(set(CHARACTERISTIC_CLASS), set(catalog.PATTERNS))
        for slug, entry in catalog.TYPES.items():
            with self.subTest(slug=slug, pattern=entry.pattern):
                body = (ROOT / "templates" / "types" / f"{slug}.html").read_text(encoding="utf-8")
                self.assertIn(CHARACTERISTIC_CLASS[entry.pattern], body)

    def test_markdown_and_html_share_titles_and_fact_tokens(self):
        """The paired formats may compose differently, but not contradict facts."""
        for slug in catalog.TYPES:
            with self.subTest(slug=slug):
                markdown = (ROOT / "examples" / f"{slug}.md").read_text(encoding="utf-8")
                source = (ROOT / "templates" / "types" / f"{slug}.html").read_text(encoding="utf-8")
                markdown_title, html_title, missing = parity_problems(markdown, source)
                self.assertEqual(markdown_title, html_title)
                self.assertEqual(missing, [], f"facts present only in Markdown: {missing}")

    def test_pages_site_builds_and_passes_its_checks(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_site.py"), "--check"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("homepage", result.stdout)

    def test_no_orphan_commands(self):
        ref_dir = SKILLS / "writing-documents" / "references"
        types = {
            p.name[len("type-") : -len(".md")]
            for p in ref_dir.glob("type-*.md")
            if p.name != "type-index.md"
        }
        commands = {p.stem for p in (ROOT / "commands").glob("*.md")}
        # Non-type commands (compose) are allowed but not required.
        self.assertEqual(commands - NON_TYPE_COMMANDS, types | COMPATIBILITY_PROFILES)

    def test_compatibility_profile_routes_to_service_docs(self):
        command = (ROOT / "commands" / "mulesoft.md").read_text(encoding="utf-8")
        self.assertIn("type-service-docs.md", command)
        self.assertIn("profile-mulesoft.md", command)
        from build_examples import LONGFORM_VARIANTS
        self.assertEqual(
            LONGFORM_VARIANTS["mulesoft"],
            ("mulesoft", "field-notes", "suite"),
        )


class TestPortability(unittest.TestCase):
    """A skill installed on its own receives only its own directory.

    `npx skills add` copies skills/<name>/ and nothing else, so every core/,
    scripts/ or templates/ file a skill relies on has to be inside it.
    """

    PATH_RE = re.compile(r"(?<![\w/.-])((?:core|scripts|templates)/[A-Za-z0-9_][A-Za-z0-9_./-]*\.[a-z]+)")

    def skill_prose(self, skill: Path) -> list[Path]:
        return [skill / "SKILL.md"] + sorted((skill / "references").glob("*.md"))

    def test_referenced_files_ship_with_the_skill(self):
        # Repo-only tools a skill may mention but must say so about.
        repo_only = {"scripts/validate_repository.py"}
        for skill in skill_dirs():
            for doc in self.skill_prose(skill):
                for ref in sorted(set(self.PATH_RE.findall(doc.read_text(encoding="utf-8")))):
                    if ref in repo_only or "<" in ref:
                        continue
                    with self.subTest(skill=skill.name, doc=doc.name, ref=ref):
                        self.assertTrue(
                            (skill / ref).is_file(),
                            f"{doc.relative_to(ROOT)} refers to {ref}, which is not "
                            f"inside {skill.name}/ — add it to MANIFEST in "
                            "scripts/sync_skill_assets.py",
                        )

    def test_no_plugin_root_variable(self):
        """${CLAUDE_PLUGIN_ROOT} is unset outside a Claude Code plugin install."""
        for skill in skill_dirs():
            for doc in self.skill_prose(skill):
                with self.subTest(doc=str(doc.relative_to(ROOT))):
                    self.assertNotIn("CLAUDE_PLUGIN_ROOT", doc.read_text(encoding="utf-8"))

    def test_script_invocations_explain_the_skill_directory(self):
        for skill in skill_dirs():
            invokes = any(
                re.search(r"(python3|node) \"?(<skill-dir>/)?scripts/", f.read_text(encoding="utf-8"))
                for f in self.skill_prose(skill)
                if f.is_file()
            )
            if not invokes:
                continue
            body = (skill / "SKILL.md").read_text(encoding="utf-8")
            with self.subTest(skill=skill.name):
                self.assertIn(
                    "relative to this skill's directory",
                    body,
                    f"{skill.name} invokes scripts/ but never says what they are relative to",
                )

    def test_vendored_assets_match_the_canonical_files(self):
        from sync_skill_assets import check_all

        self.assertEqual(
            check_all(ROOT),
            [],
            "vendored skill assets drifted — run 'python3 scripts/sync_skill_assets.py'",
        )

    def test_vendored_scripts_run_from_inside_the_skill(self):
        """The point of vendoring: build a document using only one skill's files."""
        import shutil
        import tempfile

        src = SKILLS / "writing-documents"
        with tempfile.TemporaryDirectory() as tmp:
            lone = Path(tmp) / "writing-documents"
            shutil.copytree(src, lone)
            out = Path(tmp) / "doc.html"
            result = subprocess.run(
                [
                    sys.executable,
                    str(lone / "scripts" / "build_document.py"),
                    str(lone / "templates" / "longform.html"),
                    "--theme", "field-notes",
                    "--out", str(out),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("@@INLINE", out.read_text(encoding="utf-8"))


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

    def test_document_pattern_css_has_no_hex(self):
        css = (CORE / "document-patterns.css").read_text(encoding="utf-8")
        found = re.findall(r"#[0-9a-fA-F]{3,8}\b", css)
        self.assertEqual(found, [], f"document-patterns.css contains color literals: {found}")

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
    def plugin_manifest(self) -> dict:
        import json

        return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())

    def marketplace_manifest(self) -> dict:
        import json

        return json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())

    def test_plugin_and_marketplace_agree(self):
        plugin = self.plugin_manifest()
        market = self.marketplace_manifest()
        names = [p["name"] for p in market["plugins"]]
        self.assertIn(
            plugin["name"],
            names,
            "plugin.json name is not listed in marketplace.json",
        )

    def test_marketplace_is_named_for_the_repository(self):
        """The catalog carries the repository's name, not a broader one.

        Marketplace names are global per user, not scoped to the repository
        that published them: adding a marketplace under a name already in use
        silently replaces the one already there, and the plugins installed from
        the displaced catalog are orphaned. Naming the catalog after the
        repository makes the name unique by construction. A broader name — a
        publisher or org — would collide the moment a second repository of
        theirs published a catalog too.

        This is why `document-design-system@document-design-system` repeats
        itself, and why that repetition should not be "tidied up".
        """
        market = self.marketplace_manifest()
        repo = self.plugin_manifest()["repository"].rstrip("/").rsplit("/", 1)[-1]
        self.assertEqual(
            market["name"],
            repo,
            "marketplace name must match the repository that publishes it",
        )

    def test_manifests_declare_the_same_person(self):
        plugin = self.plugin_manifest()
        market = self.marketplace_manifest()
        entry = next(
            p for p in market["plugins"] if p["name"] == plugin["name"]
        )
        self.assertEqual(plugin["author"], market["owner"])
        self.assertEqual(plugin["author"], entry["author"])

    def test_manifests_point_at_live_schemas(self):
        """A $schema URL that 404s gives editors nothing to validate against."""
        for manifest, expected in (
            (
                self.marketplace_manifest(),
                "https://json.schemastore.org/claude-code-marketplace.json",
            ),
            (
                self.plugin_manifest(),
                "https://json.schemastore.org/claude-code-plugin-manifest.json",
            ),
        ):
            self.assertEqual(manifest.get("$schema"), expected)

    def test_plugin_does_not_redeclare_the_default_skills_path(self):
        """`skills/` is scanned by default, so declaring it is redundant.

        It is also not merely redundant: for a marketplace entry whose source
        resolves to the marketplace root, an explicit skills declaration can
        replace the default scan rather than extend it, which turns a cosmetic
        line into a way to lose skills.
        """
        self.assertNotIn("skills", self.plugin_manifest())
        self.assertTrue(
            (ROOT / "skills").is_dir(),
            "skills/ must exist for the default scan to find anything",
        )


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


class TestManifestValidation(unittest.TestCase):
    """The manifest checks must actually reject; a check that never fires is
    indistinguishable from no check at all."""

    def build(self, tmp: Path, plugin_edit=None, market_edit=None) -> list[str]:
        """Lay down a minimal valid repo, apply one mutation, and validate it."""
        import json

        import validate_repository as vr

        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        if plugin_edit:
            plugin_edit(plugin)
        if market_edit:
            market_edit(market)

        (tmp / ".claude-plugin").mkdir(parents=True)
        (tmp / ".claude-plugin" / "plugin.json").write_text(json.dumps(plugin))
        (tmp / ".claude-plugin" / "marketplace.json").write_text(json.dumps(market))
        (tmp / "skills" / "a-skill").mkdir(parents=True)
        (tmp / "skills" / "a-skill" / "SKILL.md").write_text("---\nname: a-skill\n---\n")

        vr.errors.clear()
        vr.warnings.clear()
        try:
            vr.check_manifests(tmp)
            return list(vr.errors)
        finally:
            vr.errors.clear()
            vr.warnings.clear()

    def assert_rejects(self, needle: str, **edits) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            found = self.build(Path(td), **edits)
        self.assertTrue(
            any(needle in e for e in found),
            f"expected an error containing {needle!r}, got {found}",
        )

    def test_unmutated_manifests_pass(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(self.build(Path(td)), [])

    def test_rejects_marketplace_named_for_the_publisher(self):
        """The invariant that cost two reverts to settle."""
        self.assert_rejects(
            "must match the repository name",
            market_edit=lambda m: m.update({"name": "sfdxy"}),
        )

    def test_rejects_entry_missing_discovery_metadata(self):
        for field in ("license", "tags", "category", "description", "repository"):
            with self.subTest(field=field):
                self.assert_rejects(
                    f"missing non-empty {field}",
                    market_edit=lambda m, f=field: m["plugins"][0].pop(f),
                )

    def test_rejects_entry_drifting_from_plugin_manifest(self):
        self.assert_rejects(
            "disagrees with plugin.json",
            market_edit=lambda m: m["plugins"][0].update(
                {"repository": "https://github.com/Avinava/somewhere-else"}
            ),
        )

    def test_rejects_author_owner_mismatch(self):
        self.assert_rejects(
            "author must match the marketplace owner",
            market_edit=lambda m: m["plugins"][0].update({"author": {"name": "Nobody"}}),
        )

    def test_rejects_reintroduced_skills_key(self):
        self.assert_rejects(
            'remove "skills"',
            plugin_edit=lambda p: p.update({"skills": "./skills/"}),
        )

    def test_rejects_unresolvable_source(self):
        self.assert_rejects(
            "source does not resolve",
            market_edit=lambda m: m["plugins"][0].update({"source": "./nowhere/"}),
        )


class TestToolchain(unittest.TestCase):
    """One set of pins, and every hint, doc and license row agreeing with it."""

    def test_pins_are_exact_and_cover_the_renderers(self):
        import pins

        found = pins.pins(ROOT)
        self.assertEqual(
            set(found["npm"]),
            {"beautiful-mermaid", "@observablehq/plot", "jsdom", "playwright"},
        )
        self.assertEqual(set(found["pypi"]), {"playwright", "pillow"})
        for registry, entries in found.items():
            for name, version in entries.items():
                with self.subTest(registry=registry, name=name):
                    self.assertRegex(version, r"^\d+\.\d+\.\d+$")

    def test_lockfile_matches_package_json(self):
        import json

        import pins

        lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        declared = pins.npm_pins(ROOT)
        self.assertEqual(lock["packages"][""]["dependencies"], declared)
        for name, version in declared.items():
            with self.subTest(name=name):
                self.assertEqual(lock["packages"][f"node_modules/{name}"]["version"], version)

    def test_node_floor_is_declared_once_and_enforced(self):
        import json

        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["engines"]["node"], ">=22.22.2")
        self.assertIn("engine-strict=true", (ROOT / ".npmrc").read_text(encoding="utf-8"))
        self.assertEqual((ROOT / ".nvmrc").read_text(encoding="utf-8").strip(), "22")

    def test_vendored_scripts_carry_the_canonical_standalone_hint(self):
        """Vendored scripts cannot import pins.py, so their literal hint is checked here."""
        import pins

        expected = {
            "render_diagram.mjs": pins.npm_hint("beautiful-mermaid"),
            "render_chart.mjs": pins.npm_hint("@observablehq/plot", "jsdom"),
            "export_pdf.mjs": pins.npm_hint("playwright"),
            "extract_site_theme.py": pins.python_hint("playwright"),
        }
        for script, hint in expected.items():
            with self.subTest(script=script):
                text = (ROOT / "scripts" / script).read_text(encoding="utf-8")
                self.assertIn(hint, text)
                self.assertIn("npm ci" if script.endswith(".mjs") else "requirements-authoring.txt", text)

    def test_hints_name_exact_versions(self):
        import pins

        self.assertEqual(pins.npm_hint("jsdom", root=ROOT), f"npm i jsdom@{pins.npm_pins(ROOT)['jsdom']}")
        self.assertEqual(
            pins.python_hint("pillow", root=ROOT),
            f"uv pip install pillow=={pins.python_pins(ROOT)['pillow']}",
        )


class TestToolchainValidation(unittest.TestCase):
    """check_pins and check_dependencies must reject what they claim to."""

    def run_checks(self, mutate=None) -> list[str]:
        import shutil
        import tempfile

        import validate_repository as vr

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for name in ("package.json", "requirements-authoring.txt", "THIRD_PARTY_LICENSES.md", "README.md", "CONTRIBUTING.md"):
                shutil.copy2(ROOT / name, tmp / name)
            (tmp / "scripts").mkdir()
            for script in sorted((ROOT / "scripts").glob("*")):
                if script.suffix in {".py", ".mjs"}:
                    shutil.copy2(script, tmp / "scripts" / script.name)
            for skill in skill_dirs():
                dest = tmp / "skills" / skill.name
                shutil.copytree(skill / "references", dest / "references")
                shutil.copy2(skill / "SKILL.md", dest / "SKILL.md")
            if mutate:
                mutate(tmp)
            vr.errors.clear()
            vr.warnings.clear()
            try:
                vr.check_pins(tmp)
                vr.check_dependencies(tmp)
                return list(vr.errors)
            finally:
                vr.errors.clear()
                vr.warnings.clear()

    def assert_rejects(self, needle: str, mutate) -> None:
        found = self.run_checks(mutate)
        self.assertTrue(any(needle in e for e in found), f"expected {needle!r}, got {found}")

    @staticmethod
    def edit(rel: str, old: str, new: str):
        def mutate(tmp: Path) -> None:
            path = tmp / rel
            text = path.read_text(encoding="utf-8")
            assert old in text, f"{old!r} not in {rel}"
            path.write_text(text.replace(old, new, 1), encoding="utf-8")

        return mutate

    @staticmethod
    def write(rel: str, body: str):
        def mutate(tmp: Path) -> None:
            (tmp / rel).write_text(body, encoding="utf-8")

        return mutate

    def test_unmutated_copy_passes(self):
        self.assertEqual(self.run_checks(), [])

    def test_rejects_a_version_range(self):
        self.assert_rejects(
            "not an exact version",
            self.edit("package.json", '"jsdom": "30.1.2"', '"jsdom": "^30.1.2"'),
        )

    def test_rejects_a_stale_hint(self):
        self.assert_rejects(
            "disagrees with package.json",
            self.edit("scripts/render_chart.mjs", "jsdom@30.1.2", "jsdom@29.0.0"),
        )

    def test_rejects_a_stale_python_hint(self):
        self.assert_rejects(
            "disagrees with requirements-authoring.txt",
            self.edit("scripts/extract_site_theme.py", "playwright==1.63.0", "playwright==1.40.0"),
        )

    def test_rejects_a_pin_for_an_unmanaged_package(self):
        self.assert_rejects(
            "is not pinned in package.json",
            self.edit("CONTRIBUTING.md", "## Tooling", "## Tooling\n\n`npm i left-pad@1.3.0`"),
        )

    def test_rejects_an_unlisted_node_import(self):
        self.assert_rejects(
            "imports left-pad (npm), which has no row",
            self.write("scripts/pad.mjs", "const m = await import('left-pad');\n"),
        )

    def test_rejects_an_unlisted_python_import(self):
        self.assert_rejects(
            "imports requests (pypi), which has no row",
            self.write("scripts/fetch.py", "import json\nimport requests\n"),
        )

    def test_ignores_stdlib_node_builtins_and_local_modules(self):
        self.assertEqual(
            self.run_checks(
                lambda tmp: (
                    (tmp / "scripts" / "ok.mjs").write_text(
                        "import { readFileSync } from 'node:fs';\nimport './local.mjs';\n", encoding="utf-8"
                    ),
                    (tmp / "scripts" / "ok.py").write_text(
                        "import json\nfrom pins import pins\nfrom PIL import Image\n", encoding="utf-8"
                    ),
                )
            ),
            [],
        )

    def test_rejects_a_license_row_nothing_references(self):
        self.assert_rejects(
            "no script or skill references it",
            self.edit(
                "THIRD_PARTY_LICENSES.md",
                "| [`jsdom`]",
                "| [`sketchy-lines`](https://example.invalid) | npm | unpinned | MIT | nothing |\n| [`jsdom`]",
            ),
        )

    def test_rejects_a_license_row_at_the_wrong_version(self):
        self.assert_rejects(
            "is listed at '30.0.0' but pinned at 30.1.2",
            self.edit("THIRD_PARTY_LICENSES.md", "| npm | 30.1.2 |", "| npm | 30.0.0 |"),
        )

    def test_rejects_a_pinned_package_with_no_row(self):
        self.assert_rejects(
            "pinned pypi package pillow has no row",
            self.edit("THIRD_PARTY_LICENSES.md", "| [`pillow`]", "| pillow"),
        )


class TestCatalog(unittest.TestCase):
    """scripts/catalog.py parses strictly and its cross-checks fire."""

    VALID = (
        "# X\n\n```yaml\nslug: x\ntitle: X\naliases: [a, b-c]\nexample: examples/x.html\n"
        "command: /document-design-system:x\npattern: decision\ndefault-theme: field-notes\n"
        "default-format: markdown\npath: docs/x.md\n```\n"
    )

    def parse(self, text: str):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "type-x.md"
            path.write_text(text, encoding="utf-8")
            return catalog.parse_type(path)

    def test_parses_aliases_as_a_list(self):
        parsed = self.parse(self.VALID)
        self.assertEqual(parsed.aliases, ("a", "b-c"))
        self.assertEqual(parsed.default_theme, "field-notes")
        self.assertEqual(self.parse(self.VALID.replace("[a, b-c]", "[]")).aliases, ())
        self.assertEqual(
            catalog.TYPES["design-doc"].aliases, ("rfc", "tdd", "technical-design", "erd")
        )

    def test_rejects_malformed_blocks(self):
        cases = {
            "missing yaml metadata fence": self.VALID.replace("```yaml", "```text"),
            "aliases must be a [list]": self.VALID.replace("[a, b-c]", "a, b-c"),
            "unexpected": self.VALID.replace("path: docs/x.md", "path: docs/x.md\nowner: me"),
            "declares title twice": self.VALID.replace("title: X", "title: X\ntitle: Y"),
            "yaml has no pattern": self.VALID.replace("pattern: decision\n", ""),
            "yaml has no default-theme": self.VALID.replace("default-theme: field-notes", "default-theme:"),
        }
        for needle, text in cases.items():
            with self.subTest(needle=needle):
                with self.assertRaises(catalog.CatalogError) as ctx:
                    self.parse(text)
                self.assertIn(needle, str(ctx.exception))

    def test_patterns_carry_movement_modules_and_types(self):
        decision = catalog.PATTERNS["decision"]
        self.assertIn("ask band", decision.modules)
        self.assertEqual(decision.types[0], "design-doc")
        self.assertTrue(decision.movement)

    def modules_from(self, table_rows: str):
        """load_modules over the real document-patterns.md with its Modules table replaced."""
        import tempfile

        text = (ROOT / catalog.PATTERNS_MD).read_text(encoding="utf-8")
        text = re.sub(r"\n## Modules\n.*?(?=\n## )", "\n", text, flags=re.S)
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / catalog.PATTERNS_MD
            target.parent.mkdir(parents=True)
            target.write_text(
                text + "\n## Modules\n\n| Module | Class | Patterns allowed | Purpose |\n|---|---|---|---|\n"
                + table_rows,
                encoding="utf-8",
            )
            return catalog.load_modules(root)

    def test_modules_table_parses(self):
        modules = self.modules_from(
            "| ask band | `ask-band` | `decision`, `brief` | The decision asked for, first |\n"
            "| key point | `keypoint` | any | One sentence to carry |\n"
        )
        self.assertEqual(list(modules), ["ask-band", "keypoint"])
        self.assertEqual(modules["ask-band"].patterns, ("decision", "brief"))
        self.assertEqual(modules["keypoint"].patterns, EXPECTED_PATTERN_NAMES)

    def test_modules_table_rejects_malformed_rows(self):
        cases = {
            "registered twice": "| a | `x` | any | p |\n| b | `x` | any | p |\n",
            "must be `code` names": "| a | `x` | decision | p |\n",
            "module class must be `code`": "| a | x | any | p |\n",
        }
        for needle, rows in cases.items():
            with self.subTest(needle=needle):
                with self.assertRaises(catalog.CatalogError) as ctx:
                    self.modules_from(rows)
                self.assertIn(needle, str(ctx.exception))

    def test_cross_checks_fire(self):
        import dataclasses

        types = dict(catalog.TYPES)
        patterns = catalog.PATTERNS
        themes = catalog.theme_names(ROOT)

        def problems_after(**changes) -> str:
            mutated = dict(types)
            mutated["adr"] = dataclasses.replace(types["adr"], **changes)
            return "\n".join(message for _, message in catalog.problems(mutated, patterns, themes))

        self.assertIn('pattern "memo" is not one of', problems_after(pattern="memo"))
        self.assertIn("whose type file says contract", problems_after(pattern="contract"))
        self.assertIn("contract row does not list `adr`", problems_after(pattern="contract"))
        self.assertIn('default-theme "neon" is not a theme', problems_after(default_theme="neon"))
        self.assertIn("command must be", problems_after(command="/document-design-system:record"))
        self.assertIn("example must be", problems_after(example="examples/other.html"))


class TestWritingTypeValidation(unittest.TestCase):
    """check_writing_types reads the catalog and reports through the validator."""

    def run_check(self, mutate=None) -> list[str]:
        import shutil
        import tempfile

        import validate_repository as vr

        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            for rel in (catalog.TYPE_DIR, catalog.THEMES_DIR, Path("commands"), Path("templates/types")):
                shutil.copytree(ROOT / rel, tmp / rel)
            shutil.copy2(ROOT / catalog.PATTERNS_MD, tmp / catalog.PATTERNS_MD)
            if mutate:
                mutate(tmp)
            vr.errors.clear()
            try:
                vr.check_writing_types(tmp)
                return list(vr.errors)
            finally:
                vr.errors.clear()

    @staticmethod
    def edit(rel: str, old: str, new: str):
        def mutate(tmp: Path) -> None:
            path = tmp / rel
            path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")

        return mutate

    def test_unmutated_copy_passes(self):
        self.assertEqual(self.run_check(), [])

    def test_compose_command_is_reserved_not_required(self):
        def add_compose(tmp: Path) -> None:
            (tmp / "commands" / "compose.md").write_text("---\ndescription: x\n---\n", encoding="utf-8")

        self.assertEqual(self.run_check(add_compose), [])

    def test_rejects_unknown_pattern_and_theme(self):
        ref = f"{catalog.TYPE_DIR}/type-adr.md"
        found = "\n".join(self.run_check(self.edit(ref, "pattern: record", "pattern: memo")))
        self.assertIn('pattern "memo"', found)
        found = "\n".join(self.run_check(self.edit(ref, "default-theme: field-notes", "default-theme: neon")))
        self.assertIn('default-theme "neon"', found)

    def test_rejects_malformed_aliases(self):
        ref = f"{catalog.TYPE_DIR}/type-adr.md"
        found = self.run_check(self.edit(ref, "aliases: [architecture-decision]", "aliases: architecture-decision"))
        self.assertTrue(any("aliases must be a [list]" in e for e in found), found)

    def test_rejects_an_orphan_command(self):
        def add(tmp: Path) -> None:
            (tmp / "commands" / "memo.md").write_text("---\ndescription: x\n---\n", encoding="utf-8")

        self.assertTrue(any('command "memo"' in e for e in self.run_check(add)))


class TestSkillSizeValidation(unittest.TestCase):
    def check(self, body: str, description: str = "Does a thing. Use when x. Do not use for y.") -> list[str]:
        import tempfile

        import validate_repository as vr

        with tempfile.TemporaryDirectory() as td:
            skill = Path(td) / "skills" / "a-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_bytes(
                f"---\nname: a-skill\ndescription: {description}\n---\n{body}".encode("utf-8")
            )
            vr.errors.clear()
            vr.warnings.clear()
            try:
                vr.check_skill(skill, Path(td))
                return list(vr.errors)
            finally:
                vr.errors.clear()
                vr.warnings.clear()

    def test_under_the_cap_passes(self):
        self.assertEqual(self.check("x\n" * 1000), [])

    def test_over_the_byte_cap_is_an_error(self):
        import validate_repository as vr

        found = self.check("x" * vr.MAX_SKILL_BYTES)
        self.assertTrue(any("byte cap" in e for e in found), found)

    def test_crlf_is_measured_as_lf(self):
        import validate_repository as vr

        # Just under the cap with LF; CRLF would push it over if not normalised.
        lines = (vr.MAX_SKILL_BYTES - 200) // 2
        self.assertEqual(self.check("x\r\n" * lines), [])

    def test_long_description_is_an_error(self):
        found = self.check("body", "Use when x. Do not use for y. " + "z" * 1024)
        self.assertTrue(any("description is" in e for e in found), found)


class TestModuleRegistry(unittest.TestCase):
    """The registry in core/document-patterns.md, the CSS and the bodies agree."""

    NEW_MODULES = {
        "ask-band": {"decision"},
        "learning-goal": {"learning"},
        "scope-strip": {"learning", "decision", "brief", "system"},
        "crosswalk": {"learning", "decision", "contract", "system"},
    }

    def bodies(self) -> dict[str, tuple[str, set[str]]]:
        return {
            name: (pattern, catalog.body_classes(path.read_text(encoding="utf-8")))
            for name, (pattern, path) in catalog.example_bodies(ROOT).items()
        }

    def problems(self, modules=None, css=None, bodies=None) -> list[str]:
        return catalog.module_problems(
            catalog.MODULES if modules is None else modules,
            catalog.PATTERNS,
            catalog.stylesheet_classes(ROOT) if css is None else css,
            self.bodies() if bodies is None else bodies,
        )

    def test_registry_stylesheet_and_bodies_agree(self):
        self.assertEqual(self.problems(), [])

    def test_new_modules_are_registered_styled_and_used(self):
        css = catalog.stylesheet_classes(ROOT)
        bodies = self.bodies()
        for css_class, patterns in self.NEW_MODULES.items():
            with self.subTest(module=css_class):
                self.assertIn(css_class, catalog.MODULES)
                self.assertEqual(set(catalog.MODULES[css_class].patterns), patterns)
                self.assertIn(css_class, css)
                self.assertTrue(any(css_class in used for _, used in bodies.values()), f"{css_class} is unused")
        self.assertNotIn("section-takeaway", css, "the section takeaway is the takeaway class, not a second one")

    def test_decision_and_learning_bodies_use_their_new_modules(self):
        for slug in ("design-doc", "proposal"):
            with self.subTest(slug=slug):
                self.assertIn('class="ask-band"', (ROOT / "templates" / "types" / f"{slug}.html").read_text())
        for slug in ("explanation", "onboarding", "tutorial"):
            with self.subTest(slug=slug):
                self.assertIn('class="learning-goal"', (ROOT / "templates" / "types" / f"{slug}.html").read_text())

    def test_new_modules_are_responsive_and_printable(self):
        css = catalog.CSS_COMMENT.sub("", (ROOT / catalog.PATTERNS_CSS).read_text(encoding="utf-8"))
        narrow = css[css.index("@media (max-width: 620px)") : css.index("@media print")]
        printed = css[css.index("@media print") :]
        for css_class in ("ask-band", "learning-goal", "scope-strip"):
            with self.subTest(module=css_class):
                self.assertIn(f".{css_class}", narrow)
                self.assertIn(f".{css_class}", printed)
        self.assertIn(".crosswalk table { min-width: 0; }", printed)

    def test_crosswalk_never_encodes_fit_in_colour_alone(self):
        for name, (_, path) in catalog.example_bodies(ROOT).items():
            source = path.read_text(encoding="utf-8")
            for fit, label in re.findall(r'data-fit="([a-z]+)">([^<]*)<', source):
                with self.subTest(example=name, fit=fit):
                    self.assertIn(fit, {"holds", "partial", "breaks"})
                    self.assertEqual(label.strip().lower(), fit, "fit must be written as its word")

    def test_checks_fire(self):
        import dataclasses

        modules = dict(catalog.MODULES)
        bodies = self.bodies()
        css = catalog.stylesheet_classes(ROOT)

        narrowed = dict(modules)
        narrowed["cause-chain"] = dataclasses.replace(modules["cause-chain"], patterns=("incident",))
        self.assertTrue(any("explanation (learning) uses `cause-chain`" in p for p in self.problems(modules=narrowed)))

        self.assertTrue(any("`ask-band` is registered but has no rule" in p for p in self.problems(css=css - {"ask-band"})))
        self.assertTrue(any("styles `.mystery`" in p for p in self.problems(css=css | {"mystery"})))

        stripped = {
            name: (pattern, used - {"learning-goal"}) for name, (pattern, used) in bodies.items()
        }
        self.assertTrue(
            any('no learning example uses its characteristic module "learning goal"' in p
                for p in self.problems(bodies=stripped))
        )


class TestComposedExamples(unittest.TestCase):
    """Composed documents declare what they are and stay inside their pattern."""

    def test_at_least_one_composed_example_ships(self):
        self.assertIn("platform-primer", catalog.COMPOSED)

    def test_front_matter_declares_a_valid_composition(self):
        for slug, (theme, pattern) in catalog.COMPOSED.items():
            with self.subTest(slug=slug):
                markdown = (ROOT / "examples" / f"{slug}.md").read_text(encoding="utf-8")
                meta = front_matter(markdown)
                self.assertEqual(meta.get("type"), "custom")
                self.assertEqual(meta.get("pattern"), pattern)
                self.assertIn(pattern, catalog.PATTERNS)
                nearest = catalog.TYPES[meta["nearest-type"]]
                self.assertEqual(nearest.pattern, pattern, "the nearest type must share the pattern")
                self.assertEqual(nearest.default_theme, theme, "a composition takes the nearest type's theme")
                self.assertNotIn(slug, catalog.TYPES, "a composed example must not shadow a type")

    def test_declared_modules_are_allowed_and_match_the_html(self):
        for slug, (_, pattern) in catalog.COMPOSED.items():
            with self.subTest(slug=slug):
                meta = front_matter((ROOT / "examples" / f"{slug}.md").read_text(encoding="utf-8"))
                declared = {m.strip() for m in meta["modules"].strip("[]").split(",")}
                for css_class in declared:
                    self.assertIn(css_class, catalog.MODULES)
                    self.assertIn(pattern, catalog.MODULES[css_class].patterns)
                body = (ROOT / catalog.COMPOSED_DIR / f"{slug}.html").read_text(encoding="utf-8")
                used = catalog.body_classes(body) & set(catalog.MODULES)
                self.assertEqual(declared, used, "front matter modules and the HTML body disagree")

    def test_markdown_and_html_share_title_and_facts(self):
        for slug in catalog.COMPOSED:
            with self.subTest(slug=slug):
                markdown = (ROOT / "examples" / f"{slug}.md").read_text(encoding="utf-8")
                source = (ROOT / catalog.COMPOSED_DIR / f"{slug}.html").read_text(encoding="utf-8")
                markdown_title, html_title, missing = parity_problems(markdown, source)
                self.assertEqual(markdown_title, html_title)
                self.assertEqual(front_matter(markdown)["title"], markdown_title)
                self.assertEqual(missing, [], f"facts present only in Markdown: {missing}")

    def test_built_example_screenshot_and_gallery(self):
        from build_examples import COMPOSED_GALLERY
        from shoot_examples import SHOTS

        self.assertEqual(set(COMPOSED_GALLERY), set(catalog.COMPOSED))
        index = (ROOT / "examples" / "index.html").read_text(encoding="utf-8")
        for slug, (theme, pattern) in catalog.COMPOSED.items():
            with self.subTest(slug=slug):
                built = (ROOT / "examples" / f"{slug}.html").read_text(encoding="utf-8")
                self.assertIn(f'data-pattern="{pattern}"', built)
                self.assertIn(f'data-theme="{theme}"', built)
                self.assertNotIn("@FIG", built)
                self.assertIn(slug, SHOTS)
                self.assertTrue((ROOT / "docs" / "screenshots" / "thumbs" / f"{slug}.png").is_file())
                # The composed card sits in its pattern's section, beside the presets.
                section = re.search(
                    rf'<section class="pattern-section" id="{pattern}".*?</section>', index, re.S
                )
                self.assertIsNotNone(section)
                self.assertIn(f'href="{slug}.html"', section.group(0))

    def test_compose_command_routes_to_composition(self):
        body = (ROOT / "commands" / "compose.md").read_text(encoding="utf-8")
        self.assertTrue(body.startswith("---\ndescription:"))
        self.assertIn("Type slug: custom", body)
        self.assertIn("references/composing.md", body)
        self.assertIn("references/type-index.md", body)
        self.assertIn("Markdown", body)


FIXTURES = ROOT / "tests" / "fixtures"


class TestDiagramChecks(unittest.TestCase):
    """scripts/check_diagrams.py: one bad fixture per rule, each failing alone."""

    def test_good_fixtures_pass(self):
        from check_diagrams import check_paths

        for path in sorted((FIXTURES / "diagrams" / "good").glob("*.svg")):
            with self.subTest(fixture=path.name):
                self.assertEqual([str(f) for f in check_paths([path])], [])

    def test_every_rule_has_a_bad_fixture_that_fails_with_exactly_that_rule(self):
        from check_diagrams import RULES, check_paths

        bad = FIXTURES / "diagrams" / "bad"
        self.assertEqual({p.stem for p in bad.glob("*.svg")}, set(RULES))
        for rule in RULES:
            with self.subTest(rule=rule):
                found = {f.rule for f in check_paths([bad / f"{rule}.svg"])}
                self.assertEqual(found, {rule})

    def test_repository_figures_are_clean(self):
        from check_diagrams import check_paths, default_inputs

        findings = check_paths(default_inputs(ROOT))
        self.assertEqual([str(f) for f in findings], [])

    def test_doctype_is_refused(self):
        from check_diagrams import check_svg

        text = '<!DOCTYPE svg [<!ENTITY x "y">]><svg xmlns="http://www.w3.org/2000/svg"/>'
        self.assertEqual({f.rule for f in check_svg(text, "inline")}, {"parse"})

    def test_inline_svgs_in_html(self):
        """Titled inline figures are checked; labelled marks and CSS text are not."""
        from check_diagrams import check_paths
        import tempfile

        page = """<!doctype html><html><head><style>/* an <svg> in a comment */</style></head><body>
<svg role="img" aria-label="74 percent" viewBox="0 0 300 20"><rect width="222" height="20"/></svg>
<svg role="img" aria-labelledby="pg-title pg-desc" viewBox="0 0 100 40" width="100%">
  <title id="pg-title">Inline</title><desc id="pg-desc">An inline figure.</desc>
  <defs><marker id="arrow"/></defs>
  <text x="80" y="20" font-size="13">far too long a label</text>
</svg></body></html>"""
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "page.html"
            path.write_text(page, encoding="utf-8")
            found = sorted(f.rule for f in check_paths([path]))
        self.assertEqual(found, ["bounds", "shell-id-prefix"])

    def test_vendored_checker_runs_from_inside_the_skill(self):
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            lone = Path(tmp) / "diagram-design"
            shutil.copytree(SKILLS / "diagram-design", lone)
            script = lone / "scripts" / "check_diagrams.py"
            ok = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stdout + ok.stderr)
            bad = subprocess.run(
                [sys.executable, str(script), str(FIXTURES / "diagrams" / "bad" / "grid.svg")],
                capture_output=True,
                text=True,
            )
            self.assertEqual(bad.returncode, 1)
            self.assertIn(": grid: ", bad.stdout)

    def test_every_hand_diagram_is_in_the_gallery(self):
        from build_examples import HAND_DIAGRAMS

        gallery = (ROOT / "templates" / "gallery.html").read_text(encoding="utf-8")
        for slug in HAND_DIAGRAMS:
            with self.subTest(slug=slug):
                self.assertTrue((ROOT / "examples" / f"{slug}.svg").is_file())
                self.assertIn(f"<!-- @FIG {slug} -->", gallery)


class TestDiagramImport(unittest.TestCase):
    """scripts/import_diagram.py: structure in, no coordinates out, hostile input refused."""

    IMPORT = FIXTURES / "import"

    def load(self, name: str, **kw) -> dict:
        from import_diagram import import_file

        return import_file(self.IMPORT / name, **kw)

    def refused(self, path: Path, needle: str) -> None:
        from import_diagram import DiagramImportError, import_file

        with self.assertRaises(DiagramImportError) as ctx:
            import_file(path)
        self.assertIn(needle, str(ctx.exception))

    def test_drawio_plain(self):
        model = self.load("sample.drawio")
        self.assertEqual(model["source"], "drawio")
        self.assertEqual(
            [(n["id"], n["label"], n["group"]) for n in model["nodes"]],
            [
                ("producer", "Producers", None),
                ("gateway", "Gateway POST /events", "ns"),
                ("queue", "Queue ingest", "ns"),
                ("warehouse", "Warehouse", None),
            ],
        )
        self.assertEqual(
            [(e["from"], e["to"], e["label"]) for e in model["edges"]],
            [("producer", "gateway", ""), ("gateway", "queue", "enqueue"),
             ("queue", "warehouse", "consumer group")],
        )
        self.assertEqual(model["groups"], [{"id": "ns", "label": "Namespace ingest", "parent": None}])

    def test_drawio_compressed_matches_plain(self):
        self.assertEqual(self.load("sample-compressed.drawio"), self.load("sample.drawio"))

    def test_model_carries_no_layout(self):
        import json

        for name in ("sample.drawio", "sample.mmd"):
            with self.subTest(name=name):
                text = json.dumps(self.load(name))
                for key in ('"x"', '"y"', '"width"', '"height"', '"style"', "example.invalid"):
                    self.assertNotIn(key, text)

    def test_mermaid_flowchart(self):
        model = self.load("sample.mmd")
        self.assertEqual(model["source"], "mermaid")
        self.assertEqual(
            {n["id"]: (n["label"], n["group"]) for n in model["nodes"]},
            {
                "P": ("Producers", None), "G": ("Gateway", None), "D": ("Dispatcher", None),
                "QA": ("ingest-a", "queues"), "QB": ("ingest-b", "queues"), "W": ("Warehouse", None),
            },
        )
        self.assertEqual(
            [(e["from"], e["to"], e["label"]) for e in model["edges"]],
            [("P", "G", ""), ("G", "D", "hash event id"), ("D", "QA", ""), ("D", "QB", ""),
             ("QA", "W", "consumer group a"), ("QB", "W", "consumer group b")],
        )

    def test_mermaid_ids_with_hyphens_and_tight_links(self):
        from import_diagram import import_mermaid

        model = import_mermaid("graph TD\n  ingest-a-->consumer-a\n  x-.->y;y==>z")
        self.assertEqual(
            [(e["from"], e["to"]) for e in model["edges"]],
            [("ingest-a", "consumer-a"), ("x", "y"), ("y", "z")],
        )

    def test_other_mermaid_types_point_at_the_renderer(self):
        self.refused(self.IMPORT / "sequence.mmd", "render_diagram.mjs")

    def test_entity_expansion_is_refused(self):
        self.refused(self.IMPORT / "hostile" / "entity-expansion.drawio", "DOCTYPE")

    def test_zip_bomb_is_refused(self):
        self.refused(self.IMPORT / "hostile" / "zip-bomb.drawio", "inflates past")

    def test_duplicate_ids_are_refused(self):
        self.refused(self.IMPORT / "hostile" / "duplicate-ids.drawio", "duplicate cell id")

    def test_dangling_edges_are_refused(self):
        self.refused(self.IMPORT / "hostile" / "dangling-edge.drawio", "does not exist")

    def test_deep_nesting_is_refused(self):
        self.refused(self.IMPORT / "hostile" / "deep-nesting.drawio", "nesting deeper")

    def test_huge_element_counts_are_refused(self):
        import tempfile
        from import_diagram import MAX_ELEMENTS

        cells = "".join(f'<mxCell id="c{i}" vertex="1" parent="1"/>' for i in range(MAX_ELEMENTS + 1))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "huge.drawio"
            path.write_text(f'<mxGraphModel><root><mxCell id="0"/>{cells}</root></mxGraphModel>')
            self.refused(path, f"more than {MAX_ELEMENTS} elements")

    def test_oversized_files_are_refused(self):
        import tempfile
        from import_diagram import MAX_BYTES

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "big.mmd"
            path.write_bytes(b"graph LR\n" + b" " * MAX_BYTES)
            self.refused(path, "the limit is")

    def test_cli_exits_nonzero_with_a_reason(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "import_diagram.py"),
             str(self.IMPORT / "hostile" / "zip-bomb.drawio")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("import_diagram:", result.stderr)
        self.assertEqual(result.stdout, "")


@unittest.skipUnless(__import__("shutil").which("node"), "node is not installed")
class TestWaterfall(unittest.TestCase):
    SPEC = ROOT / "examples" / "specs" / "estimate-bridge.json"

    def render(self, spec_text: str) -> subprocess.CompletedProcess:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            spec = Path(td) / "spec.json"
            spec.write_text(spec_text, encoding="utf-8")
            out = Path(td) / "out.svg"
            result = subprocess.run(
                ["node", str(ROOT / "scripts" / "render_chart.mjs"), str(spec), "--out", str(out)],
                capture_output=True,
                text=True,
            )
            result.svg = out.read_text(encoding="utf-8") if out.is_file() else ""  # type: ignore[attr-defined]
            return result

    def test_a_total_that_does_not_add_up_fails(self):
        text = self.SPEC.read_text(encoding="utf-8").replace('"delta": 24', '"delta": 25')
        result = self.render(text)
        self.assertEqual(result.returncode, 1)
        self.assertIn("sum to 24", result.stderr)

    def test_estimate_matches_its_markdown(self):
        import json

        steps = json.loads(self.SPEC.read_text(encoding="utf-8"))["steps"]
        markdown = (ROOT / "examples" / "estimate.md").read_text(encoding="utf-8")
        for step in steps:
            if step["kind"] == "step" and "excluded" not in step:
                with self.subTest(step=step["label"]):
                    self.assertIn(f"| {step['label']} | {step['delta']} |", markdown)
        self.assertIn("**Expected:** 24 engineer-weeks", markdown)

    @unittest.skipUnless((ROOT / "node_modules" / "@observablehq" / "plot").is_dir(), "run npm ci")
    def test_renders_with_focal_totals_and_a_named_exclusion(self):
        from check_diagrams import check_svg

        result = self.render(self.SPEC.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("var(--accent-tint)", result.svg)
        self.assertIn("not approved", result.svg)
        self.assertEqual([str(f) for f in check_svg(result.svg, "waterfall")], [])


@unittest.skipUnless(
    __import__("importlib.util").util.find_spec("playwright"),
    "playwright is not installed (uv pip install -r requirements-authoring.txt)",
)
class TestRenderCheck(unittest.TestCase):
    def test_broken_fixture_trips_every_check(self):
        fixture = FIXTURES / "render"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_render.py"),
             "--root", str(fixture), "--theme", "field-notes", str(fixture / "broken.html")],
            capture_output=True,
            text=True,
        )
        if result.returncode == 2:
            self.skipTest(result.stderr.strip())
        self.assertEqual(result.returncode, 1, result.stderr)
        for check in ("page-scroll", "figure-box", "text-bounds", "table-clip"):
            with self.subTest(check=check):
                self.assertIn(f"] {check}: ", result.stdout)

    def test_site_pages_render_clean_in_light_and_dark(self):
        """The built index, Patterns and Modules pages at 1280, 390 and print, both schemes."""
        import build_site

        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp).resolve()
            with contextlib.redirect_stdout(io.StringIO()):
                build_site.populate(dest)
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "check_render.py"),
                 "--root", str(dest), "--theme", "executive-navy", "--scheme", "light", "--scheme", "dark",
                 *(str(dest / name) for name in build_site.SITE_PAGES)],
                capture_output=True,
                text=True,
            )
        if result.returncode == 2:
            self.skipTest(result.stderr.strip())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


@unittest.skipUnless(
    __import__("importlib.util").util.find_spec("PIL"),
    "Pillow is not installed (uv pip install -r requirements-authoring.txt)",
)
class TestScreenshotNoise(unittest.TestCase):
    """A reshoot keeps the committed image when only rendering noise differs."""

    @staticmethod
    def png(image) -> bytes:
        out = io.BytesIO()
        image.save(out, format="PNG")
        return out.getvalue()

    def setUp(self):
        from PIL import Image

        self.Image = Image
        self.base = Image.new("RGB", (100, 100), (240, 240, 240))

    def changed(self, pixels: int, delta: int) -> bytes:
        image = self.base.copy()
        for i in range(pixels):
            x, y = i % 100, i // 100
            r, g, b = image.getpixel((x, y))
            image.putpixel((x, y), (r - delta, g, b))
        return self.png(image)

    def test_identical_images_are_the_same(self):
        from shoot_examples import same_image

        self.assertTrue(same_image(self.png(self.base), self.png(self.base)))

    def test_small_channel_drift_everywhere_is_noise(self):
        from shoot_examples import same_image

        self.assertTrue(same_image(self.png(self.base), self.changed(10_000, 2)))

    def test_a_few_strong_pixels_are_noise(self):
        from shoot_examples import same_image

        # 9 of 10,000 pixels is under the 0.1% budget.
        self.assertTrue(same_image(self.png(self.base), self.changed(9, 200)))

    def test_a_real_edit_is_a_change(self):
        from shoot_examples import same_image

        # 11 of 10,000 pixels is over it.
        self.assertFalse(same_image(self.png(self.base), self.changed(11, 200)))

    def test_tolerance_is_per_channel(self):
        from shoot_examples import same_image

        self.assertFalse(same_image(self.png(self.base), self.changed(500, 9)))
        self.assertTrue(same_image(self.png(self.base), self.changed(500, 8)))

    def test_a_different_size_is_a_change(self):
        from shoot_examples import same_image

        bigger = self.png(self.Image.new("RGB", (100, 101), (240, 240, 240)))
        self.assertFalse(same_image(self.png(self.base), bigger))


if __name__ == "__main__":
    unittest.main()
