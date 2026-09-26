# Merit Design System — Review & v2 Improvement Plan

**Date:** 2026-09-26 · **Scope:** `merit-project-design-system` (v1.0), checked against
`merit-project-flutter` (shipped app) and `merit-project-frontend` (Next.js 16 +
shadcn web: landing, admin, student, contributor).

---

## 0. TL;DR

The v1 brand is strong and distinctive: neo-brutalist, sticker-sheet, gamified.
**Keep the look. Fix how it's delivered.** The main problem is not aesthetics. It is
**drift**. There are three sources of truth, and they already disagree:

| Role | DS (`merit-ds.css` / SKILL.md) | Flutter (`MeritColors`) | Web (`globals.css`) |
|---|---|---|---|
| `yellow` | `#FFCC00` | **`#F2D43B`** (DS calls this "soft") | `#FFCC00` |
| `mint` | `#9ED5B7` | **`#9CE7C8`** (DS "soft") | `#9ED5B7` light / `#9CE7C8` dark |
| `cream` | `#FFEFD7` | **`#FFF7ED`** (DS "cream-warm") | `#FFEFD7` bg |
| `ink` | `#312A31` | **`#29261B`** (DS "text") | both, mixed |
| Page background | cream `#FFEFD7` | **white** `#FFFFFF` | cream `#FFEFD7` |
| Checkbox on | mint + ink ✓ | **purple** + white ✓ | shadcn default |
| Hard shadows | mandatory | 57 `BoxShadow`s, **20 blurred** | **none**: 72 soft `shadow-sm/md/lg` |

The same token name points to a different hex on each platform. `SKILL.md` is also what
AI agents read, so it hands out Flutter snippets that don't match the real
`merit_theme.dart`. Every new screen widens the gap.

**v2 goals, in priority order:**
1. **One token source**, generated into CSS and Dart, with CI that fails on drift.
2. **Accessibility pass.** Five token pairs fail WCAG AA today (§3).
3. **Tri-lingual typography that actually works.** No Sinhala or Tamil font ships anywhere (§4).
4. **Complete the component catalogue**: quiz, feedback, and state components are missing.
5. **Retrofit** Flutter and web onto the tokens, then govern them (versioning, lint, goldens).

---

## 1. Review findings

### 1.1 Design-system repo itself

| # | Finding | Severity |
|---|---|---|
| R1 | `Merit Design System.html` loads Clash Display from the **Fontshare CDN** and Plus Jakarta from **Google Fonts**. This contradicts SKILL.md §3 and commit `227b9a1` ("self-host"). The `assets/fonts/` files are never used by the reference site. | High |
| R2 | SKILL.md Flutter snippets don't match `merit_theme.dart`: `MeritColors.yellow` differs, `MeritType.body` uses `GoogleFonts.plusJakartaSans` (the app uses the local `PlusJakartaSans` family), and a code comment says "bundle the .otf via Fontshare". Agents copying these snippets produce wrong code. | High |
| R3 | "Clash Display 800" is used for streak chips, the seal, and the starburst. Clash Display's heaviest cut is Bold 700, and only 500–700 are shipped. **800 renders as faux-bold.** | Medium |
| R4 | **No spacing, motion, z-index, opacity, focus-ring, or state tokens.** Flutter invented its own (4-dp spacing, `MeritRadius`, M3 elevation levels that go unused). | High |
| R5 | Missing component specs: quiz question card, answer option states (correct / wrong / selected / disabled), timer, results/grade screen, flashcard, dialog, bottom sheet, toast/snackbar, empty/error/offline states, skeleton loading, segmented tabs, avatar, data-viz. The app already built most of these ad hoc (`merit_quiz_option`, `merit_shimmer`, `merit_snack_bar`, …). | High |
| R6 | Tab-bar label is **8.5px**, below any legible minimum (Flutter uses 11). | Medium |
| R7 | Emoji used as UI icons (🔥 🪙 ⚡ ♛ ⏱). They render differently on iOS, Android, Windows, and Samsung, and can't be themed. | Medium |
| R8 | Sidebar backlink points to `Merit Project Brand Board.html`, which doesn't exist in the repo. | Low |
| R9 | The tweaks panel loads **React dev builds + Babel-standalone** from unpkg at runtime, which is heavy for a static reference page. | Low |
| R10 | Demo persona "Maya Okafor" doesn't fit the Sri-Lankan-local pillar. The leaderboard already uses Anjana, Rashmi, and Sahan. | Low |
| R11 | Type scale (Display 96 / H1 48 / H2 28–40) doesn't map to the Flutter M3 scale (display 57/45/36, headline 32/28/24). Nobody can say which size an "H2" is. | Medium |

### 1.2 Flutter app (`merit-project-flutter`)

| # | Finding | Evidence |
|---|---|---|
| F1 | Palette names collide with the DS (table above). | `lib/theme/merit_theme.dart:12-26` |
| F2 | **Legacy aliases still widely used.** | `sunglow` ×47, `emerald` ×42, `moonstone` ×32, `brightPink` ×28, `neutral60` ×25, `blueNCS` ×18, `indigoDye`, `midnightGreen`, M3 `neutral*` greys |
| F3 | **61 raw `Color(0x…)` in `lib/features`**, including 34× `Color(0xFF000000)` and off-brand hues: orange `#FF9800` (grade badge, completion), `#FF6B2B` (gamer header), teal/aqua gradients in `flippable_study_card.dart`, and a purple gradient in `premium_screen.dart`. | `grep Color(0x` |
| F4 | **20 blurred shadows** (`blurRadius` 8–24), which breaks the core "zero-blur" rule. | home, subjects, analytics, profile, quiz, main_screen |
| F5 | Theme helpers branch on `brightness` everywhere (`MeritBorders.resolve`, `MeritShadows._shadowColor`, and `isDark ?` in every widget) instead of a `ThemeExtension`. | `merit_theme.dart:316-362`, `merit_button.dart` |
| F6 | `MeritShadows` is almost unused (6 call sites). Widgets hand-roll `BoxShadow(offset: Offset(4,4))` 25 times. | |
| F7 | `MeritButton` borders use `MeritColors.ink` (`#29261B`), not the line color (`#000`). | `merit_button.dart` |
| F8 | **Zero `Semantics` widgets**, and only one `semanticLabel`/`tooltip` in the whole app. Icon buttons, progress rings, streak heatmap, and quiz options are opaque to TalkBack/VoiceOver. | |
| F9 | Only 2 references to `disableAnimations`. Flip cards, grade-badge animations, and shimmer ignore reduced motion. | |
| F10 | 105 literal `fontSize:` values in features (10 and 11 are the most common), bypassing `MeritTypography`. | |
| F11 | Radius literals are all over the place: 3, 4, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 30, 99, 999. | |
| F12 | 17 unused Nunito font files sit in `assets/google_fonts/` and are not declared in `pubspec.yaml`. | |
| F13 | The switch's off-track `#D6CADB` on white is **1.58:1**. The 2-px outline rescues the boundary, but the off/on fill alone isn't distinguishable. | |

### 1.3 Web frontend (`merit-project-frontend`)

| # | Finding |
|---|---|
| W1 | Only **color variables** are mapped. No border-width or hard-shadow tokens exist in `@theme`, so shadcn primitives still look like stock shadcn (the known gap in SKILL.md §8). |
| W2 | 72 soft-shadow utilities (`shadow-sm` ×39, `shadow-md` ×17, `shadow-lg` ×12, …) and only 11 `border-2`. |
| W3 | Template leftovers: shadcn-admin theme hex (`#202225`, `#36393f`, `#b9bbbe`, …), Google brand colors, and `.font-inter` / `.font-manrope` font switcher classes. |
| W4 | `--destructive: #C4393A` is reused unchanged in dark mode, giving **3.39:1 on `#1B161B`** (fails). |
| W5 | Two icon libraries (`lucide-react` + `@tabler/icons-react`). The mobile app uses `phosphor_flutter`, so there are three families in total. |
| W6 | Reduced motion is handled in only 5 places. `animate-snow-fall` and `animate-spin-slow` run unconditionally. |

---

## 2. Token architecture v2

### 2.1 Single source → generated outputs

```
merit-project-design-system/
  tokens/
    primitives.tokens.json    ← raw palette, sizes (W3C DTCG format)
    semantic.light.tokens.json← roles → primitives
    semantic.dark.tokens.json
    component.tokens.json     ← button/card/input/quiz-option…
  build/ (generated, committed)
    css/merit-tokens.css      → copied to frontend app/ + DS site
    dart/merit_tokens.dart  → copied to flutter lib/theme/
    json/merit-tokens.json    → docs site, Figma Tokens Studio
  scripts/
    build-tokens.mjs          ← Style Dictionary v4
    check-drift.mjs           ← CI: diff generated vs consumer copies
```

The rules:
- **Consumers never define hex.** Flutter `MeritColors` and web `--merit-*` are *generated*.
  Hand-written theme code (`ThemeData`, shadcn mapping) references generated names only.
- **Three layers.** Primitive (`purple.500`) → semantic (`color.action.primary`) →
  component (`button.primary.bg`). Screens use semantic or component tokens, never primitives.
- CI in both app repos runs `check-drift` and fails if the vendored token file ≠ the DS build.

### 2.2 Primitive palette (names disambiguated)

The same number of hues, now with every existing hex given one unambiguous name. No new hues.

| Primitive | Hex | Was called |
|---|---|---|
| `purple.300` | `#B48CE8` | *new tint: dark-mode purple text/links only* |
| `purple.500` | `#8E55D7` | purple |
| `purple.700` | `#6E36B8` | purple-deep |
| `purple.100` | `#EDE4F8` | Flutter `purpleLight` |
| `yellow.500` | `#FFCC00` | yellow (DS) |
| `yellow.400` | `#F2D43B` | yellow (Flutter), yellow-soft (DS) |
| `yellow.100` | `#FFF5CC` | Flutter `yellowLight` |
| `mint.500` | `#9ED5B7` | mint (DS) |
| `mint.400` | `#9CE7C8` | mint (Flutter), mint-soft (DS) |
| `mint.100` | `#D5F5E9` | Flutter `mintLight` |
| `mint.800` | `#2D6649` | Flutter `mintDark` (text on mint tint) |
| `cream.200` | `#FFEFD7` | cream (DS) |
| `cream.100` | `#FFF7ED` | cream (Flutter), cream-warm (DS) |
| `ink.900` | `#1B161B` | ink-2 / inkDeep |
| `ink.850` | `#241D24` | dark surface-2 |
| `ink.800` | `#2A222A` | dark surface (Flutter has `#2A232A`, **1-bit typo**) |
| `ink.700` | `#312A31` | ink / charcoal |
| `ink.text` | `#29261B` | text (DS), ink (Flutter) |
| `mauve.600` | `#685A68` | *replaces text-mute `#7A6C7A` (a11y, §3)* |
| `mauve.500` | `#5A4A5A` | text-dim |
| `mauve.300` | `#C4B5C4` / `mauve.400` `#9C8C9C` | dark dim / mute |
| `pink.300` `#FFB3C8`, `blue.300` `#B3D8FF` | | category accents |
| `red.600` | `#C4393A` | error |
| `red.300` | `#FF9A9A` | *dark-mode error (Flutter uses `#FFB3BA`; either passes)* |
| `black` | `#000000` | line |

**Retire:** `sunglow`, `emerald`, `moonstone`, `brightPink`, `indigoDye`, `mintGreen`,
`blueNCS`, `midnightGreen`, `neutral10…99`, `#FF9800`, `#FF6B2B`, and the teal flashcard
gradients. Handle them with a codemod (§6).

### 2.3 Semantic tokens (the layer screens use)

| Semantic | Light | Dark | Note |
|---|---|---|---|
| `bg.app` | `cream.100` `#FFF7ED` | `ink.900` | **Decision D3.** Product UI on both platforms |
| `bg.brand` | `cream.200` `#FFEFD7` | `ink.900` | Landing, marketing, hero bands |
| `surface.default` | `#FFFFFF` | `ink.800` | cards, sheets, inputs |
| `surface.sunken` | `cream.100` | `ink.850` | wells, tracks, muted rows |
| `surface.inverse` | `ink.700` | `cream.100` | "dark" button, leaderboard |
| `text.primary` | `ink.text` | `cream.100` | |
| `text.secondary` | `mauve.500` (7.25:1) | `mauve.300` | |
| `text.tertiary` | `mauve.600` (5.7:1) | `mauve.400` | captions, placeholders |
| `text.link` | **`purple.700`** (6.9:1) | **`purple.300`** (6.7:1) | purple.500 is for *fills*, not text |
| `border.default` | `black` | `cream.100` | the signature outline |
| `border.subtle` | `#E7D8C6` hairline | `#3A2F3A` | dividers only, never component edges |
| `shadow.color` | `black` | `cream.100` | hard shadow follows border |
| `action.primary` / `.on` | `purple.500` / white (4.74) | same | |
| `action.primary.pressed` | `purple.700` | same | |
| `action.accent` / `.on` | `yellow.500` / `ink.700` (9.2) | same | rewards, XP, secondary CTA |
| `feedback.success` / `.on` | `mint.500` / `ink.700` | `mint.400` / `ink.900` | |
| `feedback.warning` | `yellow.400` / `ink.700` | same | |
| `feedback.error` / text | `red.600` (fill: white 5.26) | `red.300` | **fixes W4** |
| `focus.ring` | `purple.500`, 3 px, 2 px offset | `purple.300` | ≥3:1 vs adjacent |
| `state.disabled` | 40% opacity + no shadow | same | never color alone |

**Quiz-specific** (the core loop has no tokens today):

| Token | Fill | Border / shadow | Icon (mandatory, not color-only) |
|---|---|---|---|
| `quiz.option.idle` | surface | border.default, shadow 3 | letter chip A–D |
| `quiz.option.selected` | `purple.100` | purple.500, shadow 3 purple | filled letter chip |
| `quiz.option.correct` | `mint.500` | black, shadow 4 | ✓ check (Phosphor `CheckCircle` bold) |
| `quiz.option.wrong` | `#F4C7C7` | `red.600` | ✕ (`XCircle`) |
| `quiz.option.revealed` | surface | mint.500 dashed | ✓ outline: "correct answer was…" |
| `quiz.timer.safe` / `.warn` / `.critical` | mint / yellow / red.600 | black | pulse only if motion allowed |

**Tier and gamification** (currently ad-hoc orange and gradients):

| Token | Value |
|---|---|
| `tier.wanderer` | `surface` + `ink.700` seal |
| `tier.achiever` (Pro) | `yellow.500` fill + `ink.700` ♛ seal. **Replaces the `premium_screen` gradient** |
| `reward.points` | `yellow.500` |
| `reward.streak` | `purple.500` (done), `yellow.500` (today), dashed (future) |
| `grade.A…F` | `mint.500` → `mint.400` → `yellow.400` → `yellow.500` → `pink.300` → `red.600`. **Replaces `#FF9800`** |

**Subject/category colors:** `pink.300`, `blue.300`, `mint.400`, `yellow.400`,
`purple.100`, `cream.200`. These six are assigned deterministically by subject id
(the backend exposes the index), always with ink text and a black border. This replaces
the flashcard teal gradients.

### 2.4 Non-color tokens (new)

| Group | Tokens |
|---|---|
| **Space** (4-pt, from Flutter) | `0 4 8 12 16 20 24 32 40 48 64`. Card padding `16/20/24`; section gaps `24/32/48` |
| **Border width** | `hairline 1.5` · `base 2` · `heavy 3` (hero, phone frame) |
| **Radius** | `xs 6` (tiny chips) · `sm 10` (icon chip) · `md 14` (inputs, option rows) · `lg 18` (cards) · `xl 24` (sheets, feature cards) · `2xl 32` (frames) · `pill 999`. The 15 literal values collapse into these 7 |
| **Hard shadow** | `s1 2,2` · `s2 3,3` · `s3 4,4` (default card) · `s4 6,6` (featured) · `s5 10,10` (hero). **Blur is always 0**; color = `shadow.color` |
| **Interaction offsets** | hover (web only) `translate(-2,-2)` + next shadow step; pressed `translate(+2,+2)` + `s1`. Transform only, never layout-shifting |
| **Motion** | `instant 80` · `fast 120` (press) · `base 180` (toggle, tab) · `slow 280` (sheet, card flip half) · `celebrate 600` (grade, level-up). Easing `standard cubic-bezier(.2,.7,.2,1)`, `exit` 70% of enter. Reduced motion: collapse to opacity fades ≤120 ms, no spin, flip becomes crossfade |
| **Opacity** | `disabled .4` · `scrim .5 (light) / .7 (dark)` |
| **Z (web)** | `base 0 · sticky 10 · dropdown 20 · overlay 30 · modal 40 · toast 50` |
| **Touch target** | min 48 dp (Android) / 44 pt (iOS). Hit area grows even when the visual chip is smaller |
| **Breakpoints (web)** | `sm 640 · md 768 · lg 1024 · xl 1280`. Sidebar collapses < 1024 |

### 2.5 Typography scale (one set of names for both platforms)

| Token | Family | Size / line | Weight | Tracking | Flutter `TextTheme` | Web |
|---|---|---|---|---|---|---|
| `display.xl` | Clash | 56/56 | 700 | -4% | displayLarge | `clamp(48px,7vw,96px)` landing uses School Times |
| `display.lg` | Clash | 40/44 | 700 | -3% | displayMedium | h1 |
| `display.md` | Clash | 32/36 | 700 | -2% | displaySmall / headlineLarge | h2 |
| `title.lg` | Clash | 24/30 | 600 | -2% | headlineSmall | h3 |
| `title.md` | Clash | 20/26 | 600 | -1% | titleLarge | h4 / card title |
| `title.sm` | Jakarta | 16/24 | 700 | 0 | titleMedium | |
| `body.lg` | Jakarta | 16/24 | 500 | 0 | bodyLarge | |
| `body.md` | Jakarta | 14/21 | 500 | 0 | bodyMedium | |
| `body.sm` | Jakarta | 12/18 | 500 | 0 | bodySmall (floor for body copy) | |
| `label.md` | Jakarta | 12/16 | 700 | +0.08em UPPER | labelMedium | |
| `label.sm` | Jakarta | 11/14 | 700 | +0.12em UPPER | labelSmall (**absolute floor, fixes R6**) | |
| `numeric.xl/lg/md` | Clash | 48 / 32 / 20 | 700 | -2%, tabular figures | stats, points, timers | |

- The max weight is 700. **Remove every 800 reference** (R3).
- All numbers that update live (timer, points counter) use `fontFeatures: [tabularFigures]`
  / `font-variant-numeric: tabular-nums` so they don't jitter.
- Support Dynamic Type / text scaling up to 200%. Layouts must wrap, not clip.

---

## 3. Accessibility fixes (measured, WCAG 2.2 AA)

| Pair | Today | Fix | New |
|---|---|---|---|
| Purple text on cream (`#8E55D7`/`#FFEFD7`) | **4.19** ✗ | Links/text use `purple.700` | 6.45 ✓ |
| Text-mute on cream (`#7A6C7A`/`#FFEFD7`) | **4.37** ✗ | `mauve.600` `#685A68` | 5.72 ✓ |
| Purple text on dark (`#8E55D7`/`#1B161B`) | **3.76** ✗ | `purple.300` `#B48CE8` | 6.67 ✓ |
| Web destructive on dark (`#C4393A`/`#1B161B`) | **3.39** ✗ | `red.300` `#FF9A9A` | 8.78 ✓ |
| Flutter nav unselected `#857B85` on white, 11 px | **4.06** ✗ | `text.tertiary` | 6.46 ✓ |
| Switch off-track `#D6CADB` vs white (non-text) | **1.58** ✗ | off track = `surface.sunken` + **thumb position + ink outline** carry state; add on/off glyph in thumb | ≥3:1 via border |
| White on purple (button label) | 4.74 ✓ | keep; purple-deep pressed 7.28 | |
| Ink on yellow / mint | 9.2 / 8.4 ✓ | keep | |

Plus structural rules:
1. **Never color-only.** Correct/wrong, streak states, tier, and heatmap all carry an icon, text, or pattern as well.
2. **Focus visible**: a 3-px `focus.ring` outline at 2-px offset *in addition to* the purple border swap. Keyboard users on web get it via `:focus-visible`; Flutter gets it via `FocusableActionDetector` on custom tappables.
3. **Flutter semantics**: every `GestureDetector`/`InkWell` custom control is wrapped in `Semantics(button: true, label:, selected:, enabled:)`. Icon-only buttons need a `tooltip`. Progress rings and bars need `Semantics(value: '62%')`. Decorative stickers and starbursts get `ExcludeSemantics`.
4. **Emoji → icons** (R7): a single family, **Phosphor** (already in Flutter; `@phosphor-icons/react` on web replaces lucide + tabler). Use the Bold weight to match 2-px strokes and Fill for active states. The 🔥/🪙 look survives as custom Phosphor-style SVGs `merit-flame` and `merit-coin` in the DS icon kit.
5. **Reduced motion** is honored everywhere: `MediaQuery.disableAnimationsOf(context)` on Flutter and `prefers-reduced-motion` + `motion`'s `useReducedMotion` on web.

---

## 4. Tri-lingual typography (currently missing)

Clash Display, Plus Jakarta Sans, and School Times have **no Sinhala or Tamil glyphs**, and
no Sinhala or Tamil font ships in Flutter or on the web. SI/TA text falls back to whatever
the OS has. On older Android devices that means inconsistent metrics, clipped vowel signs,
or tofu. For a "tri-lingual first-class" brand this is the biggest real-user gap.

| Script | Display (headings) | Body | Weights |
|---|---|---|---|
| Latin | Clash Display | Plus Jakarta Sans | as now |
| Sinhala | **Noto Sans Sinhala** (SemiBold/Bold) | Noto Sans Sinhala | 400/500/600/700 |
| Tamil | **Noto Sans Tamil** (SemiBold/Bold) | Noto Sans Tamil | 400/500/600/700 |

- **Flutter:** bundle the fonts, and set `fontFamilyFallback: ['NotoSansSinhala','NotoSansTamil']` on every `MeritTypography` style so mixed-script strings (e.g. "Physics – භෞතික විද්‍යාව") render correctly.
- **Web:** use `next/font/local` with `unicode-range` subsets (`U+0D80-0DFF` Sinhala, `U+0B80-0BFF` Tamil) so Latin pages don't download them.
- **Per-locale overrides** (`:lang(si)`, `:lang(ta)` / `Locale`-driven `TextTheme`):
  - letter-spacing is always **0**, because negative tracking collides conjuncts;
  - line-height is **≥1.6** for body and **≥1.3** for display (stacked vowel signs);
  - **no UPPERCASE + wide-tracking labels.** These scripts have no case, so SI/TA labels fall back to `title.sm` weight;
  - display sizes step down one level: Tamil strings run ~30–40% longer.
- Buttons, pills, and tab labels must allow a 2-line wrap or flex width. Test with the longest TA string for each key.
- Add an **SI/TA specimen** section to the DS site with real UI strings from `assets/translations`.

---

## 5. Component catalogue v2

Status: ✅ spec exists in v1 · 🔧 v1 spec needs update · 🆕 new spec (usually codifying an existing app widget).

| Component | Status | Key spec points | Flutter widget | Web |
|---|---|---|---|---|
| Button (primary/accent/dark/mint/ghost/link) | 🔧 | sizes S 36 / M 48 / L 56; loading = spinner replaces label, width locked; disabled = .4 + no shadow; border = `border.default` (fixes F7); icon slots | `MeritButton` | `Button` cva variants |
| Icon button | 🆕 | 48 hit area, 40 visual; tooltip required | `MeritCircleButton` | |
| Card (neutral/featured/reward/success) | 🔧 | padding tokens; featured = s4; selected = purple border + shadow | `MeritContentCard`, `ShadowBox` | `Card` |
| Input / textarea / select / OTP / phone (+94) | 🔧 | helper + error text *below* the field, error icon; label always visible; radius `md` | `MeritTextFormField` | `Input` |
| Pill / badge / subject badge | 🔧 | min 24 high visually, 11-px floor | `MeritPill`, `MeritBadge`, `MeritSubjectBadge` | `Badge` |
| Progress bar / ring / stepper | 🔧 | semantics value; stepper uses icon for done | `MeritProgressBar/Ring`, `MeritStepper` | `Progress` |
| Toggle / checkbox / radio | 🔧 | **Decision D5**; ink outline; glyph in on-state | `MeritToggle` | `Switch`, `Checkbox` |
| Segmented tabs / language switcher EN·SI·TA | 🆕 | pill container, active = purple fill; language names in their own script (English / සිංහල / தமிழ்) | `MeritSegmentedTabs` | `Tabs` |
| Bottom tab bar | 🔧 | 5 max, label 11 px, active chip, safe-area inset | `main_screen` | n/a |
| App/sliver header, gamer header | 🆕 | streak + coins chips top-right | `MeritHeader`, `MeritGamerHeader` | |
| **Quiz question card** | 🆕 | question number pill, LaTeX/figures, flag/bookmark, language toggle | quiz feature | student |
| **Quiz answer option** | 🆕 | states in §2.3; 56 min height; letter chip; locked after submit | `MeritQuizOption` | student |
| **Timer** (paper mode) | 🆕 | numeric tabular; safe/warn/critical; announces at 5 / 1 min | | |
| **Result / grade screen** | 🆕 | grade seal, points breakdown (+10/q, +20 accuracy bonus, ×1.5 Pro), accuracy ring, "review mistakes" CTA | `quiz_completion_screen`, `AnimatedGradeBadge` | |
| **Flashcard** (flip) | 🆕 | sticker card, category fill, no gradients, flip 2×`slow`, crossfade under reduced motion | `FlippableStudyCard` | |
| Streak chip / coin chip / ribbon / heatmap | 🔧 | Phosphor icons not emoji; heatmap 4-step purple ramp + legend | `MeritStreakHeatmap` | |
| Leaderboard row | ✅ | "You" row sticky when off-screen | `MeritLeaderboardRow` | |
| Tier badge / achievement badge / starburst | 🔧 | Wanderer vs Achiever tokens | `MeritAchievementBadge` | |
| Paywall / upgrade (Wanderer→Achiever) | 🆕 | quota meter ("12 of 50 questions today"), yellow Achiever card, no dark-pattern copy | `premium_screen` | |
| Dialog / bottom sheet | 🆕 | black border, s4 shadow, scrim token, drag handle, safe area | `MeritDialog` | `Dialog`, `Sheet` |
| Snackbar / toast | 🆕 | floating, border + s2; success/error/info with icon; 4 s, action optional | `MeritSnackBar` | `sonner` |
| Empty / error / offline states | 🆕 | geometric sticker illustration + one line + one CTA | `MeritEmptyData`, `MeritError`, `OfflineContainer` | |
| Skeleton / shimmer | 🆕 | `surface.sunken` blocks with border; shimmer off under reduced motion | `MeritShimmer` | `Skeleton` |
| Data table (admin/contributor) | 🆕 | dense variant: border 1.5, no row shadows, sticky header | n/a | `DataTable` |
| Charts (analytics) | 🆕 | categorical = `purple.500, yellow.500, mint.500, pink.300, blue.300`; sequential = purple ramp; always legend + tooltip | analytics | `chart-1..5` |

**Density modes:** the student app and landing use *expressive* density (s3 shadows, 16–24 padding).
The admin and contributor dashboards use a **compact** mode with `border.hairline` 1.5 on table
cells, s1–s2 shadows, 8–12 padding, and hard shadows reserved for primary actions and
floating layers. Neo-brutalism at full volume on a 50-row table is noise.

---

## 6. Migration plan

### Phase 0: decisions and DS doc fixes ✅ done 2026-09-26 (site v1.1)
- ✅ D1–D7 approved, recorded in §7 and SKILL.md §9. Spec text is updated where a decision contradicted v1: extended-palette roles, checkbox purple vs mint, app vs brand background, emoji → Phosphor.
- ✅ R1: the DS site self-hosts every face via `@font-face` in `merit-ds.css` (Clash, Jakarta, and School Times as `--font-landing`). The Fontshare and Google links are removed. JetBrains Mono is dropped for a system mono stack.
- ✅ R2: SKILL.md and site snippets are rewritten against the real `merit_theme.dart`: actual `MeritColors` names with DS-name mapping, deprecated aliases listed, local font families, no `google_fonts`. *Fully generated snippets still arrive with Phase 1.*
- ✅ R3: all `font-weight:800` → 700; the specimen and SKILL say 700 is the max.
- ✅ R6: the tab-bar label is 11 px.
- ✅ R8: the backlink now points to this plan.
- ✅ R9: React dev + Babel-standalone are replaced by `merit-ds-tweaks.js` (vanilla, same `__edit_mode_*` host protocol and EDITMODE block). `tweaks-panel.jsx` is removed.
- ✅ R10: the demo persona is Nethmi Perera.
- ⏭ Deferred to Phase 1: token value swaps for a11y (`text-mute` → `#685A68`, dark error, dark link purple). The *rules* are documented in SKILL.md now; the CSS values change with the token pipeline so all three platforms move together.

### Phase 1: token pipeline ✅ done 2026-09-26 (v2.0.0)
- ✅ `tokens/primitives|semantic.light|semantic.dark|component|typography.tokens.json` (DTCG) plus `tokens/contrast.json`.
- ✅ Build: `npm run build` → `build/css/merit-tokens.css`, `build/dart/merit_tokens.dart`, `build/json/merit-tokens.json`, and the SKILL.md §10 block.
  **Deviation:** a zero-dependency Node script (`scripts/build-tokens.mjs`) instead of Style Dictionary. The DS repo has no npm deps, SD's Flutter formats can't emit a `ThemeExtension`, and custom output keeps files byte-deterministic for the drift check.
- ✅ Contrast gate: 45 pairs × light/dark on every build. I also ran a negative test: restoring `#7A6C7A` fails the build.
- ✅ Generated Dart verified in a scratch Flutter 3.38.2 package: `flutter analyze` finds 0 issues, and unit tests pass (values, `lerp`, `context.meritColors`, shadow blur 0).
- ✅ `merit-ds.css` now imports the tokens, and its legacy short names alias `--merit-*`. In headless Chrome, computed light/dark card colours, borders, and shadows are unchanged.
- ✅ `scripts/check-drift.mjs` (tested for match, mismatch, and a missing file) and the DS CI `.github/workflows/tokens.yml` (`npm run check`).
- ✅ `package.json` v2.0.0 and `CHANGELOG.md`.
- ⏭ **Moved to Phase 2/3 kickoff:** vendoring the generated files and adding the drift-check CI step to `merit-project-flutter` and `merit-project-frontend`. Both checkouts are on unrelated feature branches, so this belongs on each phase's own branch. The CI step: check out the DS repo at a pinned ref, then `node ds/scripts/check-drift.mjs --dart lib/theme/merit_tokens.dart` (or `--css …`).

### Phase 2: Flutter retrofit (≈1.5–2 weeks, can run per feature)
1. Drop in `merit_tokens.dart`. Keep `MeritColors` as a thin generated class.
2. Add a **`MeritTheme extends ThemeExtension`** (borders, hard shadows s1–s5, semantic colors, quiz states, motion). Replace every `brightness == dark ? …` with `context.merit.border` and similar (F5).
3. Rewrite `ThemeData` from tokens: scaffold `bg.app`, checkbox per D5, switch fix, nav colors.
4. **Codemods** (`dart fix`-style script or `sed` + review):
   - alias → canonical (`sunglow`→`yellow400`, `emerald`→`mint400`, `moonstone`→`purple500`, `brightPink`→`error`, `neutral60`→`textTertiary`, …): about 230 sites;
   - `Color(0xFF000000)` → `context.merit.border` (34 sites);
   - literal `BorderRadius.circular(n)` → nearest `MeritRadius` token;
   - literal `fontSize:` → `MeritTypography` / `textTheme`.
5. Kill blur: replace the 20 `blurRadius > 0` shadows with the `s*` tokens (F4). Replace the flashcard, premium, and grade gradients and oranges with tokens (F3).
6. Accessibility: `Semantics` on all custom tappables and progress widgets, tooltips, reduced-motion gates (F8, F9).
7. Fonts: add Noto Sans Sinhala + Tamil, `fontFamilyFallback`, a locale-aware `TextTheme`; delete Nunito (F12).
8. **Lint**: add a `custom_lint` rule, `avoid_raw_colors`, `avoid_blur_shadow`, and `avoid_literal_font_size`, under `lib/features/**`.
9. **Golden tests** for each `merit_*` widget in light, dark, `si`, `ta`, and 2× text scale.

**Status, 2026-09-26: first pass done** on `merit-project-flutter` branch `feat/design-tokens-v2` (base `feat/fsrs-flashcards`, 7 commits). Analyzer output is identical to the pre-change baseline, and all tests pass (6 → 24).

| Step | Status |
|---|---|
| 1 Tokens vendored | ✅ `lib/theme/merit_tokens.dart`, pinned by `.design-tokens-ref`. `MeritColors` aliases `MeritPalette` |
| 2 ThemeExtension | ✅ Generated `MeritSemanticColors` plus `context.meritColors`. 242 `isDark ? … : …` ternaries are migrated; about 33 bespoke ones remain (hero bands and similar, with no matching token) |
| 3 ThemeData | ✅ One token-driven builder covering D1/D2/D3/D5, the switch off-state, nav contrast, and dark error |
| 4 Codemods | ✅ 174 alias uses, neutrals, 34 black literals, and 13 purple-as-text sites. ⏭ radius literals and `fontSize` literals (both visible changes; they need device review) |
| 5 Blur / gradients | ✅ All *live* screens: tab bar, flashcards, grade/results, loading, hierarchy, premium, avatar. The rest are in 16 unreferenced files (allow-listed) |
| 6 Accessibility | ✅ Core widgets: quiz option (also fixes selected-looks-correct), buttons, icon buttons, toggle, tabs, progress, flip under reduced motion. ⏭ Remaining ~60 ad-hoc `GestureDetector`/`InkWell`s |
| 7 Fonts | ✅ Noto Sans Sinhala/Tamil fallbacks, `themeFor(locale)`, Nunito removed (bundle −2.6 MB), license registration fixed |
| 8 Lint | ✅ As a zero-dependency guard (`tool/check_design_tokens.dart` + CI) instead of `custom_lint` |
| 9 Goldens | ⏭ Not started. Widget/semantics tests exist for the theme and quiz option |

### Phase 3: web retrofit (≈1–1.5 weeks)
1. Import `merit-tokens.css`. Extend `@theme inline` with `--shadow-brutal-1…5`, `--border-width-base`, radius tokens, and motion tokens so Tailwind emits `shadow-brutal-3`, `rounded-card`, and similar.
2. Restyle via cva variants in `components/ui` (button, card, input, badge, dialog, sheet, tabs, switch, checkbox, progress, table). Replace the 72 `shadow-sm|md|lg` uses with brutal tokens or none (compact density).
3. Remove template leftovers (W3) and fix dark `--destructive` (W4).
4. Consolidate icons on `@phosphor-icons/react` (W5).
5. Add a global reduced-motion guard for `animate-*` utilities (W6).
6. Add Noto Sinhala/Tamil via `next/font/local` + `unicode-range`, plus `:lang()` overrides.
7. Add a **Storybook** or `/design` route in the frontend that renders every primitive in light/dark and EN/SI/TA, with Chromatic or Playwright screenshot diffs.

**Status, 2026-09-26: first pass done** on `merit-project-frontend` branch `feat/design-tokens-v2` (base `feat/notes-rendering`, 5 commits). tsc is clean, lint is unchanged (3 pre-existing warnings), and it was checked in the browser as admin (dashboard, questions table, light and dark) and as student (home, subjects).

| Step | Status |
|---|---|
| 1 Tokens + `@theme` | ✅ `app/merit-tokens.css` pinned by `.design-tokens-ref`. shadcn vars are mapped to semantic tokens. Adds `shadow-brutal-*`, `rounded-card/field/chip/sheet`, `text-link`, `bg-sunken`, `font-display` |
| 2 Primitives | ✅ button, card, input, textarea, select, badge, checkbox, switch, tabs, progress, table (compact D7), toggles, all floating layers |
| 3 Leftovers | ✅ Fixed the theme-customizer bug: it re-applied the stock neutral preset over the brand. Fixed the dark destructive colour. Template demo pages stay allow-listed |
| 4 Icons (Phosphor) | ✅ 138 files via generated-then-hand-maintained `lib/icons.tsx` (Bold default, `/ssr` entry so it works in server and client components); lucide + tabler removed; the guard and PR-review rule enforce it. ⏭ `components.json` `iconLibrary` still says lucide (shadcn CLI setting) |
| 5 Reduced motion | ✅ Decorative animations |
| 6 Noto SI/TA | ✅ `next/font/local` + `unicode-range`, plus `:lang()` rules. The note reader sets `lang`; other content renderers (questions, flashcards) don't exist on the web yet |
| 7 `/design` route / Storybook | ✅ `/admin/dev/design` light + dark specimen (no Storybook). ⏭ Screenshot diffs |
| — Also | 56 purple-as-text sites → `text-link`; soft shadows on pages → hard shadows or removed; guard `scripts/check-design-tokens.mjs` + drift check in CI |

### Phase 4: DS site v2 (≈1 week, parallel with 2–3)
Add the new sections: Spacing & Layout · Motion · States & Focus · Accessibility · Iconography
· Tri-lingual Type · Quiz components · Feedback & Empty states · Data viz · Density modes
· Landing (School Times) specimen · Tokens reference (auto-generated table) · Changelog.

---

## 7. Decisions (✅ all approved as recommended, 2026-09-26)

Recorded for agents in SKILL.md §9.

| ID | Question | Decision | Why |
|---|---|---|---|
| **D1** | Which yellow is "brand yellow"? | `yellow.500 #FFCC00` for accents, CTAs, and rewards everywhere; `yellow.400 #F2D43B` only for large background fills and warning | The brand board and web use `#FFCC00`; keeping both, named clearly, avoids re-skinning the app's big yellow areas |
| **D2** | Which mint? | `mint.500 #9ED5B7` light-mode success; `mint.400 #9CE7C8` dark-mode success and category | `#9CE7C8` already *is* the web dark-mode secondary, so this makes the pattern official |
| **D3** | App background: white or cream? | `bg.app = #FFF7ED` in the product UI (app + dashboards); `#FFEFD7` for brand/landing bands | White scaffold + white cards weakens the sticker feel; `#FFEFD7` over full screens is heavy for long study sessions |
| **D4** | What does "ink" mean? | `text.primary = #29261B`; `surface.inverse = #312A31` | Both hexes already exist; they just need distinct roles |
| **D5** | Checkbox "on" = mint (DS) or purple (app)? | **Purple fill + white ✓** for form checkboxes (a selection); **mint + ink ✓** only for *completion* (todo, stage done) | Separates "selected" from "achieved", which matters in a gamified UI |
| **D6** | Icon family | Phosphor (Bold/Fill) on both platforms + custom `merit-flame` and `merit-coin` | Already in Flutter; stroke weight fits 2-px outlines |
| **D7** | Brutal intensity on admin/contributor | Compact density mode (§5) | These are data-heavy tools |

---

## 8. Definition of done / success metrics

- [ ] 0 hex literals outside generated token files (Flutter `lib/features`, web `app/ components/ features/`). Enforced by lint.
- [ ] 0 `blurRadius > 0` / soft `shadow-{sm,md,lg,xl}` in product UI.
- [ ] `check-drift` green in both app repos' CI.
- [ ] Every text/background token pair ≥ 4.5:1 (≥ 3:1 for ≥ 24 px or bold ≥ 18.66 px). A contrast test runs in the token build.
- [ ] Every custom control has a semantic label; a TalkBack/VoiceOver pass completes the quiz flow end-to-end.
- [ ] SI and TA golden screenshots for home, quiz, result, and profile show no clipping at 1.0× and 1.5× text scale.
- [ ] Reduced motion: no rotation, flip, or parallax when the OS setting is on.
- [ ] Every component in §5 has a DS spec, a Flutter widget, and a web primitive (or is marked N/A).
- [ ] SKILL.md snippets are generated, so they cannot diverge from code.

---

## 9. What stays exactly the same

The six-tone identity, black 2-px outlines, zero-blur offset shadows, pill buttons with
press-in, Clash Display for loud text, uppercase micro-labels (Latin only), sticker
motifs, cream outlines in dark mode, and the voice ("Keep your streak alive." "Earn it.").
v2 is an **engineering and accessibility upgrade to the same brand**, not a redesign.

> Note: the `ui-ux-pro-max` generator's generic "education" recommendation (teal/amber,
> Swiss minimalism, Space Grotesk) was reviewed and **rejected**. It conflicts with an
> established, distinctive brand. Only its checklist items (contrast, focus, reduced
> motion, no emoji icons, touch targets) were adopted.
