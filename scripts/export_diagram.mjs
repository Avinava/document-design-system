#!/usr/bin/env node
/**
 * export_diagram.mjs — turn a token-themed SVG figure into a standalone SVG or PNG.
 *
 *   node scripts/export_diagram.mjs figure.svg --theme executive-navy --out figure.svg
 *   node scripts/export_diagram.mjs figure.svg --theme executive-navy --format png --scale 2
 *
 * A figure written to this repo's rules colours itself with var(--…) tokens, so
 * it only looks right where a theme is loaded. An <img>, an email, a slide
 * made elsewhere, or a README has no theme. This resolves every token against
 * one theme in Chromium and writes literal colours and fonts:
 *
 *   --format svg   (default) the same figure with tokens baked to literals
 *   --format png   a raster at --scale (default 2), paper background unless --transparent
 *
 * The source file is never modified. Keep the tokened SVG as the master and
 * export per theme.
 *
 * Requires (authoring time only): `npm ci` inside the repository, or
 * `npm i playwright@1.63.0` where the skill is installed on its own; then
 * `npx playwright install chromium`. Check with scripts/diagram_doctor.py.
 */

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const FLAGS = new Set(['transparent']);
const BAKED = ['fill', 'stroke', 'stop-color', 'flood-color', 'color', 'font-family'];

function parseArgs(argv) {
  const args = { format: 'svg', scale: '2' };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--') && FLAGS.has(a.slice(2))) args[a.slice(2)] = true;
    else if (a.startsWith('--')) args[a.slice(2)] = argv[++i];
    else rest.push(a);
  }
  args._ = rest;
  return args;
}

function fail(message) {
  console.error(message);
  process.exit(1);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const input = args._[0];
  if (!input || !args.theme) {
    fail(
      'usage: export_diagram.mjs <figure.svg> --theme <name> [--format svg|png] [--out file] ' +
        '[--scale 2] [--transparent]'
    );
  }
  if (!['svg', 'png'].includes(args.format)) fail(`unknown --format "${args.format}". Known: svg, png`);
  const scale = Number(args.scale);
  if (!(scale >= 1 && scale <= 8)) fail('--scale must be between 1 and 8');

  const inputPath = resolve(input);
  if (!existsSync(inputPath)) fail(`not found: ${inputPath}`);
  const themePath = resolve(ROOT, 'core', 'themes', `${args.theme}.css`);
  if (!/^[a-z0-9-]+$/.test(args.theme) || !existsSync(themePath)) {
    fail(`unknown theme "${args.theme}": no core/themes/${args.theme}.css`);
  }

  const source = readFileSync(inputPath, 'utf8');
  if (/<!DOCTYPE|<!ENTITY|<script/i.test(source)) fail('refusing a figure with a DOCTYPE, entity or <script>');
  const box = /viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)\s*"/.exec(source);
  if (!box) fail('the figure has no viewBox; run scripts/check_diagrams.py');
  const [width, height] = [Math.ceil(Number(box[1])), Math.ceil(Number(box[2]))];

  let chromium;
  try {
    ({ chromium } = await import('playwright'));
  } catch {
    fail(
      'playwright is not installed.\n' +
        '  in the repository:      npm ci && npx playwright install chromium\n' +
        '  in an installed skill:  npm i playwright@1.63.0 && npx playwright install chromium\n' +
        'It is an authoring-time dependency only.'
    );
  }

  const css =
    readFileSync(resolve(ROOT, 'core', 'base.css'), 'utf8') + '\n' + readFileSync(themePath, 'utf8');
  const background = args.transparent ? 'transparent' : 'var(--paper)';
  const html =
    `<!doctype html><html data-theme="${args.theme}"><head><meta charset="utf-8"><style>${css}</style>` +
    `<style>html,body{margin:0;background:${background}}svg{display:block;width:${width}px;height:auto}</style>` +
    `</head><body>${source.replace(/^<\?xml[^>]*>/, '')}</body></html>`;

  const out = args.out || inputPath.replace(/\.svg$/i, `.${args.theme}.${args.format}`);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: scale });
  const problems = [];
  page.on('requestfailed', (r) => problems.push(`request failed: ${r.url()}`));
  await page.setContent(html, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);

  if (args.format === 'png') {
    await page.locator('svg').first().screenshot({ path: out, omitBackground: Boolean(args.transparent) });
  } else {
    const baked = await page.evaluate((props) => {
      const svg = document.querySelector('svg');
      for (const el of [svg, ...svg.querySelectorAll('*')]) {
        const style = getComputedStyle(el);
        for (const prop of props) {
          const raw = el.getAttribute(prop) ?? '';
          const inline = el.style.getPropertyValue(prop);
          if (raw.includes('var(') || inline.includes('var(')) {
            const value = style.getPropertyValue(prop); // read before the token is removed
            el.style.removeProperty(prop);
            el.setAttribute(prop, value);
          }
        }
        if (!el.getAttribute('style')) el.removeAttribute('style');
      }
      return new XMLSerializer().serializeToString(svg);
    }, BAKED);
    writeFileSync(out, baked + '\n');
  }
  await browser.close();

  console.error(`wrote ${out}`);
  if (problems.length) {
    console.error('\nissues during render:');
    for (const p of new Set(problems)) console.error(`  ${p}`);
  }
}

main();
