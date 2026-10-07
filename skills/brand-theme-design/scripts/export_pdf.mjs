#!/usr/bin/env node
/**
 * export_pdf.mjs — render a document or deck to PDF for print verification.
 *
 *   node scripts/export_pdf.mjs report.html --out report.pdf
 *   node scripts/export_pdf.mjs deck.html   --out deck.pdf --preset deck
 *
 * Requires: npm install playwright && npx playwright install chromium
 *
 * Chromium is the right engine here for one reason: the artifact was authored
 * against Chrome, so only Chrome's print path guarantees the PDF matches what
 * the reader sees. WeasyPrint is lighter and produces smaller files, but it is
 * a different engine — color-mix(), grid, and container queries do not render
 * identically, and this design system uses all three.
 *
 * The point of this script is INSPECTION. Print CSS existing is not evidence
 * that printing works. Export the PDF and look at it.
 */

import { existsSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const PRESETS = {
  document: { format: 'A4', landscape: false, margin: undefined },
  letter: { format: 'Letter', landscape: false, margin: undefined },
  // The deck template sets @page itself; preferCSSPageSize honors it so a
  // 1280x720 slide lands one-per-page instead of being fitted to A4.
  deck: { preferCSSPageSize: true, margin: { top: 0, right: 0, bottom: 0, left: 0 } },
};

function parseArgs(argv) {
  const args = { preset: 'document' };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) args[a.slice(2)] = argv[++i];
    else rest.push(a);
  }
  args._ = rest;
  return args;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const input = args._[0];

  if (!input) {
    console.error(
      'usage: export_pdf.mjs <input.html> [--out file.pdf] [--preset document|letter|deck]'
    );
    process.exit(1);
  }

  const inputPath = resolve(input);
  if (!existsSync(inputPath)) {
    console.error(`not found: ${inputPath}`);
    process.exit(1);
  }

  const preset = PRESETS[args.preset];
  if (!preset) {
    console.error(`unknown preset "${args.preset}". Known: ${Object.keys(PRESETS).join(', ')}`);
    process.exit(1);
  }

  let chromium;
  try {
    ({ chromium } = await import('playwright'));
  } catch {
    console.error(
      'playwright is not installed.\n' +
        '  npm install playwright && npx playwright install chromium\n' +
        'It is an authoring-time dependency only.'
    );
    process.exit(1);
  }

  const out = args.out || inputPath.replace(/\.html?$/i, '.pdf');

  const browser = await chromium.launch();
  const page = await browser.newPage();

  const problems = [];
  page.on('pageerror', (e) => problems.push(`page error: ${e.message}`));
  page.on('requestfailed', (r) => problems.push(`request failed: ${r.url()}`));

  await page.goto(pathToFileURL(inputPath).href, { waitUntil: 'networkidle' });

  // Web fonts render as fallbacks if the PDF is produced before they load, and
  // the resulting document looks subtly wrong in a way that is easy to miss.
  await page.evaluate(() => document.fonts.ready);

  await page.pdf({
    path: out,
    printBackground: true,
    ...preset,
  });

  await browser.close();

  console.error(`wrote ${out}`);

  if (problems.length) {
    console.error('\nissues during render:');
    for (const p of new Set(problems)) console.error(`  ${p}`);
    console.error(
      '\nA failed request usually means a web font did not load, so the PDF is\n' +
        'showing fallback metrics. Inline the fonts (scripts/inline_fonts.py) if\n' +
        'the document must render identically offline.'
    );
  }

  console.error(
    '\nNow open the PDF and check:\n' +
      '  - page one carries the title, as-of date, and primary metric\n' +
      '  - no chart or table is clipped horizontally\n' +
      '  - no blank pages\n' +
      '  - no heading stranded at the bottom of a page\n' +
      '  - table headers repeat across pages\n' +
      '  - it still reads in grayscale\n' +
      'Page count alone proves nothing — a drop in pages can mean clipped overflow.'
  );
}

main();
