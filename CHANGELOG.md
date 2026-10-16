# Changelog

Semver for tokens: **removing or renaming** a token is major, **adding** one is minor,
and **changing a value** is patch. The version lives in `package.json` and is stamped
into every generated file. The reference site (`Merit Design System.html`) carries its
own doc version (shown in its sidebar) for changes to the site itself, not the tokens.

## 3.1.0 — 2026-10-16

Hierarchy patchworks (D16). Adds tokens, no renames or removals.

### Added
- `color.patchwork.{seam,plate,iconLine,iconShade}`: theme-fixed patchwork tokens
  (`--merit-patchwork-*`, `MeritColors.patchwork*`).
- `scripts/patchwork/`: a deterministic generator for per-node patchworks (engine v2).
  - **Radial layout:** every patch is a wedge touching the centred icon. Subjects have 4
    patches, topics 5 and subtopics 6; each child keeps its parent's patches in order and adds
    one new patch that is unique among its siblings. The row variant shares the tile's rays,
    with the icon centred.
  - It has 16 geometry-expanded patterns, polygon and arc layouts, reference-style icon
    recolouring, and a signature + salt registry for global uniqueness and size budgets.
  - Its CLI is `index` / `suggest` / `generate` / `audit` / `demo`, and pytest covers it.
  - The licensed icon pack and production output live in the private `merit-content` repo.
- `assets/v3/patchwork-demo/`: a licence-safe demo set (MIT Phosphor glyphs) with all four
  variants, plus the 16 pattern swatches.
- SKILL.md §12 (Hierarchy patchworks) and DECISIONS D16.

### Changed
- `assets/v3/spots/*`: redrawn as **line art** (a blob plus an ink line drawing), so empty and
  error states can't be mistaken for hierarchy nodes.
- `color.category.*` is now the chip tint and the patchwork **fallback** tint (description only).
- Reference site:
  - §21 is now "Hierarchy patchworks".
  - The hero, cards and screen specimens use the demo patchworks.
  - The landing "practise" modes use Phosphor duotone instead of tiles.
  - Sparkles are removed from patchwork clusters.
- SKILL.md:
  - §6: calm screens allow only the subtopic `corner` on note and flashcard tiles.
  - §9: rewritten.

### Removed
- `assets/v3/tiles/*` (six shared category tiles), replaced by per-node patchworks.

## Site v2.3 — 2026-10-15

Brand refresh. No token value or name changes; `package.json` stays 2.1.0.

### Added
- `assets/brand/`: the cube-in-pyramid mark redrawn as clean SVG (no baked-in text) in the
  DS style. Includes dark, small, cube-only, one-colour and Achiever versions, the app icon,
  Android adaptive and monochrome icons, and MERIT / PROJECT lockups (horizontal, dark,
  stacked), with PNGs in `assets/brand/png/`.
- `merit-coin` (Merit Points): gold pyramid coin, small cut, dark version, and Fill/Bold glyphs.
- `scripts/brand/build_brand.py` generates all of the above.
- SKILL.md §11 covers logo and coin usage.

### Changed
- Reference site §21 Logo Usage was rebuilt around the new files. The sidebar mark uses
  `merit-mark-dark.svg`.

### Removed
- `assets/logo.png`, the old 1536×1024 AI raster with text baked into the cube.

## 3.0.0 — 2026-10-16

A full reinvention, inspired by the MindInventory "Online Learning" reference. Decisions D8–D15
are in `DECISIONS-v3.md` and the research is in `research/v3/`. The reference site
(`Merit Design System.html`) has **not** been rebuilt for v3 yet (that is Phase D). Until then it
renders against renamed tokens and will look broken.

### Changed: values (semantic names kept)
- **Palette (D10):**
  - `bg.app` is the warm canvas `#FBFAF4`. `bg.brand` is sand `#FCEBD3`.
  - Text is ink-slate (`#1E1B2E` / `#4A4760` / `#68667F`).
  - `action.primary` is **orange `#F65E16` with an ink label** (D9).
  - `action.accent` is violet `#54306C`, with a white label.
  - Links and the focus ring are violet `#663696`.
  - Success is sage, warning is butter, and error is `#C7362F`.
- **Dark mode (D15):** a violet-black base (`#17121F` / `#221B2C`), orange lifted to `#FF8A4C` and
  violet links at `#C9B3EA`.
- `text.onPrimary` is now **ink**, not white. White text on brand orange fails WCAG.
- `text.onAccent` is white in light mode and ink in dark mode.
- `border.default` is now the input/control edge (`#68667F` light, `#9C94AC` dark). It was the black
  signature outline.
- Border widths: `hairline` 1px (was 1.5), `base` 1.5px (was 2).
- Radii: `md` 16 (was 14), `lg` 20 (was 18). Cards use `xl` 24.
- `fontFamily.display` is **General Sans** (D8). The Flutter family name is `GeneralSans`.
- The display, title and emphasis styles use weight 600.
- Component tokens were recoloured: quiz options, timer, tier, reward, grade A–F, category 1–6 and
  chart 1–5.

### Added
- **Semantic:**
  - `surface.feature`
  - `text.eyebrow`, `text.onPrimaryStrong`, `text.onFeature`, `text.onWarning`
  - `border.strong` (the ink outline for chips and illustration)
  - `action.primaryStrong` (burnt orange with a white label), `action.accentPressed`
  - `feedback.successSubtle`
  - `decor.sparkle`, `decor.sparkleWarm`, `decor.underline`, `decor.connector`
- **Elevation (D11):** soft, themed shadows `elevation.e0–e3` (`$type: shadow`). They generate as
  CSS `--merit-elevation-e*` and as Dart `context.meritColors.elevationE0…E3` (`List<BoxShadow>`).
- **Type:** `type.emphasis.lg/md` (italic) and `type.eyebrow`. The generators emit
  `--merit-type-*-style` and `fontStyle: FontStyle.italic`.
- **Component:**
  - `timer.fg`, `timer.criticalFg`
  - `tier.achiever.cap`
  - `reward.streak`, `reward.pointsFill`
  - `category.outline`
- **Primitives:** `canvas`, `ink.500/700/900`, `orange`, `coral`, `sand.100/300`, `violet`, `sage`,
  `butter`, `blush`, `sky`, `night`, `mist`.
- **Contrast gate:** 63 pairs × light/dark = 126 checks. New checks cover orange as a non-text fill
  (≥3:1 on canvas), the eyebrow, the feature band, and quiz-option borders.
- The pipeline supports 8-digit `#RRGGBBAA` colours (Dart output is `0xAARRGGBB`).

### Removed (rename map v2 → v3)
| v2 | v3 |
|---|---|
| `shadowOffset.s1–s5`, `--merit-shadow-s1…s5`, `--merit-shadow-offset-*`, Dart `MeritShadowOffset`, `context.meritColors.shadowS1…S5` | `elevation.e1` (s1–s3), `e2` (s4), `e3` (s5, dialogs) |
| `shadow.color` / `--merit-shadow-color` / `shadowColor` | none (each elevation layer carries its own colour) |
| `borderWidth.heavy` (3px) | `borderWidth.strong` (2px) |
| `fontFamily.landing` (School Times) | `fontFamily.display` (D13) |
| `purple.100/300/500/700` | `violet.100/300/500/700` (new values; brand fill is now `violet.700`) |
| `yellow.100/400/500/900` | `butter.100/300/500` |
| `mint.100/400/500/800` | `sage.100/300/700` |
| `cream.100/200` | `canvas.50` / `sand.100` |
| `sand.200` | `canvas.200` |
| `ink.text`, `ink.600/700/800/850/900` | `ink.900`; dark surfaces move to `night.600–900` |
| `mauve.*` | `ink.500/700` (light), `mist.300/400` (dark) |
| `pink.300`, `blue.300` | `blush.300`, `sky.300` |
| `red.50`, `red.800` | none (`red.100/300/600/900` remain, with new values) |
| `black` | `ink.900` (`border.strong`) |

Consumers stay on their v2 pin (`.design-tokens-ref`, the vendored `merit_tokens.dart`) until they
migrate. See `MIGRATION-v3.md` (Phase D).

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
