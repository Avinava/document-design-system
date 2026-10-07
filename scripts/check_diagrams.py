#!/usr/bin/env python3
"""Check SVG figures against the diagram markup and geometry contract.

    python3 scripts/check_diagrams.py                  # the repository's figures
    python3 scripts/check_diagrams.py figure.svg ...   # specific files
    python3 scripts/check_diagrams.py page.html        # every titled inline <svg>

Reads coordinates; renders nothing. Each finding names a stable rule ID, so a
fixture, a CI log, and a reviewer all point at the same rule:

    parse            the file is not well-formed SVG, or declares a DOCTYPE/entity
    shell-viewbox    the root has a usable viewBox
    shell-title      <title> with an id is the first child
    shell-desc       a <desc> with an id follows
    shell-labelledby role="img" and aria-labelledby naming the title and desc
    shell-id-prefix  every id starts with the figure's slug (the title id stem)
    shell-fixed-size the root carries no pixel width or height (percent is fine)
    color-var        every colour is a var(--…) reference, never a literal
    markup           structure is marked: g.node, path.edge, g.edge-label, …
    grid             rect geometry sits on the 4px grid
    node-overlap     node boxes do not overlap
    bounds           nothing falls outside the viewBox (text at 0.6em per char)
    label-occluded   no node painted after an edge label covers its backing
    label-gap        an edge label sits at least 6px clear of its edge
    attach-spacing   attachment points on one node side are at least 12px apart
    legend-font      legend text is at least 11px
    accent-family    at most one emphasis family (accent, positive, warning, …)
    callout-count    at most two callouts

Hand-authored diagrams get every rule. Output of scripts/render_diagram.mjs and
scripts/render_chart.mjs (marked data-renderer on the root) gets the shell and
bounds rules only: the renderer owns its layout. Inline <svg> in HTML is
checked when it carries a <title> (it presents itself as a figure) and is not
a copy of a file already being checked; one without the markup contract gets
the shell and bounds rules.

Exit status 1 when any rule fails. Standard library only.
"""

from __future__ import annotations

import argparse
import html.parser
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SVG_NS = "http://www.w3.org/2000/svg"

RULES = (
    "parse",
    "shell-viewbox",
    "shell-title",
    "shell-desc",
    "shell-labelledby",
    "shell-id-prefix",
    "shell-fixed-size",
    "color-var",
    "markup",
    "grid",
    "node-overlap",
    "bounds",
    "label-occluded",
    "label-gap",
    "attach-spacing",
    "legend-font",
    "accent-family",
    "callout-count",
)

# Rules a renderer's own layout is exempt from.
RENDERED_RULES = {
    "parse", "shell-viewbox", "shell-title", "shell-desc", "shell-labelledby",
    "shell-id-prefix", "shell-fixed-size", "bounds",
}

# Classes a top-level group may carry under the markup contract.
CONTRACT_GROUPS = {"node", "edge-label", "boundary", "legend", "callout", "annotation"}
NON_DRAWING = {"title", "desc", "defs", "style", "metadata"}

GRID = 4
CHAR_EM = 0.6           # conservative average advance per character
ASCENT, DESCENT = 0.8, 0.25
MIN_LABEL_GAP = 6
MIN_ATTACH_GAP = 12
ATTACH_TOLERANCE = 2
MIN_LEGEND_FONT = 11
MAX_CALLOUTS = 2
BOUNDS_TOLERANCE = 0.5

COLOR_ATTRS = ("fill", "stroke", "stop-color", "flood-color", "lighting-color", "color")
COLOR_KEYWORDS = {"none", "transparent", "currentcolor", "inherit"}
LITERAL_COLOR_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(", re.I)
VAR_RE = re.compile(r"var\(\s*--([a-z0-9-]+)")
EMPHASIS_FAMILIES = {
    "accent": ("accent",),
    "positive": ("positive",),
    "warning": ("warning",),
    "critical": ("critical",),
    "method": ("method",),
}
NUM_RE = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


@dataclass
class Finding:
    source: str
    rule: str
    message: str

    def __str__(self) -> str:
        return f"{self.source}: {self.rule}: {self.message}"


@dataclass
class Box:
    x0: float
    y0: float
    x1: float
    y1: float

    def overlaps(self, other: "Box") -> bool:
        return (
            min(self.x1, other.x1) - max(self.x0, other.x0) > 0
            and min(self.y1, other.y1) - max(self.y0, other.y0) > 0
        )

    def distance_to_segment(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        """Shortest distance from this box to the segment a–b (0 if they touch)."""
        if _segment_hits_box(a, b, self):
            return 0.0
        corners = [(self.x0, self.y0), (self.x1, self.y0), (self.x1, self.y1), (self.x0, self.y1)]
        best = min(_point_segment(c, a, b) for c in corners)
        for p in (a, b):
            dx = max(self.x0 - p[0], 0, p[0] - self.x1)
            dy = max(self.y0 - p[1], 0, p[1] - self.y1)
            best = min(best, math.hypot(dx, dy))
        return best

    def __str__(self) -> str:
        return f"({_fmt(self.x0)},{_fmt(self.y0)})–({_fmt(self.x1)},{_fmt(self.y1)})"


def _fmt(v: float) -> str:
    return f"{v:g}" if abs(v - round(v)) > 1e-6 else str(int(round(v)))


def _point_segment(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(p[0] - ax, p[1] - ay)
    t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (ay + t * dy))


def _segment_hits_box(a, b, box: Box) -> bool:
    """Liang–Barsky clip: does segment a–b enter the box?"""
    x0, y0 = a
    dx, dy = b[0] - x0, b[1] - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - box.x0), (dx, box.x1 - x0), (-dy, y0 - box.y0), (dy, box.y1 - y0)):
        if p == 0:
            if q < 0:
                return False
            continue
        t = q / p
        if p < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return False
    return True


# ------------------------------------------------------------------ parsing


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def classes(el: ET.Element) -> set[str]:
    return set(el.get("class", "").split())


def num(value: str | None, default: float = 0.0, font_size: float = 16.0) -> float:
    if value is None or value == "":
        return default
    value = value.strip()
    m = NUM_RE.match(value)
    if not m:
        return default
    n = float(m.group(0))
    if value.endswith("em"):
        return n * font_size
    return n


def style_map(el: ET.Element) -> dict[str, str]:
    out: dict[str, str] = {}
    for decl in el.get("style", "").split(";"):
        if ":" in decl:
            k, v = decl.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def prop(el: ET.Element, name: str) -> str | None:
    styles = style_map(el)
    if name in styles:
        return styles[name]
    return el.get(name)


def parse_svg(text: str) -> ET.Element:
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.I):
        raise ValueError("DOCTYPE and entity declarations are refused")
    root = ET.fromstring(text)
    if local(root.tag) != "svg":
        raise ValueError(f"root element is <{local(root.tag)}>, not <svg>")
    return root


def renderer(root: ET.Element) -> str | None:
    return root.get("data-renderer")


# ------------------------------------------------------------- geometry walk


@dataclass
class Item:
    el: ET.Element
    box: Box | None
    kind: str                  # rect | text | path | line | shape
    points: list[tuple[float, float]]
    font_size: float
    groups: tuple[ET.Element, ...]


def _path_points(d: str) -> list[list[tuple[float, float]]]:
    """Flatten a path into polylines (curves sampled), absolute coordinates."""
    tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|" + NUM_RE.pattern, d)
    polylines: list[list[tuple[float, float]]] = []
    cur: list[tuple[float, float]] = []
    x = y = sx = sy = 0.0
    cmd = ""
    i = 0

    def take(n: int) -> list[float]:
        nonlocal i
        vals = [float(t) for t in tokens[i : i + n]]
        i += n
        return vals

    def sample_bezier(p0, ctrl, p3, steps=8):
        pts = []
        for k in range(1, steps + 1):
            t = k / steps
            if len(ctrl) == 1:
                (c,) = ctrl
                px = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p3[0]
                py = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p3[1]
            else:
                c1, c2 = ctrl
                px = ((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * c1[0]
                      + 3 * (1 - t) * t * t * c2[0] + t ** 3 * p3[0])
                py = ((1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * c1[1]
                      + 3 * (1 - t) * t * t * c2[1] + t ** 3 * p3[1])
            pts.append((px, py))
        return pts

    while i < len(tokens):
        tok = tokens[i]
        if re.fullmatch(r"[A-Za-z]", tok):
            cmd = tok
            i += 1
            if cmd in "Zz":
                if cur:
                    cur.append((sx, sy))
                x, y = sx, sy
                continue
        elif not cmd:
            break
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = (x, y) if rel else (0.0, 0.0)
        if c == "M":
            nx, ny = take(2)
            x, y = nx + ox, ny + oy
            if cur:
                polylines.append(cur)
            cur = [(x, y)]
            sx, sy = x, y
            cmd = "l" if rel else "L"
        elif c == "L" or c == "T":
            nx, ny = take(2)
            x, y = nx + ox, ny + oy
            cur.append((x, y))
        elif c == "H":
            (nx,) = take(1)
            x = nx + ox
            cur.append((x, y))
        elif c == "V":
            (ny,) = take(1)
            y = ny + (y if rel else 0.0)
            cur.append((x, y))
        elif c == "Q":
            cx, cy, nx, ny = take(4)
            p3 = (nx + ox, ny + oy)
            cur.extend(sample_bezier((x, y), [(cx + ox, cy + oy)], p3))
            x, y = p3
        elif c == "S":
            cx, cy, nx, ny = take(4)
            p3 = (nx + ox, ny + oy)
            cur.extend(sample_bezier((x, y), [(x, y), (cx + ox, cy + oy)], p3))
            x, y = p3
        elif c == "C":
            c1x, c1y, c2x, c2y, nx, ny = take(6)
            p3 = (nx + ox, ny + oy)
            cur.extend(sample_bezier((x, y), [(c1x + ox, c1y + oy), (c2x + ox, c2y + oy)], p3))
            x, y = p3
        elif c == "A":
            vals = take(7)
            if len(vals) < 7:
                break
            p3 = (vals[5] + ox, vals[6] + oy)
            # An arc's bulge is bounded by its radius; include the midpoint
            # pushed out by the larger radius so bounds stay conservative.
            r = max(abs(vals[0]), abs(vals[1]))
            mx, my = (x + p3[0]) / 2, (y + p3[1]) / 2
            cur.extend([(mx, my - r), (mx, my + r), p3] if abs(p3[1] - y) < 1e-9 else [p3])
            x, y = p3
        else:
            break
    if cur:
        polylines.append(cur)
    return polylines


def _translate(el: ET.Element) -> tuple[float, float] | None:
    """(dx, dy) for a translate-only transform, None for anything else."""
    t = el.get("transform")
    if not t:
        return (0.0, 0.0)
    m = re.fullmatch(r"\s*translate\(\s*([^,\s)]+)(?:[\s,]+([^,\s)]+))?\s*\)\s*", t)
    if not m:
        return None
    return float(m.group(1)), float(m.group(2) or 0)


def _text_lines(el: ET.Element, x: float, y: float, fs: float):
    """Yield (x, baseline_y, chars, anchor_el) per positioned line of a text element."""
    tspans = [c for c in el if local(c.tag) == "tspan"]
    head = (el.text or "").strip()
    if head or not tspans:
        yield x, y, head, el
    cy = y
    for ts in tspans:
        tx = num(ts.get("x"), x, fs) + num(ts.get("dx"), 0, fs)
        if ts.get("y") is not None:
            cy = num(ts.get("y"), cy, fs)
        cy += num(ts.get("dy"), 0, fs)
        content = "".join(ts.itertext()).strip()
        if content:
            yield tx, cy, content, ts


def walk(root: ET.Element) -> list[Item]:
    items: list[Item] = []

    def visit(el, ox, oy, fs, anchor, groups):
        tag = local(el.tag)
        if tag in NON_DRAWING or tag in {"marker", "clipPath", "mask", "pattern", "symbol"}:
            return
        shift = _translate(el)
        if shift is None:          # rotate / scale / matrix: not estimated
            return
        ox, oy = ox + shift[0], oy + shift[1]
        fs = num(prop(el, "font-size"), fs, fs)
        anchor = prop(el, "text-anchor") or anchor
        if tag == "rect":
            x = num(el.get("x")) + ox
            y = num(el.get("y")) + oy
            w, h = num(el.get("width")), num(el.get("height"))
            items.append(Item(el, Box(x, y, x + w, y + h), "rect", [], fs, groups))
        elif tag == "text":
            x = num(el.get("x"), 0, fs) + num(el.get("dx"), 0, fs) + ox
            y = num(el.get("y"), 0, fs) + num(el.get("dy"), 0, fs) + oy
            for lx, ly, chars, line_el in _text_lines(el, x, y, fs):
                lfs = num(prop(line_el, "font-size"), fs, fs)
                spacing = num(prop(line_el, "letter-spacing") or prop(el, "letter-spacing"), 0, lfs)
                width = len(chars) * (CHAR_EM * lfs + spacing)
                line_anchor = prop(line_el, "text-anchor") or anchor
                if line_anchor == "middle":
                    x0 = lx - width / 2
                elif line_anchor == "end":
                    x0 = lx - width
                else:
                    x0 = lx
                box = Box(x0, ly - ASCENT * lfs, x0 + width, ly + DESCENT * lfs)
                items.append(Item(line_el, box, "text", [], lfs, groups))
            return
        elif tag in {"path", "line", "polyline", "polygon", "circle", "ellipse"}:
            lines: list[list[tuple[float, float]]] = []
            if tag == "path":
                lines = _path_points(el.get("d", ""))
            elif tag == "line":
                lines = [[(num(el.get("x1")), num(el.get("y1"))), (num(el.get("x2")), num(el.get("y2")))]]
            elif tag in {"polyline", "polygon"}:
                vals = [float(v) for v in NUM_RE.findall(el.get("points", ""))]
                lines = [list(zip(vals[0::2], vals[1::2]))]
            else:
                cx, cy = num(el.get("cx")), num(el.get("cy"))
                rx = num(el.get("r") or el.get("rx"))
                ry = num(el.get("r") or el.get("ry"))
                lines = [[(cx - rx, cy - ry), (cx + rx, cy + ry)]]
            lines = [[(px + ox, py + oy) for px, py in line] for line in lines if line]
            pts = [p for line in lines for p in line]
            if pts:
                box = Box(min(p[0] for p in pts), min(p[1] for p in pts),
                          max(p[0] for p in pts), max(p[1] for p in pts))
                kind = "path" if tag in {"path", "line", "polyline"} else "shape"
                item = Item(el, box, kind, pts, fs, groups)
                item.polylines = lines  # type: ignore[attr-defined]
                items.append(item)
            return
        for child in el:
            visit(child, ox, oy, fs, anchor, groups + ((child,) if local(child.tag) == "g" else ()))

    root_fs = num(prop(root, "font-size"), 16.0)
    for child in root:
        visit(child, 0.0, 0.0, root_fs, prop(root, "text-anchor") or "start",
              (child,) if local(child.tag) == "g" else ())
    return items


# ------------------------------------------------------------------- rules


class Checker:
    def __init__(self, source: str, root: ET.Element, full: bool):
        self.source = source
        self.root = root
        self.full = full
        self.findings: list[Finding] = []

    def fail(self, rule: str, message: str) -> None:
        if not self.full and rule not in RENDERED_RULES:
            return
        self.findings.append(Finding(self.source, rule, message))

    # --- shell

    def viewbox(self) -> tuple[float, float, float, float] | None:
        raw = self.root.get("viewBox")
        if raw is None:
            self.fail("shell-viewbox", "root <svg> has no viewBox")
            return None
        vals = NUM_RE.findall(raw)
        if len(vals) != 4 or float(vals[2]) <= 0 or float(vals[3]) <= 0:
            self.fail("shell-viewbox", f"viewBox {raw!r} is not four numbers with positive size")
            return None
        return tuple(float(v) for v in vals)  # type: ignore[return-value]

    def shell(self) -> None:
        children = [c for c in self.root if isinstance(c.tag, str)]
        title = children[0] if children and local(children[0].tag) == "title" else None
        if title is None or not title.get("id"):
            self.fail("shell-title", "the first child must be a <title> with an id")
        descs = [c for c in children if local(c.tag) == "desc"]
        desc = descs[0] if descs else None
        if desc is None or not desc.get("id") or not "".join(desc.itertext()).strip():
            self.fail("shell-desc", "needs a non-empty <desc> with an id stating what the arrangement shows")

        labelled = self.root.get("aria-labelledby", "").split()
        wanted = [e.get("id") for e in (title, desc) if e is not None and e.get("id")]
        if self.root.get("role") != "img" or not wanted or any(w not in labelled for w in wanted):
            self.fail("shell-labelledby", 'root needs role="img" and aria-labelledby naming the title and desc ids')

        if title is not None and title.get("id"):
            tid = title.get("id")
            prefix = tid[: -len("-title")] if tid.endswith("-title") else tid
            for el in self.root.iter():
                eid = el.get("id")
                if eid and eid != prefix and not eid.startswith(prefix + "-"):
                    self.fail("shell-id-prefix", f'id "{eid}" does not start with the figure slug "{prefix}-"')

        for dim in ("width", "height"):
            value = self.root.get(dim)
            if value is not None and not value.strip().endswith("%"):
                self.fail("shell-fixed-size", f'root {dim}="{value}" fixes the size; keep the viewBox and use width="100%"')

    # --- colour

    def colors(self) -> None:
        for el in self.root.iter():
            tag = local(el.tag)
            if tag == "style":
                if LITERAL_COLOR_RE.search(el.text or ""):
                    self.fail("color-var", "<style> contains a literal colour")
                continue
            for name in COLOR_ATTRS:
                value = prop(el, name)
                if value is None:
                    continue
                v = value.strip()
                if v.lower() in COLOR_KEYWORDS or v.startswith("url(#") or v.startswith("var(--"):
                    continue
                self.fail("color-var", f'<{tag}> {name}="{v}" is a literal; use a var(--…) token')

    # --- markup contract

    def markup(self) -> None:
        for child in self.root:
            if not isinstance(child.tag, str):
                continue
            tag = local(child.tag)
            if tag in NON_DRAWING:
                continue
            cls = classes(child)
            if tag in {"path", "line"} and "edge" in cls:
                continue
            if tag == "g" and cls & CONTRACT_GROUPS:
                continue
            what = f'<{tag} class="{child.get("class")}">' if child.get("class") else f"<{tag}>"
            self.fail("markup", f"top-level {what} is unmarked; wrap it in g.node, g.edge-label, "
                      "g.boundary, g.legend, g.callout or g.annotation, or class it path.edge")
        for g in self.root.iter():
            cls = classes(g)
            kids = [local(c.tag) for c in g if isinstance(c.tag, str)]
            if local(g.tag) == "g" and "node" in cls and ("rect" not in kids or "text" not in kids):
                self.fail("markup", "g.node needs its box <rect> and a <text> label")
            if local(g.tag) == "g" and "edge-label" in cls and (
                not kids or kids[0] != "rect" or "text" not in kids
            ):
                self.fail("markup", "g.edge-label needs a backing <rect> first, then its <text>")

    # --- geometry

    def geometry(self, vb, items: list[Item]) -> None:
        vx, vy, vw, vh = vb
        frame = Box(vx, vy, vx + vw, vy + vh)
        t = BOUNDS_TOLERANCE
        for it in items:
            b = it.box
            if b is None:
                continue
            if b.x0 < frame.x0 - t or b.y0 < frame.y0 - t or b.x1 > frame.x1 + t or b.y1 > frame.y1 + t:
                label = "".join(it.el.itertext()).strip() if it.kind == "text" else ""
                what = f'text "{label[:40]}"' if label else f"<{local(it.el.tag)}>"
                self.fail("bounds", f"{what} spans {b}, outside the viewBox {_fmt(vw)}×{_fmt(vh)}")

        if not self.full:
            return

        for it in items:
            if it.kind != "rect":
                continue
            el = it.el
            for attr in ("x", "y", "width", "height"):
                value = num(el.get(attr))
                if abs(value / GRID - round(value / GRID)) > 1e-6:
                    self.fail("grid", f'<rect {attr}="{el.get(attr)}"> is off the {GRID}px grid')

        nodes = self.node_boxes(items)
        for i, (g1, b1) in enumerate(nodes):
            for g2, b2 in nodes[i + 1 :]:
                if b1.overlaps(b2):
                    self.fail("node-overlap", f"node {self.name(g1)} {b1} overlaps node {self.name(g2)} {b2}")

        order = {el: i for i, el in enumerate(self.root.iter())}
        edges = [it for it in items if it.kind == "path" and "edge" in classes(it.el)]
        for label in self.root.iter():
            if local(label.tag) != "g" or "edge-label" not in classes(label):
                continue
            backing = next((it for it in items if it.kind == "rect" and it.el in list(label)), None)
            if backing is None:
                continue
            text = "".join(label.itertext()).strip()
            for g, box in nodes:
                if order[g] > order[label] and box.overlaps(backing.box):
                    self.fail("label-occluded", f'edge label "{text}" is covered by node {self.name(g)} painted after it')
            if edges:
                gap = min(
                    backing.box.distance_to_segment(a, b)
                    for e in edges
                    for line in e.polylines  # type: ignore[attr-defined]
                    for a, b in zip(line, line[1:])
                )
                if gap < MIN_LABEL_GAP:
                    self.fail("label-gap", f'edge label "{text}" is {_fmt(gap)}px from an edge; keep {MIN_LABEL_GAP}px clear')

        self.attachments(nodes, edges)

    def node_boxes(self, items: list[Item]) -> list[tuple[ET.Element, Box]]:
        out = []
        for g in self.root.iter():
            if local(g.tag) == "g" and "node" in classes(g):
                rect = next((it for it in items if it.kind == "rect" and it.el in list(g)), None)
                if rect is not None:
                    out.append((g, rect.box))
        return out

    def attachments(self, nodes, edges) -> None:
        tol = ATTACH_TOLERANCE
        sides: dict[tuple[int, str], list[float]] = {}
        for e in edges:
            for line in e.polylines:  # type: ignore[attr-defined]
                for px, py in (line[0], line[-1]):
                    for idx, (g, b) in enumerate(nodes):
                        if b.y0 - tol <= py <= b.y1 + tol:
                            if abs(px - b.x0) <= tol:
                                sides.setdefault((idx, "left"), []).append(py)
                            elif abs(px - b.x1) <= tol:
                                sides.setdefault((idx, "right"), []).append(py)
                        if b.x0 - tol <= px <= b.x1 + tol:
                            if abs(py - b.y0) <= tol:
                                sides.setdefault((idx, "top"), []).append(px)
                            elif abs(py - b.y1) <= tol:
                                sides.setdefault((idx, "bottom"), []).append(px)
        for (idx, side), coords in sides.items():
            coords.sort()
            for a, b in zip(coords, coords[1:]):
                if b - a < MIN_ATTACH_GAP:
                    self.fail(
                        "attach-spacing",
                        f"node {self.name(nodes[idx][0])} has edges meeting its {side} side "
                        f"{_fmt(b - a)}px apart; fan them at least {MIN_ATTACH_GAP}px apart",
                    )
                    break

    def name(self, g: ET.Element) -> str:
        texts = [t for t in g.iter() if local(t.tag) == "text"]
        label = "".join(texts[0].itertext()).strip() if texts else ""
        return f'"{label}"' if label else "(unlabelled)"

    # --- emphasis

    def emphasis(self, items: list[Item]) -> None:
        for g in self.root.iter():
            if local(g.tag) == "g" and "legend" in classes(g):
                for it in items:
                    if it.kind == "text" and g in it.groups and it.font_size < MIN_LEGEND_FONT:
                        self.fail("legend-font", f'legend text "{"".join(it.el.itertext()).strip()}" is '
                                  f"{_fmt(it.font_size)}px; legends are at least {MIN_LEGEND_FONT}px")
        used: set[str] = set()
        for el in self.root.iter():
            values = [prop(el, a) or "" for a in COLOR_ATTRS]
            for value in values:
                for token in VAR_RE.findall(value):
                    for family, prefixes in EMPHASIS_FAMILIES.items():
                        if any(token == p or token.startswith(p + "-") for p in prefixes):
                            used.add(family)
        if len(used) > 1:
            self.fail("accent-family", f"uses {len(used)} emphasis families ({', '.join(sorted(used))}); "
                      "keep one and carry the rest in labels")
        callouts = sum(1 for g in self.root.iter() if local(g.tag) == "g" and "callout" in classes(g))
        if callouts > MAX_CALLOUTS:
            self.fail("callout-count", f"{callouts} callouts; at most {MAX_CALLOUTS} — a third means too many arguments")

    def run(self) -> list[Finding]:
        vb = self.viewbox()
        self.shell()
        self.colors()
        if self.full:
            self.markup()
        items = walk(self.root)
        if vb is not None:
            self.geometry(vb, items)
        if self.full:
            self.emphasis(items)
        return self.findings


def check_svg(text: str, source: str, *, inline: bool = False) -> list[Finding]:
    try:
        root = parse_svg(text)
    except (ET.ParseError, ValueError) as exc:
        return [Finding(source, "parse", str(exc))]
    full = renderer(root) is None
    if inline and full and not any(
        local(g.tag) == "g" and classes(g) & CONTRACT_GROUPS for g in root.iter()
    ):
        full = False
    return Checker(source, root, full).run()


# ------------------------------------------------------------- html inputs


class _SvgExtractor(html.parser.HTMLParser):
    """Collect the source span of every top-level <svg> outside style/script."""

    def __init__(self, text: str):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0]
        for line in text.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))
        self.depth = 0
        self.start = 0
        self.spans: list[tuple[int, int, int]] = []

    def _pos(self) -> int:
        line, col = self.getpos()
        return self.lines[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag == "svg":
            if self.depth == 0:
                self.start = self._pos()
            self.depth += 1

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag == "svg" and self.depth:
            self.depth -= 1
            if self.depth == 0:
                end = self.text.index(">", self._pos()) + 1
                self.spans.append((self.start, end, self.getpos()[0]))


def inline_svgs(text: str) -> list[tuple[str, int]]:
    parser = _SvgExtractor(text)
    parser.feed(text)
    parser.close()
    out = []
    for start, end, _ in parser.spans:
        chunk = text[start:end]
        if "xmlns=" not in chunk[: chunk.index(">")]:
            chunk = chunk.replace("<svg", f'<svg xmlns="{SVG_NS}"', 1)
        out.append((chunk, text.count("\n", 0, start) + 1))
    return out


def title_id(text: str) -> str | None:
    m = re.search(r"<title\s+id=\"([^\"]+)\"", text)
    return m.group(1) if m else None


# --------------------------------------------------------------------- main


def default_inputs(root: Path) -> list[Path]:
    paths = sorted((root / "examples").glob("*.svg")) + sorted((root / "examples").glob("*.html"))
    template = root / "templates" / "diagram.svg"
    if template.is_file():
        paths.append(template)
    return paths


def template_svg(text: str) -> str:
    """templates/diagram.svg wraps its <svg> in a <figure> and a comment."""
    m = re.search(r"<svg\b.*?</svg>", text, re.S)
    if not m:
        return text
    chunk = m.group(0)
    if "xmlns=" not in chunk[: chunk.index(">")]:
        chunk = chunk.replace("<svg", f'<svg xmlns="{SVG_NS}"', 1)
    return chunk


def check_paths(paths: list[Path], root: Path = ROOT) -> list[Finding]:
    findings: list[Finding] = []
    file_titles: set[str] = set()
    svg_paths = [p for p in paths if p.suffix == ".svg"]
    html_paths = [p for p in paths if p.suffix in {".html", ".htm"}]
    for path in svg_paths:
        text = path.read_text(encoding="utf-8")
        try:
            shown = str(path.resolve().relative_to(root))
        except ValueError:
            shown = str(path)
        if not text.lstrip().startswith("<svg"):
            text = template_svg(text)
        tid = title_id(text)
        if tid:
            file_titles.add(tid)
        findings.extend(check_svg(text, shown))
    for path in html_paths:
        text = path.read_text(encoding="utf-8")
        try:
            shown = str(path.resolve().relative_to(root))
        except ValueError:
            shown = str(path)
        for chunk, line in inline_svgs(text):
            tid = title_id(chunk)
            if tid is None or tid in file_titles:
                continue
            findings.extend(check_svg(chunk, f"{shown}:{line}", inline=True))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check SVG figures against the diagram markup and geometry contract.",
    )
    parser.add_argument("paths", nargs="*", type=Path, help=".svg or .html files (default: the repository's figures)")
    parser.add_argument("--rules", action="store_true", help="list the rule IDs and exit")
    args = parser.parse_args(argv)
    if args.rules:
        print("\n".join(RULES))
        return 0
    paths = args.paths or default_inputs(ROOT)
    missing = [p for p in paths if not p.is_file()]
    if missing:
        print(f"check_diagrams: not a file: {', '.join(map(str, missing))}", file=sys.stderr)
        return 2
    findings = check_paths(paths)
    for f in findings:
        print(f)
    checked = len(paths)
    if findings:
        print(f"\n{len(findings)} finding(s) across {checked} file(s)", file=sys.stderr)
        return 1
    print(f"{checked} file(s) clean", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
