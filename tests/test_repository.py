"""Repository invariants.

    python -m unittest discover -s tests -v

Standard library only, so CI needs no install step.
"""

from __future__ import annotations

import re
import html as html_lib
import subprocess
import sys
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
                    (ROOT / "docs" / "screenshots" / f"{slug}.png").is_file(),
                    f"missing docs/screenshots/{slug}.png",
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
        fact = re.compile(
            r"(?:\b(?:ADR|RFC|REQ|INC|NWI)-[A-Z0-9-]+\b|"
            r"/v\d+/[a-z0-9_/{}/-]+|\b\d{4}-\d{2}-\d{2}\b|"
            r"\b\d+(?:\.\d+)?(?:%|ms|s|m|h|×)\b)",
            re.I,
        )
        for slug in catalog.TYPES:
            with self.subTest(slug=slug):
                markdown = (ROOT / "examples" / f"{slug}.md").read_text(encoding="utf-8")
                source = (ROOT / "templates" / "types" / f"{slug}.html").read_text(encoding="utf-8")
                markdown_title = re.search(r"(?m)^# (.+)$", markdown).group(1).strip()
                html_title = re.search(r"<h1>(.*?)</h1>", source, re.S).group(1)
                html_title = html_lib.unescape(re.sub(r"<[^>]+>", "", html_title)).strip()
                self.assertEqual(markdown_title, html_title)
                visible = html_lib.unescape(re.sub(r"<[^>]+>", " ", source))
                missing = sorted({token for token in fact.findall(markdown) if token not in visible})
                self.assertEqual(missing, [], f"facts present only in Markdown: {missing}")

    def test_pages_site_is_homepage_plus_types(self):
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
            for name in ("package.json", "requirements-authoring.txt", "THIRD_PARTY_LICENSES.md", "README.md"):
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
            self.edit("README.md", "## Tooling", "## Tooling\n\n`npm i left-pad@1.3.0`"),
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

    def test_modules_registry_is_empty_until_the_table_exists(self):
        text = (ROOT / catalog.PATTERNS_MD).read_text(encoding="utf-8")
        if "\n## Modules" not in text:
            self.assertEqual(catalog.MODULES, {})

    def test_modules_table_parses(self):
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / catalog.PATTERNS_MD
            target.parent.mkdir(parents=True)
            shutil.copy2(ROOT / catalog.PATTERNS_MD, target)
            target.write_text(
                target.read_text(encoding="utf-8")
                + "\n## Modules\n\n| Module | Class | Patterns allowed | Purpose |\n|---|---|---|---|\n"
                "| ask band | `ask-band` | `decision`, `brief` | The decision asked for, first |\n",
                encoding="utf-8",
            )
            modules = catalog.load_modules(root)
        self.assertEqual(list(modules), ["ask-band"])
        self.assertEqual(modules["ask-band"].patterns, ("decision", "brief"))

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


if __name__ == "__main__":
    unittest.main()
