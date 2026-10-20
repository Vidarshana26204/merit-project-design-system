#!/usr/bin/env node
// Subject hub header check (DS 3.5). Mixes every subject's color_hex into subject.headerBase at
// opacity.subjectTint{Light,Dark} and gates the header text roles against it in both themes.
// Subject colours live outside this public repo, so pass them in:
//
//   node scripts/check-subject-tints.mjs ../merit-content/subjects/_subject-colors.json
//
// Accepts { subjects: { KEY: { hex } } } (merit-content) or { KEY: "#RRGGBB" }.
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

const raw = JSON.parse(readFileSync(file, 'utf8'));
const subjects = Object.entries(raw.subjects ?? raw)
  .map(([key, v]) => [key, typeof v === 'string' ? v : v.hex])
  .filter(([, hex]) => /^#[0-9a-f]{6}$/i.test(hex ?? ''));

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
if (failed) {
  console.error(`✗ Subject tints: ${failed} of ${checks} checks fail`);
  process.exit(1);
}
console.log(`✓ Subject tints: ${subjects.length} subjects × 2 themes × ${ROLES.length} roles pass`);
