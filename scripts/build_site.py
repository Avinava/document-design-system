#!/usr/bin/env python3
"""Build the GitHub Pages site into site/.

    python scripts/build_examples.py
    python scripts/build_site.py

The site teaches one idea through one engagement: the reader's question picks
the shape (pattern), the audience picks the voice (theme), and both sit on the
same facts.

    index.html     claim and install, the core shown once, the story in four
                   acts by the reader's job (ACTS and STORY below), figures,
                   checks, skills, what's new, and the pinned toolchain
    types.html     the Patterns page: reader's question -> pattern -> presets
    modules.html   one specimen per registered module

Example documents are copied beside them with a back link to the story stop
or pattern they belong to. Every list is generated — from scripts/catalog.py,
STORY, scripts/pins.py and the check scripts — so a link cannot point at a
page that does not exist and a count cannot go stale.

    python scripts/build_site.py --check
writes to a temp dir, asserts the structure, then deletes it.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"
SHOTS = ROOT / "docs" / "screenshots"
ASSETS = ROOT / "assets"

sys.path.insert(0, str(ROOT / "scripts"))
import catalog  # noqa: E402
import check_diagrams  # noqa: E402
import check_render  # noqa: E402
import pins  # noqa: E402
import site_parts  # noqa: E402
from build_document import build  # noqa: E402
from build_examples import (  # noqa: E402
    COMPOSED_GALLERY,
    TYPE_QUESTIONS,
    assemble_docs_gallery,
    figure,
)
from site_parts import REPO_URL, esc  # noqa: E402

PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"
LICENSES_MD = ROOT / "THIRD_PARTY_LICENSES.md"
DIAGRAM_FAMILIES = ROOT / "skills" / "diagram-design" / "references" / "diagram-families.md"



# --------------------------------------------------------------------------
# the story
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Act:
    slug: str  # anchor: the act's section id is act-<slug>
    name: str
    question: str  # the job every reader in this act is doing
    opening: str  # one sentence


@dataclass(frozen=True)
class Stop:
    act: str  # Act.slug
    page: str  # published page
    reader: str  # who is reading, as it follows "For"
    question: str  # the reader's question the document answers
    pattern: str | None  # the writing pattern it chose, or None for a report or deck
    shape: str  # what the shape is, as shown
    why: str  # one clause: why that shape answers that question
    theme: str  # the voice it wears; must match the built page
    image: str  # under screenshots/: a thumbnail, or a slide for the deck
    date: str | None = None  # quiet metadata; must appear verbatim in `source`
    date_label: str = ""  # what the date is: the examples' dates are not one timeline
    source: str = ""  # repository file the date is read from


# Northwind Ingestion, ordered by the reader's job rather than the calendar:
# several example dates are data-as-of or review dates, so date order would
# read as a log. --check verifies every date against its source file and every
# pattern and theme against the built page.
ACTS = (
    Act("understand", "Understand", "Something broke. What is actually true?",
        "Before anyone proposes a fix, three readers need the facts in the shape of their own question."),
    Act("decide", "Decide", "Should we do this, and what will it take?",
        "One decision, due 2026-09-01, reaches the Platform director three ways: argued, sized and presented."),
    Act("deliver", "Deliver", "How do we get there without breaking producers?",
        "With the work under way, the questions turn to sequence, current state and proof."),
    Act("run", "Run and hand on", "Who keeps it alive, and how does the next engineer learn it?",
        "The last readers are the ones who stay, and the last question is one no preset answers."),
)

STORY = (
    Stop("understand", "postmortem.html", "Platform and Reliability", TYPE_QUESTIONS["postmortem"],
         "incident", "Incident pattern",
         "Impact comes before narrative, then a timeline, the cause, and corrective actions with owners.",
         "console-violet", "thumbs/postmortem.png", "2026-07-30", "Incident", "examples/postmortem.md"),
    Stop("understand", "inventory-report.html", "the platform review", "Where does the platform footprint sit, measured?",
         None, "Analytical report",
         "A measured claim carries its denominator: 41% of the footprint is 1.84M of 2.50M units.",
         "editorial-coral", "thumbs/analytical-report.png", "2026-08-12", "Data as of", "templates/document.html"),
    Stop("understand", "discovery.html", "Platform, before funding the build", TYPE_QUESTIONS["discovery"],
         "decision", "Decision pattern",
         "It ends on a next move: go, stop or reframe RFC 014, with the one-queue-down test that decides.",
         "field-notes", "thumbs/discovery.png", "2026-08-18", "Window closed", "examples/discovery.md"),
    Stop("decide", "design-doc.html", "the Platform director, with Reliability and the producer teams reviewing",
         TYPE_QUESTIONS["design-doc"], "decision", "Decision pattern",
         "The ask and its deadline come first, then options on the same criteria and a change view of one queue becoming two.",
         "field-notes", "thumbs/design-doc.png", "2026-09-01", "Decide by", "examples/design-doc.md"),
    Stop("decide", "estimate.html", "the Platform director", TYPE_QUESTIONS["estimate"],
         "decision", "Decision pattern",
         "The number and its confidence lead; a waterfall adds up to 24 engineer-weeks and draws CR-003 without counting it.",
         "executive-navy", "thumbs/estimate.png", "2026-08-26", "As of", "examples/estimate.md"),
    Stop("decide", "capacity-deck.html", "the Platform director, in the room", "What are you asking me for, and by when?",
         None, "Deck",
         "The same decision in another medium: one claim per slide, and the options compared on the same criteria.",
         "executive-navy", "deck-compare.png", "2026-08-12", "Presented", "templates/deck.html"),
    Stop("deliver", "delivery-plan.html", "Platform, Reliability and the producer teams", TYPE_QUESTIONS["delivery-plan"],
         "plan", "Plan pattern",
         "Baseline, workstreams, dependencies, then five gates; the critical path is the one accent in the dependency graph.",
         "executive-navy", "thumbs/delivery-plan.png", "2026-08-31", "Baseline from", "examples/delivery-plan.md"),
    Stop("deliver", "status-report.html", "the Platform director, Platform and Reliability", TYPE_QUESTIONS["status-report"],
         "brief", "Brief pattern",
         "Amber first, then what moved, then the one action each reader owns before the next report.",
         "executive-navy", "thumbs/status-report.png", "2026-08-26", "Period ending", "examples/status-report.md"),
    Stop("deliver", "readiness-review.html", "Reliability, which approves the gate", TYPE_QUESTIONS["readiness-review"],
         "assurance", "Assurance pattern",
         "The verdict comes first with its evidence beside it: conditional go until chaos and rollback evidence close.",
         "console-violet", "thumbs/readiness-review.png", "2026-10-28", "Review", "examples/readiness-review.md"),
    Stop("deliver", "migration-plan.html", "Platform, running the cutover", TYPE_QUESTIONS["migration-plan"],
         "plan", "Plan pattern",
         "Rehearsal, sequence and gates, one partition at a time, with the original queue kept until hypercare closes.",
         "console-violet", "thumbs/migration-plan.png", "2026-11-02", "Cutover", "examples/migration-plan.md"),
    Stop("run", "runbook.html", "on-call, while the lag alert is firing", TYPE_QUESTIONS["runbook"],
         "procedure", "Procedure pattern",
         "Safety before steps, a checkpoint after each, and a deployment map of cluster, namespace and replicas.",
         "console-violet", "thumbs/runbook.png", "2026-08-18", "Reviewed", "examples/runbook.md"),
    Stop("run", "platform-primer.html", "an engineer joining from batch and warehouse work",
         COMPOSED_GALLERY["platform-primer"][1], "learning", "Learning pattern, composed",
         "No preset answers it. The question picks the learning pattern, and the page is composed from that "
         "pattern's modules: a scope strip, a learning goal, a crosswalk and takeaways.",
         "field-notes", "thumbs/platform-primer.png"),
)

# Who each voice is for, in the examples' own theme rules (WORLD.md).
THEME_AUDIENCE = {
    "console-violet": "Engineers on the incident, the gate and the pager",
    "executive-navy": "Leadership deciding and funding",
    "field-notes": "Internal working documents",
    "editorial-coral": "Analysis for a wider review",
}

# The core's facts strip: one claim per evidence state, from WORLD.md.
FACTS = (
    ("Four of the last six incidents trace to the shared queue", "Verified", "from incident tickets"),
    ("Two independently recoverable queues reduce blast radius", "Recommended", "by RFC 014"),
    ("Shed-and-alert rather than block", "Unresolved", "Reliability owns the decision"),
)


def story_anchor(page: str) -> str:
    return f"story-{Path(page).stem}"


# Plain-language asks in the hero; each lands on the document it produces.
ASKS = (
    ("Write the cutover plan for RFC 014.", "migration-plan.html", "A migration and cutover plan, plan pattern"),
    ("Make a primer for engineers joining from batch.", "platform-primer.html",
     "Composed in the learning pattern; no preset fits"),
    ("Turn this inventory export into a report for the platform review.", "inventory-report.html",
     "An analytical report with its denominators named"),
    ("Show what the queue split changes, before and after.", "design-doc.html",
     "A change view inside the design doc"),
)

# Inline figures on the homepage: (svg slug, form, reader question, [(page, label)]).
FIGURES = (
    ("queue-split-change", "Change view", "What changes, and what stays the same?",
     (("design-doc.html", "design doc"), ("migration-plan.html", "migration plan"))),
    ("ingest-deployment", "Deployment map", "Where does each part run?",
     (("architecture.html", "architecture guide"), ("runbook.html", "runbook"))),
    ("workstream-dependencies", "Dependency graph", "What blocks what, and which path sets the date?",
     (("delivery-plan.html", "delivery plan"),)),
    ("estimate-bridge", "Waterfall bridge", "How do the parts add up to the total?",
     (("estimate.html", "estimate"),)),
)


# --------------------------------------------------------------------------
# back links
# --------------------------------------------------------------------------

# (href, label, aria-label) for each published example's fixed back link.
def back_to_story(page: str) -> tuple[str, str, str]:
    return (f"index.html#{story_anchor(page)}", "← Story", "Back to this stop in the engagement story")


def back_to_pattern(pattern: str) -> tuple[str, str, str]:
    return (f"types.html#{pattern}", "← Patterns", f"Back to the {pattern} pattern")


def back_to_site_page(page: str, label: str) -> tuple[str, str, str]:
    return (page, f"← {label}", f"Back to the {label} page")


def back_to_home(section: str) -> tuple[str, str, str]:
    return (f"index.html#{section}", "← Home", "Back to the home page")


STORY_PAGES = {stop.page for stop in STORY}

# Showcase pages that are not types: where each one's back link leads.
HTML_KEEP = {
    "inventory-report.html": back_to_story("inventory-report.html"),
    "capacity-deck.html": back_to_story("capacity-deck.html"),
    "gallery-light.html": back_to_site_page("figures.html", "Figures"),
    "gallery-dark.html": back_to_site_page("figures.html", "Figures"),
    "themes-light.html": back_to_site_page("themes.html", "Themes"),
    "themes-dark.html": back_to_site_page("themes.html", "Themes"),
    "proposal-horizon.html": back_to_site_page("themes.html", "Themes"),
    "proposal-coral.html": back_to_site_page("themes.html", "Themes"),
    "brand.html": back_to_site_page("themes.html", "Themes"),
    "mulesoft.html": ("types.html#profiles", "← Patterns", "Back to the compatibility profiles"),
}


def type_back(slug: str) -> tuple[str, str, str]:
    page = f"{slug}.html"
    if page in STORY_PAGES:
        return back_to_story(page)
    return back_to_pattern(catalog.TYPES[slug].pattern)


def composed_back(slug: str) -> tuple[str, str, str]:
    page = f"{slug}.html"
    if page in STORY_PAGES:
        return back_to_story(page)
    return back_to_pattern(catalog.COMPOSED[slug][1])


# Local targets of src/href/srcset attributes; external, data: and mailto: URLs
# and in-page anchors are not site files.
LOCAL_REF = re.compile(r'(?:src|href|srcset)="(?!https?:|mailto:|data:|#)([^"\s]+)')


def write_page_copy(src: Path, dest: Path, back: tuple[str, str, str]) -> None:
    """Copy an assembled page and add Pages-only navigation affordances."""
    html = src.read_text(encoding="utf-8")
    html = html.replace(
        "</head>",
        f"{site_parts.FAVICON_LINK}\n</head>",
        1,
    )
    # Screenshots live in docs/screenshots/ in the repository and in
    # screenshots/ on Pages, so a repository-relative image path would break.
    html = html.replace("../docs/screenshots/", "screenshots/")
    back_href, back_label, back_aria = back
    control = (
        '<style>.site-back{position:fixed;z-index:20;top:12px;left:12px;'
        'padding:.45rem .7rem;border:1px solid var(--rule-strong);border-radius:999px;'
        'background:var(--paper);color:var(--ink);font:600 .72rem/1 var(--mono);'
        'text-decoration:none;box-shadow:0 2px 12px color-mix(in srgb,var(--ink) 10%,transparent)}'
        '.site-back:focus-visible{outline:3px solid var(--accent);outline-offset:2px}'
        # Narrow screens have no free gutter, so the control joins the flow
        # there instead of covering the page's first line.
        '@media(max-width:900px){.site-back{position:static;display:inline-block;margin:12px 0 0 16px}}'
        '@media print{.site-back{display:none}}</style>\n'
        f'<a class="site-back" href="{back_href}" aria-label="{back_aria}">{back_label}</a>\n'
    )
    html = html.replace("<body>", "<body>\n" + control, 1)
    dest.write_text(html, encoding="utf-8")


# --------------------------------------------------------------------------
# generated sections
# --------------------------------------------------------------------------


def render_stop(stop: Stop, shot: str) -> str:
    shape = (
        f'<a href="types.html#{stop.pattern}">{esc(stop.shape)}</a>' if stop.pattern else esc(stop.shape)
    )
    when = (
        f'<div><dt>{esc(stop.date_label)}</dt><dd><time datetime="{stop.date}">{stop.date}</time></dd></div>'
        if stop.date else ""
    )
    return (
        f'<li class="stop" id="{story_anchor(stop.page)}">\n'
        f'  <div class="text">\n'
        f'    <p class="reader">For {esc(stop.reader)}</p>\n'
        f'    <h4><a href="{stop.page}">{esc(stop.question)}</a></h4>\n'
        f'    <p class="why"><strong>{shape}.</strong> {esc(stop.why)}</p>\n'
        f'    <dl class="meta"><div><dt>Voice</dt><dd>{esc(stop.theme)}</dd></div>{when}</dl>\n'
        f"  </div>\n"
        f'  <a class="thumb" href="{stop.page}" tabindex="-1" aria-hidden="true">'
        f'<img src="{shot}/{stop.image}" alt="" width="640" height="400" loading="lazy" decoding="async"></a>\n'
        f"</li>"
    )


def render_story(shot: str) -> str:
    acts = []
    for number, act in enumerate(ACTS, 1):
        stops = "\n".join(render_stop(stop, shot) for stop in STORY if stop.act == act.slug)
        acts.append(
            f'<section class="act" id="act-{act.slug}" aria-labelledby="act-{act.slug}-title">\n'
            f'  <header class="act-head">\n'
            f'    <p class="act-num" aria-hidden="true">{number}</p>\n'
            f'    <h3 id="act-{act.slug}-title"><span class="sr-only">Act {number}: </span><span class="act-name">{esc(act.name)}.</span> '
            f"{esc(act.question)}</h3>\n"
            f'    <p class="act-opening">{esc(act.opening)}</p>\n'
            f"  </header>\n"
            f'  <ol class="stops">\n{stops}\n  </ol>\n'
            f"</section>"
        )
    return "\n".join(acts)


def render_shape_rows() -> str:
    """Question -> pattern, one row per pattern the story uses, in story order."""
    rows, seen = [], set()
    for stop in STORY:
        if not stop.pattern or stop.pattern in seen:
            continue
        seen.add(stop.pattern)
        rows.append(
            f'<li><a href="{stop.page}"><q>{esc(stop.question)}</q></a>'
            f'<span class="maps" aria-hidden="true"></span>'
            f'<a class="to" href="types.html#{stop.pattern}">{esc(stop.pattern)}</a></li>'
        )
    return "\n".join(rows)


def render_voice_rows() -> str:
    """Audience -> theme, from the themes the story's documents wear."""
    rows = []
    for theme, audience in THEME_AUDIENCE.items():
        stops = [s for s in STORY if s.theme == theme]
        if not stops:
            sys.exit(f"THEME_AUDIENCE names {theme}, which no story stop wears")
        used = ", ".join(f'<a href="{s.page}">{esc(stop_title(s))}</a>' for s in stops)
        rows.append(
            f'<li><span class="who">{esc(audience)}<span class="used">{used}</span></span>'
            f'<span class="maps" aria-hidden="true"></span><span class="to">{esc(theme)}</span></li>'
        )
    return "\n".join(rows)


def stop_title(stop: Stop) -> str:
    slug = Path(stop.page).stem
    if slug in catalog.TYPES:
        return catalog.TYPES[slug].title.lower()
    if slug in COMPOSED_GALLERY:
        return COMPOSED_GALLERY[slug][0].lower()
    return stop.shape.lower()


def render_facts() -> str:
    return "\n".join(
        f'<li><span class="claim">{esc(claim)}</span>'
        f'<span class="state state-{state.lower()}">{esc(state)}</span>'
        f'<span class="basis">{esc(basis)}</span></li>'
        for claim, state, basis in FACTS
    )


def render_asks() -> str:
    return "\n".join(
        f'<li><a href="{page}"><q>{esc(text)}</q><span class="becomes">{esc(becomes)}</span></a></li>'
        for text, page, becomes in ASKS
    )


def render_figures() -> str:
    out = []
    for slug, form, question, used in FIGURES:
        where = " and ".join(f'<a href="{page}">{esc(label)}</a>' for page, label in used)
        out.append(
            f'<figure>\n<div class="diagram-scroll">{figure(slug)}</div>\n'
            f"<figcaption><strong>{esc(form)}.</strong> {esc(question)} In the {where}.</figcaption>\n</figure>"
        )
    return "\n".join(out)


def diagram_forms() -> int:
    """Diagram forms documented in the diagram skill: one `## ` section each."""
    heads = re.findall(r"^## (.+)$", DIAGRAM_FAMILIES.read_text(encoding="utf-8"), re.M)
    return len([h for h in heads if h.strip() != "Contents"])


def render_ledger() -> str:
    example_pages = len(list(EX.glob("*.html")))
    render_themes = len(check_render.themes())
    widths = len(check_render.MODES)
    themes = len(list((ROOT / "core" / "themes").glob("*.css")))
    rows = (
        (len(catalog.TYPES), "presets", "Each type file declares its pattern and theme; the catalog is derived from them, never copied.",
         "validate_repository.py"),
        (len(catalog.PATTERNS), "patterns", "Every pattern's characteristic modules are used by one of its examples.",
         "validate_repository.py"),
        (len(catalog.MODULES), "modules", "Each has CSS, the stylesheet styles nothing unregistered, and no body uses a module its pattern does not allow.",
         "validate_repository.py"),
        (len(check_diagrams.RULES), "diagram rules", "Shell, colour by token, 4px grid, overlap, bounds, label clearance, one accent family.",
         "check_diagrams.py"),
        (themes, "themes audited", "Contrast for every text pair, one accent, hue separation from status colours, dark print.",
         "audit_theme.py --all"),
        (example_pages * widths * render_themes, "page renders",
         f"{example_pages} pages at 1280px, 390px and print, under {site_parts.words(render_themes)} themes: "
         "no sideways scroll, no clipped figure text.",
         "check_render.py"),
    )
    body = "\n".join(
        f'<tr><td class="count">{n}</td><td class="what">{esc(what.capitalize())}'
        f'<span class="guards">{esc(guards)}</span></td><td><code>{esc(cmd)}</code></td></tr>'
        for n, what, guards, cmd in rows
    )
    return (
        '<table class="ledger">\n<thead><tr><th scope="col" class="num">Count</th><th scope="col">What is checked</th>'
        '<th scope="col">Check</th></tr></thead>\n<tbody>\n' + body + "\n</tbody>\n</table>"
    )


def licence_rows() -> dict[tuple[str, str], str]:
    """{(package, registry): licence} from the authoring table in THIRD_PARTY_LICENSES.md."""
    found: dict[tuple[str, str], str] = {}
    for line in LICENSES_MD.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*\[`([^`]+)`\]\([^)]*\)\s*\|\s*(npm|PyPI)\s*\|\s*([^|]+)\|\s*([^|]+)\|", line)
        if m:
            found[(m.group(1).lower(), m.group(2).lower())] = m.group(4).strip()
    return found


def render_built_on() -> str:
    licences = licence_rows()
    rows = []
    for registry, entries in (("npm", pins.npm_pins()), ("pypi", pins.python_pins())):
        for name, version in sorted(entries.items()):
            licence = licences.get((name.lower(), registry))
            if licence is None:
                sys.exit(f"THIRD_PARTY_LICENSES.md has no licence row for {registry} {name}")
            shown = "PyPI" if registry == "pypi" else "npm"
            rows.append(f"<tr><td><code>{esc(name)}</code></td><td>{shown}</td><td>{esc(version)}</td><td>{esc(licence)}</td></tr>")
    licences_url = f"{REPO_URL}/blob/main/THIRD_PARTY_LICENSES.md"
    return (
        '<table class="pins">\n<thead><tr><th scope="col">Package</th><th scope="col">Registry</th>'
        '<th scope="col">Version</th><th scope="col">Licence</th></tr></thead>\n<tbody>\n'
        + "\n".join(rows)
        + "\n</tbody>\n</table>\n"
        '<p class="credit"><strong>Design influence.</strong> The diagram skill\'s editorial standard is adapted from '
        '<a href="https://github.com/cathrynlavery/diagram-design">diagram-design</a> by Cathryn Lavery (MIT): '
        "deletion as the best edit, one accent, geometry on a grid, and diagram files as structure to redraw. "
        f'No code is used. Full notices are in <a href="{licences_url}">THIRD_PARTY_LICENSES.md</a>.</p>'
    )


def _assemble(template: str, marks: dict[str, str], dest: Path) -> None:
    raw = (ROOT / "templates" / template).read_text(encoding="utf-8")
    for marker, value in marks.items():
        if marker not in raw:
            sys.exit(f"templates/{template} has no {marker} marker")
        raw = raw.replace(marker, value)
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as tmp:
        tmp.write(raw)
        tmp_path = Path(tmp.name)
    try:
        assembled = build(tmp_path, site_parts.SITE_THEME)
    finally:
        tmp_path.unlink(missing_ok=True)
    if "@@" in assembled:
        sys.exit(f"unresolved marker in {dest.name}")
    dest.write_text(assembled, encoding="utf-8")


def common_marks(page: str, title: str, description: str) -> dict[str, str]:
    return {
        "<!-- @@META -->": site_parts.head_meta(title, description, page),
        "/* @@SITE_CSS */": site_parts.SHARED_CSS,
        "/* @@DARK */": site_parts.dark_css(),
        "<!-- @@NAV -->": site_parts.site_nav(page),
    }


def home_marks(shot: str) -> dict[str, str]:
    types_word = site_parts.words(len(catalog.TYPES))
    used = {stop.pattern for stop in STORY if stop.pattern}
    marks = common_marks(
        "index.html",
        "document-design-system — documents that get a reader to a decision",
        "Name the reader and their question: the question picks the document's shape, the audience picks its "
        "voice, and both sit on the same facts. Follow one engagement in four acts.",
    )
    marks.update({
        "<!-- @@ASKS -->": render_asks(),
        "<!-- @@STORY -->": render_story(shot),
        "<!-- @@SHAPES -->": render_shape_rows(),
        "<!-- @@VOICES -->": render_voice_rows(),
        "<!-- @@FACTS -->": render_facts(),
        "<!-- @@FIGURES -->": render_figures(),
        "<!-- @@LEDGER -->": render_ledger(),
        "<!-- @@BUILT_ON -->": render_built_on(),
        "@@TYPES_WORD_CAP": types_word.capitalize(),
        "@@TYPES_WORD": types_word,
        "@@STOPS_WORD_CAP": site_parts.words(len(STORY)).capitalize(),
        "@@USED_PATTERNS_WORD": site_parts.words(len(used)),
        "@@VOICES_WORD": site_parts.words(len({stop.theme for stop in STORY})),
        "@@PATTERNS_WORD": site_parts.words(len(catalog.PATTERNS)),
        "@@OTHER_PATTERNS_WORD": site_parts.words(len(catalog.PATTERNS) - len(used)),
        "@@FORMS_WORD": site_parts.words(diagram_forms()),
        "@@SHOT": shot,
        "@@REPO": REPO_URL,
    })
    return marks


def assemble_home(shot: str, dest: Path) -> None:
    _assemble("site.html", home_marks(shot), dest)


def home_shots() -> set[str]:
    """Screenshots the homepage shows, relative to docs/screenshots/."""
    shot = "@@SHOT"
    raw = (ROOT / "templates" / "site.html").read_text(encoding="utf-8")
    for marker, value in home_marks(shot).items():
        raw = raw.replace(marker, value)
    return set(re.findall(rf'{shot}/([\w./-]+\.png)', raw))


# --------------------------------------------------------------------------
# modules page
# --------------------------------------------------------------------------

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}

# An inline module reads better inside the element that frames it.
SPECIMEN_CONTEXT = {"section-num": "section-head", "reading-time": "section-head"}

# Registered modules no example uses yet still get a specimen, written here
# from WORLD.md facts and labelled as written for this page.
SPECIMEN_FALLBACK = {
    "footnotes": (
        '<section class="footnotes"><ol>'
        "<li>Incident tickets for 2026-03-14, 2026-04-02, 2026-06-19 and 2026-07-30. Verified.</li>"
        "<li>Normalized inventory export, as of 2026-08-12. 1.84M of 2.50M units.</li>"
        "</ol></section>"
    ),
}


class _Elements(HTMLParser):
    """Source text of every element, keyed by each class it carries."""

    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=False)
        self.text = text
        self.starts = [0] + [m.end() for m in re.finditer("\n", text)]
        self.stack: list[tuple[str, int, list[str]]] = []
        self.found: dict[str, list[str]] = {}

    def _offset(self) -> int:
        line, col = self.getpos()
        return self.starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        classes = (dict(attrs).get("class") or "").split()
        self.stack.append((tag, self._offset(), classes))

    def handle_endtag(self, tag):
        while self.stack:
            open_tag, start, classes = self.stack.pop()
            if open_tag == tag:
                end = self._offset() + len(f"</{tag}>")
                for name in classes:
                    self.found.setdefault(name, []).append(self.text[start:end])
                return


def specimens() -> dict[str, tuple[str, str | None]]:
    """{module class: (markup, example it came from or None)} — the shortest real use."""
    candidates: dict[str, list[tuple[int, str, str]]] = {}
    for name, (_, path) in catalog.example_bodies().items():
        text = path.read_text(encoding="utf-8")
        parser = _Elements(text)
        parser.feed(text)
        for css_class in catalog.MODULES:
            source = SPECIMEN_CONTEXT.get(css_class, css_class)
            for fragment in parser.found.get(source, []):
                if source != css_class and f'class="{css_class}"' not in fragment:
                    continue
                candidates.setdefault(css_class, []).append((len(fragment), name, fragment))
    out: dict[str, tuple[str, str | None]] = {}
    for css_class in catalog.MODULES:
        if css_class in candidates:
            _, name, fragment = min(candidates[css_class])
            out[css_class] = (fragment, name)
        elif css_class in SPECIMEN_FALLBACK:
            out[css_class] = (SPECIMEN_FALLBACK[css_class], None)
        else:
            sys.exit(f"module `{css_class}` has no example use and no fallback specimen")
    return out


def _clean_specimen(fragment: str) -> str:
    """Inline figures and drop ids, which would repeat across the page."""
    fragment = re.sub(r"<!-- @FIG ([a-z0-9-]+) -->", lambda m: figure(m.group(1)), fragment)
    if "<svg" in fragment:
        return fragment
    return re.sub(r'\s(?:id|aria-labelledby|aria-describedby)="[^"]*"', "", fragment)


def module_users() -> dict[str, list[str]]:
    users: dict[str, list[str]] = {c: [] for c in catalog.MODULES}
    for name, (_, path) in sorted(catalog.example_bodies().items()):
        used = catalog.body_classes(path.read_text(encoding="utf-8"))
        for css_class in users:
            if css_class in used:
                users[css_class].append(name)
    return users


def example_title(name: str) -> str:
    if name in catalog.TYPES:
        return catalog.TYPES[name].title
    if name in COMPOSED_GALLERY:
        return COMPOSED_GALLERY[name][0]
    return name


def assemble_modules(dest: Path) -> None:
    specs = specimens()
    users = module_users()
    index = []
    sections = []
    for css_class, module in catalog.MODULES.items():
        markup, source = specs[css_class]
        allowed = (
            "every pattern"
            if len(module.patterns) == len(catalog.PATTERNS)
            else ", ".join(f'<a href="types.html#{p}">{p.capitalize()}</a>' for p in module.patterns)
        )
        used = users[css_class]
        used_html = ", ".join(f'<a href="{n}.html">{esc(example_title(n))}</a>' for n in used) or "No example yet"
        if source:
            origin = f'Specimen from the <a href="{source}.html">{esc(example_title(source))}</a>.'
        else:
            origin = "No example uses this module yet; this specimen is written for this page."
        index.append(f'<li><a href="#{css_class}">{esc(module.name.capitalize())}</a></li>')
        sections.append(
            f'<section class="module{"" if used else " unused"}" id="{css_class}" aria-labelledby="{css_class}-title">\n'
            f'  <header class="module-head">\n'
            f'    <h2 id="{css_class}-title">{esc(module.name.capitalize())}</h2>\n'
            f'    <code class="class-name">.{css_class}</code>\n'
            f'    <p class="purpose">{esc(module.purpose)}.</p>\n'
            f"    <dl><dt>Allowed in</dt><dd>{allowed}</dd>"
            f"<dt>Used in {len(used)} example{'s' if len(used) != 1 else ''}</dt><dd>{used_html}</dd></dl>\n"
            f"  </header>\n"
            f'  <div>\n    <div class="specimen-frame">\n{_clean_specimen(markup)}\n    </div>\n'
            f'    <p class="specimen-source">{origin}</p>\n  </div>\n'
            f"</section>"
        )
    marks = common_marks(
        "modules.html",
        "Document modules — document-design-system",
        f"{len(catalog.MODULES)} document modules, each with a specimen from a real example, "
        "the patterns that may use it, and where it is used.",
    )
    marks.update({
        "<!-- @@INDEX -->": "\n".join(index),
        "<!-- @@MODULES -->": "\n".join(sections),
        "@@MODULES_WORD_CAP": site_parts.words(len(catalog.MODULES)).capitalize(),
        "@@REPO": REPO_URL,
    })
    _assemble("modules.html", marks, dest)


# --------------------------------------------------------------------------
# figures and themes pages
# --------------------------------------------------------------------------


def shared_block(template: str, name: str) -> tuple[str, str]:
    """The CSS and markup a showcase template marks as shared with a site page:
    `/* name: begin … */ … /* name: end */` and `<!-- name: begin --> … <!-- name: end -->`."""
    raw = (ROOT / "templates" / template).read_text(encoding="utf-8")
    css = re.search(rf"/\* {name}: begin[^*]*\*/(.*?)/\* {name}: end \*/", raw, re.S)
    body = re.search(rf"<!-- {name}: begin -->(.*?)<!-- {name}: end -->", raw, re.S)
    if not css or not body:
        sys.exit(f"templates/{template} lost its '{name}: begin/end' markers")
    return css.group(1).strip(), body.group(1).strip()


def assemble_figures(dest: Path) -> None:
    css, grid = shared_block("gallery.html", "figures")
    grid = re.sub(r"<!-- @FIG ([a-z0-9-]+) -->", lambda m: figure(m.group(1)), grid)
    marks = common_marks(
        "figures.html",
        "Figures — document-design-system",
        "Every diagram and chart form the examples use, as SVG on the page's own tokens, "
        "each with the reader's question it answers.",
    )
    marks.update({
        "<!-- @@FAVICON -->": site_parts.FAVICON_LINK,
        "/* @@GALLERY_CSS */": css,
        "<!-- @@GALLERY -->": grid,
        "@@FORMS_WORD_CAP": site_parts.words(diagram_forms()).capitalize(),
        "@@RULES_WORD_CAP": site_parts.words(len(check_diagrams.RULES)).capitalize(),
        "@@REPO": REPO_URL,
    })
    _assemble("site-figures.html", marks, dest)


def assemble_themes(dest: Path) -> None:
    css, panels = shared_block("themes.html", "panels")
    marks = common_marks(
        "themes.html",
        "Themes — document-design-system",
        "The same content under every theme, one proposal in three voices, and how a client's brand "
        "becomes a theme with its contrast audited.",
    )
    marks.update({
        "<!-- @@FAVICON -->": site_parts.FAVICON_LINK,
        "/* @@PANELS_CSS */": css,
        "<!-- @@PANELS -->": panels,
        "@@REPO": REPO_URL,
    })
    _assemble("site-themes.html", marks, dest)


# --------------------------------------------------------------------------
# build and check
# --------------------------------------------------------------------------


def populate(dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    shots = dest / "screenshots"
    shots.mkdir(exist_ok=True)
    for png in sorted(SHOTS.glob("*.png")):
        shutil.copy2(png, shots / png.name)
    thumb_source = SHOTS / "thumbs"
    if thumb_source.is_dir():
        shutil.copytree(thumb_source, shots / "thumbs", dirs_exist_ok=True)

    assets = dest / "assets"
    assets.mkdir(exist_ok=True)
    for name in ("banner.svg", "mark.svg", "wordmark.svg"):
        if (ASSETS / name).is_file():
            shutil.copy2(ASSETS / name, assets / name)

    for slug in catalog.TYPES:
        src = EX / f"{slug}.html"
        if not src.is_file():
            sys.exit(f"missing {src.relative_to(ROOT)} — run build_examples.py first")
        write_page_copy(src, dest / f"{slug}.html", type_back(slug))

    # Composed examples return to their story stop, or to the pattern they
    # were composed in.
    for slug in catalog.COMPOSED:
        src = EX / f"{slug}.html"
        if not src.is_file():
            sys.exit(f"missing {src.relative_to(ROOT)} — run build_examples.py first")
        write_page_copy(src, dest / f"{slug}.html", composed_back(slug))

    for name, back in HTML_KEEP.items():
        src = EX / name
        if src.is_file():
            write_page_copy(src, dest / name, back)

    assemble_home("screenshots", dest / "index.html")
    assemble_docs_gallery("screenshots/thumbs", dest / "types.html", site=True)
    assemble_modules(dest / "modules.html")
    assemble_figures(dest / "figures.html")
    assemble_themes(dest / "themes.html")
    (dest / ".nojekyll").write_text("", encoding="utf-8")


SITE_PAGES = ("index.html", "types.html", "modules.html", "figures.html", "themes.html")


def check_built(dest: Path) -> None:
    def fail(message: str) -> None:
        sys.exit(f"site check: {message}")

    pages = {}
    for name in SITE_PAGES:
        path = dest / name
        if not path.is_file():
            fail(f"{name} failed to assemble")
        pages[name] = path.read_text(encoding="utf-8")
    home, gallery, modules = pages["index.html"], pages["types.html"], pages["modules.html"]

    # Every item in the navigation opens a site page that carries it; a nav
    # item landing on a standalone document strands the reader.
    for _, href in site_parts.NAV:
        if not href.startswith("http") and href not in pages:
            fail(f"navigation item {href} is not a site page")

    for name, text in pages.items():
        if "@@" in text:
            fail(f"unresolved marker in {name}")
        if re.search(r'<img[^>]+src="\.\./docs/screenshots', text):
            fail(f"{name} still points at ../docs/screenshots")
        # The navigation, in order, with this page marked current.
        nav = re.search(r'<nav class="site-nav".*?</nav>', text, re.S)
        if not nav:
            fail(f"{name} has no site navigation")
        hrefs = re.findall(r'<li><a href="([^"]+)"', nav.group(0))
        if hrefs != [href for _, href in site_parts.NAV]:
            fail(f"{name} navigation is {hrefs}, expected {[h for _, h in site_parts.NAV]}")
        if f'href="{name}" aria-current="page"' not in nav.group(0):
            fail(f"{name} does not mark itself current in the navigation")
        for tag in ('name="description"', 'property="og:title"', 'property="og:image"',
                    'name="twitter:card"', 'rel="canonical"', 'name="color-scheme"'):
            if tag not in text:
                fail(f"{name} is missing <meta {tag}>")
        if "prefers-color-scheme: dark" not in text:
            fail(f"{name} has no dark palette")
    if not (dest / site_parts.SOCIAL_IMAGE).is_file():
        fail(f"missing {site_parts.SOCIAL_IMAGE} — run shoot_examples.py social-preview")

    # Homepage: the story, the patterns, the composed examples, the version.
    if "/plugin marketplace add Avinava/document-design-system" not in home:
        fail("homepage lost the install block")
    act_slugs = [act.slug for act in ACTS]
    if len(set(act_slugs)) != len(act_slugs):
        fail("two acts share a slug")
    for act in ACTS:
        if not any(stop.act == act.slug for stop in STORY):
            fail(f"act {act.slug} has no stops")
        if f'id="act-{act.slug}"' not in home:
            fail(f"homepage does not show act {act.slug}")
    for stop in STORY:
        if stop.act not in act_slugs:
            fail(f"story stop {stop.page} is in unknown act {stop.act}")
        if stop.date:
            source = (ROOT / stop.source).read_text(encoding="utf-8")
            if stop.date not in source:
                fail(f"story stop {stop.page} is dated {stop.date}, which {stop.source} does not contain")
        published = dest / stop.page
        if not published.is_file():
            fail(f"story stop {stop.page} is not in the published site")
        built = published.read_text(encoding="utf-8")
        if f'data-theme="{stop.theme}"' not in built:
            fail(f"story stop {stop.page} says it wears {stop.theme}, which the page does not")
        if stop.pattern and f'data-pattern="{stop.pattern}"' not in built:
            fail(f"story stop {stop.page} says it uses the {stop.pattern} pattern, which the page does not")
        if f'id="{story_anchor(stop.page)}"' not in home or f'href="{stop.page}"' not in home:
            fail(f"homepage does not link story stop {stop.page}")
        if f'class="site-back" href="{back_to_story(stop.page)[0]}"' not in built:
            fail(f"story stop {stop.page} has no back link to its stop")
        if not (dest / "screenshots" / stop.image).is_file():
            fail(f"story stop {stop.page} has no image {stop.image}")
    for pattern in {stop.pattern for stop in STORY if stop.pattern}:
        if f'href="types.html#{pattern}"' not in home:
            fail(f"homepage does not link the {pattern} pattern")
    if 'href="types.html"' not in home:
        fail("homepage does not link the Patterns page")
    for slug in catalog.COMPOSED:
        if f'href="{slug}.html"' not in home:
            fail(f"homepage does not link composed example {slug}.html")
    for slug, *_ in FIGURES:
        title = re.search(r'<title id="([^"]+)"', figure(slug))
        if not title or f'<title id="{title.group(1)}"' not in home:
            fail(f"homepage does not inline figure {slug}")
    version = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))["version"]
    shown = re.search(r"What's new in ([0-9][0-9.]*)", home)
    if not shown or shown.group(1) != version:
        fail(f"homepage describes {shown.group(1) if shown else 'no version'}; plugin.json is {version}")
    for skill in sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir()):
        if skill not in home:
            fail(f"homepage skills table is missing {skill}")
    for registry, entries in pins.pins().items():
        for name, ver in entries.items():
            if f"<code>{name}</code></td><td>{'PyPI' if registry == 'pypi' else 'npm'}</td><td>{ver}</td>" not in home:
                fail(f"homepage Built on is missing {name} {ver}")
    if "THIRD_PARTY_LICENSES.md" not in home:
        fail("homepage does not link the third-party licences")

    # Patterns page: every pattern, preset, module chip and composed example.
    for pattern in catalog.PATTERNS.values():
        if f'id="{pattern.name}"' not in gallery:
            fail(f"types.html missing the {pattern.name} pattern")
        for module_name in pattern.modules:
            css_class = next(m.css_class for m in catalog.MODULES.values() if m.name == module_name)
            if f'href="modules.html#{css_class}"' not in gallery:
                fail(f"types.html does not link {pattern.name}'s module {css_class}")
    for slug in catalog.TYPES:
        if f'href="{slug}.html"' not in gallery:
            fail(f"types.html missing {slug}.html")
        if not (dest / "screenshots" / "thumbs" / f"{slug}.png").is_file():
            fail(f"site missing thumbnail for {slug}")
    for slug in catalog.COMPOSED:
        if f'href="{slug}.html"' not in gallery:
            fail(f"types.html does not link composed example {slug}.html")
        if not (dest / "screenshots" / "thumbs" / f"{slug}.png").is_file():
            fail(f"site missing thumbnail for {slug}")
    for needle in ('id="lifecycle"', 'id="common-names"', 'id="profiles"', 'id="not-listed"', 'class="chooser"'):
        if needle not in gallery:
            fail(f"types.html missing {needle}")
    if 'loading="lazy"' not in gallery or "screenshots/thumbs" not in gallery:
        fail("types.html must use lazy, lightweight thumbnails")
    if 'id="skills"' in gallery:
        fail("types.html should not repeat the skill strip")

    # Modules page: one section per registered module.
    for css_class in catalog.MODULES:
        if f'<section class="module' not in modules or f'id="{css_class}"' not in modules:
            fail(f"modules.html missing module {css_class}")

    # Every published example has a way back, and the anchor it targets exists.
    published = {f"{slug}.html": type_back(slug) for slug in catalog.TYPES}
    published.update({f"{slug}.html": composed_back(slug) for slug in catalog.COMPOSED})
    published.update(HTML_KEEP)
    for name, (back_href, _, _) in published.items():
        page = dest / name
        if not page.is_file():
            fail(f"site missing {name}")
        if f'class="site-back" href="{back_href}"' not in page.read_text(encoding="utf-8"):
            fail(f"{name} has no way back to {back_href}")
        target, _, anchor = back_href.partition("#")
        if anchor and f'id="{anchor}"' not in pages[target]:
            fail(f"{name} returns to {back_href}, which has no such anchor")
        if f'href="{site_parts.FAVICON}"' not in page.read_text(encoding="utf-8"):
            fail(f"{name} is missing the favicon")

    # docs/screenshots/ holds exactly what something shows: no orphan is
    # committed, and nothing shown is missing.
    from shoot_examples import referenced_shots

    shown = referenced_shots()
    committed = {p.relative_to(SHOTS).as_posix() for p in SHOTS.rglob("*.png")}
    for rel in sorted(shown - committed):
        fail(f"docs/screenshots/{rel} is referenced but missing — run shoot_examples.py")
    for rel in sorted(committed - shown):
        fail(f"docs/screenshots/{rel} is not referenced by the README, an example or the site — delete it")

    for page in sorted(dest.glob("*.html")):
        for ref in LOCAL_REF.findall(page.read_text(encoding="utf-8")):
            target = ref.split("#")[0].split("?")[0]
            if target and not (dest / target).exists():
                fail(f"{page.name} refers to {ref}, which is not in the published site")
    print(
        f"ok: homepage {len(home):,} bytes, types {len(gallery):,} bytes, modules {len(modules):,} bytes; "
        f"{len(STORY)} story stops, {len(catalog.PATTERNS)} patterns, {len(catalog.MODULES)} modules"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="assemble into a temp dir and exit (CI)",
    )
    args = parser.parse_args()

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp)
            populate(dest)
            check_built(dest)
        return

    dest = ROOT / "site"
    if dest.exists():
        shutil.rmtree(dest)
    populate(dest)
    check_built(dest)
    print(f"wrote {dest.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
