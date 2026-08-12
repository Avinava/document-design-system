#!/usr/bin/env python3
"""Validate the repository's skills, tokens, and cross-references.

    python scripts/validate_repository.py .

The linter reads the same source of truth the skills read — core/tokens.md for
the required token list and core/themes/*.css for the palette — so the prose
rules and the machine check cannot drift apart.

Standard library only. Exit code 1 on any error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# frontmatter schema
# --------------------------------------------------------------------------

ALLOWED_KEYS = {"name", "description"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
MAX_SKILL_LINES = 400

# Hex literals are allowed only where the palette is defined. Everywhere else
# they mean a component has learned about a theme, which is the one thing the
# token contract exists to prevent.
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
HEX_EXEMPT_DIRS = {"core/themes"}
HEX_EXEMPT_FILES = {
    "core/tokens.md",
    "core/README.md",
    "THIRD_PARTY_LICENSES.md",
    # Print normalization deliberately leaves the theme behind — flattening to
    # white paper and neutral greys is the whole point of that layer, so its
    # literals are intentional rather than a leak of theme knowledge.
    "core/print.css",
}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)#][^)]*)\)")

errors: list[str] = []
warnings: list[str] = []


def error(path: Path, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def warn(path: Path, msg: str) -> None:
    warnings.append(f"{path}: {msg}")


# --------------------------------------------------------------------------
# frontmatter
# --------------------------------------------------------------------------


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Minimal flat YAML frontmatter parser.

    Deliberately does not support nesting: the schema is two flat keys, and a
    parser that silently accepts more would let the schema drift.
    """
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None

    block = text[4:end]
    data: dict[str, str] = {}
    key: str | None = None

    for line in block.split("\n"):
        if not line.strip():
            continue
        if line[0] in " \t":
            if key is None:
                return None
            data[key] += " " + line.strip()
            continue
        if ":" not in line:
            return None
        key, _, value = line.partition(":")
        key = key.strip()
        data[key] = value.strip()

    return data


def check_skill(skill_dir: Path, root: Path) -> None:
    rel = skill_dir.relative_to(root)
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.is_file():
        error(rel, "missing SKILL.md")
        return

    text = skill_md.read_text(encoding="utf-8")
    rel_md = skill_md.relative_to(root)

    fm = parse_frontmatter(text)
    if fm is None:
        error(rel_md, "missing or malformed YAML frontmatter")
        return

    extra = set(fm) - ALLOWED_KEYS
    if extra:
        error(
            rel_md,
            f"unexpected frontmatter keys: {', '.join(sorted(extra))}. "
            f"Only {', '.join(sorted(ALLOWED_KEYS))} are allowed — version and "
            "license live in .claude-plugin/plugin.json and LICENSE.",
        )

    name = fm.get("name", "")
    if not name:
        error(rel_md, "frontmatter has no name")
    else:
        if not NAME_RE.match(name):
            error(rel_md, f'name "{name}" must be lowercase-hyphenated')
        if len(name) > MAX_NAME:
            error(rel_md, f"name is {len(name)} chars, max {MAX_NAME}")
        if name != skill_dir.name:
            error(rel_md, f'name "{name}" does not match folder "{skill_dir.name}"')

    desc = fm.get("description", "")
    if not desc:
        error(rel_md, "frontmatter has no description")
    else:
        if len(desc) > MAX_DESCRIPTION:
            error(rel_md, f"description is {len(desc)} chars, max {MAX_DESCRIPTION}")
        # These five skills sit close enough together that without an explicit
        # negative scope they compete for the same prompts.
        if "do not use" not in desc.lower():
            error(
                rel_md,
                'description needs a "Do not use for ..." clause so it does not '
                "compete with the sibling skills",
            )
        if "use when" not in desc.lower() and "use for" not in desc.lower():
            warn(rel_md, 'description should say "Use when ..." or "Use for ..."')

    line_count = text.count("\n") + 1
    if line_count > MAX_SKILL_LINES:
        warn(
            rel_md,
            f"{line_count} lines, over the {MAX_SKILL_LINES}-line target — "
            "move depth into references/ so it loads only when needed",
        )


# --------------------------------------------------------------------------
# tokens
# --------------------------------------------------------------------------


CSS_COMMENT = re.compile(r"/\*.*?\*/", re.S)
CSS_DECL = re.compile(r"(--[a-z0-9-]+)\s*:")


def declared_tokens(css: str) -> set[str]:
    """Custom properties declared in a stylesheet.

    Comments are stripped first, because core/base.css discusses tokens in
    prose (`--accent: var(--accent)` as an example of a cycle) and those must
    not count as declarations.

    Matching is not anchored to line start: a declaration always has a colon
    after the name and a var() reference never does, so the anchor bought
    nothing and made a single-line or minified theme report every token as
    missing.
    """
    return set(CSS_DECL.findall(CSS_COMMENT.sub("", css)))


def required_tokens(root: Path) -> set[str]:
    """Read the required token list out of core/tokens.md's tables."""
    tokens_md = root / "core" / "tokens.md"
    if not tokens_md.is_file():
        error(Path("core/tokens.md"), "missing")
        return set()

    found: set[str] = set()
    optional = False
    for line in tokens_md.read_text(encoding="utf-8").split("\n"):
        if line.startswith("### "):
            optional = "optional" in line.lower()
        if optional:
            continue
        m = re.match(r"\|\s*`(--[a-z0-9-]+)`\s*\|", line)
        if m:
            found.add(m.group(1))
    return found


def check_themes(root: Path) -> set[str]:
    """Every theme defines every required token. Returns the palette."""
    required = required_tokens(root)
    theme_dir = root / "core" / "themes"
    palette: set[str] = set()

    themes = sorted(theme_dir.glob("*.css"))
    if not themes:
        error(Path("core/themes"), "no theme files found")
        return palette

    for theme in themes:
        rel = theme.relative_to(root)
        css = theme.read_text(encoding="utf-8")
        defined = declared_tokens(css)

        missing = required - defined
        if missing:
            error(
                rel,
                "missing required tokens: "
                + ", ".join(sorted(missing))
                + " — a theme that leaves one undefined renders a partially "
                "themed document",
            )

        palette.update(h.lower() for h in HEX_RE.findall(css))

    return palette


def check_hex_literals(root: Path, palette: set[str]) -> None:
    """No hex outside the palette definitions.

    This is the load-bearing rule of the token contract: components name roles,
    never colors.
    """
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".css", ".html", ".svg", ".mjs", ".js"}:
            continue

        rel = path.relative_to(root)
        rel_str = rel.as_posix()

        if any(part in {"node_modules", ".git", "dist"} for part in rel.parts):
            continue
        # examples/ holds assembled output, which contains the inlined theme by
        # definition. The rule is about sources — a built document is supposed
        # to have the palette in it.
        #
        # assets/ holds artwork rendered through <img>, which is an isolated
        # document that the page's custom properties never reach. A banner has
        # to carry literal colors and do its own light/dark handling; there is
        # no token to reference from in there.
        if rel.parts[0] in {"examples", "assets"}:
            continue
        if rel_str in HEX_EXEMPT_FILES:
            continue
        if any(rel_str.startswith(d + "/") for d in HEX_EXEMPT_DIRS):
            continue

        for i, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            for hex_value in HEX_RE.findall(line):
                low = hex_value.lower()
                # Plain white and black are permitted in print normalization,
                # where the point is precisely to leave the theme behind.
                if low in {"#fff", "#ffffff", "#000", "#000000"}:
                    continue
                if low in palette:
                    warn(
                        rel,
                        f"line {i}: {hex_value} is a palette value used outside "
                        "core/themes/ — reference the token instead",
                    )
                else:
                    error(
                        rel,
                        f"line {i}: {hex_value} is not in the palette and not in "
                        "core/themes/ — components must consume tokens, not colors",
                    )


# --------------------------------------------------------------------------
# links
# --------------------------------------------------------------------------


def check_links(root: Path) -> None:
    for md in sorted(root.rglob("*.md")):
        if any(p in {"node_modules", ".git", "dist"} for p in md.relative_to(root).parts):
            continue
        rel = md.relative_to(root)
        for target in LINK_RE.findall(md.read_text(encoding="utf-8")):
            target = target.split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            # Repo-root-relative paths are written without a leading slash.
            if not (md.parent / target).exists() and not (root / target).exists():
                error(rel, f"broken relative link: {target}")


# --------------------------------------------------------------------------


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()

    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        print(f"no skills/ directory under {root}", file=sys.stderr)
        return 1

    skills = sorted(p for p in skills_dir.iterdir() if p.is_dir())
    for skill in skills:
        check_skill(skill, root)

    palette = check_themes(root)
    check_hex_literals(root, palette)
    check_links(root)

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}", file=sys.stderr)

    print(
        f"\nchecked {len(skills)} skills, {len(palette)} palette colors · "
        f"{len(errors)} errors, {len(warnings)} warnings"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
