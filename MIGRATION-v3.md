# Migrating to Merit DS v3

v3.0.0 is a breaking token release. See `CHANGELOG.md` for the full rename map and
`DECISIONS-v3.md` for the reasoning. Each consumer migrates on **its own branch**, pins the new DS
commit, and keeps CI drift checks green.

**Order of work:** tokens and theme plumbing come first, then shared widgets and components, then
screens by impact. Ship behind no flag. v3 is a whole-app reskin, so merge it when the shared layer
is done and the top screens have been reviewed.

---

## 1. Flutter (`merit-project-flutter`)

**Branch:** `feat/design-system-v3` from `dev`.

### 1.1 Tokens and fonts
1. Copy `build/dart/merit_tokens.dart` to `lib/theme/merit_tokens.dart` exactly as generated.
   The drift check (`check-drift.mjs --dart`) must pass.
2. Add General Sans (Medium, Semibold, Bold and their Italics) to `assets/google_fonts/`. That repo
   is private, so embedding it is allowed under the FFL. Declare the family `GeneralSans` in
   `pubspec.yaml` and remove `ClashDisplay`.
3. Remove the `google_fonts` dependency if nothing else uses it.

### 1.2 `lib/theme/merit_theme.dart`
- **Remap `MeritColors.*` aliases to v3 primitives.** This recolours all 541 call sites at once.
  Suggested mapping:

| Old alias | v3 |
|---|---|
| `purple` | `MeritPalette.violet700` (fill), with links via `context.meritColors.textLink` |
| `purpleDeep` | `violet800` |
| `purpleLight` | `violet100` |
| `yellow`, `yellowBrand` | `butter300` |
| `mint` | `sage300` |
| `cream` | `canvas50` |
| `ink` | `ink900` |
| `inkDeep` | `night900` |
| `inkSurface` | `night800` |
| `pink` | `blush300` |
| `blue` | `sky300` |
| `error` | `red600` |
| `textDim` | `ink700` |
| `textMute` | `ink500` |

  Then add a lint (a `custom_lint` rule or a CI grep) that forbids **new** `MeritColors.` uses in
  `lib/features/**`. Burn the remaining uses down toward `context.meritColors`.
- **Primary action:** buttons that used `MeritColors.purple` with white text become
  `actionPrimary` with `textOnPrimary` (ink). This is the biggest visual change, so review every
  `MeritButton` variant.
- **Borders and shadows:**
  - `MeritShadows.brutal*` becomes `context.meritColors.elevationE1…E3`.
  - `MeritBorders.resolve(context)` on **cards** goes away entirely (cards are borderless).
    Keep it only for inputs (`borderDefault`, 1.5) and illustration (`borderStrong`).
  - Expect most of the 115 `MeritBorders` uses to be deleted rather than replaced.
- **`MeritTypography` becomes `MeritTypeScale`:**
  - Display, headline and title styles point at the General Sans styles.
  - Convert the 113 literal `fontSize:` values in features to scale styles while you are in each file.
- **`ThemeData`:**
  - `scaffoldBackgroundColor` is `bgApp`.
  - `cardTheme` uses elevation 0 with `elevationE1` through a `DecoratedBox` wrapper.
  - `colorScheme.primary` is `actionPrimary` and `onPrimary` is `textOnPrimary`.
  - `focusColor` is `focusRing`.

### 1.3 Shared widgets (`lib/features/common/ui/widgets/`)
Restyle these first, in this order:
1. `merit_button`
2. `merit_content_card` / `shadow_box`
3. `merit_text_form_field`
4. `merit_pill` / `merit_badge` / `merit_subject_badge`
5. `merit_progress_bar` / `merit_progress_ring` / `merit_stepper`
6. `merit_toggle`
7. `merit_segmented_tabs` and the bottom bar in `main_screen`
8. `merit_quiz_option`
9. `merit_gamer_header`, `merit_leaderboard_row`, `merit_achievement_badge`
10. `merit_dialog`, `merit_snack_bar`, `merit_empty_data` / `merit_error` / `offline_container` (switch to the line-art `assets/v3/spots/*` SVGs; never a patchwork), `merit_shimmer`

The specs are in SKILL.md §5 and the reference site.

### 1.4 New widgets
- `MeritPatchwork`: per-node hierarchy patchworks (§1.4a below). Replaces the v3.0 category tiles.
- `MeritLearningPath`: replaces the plain hierarchy tree in `hierarchy_navigator`.
- `MeritSectionHeader`: eyebrow plus a title with an optional brush underline (a `CustomPainter` or the SVG). SI/TA versions get no uppercase.
- `MeritAchieverBand`: replaces the `Color(0x…)` gradient in `premium/ui/premium_screen.dart`.

### 1.4a `MeritPatchwork` (DS 3.2, SKILL.md §12)
**Data:** the backend adds `patchwork` to subject, topic and subtopic payloads (§3a). Add a
Freezed model:
```dart
@freezed
class Patchwork with _$Patchwork {
  const factory Patchwork({
    required String signature,
    required String version,
    required PatchworkUrls urls, // tile, row, mono, wash? (topics + subtopics)
    PatchworkInk? washInk,       // {light, dark} hex for the wash
  }) = _Patchwork;
}
```
**Widget:**
```dart
MeritPatchwork(
  patchwork: node.patchwork,          // nullable
  variant: PatchworkVariant.tile,     // tile | row | mono (wash: MeritPatchworkWash)
  fallbackCategory: subject.categoryIndex,
  semanticLabel: node.title,
)
```
- **Rendering:** `SvgPicture.network(url)`, cached on disk by `signature` (it is immutable per
  signature). Use the `flutter_cache_manager` already in deps, or add it.
- **Loading or missing:** draw the same frame with the `category.N` tint and a Phosphor
  **duotone** icon. Never show another node's patchwork.
- **Mono:** `colorFilter: ColorFilter.mode(color, BlendMode.srcIn)`.
- **Wash:** `MeritPatchworkWash(patchwork: subtopic.patchwork)` goes first in the card's
  `Stack`, inside its `ClipRRect`: `Positioned(top: 0, right: 0, width: min(cardWidth, 360))`,
  `SvgPicture.network(urls.wash, colorFilter: ColorFilter.mode(ink, BlendMode.srcIn))` inside an
  `Opacity` of 0.26 (light, `washInk.light`) or 0.16 (dark, `washInk.dark`). No wash URL → draw
  nothing (no fallback art behind copy). Content padding is unchanged.
- **Accessibility:** `tile` and `row` take the node title as their semantics label. The wash
  is `excludeFromSemantics`.

**Where each variant goes:**

| Widget | Variant |
|---|---|
| `subjects_screen` grid, `enrollment_card` | `tile` |
| `subject_details_screen` header | `row` (expanded) → `tile` (collapsed app bar) |
| `enhanced_topic_card`, `topics_list`, `hierarchy_sliver_list` topic rows | `row` (or `tile` in grid layout) |
| `enhanced_subtopic_card`, `subtopics_list` | `row` |
| `flippable_study_card` (front face), `study_card_stack`, `flashcard_dashboard_screen` deck tiles | subtopic `wash` |
| Notes list and note tiles (study screen) | subtopic `wash` |
| `hierarchy_breadcrumb_bar` | `mono` at 16dp |
| Quiz option cards, quiz-taking body, notes reader body | **none** (calm mode) |
| Empty / error / offline | **none**: line-art spots only |

**Verification:** golden tests for the four variants plus the fallback, in light and dark.

### 1.5 Icons
- `PhosphorIconsBold.*` becomes `PhosphorIconsRegular.*`, except active states (Fill) and category chips (Duotone).
- Replace the 143 Material `Icons.*` uses with Phosphor equivalents.

### 1.6 Screens (impact order)
home → quiz (mode select, taking, completion, attempt detail) → study / flashcards → subjects /
subject detail / hierarchy → leaderboard / points → premium → profile / settings → auth /
onboarding.

### 1.7 Verify
- `fvm flutter analyze` is clean.
- Golden or screenshot tests of the shared widgets pass in light and dark.
- Manual pass of the SI/TA strings on a small Android device (360dp).

---

## 2. Web frontend (`merit-project-frontend`)

**Branch:** `feat/design-system-v3` from `dev`.

### 2.1 Tokens
1. Copy `build/css/merit-tokens.css` to `app/merit-tokens.css` exactly as generated.
2. Bump `.design-tokens-ref` to the v3 DS commit.
3. Self-host General Sans in `app/fonts/` with `next/font/local`, as `--font-merit-display`. Drop
   Clash Display and drop School Times from `(landing)/layout.tsx`.

### 2.2 `app/globals.css`
- Re-map the shadcn variables per SKILL.md §9a. Note that `--primary-foreground` becomes **ink**.
- Replace `--shadow-brutal-1…5` with `--shadow-elev-1…3` mapped to `--merit-elevation-e1…e3`.
  Codemod the 49 files: `shadow-brutal-1/2/3` becomes `shadow-elev-1`, `shadow-brutal-4` becomes
  `shadow-elev-2`, and `shadow-brutal-5` becomes `shadow-elev-3`.
- Remove the `--merit-shadow-color`-based utilities.

### 2.3 Components
- `components/ui/button.tsx`:
  - Remove `border-2` and the `shadow-brutal-2` / `active:shadow-none` press.
  - Use `shadow-elev-1` with `active:translate-y-px active:shadow-none`.
  - The `outline` variant becomes an inset 1.5 `border-default`.
  - Add a `strong` variant.
- `components/ui/card.tsx`: remove `border-2` and use `rounded-[var(--merit-radius-xl)] shadow-elev-1`.
- Inputs, badges, tabs and sidebar follow SKILL.md §5 and §9b.

### 2.4 Guard (`scripts/check-design-tokens.mjs`)
- **Forbid** `shadow-brutal-*` (a v2 regression).
- **Allow** `shadow-elev-*`, and keep forbidding Tailwind's `shadow-sm…2xl`.
- **Forbid** `border-2` on `Card`.
- Keep the raw-hex, icon-import, `/admin` link and `backdrop-blur` guards.

### 2.5 Icons
In `lib/icons.tsx`, change the default weight from `bold` to `regular`. Audit the 4 explicit `fill`
uses, which stay as they are.

### 2.5a Patchworks
Add `components/merit/patchwork.tsx` (`<Patchwork patchwork={…} variant="tile|row|mono" />`) and `<PatchworkWash>`:
- `tile` and `row` render as `<img>` with `alt` = the node title.
- `wash` renders as an absolutely positioned `<span>` (top-right, `aria-hidden`) using the SVG as a CSS `mask` over `background: washInk.light|dark`, opacity 0.26 / 0.16 (see `.pwwash` in `merit-ds.css`).
- `mono` renders as a CSS mask over `currentColor`.

The fallback and the placement rules match Flutter §1.4a: subject, topic and subtopic cards and
lists, note and flashcard tiles (wash), and breadcrumbs (mono). Admin tables use `mono` only.

### 2.6 Landing (`app/(landing)`, `features/landing`)
Rebuild the hero, programme grid and CTA band from the landing specimen (reference site §29).

### 2.7 Verify
- `pnpm lint && pnpm build`.
- The guard script passes.
- The drift check passes.
- Visual pass of the admin pages in compact density, light and dark.

---

## 3. Backend templ landing (`merit-project-backend/internal/web/templates/`)

- Delete the hand-copied `--purple`, `--yellow`, `--mint`, `--cream`, `--ink` and `--line`
  variables and the inline hard shadows in `layout.templ`.
- Serve a vendored copy of `build/css/merit-tokens.css` from `web/static/css/`, and add a drift
  check to its CI.
- Replace School Times with self-hosted General Sans. The FFL allows self-hosting on our own site.
- Restyle the components (navbar, hero, about, features, subjects, pricing, testimonials,
  community, faq, cta, footer) to the landing specimen.
- Or, if the Next.js `(landing)` route is now canonical, retire the templ landing instead.
  **Decide this before investing in it.**

---

## 3a. Backend: `hierarchy_patchworks` (`merit-project-backend`, branch `feat/patchworks`)
- **Migration:** the `hierarchy_patchworks` table:
  - `node_type` is one of `subject`, `topic`, `subtopic` or `quest`;
  - plus `node_id`, `signature` (unique), `icon_id`, `engine_version`, `variants` JSONB and timestamps;
  - `UNIQUE(node_type, node_id)`.
- **Import:** `make patchworks-import MANIFEST=../merit-content/patchworks/manifest.json` upserts
  every node. Subjects resolve by `code`; topics and subtopics resolve by UUID.
- **API:** hierarchy, subject and topic responses add
  `patchwork: {signature, version, urls{tile,row,mono[,wash]}, washInk?}`. The URLs are built from
  `CONTENT_CDN_BASE` + the variant path.
- **Upload:** sync `merit-content/patchworks/out/` to the CDN bucket under `patchworks/`.

## 4. Out of scope
- `merit-project-admin` (legacy, folded into the frontend).
- Push and email templates. Do them in a follow-up and reuse the tokens and the wordmark lockups.
