#!/usr/bin/env python3
"""Rebuild everything in examples/ from templates, specs, and core/.

    python scripts/build_examples.py

Renders the charts and diagrams, assembles the report, the deck, the thirty-four
canonical writing-document types, the figure gallery, and the theme panels, and inlines
each figure into its slot. Committed outputs double as CI fixtures and as the
screenshots in the README, so they need to be reproducible rather than
hand-maintained.

Node renderers are optional: if their dependencies are missing, the existing
committed SVGs are reused and the step is reported as skipped. That keeps the
document build working on a machine with only Python.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
TYPES = ROOT / "templates" / "types"

sys.path.insert(0, str(ROOT / "scripts"))
import catalog  # noqa: E402
from build_document import build  # noqa: E402
import site_parts  # noqa: E402
from pins import REPO_NPM_HINT  # noqa: E402

# figure slug -> (renderer, spec, extra args)
CHARTS = {
    "footprint-by-function": "specs/footprint.json",
    "cohorts-by-year": "specs/cohorts.json",
    "latency-p99": "specs/latency.json",
    # Full-width variant for the deck. A doc-inline chart dropped into a
    # 1280px slide sits in the middle with its labels shrunk to nothing.
    "footprint-by-function-wide": "specs/footprint-wide.json",
    "estimate-bridge": "specs/estimate-bridge.json",
}

DIAGRAMS = {
    "ingestion-path": (
        "specs/ingestion.mmd",
        "Ingestion path",
        "Client posts events to the gateway, which enqueues them; the queue acknowledges.",
    ),
}

# Hand-authored figures: committed SVGs, checked by scripts/check_diagrams.py
# rather than rendered. Each one is also shown on the figure gallery.
HAND_DIAGRAMS = [
    "platform-architecture",
    "queue-split-change",
    "ingest-deployment",
    "workstream-dependencies",
]

# output -> (template, theme)
DOCUMENTS = {
    "inventory-report.html": ("document.html", "editorial-coral"),
    "capacity-deck.html": ("deck.html", "executive-navy"),
    # The two images the README swaps with the reader's GitHub theme are built
    # twice, once under a light root theme and once under the dark one. Only
    # these two carry the design argument; the rest render once.
    "gallery-light.html": ("gallery.html", "editorial-coral"),
    "gallery-dark.html": ("gallery.html", "console-violet"),
    "themes-light.html": ("themes.html", "editorial-coral"),
    "themes-dark.html": ("themes.html", "console-violet"),
}

# writing-documents examples: slug -> (theme, document-pattern), derived from
# each type reference's yaml block. Bodies live in templates/types/<slug>.html;
# the shell is templates/longform.html.
LONGFORM = {slug: (t.default_theme, t.pattern) for slug, t in catalog.TYPES.items()}

# Same body and pattern, different theme — the two-axis contract proof.
# out_slug -> (body slug, theme, pattern)
LONGFORM_VARIANTS = {
    "proposal-horizon": ("proposal", "horizon", "decision"),
    "proposal-coral": ("proposal", "editorial-coral", "decision"),
    # Backward-compatible specialized profile of the canonical service suite.
    "mulesoft": ("mulesoft", "field-notes", "suite"),
}

FONTS = {
    "field-notes": (
        "https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;500;600;700"
        "&family=Source+Code+Pro:wght@400;500;600&display=swap"
    ),
    "editorial-coral": (
        "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700"
        "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap"
    ),
    "executive-navy": (
        "https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700"
        "&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
    ),
    "console-violet": (
        "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700"
        "&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
    ),
    "horizon": (
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700"
        "&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
    ),
}

# Display copy for the document-type gallery. Which types exist, their
# pattern, and the order of both come from the catalog; these only say how a
# card reads. Pattern sections appear in families-table order.
PATTERN_PROMISES = {
    "decision": "Put the ask and trade-offs before the implementation detail.",
    "record": "Preserve one settled choice and make its consequences traceable.",
    "contract": "Make exact rules, specimens, and compliance conditions easy to scan.",
    "procedure": "Keep safe execution, verification, and recovery in one visible path.",
    "learning": "Build understanding through staged context, practice, and checkpoints.",
    "system": "Use maps, boundaries, interfaces, and states to build a spatial model.",
    "incident": "Lead with impact, reconstruct time, then connect cause to owned action.",
    "suite": "Orient readers across a linked set with ownership and freshness visible.",
    "plan": "Make workstreams, dependencies, gates, and forecast movement visible.",
    "assurance": "Put the verdict beside the evidence, findings, and residual risk.",
    "brief": "Expose current state, material change, required action, and next update.",
}

TYPE_QUESTIONS = {
    "design-doc": "Should we do this, and is the approach sound?",
    "discovery": "What did we learn, and should we proceed?",
    "proposal": "Should I approve this?",
    "project-charter": "What are we committing to, and who can decide?",
    "estimate": "What will this take, and how confident are we?",
    "change-request": "Should we change the agreed baseline?",
    "adr": "Why is it like this?",
    "spec": "What exactly must I build, and how do I know I am done?",
    "api-contract": "How do I call this correctly, and what happens when I do it wrong?",
    "reference": "What is the exact fact?",
    "requirements": "What outcome and behavior must delivery satisfy?",
    "statement-of-work": "What services and acceptance are agreed?",
    "support-model": "Who supports this service, and under what rules?",
    "handoff": "What do I run, change, and not break after you leave?",
    "how-to": "How do I get this job done?",
    "runbook": "What do I do right now?",
    "explanation": "Why is it like this?",
    "onboarding": "How do I get it running and prove it works?",
    "tutorial": "Can I learn this by doing it once?",
    "architecture": "How is it arranged today?",
    "design-handoff": "What do I build, in every state?",
    "postmortem": "What happened, why, and what stops it recurring?",
    "service-docs": "What does this service do, and where is each fact owned?",
    "delivery-plan": "How will the agreed outcome be delivered and governed?",
    "migration-plan": "How do we move safely and back out?",
    "test-strategy": "How will quality risks be tested?",
    "test-report": "Can we ship, on this build?",
    "threat-model": "What can go wrong, and what will we do?",
    "readiness-review": "Is this change ready for production?",
    "risk-register": "Where is delivery exposed, and who owns it?",
    "status-report": "Where are we now, and what needs attention?",
    "release-notes": "What changed, and what must readers do?",
    "workshop-summary": "What did the workshop establish and leave open?",
    "incident-update": "What is happening now, and when is the next update?",
}

# Display copy for composed examples (catalog.COMPOSED): a card title (a
# composed document has no type to borrow one from), the reader's question,
# and the nearest type the composition borrowed its section discipline from.
COMPOSED_GALLERY = {
    "platform-primer": ("Platform primer", "Can I reuse what I know from batch loads here?", "explanation"),
}

SHOT_PREFIX = "../docs/screenshots/thumbs"

PROFILE_GALLERY = [
    (
        "mulesoft",
        "mulesoft.html",
        "mulesoft.png",
        "The service documentation suite, specialised for one integration platform",
    ),
]

# Cards at the top of the type gallery — one per skill in the README table.
# diagram-design and chart-design share the figure gallery on purpose: that
# page is the proof they resolve against the same tokens.
SKILL_GALLERY = [
    (
        "analytical-document-design",
        "inventory-report.html",
        "analytical-report.png",
        "Evidence-led reports from structured data",
    ),
    (
        "diagram-design",
        "gallery-light.html",
        "gallery-light.png",
        "Editorial SVG — architecture, sequence, maps",
    ),
    (
        "chart-design",
        "gallery-light.html",
        "gallery-light.png",
        "Honest charts as inline SVG",
    ),
    (
        "presentation-design",
        "capacity-deck.html",
        "deck-title.png",
        "16:9 decks, one idea per slide",
    ),
    (
        "writing-documents",
        "#types",
        "design-doc.png",
        "Thirty-four types, Markdown by default",
    ),
    (
        "brand-theme-design",
        "themes-light.html",
        "themes-light.png",
        "A brand in, a theme out",
    ),
]

# Figures inlined into the analytical report, in document order.
REPORT_SLOTS = [
    ("<!-- inline the SVG from scripts/render_chart.mjs here -->", "footprint-by-function"),
    ('<div class="chart-frame"></div>', "cohorts-by-year"),
]


def run(cmd: list[str]) -> bool:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        print(f"  skipped: {result.stderr.strip().splitlines()[0] if result.stderr else 'failed'}")
        return False
    return True


def render_figures() -> None:
    print("rendering figures")
    ok = True
    for slug, spec in CHARTS.items():
        ok &= run(["node", "scripts/render_chart.mjs", str(EX / spec), "--out", str(EX / f"{slug}.svg")])
    for slug, (spec, title, desc) in DIAGRAMS.items():
        ok &= run([
            "node", "scripts/render_diagram.mjs", str(EX / spec),
            "--id", slug.split("-")[0], "--title", title, "--desc", desc,
            "--out", str(EX / f"{slug}.svg"),
        ])
    if not ok:
        print(f"  (reusing committed SVGs — run `{REPO_NPM_HINT}` to re-render)")


def figure(slug: str) -> str:
    path = EX / f"{slug}.svg"
    if not path.is_file():
        sys.exit(f"missing figure: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8").strip()


def _title(body: str) -> str:
    m = re.search(r"<h1>(.*?)</h1>", body, re.S)
    if not m:
        return "Document"
    return re.sub(r"<[^>]+>", "", m.group(1)).strip()


def _assemble_one_longform(
    out_slug: str, body_slug: str, theme: str, pattern: str, shell: str, body_dir: Path = TYPES
) -> None:
    body_path = body_dir / f"{body_slug}.html"
    if not body_path.is_file():
        sys.exit(f"missing body: {body_path.relative_to(ROOT)}")
    body = body_path.read_text(encoding="utf-8")

    def inline_body_figure(match: re.Match[str]) -> str:
        return figure(match.group(1))

    body = re.sub(r"<!-- @FIG ([a-z0-9-]+) -->", inline_body_figure, body)
    href = FONTS[theme]
    html = shell.replace("<!-- @@TITLE -->", _title(body), 1)
    html = html.replace(
        "<!-- @@FONTS -->",
        f'<link href="{href}" rel="stylesheet">',
        1,
    )
    html = html.replace("<!-- @@BODY -->", body, 1)
    html = re.sub(
        r'(<html[^>]*\sdata-pattern=")[^"]*(")',
        rf"\g<1>{pattern}\g<2>",
        html,
        count=1,
    )
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)
    try:
        assembled = build(tmp_path, theme)
    finally:
        tmp_path.unlink(missing_ok=True)
    if "@@INLINE" in assembled or "@@BODY" in assembled or "@@TITLE" in assembled:
        sys.exit(f"unresolved marker in {out_slug}")
    (EX / f"{out_slug}.html").write_text(assembled, encoding="utf-8")
    print(f"  {out_slug}.html ({pattern}, {theme}, {len(assembled):,} bytes)")


def assemble_longform() -> None:
    print("assembling writing-documents examples")
    shell = (ROOT / "templates" / "longform.html").read_text(encoding="utf-8")
    stale = EX / "platform-rfc.html"
    if stale.is_file():
        stale.unlink()

    for slug, (theme, pattern) in LONGFORM.items():
        _assemble_one_longform(slug, slug, theme, pattern, shell)
    for out_slug, (body_slug, theme, pattern) in LONGFORM_VARIANTS.items():
        _assemble_one_longform(out_slug, body_slug, theme, pattern, shell)
    # Composed documents use the same shell; the pattern comes from the
    # composition, not from a type preset.
    for slug, (theme, pattern) in catalog.COMPOSED.items():
        _assemble_one_longform(slug, slug, theme, pattern, shell, ROOT / catalog.COMPOSED_DIR)

    assemble_brand(SHOT_PREFIX, EX / "brand.html")
    assemble_docs_gallery(SHOT_PREFIX)


def assemble_brand(shot_prefix: str, dest: Path) -> None:
    raw = (ROOT / "templates" / "brand.html").read_text(encoding="utf-8")
    filled = raw.replace("@@SHOT", shot_prefix)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(filled)
        tmp_path = Path(tmp.name)
    try:
        assembled = build(tmp_path, "editorial-coral")
    finally:
        tmp_path.unlink(missing_ok=True)
    if "@@INLINE" in assembled or "@@SHOT" in assembled:
        sys.exit("unresolved marker in brand.html")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(assembled, encoding="utf-8")
    try:
        shown = dest.relative_to(ROOT)
    except ValueError:
        shown = dest
    print(f"  {shown} ({len(assembled):,} bytes)")


def _fill(raw: str, marks: dict[str, str]) -> str:
    for marker, value in marks.items():
        if marker not in raw:
            sys.exit(f"template has no {marker} marker")
        raw = raw.replace(marker, value)
    return raw


def assemble_docs_gallery(
    shot_prefix: str,
    dest: Path | None = None,
    *,
    site: bool = False,
) -> None:
    """Fill templates/docs-gallery.html — the Patterns page.

    Local (default) writes examples/index.html, with the six-skill strip and
    navigation limited to what exists in examples/. With `site=True` it writes
    Pages' types.html: full site navigation, meta tags, and module chips that
    link to modules.html.
    """
    esc = site_parts.esc
    modules_by_name = {m.name: m for m in catalog.MODULES.values()}

    def module_chip(name: str) -> str:
        module = modules_by_name[name]
        if site:
            return f'<li><a href="modules.html#{module.css_class}">{esc(module.name)}</a></li>'
        return f"<li><span>{esc(module.name)}</span></li>"

    def preset_card(slug: str, href: str, name: str, question: str, theme: str, label: str = "") -> str:
        cls = "preset composed" if label else "preset"
        tag = f'<span class="label">{esc(label)}</span>' if label else ""
        return (
            f'<a class="{cls}" id="type-{slug}" href="{href}">\n'
            f'  <img src="{shot_prefix}/{slug}.png" alt="" width="640" height="400" loading="lazy" decoding="async">\n'
            f'  <span class="pad"><span class="name">{esc(name)}{tag}</span>'
            f'<span class="question">{esc(question)}</span>'
            f'<span class="theme">Theme: {esc(theme)}</span></span>\n'
            f"</a>"
        )

    groups = []
    for pattern in catalog.PATTERNS.values():
        cards = [
            preset_card(slug, f"{slug}.html", catalog.TYPES[slug].title, TYPE_QUESTIONS[slug], LONGFORM[slug][0])
            for slug in pattern.types
        ]
        for slug, (theme, composed_pattern) in catalog.COMPOSED.items():
            if composed_pattern == pattern.name:
                title, question, nearest = COMPOSED_GALLERY[slug]
                theme_note = f"{theme}. Nearest preset: {catalog.TYPES[nearest].title}"
                cards.append(preset_card(slug, f"{slug}.html", title, question, theme_note, "Composed"))
        chips = "".join(module_chip(name) for name in pattern.modules)
        groups.append(
            f'<section class="pattern-section" id="{pattern.name}" aria-labelledby="{pattern.name}-title">\n'
            f'  <header class="pattern-head">\n'
            f'    <h2 id="{pattern.name}-title">{pattern.name.capitalize()}</h2>\n'
            f'    <p class="movement">{esc(pattern.movement)}.</p>\n'
            f'    <p class="promise">{esc(PATTERN_PROMISES[pattern.name])}</p>\n'
            f'    <h3>Characteristic modules</h3>\n'
            f'    <ul class="module-links">{chips}</ul>\n'
            f"  </header>\n"
            f'  <div class="preset-grid">\n    ' + "\n    ".join(cards) + "\n  </div>\n</section>"
        )

    stages = []
    for stage in catalog.LIFECYCLE:
        owners = "".join(
            f'<li><a href="#type-{slug}">{esc(catalog.TYPES[slug].title)}</a></li>' for slug in stage.owners
        )
        stages.append(
            f'<li><h3>{esc(stage.name)}</h3><p class="need">{esc(stage.need)}.</p><ul>{owners}</ul></li>'
        )
    lifecycle_html = '<ol class="lifecycle">' + "".join(stages) + "</ol>"

    names = []
    for slug, entry in sorted(catalog.TYPES.items(), key=lambda item: item[1].title.lower()):
        if not entry.aliases:
            continue
        aliases = ", ".join(f"<code>{esc(alias)}</code>" for alias in entry.aliases)
        names.append(f'<li><a href="#type-{slug}">{esc(entry.title)}</a><br>{aliases}</li>')
    names_html = '<ul class="names">' + "".join(names) + "</ul>"

    profile_cards = [
        preset_card(name, href, name, blurb, LONGFORM_VARIANTS[name][1], "Profile")
        for name, href, _shot, blurb in PROFILE_GALLERY
    ]
    profiles_html = (
        '<section class="profiles" id="profiles" aria-labelledby="profiles-title">\n'
        '  <h2 id="profiles-title">Compatibility profiles</h2>\n'
        '  <p class="site-lead">An older specialised command stays supported while the canonical preset stays general.</p>\n'
        '  <div class="preset-grid">' + "".join(profile_cards) + "</div>\n</section>"
    )

    skills_html = ""
    if not site:
        skill_cards = []
        for name, href, shot, blurb in SKILL_GALLERY:
            skill_cards.append(
                f'<a class="preset" href="{href}">\n'
                f'  <img src="{shot_prefix}/{shot}" alt="" width="640" height="400" loading="lazy" decoding="async">\n'
                f'  <span class="pad"><span class="name">{esc(name)}</span><span class="question">{esc(blurb)}</span></span>\n'
                f"</a>"
            )
        skills_html = (
            '<section class="skill-strip" id="skills" aria-labelledby="skills-title">\n'
            '  <h2 id="skills-title">The skills</h2>\n'
            '  <div class="preset-grid">' + "".join(skill_cards) + "</div>\n</section>"
        )

    if site:
        nav = site_parts.site_nav("types.html")
        meta = site_parts.head_meta(
            "Document patterns — document-design-system",
            f"Start from the reader's question: {len(catalog.PATTERNS)} reading patterns, "
            f"{len(catalog.TYPES)} presets, and how to compose when none fits.",
            "types.html",
        )
        chooser = site_parts.chooser(lambda p: f"#{p}", lambda s: f"{s}.html",
                                     "Reader's question, pattern, and presets")
    else:
        nav = site_parts.site_nav("index.html", site_parts.LOCAL_NAV)
        meta = ""
        chooser = site_parts.chooser(lambda p: f"#{p}", lambda s: f"{s}.html",
                                     "Reader's question, pattern, and presets")

    raw = (ROOT / "templates" / "docs-gallery.html").read_text(encoding="utf-8")
    filled = _fill(raw, {
        "<!-- @@META -->": meta,
        "/* @@SITE_CSS */": site_parts.SHARED_CSS,
        "/* @@DARK */": site_parts.dark_css(),
        "<!-- @@NAV -->": nav,
        "<!-- @@CHOOSER -->": chooser,
        "<!-- @@CARDS -->": "\n".join(groups),
        "<!-- @@LIFECYCLE -->": lifecycle_html,
        "<!-- @@NAMES -->": names_html,
        "<!-- @@PROFILES -->": profiles_html,
        "<!-- @@SKILLS -->": skills_html,
        "@@TYPES_WORD": site_parts.words(len(catalog.TYPES)),
        "@@PATTERNS_WORD": site_parts.words(len(catalog.PATTERNS)),
        "@@MODULES_HREF": "modules.html" if site else "../core/document-patterns.md#modules",
    })
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(filled)
        tmp_path = Path(tmp.name)
    try:
        assembled = build(tmp_path, site_parts.SITE_THEME)
    finally:
        tmp_path.unlink(missing_ok=True)
    if "@@" in assembled:
        sys.exit("unresolved marker in docs-gallery")
    out = dest or (EX / "index.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(assembled, encoding="utf-8")
    try:
        shown = out.relative_to(ROOT)
    except ValueError:
        shown = out
    print(f"  {shown} ({len(assembled):,} bytes)")


def build_documents() -> None:
    print("assembling documents")
    assemble_longform()
    for out, (template, theme) in DOCUMENTS.items():
        target = EX / out
        if not run([
            sys.executable, "scripts/build_document.py",
            str(ROOT / "templates" / template), "--theme", theme, "--out", str(target),
        ]):
            sys.exit(f"failed to assemble {out}")

        html = target.read_text(encoding="utf-8")

        # gallery.html uses named slots; the report uses positional ones.
        if out.startswith("gallery"):
            gallery_figs = [f for f in CHARTS if not f.endswith("-wide")]
            for slug in gallery_figs + list(DIAGRAMS) + HAND_DIAGRAMS:
                html = html.replace(f"<!-- @FIG {slug} -->", figure(slug))
        elif out == "inventory-report.html":
            for marker, slug in REPORT_SLOTS:
                replacement = figure(slug)
                if marker.startswith("<div"):
                    replacement = f'<div class="chart-frame">{replacement}</div>'
                html = html.replace(marker, replacement, 1)
        elif out == "capacity-deck.html":
            html = html.replace(
                "<!-- inline the full-width SVG from scripts/render_chart.mjs here -->",
                figure("footprint-by-function-wide"), 1,
            )

        target.write_text(html, encoding="utf-8")
        print(f"  {out} ({theme}, {len(html):,} bytes)")


def main() -> None:
    render_figures()
    build_documents()
    print("\ndone. Screenshot with: uv run python scripts/shoot_examples.py")


if __name__ == "__main__":
    main()
