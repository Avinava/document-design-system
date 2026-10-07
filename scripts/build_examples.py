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
from build_document import build  # noqa: E402
from pins import REPO_NPM_HINT  # noqa: E402

# figure slug -> (renderer, spec, extra args)
CHARTS = {
    "footprint-by-function": "specs/footprint.json",
    "cohorts-by-year": "specs/cohorts.json",
    "latency-p99": "specs/latency.json",
    # Full-width variant for the deck. A doc-inline chart dropped into a
    # 1280px slide sits in the middle with its labels shrunk to nothing.
    "footprint-by-function-wide": "specs/footprint-wide.json",
}

DIAGRAMS = {
    "ingestion-path": (
        "specs/ingestion.mmd",
        "Ingestion path",
        "Client posts events to the gateway, which enqueues them; the queue acknowledges.",
    ),
}

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

# writing-documents examples: slug -> (theme, document-pattern)
# Bodies live in templates/types/<slug>.html; the shell is templates/longform.html.
LONGFORM = {
    "design-doc": ("field-notes", "decision"),
    "adr": ("field-notes", "record"),
    "spec": ("field-notes", "contract"),
    "api-contract": ("console-violet", "contract"),
    "architecture": ("field-notes", "system"),
    "handoff": ("field-notes", "procedure"),
    "design-handoff": ("editorial-coral", "system"),
    "discovery": ("field-notes", "decision"),
    "test-report": ("editorial-coral", "assurance"),
    "postmortem": ("console-violet", "incident"),
    "proposal": ("executive-navy", "decision"),
    "runbook": ("console-violet", "procedure"),
    "onboarding": ("field-notes", "learning"),
    "tutorial": ("editorial-coral", "learning"),
    "how-to": ("editorial-coral", "procedure"),
    "reference": ("console-violet", "contract"),
    "explanation": ("field-notes", "learning"),
    "project-charter": ("executive-navy", "decision"),
    "estimate": ("executive-navy", "decision"),
    "change-request": ("executive-navy", "decision"),
    "requirements": ("field-notes", "contract"),
    "statement-of-work": ("executive-navy", "contract"),
    "support-model": ("field-notes", "contract"),
    "delivery-plan": ("executive-navy", "plan"),
    "migration-plan": ("console-violet", "plan"),
    "test-strategy": ("editorial-coral", "plan"),
    "threat-model": ("console-violet", "assurance"),
    "readiness-review": ("console-violet", "assurance"),
    "risk-register": ("executive-navy", "assurance"),
    "status-report": ("executive-navy", "brief"),
    "release-notes": ("editorial-coral", "brief"),
    "workshop-summary": ("field-notes", "brief"),
    "incident-update": ("console-violet", "brief"),
    "service-docs": ("field-notes", "suite"),
}

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

# Cards on the document-type gallery, grouped by reading pattern.
# pattern -> (label, promise, items)
TYPE_GALLERY = [
    (
        "decision",
        "Decision",
        "Put the ask and trade-offs before the implementation detail.",
        [
            ("design-doc", "Should we do this, and is the approach sound?"),
            ("discovery", "What did we learn, and should we proceed?"),
            ("proposal", "Should I approve this?"),
            ("project-charter", "What are we committing to, and who can decide?"),
            ("estimate", "What will this take, and how confident are we?"),
            ("change-request", "Should we change the agreed baseline?"),
        ],
    ),
    (
        "record",
        "Record",
        "Preserve one settled choice and make its consequences traceable.",
        [("adr", "Why is it like this?")],
    ),
    (
        "contract",
        "Contract",
        "Make exact rules, specimens, and compliance conditions easy to scan.",
        [
            ("spec", "What exactly must I build, and how do I know I am done?"),
            ("api-contract", "How do I call this correctly, and what happens when I do it wrong?"),
            ("reference", "What is the exact fact?"),
            ("requirements", "What outcome and behavior must delivery satisfy?"),
            ("statement-of-work", "What services and acceptance are agreed?"),
            ("support-model", "Who supports this service, and under what rules?"),
        ],
    ),
    (
        "procedure",
        "Procedure",
        "Keep safe execution, verification, and recovery in one visible path.",
        [
            ("handoff", "What do I run, change, and not break after you leave?"),
            ("how-to", "How do I get this job done?"),
            ("runbook", "What do I do right now?"),
        ],
    ),
    (
        "learning",
        "Learning",
        "Build understanding through staged context, practice, and checkpoints.",
        [
            ("explanation", "Why is it like this?"),
            ("onboarding", "How do I get it running and prove it works?"),
            ("tutorial", "Can I learn this by doing it once?"),
        ],
    ),
    (
        "system",
        "System",
        "Use maps, boundaries, interfaces, and states to build a spatial model.",
        [
            ("architecture", "How is it arranged today?"),
            ("design-handoff", "What do I build, in every state?"),
        ],
    ),
    (
        "incident",
        "Incident",
        "Lead with impact, reconstruct time, then connect cause to owned action.",
        [("postmortem", "What happened, why, and what stops it recurring?")],
    ),
    (
        "suite",
        "Suite",
        "Orient readers across a linked set with ownership and freshness visible.",
        [("service-docs", "What does this service do, and where is each fact owned?")],
    ),
    (
        "plan",
        "Plan",
        "Make workstreams, dependencies, gates, and forecast movement visible.",
        [
            ("delivery-plan", "How will the agreed outcome be delivered and governed?"),
            ("migration-plan", "How do we move safely and back out?"),
            ("test-strategy", "How will quality risks be tested?"),
        ],
    ),
    (
        "assurance",
        "Assurance",
        "Put the verdict beside the evidence, findings, and residual risk.",
        [
            ("test-report", "Can we ship, on this build?"),
            ("threat-model", "What can go wrong, and what will we do?"),
            ("readiness-review", "Is this change ready for production?"),
            ("risk-register", "Where is delivery exposed, and who owns it?"),
        ],
    ),
    (
        "brief",
        "Brief",
        "Expose current state, material change, required action, and next update.",
        [
            ("status-report", "Where are we now, and what needs attention?"),
            ("release-notes", "What changed, and what must readers do?"),
            ("workshop-summary", "What did the workshop establish and leave open?"),
            ("incident-update", "What is happening now, and when is the next update?"),
        ],
    ),
]

SHOT_PREFIX = "../docs/screenshots/thumbs"

# Theme variants shown on the local type gallery (and Pages types.html).
VOICES_GALLERY = [
    ("proposal", "proposal.html", "proposal.png", "executive-navy — board voice"),
    ("proposal-horizon", "proposal-horizon.html", "proposal-horizon.png", "horizon — client brand"),
    ("proposal-coral", "proposal-coral.html", "proposal-coral.png", "editorial-coral — default"),
    ("brand", "brand.html", "brand.png", "How the Horizon brand was built"),
]

PROFILE_GALLERY = [
    (
        "mulesoft",
        "mulesoft.html",
        "mulesoft.png",
        "Backward-compatible specialized profile of service-docs",
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


def _assemble_one_longform(out_slug: str, body_slug: str, theme: str, pattern: str, shell: str) -> None:
    body_path = TYPES / f"{body_slug}.html"
    if not body_path.is_file():
        sys.exit(f"missing type body: {body_path.relative_to(ROOT)}")
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


def assemble_docs_gallery(
    shot_prefix: str,
    dest: Path | None = None,
    *,
    include_skills: bool = True,
    types_href: str = "#types",
) -> None:
    """Fill templates/docs-gallery.html.

    Local default writes examples/index.html with the six-skill strip.
    Pages writes types.html without that strip — the homepage already
    introduced the skills.
    """
    groups = []
    for pattern, heading, promise, items in TYPE_GALLERY:
        cards = []
        for slug, question in items:
            shot = f"{shot_prefix}/{slug}.png"
            theme = LONGFORM[slug][0]
            cards.append(
                f'<a class="type-card" id="type-{slug}" href="{slug}.html">\n'
                f'  <img src="{shot}" alt="" width="640" height="400" loading="lazy" decoding="async">\n'
                f'  <div class="pad">\n'
                f'    <span class="kind">{slug}</span><span class="theme">{theme}</span>\n'
                f'    <h3>{question}</h3>\n'
                f'  </div>\n'
                f'</a>'
            )
        groups.append(
            f'<section class="pattern-section pattern-{pattern}" id="{pattern}">\n'
            f'  <header><span class="pattern-index">{len(groups) + 1:02d}</span>'
            f'<div><p class="eyebrow">{pattern} pattern</p><h2>{heading}</h2>'
            f'<p>{promise}</p></div></header>\n'
            f'  <div class="type-cards">\n    '
            + "\n    ".join(cards)
            + "\n  </div>\n</section>"
        )
    cards_html = "\n".join(groups)
    voice_cards = []
    for name, href, shot, blurb in VOICES_GALLERY:
        voice_cards.append(
            f'<a class="card" href="{href}">\n'
            f'  <img src="{shot_prefix}/{shot}" alt="" width="640" height="400" loading="lazy" decoding="async">\n'
            f'  <div class="pad">\n'
            f'    <span class="kind">{name}</span>\n'
            f'    <h3>{blurb}</h3>\n'
            f'  </div>\n'
            f'</a>'
        )
    voices_html = (
        '<section class="group">\n'
        '  <h2>Voices</h2>\n'
        '  <p class="lead">The same proposal in three themes, then how the client brand was built.</p>\n'
        '  <div class="cards">\n    '
        + "\n    ".join(voice_cards)
        + "\n  </div>\n</section>"
    )
    profile_cards = []
    for name, href, shot, blurb in PROFILE_GALLERY:
        profile_cards.append(
            f'<a class="card" href="{href}">\n'
            f'  <img src="{shot_prefix}/{shot}" alt="" width="640" height="400" loading="lazy" decoding="async">\n'
            f'  <div class="pad"><span class="kind">{name}</span><h3>{blurb}</h3></div>\n'
            f'</a>'
        )
    profiles_html = (
        '<section class="group" id="profiles">\n'
        '  <h2>Compatibility profiles</h2>\n'
        '  <p class="lead">Existing specialized commands remain supported while the canonical suite stays general.</p>\n'
        '  <div class="cards">\n    '
        + "\n    ".join(profile_cards)
        + "\n  </div>\n</section>"
    )
    skill_cards = []
    for name, href, shot, blurb in SKILL_GALLERY:
        skill_cards.append(
            f'<a class="card" href="{href}">\n'
            f'  <img src="{shot_prefix}/{shot}" alt="" width="640" height="400" loading="lazy" decoding="async">\n'
            f'  <div class="pad">\n'
            f'    <span class="kind">{name}</span>\n'
            f'    <h3>{blurb}</h3>\n'
            f'  </div>\n'
            f'</a>'
        )
    skills_html = ""
    if include_skills:
        skills_html = (
            '<section class="group">\n'
            '  <h2>The skills</h2>\n'
            '  <div class="cards">\n    '
            + "\n    ".join(skill_cards)
            + "\n  </div>\n</section>"
        )
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", encoding="utf-8", delete=False
    ) as tmp:
        raw = (ROOT / "templates" / "docs-gallery.html").read_text(encoding="utf-8")
        filled = (
            raw.replace("<!-- @@VOICES -->", voices_html, 1)
            .replace("<!-- @@PROFILES -->", profiles_html, 1)
            .replace("<!-- @@SKILLS -->", skills_html, 1)
            .replace("<!-- @@CARDS -->", cards_html, 1)
            .replace("@@TYPES_HREF", types_href)
        )
        tmp.write(filled)
        tmp_path = Path(tmp.name)
    try:
        assembled = build(tmp_path, "field-notes")
    finally:
        tmp_path.unlink(missing_ok=True)
    if (
        "@@INLINE" in assembled
        or "@@CARDS" in assembled
        or "@@SKILLS" in assembled
        or "@@VOICES" in assembled
        or "@@TYPES_HREF" in assembled
    ):
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
            for slug in gallery_figs + list(DIAGRAMS) + ["platform-architecture"]:
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
    print("\ndone. Screenshot with: python scripts/shoot_examples.py")


if __name__ == "__main__":
    main()
