#!/usr/bin/env node
// Subject hub header check (DS 3.5). Mixes every subject's color_hex into subject.headerBase at
// opacity.subjectTint{Light,Dark} and gates the header text roles against it in both themes.
// Subject colours live outside this public repo, so pass them in:
//
//   node scripts/check-subject-tints.mjs ../merit-content/subjects/_subject-colors.json
//
// Accepts { subjects: { KEY: { hex, streams? } } } (merit-content) or { KEY: "#RRGGBB" }.
//
// v3.7 also checks:
//   - the dark-mode rim (subject colour at opacity.subjectRimDark over the dark tint) is visible
//     against bg.app (≥ 1.5:1 — a decorative edge, so a soft floor, not 3:1);
//   - colour-blind safety: stream-mates (same `streams` entry) must stay ≥ CVD_MIN apart in OKLab
//     under simulated deuteranopia and protanopia (Machado 2009, severity 1). Reported as
//     warnings unless --strict.
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadTokens, contrast } from './lib/tokens.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const file = process.argv[2];
if (!file) {
  console.error('usage: check-subject-tints.mjs <subject-colors.json>');
  process.exit(2);
}

// Text roles allowed on a subject header (SKILL.md §5, hub header). 4.5 = text.
const ROLES = ['color.text.primary', 'color.text.secondary'];

const strict = process.argv.includes('--strict');
const CVD_MIN = 0.02;
const RIM_MIN = 1.5;
const raw = JSON.parse(readFileSync(file, 'utf8'));
const entries = Object.entries(raw.subjects ?? raw)
  .map(([key, v]) => [key, typeof v === 'string' ? v : v.hex, typeof v === 'string' ? [] : (v.streams ?? [])])
  .filter(([, hex]) => /^#[0-9a-f]{6}$/i.test(hex ?? ''));
const subjects = entries.map(([k, h]) => [k, h]);

const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));
const toHex = (c) => `#${c.map((v) => Math.round(v).toString(16).padStart(2, '0')).join('').toUpperCase()}`;
const mix = (a, b, p) => toHex(rgb(a).map((v, i) => v * p + rgb(b)[i] * (1 - p)));

const themes = loadTokens(join(ROOT, 'tokens'));
const share = { light: 'opacity.subjectTintLight', dark: 'opacity.subjectTintDark' };

let failed = 0;
let checks = 0;
for (const th of ['light', 'dark']) {
  const t = themes[th];
  const base = t.get('color.subject.headerBase').value;
  const p = t.get(share[th]).value;
  for (const [key, hex] of subjects) {
    const tint = mix(hex, base, p);
    for (const role of ROLES) {
      checks++;
      const ratio = contrast(t.get(role).value, tint);
      if (ratio < 4.5) {
        failed++;
        console.error(`  [${th}] ${key} ${hex} → ${tint}: ${role} ${ratio.toFixed(2)} < 4.5`);
      }
    }
  }
}
// ---- dark rim ----
{
  const t = themes.dark;
  const base = t.get('color.subject.headerBase').value;
  const app = t.get('color.bg.app').value;
  const rimA = t.get('opacity.subjectRimDark').value;
  for (const [key, hex] of subjects) {
    const tint = mix(hex, base, t.get(share.dark).value);
    const rim = mix(hex, tint, rimA);
    checks++;
    const ratio = contrast(rim, app);
    if (ratio < RIM_MIN) {
      failed++;
      console.error(`  [dark] ${key} rim ${rim} on bg.app: ${ratio.toFixed(2)} < ${RIM_MIN}`);
    }
  }
}

// ---- colour-blind separation of stream-mates ----
const lin = (c) => { c /= 255; return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
const MACHADO = {
  deutan: [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
  protan: [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
};
const oklab = ([r, g, b]) => {
  const l = Math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b);
  const m = Math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b);
  const s2 = Math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b);
  return [0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s2,
    1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s2,
    0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s2];
};
const sim = (hex, M) => {
  const c = rgb(hex).map(lin);
  return M.map((row) => Math.min(1, Math.max(0, row[0] * c[0] + row[1] * c[1] + row[2] * c[2])));
};
const dE = (a, b) => Math.hypot(...a.map((v, i) => v - b[i]));
const streams = new Map();
for (const [key, hex, ss] of entries) for (const st of ss) streams.set(st, [...(streams.get(st) ?? []), [key, hex]]);
const cvdWarn = [];
let cvdPairs = 0;
for (const [st, list] of streams) {
  for (let i = 0; i < list.length; i++) {
    for (let j = i + 1; j < list.length; j++) {
      for (const [kind, M] of Object.entries(MACHADO)) {
        cvdPairs++;
        const d = dE(oklab(sim(list[i][1], M)), oklab(sim(list[j][1], M)));
        if (d < CVD_MIN) cvdWarn.push(`  [${kind}] ${st}: ${list[i][0]} ${list[i][1]} vs ${list[j][0]} ${list[j][1]}: ΔE ${d.toFixed(3)} < ${CVD_MIN}`);
      }
    }
  }
}
if (cvdWarn.length) {
  console[strict ? 'error' : 'warn'](`${strict ? '✗' : '!'} CVD: ${cvdWarn.length} of ${cvdPairs} stream-mate checks below ΔE ${CVD_MIN}`);
  for (const w of cvdWarn) console[strict ? 'error' : 'warn'](w);
  if (strict) failed += cvdWarn.length;
} else if (cvdPairs) {
  console.log(`✓ CVD: ${cvdPairs} stream-mate checks (deutan + protan) ≥ ΔE ${CVD_MIN}`);
}

if (failed) {
  console.error(`✗ Subject tints: ${failed} of ${checks} checks fail`);
  process.exit(1);
}
console.log(`✓ Subject tints: ${subjects.length} subjects × 2 themes × ${ROLES.length} roles + dark rim pass`);
