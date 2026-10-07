#!/usr/bin/env node
/**
 * render_diagram.mjs — Mermaid source to a token-themed, self-contained inline SVG.
 *
 * Mermaid is the input notation. The output is an SVG that consumes this repo's
 * design tokens, so a theme swap on the document retheme the diagram with no
 * re-render and no JavaScript.
 *
 *   node scripts/render_diagram.mjs diagram.mmd --id ingest \
 *        --title "Ingestion path" \
 *        --desc "Events enter through the gateway and land in the warehouse." \
 *        --size doc-inline --out diagram.svg
 *
 * Requires: npm install beautiful-mermaid
 *
 * beautiful-mermaid (MIT, Craft Docs) does the parsing and layout. This wrapper
 * exists because its raw output is not safe to drop into a designed document:
 *
 *  1. It always emits an @import for Google Fonts inside the SVG. That is an
 *     external network request from inside a file that is supposed to be
 *     self-contained, and it fails closed in offline and print contexts.
 *  2. It emits generic element IDs ("arrowhead"). Two diagrams in one document
 *     produce duplicate IDs, and the second diagram's markers silently resolve
 *     to the first diagram's definitions.
 *  3. It hardcodes width/height attributes, which stops the SVG scaling into a
 *     print page.
 *  4. Its theme keys (--accent, --muted, --surface) collide with this repo's
 *     token names. Emitting `--accent: var(--accent)` on the <svg> is a
 *     self-reference, which is invalid at computed-value time. We map through
 *     the --dds-* aliases defined in core/base.css instead.
 *
 * Each of those is handled below.
 */

import { readFileSync, writeFileSync } from 'node:fs';
import { basename } from 'node:path';

const SIZES = {
  'doc-inline': 720,
  'full-width': 1100,
  'print-portrait': 640,
  'print-landscape': 980,
};

/* beautiful-mermaid's theme namespace mapped onto our tokens.
 * The --dds-* aliases exist precisely to avoid the self-reference cycle
 * described above. See core/base.css. */
const THEME = {
  bg: 'var(--dds-surface)',
  fg: 'var(--dds-ink)',
  line: 'var(--dds-rule-strong)',
  accent: 'var(--dds-accent)',
  muted: 'var(--dds-muted)',
  surface: 'var(--dds-surface-muted)',
  border: 'var(--dds-rule)',
  transparent: true,
};

function parseArgs(argv) {
  const args = { size: 'doc-inline' };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) args[a.slice(2)] = argv[++i];
    else rest.push(a);
  }
  args._ = rest;
  return args;
}

function escapeXml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Namespace every id="…" and its url(#…) / href="#…" references so multiple
 * diagrams can coexist in one document.
 */
function namespaceIds(svg, slug) {
  const ids = [...svg.matchAll(/id="([^"]+)"/g)].map((m) => m[1]);
  for (const id of new Set(ids)) {
    const safe = id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    svg = svg
      .replace(new RegExp(`id="${safe}"`, 'g'), `id="${slug}-${id}"`)
      .replace(new RegExp(`url\\(#${safe}\\)`, 'g'), `url(#${slug}-${id})`)
      .replace(new RegExp(`href="#${safe}"`, 'g'), `href="#${slug}-${id}"`);
  }
  return svg;
}

/**
 * Remove the external font import and route text through our type tokens.
 * Without this the SVG reaches out to fonts.googleapis.com at render time.
 */
function detachFonts(svg) {
  return svg
    .replace(/\s*@import\s+url\([^)]*\);?/g, '')
    .replace(/font-family:\s*'[^']*'[^;}]*/g, 'font-family: var(--sans)');
}

/**
 * Make the SVG scale rather than sit at a fixed pixel size.
 *
 * Two things this has to get right:
 *
 *  - Every edit is scoped to the ROOT <svg> open tag. Stripping width/height
 *    globally also strips them from every <rect>, which silently empties the
 *    diagram while leaving its labels in place.
 *  - max-width is merged into the existing style attribute rather than appended
 *    as a second one; an element may carry only one, and parsers keep the first
 *    and discard the rest.
 */
function makeResponsive(svg, targetWidth) {
  if (!/viewBox="/.test(svg)) {
    throw new Error('rendered SVG has no viewBox — cannot scale safely');
  }

  return svg.replace(/<svg([^>]*)>/, (_m, rawAttrs) => {
    let attrs = rawAttrs.replace(/\s(width|height)="[^"]*"/g, '');

    attrs = /\sstyle="/.test(attrs)
      ? attrs.replace(/\sstyle="([^"]*)"/, (_s, css) => {
          const sep = css.trim().endsWith(';') ? '' : ';';
          return ` style="${css}${sep}max-width:${targetWidth}px"`;
        })
      : `${attrs} style="max-width:${targetWidth}px"`;

    return `<svg${attrs} width="100%">`;
  });
}

/** Add the accessibility shell. core/a11y.md requires title first, then desc. */
function addA11y(svg, slug, title, desc) {
  const titleId = `${slug}-title`;
  const descId = `${slug}-desc`;
  svg = svg.replace(
    /<svg([^>]*)>/,
    `<svg$1 role="img" aria-labelledby="${titleId} ${descId}">`
  );
  const block =
    `\n  <title id="${titleId}">${escapeXml(title)}</title>` +
    `\n  <desc id="${descId}">${escapeXml(desc)}</desc>`;
  return svg.replace(/(<svg[^>]*>)/, `$1${block}`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const input = args._[0];

  if (!input) {
    console.error(
      'usage: render_diagram.mjs <input.mmd> --title "…" --desc "…" ' +
        '[--id slug] [--size doc-inline|full-width|print-portrait|print-landscape] [--out file.svg]'
    );
    process.exit(1);
  }

  let renderMermaidSVG;
  try {
    ({ renderMermaidSVG } = await import('beautiful-mermaid'));
  } catch {
    console.error(
      'beautiful-mermaid is not installed.\n' +
        '  npm install beautiful-mermaid\n' +
        'It is an authoring-time dependency only — the rendered SVG carries none of it.'
    );
    process.exit(1);
  }

  const slug = (args.id || basename(input).replace(/\.[^.]+$/, ''))
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

  const width = SIZES[args.size];
  if (!width) {
    console.error(`unknown --size "${args.size}". Known: ${Object.keys(SIZES).join(', ')}`);
    process.exit(1);
  }

  // A diagram without a description is not deliverable — a screen-reader user
  // and a grayscale reader both depend on it, and it is also the fastest way to
  // notice the diagram has no point.
  if (!args.title || !args.desc) {
    console.error(
      '--title and --desc are both required.\n' +
        'The desc should state what the arrangement shows, including what the accent marks.'
    );
    process.exit(1);
  }

  let source;
  try {
    source = readFileSync(input, 'utf8');
  } catch (err) {
    console.error(
      err.code === 'ENOENT'
        ? `input not found: ${input}`
        : `could not read ${input}: ${err.message}`
    );
    process.exit(1);
  }

  let svg;
  try {
    svg = renderMermaidSVG(source, THEME);
  } catch (err) {
    console.error(`mermaid render failed for ${input}: ${err.message}`);
    process.exit(1);
  }

  svg = detachFonts(svg);
  svg = namespaceIds(svg, slug);
  svg = makeResponsive(svg, width);
  svg = addA11y(svg, slug, args.title, args.desc);

  if (args.out) {
    writeFileSync(args.out, svg + '\n');
    console.error(`wrote ${args.out} (${svg.length} bytes, ${args.size})`);
  } else {
    process.stdout.write(svg + '\n');
  }
}

main();
