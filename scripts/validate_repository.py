#!/usr/bin/env python3
"""Validate the repository's skills, tokens, and cross-references.

    python scripts/validate_repository.py .

The linter reads the same source of truth the skills read — core/tokens.md for
the required token list and core/themes/*.css for the palette — so the prose
rules and the machine check cannot drift apart.

Standard library only. Exit code 1 on any error.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402
import pins  # noqa: E402
import sync_skill_assets  # noqa: E402
from sync_skill_assets import VENDORED_DIRS  # noqa: E402

# --------------------------------------------------------------------------
# frontmatter schema
# --------------------------------------------------------------------------

ALLOWED_KEYS = {"name", "description"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024
# A SKILL.md loads in full whenever the skill triggers, so its size is a cost
# paid on every use. Bytes rather than lines: a line cap rewards long lines.
# Counted with line endings normalised to LF so a CRLF checkout measures the same.
MAX_SKILL_BYTES = 14_000

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
    # The brand exhibit quotes the fictional guide's hex values as evidence.
    # That is provenance, not a component learning a theme.
    "templates/brand.html",
}

# Installed dependencies and build output: not this repository's sources.
# .venv is where the documented `uv venv` puts the authoring Python packages.
SKIP_DIRS = {"node_modules", ".git", "dist", ".venv", "venv"}

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

    size = len(text.replace("\r\n", "\n").encode("utf-8"))
    if size > MAX_SKILL_BYTES:
        error(
            rel_md,
            f"{size:,} bytes, over the {MAX_SKILL_BYTES:,}-byte cap — "
            "move depth into references/ so it loads only when needed",
        )


def check_writing_types(root: Path) -> None:
    """The type references, the families table, commands and bodies agree.

    The catalog is parsed from the type files and core/document-patterns.md
    (scripts/catalog.py). A command or body without a type file — or the
    reverse — is how the catalog and the skill drift apart.
    """
    if not (root / catalog.TYPE_DIR).is_dir():
        return

    types: dict[str, catalog.Type] = {}
    for path in catalog.type_files(root):
        rel = path.relative_to(root)
        try:
            parsed = catalog.parse_type(path)
        except catalog.CatalogError as exc:
            error(rel, str(exc))
            continue
        types[parsed.slug] = parsed
        if "Reader's question" not in path.read_text(encoding="utf-8").replace("\u2019", "'"):
            error(rel, "missing reader's question")

    try:
        patterns = catalog.load_patterns(root)
    except (OSError, catalog.CatalogError) as exc:
        error(catalog.PATTERNS_MD, str(exc))
        return
    try:
        catalog.load_modules(root)
    except catalog.CatalogError as exc:
        error(catalog.PATTERNS_MD, str(exc))

    for where, message in catalog.problems(types, patterns, catalog.theme_names(root)):
        error(where.relative_to(root) if where.is_absolute() else where, message)

    slugs = set(types)
    commands = root / "commands"
    if commands.is_dir() and slugs:
        allowed = slugs | catalog.COMPATIBILITY_PROFILES | catalog.NON_TYPE_COMMANDS
        cmd_slugs = {p.stem for p in commands.glob("*.md")}
        for extra in sorted(cmd_slugs - allowed):
            error(
                (commands / f"{extra}.md").relative_to(root),
                f'command "{extra}" has no matching type-{extra}.md',
            )
        for missing in sorted(slugs - cmd_slugs):
            error(
                Path("commands") / f"{missing}.md",
                f"missing command for shipped type {missing}",
            )

    types_dir = root / "templates" / "types"
    if types_dir.is_dir() and slugs:
        body_slugs = {p.stem for p in types_dir.glob("*.html")}
        for extra in sorted(body_slugs - slugs - catalog.COMPATIBILITY_PROFILES):
            error(
                (types_dir / f"{extra}.html").relative_to(root),
                f'type body "{extra}" has no matching type-{extra}.md',
            )
        for missing in sorted(slugs - body_slugs):
            error(
                Path("templates/types") / f"{missing}.html",
                f"missing type body for shipped type {missing}",
            )


def check_commands(root: Path) -> None:
    """Plugin commands need YAML frontmatter. `claude plugin validate --strict`
    treats a missing description as a warning, then fails the job."""
    commands = root / "commands"
    if not commands.is_dir():
        return
    for path in sorted(commands.glob("*.md")):
        rel = path.relative_to(root)
        fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            error(rel, "missing YAML frontmatter (plugin validate --strict fails)")
            continue
        if not fm.get("description"):
            error(rel, "frontmatter has no description")


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

        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        # examples/ holds assembled output, which contains the inlined theme by
        # definition. The rule is about sources — a built document is supposed
        # to have the palette in it.
        #
        # assets/ holds artwork rendered through <img>, which is an isolated
        # document that the page's custom properties never reach. A banner has
        # to carry literal colors and do its own light/dark handling; there is
        # no token to reference from in there.
        if rel.parts[0] in {"examples", "assets", "site"}:
            continue
        # Vendored copies are byte-identical to the canonical files, which are
        # checked above; check_vendored_assets enforces the identity.
        if is_vendored(rel):
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


def check_manifests(root: Path) -> None:
    """Validate the plugin and marketplace manifests with no dependencies.

    `claude plugin validate` covers this far more thoroughly, but it needs
    node and a network fetch, so it only runs in CI. These checks are the
    subset worth catching before a push, and they encode two invariants the
    schema cannot express: that the marketplace is named for the repository,
    and that the two manifests do not drift apart.
    """
    plugin_path = root / ".claude-plugin" / "plugin.json"
    market_path = root / ".claude-plugin" / "marketplace.json"

    plugin: dict = {}
    if not plugin_path.is_file():
        error(plugin_path.relative_to(root), "missing plugin manifest")
    else:
        try:
            plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            error(plugin_path.relative_to(root), f"invalid JSON: {exc}")

    if plugin:
        rel = plugin_path.relative_to(root)
        name = plugin.get("name")
        if not isinstance(name, str) or not NAME_RE.fullmatch(name):
            error(rel, f"name must be kebab-case, got {name!r}")
        if not isinstance(plugin.get("version"), str):
            error(rel, "missing string version")
        for field in ("description", "license", "repository", "homepage"):
            if not plugin.get(field):
                error(rel, f"missing non-empty {field}")

    if not market_path.is_file():
        error(market_path.relative_to(root), "missing marketplace manifest")
        return

    rel = market_path.relative_to(root)
    try:
        market = json.loads(market_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error(rel, f"invalid JSON: {exc}")
        return

    for field in ("name", "description", "owner", "plugins"):
        if not market.get(field):
            error(rel, f"missing non-empty {field}")

    name = market.get("name")
    if isinstance(name, str) and not NAME_RE.fullmatch(name):
        error(rel, f"name must be kebab-case, got {name!r}")

    # Marketplace names are global per user: a second catalog registered under
    # a name already in use silently displaces the first and orphans the
    # plugins installed from it. Naming the catalog after the repository makes
    # the name unique by construction. See CHANGELOG 0.1.1.
    repo_url = plugin.get("repository")
    if isinstance(name, str) and isinstance(repo_url, str):
        repo_name = repo_url.rstrip("/").rsplit("/", 1)[-1]
        if name != repo_name:
            error(
                rel,
                f"marketplace name {name!r} must match the repository name "
                f"{repo_name!r} — a shared catalog name silently displaces "
                "another repository's marketplace",
            )

    owner = market.get("owner")
    if isinstance(owner, dict) and not owner.get("name"):
        error(rel, "owner.name is required")

    entries = market.get("plugins")
    if not isinstance(entries, list):
        error(rel, "plugins must be a list")
        return

    for index, entry in enumerate(entries):
        label = f"plugins[{index}]"
        if not isinstance(entry, dict):
            error(rel, f"{label}: must be an object")
            continue

        entry_name = entry.get("name")
        if not isinstance(entry_name, str) or not NAME_RE.fullmatch(entry_name):
            error(rel, f"{label}: name must be kebab-case, got {entry_name!r}")

        source = entry.get("source")
        if not source:
            error(rel, f"{label}: missing source")
        elif isinstance(source, str):
            if not source.startswith("./"):
                error(rel, f"{label}: relative source must start with './', got {source!r}")
            elif not (root / source).is_dir():
                error(rel, f"{label}: source does not resolve: {source}")

        # A field duplicated from plugin.json is a field that can drift.
        for field in ("description", "version", "license", "repository", "homepage"):
            value = entry.get(field)
            if value is not None and plugin.get(field) is not None and value != plugin[field]:
                error(
                    rel,
                    f"{label}: {field} {value!r} disagrees with plugin.json "
                    f"{plugin[field]!r}",
                )

        if entry.get("author") != market.get("owner"):
            error(rel, f"{label}: author must match the marketplace owner")

        # Whatever a marketplace browser shows comes from the entry, not from
        # plugin.json, so the entry has to carry its own discovery metadata.
        for field in ("description", "license", "repository", "category", "tags"):
            if not entry.get(field):
                error(rel, f"{label}: missing non-empty {field}")

        if isinstance(source, str) and source in ("./", "."):
            if entry_name != plugin.get("name"):
                error(
                    rel,
                    f"{label}: name {entry_name!r} must match plugin.json "
                    f"{plugin.get('name')!r} when source is the repository root",
                )
            # With source at the repo root, skills/ is scanned by default; an
            # explicit `skills` declaration can replace that scan rather than
            # extend it, which silently drops skills.
            if "skills" in plugin:
                error(
                    plugin_path.relative_to(root),
                    "remove \"skills\": skills/ is scanned by default, and "
                    "declaring it can replace that scan rather than extend it",
                )
            for skill_dir in sorted((root / "skills").glob("*/")):
                if not (skill_dir / "SKILL.md").is_file():
                    error(skill_dir.relative_to(root), "directory under skills/ has no SKILL.md")


# --------------------------------------------------------------------------
# authoring toolchain
# --------------------------------------------------------------------------

# `name@<x.y.z>` (npm, optionally scoped) and `name==<x.y.z>` (PyPI). The lookbehind
# keeps an email address or a path segment from reading as a package.
NPM_PIN_RE = re.compile(r"(?<![\w@/.-])((?:@[a-z0-9][\w.-]*/)?[a-z0-9][\w.-]*)@(\d+\.\d+\.\d+)\b")
PYPI_PIN_RE = re.compile(r"(?<![\w.-])([A-Za-z0-9][\w.-]*)==(\d+(?:\.\d+)*)\b")

LICENSES = "THIRD_PARTY_LICENSES.md"
# A dependency row: [`package`](url) | registry | version | license | ...
LICENSE_ROW_RE = re.compile(r"^\|\s*\[`([^`]+)`\]\([^)]*\)\s*\|\s*(npm|PyPI)\s*\|\s*([^|]*?)\s*\|", re.M)
REGISTRY = {"npm": "npm", "PyPI": "pypi"}

# Import name -> distribution name, where the two differ.
IMPORT_TO_DIST = {"PIL": "pillow"}
# Static `import … from 'x'`, bare `import 'x'`, and dynamic `import('x')`.
MJS_IMPORT_RE = re.compile(r"""(?:\bfrom\s+|^\s*import\s+|\bimport\s*\(\s*)['"]([^'"]+)['"]""", re.M)


def script_and_skill_files(root: Path) -> list[Path]:
    """The canonical scripts plus every skill's prose: what a user actually runs or reads."""
    files = [p for p in sorted((root / "scripts").glob("*")) if p.suffix in {".py", ".mjs"}]
    for skill in sorted((root / "skills").glob("*/")):
        files.append(skill / "SKILL.md")
        files.extend(sorted((skill / "references").glob("*.md")))
    return [p for p in files if p.is_file()]


def pinned_mention_files(root: Path) -> list[Path]:
    """Every file whose version mentions must agree with the pins."""
    docs = [root / name for name in ("README.md", LICENSES, "examples/README.md", "AGENTS.md")]
    return script_and_skill_files(root) + [p for p in docs if p.is_file()]


def load_pins(root: Path) -> dict[str, dict[str, str]] | None:
    try:
        return pins.pins(root)
    except FileNotFoundError as exc:
        error(Path(Path(exc.filename).name), "missing — the authoring toolchain is pinned there")
    except (ValueError, json.JSONDecodeError) as exc:
        error(Path(pins.PACKAGE_JSON), str(exc))
    return None


def check_pins(root: Path) -> None:
    """Every `pkg@x.y.z` / `pkg==x.y.z` in docs and scripts names a pinned
    package at its pinned version, so a hint can never install something the
    lockfile does not."""
    found = load_pins(root)
    if found is None:
        return
    for path in pinned_mention_files(root):
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8")
        for registry, pattern, manifest in (
            ("npm", NPM_PIN_RE, pins.PACKAGE_JSON),
            ("pypi", PYPI_PIN_RE, pins.REQUIREMENTS),
        ):
            for m in pattern.finditer(text):
                name, version = m.group(1), m.group(2)
                key = name.lower() if registry == "pypi" else name
                line = text.count("\n", 0, m.start()) + 1
                pinned = found[registry].get(key)
                if pinned is None:
                    error(rel, f"line {line}: {m.group(0)} is not pinned in {manifest}")
                elif pinned != version:
                    error(rel, f"line {line}: {m.group(0)} disagrees with {manifest} ({pinned})")


def script_imports(root: Path) -> dict[tuple[str, str], list[Path]]:
    """Third-party packages imported by scripts/*.mjs and scripts/*.py.

    Returns {(registry, distribution): [importing scripts]}.
    """
    scripts = root / "scripts"
    local = {p.stem for p in scripts.glob("*.py")}
    found: dict[tuple[str, str], list[Path]] = {}

    def add(key: tuple[str, str], path: Path) -> None:
        found.setdefault(key, [])
        if path not in found[key]:
            found[key].append(path)

    for path in sorted(scripts.glob("*.mjs")):
        for spec in MJS_IMPORT_RE.findall(path.read_text(encoding="utf-8")):
            if spec.startswith(("node:", ".", "/")):
                continue
            parts = spec.split("/")
            name = "/".join(parts[:2]) if spec.startswith("@") else parts[0]
            add(("npm", name), path)

    for path in sorted(scripts.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            error(path.relative_to(root), f"does not parse: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules = [node.module]
            else:
                continue
            for module in modules:
                top = module.split(".")[0]
                if top in sys.stdlib_module_names or top in local or top == "__future__":
                    continue
                add(("pypi", IMPORT_TO_DIST.get(top, top).lower()), path)
    return found


def check_dependencies(root: Path) -> None:
    """The license table and the code agree in both directions.

    Every third-party import in scripts/ and every pinned package has a row in
    THIRD_PARTY_LICENSES.md (at its pinned version), and every row is used by a
    script or named by a skill — a row nobody references is an attribution for
    a dependency that no longer exists.
    """
    licenses = root / LICENSES
    if not licenses.is_file():
        error(Path(LICENSES), "missing")
        return
    rows: dict[tuple[str, str], str] = {}
    for name, registry, version in LICENSE_ROW_RE.findall(licenses.read_text(encoding="utf-8")):
        reg = REGISTRY[registry]
        rows[(reg, name.lower() if reg == "pypi" else name)] = version

    imports = script_imports(root)
    for (registry, name), users in sorted(imports.items()):
        if (registry, name) not in rows:
            for user in users:
                error(
                    user.relative_to(root),
                    f"imports {name} ({registry}), which has no row in {LICENSES}",
                )

    found = load_pins(root)
    if found is not None:
        for registry, entries in found.items():
            for name, version in sorted(entries.items()):
                listed = rows.get((registry, name))
                if listed is None:
                    error(Path(LICENSES), f"pinned {registry} package {name} has no row")
                elif listed != version:
                    error(
                        Path(LICENSES),
                        f"{name} ({registry}) is listed at {listed!r} but pinned at {version}",
                    )

    corpus = "\n".join(p.read_text(encoding="utf-8") for p in script_and_skill_files(root)).lower()
    for registry, name in sorted(rows):
        if (registry, name) in imports:
            continue
        if name.lower() not in corpus:
            error(
                Path(LICENSES),
                f"{name} ({registry}) is listed but no script or skill references it — "
                "remove the row or the dependency it describes",
            )


def is_vendored(rel: Path) -> bool:
    """True for skills/<name>/{core,scripts,templates}/..., the generated copies."""
    return len(rel.parts) > 3 and rel.parts[0] == "skills" and rel.parts[2] in VENDORED_DIRS


def check_vendored_assets(root: Path) -> None:
    for problem in sync_skill_assets.check_all(root):
        error("skills", f"vendored asset drift: {problem} (run scripts/sync_skill_assets.py)")


def check_links(root: Path) -> None:
    for md in sorted(root.rglob("*.md")):
        if any(p in SKIP_DIRS for p in md.relative_to(root).parts):
            continue
        rel = md.relative_to(root)
        if is_vendored(rel):
            continue
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
    check_writing_types(root)
    check_commands(root)

    palette = check_themes(root)
    check_hex_literals(root, palette)
    check_manifests(root)
    check_pins(root)
    check_dependencies(root)
    check_vendored_assets(root)
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
