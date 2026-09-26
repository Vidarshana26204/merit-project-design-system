#!/usr/bin/env node
// Consumer drift check — run from an app repo's CI against a checkout of this
// design-system repo. Fails if a vendored token file differs from the DS build.
//
//   node <ds>/scripts/check-drift.mjs --dart lib/theme/merit_tokens.g.dart
//   node <ds>/scripts/check-drift.mjs --css app/merit-tokens.css
//
// Paths are relative to the current working directory (the app repo).
import { readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const DS = join(dirname(fileURLToPath(import.meta.url)), '..');
const SOURCES = {
  '--css': 'build/css/merit-tokens.css',
  '--dart': 'build/dart/merit_tokens.g.dart',
  '--json': 'build/json/merit-tokens.json',
};

const args = process.argv.slice(2);
if (!args.length || args.length % 2) {
  console.error('usage: check-drift.mjs [--css <file>] [--dart <file>] [--json <file>]');
  process.exit(2);
}

let failed = false;
for (let i = 0; i < args.length; i += 2) {
  const [flag, consumer] = [args[i], args[i + 1]];
  const source = SOURCES[flag];
  if (!source) { console.error(`unknown flag ${flag}`); process.exit(2); }

  let theirs;
  try { theirs = readFileSync(resolve(consumer), 'utf8'); } catch {
    console.error(`✗ ${consumer}: missing (copy ${source} from the design-system repo)`);
    failed = true; continue;
  }
  const ours = readFileSync(join(DS, source), 'utf8');
  if (theirs !== ours) {
    const a = theirs.split('\n'), b = ours.split('\n');
    const line = a.findIndex((l, n) => l !== b[n]);
    console.error(`✗ ${consumer} drifted from design-system ${source} (first diff at line ${line + 1})`);
    console.error(`    app: ${a[line] ?? '<EOF>'}\n     ds: ${b[line] ?? '<EOF>'}`);
    failed = true;
  } else {
    console.log(`✓ ${consumer} matches ${source}`);
  }
}
process.exit(failed ? 1 : 0);
