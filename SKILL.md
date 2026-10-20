---
name: merit-design-system
description: >-
  The Merit Project design system v3: a warm, calm-to-study, gamified
  education brand for Sri Lankan O/L & A/L students. Use this skill whenever
  building or styling ANY Merit Project surface: the Flutter mobile app, the
  student/admin/contributor web app, the landing page, or supporting graphics.
  It defines the canonical tokens (canvas, ink-slate, orange, violet, sage,
  butter), General Sans + Plus Jakarta Sans typography, soft elevation, the
  patchwork illustration kit, calm vs energy screen modes, component recipes
  (buttons, cards, inputs, chips, progress, quiz options, flashcards, learning
  path, gamification), dark mode, Phosphor icon rules and copy voice, with
  ready-to-paste Flutter (Dart) and CSS snippets.
---

# Merit Project: Design System v3

> **Learn it. Level up. Earn Merit.**
> A gamified exam-prep platform for Sri Lankan **O/L** and **A/L** students:
> quizzes, flashcards, past papers, streaks and adaptive practice across
> **Sinhala, Tamil and English**.

This skill is the single source of truth for the Merit brand across the **Flutter app**, the
**web frontend** (student, admin and contributor) and the **landing page**.

**References:**
- **Reference site:** `Merit Design System.html`
- **Decisions:** `DECISIONS-v3.md` (D0–D15)
- **Research:** `research/v3/`
- **Migration from v2:** `MIGRATION-v3.md`

**Inspiration:** MindInventory's "Online Learning" shot on Dribbble (18955306). We use its
grammar only, never its layouts or art.

> **Migration status (2026-10-16):** tokens v3.0.0 are built here. The Flutter and web apps
> still vendor **v2.1.0** until each migrates on its own branch (`MIGRATION-v3.md`). When you
> edit an app that hasn't migrated, follow that app's vendored tokens. Don't mix v2 and v3
> values in one screen.

---

## 1. Brand essence

Merit is **warm, clear and quietly playful**. A calm canvas suits hours of study, and the game
layer is bright enough that every streak feels earned.

**Three pillars to keep in every screen:**
1. **Calm canvas.** A warm off-white page, ink-slate text, and soft depth with no hard outlines on UI chrome.
2. **Earned energy.** Orange, sparkles and the brush underline are reserved for actions, rewards and celebration.
3. **Patchwork learning.** Every subject, topic and subtopic has its own generated patchwork (§12), and topics connect as a dotted learning path. The illustration system is also the navigation.

Tri-lingual is first-class: EN / SI / TA switchers, and content that is specific to Sri Lanka
(A/L streams, districts, schools).

**Voice:** confident, encouraging, short. "Keep your streak alive." "Hit your weak spots
first." "12 of 50 questions today." Never shaming ("You're falling behind!"), never corporate.
Emoji are fine in **copy** (push notifications, celebratory text) but are **never UI icons**.

---

## 2. Colour

**Use semantic tokens only.** In CSS that means `var(--merit-text-primary)`. In Flutter it means
`context.meritColors.textPrimary`. Never use raw hex or primitives in screens. The full
light/dark table is generated in §10.

**Families (D10):**

| Family | Key values | Role |
|---|---|---|
| **Canvas** | `#FBFAF4` / `#F4F1E6` / `#E9E4D4` | `bg.app`, `surface.sunken`, dividers |
| **Ink-slate** | `#1E1B2E` / `#4A4760` / `#68667F` | Text primary / secondary / tertiary. Ink is also the illustration outline |
| **Orange** | **`#F65E16`**, pressed `#EA540E`, strong `#B23F06` | `action.primary`, eyebrow text (700), energy |
| **Coral / sand** | `#FC906C` / `#FCEBD3`, `#F0DEC0` | Patch tints, `bg.brand` (sand 100) |
| **Violet** | **`#54306C`** (700), `#663696` (500), `#E7DCF2` (100), electric `#7E24DE` (sparkles only) | `action.accent`, feature band, Achiever, links, focus, selection |
| **Sage** | `#A2D2AE` / `#E2F2E6` / `#2F6B43` | Success fill / subtle / text |
| **Butter** | `#FFD66B` / `#F5B700` | Rewards, warning, coin glyph, Achiever seal |
| **Blush / sky** | `#F6B5C3` / `#BCD6F2` | **Subject categories only** |
| **Red** | `#C7362F` (light), `#FF9A8F` (dark) | Error |
| **Night / mist** | `#17121F` / `#221B2C` … `#F7F3EA` | Dark mode (§6) |

**Hard rules:**
- **D9:** brand orange takes an **ink** label (`text.onPrimary`, 5.22:1). **White on orange
  fails WCAG and is never used.** Dense or long labels use `action.primaryStrong` (`#B23F06`)
  with white (5.82:1).
- **Links, the focus ring and form selection are violet.** Orange is too light for focus on the
  canvas (2.85:1).
- **D5:** *selected* means violet with a white ✓. *Completed or achieved* means sage with an
  ink ✓. The two must never look alike.
- Correct and wrong answers always pair colour with an **icon** (✓/✕). Colour is never the only
  signal.
- No gradients, and no new hues. If a role is missing, add a semantic token here and don't
  write a hex in the app.

---

## 3. Typography

| Family | Where | Weights |
|---|---|---|
| **General Sans** (D8) | Headings, titles, numbers, the wordmark, the italic emphasis voice. Product and landing alike (School Times is retired, D13) | 500 / 600 / 700, plus italics |
| **Plus Jakarta Sans** | Body, labels, form values, eyebrows | 400–700 |
| **Noto Sans Sinhala / Tamil** | Fallback in every stack for SI/TA glyphs | 400–700 |

**Type scale** (`--merit-type-*` / `MeritTypeScale.*`):
- display xl/lg/md: 56/40/32, weight 600, tracking −0.03…−0.02em
- title lg/md: 24/20, General Sans 600. title sm: 16, Jakarta 700
- **emphasis lg/md:** 24/18, General Sans 600 *italic*
- body lg/md/sm: 16/14/12, Jakarta 500
- label md/sm and **eyebrow:** 12/11, 700, uppercase, tracked. **Nothing goes below 11px.**
- numeric xl/lg/md: 48/32/20, 700, **tabular figures**. Use these for timers, points and ranks.

**Emphasis pattern:** use at most one key word per heading. Set it in the emphasis style
and/or draw the **brush underline** under it (`decor.underline`,
`assets/v3/motifs/brush-underline-mono.svg` as a CSS mask). The underline sits under the text
box, so it works with Sinhala and Tamil.

**Eyebrow pattern:** a small uppercase `text.eyebrow` (orange 700) label above section
headings. **SI/TA eyebrows are never uppercased and have tracking 0.**

**SI/TA rules (C4):**
- letter-spacing 0
- body line-height ≥ 1.6, display ≥ 1.3
- buttons, chips and tabs wrap and never truncate (Tamil runs +30–40%)
- language names appear in their own script: English / සිංහල / தமிழ்

**Fonts and licensing:**
- General Sans is under the ITF Free Font License, which **forbids redistribution from a public
  repo**. This repo gitignores it (`assets/fonts/README.md`).
- The apps bundle and self-host their own copies. On Flutter the family is `GeneralSans`.
- Never load it from Google Fonts. Don't use the `google_fonts` package.

```dart
Text('Keep your streak alive', style: MeritTypeScale.titleLg.copyWith(color: context.meritColors.textPrimary));
Text('04:59', style: MeritTypeScale.numericLg); // tabular figures built in
```

---

## 4. Shape and depth (D11)

The neo-brutalist black outline and hard offset shadow are **retired**.

| Property | Token | Notes |
|---|---|---|
| **Elevation** | `elevation.e0–e3` → `--merit-elevation-e*` / `context.meritColors.elevationE*` | Soft, violet-tinted, at most 2 layers. e1 is cards, chips and search. e2 is the tab bar, toasts and hover. e3 is dialogs and sheets |
| **Card border** | none | A card **never** combines a border with elevation |
| **Border widths** | hairline 1 · base 1.5 · strong 2 | Base is for inputs, filter chips and patchwork outlines. Strong is for selected and focused edges |
| **Radii** | xs 6 · sm 10 · md 16 · lg 20 · xl 24 · 2xl 32 · pill | Cards are xl. Inputs and quiz options are md. Sheets and bands are 2xl. Buttons and chips are pill |
| **Ink outline** | `border.strong` / `category.outline` | Only on illustration, filter chips, patchwork tiles and learning-path nodes |

```css
.card { background: var(--merit-surface-default); border-radius: var(--merit-radius-xl); box-shadow: var(--merit-elevation-e1); }
```
```dart
BoxDecoration(
  color: context.meritColors.surfaceDefault,
  borderRadius: BorderRadius.circular(MeritRadii.xl),
  boxShadow: context.meritColors.elevationE1,
);
```

---

## 5. Components (quick reference; live demos in the reference site)

**Buttons**
- Pills, S 36 / M 48 / L 56.
- **Variants:**
  - primary: orange with an ink label, e1
  - strong: burnt orange with a white label
  - accent: violet with white
  - inverse: ink
  - ghost: 1.5 inset border
  - link: violet underline
- **Loading:** a spinner replaces the label and the width stays locked.
- **Disabled:** .4 opacity and no elevation.
- **Press:** move down 1px and drop to e0.

**Cards:** borderless, xl, e1.
- feature: violet `surface.feature`
- reward: butter
- success: sage-subtle
- selected: a 2px violet inset
- interactive: rises to e2 on hover

**Inputs**
- md radius, 1.5 `border.default` (≥3:1).
- **Focus:** violet border plus a soft violet ring.
- **Label** always visible above the field. **Help and error text** go below, and errors carry an icon.
- **Phone fields** use a `+94` prefix. **OTP** is 6 boxes.

**Search pill:** a white pill on e2 with a round orange action button.

**Chips and badges**
- **Filter chip:** 1.5 ink outline. The selected chip fills violet.
- **Badges:** flat, at least 24 high, 11.5px label.
- **Subject badge:** category tint plus the node's `mono` patchwork icon (§12).

**Progress**
- **Bar:** a sunken track. The fill is orange in energy screens and violet in calm screens.
- **Ring:** carries a tabular number.
- **Stepper:** done is sage ✓, current is orange, to-do is sunken, with a dotted connector between steps.

**Toggles:** 48×28, with the on state violet. For checkboxes and radios, follow D5.

**Tab bar:** floats on e2 with a 2xl radius, 5 items max. The active item is a
`surface.selected` pill with a Fill icon. Labels are at least 11px, touch targets at least 48dp,
and the bar respects the safe area.

**Segmented control:** a sunken track. The active segment is white on e1.

**Dialog / sheet:** e3, 2xl radius, over a 50% ink scrim. Sheets get a drag handle.

**Toast:** the inverse surface on e2, shown for 4s, with an icon and at most one action.

**Skeleton:** sunken blocks with no border. Shimmer is off under reduced motion.

**Quiz option**
- At least 56 high, with a letter chip. Options lock once the answer is submitted.
- **States** (`quizOption.*`): idle · selected (violet) · correct (sage-subtle + ✓) · wrong (red-subtle + ✕) · revealed (dashed sage).

**Timer (v3.5, colour-only):** no pill. The digits and the timer icon change colour: `timer.text` above 5 min, `timer.warnText` at ≤5 min (orange-700 light / butter-300 dark), `timer.criticalText` at ≤1 min. Paper timers count **down**. Each change is announced to screen readers. The pill tokens (`timer.safe/warn/critical/fg/criticalFg`) are deprecated and go in v4.

**Subject hub header (v3.5):** the hero is tinted with the subject's `color_hex` mixed into `subject.headerBase` at `opacity.subjectTintLight` (0.30) or `opacity.subjectTintDark` (0.24); dark adds a 1.5 bottom rim of the subject colour at `opacity.subjectRimDark`. Text on the tint uses `text.primary` and `text.secondary` only: no `text.tertiary`, no orange eyebrow. `node scripts/check-subject-tints.mjs <subject-colors.json>` gates every subject in both themes. The tile and section names sit on the tint; it collapses to a 56dp bar with the tile at 32.

**Flashcard:** the front takes any **tone** (`flashcard.<sage|sky|coral|butter|violet|blush>.bg`, ink text in both themes) or stays plain (`surface.default`), and carries its subtopic's `wash` (§12). On a tone the wash ink is `flashcard.<tone>.wash` (the tone mixed 42% toward ink) at 30% layer opacity, so the colour belongs to the card and the pattern's shape signs the subtopic; a plain card uses the manifest's `washInk`. Note tiles follow the same rule. The back is white. The flip runs 2 × `slow`, or crossfades under reduced motion. FSRS rating buttons are Again (coral), Hard (sand), Good (sage) and Easy (violet).

**Learning path:** the topic hierarchy shown as tiles joined by dotted connectors.
- **Node states:** done (sage ✓), current (larger, orange, sparkle, %), locked (sunken + lock).
- On mobile the path scrolls horizontally.

**Gamification**
- **Header chips:** the streak is an orange Fill `flame`, and points are a butter Fill `coins`. Numbers are tabular.
- **Streak ribbon:** done days are orange, today is butter with an ink ring, future days are a hairline outline.
- **Leaderboard:** a podium, then rows. The "You" row is violet-selected and sticks when scrolled off-screen.
- **Grades A–F:** sage, sage-subtle, butter, orange-300, coral, red. The letter is always shown.
- **Points breakdown:** +10 per correct answer, +20 when accuracy is ≥80%, ×1.5 for Achiever.

**Tiers (C6)**
- **Wanderer:** neutral.
- **Feature banners** (`.band`, tokens `banner.*`, D17): a violet **stadium** with hairline circle arcs off the left edge and an orange disc clipped at the top-right with one echo arc. The band and the disc each carry one pattern, tone on tone, that dissolves before the copy. Each context owns a pair: **cta** halftone · chevron, **achiever** diamonds · arcs, **promo** plus · waves, **streak** dashes · scales (`assets/v3/banners/<ctx>-{field,disc}.svg`). Copy is white. The action (white button or pill input) sits on the copy's row at the right, vertically centred; when the row cannot fit both it wraps to its own row, still **right-aligned** (thumb side), never stranded under the copy on the left. Below 760px the stadium becomes a 2xl rounded rectangle. At most one per screen. Patterns only, never pack icons.
- **Quota meter copy:** "32 of 50 questions today", never shaming.

**Empty / error / offline:** a line-art spot (`assets/v3/spots/`), one line of text and one CTA. Spots are never patchworks (§12).

---

## 6. Modes and dark mode (D15)

**Calm mode** (quiz-taking, paper mode, notes reader)
- Canvas or white surfaces, slate text, violet selection.
- **No** sparkles or brush underlines. Patchworks appear only as a subtopic's `wash` behind note and flashcard tiles, never inside the reading or quiz body.
- At most **one** orange action.

**Energy mode** (home, rewards, results, leaderboard, landing)
- Orange, butter, patchwork and sparkles.
- Celebration motion up to 600ms.

**Dark mode** is a violet-black base, never neutral grey:

| | Light | Dark |
|---|---|---|
| `bg.app` | `#FBFAF4` | `#17121F` |
| `surface.default` | `#FFFFFF` | `#221B2C` |
| `text.primary` | `#1E1B2E` | `#F7F3EA` |
| `action.primary` | `#F65E16` | `#FF8A4C` (still with an ink label) |
| `text.link` / `focus.ring` | `#663696` | `#C9B3EA` |
| Elevation | violet-tinted | black, stronger. Depth comes mostly from surface steps |

**Theme scopes:**
- **Light** applies on `:root`, `.light` and `[data-theme="light"]`.
- **Dark** applies on `.dark` and `[data-theme="dark"]`.
- You can nest either inside the other, for example a light island on a dark page.

---

## 7. Motion

| Duration | Value | Use |
|---|---|---|
| instant | 80 | — |
| fast | 120 | Press |
| base | 180 | Toggle, tab |
| slow | 280 | Sheet, card-flip half |
| celebrate | 600 | Grade, level-up |

- **Curves:** `standard` for movement in and within the screen, `exit` for things leaving.
- **Reduced motion** (`MediaQuery.disableAnimationsOf` / `prefers-reduced-motion`): no shimmer, no sparkle twinkle, and a crossfade instead of the flip.

---

## 8. Iconography (D12)

- **Phosphor only, on both platforms:** `phosphor_flutter` and `@phosphor-icons/react`. On web, import through `@/lib/icons`.
- **Weights:**
  - **Regular** by default. Bold is retired as the default.
  - **Fill** for active and selected states.
  - **Duotone** on category and feature chips.
- **Size:** 20–24px in UI, 1.15em inside buttons.
- **Colour:** icons inherit the text colour. Only reward glyphs carry their own colour: the orange `flame` and the butter `coins`.
- No Material `Icons.*`, no lucide, no tabler, and no emoji as icons.

---

## 9. Illustration kit (D14, D16)

`scripts/brand/build_v3_brand.py` generates the brand, motifs, banners and spots into `assets/v3/`.
`scripts/patchwork/` generates hierarchy patchworks (§12). `assets/v3/index.html` previews both.

- **Hierarchy patchworks:** see §12. They replace the v3.0 six category tiles.
- **Patterns** (`patterns/*.svg`): legacy CSS-background swatches (dots, stripes, checks, hatch).
  Patchworks use the 16 geometry-expanded patterns in `scripts/patchwork/patterns.py`.
- **Motifs** (`motifs/*.svg`):
  - 4-point sparkle in violet, warm or `currentColor` (rewards and celebration only)
  - brush underline (colour or mono mask)
  - dotted connector with node circles
- **Spots** (`spots/*.svg`): empty, error, offline, not-found, success. **Line art**: one flat
  tinted blob plus a single 2.5 ink line drawing. No frame, patches, patterns or pack icons.

**Rules:**
- At most 2–3 sparkles per composition, and **never on a patchwork**.
- No patchwork in admin tables (use `mono`).
- No freehand people, stock art or gradients.
- SVG only. Don't hand-edit the outputs: change the generator and re-run it.

---

## 9a. Web / shadcn mapping (merit-project-frontend, target for v3)

The shadcn variables re-point at v3 semantics. The names are kept so `components/ui/*`
restyles automatically.

| shadcn | v3 token |
|---|---|
| `--background` | `--merit-bg-app` |
| `--card`, `--popover` | `--merit-surface-default` |
| `--foreground` | `--merit-text-primary` |
| `--primary` / `--primary-foreground` | `--merit-action-primary` / `--merit-text-on-primary` (**ink**) |
| `--secondary` / `-foreground` | `--merit-surface-sunken` / `--merit-text-primary` |
| `--accent` / `-foreground` | `--merit-action-accent` / `--merit-text-on-accent` |
| `--muted` / `-foreground` | `--merit-surface-sunken` / `--merit-text-secondary` |
| `--destructive` | `--merit-feedback-error` |
| `--border`, `--input` | `--merit-border-default` |
| `--ring` | `--merit-focus-ring` |
| `--radius` | `--merit-radius-lg` |
| `--chart-1..5` | `--merit-chart-1..5` |
| `shadow-brutal-1…5` | **replaced by** `shadow-elev-1…3` (`--merit-elevation-e1…e3`) |

The frontend guard `scripts/check-design-tokens.mjs` must change in two ways. It must
**forbid** `shadow-brutal-*`, and it must **allow** `shadow-elev-*` while still forbidding
Tailwind's `shadow-sm…2xl`. Keep the raw-hex and icon-import guards. See `MIGRATION-v3.md`.

---

## 9b. Layout & actions (web admin / contributor / student shells)

Added 2026-10-01 after an audit found per-page drift. Enforced where noted by `merit-project-frontend/scripts/check-design-tokens.mjs`.

- **Page header.** Every page opens with `PageHeader` (`components/shared/page-header.tsx`): title + description left, page-level actions right (wrap below the title on narrow screens). Pages add no horizontal padding of their own — the mode layout already provides `p-4`. Sections are separated with `space-y-6`.
- **Page actions** ("Add …", "Import", "Create") live in `PageHeader actions`, never in a table/filter toolbar. Toolbars hold filters and search only, left-aligned.
- **Form action rows:** `flex gap-3`, **left-aligned**, primary first (`Save` then `Cancel`), same button size throughout the form.
- **Dialog footers:** right-aligned, `Cancel` then primary (the shadcn `DialogFooter` default).
- **Header chrome controls** (sidebar trigger, search, theme, settings, avatar): all `h-9` and `rounded-full`, i.e. `Button variant="outline" size="icon"`; the search trigger is the same pill, wider. v2: `border-2 shadow-brutal-2`. **v3:** no border, `shadow-elev-1` on a `surface.default` fill.
- **Sidebar:** same chrome as the content pane; menu items are pills. v2: `border-2 rounded-xl shadow-brutal-2`, with the active item `bg-sidebar-primary border-2 shadow-brutal-1`. **v3:** `rounded-2xl shadow-elev-1`, no border, and the active item is a `surface.selected` pill with a Fill icon. No translucency / `backdrop-blur` on layout chrome (guarded).
- **Links** to mode routes carry the mode prefix (`/admin/...`); build admin URLs with `lib/admin-routes.ts` (guarded).
- **Density (D7):** admin and contributor screens are compact: 8–12 padding, hairline table rows, e0–e1, no patchwork in tables.

## 10. Token reference (generated)

<!-- MERIT-TOKENS:BEGIN (generated by scripts/build-tokens.mjs — do not edit by hand) -->
Tokens **v3.5.0**. Source of truth: `tokens/*.tokens.json`; build with `npm run build`.
Outputs: `build/css/merit-tokens.css` (web), `build/dart/merit_tokens.dart` (Flutter),
`build/json/merit-tokens.json`. Never hand-edit outputs or hard-code these hex values.

### Semantic colours

| Token | Light | Dark | CSS | Flutter |
|---|---|---|---|---|
| `bg.app` | `#FBFAF4` | `#17121F` | `--merit-bg-app` | `context.meritColors.bgApp` |
| `bg.brand` | `#FCEBD3` | `#1C1625` | `--merit-bg-brand` | `context.meritColors.bgBrand` |
| `surface.default` | `#FFFFFF` | `#221B2C` | `--merit-surface-default` | `context.meritColors.surfaceDefault` |
| `surface.sunken` | `#F4F1E6` | `#1C1625` | `--merit-surface-sunken` | `context.meritColors.surfaceSunken` |
| `surface.inverse` | `#1E1B2E` | `#F7F3EA` | `--merit-surface-inverse` | `context.meritColors.surfaceInverse` |
| `surface.selected` | `#E7DCF2` | `#3C244E` | `--merit-surface-selected` | `context.meritColors.surfaceSelected` |
| `surface.feature` | `#54306C` | `#3C244E` | `--merit-surface-feature` | `context.meritColors.surfaceFeature` |
| `text.primary` | `#1E1B2E` | `#F7F3EA` | `--merit-text-primary` | `context.meritColors.textPrimary` |
| `text.secondary` | `#4A4760` | `#B9B2C6` | `--merit-text-secondary` | `context.meritColors.textSecondary` |
| `text.tertiary` | `#68667F` | `#9C94AC` | `--merit-text-tertiary` | `context.meritColors.textTertiary` |
| `text.link` | `#663696` | `#C9B3EA` | `--merit-text-link` | `context.meritColors.textLink` |
| `text.eyebrow` | `#B23F06` | `#FF8A4C` | `--merit-text-eyebrow` | `context.meritColors.textEyebrow` |
| `text.onPrimary` | `#1E1B2E` | `#1E1B2E` | `--merit-text-on-primary` | `context.meritColors.textOnPrimary` |
| `text.onPrimaryStrong` | `#FFFFFF` | `#1E1B2E` | `--merit-text-on-primary-strong` | `context.meritColors.textOnPrimaryStrong` |
| `text.onAccent` | `#FFFFFF` | `#1E1B2E` | `--merit-text-on-accent` | `context.meritColors.textOnAccent` |
| `text.onFeature` | `#FFFFFF` | `#FFFFFF` | `--merit-text-on-feature` | `context.meritColors.textOnFeature` |
| `text.onInverse` | `#FBFAF4` | `#1E1B2E` | `--merit-text-on-inverse` | `context.meritColors.textOnInverse` |
| `text.onSuccess` | `#1E1B2E` | `#1E1B2E` | `--merit-text-on-success` | `context.meritColors.textOnSuccess` |
| `text.onWarning` | `#1E1B2E` | `#1E1B2E` | `--merit-text-on-warning` | `context.meritColors.textOnWarning` |
| `text.onError` | `#FFFFFF` | `#1E1B2E` | `--merit-text-on-error` | `context.meritColors.textOnError` |
| `border.default` | `#68667F` | `#9C94AC` | `--merit-border-default` | `context.meritColors.borderDefault` |
| `border.strong` | `#1E1B2E` | `#F7F3EA` | `--merit-border-strong` | `context.meritColors.borderStrong` |
| `border.subtle` | `#E9E4D4` | `#3A3048` | `--merit-border-subtle` | `context.meritColors.borderSubtle` |
| `action.primary` | `#F65E16` | `#FF8A4C` | `--merit-action-primary` | `context.meritColors.actionPrimary` |
| `action.primaryPressed` | `#EA540E` | `#FF9A63` | `--merit-action-primary-pressed` | `context.meritColors.actionPrimaryPressed` |
| `action.primaryStrong` | `#B23F06` | `#FF8A4C` | `--merit-action-primary-strong` | `context.meritColors.actionPrimaryStrong` |
| `action.accent` | `#54306C` | `#C9B3EA` | `--merit-action-accent` | `context.meritColors.actionAccent` |
| `action.accentPressed` | `#3C244E` | `#E7DCF2` | `--merit-action-accent-pressed` | `context.meritColors.actionAccentPressed` |
| `feedback.success` | `#A2D2AE` | `#A2D2AE` | `--merit-feedback-success` | `context.meritColors.feedbackSuccess` |
| `feedback.successSubtle` | `#E2F2E6` | `#1D3B28` | `--merit-feedback-success-subtle` | `context.meritColors.feedbackSuccessSubtle` |
| `feedback.successText` | `#2F6B43` | `#A2D2AE` | `--merit-feedback-success-text` | `context.meritColors.feedbackSuccessText` |
| `feedback.warning` | `#FFD66B` | `#FFD66B` | `--merit-feedback-warning` | `context.meritColors.feedbackWarning` |
| `feedback.warningText` | `#B23F06` | `#FFD66B` | `--merit-feedback-warning-text` | `context.meritColors.feedbackWarningText` |
| `feedback.error` | `#C7362F` | `#FF9A8F` | `--merit-feedback-error` | `context.meritColors.feedbackError` |
| `feedback.errorSubtle` | `#FBDAD6` | `#5A1A1A` | `--merit-feedback-error-subtle` | `context.meritColors.feedbackErrorSubtle` |
| `subject.headerBase` | `#FBFAF4` | `#1C1625` | `--merit-subject-header-base` | `context.meritColors.subjectHeaderBase` |
| `focus.ring` | `#663696` | `#C9B3EA` | `--merit-focus-ring` | `context.meritColors.focusRing` |
| `decor.sparkle` | `#7E24DE` | `#C9B3EA` | `--merit-decor-sparkle` | `context.meritColors.decorSparkle` |
| `decor.sparkleWarm` | `#F65E16` | `#FF8A4C` | `--merit-decor-sparkle-warm` | `context.meritColors.decorSparkleWarm` |
| `decor.underline` | `#F65E16` | `#FF8A4C` | `--merit-decor-underline` | `context.meritColors.decorUnderline` |
| `decor.connector` | `#68667F` | `#9C94AC` | `--merit-decor-connector` | `context.meritColors.decorConnector` |

Component tokens (quiz option states, timer, tier, grade A–F, subject category 1–6, chart 1–5),
spacing (`--merit-space-*` / `MeritSpace`), radii, border widths, soft elevation
(`--merit-elevation-e0…e3` / `context.meritColors.elevationE0…E3`), motion and the type scale
(`--merit-type-*` / `MeritTypeScale`) are in the generated files.

### Contrast gate — 152 checks (76 pairs × light/dark), all ≥ AA

Lowest five:

| Theme | Foreground | Background | Ratio | Min |
|---|---|---|---|---|
| light | `action.primary` | `bg.app` | 3.07 | 3 |
| light | `action.primary` | `surface.default` | 3.22 | 3 |
| light | `quizOption.wrong.border` | `quizOption.wrong.bg` | 4.03 | 3 |
| light | `text.onPrimary` | `action.primaryPressed` | 4.61 | 4.5 |
| light | `text.tertiary` | `bg.brand` | 4.73 | 4.5 |
<!-- MERIT-TOKENS:END -->

---

## 11. Logo & Merit Points coin

**Sources:**
- v3: `assets/v3/brand/*.svg`, generated by `scripts/brand/build_v3_brand.py`. It needs the local
  General Sans `.ttf` files and fontTools.
- v2 masters: `assets/brand/` (built by `scripts/brand/build_brand.py`). They stay until every
  consumer has migrated.

Never redraw or recolour by hand. Change the script and regenerate.

**The mark.** The cube-in-pyramid is already a patchwork, which fits v3. v3 makes three changes:
- recolours the facets to orange / coral / sage / violet with a sand cube top;
- **drops the hard offset shadow**;
- thins the outlines by 25%, in ink (`#1E1B2E`, or mist on dark).

The filenames and uses are unchanged from v2:

| File | Use |
|---|---|
| `merit-mark` / `-dark` | Default mark |
| `merit-mark-small` / `-small-dark` | 24–32px |
| `merit-cube` | 16px and favicons |
| `merit-mark-black` / `-white` | Single colour |
| `merit-mark-achiever` | Achiever tier |
| `merit-app-icon` | iOS and store icons, on sand |
| `merit-android-foreground` / `-monochrome` | Android adaptive and themed icons |
| `merit-lockup-*` | Mark plus wordmark |

**Wordmark (D13):**
- **MERIT** is set in General Sans **Bold Italic**, uppercase, followed by an **orange full stop**
  (`action.primary`).
- **PROJECT** sits below or beside it in General Sans Semibold, tracked +0.32em, in `text.secondary`.
- Both are outlined to paths in the lockups. A logo made with the font is not a derivative of the
  font under the FFL.
- In UI, live text can render the wordmark as `MERIT` plus an orange `.` in the emphasis style.

**Clear space:** at least twice the dot's diameter on every side. **Minimum sizes:** the mark
is 32px, the small cut 24px, the cube 16px.

**`merit-coin` (Merit Points):** the pyramid cut in **butter** facets (`#FFD66B` / `#F5B700`) with
ink outlines. Use `merit-coin-glyph-fill` (`currentColor`) inside chips. In UI, the Phosphor
`coins` Fill icon in `reward.points` is the default glyph.

**Don't:**
- recolour facets outside the generator;
- add shadows or gradients;
- rotate or stretch the mark;
- set the wordmark upright or in mixed case.

---

## 12. Hierarchy patchworks (D16)

**Every Subject, Topic and Subtopic has its own patchwork.** It is the node's identity wherever
the node appears. **Patterns + pack icons are hierarchy identity only.** Modes, rewards, tiers and
empty/error states must never use them.

**Grammar**
- **Frame:** a 256 rounded square (rx 32) with a 3.6 ink frame (`patchwork.seam`).
- **Body (square in a square, engine v4, D16 rev 4):** fixed cuts, symmetric on both axes and
  both diagonals (the economy quilt block). Each level **nests one shape inside its parent's**:

  | Level | Patches | Adds | Plate |
  |---|---|---|---|
  | Subject | 4 | hourglass X (top+bottom, left+right) + corner triangles (two diagonal pairs); 4 fresh styles, at most one solid | **square** |
  | Topic | 5 | a **diamond** with its points on the edge midpoints | **pentagon** (point-up) |
  | Subtopic | 6 | a **square** over the diamond; its corners poke out (8-point star) | **hexagon** (flat-top) |
  | Quest (reserved) | 7 | a wider square under the subtopic's, showing as a band | heptagon |

  A child keeps its parent's styles and its new patch is always the innermost. It uses a
  pattern the parent doesn't, a tint that differs from every patch it touches, and is
  **unique among siblings**. Uniqueness comes from tints, patterns, angle and density, never
  from the cuts.
- **Seams are crisp tint edges** with no ink, and each pattern **dissolves** toward the edges of
  the region it shows in: elements shrink to nothing over a 16-unit band and tiny ones are
  dropped. Only the frame and the plate keep ink outlines.
- **Patch fill:** a tint, or a tint plus one of **16 patterns**: dots, halftone, stripes, checks,
  hatch, waves, zigzag, chevron, triangles, grid, plus, arcs, diamonds, scales, bricks, dashes.
  Pattern ink is the patch tint mixed 42% toward ink. At most one **solid** patch (violet 500/700,
  orange 500 or sage 500, solid or dotted) per tile.
- **Icon:** from the licensed "filled outline" pack, restyled to the reference look:
  - fills become `patchwork.plate` (white);
  - the dominant hue becomes the node accent (with a deeper twin);
  - near-black and the outline become ink;
  - shade layers become `patchwork.iconShade`.
- **Icon:** always **centred**, 136 of 256, on a white plate with as many sides as the tile has
  patches (square 4, pentagon 5, hexagon 6, heptagon 7; rounded corners, 2.6 ink stroke).
- **No sparkles, shadows or gradients.** Tiles are theme-fixed:
  plates stay light in dark mode.
- **Mastery fill (the one exception, v3.5, D18).** Where a tile shows the student's progress on
  that node (the Learn quilt, the Home quilt, Stats), it may be drawn twice: a greyscale base at
  35% opacity, and the full-colour tile clipped from the bottom to the mastery percentage. Nothing
  else may alter a tile: no recolouring, cropping, filters or overlays, and never on a node that
  isn't showing progress.

**Colour comes from the subject** (engine v5, D16 rev 5). The subject's `color_hex` (backend
`subjects.color_hex`, mirrored as `color_hex` in merit-content `subjects/<S>/subject.json`) is the
only colour input. `scripts/patchwork/palette.py` keeps its **hue** and sets lightness and chroma
in OKLCH, so any hex gives a palette that sits with the DS tokens. The subject and **every node
below it** draw from it:

| Role | Recipe (OKLCH) | Use |
|---|---|---|
| Patch tints (7) | hue, hue ±28°, hue +60°, complement; L 0.86–0.955, low chroma | patch fills; pattern ink = tint mixed 42% toward ink |
| Solid | the subject colour itself (L kept 0.52–0.80) + a deeper twin | at most one solid patch per tile |
| Icon accent (3) | hue, hue ±22°; L ≈ 0.77, + a shade 0.10 darker | the icon's dominant hue and its darker twin |

The colour is part of the signature: change `color_hex`, regenerate, re-import (the importer
warns when the DB colour has drifted from the generated one). Pick subject colours that differ
in **hue**, since two subjects with one hue get look-alike branches. Without a `color_hex` a subject
falls back to a token family (warm, cool, fresh, mixed).
**Subject colours** are proposed per subject by `merit-content/tools/subject_colors.py` →
`subjects/_subject-colors.json` (62 subjects, unique; stream-mates ≥ 0.10 ΔE in the core
streams; no hues 18–55° or 294–314°) and applied by backend migration `000048_subject_colors`.

**Variants** (per node)

| Variant | Size | Use |
|---|---|---|
| `tile` | 1:1, 256 | Everywhere the node appears: subject grid and topic cards (96–160), list rows and headers (40–64). The 4:1 `row` was retired in v3.3: never stretch a tile into a banner |
| `wash` | 1:1, 400, transparent, `currentColor` | Background of **flashcard and note tiles**: the one pattern the subtopic **added** (its "+1" patch), radiating from the top-right corner and gone by about 45% of the diagonal. No icon, frame or seams. Tint it with the manifest's `ink.light` (≈26% layer opacity) or `ink.dark` (≈16%); text must sit on ≤ 6% ink. Only nodes that added a patch have one (not subjects). Questions don't get one. Replaces v3.1's `corner` |
| `mono` | `currentColor` icon | Dense tables, admin, chips, tab icons |

**Uniqueness**
- **Subject icons** are unique across all subjects.
- **Topic and subtopic icons** are unique within their subject.
- The **composition** (per-patch tint, pattern, angle, density; cuts and plate are fixed per level) is unique across **every node of every subject**, and the patch a child adds is unique among its siblings.
- **Signature:** `sha256(node_id ‖ icon_sha256 ‖ subject_color ‖ engine_version)`, where `icon_sha256` is the checksum of the canonical icon. It seeds the PRNG.
- **Registry:** `registry.json` in merit-content is append-only. On a key collision or a file over budget, it bumps a stored `salt`, so regeneration is byte-stable.
- **Quests:** the node id `quest:<subtopic_id>:<n>` is reserved for future Quests. They use the same engine and registry, so a quest's patchwork never collides with a node's.

**Budgets:** `tile` at most 48 KB, `wash` 40 KB. The SVG uses only
`path`/`rect`/`circle`/`polygon`, `clipPath` and `transform`.
There is no `<pattern>`, `<filter>`, `<mask>`, `<image>` or gradient, because
flutter_svg / vector_graphics must render every file (this is checked).

**Patterns as elements** (`scripts/patchwork/patterns.py`): every pattern is a list of small
elements, each drawn about its own anchor at a scale k ∈ (0, 1]; continuous patterns (stripes,
hatch, grid, waves…) are cut into cell-sized pieces that join up at k = 1. Seam dissolves, the
wash and banners all set k per element, so one engine drives every dissolve.

**Pipeline** (run from this repo; the icon pack is licensed and **never** committed here):
```bash
VENV=…/venv   # python3 -m venv; pip install fonttools pytest
$VENV/bin/python -m scripts.patchwork.build index    --icons ../Assets/patchwork-icons --content ../merit-content
$VENV/bin/python -m scripts.patchwork.build suggest  --content ../merit-content --subject BIOLOGY
$VENV/bin/python -m scripts.patchwork.build generate --content ../merit-content --subject PHYSICS --subject CHEMISTRY --subject BIOLOGY
$VENV/bin/python -m scripts.patchwork.build audit    --content ../merit-content
$VENV/bin/python -m scripts.patchwork.build demo     # public demo set (MIT Phosphor glyphs)
(cd scripts && $VENV/bin/python -m pytest -q patchwork)
```
- **Curation:** `merit-content/patchworks/maps/<SUBJECT>.json` maps a node `code` to `{icon, why}`. Unmapped nodes get a deterministic pool pick (science-adjacent sets first). Review in `merit-content/patchworks/index.html`.
- **Icon audit (Jev):** `tools/run.sh tools/patchwork_jev.py PHYSICS CHEMISTRY BIOLOGY` in merit-content ranks a 14-icon lexical shortlist per node (16 per app feature) with one Jev Choice (text only: set, name, tags) and writes `patchworks/reports/icon-audit.{json,html}`. Report-only: Jev can't see the drawings and filename puns fool it, so a person picks. `tools/run.sh tools/patchwork_review.py serve` opens the report as a picker (127.0.0.1 only; Claude's visual picks are badged), **Save** writes `reports/icon-selections.json`, and `… apply` writes `maps/<SUBJECT>.json` and `maps/_features.json`; then regenerate.
- **Feature icons (deferred, 2026-10-18):** app features use **Phosphor** like every other UI glyph. The groundwork stays: `maps/_features.json` can reserve one pack icon per feature (no node may reuse it; the audit fails otherwise), `generate` would then write `out/features/<key>/{color,mono}.svg`, and `patchwork_jev.py --features` re-suggests candidates.
- **Avatars:** avatar packs are indexed to `merit-content/patchworks/avatars/` with `avatars.json` (full colour, verbatim, never in the node pool). The review page has an Avatars tab to drop any from the student set.
- **Delivery:** the backend table `hierarchy_patchworks` (imported from `manifest.json`) exposes `patchwork {signature, version, urls{tile,mono[,wash]}, washInk?{light,dark}}` on hierarchy responses.
- **Going live is a manual release** (S3 upload + server import), not part of any deploy: merit-content `docs/PATCHWORKS-RELEASE.md`. Its CI warns until it's done.
- **Fallback:** if the URLs are missing, render the `category.N` tint + a Phosphor duotone icon in the same frame. Never borrow another node's patchwork.

**Don't:**
- edit the generated SVGs or recolour them in code;
- add sparkles, shadows or text to a patchwork;
- use patchworks for modes, tiers, rewards or empty states;
- reuse a patchwork for a different node.
