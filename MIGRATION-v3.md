# Migrating to Merit DS v3

v3.0.0 is a breaking token release. See `CHANGELOG.md` for the full rename map and
`DECISIONS-v3.md` for the reasoning. Each consumer migrates on **its own branch**, pins the new DS
commit, and keeps CI drift checks green.

**Order of work:** tokens and theme plumbing come first, then shared widgets and components, then
screens by impact. Ship behind no flag. v3 is a whole-app reskin, so merge it when the shared layer
is done and the top screens have been reviewed.

---

## 1. Flutter (`merit-project-flutter`)

**Branch:** `feat/design-system-v3` from `dev`. **Layouts:** follow `wireframes/DECISIONS.md` (the picked
variants on `wireframes.html`); this section says how, the board says what.

**Status (2026-10-24):** every v3 screen is built on the Flutter branch, which vendors DS 3.7.0 (`633bbdf`) and the
D1 coin (`89b53c7`). Remaining Flutter work is the Step 3 list in the pre-release plan (see `HANDOFF.md`).

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

- **Subject tint (D20):** `context.meritColors.subjectHeaderTint(color, brightness)` and `subjectHeaderRim` in
  `merit_theme.dart`. Text on a tint uses `textPrimary` / `textSecondary` only.
- **Guard:** `tool/check_design_tokens.dart` caps legacy `MeritColors.` / `MeritShadows.brutal` / `MeritBorders.`
  uses in `lib/features` at a baseline (lower it as screens are restyled) and bans the deprecated pill-timer tokens.

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
11. `MeritIllusBlock` + deco shapes (`merit_decoration_shapes.dart`): keep the art, drop the 2px line border and
    hard offset shadow, radius `xxl`, recolour to v3 primitives (register + onboarding step 1, board 08).
12. Quiz timer: colour-only (D19): digits + icon in `timerText` → `timerWarnText` (≤5 min) → `timerCriticalText`
    (≤1 min), no pill; paper timers count **down** from `duration_minutes`.

The specs are in SKILL.md §5 and the reference site.

### 1.4 New widgets (from the wireframe decisions)
| Widget | Board | Notes |
|---|---|---|
| Navigation shell | 00 B | Four tabs: Today · Learn · Compete · Me (floating bar, e2). Quiz taking, reviews, card sessions and the notes reader are full-screen, no tab bar. |
| `MeritHubHeader` | 04 hub header A + C tabs | Subject tint hero (D20), ring + tile 72–78, type-scale section switcher (Learn / Practise / Cards / Stats); collapses to a 56dp bar with tile 32. |
| `MeritQuiltMap` | 04 Learn A | Topic tiles in a 3-column quilt with the mastery fill (D18); tapping a topic opens its subtopics inline. Replaces the tree explorers (`tree_sliver_hierarchy_explorer`, `animated_tree_hierarchy_explorer`). |
| Subtopic sheet | 04 Subtopic A (revised) | Bottom sheet over the quilt: recipe ring (arcs = mastery parts, weights from the API) + Read → Remember → Prove rows whose bars match the arcs. |
| `MeritShareCard` | 02 Complete A (revised) | One 1080×1350 theme-independent template (light ticket on violet); quiz results first, later streaks, rank-ups, achievements. |
| Compete row | 05 Compete root | 84dp row: icon tile, title, teaser value (balance, rank, pending, progress). |
| Task row + state filter | 05 Tasks & Quests | Segmented Tasks / Quests; chips All · Pending · Completed · Expired with counts; referral tiers strip. |
| Stream row | 08 step 2 | Selectable row: category-tint icon tile, name, text subject labels, radio. No patchworks. |
| Subject-language row | 07 settings, 08 step 3 | Checkbox, tile 40, name, EN / සිං / த segmented switch (shown when ticked); greys languages missing from `available_languages`. |
| `MeritSectionHeader` | all | Eyebrow plus a title with an optional brush underline. SI/TA versions get no uppercase. |
| `MeritAchieverBand` | 06 Paywall A | Replaces the `Color(0x…)` gradient in `premium/ui/premium_screen.dart`. |

`MeritLearningPath` is **dropped**: Learn picked the quilt map (A), not the path (B).

### 1.4a `MeritPatchwork` (DS 3.2, SKILL.md §12)
**Data:** the backend adds `patchwork` to subject, topic and subtopic payloads (§3a). Add a
Freezed model:
```dart
@freezed
class Patchwork with _$Patchwork {
  const factory Patchwork({
    required String signature,
    required String version,
    required PatchworkUrls urls, // tile, mono, wash? (topics + subtopics)
    PatchworkInk? washInk,       // {light, dark} hex for the wash
  }) = _Patchwork;
}
```
**Widget:**
```dart
MeritPatchwork(
  patchwork: node.patchwork,          // nullable
  variant: PatchworkVariant.tile,     // tile | mono (wash: MeritPatchworkWash); row retired in DS 3.3
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
- **Card tones:** a flashcard or note card may take any `MeritFlashcardTone` (sage, sky, coral,
  butter, violet, blush → `flashcard<Tone>Bg`, text `flashcardFg` in both themes). Pass it as
  `MeritPatchworkWash(patchwork: …, tone: tone)`: the ink becomes `flashcard<Tone>Wash` at 0.30,
  theme-fixed. `tone: null` (plain `surface.default`) keeps `washInk.light/dark` as above.
- **Feature icons:** deferred (DS 3.3): features use Phosphor. If `features.json` ships later it
  maps each feature to `color` and `mono` SVGs (`out/features/<key>/`).
- **Avatars:** student avatars come from `merit-content/patchworks/avatars/avatars.json` (ids
  with `active: true`), full colour, shown in a circle; upload them with the patchworks.
- **Subject colour (DS 3.4):** a branch's patchworks are generated from its subject's
  `color_hex`, so any node UI that tints by subject (chips, progress bars, topic and subtopic
  headers) should use `subject_color` from the same subject. Changing a subject's colour in admin
  needs a patchwork regenerate + re-import; until then the importer reports colour drift.
- **Accessibility:** `tile` takes the node title as its semantics label. The wash
  is `excludeFromSemantics`.

**Where each variant goes:**

| Widget | Variant |
|---|---|
| `subjects_screen` rows (04 Subjects list A), `enrollment_card`, onboarding step 3 rows | `tile` at 40–56, leading |
| Learn quilt (`MeritQuiltMap`), Home subject row | `tile` with mastery fill (D18) |
| `MeritHubHeader` (replaces the `subject_details_screen` header) | `tile` at 72–78 in the ring (expanded) → 32 (collapsed bar) |
| `enhanced_topic_card`, `topics_list`, `hierarchy_sliver_list` topic rows | `tile` at 48–56, leading |
| `enhanced_subtopic_card`, `subtopics_list` | `tile` at 40–48, leading |
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
Shell first, because navigation B reshapes everything below it:
1. **Shell:** 4-tab bar (Today · Learn · Compete · Me) in `main_screen`, routes in `lib/routing/`.
2. **Today** (01 Home B + A's subject row).
3. **Subject hub:** header, Learn quilt + subtopic sheet, Practise, Cards, Stats (B + C's prediction card).
4. **Quiz:** taking A (colour timer), complete A revised + share card, review A, limit sheet → paywall.
5. **Study:** cards A, session A, notes reader A (progress in the header).
6. **Compete:** root rows → Points A, Leaderboard A, Tasks & Quests, Achievements B.
7. **Premium:** paywall A + limit sheet C.
8. **Me** A + settings (subject languages).
9. **Auth / onboarding:** register A, onboarding A revised (illustrations kept, stream rows, language rows).

Screens that need backend work first are listed in `wireframes/BACKEND-GAPS.md`; build them against the
fallbacks shown on the board until the endpoints land.

### 1.7 Verify
- `fvm flutter analyze` is clean.
- Golden or screenshot tests of the shared widgets pass in light and dark.
- Manual pass of the SI/TA strings on a small Android device (360dp).

---

## 2. Web frontend (`merit-project-frontend`)

**Branch:** `feat/design-system-v3` from `dev`. One Next.js app on one origin: landing `/`, `/admin`, `/student`,
`/contributor` (`lib/mode.ts`). This pass covers the foundations, the landing, the student portal and an admin
look-over; the contributor portal only gets what the shared components bring. Web layouts are picked on the
wireframe board's **Web** flow before screens are built.

### 2.1 Tokens and fonts
1. Copy `build/css/merit-tokens.css` to `app/merit-tokens.css` exactly as generated; bump `.design-tokens-ref`.
   `pnpm check:drift` compares it with a sibling DS checkout.
2. General Sans (500/600/700 + italics) via `next/font/local` as `--font-merit-display`. Drop Clash Display,
   School Times and the template's Geist fonts. The repo is private, so the font files may be committed.

### 2.2 Theme (D26)
- Re-map the shadcn variables in `app/globals.css` per SKILL §9a (`--primary-foreground` is **ink**,
  `--secondary` is `surface.sunken`).
- Replace `shadow-brutal-1…5` with `shadow-elev-1…3` (`--merit-elevation-e1…e3`). Codemod: brutal-1/2/3 → elev-1,
  `hover:shadow-brutal-2` → `hover:shadow-elev-2`.
- Keep the tweakcn theme picker. **Merit** is the first preset and the default; applying it clears inline
  overrides. The choice persists in `merit-color-theme`.
- Light/dark is `next-themes` (`.dark`) everywhere, the landing included.

### 2.3 Components
- `components/ui/*` may be edited. Button: no `border-2`, `shadow-elev-1`, press `active:translate-y-px
  active:shadow-none`, `outline` = inset 1.5 `border-default`, new `strong` variant. Card: no `border-2`,
  `rounded-[var(--merit-radius-xl)] shadow-elev-1`. Inputs, badges, tabs and sidebar per SKILL §5 / §9b.
- New `components/merit/`: `patchwork.tsx` (`<Patchwork variant="tile|mono">`, `<PatchworkWash>`, category
  fallback), `merit-coin.tsx` (D21), `mastery-ring.tsx`, `stat-chip.tsx`.
- Data: `@tanstack/react-query` in the student and admin layouts; new screens use query hooks.
- Remove the shadcn-admin template leftovers (`app/(dashboard)`, the numbered auth pages, template `features/*`)
  and build Cmd+K search from the current mode's sidebar.

### 2.4 Guard (`scripts/check-design-tokens.mjs`, `pnpm check:tokens`, pre-push)
- **Forbid** `shadow-brutal-*` and `border-2` on `Card`; keep forbidding Tailwind's `shadow-sm…2xl`.
- Raw palette classes are banned in `features/student` and `features/landing` as well as the existing paths.
- Keep the raw-hex, icon-import, `/admin` link and `backdrop-blur` guards.

### 2.5 Icons
`lib/icons.tsx` default weight `bold` → `regular`; Fill for active states. Points use the Merit coin, never an icon.

### 2.5a Patchworks
- `tile` renders as `<img>` with `alt` = the node title.
- `wash` is an absolutely positioned `<span>` (top-right, `aria-hidden`) with the SVG as a CSS `mask` over
  `washInk.light|dark` at opacity 0.26 / 0.16 (see `.pwwash` in `merit-ds.css`).
- `mono` is a CSS mask over `currentColor`.
- Placement follows Flutter §1.4a. Admin tables use `mono` only, 20px, in name cells (SKILL §9b).

### 2.6 Landing (`app/(landing)`, `features/landing`)
- Sections: nav, **Quilt Map hero** (D27), programme grid (Paper / Mastery / Adaptive), pricing (Wanderer vs
  Achiever, 14-day trial, buy in the app), FAQ, CTA band, footer. Port `landing.css` to Tailwind + tokens.
- Stays trilingual (`?lang=en|si|ta`); SI/TA typography rules from SKILL §3 apply.
- **Quilt Map** (`features/landing/quilt-map/`): data from backend `GET /public/explore` (streams → subjects →
  topics with counts, exam share and patchworks), fetched on the server and revalidated hourly. A pure polar
  layout (`layout.ts`, unit tested) places subjects on ring 1, the selected subject's topics on an arc at ring 2
  and subtopic beads at ring 3. Connectors are an SVG layer of dotted paths (`decor.connector`); nodes are HTML
  buttons with patchwork images. The camera is a CSS transform animated with `motion`. An idle coin tour runs
  until the first interaction and pauses offscreen. Keyboard: arrows move, Enter expands, Esc goes back; a
  "Skip map" link; reduced motion renders the static end state; phones get a vertical learning path. A topic
  leads to `/student/sign-up?subject=<id>`.

### 2.6a Student portal (`app/student`, `features/student`)
Mirrors the app's v3 decisions using the same APIs:
- **Shell:** sidebar Today · Learn · Compete · Me; bottom tab bar below 768px; coin and streak header chips.
- **Today** (`/today/plan`, exam countdown, your subjects rule, cards due) · **Learn** (enrolled subjects quilt,
  add subject) · **Subject hub** (`?tab=learn|practise|stats`; Stats with prediction, insights, exam insights and
  peers, Achiever-locked) · subtopic panel (Read → Remember → Prove) · notes reader · cards (FSRS, retention from
  the study plan) · quiz focus layout, results (points card + inline review) and review · **Compete** (podium
  preview, week bars, streak dots, achievements, tasks; leaderboard, points, achievements, tasks pages) ·
  **Me** (D23 sections, avatar picker) · **Premium** (plans and trial; buying happens in the app) · web onboarding
  (5 steps, `?subject=` preselect, D22 mobile field).
- Error codes: `PREMIUM_REQUIRED` → paywall, `DAILY_LIMIT_REACHED` → limit sheet.

### 2.7 Verify
- `pnpm lint && pnpm build && pnpm check:tokens && pnpm test`, plus `pnpm check:drift`.
- Browser pass: landing (mouse, keyboard only, reduced motion, 390px, EN/SI/TA, light/dark), the student
  flows end to end, and every admin page in compact density, light and dark.

---

## 3. Backend templ landing: retired (2026-10-21)

The Next.js `(landing)` route in `merit-project-frontend` is canonical (it already has the landing, privacy
policy and terms pages). The backend templ landing (`internal/web/`, `web/static/`, the templ build step) is
removed on `feat/patchworks`; `meritproject.lk` and `www` point at the frontend in the same deploy. Build the v3
landing in §2.6 only.

---

## 3a. Backend: `hierarchy_patchworks` (`merit-project-backend`, branch `feat/patchworks`)
- **Migration:** the `hierarchy_patchworks` table:
  - `node_type` is one of `subject`, `topic`, `subtopic` or `quest`;
  - plus `node_id`, `signature` (unique), `icon_id`, `engine_version`, `variants` JSONB and timestamps;
  - `UNIQUE(node_type, node_id)`.
- **Import:** `make patchworks-import MANIFEST=../merit-content/patchworks/manifest.json` upserts
  every node. Subjects resolve by `code`; topics and subtopics resolve by UUID.
- **API:** hierarchy, subject and topic responses add
  `patchwork: {signature, version, urls{tile,mono[,wash]}, washInk?}`. The URLs are built from
  `CONTENT_CDN_BASE` + the variant path.
- **Upload + go live:** a manual content release, not part of any deploy. Follow merit-content
  `docs/PATCHWORKS-RELEASE.md`: `tools/publish_patchworks.py push` uploads `out/` and `avatars/` to
  `s3://merit-project-static-prod/content-assets/patchworks/`, then `./patchworksimport` runs inside
  the backend container. `CONTENT_CDN_BASE` (GitHub variable, environment `production`) =
  `https://merit-project-static-prod.s3.ap-southeast-1.amazonaws.com/content-assets`; empty = off.
  Migrations (`000047`, `000048`; renumbered 2026-10-21) apply automatically when the server starts.

## 4. Out of scope
- `merit-project-admin` (legacy, folded into the frontend).
- Push and email templates. Do them in a follow-up and reuse the tokens and the wordmark lockups.
