---
name: merit-design-system
description: >-
  The Merit Project design system — a playful, neo-brutalist, gamified
  education brand for Sri Lankan O/L & A/L students. Use this skill whenever
  building or styling ANY Merit Project surface: the Flutter mobile app, the
  marketing/landing website, or supporting graphics. It defines the canonical
  color tokens, typography, the signature hard-shadow + black-border look,
  component recipes (buttons, cards, inputs, pills, progress, badges, toggles,
  tab bars), decorative motifs, dark-mode rules, and copy voice — with ready-to-
  paste Flutter (Dart) and HTML/CSS snippets.
---

# Merit Project — Design System

> **Learn it. Level up. Earn Merit.**
> A gamified exam-prep platform for Sri Lankan **O/L** and **A/L** students —
> quizzes, flashcards, past papers, streaks and adaptive practice across
> **Sinhala, Tamil and English**.

This skill is the single source of truth for the Merit brand across the
**Flutter app** and the **landing page**. When the two references disagree, the
priority order is: **Brand Board → Mobile App Screens → Landing**.

---

## 1. Brand essence

Merit is **bold, playful, and unmistakably game-like** — but built for serious
study. The look is **neo-brutalist**: flat saturated color blocks, **solid black
2px outlines on everything**, and **hard offset drop-shadows** (no blur). It
feels like a sticker sheet, an arcade, and a study planner at once.

**Three pillars to keep in every screen:**
1. **Outlined & chunky** — black borders + hard shadows give physical, tactile weight.
2. **Gamified** — streaks 🔥, merit points 🪙, tiers, starbursts, leaderboards, progress bars.
3. **Tri-lingual & local** — EN / SI / TA toggles are first-class; content is Sri-Lanka-specific (A/L streams, districts, schools).

**Voice:** confident, encouraging, short. "Keep your streak alive." "Earn it."
"Hit your weak spots first." Never corporate, never condescending. Emoji are fine
in **copy** (push notifications, celebratory text) but are **not UI icons**. Streak,
coins, rating, and timer glyphs use the icon set (D6: **Phosphor**, Bold weight to
match 2px outlines, Fill for active states; `phosphor_flutter` in the app,
`@phosphor-icons/react` on web). Brand glyphs `merit-flame` and `merit-coin` come from the DS icon kit.

---

## 2. Color tokens (canonical)

> **v2:** every value below is generated from `tokens/*.tokens.json` (see §10 for the
> semantic token table). In new code, use **semantic tokens**: CSS
> `var(--merit-text-primary)` or Flutter `context.meritColors.textPrimary`. Don't
> use raw hex, and don't use primitives.

These six tones + black are the **whole system. No remix, no new hues.**

| Token | Hex | Role |
|---|---|---|
| **Purple** | `#8E55D7` | Primary — main actions, brand, active states |
| **Purple Deep** | `#6E36B8` | Primary pressed / deep shade |
| **Yellow** | `#FFCC00` | Accent — highlights, XP, rewards, secondary CTA |
| **Mint** | `#9ED5B7` | Support — success, "done", positive stats |
| **Cream** | `#FFEFD7` | Surface — light background, soft cards |
| **Ink** | `#312A31` | Charcoal — primary text, dark cards |
| **Ink-2** | `#1B161B` | Darkest — dark-mode background |
| **White** | `#FFFFFF` | Base surface |
| **Line / Border** | `#000000` | The black outline on *everything* |

### Extended palette: supporting tints (roles approved in v2 decisions D1–D4)

| Token | Hex | Use |
|---|---|---|
| Yellow (soft) | `#F2D43B` | **Large background fills and warning only.** Brand yellow for accents, CTAs, and rewards is `#FFCC00` (D1) |
| Mint (soft) | `#9CE7C8` | **Dark-mode success** and category tint. Light-mode success is `#9ED5B7` (D2) |
| Pink | `#FFB3C8` | Category accent (e.g. Arts, Biology) |
| Blue | `#B3D8FF` | Category accent (e.g. Technology, ICT) |
| Cream (warm) | `#FFF7ED` | **`bg.app`: page background for all product UI** (app + dashboards). `#FFEFD7` is for brand and landing bands (D3) |
| Text | `#29261B` | `text.primary`. Ink `#312A31` is `surface.inverse` (dark buttons and cards), not text (D4) |
| Text Dim | `#5A4A5A` | Secondary text |
| Text Mute | `#685A68` | Tertiary / captions / placeholders (`text.tertiary`). Replaces `#7A6C7A`, which was 4.37:1 on cream and failed AA. Flutter still has the old value until Phase 2 |
| Error | `#C4393A` | Error fill (white text 5.26:1). In dark mode use `#FF9A9A` (`feedback.error` dark), never `#C4393A` (3.39:1) |

**Text-on-colour rule:** purple `#8E55D7` is a **fill** colour. Purple *text* or links on light
surfaces use purple-deep `#6E36B8` (6.45:1). Purple `#8E55D7` on cream is only 4.19:1.

### Flutter: `MeritColors` (real names, `lib/theme/merit_theme.dart`)

**Don't redefine the palette.** Import `package:merit_project/theme/merit_theme.dart`.
The app's constant *names* predate the DS names, so map them carefully:

```dart
// What the app defines today. Phase 2 adopts build/dart/merit_tokens.dart
// (MeritPalette, MeritSemanticColors via context.meritColors, MeritSpace, MeritRadii…):
MeritColors.purple      // #8E55D7  action.primary fill
MeritColors.purpleDeep  // #6E36B8  pressed · purple text on light surfaces
MeritColors.purpleLight // #EDE4F8  selected tint
MeritColors.yellow      // #F2D43B  ⚠ = DS "yellow soft", NOT brand #FFCC00
MeritColors.mint        // #9CE7C8  ⚠ = DS "mint soft", NOT #9ED5B7
MeritColors.cream       // #FFF7ED  ⚠ = DS "cream warm" (bg.app, dark-mode border)
MeritColors.ink         // #29261B  ⚠ = DS "text" (text.primary)
MeritColors.inkDeep     // #1B161B  dark background
MeritColors.inkSurface  // #2A232A  dark surface
MeritColors.pink / .blue
MeritColors.textDim / .textMute / .textDimDark / .textMuteDark
MeritColors.error       // #C4393A

// Deprecated aliases: do NOT use in new code (codemod pending):
// sunglow→yellow, emerald→mint, moonstone→purple, brightPink→error,
// indigoDye→inkDeep, mintGreen→mintLight, blueNCS→blue, neutral10…99
```

Never add `Color(0x…)` literals in `lib/features/**`. For borders and hard shadows, use
`MeritBorders.resolve(context)` / `MeritShadows.brutal*(context)`, which flip to cream in dark mode.

---

## 3. Typography

| Family | Where | Weights | Tracking |
|---|---|---|---|
| **Clash Display** | App UI headings, numbers, buttons, stat figures, labels-as-display (mobile app + admin/student/contributor web dashboards) | 500–700 (**700 is the heaviest cut; never 800**, which renders faux-bold) | tight: `-0.02em` (display down to `-0.04em`) |
| **Plus Jakarta Sans** | Body copy, descriptions, form values, fine print — everywhere | 400–700 | normal |
| **School Times** | Landing page (`meritproject.lk`) headings only — a punchier, more playful marketing-only display face, deliberately distinct from the in-app Clash Display | 400–700 | as authored, no extra tracking |

Font files (self-hosted, not Google Fonts): `assets/fonts/` in this repo —
`ClashDisplay-{Medium,SemiBold,Bold}.ttf`,
`PlusJakartaSans-{Regular,Medium,SemiBold,Bold}.ttf`,
`SchoolTimes-Regular.otf`. Flutter bundles its own copies at
`merit-project-flutter/assets/google_fonts/`; the backend landing bundles
its own copy at `merit-project-backend/web/static/fonts/`. Despite the
`google_fonts` directory name, none of these are loaded from Google
Fonts — they're local asset files, which is exactly why they should be
self-hosted on web too rather than substituted with a Google Fonts
lookalike.

**Sinhala / Tamil:** none of these three families contain Sinhala or Tamil glyphs, and
no SI/TA font ships yet (v2 adds Noto Sans Sinhala and Noto Sans Tamil; see IMPROVEMENT-PLAN §4).
Until then, for SI/TA strings: letter-spacing 0 (never negative), line-height ≥ 1.6,
no UPPERCASE wide-tracked labels, and let buttons, pills, and tabs wrap or flex. Tamil
runs about 30–40% longer than English.

### Flutter typography

The fonts are declared in `pubspec.yaml` as local families: `ClashDisplay`
(w500/600/700) and `PlusJakartaSans` (w400–700). **Do not use the `google_fonts`
package.** In screens, use `Theme.of(context).textTheme.*` or `MeritTypography.*`
(`lib/theme/merit_theme.dart`) rather than literal `fontSize:`. Label floor: 11.

```dart
// MeritTypography (real) — display/headline/titleLarge = ClashDisplay,
// titleMedium and below = PlusJakartaSans.
Text('Keep the streak', style: Theme.of(context).textTheme.headlineMedium);
Text('12 of 50 today', style: MeritTypography.labelMedium.copyWith(
    color: Theme.of(context).colorScheme.onSurfaceVariant));
// Live-updating numbers (timer, points): add tabular figures
MeritTypography.headlineLarge.copyWith(
    fontFeatures: const [FontFeature.tabularFigures()]);
```

---

## 4. The signature look — borders, shadows, radii

| Property | Value | Notes |
|---|---|---|
| **Border** | `2px solid #000` | 3px on large/hero frames, 1.5px on tiny chips |
| **Hard shadow — small** | `2px 2px 0` / `3px 3px 0` | chips, inputs |
| **Hard shadow — card** | `4px 4px 0` / `5px 5px 0` | content cards |
| **Hard shadow — hero** | `6px 6px 0` … up to `14px 14px 0` | bigger = more important |
| **Radius — pill** | `999px` | buttons, toggles, tags, progress bars |
| **Radius — card** | `18–28px` | content cards |
| **Radius — large frame** | `32–46px` | phone bezel, image frames |
| **Radius — icon chip** | `8–16px` | square-ish badges/icons |

### Flutter — `meritBox`

```dart
BoxDecoration meritBox({
  Color fill = MeritColors.white,
  double radius = 18,
  double offset = 4,
  Color border = MeritColors.line,
  Color? shadow,
}) => BoxDecoration(
  color: fill,
  borderRadius: BorderRadius.circular(radius),
  border: Border.all(color: border, width: 2),
  boxShadow: [
    BoxShadow(color: shadow ?? MeritColors.line,
              offset: Offset(offset, offset), blurRadius: 0),
  ],
);
```

---

## 5. Components (quick reference)

### Buttons
- **Primary** — purple fill, white text
- **Accent** — yellow fill, ink text
- **Dark** — ink fill, cream text, yellow circular arrow chip
- **Ghost** — transparent, ink border
- **Link** — purple underline, no border

### Cards
`meritBox` + padding 14–26px. White/cream = neutral, purple/ink = featured, yellow = reward, mint = success.

### Inputs
Radius 14px (not pill). UPPERCASE micro-label above. Focus → purple border + shadow.

### Pills
`.p` purple · `.y` yellow · `.m` mint · `.k` ink — 1.5–2px border, 99px radius.

### Progress
Bordered track, accent fill, **black right-edge divider** on fill. Stepper: done=mint, current=purple, todo=white.

### Toggles
46×24 pill, ink→mint. Checkbox: 24×24 rounded-7px. **Form selection = purple fill + white ✓.
Completion (todo done, stage cleared) = mint fill + ink ✓** (D5: "selected" must never read as "achieved").

### Tab bar
`meritBox(radius:20, offset:3)`, 5 items max. Active = purple chip with white glyph.
Label **11px minimum**. Touch target ≥ 48dp.

### Gamification
- Streak chip: white pill, flame icon + {n}, Clash 700
- Coins chip: yellow pill, 🪙 {points}
- Streak ribbon: done=purple ✓, today=yellow !, future=dashed
- Leaderboard: dark card, "You" row highlighted purple, points yellow ★
- Tier starburst: purple multi-point SVG

---

## 6. Dark mode

| | Light | Dark |
|---|---|---|
| Background: product UI (app, dashboards) | `#FFF7ED` | `#1B161B` |
| Background: brand / landing bands | `#FFEFD7` | `#1B161B` |
| Surface | `#FFFFFF` | `#2A222A` |
| Text | `#29261B` | `#FFF7ED` |
| Border | `#000000` | `#FFF7ED` (cream!) |

**Key rule:** black outline → cream outline in dark mode.

---

## 7. Do / Don't

**Do:** outline everything · zero-blur hard shadows · Clash Display for loud text · six canonical colors · gamification everywhere · EN/SI/TA first-class.

**Don't:** soft/blurred Material shadows · gradients or new hues · unstyled Material widgets · freehand illustration (use geometric sticker kit) · overuse emoji.

---

## 8. Web / shadcn mapping (merit-project-frontend)

> **v2 naming change:** the generated CSS uses stepped primitive names
> (`--merit-purple-500`, `--merit-cream-100`, …) plus semantic names
> (`--merit-bg-app`, `--merit-text-primary`, …). The frontend's current hand-written
> `--merit-purple`, `--merit-cream`, and similar are the **v1 names**. In Phase 3 the
> frontend vendors `build/css/merit-tokens.css` and re-points the shadcn variables at
> semantic tokens; until then, the table below describes the frontend as it is today.

Added when the unified web frontend (`merit-project-frontend`) needed these
tokens expressed as shadcn/Tailwind v4 CSS variables. Applied in
`app/globals.css` — shadcn variable names are kept unprefixed so every
`components/ui/*` primitive restyles automatically; the raw merit-ds values
are also exposed as `--merit-*` for direct use outside the shadcn mapping.

| shadcn var | Light | Dark | merit-ds source |
|---|---|---|---|
| `--background` | `#FFEFD7` (cream) | `#1B161B` (ink-2) | `--bg` |
| `--card` / `--popover` | `#FFFFFF` | `#2A222A` | `--surface` |
| `--foreground` | `#29261B` | `#FFF7ED` | `--text` |
| `--primary` | `#8E55D7` (purple) | same | `--purple` |
| `--secondary` | `#9ED5B7` (mint) | `#9CE7C8` (mint-soft) | `--mint` |
| `--muted` | `#FFF7ED` (cream-warm) | `#241D24` | `--surface-2` |
| `--accent` | `#FFCC00` (yellow) | same | `--yellow` |
| `--destructive` | `#C4393A` | same | Flutter `MeritColors.error` (not yet in merit-ds.css root tokens — carried over from the mobile app for consistency) |
| `--border` / `--input` | `#000000` | `#FFF7ED` | `--line` (dark-mode flip is merit-ds.css's own rule) |
| `--radius` | `1.125rem` (18px) | same | §4 "Radius — card" |
| `--chart-1..5` | purple/yellow/mint/pink/blue | same | categorical accent set |

**Fonts:** self-hosted via `next/font/local`, not `next/font/google` — the
same `.ttf`/`.otf` files this repo carries in `assets/fonts/` (§3), copied
into `merit-project-frontend/public/fonts/`. Plus Jakarta Sans is the body
face everywhere (`--font-merit-sans`); Clash Display is the display face
for app UI headings (`--font-merit-display`, used in `app/admin`,
`app/student`, `app/contributor`); School Times is loaded separately and
scoped only to the landing route group (`app/(landing)/layout.tsx`) as
`--font-landing-display`, matching the backend templ landing exactly.
JetBrains Mono still loads from `next/font/google` (`--font-merit-mono`) —
no local copy of it exists in this design system.

**Known gaps, follow-up work:**
- Component border-width (2px per §4) isn't retrofitted onto every
  `components/ui/*` primitive yet — only the CSS variable color is mapped.
  Hard-offset shadows (§4) aren't applied to shadcn cards/buttons either.
- No square favicon/app-icon asset exists yet — `assets/logo.png` is a
  1536×1024 wordmark, not favicon-shaped.
- This section covers step 1 (setup + skeletons) of the frontend unification
  only. Full component-level parity with §5 (buttons/cards/inputs/pills/
  progress/toggles/tab bar) lands as the real admin/student/contributor UI
  gets built in later phases.

---

## 9. v2 decisions (approved 2026-09-26)

Full rationale, measured contrast data and the migration roadmap live in
`IMPROVEMENT-PLAN.md`. Until the Phase 1 token pipeline lands, these rules
override any older wording above.

| ID | Decision |
|---|---|
| D1 | Brand yellow = `#FFCC00` (accents, CTAs, rewards). `#F2D43B` = large fills + warning only |
| D2 | `#9ED5B7` = light-mode success. `#9CE7C8` = dark-mode success + category tint |
| D3 | `bg.app` = `#FFF7ED` for all product UI; `#FFEFD7` = brand / landing bands |
| D4 | `text.primary` = `#29261B`; `surface.inverse` = `#312A31` |
| D5 | Checkbox: form selection = purple + white ✓; completion = mint + ink ✓ |
| D6 | One icon family on both platforms: Phosphor (Bold / Fill) + `merit-flame`, `merit-coin` |
| D7 | Admin / contributor dashboards use **compact density**: 1.5px borders on table cells, s1–s2 shadows, 8–12 padding; full hard shadows only for primary actions and floating layers |

---

## 10. Token reference (generated)

<!-- MERIT-TOKENS:BEGIN (generated by scripts/build-tokens.mjs — do not edit by hand) -->
Tokens **v2.1.0**. Source of truth: `tokens/*.tokens.json`; build with `npm run build`.
Outputs: `build/css/merit-tokens.css` (web), `build/dart/merit_tokens.dart` (Flutter),
`build/json/merit-tokens.json`. Never hand-edit outputs or hard-code these hex values.

### Semantic colours

| Token | Light | Dark | CSS | Flutter |
|---|---|---|---|---|
| `bg.app` | `#FFF7ED` | `#1B161B` | `--merit-bg-app` | `context.meritColors.bgApp` |
| `bg.brand` | `#FFEFD7` | `#1B161B` | `--merit-bg-brand` | `context.meritColors.bgBrand` |
| `surface.default` | `#FFFFFF` | `#2A222A` | `--merit-surface-default` | `context.meritColors.surfaceDefault` |
| `surface.sunken` | `#FFF7ED` | `#241D24` | `--merit-surface-sunken` | `context.meritColors.surfaceSunken` |
| `surface.inverse` | `#312A31` | `#FFF7ED` | `--merit-surface-inverse` | `context.meritColors.surfaceInverse` |
| `surface.selected` | `#EDE4F8` | `#6E36B8` | `--merit-surface-selected` | `context.meritColors.surfaceSelected` |
| `text.primary` | `#29261B` | `#FFF7ED` | `--merit-text-primary` | `context.meritColors.textPrimary` |
| `text.secondary` | `#5A4A5A` | `#C4B5C4` | `--merit-text-secondary` | `context.meritColors.textSecondary` |
| `text.tertiary` | `#685A68` | `#9C8C9C` | `--merit-text-tertiary` | `context.meritColors.textTertiary` |
| `text.link` | `#6E36B8` | `#B48CE8` | `--merit-text-link` | `context.meritColors.textLink` |
| `text.onPrimary` | `#FFFFFF` | `#FFFFFF` | `--merit-text-on-primary` | `context.meritColors.textOnPrimary` |
| `text.onAccent` | `#312A31` | `#312A31` | `--merit-text-on-accent` | `context.meritColors.textOnAccent` |
| `text.onInverse` | `#FFF7ED` | `#312A31` | `--merit-text-on-inverse` | `context.meritColors.textOnInverse` |
| `text.onSuccess` | `#312A31` | `#1B161B` | `--merit-text-on-success` | `context.meritColors.textOnSuccess` |
| `text.onError` | `#FFFFFF` | `#1B161B` | `--merit-text-on-error` | `context.meritColors.textOnError` |
| `border.default` | `#000000` | `#FFF7ED` | `--merit-border-default` | `context.meritColors.borderDefault` |
| `border.subtle` | `#E7D8C6` | `#3A2F3A` | `--merit-border-subtle` | `context.meritColors.borderSubtle` |
| `shadow.color` | `#000000` | `#FFF7ED` | `--merit-shadow-color` | `context.meritColors.shadowColor` |
| `action.primary` | `#8E55D7` | `#8E55D7` | `--merit-action-primary` | `context.meritColors.actionPrimary` |
| `action.primaryPressed` | `#6E36B8` | `#6E36B8` | `--merit-action-primary-pressed` | `context.meritColors.actionPrimaryPressed` |
| `action.accent` | `#FFCC00` | `#FFCC00` | `--merit-action-accent` | `context.meritColors.actionAccent` |
| `feedback.success` | `#9ED5B7` | `#9CE7C8` | `--merit-feedback-success` | `context.meritColors.feedbackSuccess` |
| `feedback.successText` | `#2D6649` | `#9CE7C8` | `--merit-feedback-success-text` | `context.meritColors.feedbackSuccessText` |
| `feedback.warning` | `#F2D43B` | `#F2D43B` | `--merit-feedback-warning` | `context.meritColors.feedbackWarning` |
| `feedback.error` | `#C4393A` | `#FF9A9A` | `--merit-feedback-error` | `context.meritColors.feedbackError` |
| `feedback.errorSubtle` | `#F4C7C7` | `#93001A` | `--merit-feedback-error-subtle` | `context.meritColors.feedbackErrorSubtle` |
| `focus.ring` | `#8E55D7` | `#B48CE8` | `--merit-focus-ring` | `context.meritColors.focusRing` |

Component tokens (quiz option states, timer, tier, grade A–F, subject category 1–6, chart 1–5),
spacing (`--merit-space-*` / `MeritSpace`), radii, border widths, hard shadows
(`--merit-shadow-s1…s5` / `context.meritColors.shadowS1…S5`), motion and the type scale
(`--merit-type-*` / `MeritTypeScale`) are in the generated files.

### Contrast gate — 90 checks (45 pairs × light/dark), all ≥ AA

Lowest five:

| Theme | Foreground | Background | Ratio | Min |
|---|---|---|---|---|
| light | `focus.ring` | `bg.app` | 4.46 | 3 |
| light | `text.onPrimary` | `action.primary` | 4.74 | 4.5 |
| light | `focus.ring` | `surface.default` | 4.74 | 3 |
| dark | `text.onPrimary` | `action.primary` | 4.74 | 4.5 |
| dark | `text.tertiary` | `surface.default` | 4.88 | 4.5 |
<!-- MERIT-TOKENS:END -->
