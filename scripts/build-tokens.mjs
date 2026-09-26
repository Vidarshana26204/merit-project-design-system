#!/usr/bin/env node
// Merit token build.
//   node scripts/build-tokens.mjs          → write build/* + SKILL.md token block
//   node scripts/build-tokens.mjs --check  → write nothing; exit 1 if outputs are stale
// Both modes run the WCAG contrast gate and exit 1 on any failing pair.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadTokens, loadContrastPairs, checkContrast } from './lib/tokens.mjs';
import {
  formatCss, formatDart, formatJson, formatSkillBlock, SKILL_BEGIN, SKILL_END,
} from './lib/formats.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const check = process.argv.includes('--check');

const OUTPUTS = {
  css: 'build/css/merit-tokens.css',
  dart: 'build/dart/merit_tokens.g.dart',
  json: 'build/json/merit-tokens.json',
};

const read = (p) => { try { return readFileSync(join(ROOT, p), 'utf8'); } catch { return null; } };

function main() {
  const { version } = JSON.parse(read('package.json'));
  const tokensDir = join(ROOT, 'tokens');
  const themes = loadTokens(tokensDir);

  // ---- contrast gate ----
  const results = checkContrast(themes, loadContrastPairs(tokensDir));
  const failed = results.filter((r) => !r.ok);
  if (failed.length) {
    console.error(`✗ Contrast gate: ${failed.length} failing pair(s)`);
    for (const r of failed) {
      console.error(`  [${r.theme}] ${r.fg} ${r.fgHex} on ${r.bg} ${r.bgHex}: ${r.ratio.toFixed(2)} < ${r.min}`);
    }
    process.exit(1);
  }
  console.log(`✓ Contrast gate: ${results.length} checks pass`);

  // ---- render ----
  const files = {
    [OUTPUTS.css]: formatCss(themes, version),
    [OUTPUTS.dart]: formatDart(themes, version),
    [OUTPUTS.json]: formatJson(themes, version),
  };
  const skill = read('SKILL.md');
  const b = skill.indexOf(SKILL_BEGIN), e = skill.indexOf(SKILL_END);
  if (b === -1 || e === -1) throw new Error('SKILL.md is missing the MERIT-TOKENS markers');
  files['SKILL.md'] = skill.slice(0, b) + formatSkillBlock(themes, results, version) + skill.slice(e + SKILL_END.length);

  const stale = Object.entries(files).filter(([p, content]) => read(p) !== content).map(([p]) => p);

  if (check) {
    if (stale.length) {
      console.error(`✗ Stale outputs (run \`npm run build\`): ${stale.join(', ')}`);
      process.exit(1);
    }
    console.log('✓ Outputs up to date');
    return;
  }
  for (const [p, content] of Object.entries(files)) {
    mkdirSync(dirname(join(ROOT, p)), { recursive: true });
    writeFileSync(join(ROOT, p), content);
  }
  console.log(stale.length ? `✓ Wrote ${stale.join(', ')}` : '✓ Nothing changed');
}

try {
  main();
} catch (err) {
  console.error(`✗ ${err.message}`);
  process.exit(1);
}

