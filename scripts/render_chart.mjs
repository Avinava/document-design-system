#!/usr/bin/env node
/**
 * render_chart.mjs — a chart spec to a token-themed, self-contained inline SVG.
 *
 *   node scripts/render_chart.mjs spec.json --out chart.svg
 *
 * Requires: npm install @observablehq/plot jsdom   (authoring-time only)
 *
 * The spec is deliberately small. It covers the forms in
 * skills/chart-design/references/chart-forms.md and refuses the ones that
 * chart-design rejects, so the honest default is also the easy one.
 *
 *   {
 *     "form":  "bars" | "columns" | "line" | "scatter",
 *     "id":    "fn-footprint",
 *     "title": "Ingestion holds 41% of the footprint",
 *     "desc":  "Nine functions ranked by size. Ingestion holds 41 percent of
 *               the 1.8 million unit total, more than the next three combined.",
 *     "data":  [ { "k": "Ingestion", "v": 41 }, ... ],
 *     "x":     "v",
 *     "y":     "k",
 *     "focal": "Ingestion",
 *     "xLabel": "Share of included total (%)",
 *     "yLabel": null,
 *     "series": "name",        // line/scatter only
 *     "size":  "doc-inline",
 *     "zero":  true            // bars/columns: enforced, see below
 *   }
 *
 * Observable Plot (ISC) does the layout. This wrapper exists because Plot's
 * raw output is not safe to drop into a designed document:
 *
 *  1. It hardcodes `--plot-background: white` and a `font-family` attribute,
 *     neither of which know about the document's theme.
 *  2. It sets fixed width/height attributes, which stop it scaling into print.
 *  3. It emits no accessibility shell.
 *  4. Its default mark colors are not the document's tokens.
 */

import { readFileSync, writeFileSync } from 'node:fs';

const SIZES = {
  'doc-inline': { width: 720, height: 320 },
  'full-width': { width: 1100, height: 420 },
  'print-portrait': { width: 640, height: 300 },
  'print-landscape': { width: 980, height: 380 },
};

const FORMS = new Set(['bars', 'columns', 'line', 'scatter']);

function parseArgs(argv) {
  const args = {};
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

function fail(msg) {
  console.error(msg);
  process.exit(1);
}

function buildMarks(Plot, spec) {
  const { form, data, x, y, focal, series } = spec;

  // The accent goes on one mark via a per-datum fill rather than by splitting
  // the data into two marks. Splitting looks tempting but breaks the chart:
  // each mark derives its own scale domain, so the focal datum and the rest
  // end up on different axes and the bars fail to render at all.
  //
  // These are var() references, not literals, so the fill still resolves
  // through the theme — and the focal bar is labelled too, so the chart does
  // not depend on the color being seen.
  const isFocal = (d) => focal != null && (d[y] === focal || d[x] === focal);
  const fill = (d) => (isFocal(d) ? 'var(--accent-tint)' : 'var(--comparison-fill)');
  const stroke = (d) => (isFocal(d) ? 'var(--accent)' : 'var(--muted)');

  if (form === 'bars') {
    return [
      Plot.barX(data, { x, y, sort: { y: '-x' }, fill, stroke, strokeWidth: 1 }),
      Plot.ruleX([0], { stroke: 'var(--rule-strong)' }),
    ];
  }

  if (form === 'columns') {
    return [
      Plot.barY(data, { x, y, fill, stroke, strokeWidth: 1 }),
      Plot.ruleY([0], { stroke: 'var(--rule-strong)' }),
    ];
  }

  if (form === 'line') {
    return [
      // Straight segments, never a spline: curve fitting invents measurements
      // between points that were never taken.
      Plot.line(data, {
        x, y, z: series, curve: 'linear',
        stroke: series ? undefined : 'var(--accent)',
        strokeWidth: 1.5,
      }),
      Plot.ruleY([0], { stroke: 'var(--rule-strong)' }),
    ];
  }

  return [Plot.dot(data, { x, y, fill, stroke, strokeWidth: 1, r: 3.5 })];
}

/**
 * Strip Plot's hardcoded presentation and route it through the token system.
 */
function detheme(svg) {
  return svg
    // Plot writes a literal white background into its scoped style block.
    .replace(/--plot-background:\s*[^;]+;/g, '--plot-background: transparent;')
    // and a system font stack as an attribute on the root <svg>.
    .replace(/font-family="[^"]*"/g, 'font-family="var(--sans)"');
}

/**
 * Make the SVG scale rather than sit at a fixed pixel size.
 *
 * Every edit here is scoped to the ROOT <svg> open tag. Stripping width/height
 * globally also strips them from every <rect>, which removes the bars while
 * leaving the axes and labels intact — a chart that looks merely empty rather
 * than broken.
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

function addA11y(svg, slug, title, desc) {
  svg = svg.replace(
    /<svg([^>]*)>/,
    `<svg$1 role="img" aria-labelledby="${slug}-title ${slug}-desc">`
  );
  const block =
    `\n  <title id="${slug}-title">${escapeXml(title)}</title>` +
    `\n  <desc id="${slug}-desc">${escapeXml(desc)}</desc>`;
  return svg.replace(/(<svg[^>]*>)/, `$1${block}`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const specPath = args._[0];
  if (!specPath) fail('usage: render_chart.mjs <spec.json> [--out chart.svg]');

  let Plot, JSDOM;
  try {
    Plot = await import('@observablehq/plot');
    ({ JSDOM } = await import('jsdom'));
  } catch {
    fail(
      '@observablehq/plot and jsdom are not installed.\n' +
        '  npm install @observablehq/plot jsdom\n' +
        'Both are authoring-time only — the rendered SVG carries neither.'
    );
  }

  let spec;
  try {
    spec = JSON.parse(readFileSync(specPath, 'utf8'));
  } catch (err) {
    // Without this, a missing file or a stray comma surfaces as a raw Node
    // stack trace, which buries the one line that says what to fix.
    fail(
      err.code === 'ENOENT'
        ? `spec not found: ${specPath}`
        : `${specPath} is not valid JSON: ${err.message}`
    );
  }

  if (!FORMS.has(spec.form)) {
    fail(
      `unknown form "${spec.form}". Supported: ${[...FORMS].join(', ')}.\n` +
        'Pie, donut, radar, and dual-axis charts are intentionally unsupported — ' +
        'see skills/chart-design/references/chart-forms.md for what to use instead.'
    );
  }
  if (!spec.title || !spec.desc) {
    fail(
      'spec needs "title" and "desc".\n' +
        'The title should state the finding, not the variables. The desc is what ' +
        'a screen-reader user gets instead of the chart.'
    );
  }
  if (!Array.isArray(spec.data) || spec.data.length === 0) {
    fail('spec needs a non-empty "data" array.');
  }

  const size = SIZES[spec.size || 'doc-inline'];
  if (!size) fail(`unknown size "${spec.size}". Known: ${Object.keys(SIZES).join(', ')}`);

  const slug = (spec.id || 'chart').toLowerCase().replace(/[^a-z0-9]+/g, '-');

  // Bar and column length encodes magnitude, so the baseline is not negotiable.
  // A truncated bar axis multiplies apparent differences by an arbitrary factor.
  // Plot's bar marks already baseline at zero; `zero: true` keeps that explicit
  // and survives someone later adding a line mark to the same plot.
  const isBar = spec.form === 'bars' || spec.form === 'columns';

  const dom = new JSDOM('');
  const chart = Plot.plot({
    document: dom.window.document,
    width: size.width,
    height: size.height,
    marginLeft: spec.form === 'bars' ? 130 : 56,
    marginBottom: 44,
    style: { background: 'transparent' },
    x: {
      label: spec.xLabel ?? null,
      grid: spec.form !== 'bars',
      ...(isBar && spec.form === 'bars' ? { zero: true } : {}),
      // For columns the x axis is categories (years, months, buckets), not a
      // continuous measure. Without this, year labels that look like numbers
      // get treated as a linear scale and the columns land in the wrong places.
      ...(spec.form === 'columns' ? { type: 'band' } : {}),
    },
    y: {
      label: spec.yLabel ?? null,
      grid: spec.form === 'bars' ? false : true,
      ...(isBar && spec.form === 'columns' ? { zero: true } : {}),
    },
    marks: buildMarks(Plot, spec),
  });

  let svg = chart.outerHTML ?? String(chart);
  svg = detheme(svg);
  svg = makeResponsive(svg, size.width);
  svg = addA11y(svg, slug, spec.title, spec.desc);

  if (args.out) {
    writeFileSync(args.out, svg + '\n');
    console.error(`wrote ${args.out} (${svg.length} bytes, ${spec.form}, ${spec.size || 'doc-inline'})`);
  } else {
    process.stdout.write(svg + '\n');
  }
}

main();
