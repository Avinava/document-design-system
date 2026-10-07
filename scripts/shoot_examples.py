#!/usr/bin/env python3
"""Screenshot the built examples into docs/screenshots/ for the README.

    uv venv && uv pip install -r requirements-authoring.txt
    uv run playwright install chromium
    python scripts/build_examples.py
    uv run python scripts/shoot_examples.py

Serves the repository root over localhost rather than using file:// URLs — a file:// page
cannot load the Google Fonts stylesheet consistently, and the screenshots would
show fallback metrics rather than what a reader sees. Serving the root also lets
the type gallery resolve its ../docs/screenshots/thumbs/ previews.

Two rules keep docs/screenshots/ small and reshoots idempotent:

- An image is written only when something shows it (referenced_shots): the
  README, a built example page, or the site. Thumbnails are cut from the
  in-memory capture, so a type's thumbnail needs no full-size file beside it.
- A capture that differs from the committed image only by rendering noise
  (same_image) keeps the committed bytes, so reshooting everything leaves an
  unchanged page's PNG untouched in git.
"""

from __future__ import annotations

import io
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT / "scripts"))
from _serve import serve  # noqa: E402
from pins import REPO_PYTHON_HINT  # noqa: E402

EX = ROOT / "examples"
OUT = ROOT / "docs" / "screenshots"
README = ROOT / "README.md"
PORT = 8931

# Two captures of an unchanged page differ by anti-aliasing and sub-pixel text
# placement: at most a couple of levels per channel, and in the worst case
# seen a 1px shift of one chart label (under 0.08% of the slide's pixels). A
# pixel counts as changed past TOLERANCE on any channel; a capture is noise
# while under MAX_CHANGED of its pixels changed. Keep MAX_CHANGED small: a
# real one-word copy edit on a full page is not much larger.
TOLERANCE = 8
MAX_CHANGED = 0.001

# name -> (page, viewport, full_page)
#
# Prefer a framed viewport over full_page for the prose documents. A full-page
# capture of a real report is ~2500 CSS px tall, which renders in a README as an
# unreadable sliver — the point of these is to show what the system looks like,
# not to reproduce the whole document.
SHOTS = {
    "patterns-gallery": ("index.html", (1280, 900), False),
    "analytical-report": ("inventory-report.html", (1280, 980), False),
    "analytical-report-detail": ("inventory-report.html", (1280, 980), False),
    "design-doc": ("design-doc.html", (1280, 980), False),
    "adr": ("adr.html", (1280, 720), False),
    "spec": ("spec.html", (1280, 980), False),
    "api-contract": ("api-contract.html", (1280, 980), False),
    "architecture": ("architecture.html", (1280, 980), False),
    "handoff": ("handoff.html", (1280, 980), False),
    "design-handoff": ("design-handoff.html", (1280, 980), False),
    "discovery": ("discovery.html", (1280, 980), False),
    "test-report": ("test-report.html", (1280, 980), False),
    "postmortem": ("postmortem.html", (1280, 980), False),
    "proposal": ("proposal.html", (1280, 800), False),
    "proposal-horizon": ("proposal-horizon.html", (1280, 800), False),
    "proposal-coral": ("proposal-coral.html", (1280, 800), False),
    "brand": ("brand.html", (1280, 900), False),
    "runbook": ("runbook.html", (1280, 980), False),
    "onboarding": ("onboarding.html", (1280, 900), False),
    "tutorial": ("tutorial.html", (1280, 900), False),
    "how-to": ("how-to.html", (1280, 800), False),
    "reference": ("reference.html", (1280, 800), False),
    "explanation": ("explanation.html", (1280, 800), False),
    "mulesoft": ("mulesoft.html", (1280, 900), False),
    "project-charter": ("project-charter.html", (1280, 980), False),
    "estimate": ("estimate.html", (1280, 980), False),
    "change-request": ("change-request.html", (1280, 980), False),
    "requirements": ("requirements.html", (1280, 980), False),
    "statement-of-work": ("statement-of-work.html", (1280, 980), False),
    "support-model": ("support-model.html", (1280, 980), False),
    "delivery-plan": ("delivery-plan.html", (1280, 980), False),
    "migration-plan": ("migration-plan.html", (1280, 980), False),
    "test-strategy": ("test-strategy.html", (1280, 980), False),
    "threat-model": ("threat-model.html", (1280, 980), False),
    "readiness-review": ("readiness-review.html", (1280, 980), False),
    "risk-register": ("risk-register.html", (1280, 980), False),
    "status-report": ("status-report.html", (1280, 980), False),
    "release-notes": ("release-notes.html", (1280, 980), False),
    "workshop-summary": ("workshop-summary.html", (1280, 980), False),
    "incident-update": ("incident-update.html", (1280, 980), False),
    "service-docs": ("service-docs.html", (1280, 980), False),
    # Composed from the learning pattern rather than a type preset.
    "platform-primer": ("platform-primer.html", (1280, 980), False),
    # Built Pages site (python scripts/build_site.py first). The social
    # preview is the Open Graph image, at its native 1200×630.
    "modules": ("../site/modules.html", (1280, 980), False),
    "social-preview": ("../site/index.html", (1200, 630), False),
    # Light/dark pairs, for the README <picture> elements that follow the
    # reader's GitHub theme.
    "gallery-light": ("gallery-light.html", (1280, 1430), True),
    "gallery-dark": ("gallery-dark.html", (1280, 1430), True),
    "themes-light": ("themes-light.html", (1280, 1180), False),
    "themes-dark": ("themes-dark.html", (1280, 1180), False),
}

# Scroll offset in CSS pixels, for shots that should show a section further
# down the page than the header.
SCROLL = {"analytical-report-detail": 1128}

# The Open Graph image is shown by other sites at its own pixel size, so it is
# taken at 1×.
NATIVE = {"social-preview"}

# name -> (page, zero-based slide index)
#
# Slides are captured as elements rather than viewports. A deck's title slide is
# deliberately sparse — one idea per slide — so a viewport shot of page one is
# mostly empty paper and tells a reader nothing about the system.
SLIDE_SHOTS = {
    "deck-title": ("capacity-deck.html", 0),
    "deck-statement": ("capacity-deck.html", 2),
    "deck-divider": ("capacity-deck.html", 3),
    "deck-table": ("capacity-deck.html", 4),
    "deck-metric": ("capacity-deck.html", 5),
    "deck-chart": ("capacity-deck.html", 6),
    "deck-diagram": ("capacity-deck.html", 7),
    "deck-compare": ("capacity-deck.html", 10),
    "deck-close": ("capacity-deck.html", 13),
}


SHOT_REF = re.compile(r"docs/screenshots/([\w./-]+\.png)")


def referenced_shots() -> set[str]:
    """Every image under docs/screenshots/ that something shows, as a path
    relative to it ("postmortem.png", "thumbs/postmortem.png").

    Read from the README, every built page in examples/ (the Patterns page's
    cards, the brand exhibit), and the site build (homepage and social image).
    """
    import build_site  # the site build imports the catalog and check scripts
    import site_parts

    found = set(SHOT_REF.findall(README.read_text(encoding="utf-8")))
    for page in sorted(EX.glob("*.html")):
        found |= set(SHOT_REF.findall(page.read_text(encoding="utf-8")))
    found |= build_site.home_shots()
    found.add(site_parts.SOCIAL_IMAGE.removeprefix("screenshots/"))
    return found


def same_image(a: bytes, b: bytes, *, tolerance: int = TOLERANCE, max_changed: float = MAX_CHANGED) -> bool:
    """True when two PNGs differ by no more than rendering noise: equal size,
    and under `max_changed` of the pixels move more than `tolerance` on any
    channel."""
    from PIL import Image, ImageChops

    if a == b:
        return True
    with Image.open(io.BytesIO(a)) as left, Image.open(io.BytesIO(b)) as right:
        if left.size != right.size:
            return False
        diff = ImageChops.difference(left.convert("RGBA"), right.convert("RGBA"))
    changed = None
    for band in diff.split():
        over = band.point(lambda v: 255 if v > tolerance else 0)
        changed = over if changed is None else ImageChops.lighter(changed, over)
    width, height = diff.size
    return changed.histogram()[255] < max_changed * width * height


def baseline(rel: str) -> bytes | None:
    """The committed image if git tracks it, else the file on disk, else None."""
    shown = subprocess.run(
        ["git", "show", f"HEAD:docs/screenshots/{rel}"], cwd=ROOT, capture_output=True
    )
    if shown.returncode == 0:
        return shown.stdout
    path = OUT / rel
    return path.read_bytes() if path.is_file() else None


def keep_or_write(rel: str, data: bytes) -> str:
    """Write a capture unless it is noise against its baseline; return the state."""
    base = baseline(rel)
    if base is not None and same_image(base, data):
        data, state = base, "unchanged"
    else:
        state = "new" if base is None else "updated"
    target = OUT / rel
    if not target.is_file() or target.read_bytes() != data:
        target.write_bytes(data)
    print(f"  {state:9} {target.relative_to(ROOT)}")
    return state


def thumbnail(data: bytes) -> bytes:
    from PIL import Image, ImageOps

    with Image.open(io.BytesIO(data)) as source:
        thumb = ImageOps.fit(
            source.convert("RGB"),
            (640, 400),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.0),
        )
    out = io.BytesIO()
    thumb.save(out, format="PNG", optimize=True)
    return out.getvalue()


def main() -> None:
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None

    try:
        from playwright.sync_api import sync_playwright
        import PIL  # noqa: F401
    except ImportError:
        sys.exit(
            "playwright and Pillow are required.\n"
            f"  {REPO_PYTHON_HINT}\n"
            "They are authoring-time dependencies only."
        )

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "thumbs").mkdir(exist_ok=True)
    wanted = referenced_shots()
    states: dict[str, int] = {}

    def save(name: str, capture) -> None:
        targets = [(f"{name}.png", lambda data: data), (f"thumbs/{name}.png", thumbnail)]
        targets = [(rel, cut) for rel, cut in targets if rel in wanted]
        data = capture()
        # A real change reproduces; a rendering flake (glyphs rasterised a
        # sub-pixel apart late in a long run) usually does not. Retake once
        # before treating a difference from a committed image as a change.
        for rel, cut in targets:
            base = baseline(rel)
            if base is not None and not same_image(base, cut(data)):
                data = capture()
                break
        for rel, cut in targets:
            state = keep_or_write(rel, cut(data))
            states[state] = states.get(state, 0) + 1

    def needed(name: str) -> bool:
        if only and name not in only:
            return False
        if f"{name}.png" in wanted or f"thumbs/{name}.png" in wanted:
            return True
        print(f"  skipped   {name}: nothing references it")
        return False

    httpd, base = serve(ROOT, PORT)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()

            for name, (page_file, (w, h), full) in SHOTS.items():
                if not needed(name):
                    continue
                if page_file.startswith("../site/") and not (EX / page_file).resolve().is_file():
                    print(f"  skipped   {name}: run python scripts/build_site.py first")
                    continue

                def shoot_page(page_file=page_file, w=w, h=h, full=full, name=name) -> bytes:
                    page = browser.new_page(viewport={"width": w, "height": h},
                                            device_scale_factor=1 if name in NATIVE else 2)
                    page.goto(f"{base}/examples/{page_file}", wait_until="networkidle")
                    # Web fonts render as fallbacks if the shot is taken before
                    # they load, and the result looks subtly wrong in a way that
                    # is easy to miss in a thumbnail.
                    page.evaluate("document.fonts.ready")
                    if name in SCROLL:
                        page.evaluate(f"window.scrollTo(0, {SCROLL[name]})")
                        page.wait_for_timeout(200)
                    data = page.screenshot(full_page=full)
                    page.close()
                    return data

                save(name, shoot_page)

            for name, (page_file, index) in SLIDE_SHOTS.items():
                if not needed(name):
                    continue

                def shoot_slide(page_file=page_file, index=index) -> bytes:
                    page = browser.new_page(viewport={"width": 1280, "height": 760},
                                            device_scale_factor=2)
                    page.goto(f"{base}/examples/{page_file}", wait_until="networkidle")
                    page.evaluate("document.fonts.ready")
                    slide = page.locator("section.slide").nth(index)
                    slide.scroll_into_view_if_needed()
                    page.wait_for_timeout(200)
                    data = slide.screenshot()
                    page.close()
                    return data

                save(name, shoot_slide)

            browser.close()
    finally:
        httpd.shutdown()

    summary = ", ".join(f"{n} {state}" for state, n in sorted(states.items())) or "nothing"
    print(f"\n{summary} in {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
