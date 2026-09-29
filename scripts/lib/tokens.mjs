// Load, flatten and resolve the DTCG token files in tokens/.
// Zero dependencies — Node >= 20.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';

export const THEMES = ['light', 'dark'];
const SHARED = ['primitives', 'component', 'typography'];
const REF = /^\{([^{}]+)\}$/;

const readJson = (dir, name) => JSON.parse(readFileSync(join(dir, `${name}.tokens.json`), 'utf8'));

/** Walk a token tree → Map<path, token>. Tokens inherit `$type` + `$extensions` from groups. */
function flatten(tree, layer, out = new Map(), path = [], inherited = {}) {
  const ctx = { ...inherited };
  if (tree.$type) ctx.type = tree.$type;
  if (tree.$extensions) ctx.extensions = { ...ctx.extensions, ...tree.$extensions };

  if ('$value' in tree) {
    const id = path.join('.');
    if (out.has(id)) throw new Error(`Duplicate token "${id}"`);
    if (!ctx.type) throw new Error(`Token "${id}" has no $type`);
    out.set(id, {
      id, path, layer,
      type: ctx.type,
      raw: tree.$value,
      description: tree.$description,
      extensions: ctx.extensions ?? {},
    });
    return out;
  }
  for (const [key, child] of Object.entries(tree)) {
    if (key.startsWith('$')) continue;
    flatten(child, layer, out, [...path, key], ctx);
  }
  return out;
}

/** Resolve `{a.b.c}` references (recursively, incl. inside composite values). */
function resolveAll(tokens) {
  const resolving = new Set();

  const resolveValue = (value, from) => {
    if (typeof value === 'string') {
      const m = value.match(REF);
      if (!m) return value;
      return resolveToken(m[1], from).value;
    }
    if (Array.isArray(value)) return value.map((v) => resolveValue(v, from));
    if (value && typeof value === 'object') {
      return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, resolveValue(v, from)]));
    }
    return value;
  };

  const resolveToken = (id, from) => {
    const t = tokens.get(id);
    if (!t) throw new Error(`Unknown reference {${id}}${from ? ` in "${from}"` : ''}`);
    if ('value' in t) return t;
    if (resolving.has(id)) throw new Error(`Circular reference at "${id}"`);
    resolving.add(id);
    const m = typeof t.raw === 'string' && t.raw.match(REF);
    t.ref = m ? m[1] : null; // direct alias target (for CSS var() / Dart palette names)
    t.value = resolveValue(t.raw, id);
    resolving.delete(id);
    return t;
  };

  for (const id of tokens.keys()) resolveToken(id);
  return tokens;
}

/** Follow an alias chain down to the primitive it finally points at. */
export function primitiveOf(tokens, t) {
  let cur = t;
  while (cur.ref) cur = tokens.get(cur.ref);
  return cur;
}

/** Returns { light: Map, dark: Map } — each a fully resolved token set. */
export function loadTokens(tokensDir) {
  const shared = SHARED.map((name) => [name, readJson(tokensDir, name)]);
  const semantic = Object.fromEntries(THEMES.map((th) => [th, readJson(tokensDir, `semantic.${th}`)]));

  const keys = THEMES.map((th) => [...flatten(semantic[th], 'semantic').keys()].sort().join('\n'));
  if (keys[0] !== keys[1]) {
    const [a, b] = keys.map((k) => new Set(k.split('\n')));
    const diff = [...a].filter((k) => !b.has(k)).concat([...b].filter((k) => !a.has(k)));
    throw new Error(`semantic.light / semantic.dark key mismatch: ${diff.join(', ')}`);
  }

  const out = {};
  for (const th of THEMES) {
    const map = new Map();
    for (const [name, tree] of shared) flatten(tree, name === 'primitives' ? 'primitive' : name, map);
    flatten(semantic[th], 'semantic', map);
    out[th] = resolveAll(map);
  }
  return out;
}

export function loadContrastPairs(tokensDir) {
  return JSON.parse(readFileSync(join(tokensDir, 'contrast.json'), 'utf8')).pairs;
}

// ---- WCAG contrast -------------------------------------------------------
function luminance(hex) {
  const n = hex.replace('#', '');
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(n.slice(i, i + 2), 16) / 255)
    .map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
export function contrast(a, b) {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

/** Check every pair in every theme → [{theme, fg, bg, min, ratio, ok}] */
export function checkContrast(themes, pairs) {
  const results = [];
  for (const th of THEMES) {
    for (const [fg, bg, min] of pairs) {
      const f = themes[th].get(fg), b = themes[th].get(bg);
      if (!f || !b) throw new Error(`contrast.json references unknown token: ${!f ? fg : bg}`);
      const ratio = contrast(f.value, b.value);
      results.push({ theme: th, fg, bg, min, ratio, ok: ratio >= min, fgHex: f.value, bgHex: b.value });
    }
  }
  return results;
}
