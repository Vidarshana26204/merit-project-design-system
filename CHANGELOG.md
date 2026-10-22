# Changelog

Semver for tokens: **removing or renaming** a token is major, **adding** one is minor,
and **changing a value** is patch. The version lives in `package.json` and is stamped
into every generated file. The reference site (`Merit Design System.html`) carries its
own doc version (shown in its sidebar) for changes to the site itself, not the tokens.

## Docs 3.6 — 2026-10-22 (tokens unchanged at 3.5.0)

Rulings from the Flutter build and the round 10 device test, plus the web track (D21–D27). No token changes,
so the token version stays 3.5.0; the reference site shows doc v3.6.

### Changed
- **D21** one Merit coin asset family for every points mark (SKILL §5, §8, §11; reference site chips,
  leaderboard and reward cards now use `merit-coin*.svg`). Phosphor `coins` is no longer used for points.
- **D22** Sri Lankan mobile field: fixed `+94`, first digit 7 (SKILL §5).
- **D23** Me absorbs Settings; **D24** 14-day Achiever trial; **D25** share card shows username + score.
- **D26** web theming: Merit is the default tweakcn preset (SKILL §9a); student web shell and admin patchwork
  rule (SKILL §9b).
- **D27** landing hero becomes the Quilt Map (composition picked on the web wireframe round).
- SKILL §5: results points card + inline review, Today subjects layout, Compete root, Me sections.
- Wireframe board: round 10 merged into `wireframes.html` (`wireframes-r10.html` removed); trial copy 14 days;
  new Web round.
- `MIGRATION-v3.md` §2 rewritten for the web track.
- Reference site footer version fixed (it still said v3.4.0).

## 3.5.0 — 2026-10-21

Rulings from the mobile wireframe review (D18–D20). Adds tokens; no renames or removals.

### Added
- `color.timer.text`, `color.timer.warnText`, `color.timer.criticalText`: the colour-only timer
  (digits + icon, no pill). Light warns in orange-700 because butter fails as text.
- `color.feedback.warningText` (light orange-700, dark butter-300).
- `color.subject.headerBase` (light canvas-50, dark night-850) and `opacity.subjectTintLight` 0.30,
  `opacity.subjectTintDark` 0.24, `opacity.subjectRimDark` 0.40 for subject hub headers.
- `scripts/check-subject-tints.mjs` (`npm run check:subjects -- <file>`): gates text.primary and
  text.secondary on every subject's header tint in both themes. All 62 subjects pass.
- Contrast pairs for the new tokens (152 checks).
- Mobile wireframe board (`wireframes.html`, `wireframes/DECISIONS.md`, `wireframes/BACKEND-GAPS.md`).

### Changed
- SKILL §12: a tile showing progress may carry a mastery fill (greyscale base + colour clipped to
  the %); the only sanctioned alteration (D18).
- SKILL §5: timer and subject hub header specs. Reference site timer specimens are colour-only.

### Deprecated
- `color.timer.safe`, `.warn`, `.critical`, `.fg`, `.criticalFg` (pill timer). Removed in v4.

## 3.4.0 — 2026-10-18

Subject colour drives patchworks (D16 rev 5). No token changes.

### Added
- `scripts/patchwork/palette.py`: one subject `color_hex` → its palette in OKLCH (7 pastel patch
  tints around the hue incl. a soft complement, the subject colour as the solid patch plus a
  deeper twin, 3 icon accents with shades). Out-of-gamut colours lose chroma until they fit.
- `subjects/<S>/subject.json` → `color_hex` (merit-content, = backend `subjects.color_hex`) is the
  generator's input; `manifest.json` records `subject_color` per node.
- Subject colour set: one brand-safe, distinct colour per subject (merit-content
  `subjects/_subject-colors.json`, backend migration `000047_subject_colors`). Physics `#4C88D3`,
  Chemistry `#03999A`, Biology `#4E9A52`, Agricultural Science `#A6801F`, ICT `#A8B35E`.

### Changed
- **Engine v5:** every node of a subject draws its tints, solid patch and icon accent from the
  subject's palette, so a branch reads as its subject's colour. The signature includes the
  colour: changing a subject's `color_hex` re-signs its whole branch. Subjects without a colour
  fall back to the token families (warm, cool, fresh, mixed).
- **Plate sides = patches:** subject **square** (4), topic pentagon (5), subtopic **hexagon** (6),
  quest heptagon (7). Subject and subtopic shapes are swapped from 3.3.0.

## 3.3.0 — 2026-10-18

Square-in-a-square patchworks (D16 rev 4), flashcard tones and the banner action rule.
Adds tokens, no token renames or removals. The patchwork `row` variant is retired.

### Added
- `color.flashcard.fg` and `color.flashcard.<sage|sky|coral|butter|violet|blush>.{bg,wash}`: card tones;
  the wash goes tone-on-tone on a toned card. `.tone .tone-<name>` in `merit-ds.css`.
- Indexer: the "30 X Icons" packs (Colorline + Outline stacked into the filled-outline structure:
  sets `EcologyLine`, `EducationLine`, `Genetics`, `Healthcare`, `MedicalLine`), numbered packs
  (`146 - Chemistry - …` → set `Chemistry`) and avatar packs (copied verbatim to `avatars/` with
  `avatars.json`, never in the node pool).
- Feature-icon groundwork, **deferred**: `maps/_features.json` (merit-content) can reserve a pack
  icon per app feature and `generate` then writes `out/features/`. None are set; the app keeps
  Phosphor for features.

### Changed
- **Engine v4, square in a square:** fixed symmetric cuts replace the jittered radial wedges.
  Subject: hourglass X + corner triangles (4 patches); topic: + a diamond (5); subtopic: + a
  square over the diamond (6); quest: + a band under it (7). Each level nests one shape inside
  its parent's, and the child's patch is always the innermost. Uniqueness comes from tints,
  patterns, pattern angle and density only. Seams are crisp tint edges; patterns still dissolve
  toward them (the v3 gradient strips are gone). Every signature changes: regenerate and
  re-import. Output: 12.7 → 5.0 MB for 296 nodes.
- **Plate shape says the level:** subject hexagon, topic pentagon, subtopic (and quest) square,
  with rounded corners. Plates are larger and the icon box grows 124 → 136 (of 256).
- `.band` action sits on the copy's row at the right and wraps to its own right-aligned row when
  it cannot fit, instead of dropping under the copy on the left.

### Removed
- Patchwork `row` (4:1) variant. Use the tile everywhere; lists and headers show it at 40–64 px.

## 3.2.0 — 2026-10-17

Patchwork refinements (D16 rev 3) and feature banners (D17). Adds tokens, no renames or removals.

### Added
- `color.banner.{bg,fg,bandInk,disc,discInk,arc}`: feature banner tokens.
- `assets/v3/banners/<cta|achiever|promo|streak>-{field,disc}.svg`, generated by
  `scripts/brand/build_v3_brand.py` from the patchwork pattern engine.
- Patchwork `wash` variant (topics, subtopics, quests) plus `ink {light, dark}` in the manifest.

### Changed
- **Engine v3:** ink seams are gone; tints blend through a gradient strip along each ray and
  patterns dissolve near seams. Patterns are now scalable elements (`patterns.field/draw`).
  A child's added patch always carries a pattern. Every signature changes: regenerate and
  re-import. Budgets: tile 48 KB, row 72 KB, wash 40 KB. Output shrank (26 → 12.7 MB for 296
  nodes) because patterns are no longer drawn over each wedge's bounding box.
- `.band` is a patterned violet stadium with a clipped orange disc; `.band.achiever`,
  `.promo` and `.streak` pick their pattern pairs.
- Flashcard fronts are plain surfaces with the subtopic wash (§18).

### Removed
- Patchwork `corner` variant (replaced by `wash`).

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
