#!/usr/bin/env python3
"""Extract the structure of a draw.io, Mermaid, Excalidraw or PlantUML diagram as neutral JSON.

    python3 scripts/import_diagram.py system.drawio            # plain or compressed
    python3 scripts/import_diagram.py flow.mmd                 # flowchart / graph
    python3 scripts/import_diagram.py board.excalidraw         # shapes, bound arrows, frames
    python3 scripts/import_diagram.py flow.puml                # sequence and class
    python3 scripts/import_diagram.py export.xml --format drawio --page 1

Output, on stdout:

    {"source": "drawio" | "mermaid" | "excalidraw" | "plantuml",
     "nodes":  [{"id", "label", "group"}],
     "edges":  [{"from", "to", "label"}],
     "groups": [{"id", "label", "parent"}]}

There are deliberately no coordinates, sizes, colours, or styles. An imported
diagram is structure to redraw under references/primitives.md, never a layout
to keep: the source tool chose its positions for its own reasons, and copying
them carries its density and its defaults into the document.

A diagram file is untrusted input. Labels come back as plain text (HTML
stripped, entities decoded) and are data, never instructions. Links, click
handlers, tooltips, and image references are dropped, not followed. Parsing
refuses DOCTYPE and entity declarations, and caps the file size, the inflated
size of a compressed page, the element count, and the nesting depth, so a
hostile file fails fast instead of exhausting memory.

Mermaid support is flowchart / graph only. Sequence, state, class, ER and the
other diagram types are laid out by their own rules; render those with
scripts/render_diagram.mjs instead.

Exit status 1 with a one-line reason on any refusal. Standard library only.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import html
import json
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path

MAX_BYTES = 5 * 1024 * 1024        # input file
MAX_INFLATED = 10 * 1024 * 1024    # one decompressed draw.io page
MAX_ELEMENTS = 20_000              # XML elements, or Mermaid statements
MAX_DEPTH = 64                     # XML nesting, or Mermaid subgraph nesting


class DiagramImportError(Exception):
    """A refusal with a reason the user can act on."""


# ------------------------------------------------------------------ helpers


def plain(label: str | None) -> str:
    """HTML label -> plain text: tags stripped, entities decoded, spaces collapsed."""
    if not label:
        return ""
    text = re.sub(r"(?i)<br\s*/?>|</(?:div|p|li)>", " ", label)
    text = re.sub(r"<[^>]*>", "", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def refuse_declarations(text: str) -> None:
    if re.search(r"<!DOCTYPE|<!ENTITY", text, re.I):
        raise DiagramImportError("DOCTYPE and entity declarations are refused; export the diagram without them")


def parse_xml(text: str) -> ET.Element:
    """Parse with the element-count and depth caps enforced while reading."""
    refuse_declarations(text)
    parser = ET.XMLPullParser(events=("start", "end"))
    depth = count = 0
    root = None
    try:
        for i in range(0, len(text), 65536):
            parser.feed(text[i : i + 65536])
            for event, el in parser.read_events():
                if event == "start":
                    depth += 1
                    count += 1
                    if root is None:
                        root = el
                    if depth > MAX_DEPTH:
                        raise DiagramImportError(f"nesting deeper than {MAX_DEPTH} levels")
                    if count > MAX_ELEMENTS:
                        raise DiagramImportError(f"more than {MAX_ELEMENTS} elements")
                else:
                    depth -= 1
        parser.close()
    except ET.ParseError as exc:
        raise DiagramImportError(f"not well-formed XML: {exc}") from None
    if root is None:
        raise DiagramImportError("empty document")
    return root


def inflate(payload: str) -> str:
    """draw.io page compression: base64 -> raw deflate -> URL-encoded XML."""
    try:
        raw = base64.b64decode(payload.strip(), validate=True)
    except (binascii.Error, ValueError):
        raise DiagramImportError("compressed page is not valid base64") from None
    d = zlib.decompressobj(-zlib.MAX_WBITS)
    try:
        out = d.decompress(raw, MAX_INFLATED + 1)
    except zlib.error as exc:
        raise DiagramImportError(f"compressed page does not inflate: {exc}") from None
    if len(out) > MAX_INFLATED or d.unconsumed_tail:
        raise DiagramImportError(f"compressed page inflates past {MAX_INFLATED // (1024 * 1024)} MB")
    return urllib.parse.unquote(out.decode("utf-8", errors="replace"))


def finish(source: str, nodes: dict, edges: list, groups: dict) -> dict:
    for e in edges:
        missing = [end for end in (e["from"], e["to"]) if end not in nodes and end not in groups]
        if missing:
            raise DiagramImportError(
                f"edge {e['from']} -> {e['to']} points at {', '.join(missing)}, which does not exist; "
                "connect or delete the floating edge in the source"
            )
    return {
        "source": source,
        "nodes": list(nodes.values()),
        "edges": edges,
        "groups": list(groups.values()),
    }


# ------------------------------------------------------------------ draw.io


def _cells(model: ET.Element) -> list[tuple[ET.Element, dict[str, str]]]:
    """mxCell elements with their effective attributes.

    A cell wrapped in <UserObject> or <object> takes its id and label from the
    wrapper; any other wrapper attributes (links, tooltips, placeholders) are
    ignored.
    """
    root = model.find("root")
    if root is None:
        raise DiagramImportError("mxGraphModel has no <root>")
    out = []
    for child in root:
        if child.tag == "mxCell":
            out.append((child, dict(child.attrib)))
        elif child.tag in {"UserObject", "object"}:
            cell = child.find("mxCell")
            if cell is None:
                continue
            attrs = dict(cell.attrib)
            attrs["id"] = child.get("id", attrs.get("id", ""))
            attrs["value"] = child.get("label", attrs.get("value", ""))
            out.append((cell, attrs))
    return out


def _model(root: ET.Element, page: int) -> ET.Element:
    if root.tag == "mxGraphModel":
        return root
    if root.tag != "mxfile":
        raise DiagramImportError(f"expected <mxfile> or <mxGraphModel>, found <{root.tag}>")
    diagrams = root.findall("diagram")
    if not diagrams:
        raise DiagramImportError("mxfile has no <diagram> pages")
    if not 0 <= page < len(diagrams):
        raise DiagramImportError(f"page {page} does not exist; the file has {len(diagrams)}")
    diagram = diagrams[page]
    model = diagram.find("mxGraphModel")
    if model is not None:
        return model
    payload = (diagram.text or "").strip()
    if not payload:
        raise DiagramImportError("diagram page is empty")
    inner = parse_xml(inflate(payload))
    if inner.tag != "mxGraphModel":
        raise DiagramImportError(f"compressed page holds <{inner.tag}>, not <mxGraphModel>")
    return inner


def import_drawio(text: str, page: int = 0) -> dict:
    model = _model(parse_xml(text), page)
    cells = _cells(model)

    seen: set[str] = set()
    for _, a in cells:
        cid = a.get("id", "")
        if not cid:
            raise DiagramImportError("a cell has no id")
        if cid in seen:
            raise DiagramImportError(f"duplicate cell id {cid!r}; ids must be unique to keep edges unambiguous")
        seen.add(cid)

    by_id = {a["id"]: a for _, a in cells}
    # Layer cells (the root and its children) carry no vertex/edge flag, so
    # they never become nodes, and nothing that sits on a layer gets a group.
    vertices = {cid for cid, a in by_id.items() if a.get("vertex") == "1"}
    edge_ids = {cid for cid, a in by_id.items() if a.get("edge") == "1"}

    # A vertex is a group when its style says so or another vertex sits in it.
    contains = {a.get("parent") for cid, a in by_id.items() if cid in vertices}
    groups: dict[str, dict] = {}
    for cid in (c for c in by_id if c in vertices):  # document order
        style = by_id[cid].get("style", "")
        if cid in contains or re.search(r"(?:^|;)(?:group|swimlane|container=1)", style):
            groups[cid] = {"id": cid, "label": plain(by_id[cid].get("value")), "parent": None}

    def owner(cid: str) -> str | None:
        parent = by_id.get(cid, {}).get("parent")
        return parent if parent in groups else None

    for gid in groups:
        groups[gid]["parent"] = owner(gid)

    nodes: dict[str, dict] = {}
    edge_labels: dict[str, list[str]] = {}
    for cid in (c for c in by_id if c in vertices and c not in groups):
        a = by_id[cid]
        parent = a.get("parent")
        # Edge labels are vertices parented to their edge.
        if parent in edge_ids or "edgeLabel" in a.get("style", ""):
            if parent in edge_ids and plain(a.get("value")):
                edge_labels.setdefault(parent, []).append(plain(a.get("value")))
            continue
        nodes[cid] = {"id": cid, "label": plain(a.get("value")), "group": owner(cid)}

    edges = []
    for cid in (c for c in by_id if c in edge_ids):
        a = by_id[cid]
        src, dst = a.get("source"), a.get("target")
        if not src or not dst:
            raise DiagramImportError(f"edge {cid!r} is not connected at both ends; connect or delete it in the source")
        label = " ".join([plain(a.get("value"))] + edge_labels.get(cid, [])).strip()
        edges.append({"from": src, "to": dst, "label": label})

    return finish("drawio", nodes, edges, groups)


# ------------------------------------------------------------------ Mermaid

MERMAID_OTHER = re.compile(
    r"^(sequenceDiagram|classDiagram|stateDiagram(?:-v2)?|erDiagram|gantt|pie|journey|gitGraph|"
    r"mindmap|timeline|quadrantChart|requirementDiagram|C4\w*|sankey(?:-beta)?|xychart(?:-beta)?|"
    r"block(?:-beta)?|packet(?:-beta)?|architecture(?:-beta)?|kanban)\b"
)
HEADER = re.compile(r"^(?:flowchart|graph)(?:\s+(?:TB|TD|BT|RL|LR))?\s*;?\s*$")
# A hyphen belongs to the id unless it starts a link (A-->B, A-.->B).
NODE_ID = re.compile(r"[A-Za-z0-9_](?:\w|-(?![-.=>]))*")
# Openers in longest-first order, each with its closer.
SHAPES = [
    ("(((", ")))"), ("([", "])"), ("[[", "]]"), ("[(", ")]"), ("((", "))"), ("{{", "}}"),
    ("[/", "/]"), ("[/", "\\]"), ("[\\", "\\]"), ("[\\", "/]"),
    ("[", "]"), ("(", ")"), ("{", "}"), (">", "]"),
]
# Link operators: optional start head, a line of -, =, or dotted, optional end head.
LINK = re.compile(r"\s*(?:[<ox])?(?:-{2,}|={2,}|-\.+-|~{3,})(?:[>ox])?")
LINK_TEXT = re.compile(r"\s*(?:[<ox])?(--|==|-\.)\s*(?!>)([^\n]*?)\s*(-{2,}[>ox]?|={2,}[>ox]?|\.-+[>ox]?)")
PIPE = re.compile(r"\s*\|([^|]*)\|")
IGNORED = re.compile(r"^(?:classDef|class|style|linkStyle|click|direction|accTitle|accDescr|%%)\b")


def _strip_quotes(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1]
    if len(text) >= 2 and text[0] == text[-1] == "`":
        text = text[1:-1]
    return plain(text)


def _node(stmt: str, i: int) -> tuple[str, str | None, int]:
    """Parse `id` plus an optional shape at stmt[i]. Returns (id, label|None, next)."""
    m = NODE_ID.match(stmt, i)
    if not m:
        raise DiagramImportError(f"expected a node id at: {stmt[i:i + 40]!r}")
    nid, j = m.group(0), m.end()
    for opener, closer in SHAPES:
        if stmt.startswith(opener, j):
            k = j + len(opener)
            if stmt.startswith('"', k):
                q = stmt.find('"', k + 1)
                end = stmt.find(closer, q + 1) if q != -1 else -1
            else:
                end = stmt.find(closer, k)
            if end == -1:
                continue
            return nid, _strip_quotes(stmt[k:end]), _skip_class(stmt, end + len(closer))
    return nid, None, _skip_class(stmt, j)


def _skip_class(stmt: str, i: int) -> int:
    """Skip a `:::className` suffix; styling is not structure."""
    m = re.compile(r":::[\w-]+").match(stmt, i)
    return m.end() if m else i


def _link(stmt: str, i: int) -> tuple[str, int] | None:
    """Parse a link at stmt[i]. Returns (label, next) or None."""
    m = LINK_TEXT.match(stmt, i)
    if m and m.group(2) and not m.group(2).startswith(("-", "=", ">")):
        return _strip_quotes(m.group(2)), m.end()
    m = LINK.match(stmt, i)
    if not m:
        return None
    j = m.end()
    p = PIPE.match(stmt, j)
    if p:
        return _strip_quotes(p.group(1)), p.end()
    return "", j


def _statements(text: str) -> list[str]:
    out = []
    for line in text.splitlines():
        line = re.sub(r"%%.*$", "", line).strip()
        if not line:
            continue
        # Semicolons separate statements, except inside a quoted label.
        out.extend(s.strip() for s in re.split(r';(?=(?:[^"]*"[^"]*")*[^"]*$)', line) if s.strip())
    return out


def import_mermaid(text: str) -> dict:
    stmts = _statements(text)
    if not stmts:
        raise DiagramImportError("empty Mermaid source")
    head = stmts[0]
    other = MERMAID_OTHER.match(head)
    if other:
        raise DiagramImportError(
            f"{other.group(1)} is not supported: only flowchart / graph structure is imported. "
            "Render it with scripts/render_diagram.mjs instead."
        )
    if not HEADER.match(head):
        raise DiagramImportError(f"not a Mermaid flowchart: first statement is {head[:40]!r}")
    if len(stmts) > MAX_ELEMENTS:
        raise DiagramImportError(f"more than {MAX_ELEMENTS} statements")

    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    groups: dict[str, dict] = {}
    stack: list[str] = []

    def touch(nid: str, label: str | None) -> None:
        if nid in groups:
            return
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": label if label is not None else nid,
                          "group": stack[-1] if stack else None}
        elif label is not None:
            nodes[nid]["label"] = label

    for stmt in stmts[1:]:
        if IGNORED.match(stmt):
            continue
        if stmt == "end":
            if not stack:
                raise DiagramImportError("'end' without a matching subgraph")
            stack.pop()
            continue
        sub = re.match(r"^subgraph\s+(.+)$", stmt)
        if sub:
            body = sub.group(1).strip()
            m = re.match(r"^([A-Za-z0-9_][\w-]*)\s*\[(.*)\]$", body)
            gid, label = (m.group(1), _strip_quotes(m.group(2))) if m else (None, _strip_quotes(body))
            if gid is None:
                gid = body if NODE_ID.fullmatch(body) else f"subgraph-{len(groups) + 1}"
            if gid in groups:
                raise DiagramImportError(f"duplicate subgraph id {gid!r}")
            if gid in nodes:
                raise DiagramImportError(f"subgraph id {gid!r} is already a node id")
            groups[gid] = {"id": gid, "label": label, "parent": stack[-1] if stack else None}
            stack.append(gid)
            if len(stack) > MAX_DEPTH:
                raise DiagramImportError(f"subgraphs nested deeper than {MAX_DEPTH} levels")
            continue

        # node-group (link node-group)*, where a node-group is `a & b & c`.
        i, previous = 0, None
        while True:
            current = []
            while True:
                while i < len(stmt) and stmt[i] == " ":
                    i += 1
                nid, label, i = _node(stmt, i)
                touch(nid, label)
                current.append(nid)
                amp = re.compile(r"\s*&\s*").match(stmt, i)
                if not amp:
                    break
                i = amp.end()
            if previous is not None:
                for a in previous[0]:
                    for b in current:
                        edges.append({"from": a, "to": b, "label": previous[1]})
            rest = stmt[i:].strip()
            if not rest:
                break
            link = _link(stmt, i)
            if link is None:
                raise DiagramImportError(f"cannot read statement near: {stmt[i:i + 40]!r}")
            previous = (current, link[0])
            i = link[1]
    if stack:
        raise DiagramImportError(f"subgraph {stack[-1]!r} is never closed with 'end'")
    return finish("mermaid", nodes, edges, groups)


# --------------------------------------------------------------- Excalidraw

EXCALIDRAW_NODES = {"rectangle", "ellipse", "diamond", "embeddable", "image"}
EXCALIDRAW_LINKS = {"arrow", "line"}


def import_excalidraw(text: str) -> dict:
    """Shapes become nodes, bound arrows become edges, frames become groups.

    A label is the text element bound to its shape or arrow (`containerId`).
    Free-standing text, freehand strokes, links, and styling are dropped.
    """
    try:
        doc = json.loads(text)
    except (json.JSONDecodeError, RecursionError):
        raise DiagramImportError("not valid JSON (or nested too deeply to read)") from None
    elements = doc.get("elements") if isinstance(doc, dict) else None
    if not isinstance(elements, list):
        raise DiagramImportError('not an Excalidraw scene: expected an object with an "elements" list')
    if len(elements) > MAX_ELEMENTS:
        raise DiagramImportError(f"more than {MAX_ELEMENTS} elements")

    live: list[dict] = []
    seen: set[str] = set()
    for el in elements:
        if not isinstance(el, dict) or not isinstance(el.get("id"), str) or not el["id"]:
            raise DiagramImportError("an element has no string id")
        if el["id"] in seen:
            raise DiagramImportError(f"duplicate element id {el['id']!r}; ids must be unique to keep edges unambiguous")
        seen.add(el["id"])
        if not el.get("isDeleted"):
            live.append(el)

    by_id = {el["id"]: el for el in live}
    bound_text: dict[str, list[str]] = {}
    for el in live:
        container = el.get("containerId")
        if el.get("type") == "text" and isinstance(container, str) and container in by_id:
            label = plain(el.get("text") if isinstance(el.get("text"), str) else "")
            if label:
                bound_text.setdefault(container, []).append(label)

    def label_of(eid: str) -> str:
        return " ".join(bound_text.get(eid, []))

    groups: dict[str, dict] = {}
    for el in live:
        if el.get("type") == "frame":
            name = el.get("name")
            groups[el["id"]] = {"id": el["id"], "label": plain(name if isinstance(name, str) else ""), "parent": None}

    def frame_of(el: dict) -> str | None:
        frame = el.get("frameId")
        return frame if frame in groups else None

    nodes: dict[str, dict] = {}
    for el in live:
        if el.get("type") in EXCALIDRAW_NODES:
            nodes[el["id"]] = {"id": el["id"], "label": label_of(el["id"]), "group": frame_of(el)}

    edges: list[dict] = []
    for el in live:
        if el.get("type") not in EXCALIDRAW_LINKS:
            continue
        ends = []
        for key in ("startBinding", "endBinding"):
            binding = el.get(key)
            ends.append(binding.get("elementId") if isinstance(binding, dict) else None)
        if not all(isinstance(e, str) for e in ends):
            if el["type"] == "line":
                continue  # a plain line is decoration; only arrows carry meaning
            raise DiagramImportError(
                f"arrow {el['id']!r} is not bound to a shape at both ends; connect or delete it in the source"
            )
        edges.append({"from": ends[0], "to": ends[1], "label": label_of(el["id"])})
    return finish("excalidraw", nodes, edges, groups)


# ----------------------------------------------------------------- PlantUML

PLANT_NAME = r'"[^"\n]+"|[A-Za-z_][\w.]*'
PLANT_DECL = re.compile(
    rf"^(?P<kind>participant|actor|boundary|control|entity|database|collections|queue|"
    rf"abstract\s+class|abstract|class|interface|enum|annotation)\s+"
    rf"(?P<name>{PLANT_NAME})(?:\s+as\s+(?P<alias>[\w.]+))?(?P<rest>.*)$"
)
PLANT_SEQ_KINDS = {"participant", "actor", "boundary", "control", "entity", "database", "collections", "queue"}
PLANT_SEQ_MSG = re.compile(
    rf"^(?P<a>{PLANT_NAME})\s*(?P<arrow><{{0,2}}[\\/ox]?-{{1,2}}(?:\[[^\]\n]*\])?-{{0,2}}[\\/ox]?>{{0,2}})\s*"
    rf"(?P<b>{PLANT_NAME})\s*(?::\s*(?P<label>.*))?$"
)
PLANT_REL = re.compile(
    rf"^(?P<a>{PLANT_NAME})\s*(?:\"[^\"\n]*\"\s*)?(?P<arrow>(?:<\|?|\*|o|\+|#|\^|\}})?(?:-+|\.+)"
    rf"(?:\[[^\]\n]*\])?(?:-*|\.*)(?:\|>|>|\*|o|\+|#|\^)?)\s*(?:\"[^\"\n]*\"\s*)?"
    rf"(?P<b>{PLANT_NAME})\s*(?::\s*(?P<label>.*))?$"
)
PLANT_IGNORED = re.compile(
    r"^(?:(?:title|header|footer|skinparam|hide|show|autonumber|activate|deactivate|destroy|"
    r"return|create|newpage|ref|set|scale)\b|left to right direction|top to bottom direction|"
    r"==.*==|\.\.\..*|\|\|\||\|\|\d+\|\|)"
)
PLANT_BLOCK_OPEN = re.compile(r"^(?:alt|else|opt|loop|par|and|break|critical|group|box|partition)\b")
PLANT_UNSUPPORTED = re.compile(
    r"^(?:(?:state|usecase|component|node|cloud|frame|rectangle|artifact|storage|folder|"
    r"start|stop|if|while|repeat|fork|object|map|json|yaml|salt|gantt|mindmap|wbs)\b|:.*;$)"
)


def _plant_name(raw: str) -> str:
    raw = raw.strip()
    return raw[1:-1] if raw.startswith('"') else raw


def import_plantuml(text: str) -> dict:
    """Sequence and class diagrams. Anything else is refused, not guessed at.

    `!include`, `!pragma` and every other preprocessor line is dropped: nothing
    named in a diagram is ever opened.
    """
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("'") or line.startswith("/'"):
            continue
        lines.append(line)
    if len(lines) > MAX_ELEMENTS:
        raise DiagramImportError(f"more than {MAX_ELEMENTS} statements")
    if lines and lines[0].lower().startswith("@start") and not lines[0].lower().startswith("@startuml"):
        raise DiagramImportError(f"{lines[0].split()[0]} is not supported: only @startuml sequence and class diagrams")
    lines = [ln for ln in lines if not ln.lower().startswith(("@startuml", "@enduml"))]

    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    groups: dict[str, dict] = {}
    stack: list[tuple[str, str | None]] = []   # ("body" | "group" | "block", group id)
    is_class = any(PLANT_DECL.match(ln) and PLANT_DECL.match(ln).group("kind") not in PLANT_SEQ_KINDS for ln in lines)
    is_class = is_class or any(re.match(r"^(?:package|namespace)\b", ln) for ln in lines)

    def current_group() -> str | None:
        for kind, gid in reversed(stack):
            if kind == "group":
                return gid
        return None

    def touch(name: str, label: str | None = None, alias: str | None = None) -> str:
        nid = alias or _plant_name(name)
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": plain(label if label is not None else _plant_name(name)),
                          "group": current_group()}
        elif label is not None:
            nodes[nid]["label"] = plain(label)
        return nid

    in_note = False
    for line in lines:
        low = line.lower()
        if in_note:
            if re.match(r"^end\s*(?:note|legend)$", low) or low in {"endnote", "endlegend"}:
                in_note = False
            continue
        if line.startswith("!"):
            continue
        if re.match(r"^(?:note|rnote|hnote)\b", low):
            if ":" not in line:
                in_note = True
            continue
        if re.match(r"^legend\b", low):
            in_note = True
            continue
        if PLANT_IGNORED.match(line):
            continue
        if line == "}":
            if not stack:
                raise DiagramImportError("'}' without a matching '{'")
            stack.pop()
            continue
        if stack and stack[-1][0] == "body":
            continue                                    # class members are not structure
        pkg = re.match(rf"^(?:package|namespace)\s+({PLANT_NAME})(?:\s+as\s+([\w.]+))?[^{{]*\{{$", line)
        if pkg:
            gid = pkg.group(2) or _plant_name(pkg.group(1))
            if gid in groups or gid in nodes:
                raise DiagramImportError(f"duplicate id {gid!r}")
            groups[gid] = {"id": gid, "label": _plant_name(pkg.group(1)), "parent": current_group()}
            stack.append(("group", gid))
            if len(stack) > MAX_DEPTH:
                raise DiagramImportError(f"nesting deeper than {MAX_DEPTH} levels")
            continue
        decl = PLANT_DECL.match(line)
        if decl:
            kind = decl.group("kind")
            touch(decl.group("name"), alias=decl.group("alias"))
            if kind not in PLANT_SEQ_KINDS and decl.group("rest").rstrip().endswith("{"):
                stack.append(("body", None))
            continue
        if PLANT_UNSUPPORTED.match(line):
            raise DiagramImportError(
                f"unsupported PlantUML statement {line[:40]!r}: only sequence and class diagrams are imported"
            )
        if not is_class and (PLANT_BLOCK_OPEN.match(low) or low in {"end", "end box"}):
            if low.startswith("end"):
                if not stack:
                    raise DiagramImportError("'end' without a matching block")
                stack.pop()
            elif not low.startswith(("else", "and")):
                stack.append(("block", None))
            continue
        if is_class:
            rel = PLANT_REL.match(line)
            if rel:
                arrow = rel.group("arrow")
                a, b = touch(rel.group("a")), touch(rel.group("b"))
                src, dst = (b, a) if arrow.startswith(("<|", "<")) else (a, b)
                edges.append({"from": src, "to": dst, "label": plain(rel.group("label") or "")})
                continue
        else:
            msg = PLANT_SEQ_MSG.match(line)
            if msg and re.search(r"[<>]", msg.group("arrow")):
                a, b = touch(msg.group("a")), touch(msg.group("b"))
                src, dst = (b, a) if msg.group("arrow").startswith("<") else (a, b)
                edges.append({"from": src, "to": dst, "label": plain((msg.group("label") or "").replace("\\n", " "))})
                continue
        raise DiagramImportError(f"cannot read PlantUML statement {line[:40]!r}")
    if stack:
        raise DiagramImportError(f"{stack[-1][0]} is never closed")
    if not nodes:
        raise DiagramImportError("no participants or classes found")
    return finish("plantuml", nodes, edges, groups)


# --------------------------------------------------------------------- main

FORMATS = ("drawio", "mermaid", "excalidraw", "plantuml")


def detect(path: Path, text: str) -> str:
    suffix = path.suffix.lower()
    if suffix == ".excalidraw":
        return "excalidraw"
    if suffix in {".puml", ".plantuml", ".pu", ".wsd"} or text.lstrip().startswith("@startuml"):
        return "plantuml"
    if suffix in {".drawio", ".xml"} or text.lstrip().startswith("<"):
        return "drawio"
    if suffix == ".json" or text.lstrip().startswith("{"):
        return "excalidraw"
    return "mermaid"


def import_file(path: Path, fmt: str | None = None, page: int = 0) -> dict:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise DiagramImportError(f"{path.name} is {size:,} bytes; the limit is {MAX_BYTES:,}")
    text = path.read_text(encoding="utf-8", errors="replace")
    fmt = fmt or detect(path, text)
    if fmt == "drawio":
        return import_drawio(text, page)
    if fmt == "excalidraw":
        return import_excalidraw(text)
    if fmt == "plantuml":
        return import_plantuml(text)
    return import_mermaid(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract diagram structure as neutral JSON (no coordinates).")
    parser.add_argument("path", type=Path, help=".drawio / .xml, .mmd / .mermaid, .excalidraw or .puml file")
    parser.add_argument("--format", choices=FORMATS, help="override detection by extension")
    parser.add_argument("--page", type=int, default=0, help="draw.io page index (default 0)")
    args = parser.parse_args(argv)
    try:
        model = import_file(args.path, args.format, args.page)
    except DiagramImportError as exc:
        print(f"import_diagram: {args.path}: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"import_diagram: {exc}", file=sys.stderr)
        return 1
    json.dump(model, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
