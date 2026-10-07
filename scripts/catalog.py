#!/usr/bin/env python3
"""The writing-document catalog, derived from the files that define it.

    python3 scripts/catalog.py         # print types grouped by pattern

The catalog has exactly two sources:

- each `skills/writing-documents/references/type-<slug>.md` declares one type in
  its fenced `yaml` block;
- `core/document-patterns.md` declares the reading patterns in its families
  table and the module registry in its "Modules" table.

Everything else — the example build, the Pages site, the validator, the tests —
reads the catalog from here instead of keeping its own copy. Adding or changing
a type means editing its type file; nothing else repeats the slug-to-pattern
mapping.

The module-level `TYPES`, `PATTERNS` and `MODULES` load lazily on first access
from this repository. Tools that check another tree (the validator runs against
a path) call `load_types(root)` / `load_patterns(root)` / `load_modules(root)`.

Standard library only. Repository-only: no vendored skill script imports it.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TYPE_DIR = Path("skills/writing-documents/references")
PATTERNS_MD = Path("core/document-patterns.md")
THEMES_DIR = Path("core/themes")
COMMAND_PREFIX = "/document-design-system:"

# Commands and example bodies that keep a stable name without being a second
# canonical type. `mulesoft` is a profile of `service-docs`.
COMPATIBILITY_PROFILES = frozenset({"mulesoft"})

# Commands that are not types at all. Reserved here so the validator and the
# tests accept the command once it exists; its absence is not an error.
NON_TYPE_COMMANDS = frozenset({"compose"})

# The canonical type each compatibility profile specialises; its body reads
# with that type's pattern.
PROFILE_BASE = {"mulesoft": "service-docs"}

# Composed examples: documents built from a pattern rather than a type preset.
# Shape: {slug: (theme, pattern)}, mirroring the longform build's
# {slug: (theme, pattern)}. The body lives in templates/composed/<slug>.html and
# the Markdown in examples/<slug>.md declares `type: custom`.
COMPOSED: dict[str, tuple[str, str]] = {
    "platform-primer": ("field-notes", "learning"),
}
COMPOSED_DIR = Path("templates/composed")
TYPE_BODY_DIR = Path("templates/types")
PATTERNS_CSS = Path("core/document-patterns.css")

# Classes in core/document-patterns.css that are not modules. The shell frames
# every page; a part only appears inside its owning module. Both lists are
# also named in prose under "## Modules" in core/document-patterns.md.
SHELL_CLASSES = frozenset({
    "doc", "doc-hero", "lede", "doc-meta", "status-banner",
    "section", "section-head", "component-label", "lang",
})
MODULE_PARTS = {
    "recommended": "comparison-grid",
    "requirement-id": "requirement",
    "http-method": "endpoint",
    "impact-value": "impact-strip",
    "impact-label": "impact-strip",
    "crosswalk-legend": "crosswalk",
}

# A module whose allowed-patterns cell is this word serves every pattern.
ANY_PATTERN = "any"

TYPE_FIELDS = (
    "slug",
    "title",
    "aliases",
    "example",
    "command",
    "pattern",
    "default-theme",
    "default-format",
    "path",
)

YAML_FENCE = re.compile(r"^```yaml\n(.*?)^```", re.M | re.S)
CODE = re.compile(r"`([^`]+)`")


class CatalogError(ValueError):
    """A catalog source file is malformed. The message names the file."""


@dataclass(frozen=True)
class Type:
    slug: str
    title: str
    aliases: tuple[str, ...]
    example: str
    command: str
    pattern: str
    default_theme: str
    default_format: str
    path: str
    source: Path


@dataclass(frozen=True)
class Pattern:
    name: str
    movement: str
    modules: tuple[str, ...]  # characteristic modules, as named in prose
    types: tuple[str, ...]  # type slugs, in table order


@dataclass(frozen=True)
class Module:
    name: str
    css_class: str
    patterns: tuple[str, ...]
    purpose: str


# --------------------------------------------------------------------------
# types
# --------------------------------------------------------------------------


def type_files(root: Path = ROOT) -> list[Path]:
    """Every type reference, in filename order. type-index.md is the router, not a type."""
    return sorted(p for p in (root / TYPE_DIR).glob("type-*.md") if p.name != "type-index.md")


def _parse_list(raw: str, where: str) -> tuple[str, ...]:
    if not (raw.startswith("[") and raw.endswith("]")):
        raise CatalogError(f"{where}: aliases must be a [list], got {raw!r}")
    items = [item.strip() for item in raw[1:-1].split(",")]
    if items == [""]:
        return ()
    if any(not item for item in items):
        raise CatalogError(f"{where}: aliases has an empty entry: {raw!r}")
    return tuple(items)


def parse_type(path: Path) -> Type:
    """Parse one type reference's fenced `yaml` block.

    The block is flat `key: value` lines with a fixed key set; a parser that
    accepted more would let the schema drift.
    """
    text = path.read_text(encoding="utf-8")
    m = YAML_FENCE.search(text)
    if not m:
        raise CatalogError(f"{path.name}: missing yaml metadata fence")
    meta: dict[str, str] = {}
    for number, line in enumerate(m.group(1).splitlines(), 1):
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        key = key.strip()
        if not sep or key not in TYPE_FIELDS:
            raise CatalogError(f"{path.name}: yaml line {number}: unexpected {line!r}")
        if key in meta:
            raise CatalogError(f"{path.name}: yaml declares {key} twice")
        meta[key] = value.strip()
    # aliases may be an empty list; every other field needs a value.
    missing = [f for f in TYPE_FIELDS if f not in meta or (not meta[f] and f != "aliases")]
    if missing:
        raise CatalogError(f"{path.name}: yaml has no {', '.join(missing)}")
    return Type(
        slug=meta["slug"],
        title=meta["title"],
        aliases=_parse_list(meta["aliases"], path.name),
        example=meta["example"],
        command=meta["command"],
        pattern=meta["pattern"],
        default_theme=meta["default-theme"],
        default_format=meta["default-format"],
        path=meta["path"],
        source=path,
    )


def load_types(root: Path = ROOT) -> dict[str, Type]:
    """{slug: Type}, in filename order. Raises CatalogError on the first bad file."""
    types: dict[str, Type] = {}
    for path in type_files(root):
        parsed = parse_type(path)
        types[parsed.slug] = parsed
    return types


# --------------------------------------------------------------------------
# patterns and modules (core/document-patterns.md)
# --------------------------------------------------------------------------


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _section_table(text: str, heading: str) -> list[list[str]] | None:
    """Rows (header first) of the first table under the `## ` heading matching
    the regex `heading`, or None when there is no such section or table."""
    m = re.search(rf"^## {heading}\s*$", text, re.M)
    if not m:
        return None
    rows: list[list[str]] = []
    for line in text[m.end():].splitlines():
        if line.startswith("## "):
            break
        if line.startswith("|"):
            if re.fullmatch(r"\|[\s|:-]+\|", line.strip()):
                continue
            rows.append(_cells(line))
        elif rows:
            break
    return rows or None


FAMILIES_HEADER = ["Pattern", "Reader movement", "Characteristic modules", "Types"]
MODULES_HEADER = ["module", "class", "patterns allowed", "purpose"]


def load_patterns(root: Path = ROOT) -> dict[str, Pattern]:
    """{name: Pattern} from the families table, in table order."""
    source = root / PATTERNS_MD
    rows = _section_table(source.read_text(encoding="utf-8"), r"The [a-z-]+ families")
    if not rows:
        raise CatalogError(f"{PATTERNS_MD}: no table under a '## The <n> families' heading")
    if rows[0] != FAMILIES_HEADER:
        raise CatalogError(f"{PATTERNS_MD}: families table header must be {FAMILIES_HEADER}, got {rows[0]}")
    patterns: dict[str, Pattern] = {}
    for row in rows[1:]:
        if len(row) != len(FAMILIES_HEADER):
            raise CatalogError(f"{PATTERNS_MD}: families row has {len(row)} cells: {row}")
        name = CODE.fullmatch(row[0])
        if not name:
            raise CatalogError(f"{PATTERNS_MD}: pattern cell must be `code`, got {row[0]!r}")
        patterns[name.group(1)] = Pattern(
            name=name.group(1),
            movement=row[1],
            modules=tuple(part.strip() for part in row[2].split(",") if part.strip()),
            types=tuple(CODE.findall(row[3])),
        )
    return patterns


def load_modules(root: Path = ROOT) -> dict[str, Module]:
    """{class name: Module} from the strict `## Modules` table.

    The table's header is exactly `| module | class | patterns allowed |
    purpose |` (case-insensitive); `class` and each allowed pattern are
    `code`, or the allowed-patterns cell is the word `any`, which expands to
    every pattern in the families table. Returns {} while
    core/document-patterns.md has no Modules section.
    """
    source = root / PATTERNS_MD
    rows = _section_table(source.read_text(encoding="utf-8"), "Modules")
    if rows is None:
        return {}
    if [cell.lower() for cell in rows[0]] != MODULES_HEADER:
        raise CatalogError(f"{PATTERNS_MD}: Modules table header must be {MODULES_HEADER}, got {rows[0]}")
    modules: dict[str, Module] = {}
    names: set[str] = set()
    for row in rows[1:]:
        if len(row) != len(MODULES_HEADER):
            raise CatalogError(f"{PATTERNS_MD}: Modules row has {len(row)} cells: {row}")
        css_class = CODE.fullmatch(row[1])
        if not css_class:
            raise CatalogError(f"{PATTERNS_MD}: module class must be `code`, got {row[1]!r}")
        if css_class.group(1) in modules:
            raise CatalogError(f"{PATTERNS_MD}: module class `{css_class.group(1)}` is registered twice")
        if row[0] in names:
            raise CatalogError(f"{PATTERNS_MD}: module name {row[0]!r} is registered twice")
        names.add(row[0])
        if row[2] == ANY_PATTERN:
            allowed = tuple(load_patterns(root))
        else:
            allowed = tuple(CODE.findall(row[2]))
            leftover = CODE.sub("", row[2]).replace(",", "").strip()
            if not allowed or leftover:
                raise CatalogError(
                    f"{PATTERNS_MD}: patterns allowed for `{css_class.group(1)}` must be "
                    f"`code` names or {ANY_PATTERN!r}, got {row[2]!r}"
                )
        modules[css_class.group(1)] = Module(
            name=row[0],
            css_class=css_class.group(1),
            patterns=allowed,
            purpose=row[3],
        )
    return modules


# --------------------------------------------------------------------------
# module use (core/document-patterns.css and the example bodies)
# --------------------------------------------------------------------------

CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
CSS_CLASS = re.compile(r"\.([a-z][a-z0-9-]*)")
CLASS_ATTR = re.compile(r'\bclass="([^"]*)"')


def stylesheet_classes(root: Path = ROOT) -> set[str]:
    """Every class selector in core/document-patterns.css."""
    css = CSS_COMMENT.sub("", (root / PATTERNS_CSS).read_text(encoding="utf-8"))
    return set(CSS_CLASS.findall(css))


def body_classes(html: str) -> set[str]:
    """Every class named in a body's class="…" attributes."""
    return {name for attr in CLASS_ATTR.findall(html) for name in attr.split()}


def example_bodies(root: Path = ROOT, types: dict[str, Type] | None = None) -> dict[str, tuple[str, Path]]:
    """{example name: (pattern, body path)} for every type, profile and composed body that exists."""
    types = load_types(root) if types is None else types
    bodies: dict[str, tuple[str, Path]] = {}
    for slug, entry in types.items():
        bodies[slug] = (entry.pattern, root / TYPE_BODY_DIR / f"{slug}.html")
    for profile, base in PROFILE_BASE.items():
        if base in types:
            bodies[profile] = (types[base].pattern, root / TYPE_BODY_DIR / f"{profile}.html")
    for slug, (_, pattern) in COMPOSED.items():
        bodies[slug] = (pattern, root / COMPOSED_DIR / f"{slug}.html")
    return {name: (pattern, path) for name, (pattern, path) in bodies.items() if path.is_file()}


def module_problems(
    modules: dict[str, Module],
    patterns: dict[str, Pattern],
    css_classes: set[str],
    bodies: dict[str, tuple[str, set[str]]],
) -> list[str]:
    """Disagreements between the registry, the stylesheet, the families table and the bodies.

    `bodies` is {example name: (pattern, classes used)}.
    """
    found: list[str] = []
    for css_class, module in modules.items():
        if css_class not in css_classes:
            found.append(f"module `{css_class}` is registered but has no rule in {PATTERNS_CSS}")
        for pattern in module.patterns:
            if pattern not in patterns:
                found.append(f'module `{css_class}` allows unknown pattern "{pattern}"')
    for css_class in sorted(css_classes - set(modules) - SHELL_CLASSES - set(MODULE_PARTS)):
        found.append(
            f"{PATTERNS_CSS} styles `.{css_class}`, which is not a registered module, shell class or part"
        )
    for part, owner in MODULE_PARTS.items():
        if owner not in modules:
            found.append(f"part `{part}` belongs to `{owner}`, which is not a registered module")

    by_name = {module.name: module for module in modules.values()}
    for name, pattern in patterns.items():
        for module_name in pattern.modules:
            module = by_name.get(module_name)
            if module is None:
                found.append(f'the {name} row names characteristic module "{module_name}", which is not registered')
                continue
            if name not in module.patterns:
                found.append(f'the {name} row names "{module_name}", which the registry does not allow for {name}')
            users = [body for body, (p, used) in bodies.items() if p == name and module.css_class in used]
            if not users:
                found.append(f'no {name} example uses its characteristic module "{module_name}"')

    for body, (pattern, used) in sorted(bodies.items()):
        for css_class in sorted(used & set(modules)):
            if pattern not in modules[css_class].patterns:
                found.append(
                    f"{body} ({pattern}) uses `{css_class}`, which the registry allows only for "
                    f"{', '.join(modules[css_class].patterns)}"
                )
    return found


def theme_names(root: Path = ROOT) -> set[str]:
    return {p.stem for p in (root / THEMES_DIR).glob("*.css")}


# --------------------------------------------------------------------------
# cross-checks
# --------------------------------------------------------------------------


def problems(types: dict[str, Type], patterns: dict[str, Pattern], themes: set[str]) -> list[tuple[Path, str]]:
    """Disagreements between the type files, the families table and the themes.

    Returns [(file, message)] so the caller decides how to report.
    """
    found: list[tuple[Path, str]] = []
    for slug, entry in types.items():
        where = entry.source
        expected = entry.source.name[len("type-") : -len(".md")]
        if slug != expected:
            found.append((where, f'slug "{slug}" does not match filename (expected "{expected}")'))
        if entry.command != f"{COMMAND_PREFIX}{slug}":
            found.append((where, f"command must be {COMMAND_PREFIX}{slug}"))
        if entry.example != f"examples/{slug}.html":
            found.append((where, f"example must be examples/{slug}.html"))
        if entry.pattern not in patterns:
            found.append((where, f'pattern "{entry.pattern}" is not one of {", ".join(patterns)}'))
        elif slug not in patterns[entry.pattern].types:
            found.append((PATTERNS_MD, f'the {entry.pattern} row does not list `{slug}`'))
        if entry.default_theme not in themes:
            found.append((where, f'default-theme "{entry.default_theme}" is not a theme in {THEMES_DIR}'))
    for name, pattern in patterns.items():
        for slug in pattern.types:
            if slug not in types:
                found.append((PATTERNS_MD, f"the {name} row lists `{slug}`, which has no type file"))
            elif types[slug].pattern != name:
                found.append(
                    (PATTERNS_MD, f"the {name} row lists `{slug}`, whose type file says {types[slug].pattern}")
                )
    return found


# --------------------------------------------------------------------------
# lazy module attributes
# --------------------------------------------------------------------------

_LOADERS = {
    "TYPES": load_types,
    "PATTERNS": load_patterns,
    "MODULES": load_modules,
}
_CACHE: dict[str, object] = {}


def __getattr__(name: str) -> object:
    """TYPES: {slug: Type}; PATTERNS: {name: Pattern}; MODULES: {class: Module}.

    Loaded from this repository on first access, so importing the module for
    its parsers never fails on a malformed file.
    """
    if name in _LOADERS:
        if name not in _CACHE:
            _CACHE[name] = _LOADERS[name](ROOT)
        return _CACHE[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def main() -> None:
    try:
        types = load_types()
        patterns = load_patterns()
    except CatalogError as exc:
        sys.exit(str(exc))
    for pattern in patterns.values():
        print(f"{pattern.name}: {', '.join(pattern.types)}")
    print(f"\n{len(types)} types, {len(patterns)} patterns")
    for where, message in problems(types, patterns, theme_names()):
        print(f"problem: {where}: {message}", file=sys.stderr)


if __name__ == "__main__":
    main()
