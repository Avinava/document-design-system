#!/usr/bin/env python3
"""Build the GitHub Pages site into site/.

    python scripts/build_examples.py
    python scripts/build_site.py

The site tells one engagement's story rather than listing artifacts:

    index.html     the story: claim, the engagement rail (STORY below), the two
                   dials, composition, figures, checks, skills, what's new,
                   and the pinned toolchain
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
class Stop:
    page: str  # published page
    date: str  # as printed; must appear verbatim in `source`
    source: str  # repository file the date is read from
    beat: str  # what happens in the engagement here
    question: str  # the reader's question the document answers
    shows: str  # what the document does to answer it
    kind: str  # what the document is
    image: str  # under screenshots/: a thumbnail, or a slide for the deck


# Northwind Ingestion in date order. Dates are the examples' own (WORLD.md is
# the ledger they share); --check fails if a date is not in its source file.
STORY = (
    Stop("postmortem.html", "2026-07-30", "examples/postmortem.md",
         "The shared queue fills and every producer stops for 1 hour 52 minutes.",
         TYPE_QUESTIONS["postmortem"],
         "Impact before narrative, a timestamped reconstruction, and corrective actions with owners.",
         "Postmortem, incident pattern", "thumbs/postmortem.png"),
    Stop("inventory-report.html", "2026-08-12", "templates/document.html",
         "An inventory snapshot shows where the risk concentrates.",
         "Where does the platform footprint sit, measured?",
         "41% of the footprint sits on ingestion, with named denominators, a limit ledger and a methodology block.",
         "Analytical report", "thumbs/analytical-report.png"),
    Stop("capacity-deck.html", "2026-08-12", "templates/deck.html",
         "Platform presents the ask to the Platform director.",
         "What are you asking me for, and by when?",
         "Fourteen slides with claim titles: four of the last six incidents, three options, one recommendation.",
         "Deck", "deck-compare.png"),
    Stop("discovery.html", "2026-08-18", "examples/discovery.md",
         "Discovery closes: the queue is the failure boundary.",
         TYPE_QUESTIONS["discovery"],
         "Evidence that faster detection alone will not fix it, and the fastest way to test the split.",
         "Discovery brief, decision pattern", "thumbs/discovery.png"),
    Stop("runbook.html", "2026-08-18", "examples/runbook.md",
         "Until the split ships, on-call keeps the single queue alive.",
         TYPE_QUESTIONS["runbook"],
         "Safety first, then steps with checkpoints, beside a deployment map of clusters, namespace and replicas.",
         "Runbook, procedure pattern", "thumbs/runbook.png"),
    Stop("estimate.html", "2026-08-26", "examples/estimate.md",
         "The split is sized before anyone commits to it.",
         TYPE_QUESTIONS["estimate"],
         "A waterfall from workstreams to 24 engineer-weeks, with the unapproved change request shown but not counted.",
         "Basis of estimate, decision pattern", "thumbs/estimate.png"),
    Stop("status-report.html", "2026-08-26", "examples/status-report.md",
         "Delivery reports Amber: the decision and the test environment are still open.",
         TYPE_QUESTIONS["status-report"],
         "Current state in three cells, what moved, and the one action each reader owns.",
         "Delivery status report, brief pattern", "thumbs/status-report.png"),
    Stop("design-doc.html", "2026-09-01", "examples/design-doc.md",
         "RFC 014 goes to the Platform director for a decision.",
         TYPE_QUESTIONS["design-doc"],
         "The ask up front, options on the same criteria, and a change view of one queue becoming two.",
         "Design doc, decision pattern", "thumbs/design-doc.png"),
    Stop("delivery-plan.html", "2026-09-01", "examples/delivery-plan.md",
         "Five gates carry the work from the decision to handoff.",
         TYPE_QUESTIONS["delivery-plan"],
         "A milestone rail, workstreams, and a dependency graph whose critical path is the one accent.",
         "Delivery plan, plan pattern", "thumbs/delivery-plan.png"),
    Stop("readiness-review.html", "2026-10-28", "examples/readiness-review.md",
         "The readiness gate: conditional go.",
         TYPE_QUESTIONS["readiness-review"],
         "The verdict beside its evidence; chaos and rollback evidence must close before release.",
         "Production readiness review, assurance pattern", "thumbs/readiness-review.png"),
    Stop("migration-plan.html", "2026-11-02", "examples/migration-plan.md",
         "Cutover moves one partition at a time.",
         TYPE_QUESTIONS["migration-plan"],
         "Rehearsal, sequence and gates, with the original queue kept recoverable until hypercare closes.",
         "Migration and cutover plan, plan pattern", "thumbs/migration-plan.png"),
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


def back_to_home(section: str) -> tuple[str, str, str]:
    return (f"index.html#{section}", "← Home", "Back to the home page")


STORY_PAGES = {stop.page for stop in STORY}

# Showcase pages that are not types: where each one's back link leads.
HTML_KEEP = {
    "inventory-report.html": back_to_story("inventory-report.html"),
    "capacity-deck.html": back_to_story("capacity-deck.html"),
    "gallery-light.html": back_to_home("figures"),
    "gallery-dark.html": back_to_home("figures"),
    "themes-light.html": back_to_home("dials"),
    "themes-dark.html": back_to_home("dials"),
    "proposal-horizon.html": back_to_home("dials"),
    "proposal-coral.html": back_to_home("dials"),
    "brand.html": back_to_home("dials"),
    "mulesoft.html": ("types.html#profiles", "← Patterns", "Back to the compatibility profiles"),
}


def type_back(slug: str) -> tuple[str, str, str]:
    page = f"{slug}.html"
    if page in STORY_PAGES:
        return back_to_story(page)
    return back_to_pattern(catalog.TYPES[slug].pattern)


# Local targets of src/href/srcset attributes; external, data: and mailto: URLs
# and in-page anchors are not site files.
LOCAL_REF = re.compile(r'(?:src|href|srcset)="(?!https?:|mailto:|data:|#)([^"\s]+)')


def write_page_copy(src: Path, dest: Path, back: tuple[str, str, str]) -> None:
    """Copy an assembled page and add Pages-only navigation affordances."""
    html = src.read_text(encoding="utf-8")
    html = html.replace(
        "</head>",
        '<link rel="icon" href="assets/banner.svg" type="image/svg+xml">\n</head>',
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


def render_story(shot: str) -> str:
    items = []
    for i, stop in enumerate(STORY):
        focal = " focal" if i == len(STORY) - 1 else ""
        items.append(
            f'<li class="stop{focal}" id="{story_anchor(stop.page)}">\n'
            f'  <time datetime="{stop.date}">{stop.date}</time><span class="dot" aria-hidden="true"></span>\n'
            f'  <div class="text">\n'
            f'    <p class="beat">{esc(stop.beat)}</p>\n'
            f'    <h3><a href="{stop.page}">{esc(stop.question)}</a></h3>\n'
            f'    <p class="shows">{esc(stop.shows)}<span class="doc-kind">{esc(stop.kind)}</span></p>\n'
            f"  </div>\n"
            f'  <a class="thumb" href="{stop.page}" tabindex="-1" aria-hidden="true">'
            f'<img src="{shot}/{stop.image}" alt="" width="640" height="400" loading="lazy" decoding="async"></a>\n'
            f"</li>"
        )
    return "\n".join(items)


def render_asks() -> str:
    return "\n".join(
        f'<li><a href="{page}"><q>{esc(text)}</q><span class="becomes">{esc(becomes)}</span></a></li>'
        for text, page, becomes in ASKS
    )


def modules_used(slug: str) -> list[catalog.Module]:
    bodies = catalog.example_bodies()
    _, path = bodies[slug]
    used = catalog.body_classes(path.read_text(encoding="utf-8"))
    return [m for c, m in catalog.MODULES.items() if c in used]


def render_primer(shot: str) -> str:
    blocks = []
    for slug, (theme, pattern) in catalog.COMPOSED.items():
        title, question, nearest = COMPOSED_GALLERY[slug]
        mods = ", ".join(
            f'<a href="modules.html#{m.css_class}">{esc(m.name)}</a>'
            for m in modules_used(slug)
            if m.css_class not in {"section-num", "reading-time", "figure", "table-scroll"}
        )
        blocks.append(
            '<div class="primer" id="composed">\n'
            f'  <a class="frame crop" href="{slug}.html"><img alt="The {esc(title.lower())}: a composed document in the {pattern} pattern" '
            f'src="{shot}/thumbs/{slug}.png" width="640" height="400" loading="lazy"></a>\n'
            f'  <div>\n'
            f'    <h3><a href="{slug}.html">{esc(title)}: {esc(question)}</a></h3>\n'
            f'    <p>An engineer arriving from batch and warehouse work asks how ingestion maps onto what they know. '
            f'No preset answers that, so the writing skill composes one.</p>\n'
            f'    <dl><dt>Pattern</dt><dd><a href="types.html#{pattern}">{pattern.capitalize()}</a></dd>'
            f'<dt>Modules</dt><dd>{mods}</dd>'
            f'<dt>Nearest preset</dt><dd><a href="{nearest}.html">{esc(catalog.TYPES[nearest].title)}</a></dd>'
            f'<dt>Theme</dt><dd>{esc(theme)}</dd></dl>\n'
            f"  </div>\n"
            f"</div>"
        )
    blocks.append(
        '<p class="promotion">A shape composed three times becomes a preset. '
        "That is the only way the catalog grows.</p>"
    )
    return "\n".join(blocks)


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
    marks = common_marks(
        "index.html",
        "document-design-system — documents that get a reader to a decision",
        "A design system for documents: pick the pattern for how it reads and the theme for how it sounds. "
        "Follow one engagement from incident to cutover.",
    )
    marks.update({
        "<!-- @@ASKS -->": render_asks(),
        "<!-- @@STORY -->": render_story(shot),
        "<!-- @@CHOOSER -->": site_parts.chooser(
            lambda p: f"types.html#{p}", lambda s: f"{s}.html", "Reader's question, pattern, and presets"
        ),
        "<!-- @@PRIMER -->": render_primer(shot),
        "<!-- @@FIGURES -->": render_figures(),
        "<!-- @@LEDGER -->": render_ledger(),
        "<!-- @@BUILT_ON -->": render_built_on(),
        "@@TYPES_WORD_CAP": types_word.capitalize(),
        "@@PATTERNS_WORD": site_parts.words(len(catalog.PATTERNS)),
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
    banner = ASSETS / "banner.svg"
    if banner.is_file():
        shutil.copy2(banner, assets / "banner.svg")

    for slug in catalog.TYPES:
        src = EX / f"{slug}.html"
        if not src.is_file():
            sys.exit(f"missing {src.relative_to(ROOT)} — run build_examples.py first")
        write_page_copy(src, dest / f"{slug}.html", type_back(slug))

    # Composed examples return to the pattern they were composed in.
    for slug, (_, pattern) in catalog.COMPOSED.items():
        src = EX / f"{slug}.html"
        if not src.is_file():
            sys.exit(f"missing {src.relative_to(ROOT)} — run build_examples.py first")
        write_page_copy(src, dest / f"{slug}.html", back_to_pattern(pattern))

    for name, back in HTML_KEEP.items():
        src = EX / name
        if src.is_file():
            write_page_copy(src, dest / name, back)

    assemble_home("screenshots", dest / "index.html")
    assemble_docs_gallery("screenshots/thumbs", dest / "types.html", site=True)
    assemble_modules(dest / "modules.html")
    (dest / ".nojekyll").write_text("", encoding="utf-8")


SITE_PAGES = ("index.html", "types.html", "modules.html")


def check_built(dest: Path) -> None:
    def fail(message: str) -> None:
        sys.exit(f"site check: {message}")

    pages = {}
    for name in SITE_PAGES:
        path = dest / name
        if not path.is_file():
            fail(f"{name} failed to assemble")
        pages[name] = path.read_text(encoding="utf-8")
    home, gallery, modules = (pages[n] for n in SITE_PAGES)

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
    for stop in STORY:
        source = (ROOT / stop.source).read_text(encoding="utf-8")
        if stop.date not in source:
            fail(f"story stop {stop.page} is dated {stop.date}, which {stop.source} does not contain")
        if not (dest / stop.page).is_file():
            fail(f"story stop {stop.page} is not in the published site")
        if f'id="{story_anchor(stop.page)}"' not in home or f'href="{stop.page}"' not in home:
            fail(f"homepage does not link story stop {stop.page}")
        if not (dest / "screenshots" / stop.image).is_file():
            fail(f"story stop {stop.page} has no image {stop.image}")
    dates = [stop.date for stop in STORY]
    if dates != sorted(dates):
        fail("STORY is not in date order")
    for pattern in catalog.PATTERNS:
        if f'href="types.html#{pattern}"' not in home:
            fail(f"homepage does not link the {pattern} pattern")
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
    published.update({f"{slug}.html": back_to_pattern(p) for slug, (_, p) in catalog.COMPOSED.items()})
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
        if 'href="assets/banner.svg"' not in page.read_text(encoding="utf-8"):
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
