# Changelog

Semver for tokens: **removing or renaming** a token is major, **adding** one is minor,
and **changing a value** is patch. The version lives in `package.json` and is stamped
into every generated file. The reference site (`Merit Design System.html`) carries its
own doc version (shown in its sidebar) for changes to the site itself, not the tokens.

## Site v2.2 — 2026-09-29

Phase 4: reference-site rebuild. No token value or name changes — `package.json`
stays 2.1.0.

### Added
- Twelve new sections: Spacing & Layout, Motion, States & Focus, Quiz Components,
  Feedback & Empty States, Iconography, Tri-lingual Type, Data Viz, Density Modes,
  Landing Specimen, Tokens Reference, Changelog.
- **Tokens Reference (§24)** reads live computed values off
  `build/css/merit-tokens.css` at page load via `buildTokenTable()` in
  `merit-ds.js` — the hex values shown can never drift from what's shipped
  (only the token *name* list needs manual sync when a token is added/removed).
- Quiz option states (`.qopt`), timer (`.qtimer`), empty states, toasts, skeleton
  shimmer, density comparison, motion demo, and a live focus-ring tab-through, all
  new CSS in `merit-ds.css`.
- Nav renumbered 00–25 across four groups (Foundations, Components, Patterns,
  Reference); all existing section anchors unchanged.

## 2.1.0 — 2026-09-26

### Added
- Sinhala/Tamil font fallbacks. Every `fontFamily` stack now includes
  `Noto Sans Sinhala` and `Noto Sans Tamil` before system fonts. Flutter gets
  `MeritFonts.fallback`, and every `MeritTypeScale` style sets
  `fontFamilyFallback`. Consumers must bundle or host the Noto files.

### Changed
- The Dart output is renamed `build/dart/merit_tokens.dart` (it was `.g.dart`,
  which consumer repos gitignore).

## 2.0.0 — 2026-09-26

Token pipeline (IMPROVEMENT-PLAN Phase 1).

### Added
- `tokens/*.tokens.json`: a single source of truth in W3C DTCG format. It has three
  layers (primitive → semantic → component) plus the typography scale.
- `npm run build` (`scripts/build-tokens.mjs`, zero dependencies) generates:
  - `build/css/merit-tokens.css`: `--merit-*` custom properties. Light is on `:root`;
    dark is on `.dark` / `[data-theme="dark"]`; there are hard-shadow composites
    `--merit-shadow-s1…s5` and a typography var group per style.
  - `build/dart/merit_tokens.dart`: `MeritPalette`, `MeritSpace`, `MeritRadii`,
    `MeritBorderWidth`, `MeritShadowOffset`, `MeritMotion`, `MeritOpacity`,
    `MeritTouch`, `MeritSize`, `MeritFonts`, `MeritTypeScale`, and the
    `MeritSemanticColors` ThemeExtension (with `shadowS1…S5`, `lerp`, and
    `context.meritColors`). The class names don't collide with the existing
    `merit_theme.dart`.
  - `build/json/merit-tokens.json`: resolved values per theme.
  - The SKILL.md §10 token reference block.
- **Contrast gate**: 45 fg/bg pairs × light/dark are checked against WCAG AA on
  every build (`tokens/contrast.json`). The build fails below the minimum.
- `npm run check`: CI mode. It fails when outputs are stale or contrast fails
  (`.github/workflows/tokens.yml`).
- `scripts/check-drift.mjs`: for app-repo CI. It fails if a vendored copy of a
  generated file differs from this repo's build.
- New token groups: spacing, radii (7-step), border widths, hard-shadow offsets,
  motion (durations + curves), opacity, z-index, breakpoints, touch target,
  quiz-option states, timer, tier, grade A–F, subject category 1–6, chart 1–5.

### Changed
- `merit-ds.css` now imports the generated tokens. Its short names (`--purple`,
  `--text`, …) are aliases of `--merit-*` tokens. The site renders the same
  except for the accessibility values below.
- **Accessibility value changes:**
  - `text.tertiary` (text-mute) light: `#7A6C7A` → `#685A68` (4.37 → 5.72:1 on cream).
  - Dark-mode error: `#FF9A9A`, replacing `#C4393A` (3.39 → 8.78:1).
  - Dark-mode link/focus purple: `#B48CE8` (3.76 → 6.67:1).
  - Light link text: purple-700 `#6E36B8` (purple-500 is fills only).

## 1.1.0 — 2026-09-26

Phase 0. Recorded decisions D1–D7; fonts are self-hosted; SKILL.md snippets match
the real Flutter theme; there are no 800 weights; the tab label is 11px; the
tweaks panel is vanilla JS.

## 1.0.0

Initial design system: brand, colour, type, signature look, components, and patterns.
