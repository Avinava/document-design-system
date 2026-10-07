#!/usr/bin/env python3
"""Extract the structure of a draw.io or Mermaid diagram as neutral JSON.

    python3 scripts/import_diagram.py system.drawio            # plain or compressed
    python3 scripts/import_diagram.py flow.mmd                 # flowchart / graph
    python3 scripts/import_diagram.py export.xml --format drawio --page 1

Output, on stdout:

    {"source": "drawio" | "mermaid",
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


# --------------------------------------------------------------------- main


def detect(path: Path, text: str) -> str:
    if path.suffix.lower() in {".drawio", ".xml"} or text.lstrip().startswith("<"):
        return "drawio"
    if path.suffix.lower() in {".mmd", ".mermaid"}:
        return "mermaid"
    return "mermaid"


def import_file(path: Path, fmt: str | None = None, page: int = 0) -> dict:
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise DiagramImportError(f"{path.name} is {size:,} bytes; the limit is {MAX_BYTES:,}")
    text = path.read_text(encoding="utf-8", errors="replace")
    fmt = fmt or detect(path, text)
    if fmt == "drawio":
        return import_drawio(text, page)
    return import_mermaid(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract diagram structure as neutral JSON (no coordinates).")
    parser.add_argument("path", type=Path, help=".drawio / .xml or .mmd / .mermaid file")
    parser.add_argument("--format", choices=("drawio", "mermaid"), help="override detection by extension")
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
