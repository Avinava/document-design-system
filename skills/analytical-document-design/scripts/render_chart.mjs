#!/usr/bin/env node
/**
 * render_chart.mjs — a chart spec to a token-themed, self-contained inline SVG.
 *
 *   node scripts/render_chart.mjs spec.json --out chart.svg
 *
 * Requires (authoring time only, Node 22.22.2 or newer): `npm ci` inside the
 * repository, or `npm i @observablehq/plot@0.6.17 jsdom@30.1.2` where the skill
 * is installed on its own.
 *
 * The spec is deliberately small. It covers the forms in
 * skills/chart-design/references/chart-forms.md and refuses the ones that
 * chart-design rejects, so the honest default is also the easy one.
 *
 *   {
 *     "form":  "bars" | "columns" | "line" | "scatter" | "waterfall",
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
 * A waterfall replaces "data", "x", "y" and "focal" with "steps" — see
 * waterfallRows() below. Every declared total must equal the sum of the steps
 * before it, or the render fails.
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

const FORMS = new Set(['bars', 'columns', 'line', 'scatter', 'waterfall']);

const STEP_KINDS = new Set(['start', 'step', 'total']);
const ROW = 36; // px per waterfall row: a 22px bar plus air for the connector

/**
 * Validate a waterfall spec and compute where each bar sits.
 *
 * A bridge's whole claim is that its parts sum to its totals, so a declared
 * total that disagrees with its steps is an error, not a rendering choice:
 * the chart would show one number and its bars another.
 *
 *   steps: [{ label, delta, kind: "start" | "step" | "total",
 *             excluded?: "reason",          // step only: drawn, never summed
 *             range?: [low, high] }]        // total only: drawn as a whisker
 */
function waterfallRows(spec) {
  if (!Array.isArray(spec.steps) || spec.steps.length === 0) {
    fail('a waterfall spec needs a non-empty "steps" array of { label, delta, kind }.');
  }
  let running = 0;
  let counted = 0;
  return spec.steps.map((s, i) => {
    const where = `steps[${i}]${s && s.label ? ` ("${s.label}")` : ''}`;
    if (!s || typeof s.label !== 'string' || !s.label.trim()) fail(`${where} needs a "label".`);
    if (typeof s.delta !== 'number' || !Number.isFinite(s.delta)) fail(`${where} needs a numeric "delta".`);
    if (!STEP_KINDS.has(s.kind)) fail(`${where} has kind "${s.kind}"; use start, step, or total.`);
    if (s.excluded != null && (s.kind !== 'step' || typeof s.excluded !== 'string')) {
      fail(`${where}: "excluded" is a reason string, and only a step can be excluded.`);
    }
    if (s.range != null && s.kind !== 'total') fail(`${where}: only a total carries a "range".`);
    if (s.kind === 'start' && counted > 0) fail(`${where}: a start can only open the bridge.`);

    const row = { i, label: s.label, delta: s.delta, kind: s.kind, excluded: s.excluded ?? null };
    if (s.kind === 'start') {
      [row.x1, row.x2] = [0, s.delta];
      running = s.delta;
      counted++;
    } else if (s.kind === 'total') {
      if (counted === 0) fail(`${where}: a total needs steps before it.`);
      if (Math.abs(s.delta - running) > 1e-9) {
        fail(
          `${where} declares a total of ${s.delta}, but the steps before it sum to ${running}.\n` +
            'Fix the steps or the total; a bridge that does not add up cannot be drawn.'
        );
      }
      if (s.range != null) {
        const [lo, hi] = Array.isArray(s.range) ? s.range : [];
        if (!(Number.isFinite(lo) && Number.isFinite(hi) && lo <= s.delta && s.delta <= hi)) {
          fail(`${where}: "range" must be [low, high] with low <= ${s.delta} <= high.`);
        }
        row.range = [lo, hi];
      }
      [row.x1, row.x2] = [0, s.delta];
    } else {
      [row.x1, row.x2] = [running, running + s.delta];
      if (!row.excluded) {
        running += s.delta;
        counted++;
      }
    }
    return row;
  });
}

function signed(n) {
  return n < 0 ? `−${Math.abs(n)}` : `+${n}`;
}

/**
 * A horizontal bridge: one row per step, read top to bottom.
 *
 * Direction is carried three ways so no reader depends on hue: a signed
 * label (+9 / −2), the side the bar grows toward, and the label sitting at
 * the bar's leading end. Totals start at zero and take the focal accent;
 * an excluded step is a dashed outline that the total does not include.
 */
function waterfallPlot(Plot, spec, rows, size, document) {
  const n = rows.length;
  const steps = rows.filter((r) => r.kind !== 'total' && !r.excluded);
  const totals = rows.filter((r) => r.kind === 'total' || r.kind === 'start');
  const excluded = rows.filter((r) => r.excluded);
  const lead = (r) => (isDecrease(r) ? Math.min(r.x1, r.x2) : Math.max(r.x1, r.x2, ...(r.range || [])));
  const text = (r) =>
    r.kind === 'total'
      ? `${r.delta}${r.range ? `  (range ${r.range[0]}–${r.range[1]})` : ''}`
      : r.excluded
        ? `${signed(r.delta)} · ${r.excluded}`
        : r.kind === 'start' ? `${r.delta}` : signed(r.delta);

  // Connectors carry the running total from one bar's end to the next bar's
  // start, so the eye can audit the arithmetic without reading numbers.
  const links = rows.slice(1).map((r, k) => {
    const prev = rows[k];
    return { x: prev.kind === 'total' || !prev.excluded ? prev.x2 : prev.x1, y1: k + 0.32, y2: k + 1 - 0.32 };
  });

  const half = 0.32;
  const right = Math.max(...rows.map((r) => Math.max(r.x1, r.x2, ...(r.range || []))));
  const left = Math.min(0, ...rows.map((r) => Math.min(r.x1, r.x2)));
  const marginTop = 16;
  const marginBottom = 44;
  const longest = Math.max(...rows.map((r) => r.label.length));
  return {
    document,
    width: size.width,
    height: marginTop + marginBottom + n * ROW,
    marginTop,
    marginBottom,
    marginLeft: Math.min(240, Math.max(96, Math.ceil(longest * 6.4) + 16)),
    marginRight: 136,
    style: { background: 'transparent' },
    // Round the domain out to whole ticks so the last bar, whisker, or
    // excluded step never ends exactly on the frame edge.
    x: { label: spec.xLabel ?? null, labelOffset: 36, grid: true, domain: niceDomain(left, right) },
    y: { domain: [n - 0.5, -0.5], axis: null },
    marks: [
      Plot.ruleX([0], { stroke: 'var(--rule-strong)' }),
      Plot.axisY(rows.map((r) => r.i), {
        tickSize: 0,
        tickPadding: 8,
        tickFormat: (i) => rows[i].label,
        label: null,
      }),
      Plot.ruleX(links, {
        x: 'x', y1: 'y1', y2: 'y2', stroke: 'var(--muted)', strokeDasharray: '2 2',
      }),
      Plot.rect(steps, {
        x1: 'x1', x2: 'x2', y1: (r) => r.i - half, y2: (r) => r.i + half,
        fill: 'var(--comparison-fill)', stroke: 'var(--muted)', strokeWidth: 1,
      }),
      Plot.rect(totals, {
        x1: 'x1', x2: 'x2', y1: (r) => r.i - half, y2: (r) => r.i + half,
        fill: 'var(--accent-tint)', stroke: 'var(--accent)', strokeWidth: 1,
      }),
      Plot.rect(excluded, {
        x1: 'x1', x2: 'x2', y1: (r) => r.i - half, y2: (r) => r.i + half,
        fill: 'none', stroke: 'var(--muted)', strokeWidth: 1, strokeDasharray: '4 3',
      }),
      // The estimate range, as a whisker through the total's end.
      Plot.ruleY(rows.filter((r) => r.range), {
        y: 'i', x1: (r) => r.range[0], x2: (r) => r.range[1], stroke: 'var(--ink)', strokeWidth: 1.5,
      }),
      Plot.ruleX(rows.filter((r) => r.range).flatMap((r) => r.range.map((x) => ({ x, i: r.i }))), {
        x: 'x', y1: (d) => d.i - 0.18, y2: (d) => d.i + 0.18, stroke: 'var(--ink)', strokeWidth: 1.5,
      }),
      // Value labels sit at each bar's leading end: right of an increase,
      // left of a decrease. Totals are set in the heavier weight.
      Plot.text(rows.filter((r) => !isDecrease(r) && r.kind !== 'total'), {
        x: lead, y: 'i', text, dx: 8, textAnchor: 'start', fill: 'var(--ink)',
      }),
      Plot.text(rows.filter(isDecrease), {
        x: lead, y: 'i', text, dx: -8, textAnchor: 'end', fill: 'var(--ink)',
      }),
      Plot.text(rows.filter((r) => r.kind === 'total'), {
        x: lead, y: 'i', text, dx: 8, textAnchor: 'start', fill: 'var(--ink)', fontWeight: 600,
      }),
    ],
  };
}

function niceDomain(lo, hi, ticks = 6) {
  const raw = (hi - lo) / ticks;
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((m) => m * mag).find((s) => s >= raw);
  return [Math.floor(lo / step) * step, Math.ceil(hi / step) * step];
}

function isDecrease(r) {
  return r.kind === 'step' && r.delta < 0;
}

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

    // data-renderer tells scripts/check_diagrams.py the layout is the
    // renderer's own, so it applies the shell and bounds rules only.
    return `<svg${attrs} width="100%" data-renderer="render_chart">`;
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
  const bridge = spec.form === 'waterfall' ? waterfallRows(spec) : null;
  if (!bridge && (!Array.isArray(spec.data) || spec.data.length === 0)) {
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

  // Imported after the spec is validated, so a spec error (a waterfall total
  // that does not add up, an unknown form) is reported even where the
  // renderer's dependencies are not installed.
  let Plot, JSDOM;
  try {
    Plot = await import('@observablehq/plot');
    ({ JSDOM } = await import('jsdom'));
  } catch {
    fail(
      '@observablehq/plot and jsdom are not installed.\n' +
        '  in the repository:      npm ci\n' +
        '  in an installed skill:  npm i @observablehq/plot@0.6.17 jsdom@30.1.2\n' +
        'Both are authoring-time only — the rendered SVG carries neither.'
    );
  }

  const dom = new JSDOM('');
  const chart = bridge
    ? Plot.plot(waterfallPlot(Plot, spec, bridge, size, dom.window.document))
    : Plot.plot({
    document: dom.window.document,
    width: size.width,
    height: size.height,
    marginLeft: spec.form === 'bars' ? 130 : 56,
    marginBottom: 44,
    style: { background: 'transparent' },
    x: {
      label: spec.xLabel ?? null,
      // Plot's default puts the axis label 3px above the frame's bottom edge,
      // so a descender in the theme's typeface pokes out of the viewBox and
      // is clipped. scripts/check_render.py measures exactly that.
      labelOffset: 36,
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
