# v3 feature inventory

Maps every product surface to the v3 components it needs. Sources: Flutter `lib/features/*`
(branch `feat/design-tokens-v2`), frontend `app/{student,admin,contributor,(landing)}`, backend templ
landing, v2 catalogue (IMPROVEMENT-PLAN §5).

Legend — **R** reuse spec, recolour only · **S** restyle (shape/depth change) · **N** new in v3.

## 1. Surfaces → components

| Surface (Flutter screen / web route) | Mode (C2) | Components |
|---|---|---|
| Onboarding, splash (`onboarding`) | energy | Patchwork hero tile **N**, eyebrow+underline header **N**, pill CTA **S**, page dots **S** |
| Auth: sign-in, register, OTP (`authentication`, web `sign-in/up`) | calm | Input + phone (+94) **S**, OTP boxes **S**, pill CTA **S**, language switcher **R** |
| Home (`home`) | energy | Gamer header (streak + coins chips) **S**, quest card **S**, continue-learning card **N** (patchwork thumb), study stats card **S**, sparkle decor **N** |
| Subjects / subject detail (`subjects`, web `student/subjects`) | energy | Subject patchwork tile **N**, chip filter row **N**, progress ring **S**, enrol CTA |
| Hierarchy navigator / tree (`hierarchy`) | energy | **Learning path map N** — connected tiles + dotted connectors (replaces plain tree), subtopic progress pill **S** |
| Study / flashcards (`study`, `cards`, web `student/flashcards`) | calm→energy | Flashcard flip **S** (category patch tint, no border), FSRS rating buttons **S**, deck card **S** |
| Notes reader (web `student/notes`; Flutter via study) | calm | Reading surface **N** spec (C1), callout blocks **S**, LaTeX plate **N**, TOC chip row |
| Quiz mode select (`quiz_mode_selection`) | energy | Mode cards (Paper / Mastery / Adaptive) **S**, Pro lock badge **S** |
| Quiz taking (`quiz_taking`, web `student/quiz`) | **calm** | Question card **S**, answer option (idle/selected/correct/wrong/revealed) **S**, timer **S**, progress stepper **S**, flag/bookmark icon buttons **R** |
| Quiz completion (`quiz_completion`) | celebration | Grade seal **S**, points breakdown (+10/q, +20 accuracy, ×1.5 Pro) **S**, accuracy ring **S**, review-mistakes CTA, sparkle burst **N** |
| Attempt detail (`quiz_attempt_detail`) | calm | Option states (read-only) **R**, explanation callout **S** |
| Leaderboard (`leaderboards`) | energy | Podium **N**, leaderboard row **S**, sticky "You" row **R**, tab/segment **S** |
| Points / history (`points`) | energy | History entry tile **S**, coin chip **S** |
| Analytics / streak / subject report (`analytics`, web `student/analytics`) | energy | Streak heatmap **S** (orange ramp), charts **S** (new categorical set), grade bars |
| Premium / paywall (`premium`, web `student/premium`) | energy | Achiever violet band + orange cap **N**, tier compare card **S**, quota meter **S** (replaces `Color(0x…)` gradient in `premium_screen.dart`) |
| Profile, settings, appearance, languages (`profile`) | calm | Settings item **R**, avatar with ring **S**, toggle **S**, segmented tabs **R** |
| Bottom nav shell (`main`) | — | Tab bar **S** (flat, active = violet pill + Fill icon) |
| Empty / error / offline / 404 | — | Patchwork spot illustration **N** + one line + one CTA |
| Snackbar/toast, dialog, bottom sheet | — | **S** (elevation e2/e3, no hard border) |
| Skeleton / shimmer | — | **S** (`surface.sunken` blocks, no border) |
| Admin & contributor (web `admin/*`, `contributor/*`) | compact | Data table **S**, page header **R** (§9b), sidebar **S**, forms **S**, editors (question/note/paper/flashcard) **S**, status badges **S** |
| Landing (backend templ + web `(landing)`) | energy | Hero (eyebrow + underlined headline + pill search + patchwork cluster) **N**, programme grid **N**, pricing **S**, testimonials **S**, CTA band **N**, footer **S** |

## 2. Component catalogue v3 (deduplicated)

| Component | v2 widget / web | Status | v3 key change |
|---|---|---|---|
| Button (primary/secondary/accent/ghost/link/dark) | `MeritButton` / `Button` | S | Pill, no border, e1; primary = orange w/ ink label (D9) |
| Icon button | `MeritCircleButton` | S | Round, tint bg, Regular icon |
| Card (neutral/feature/reward/success) | `MeritContentCard`, `ShadowBox` / `Card` | S | No border, radius 24, e1; feature = violet band |
| Patchwork tile | — | **N** | Category tint + pattern id + ink outline + Phosphor Duotone glyph |
| Learning path map | hierarchy tree | **N** | Tiles + dotted connectors + node states (locked/current/done) |
| Section header (eyebrow + underline) | — | **N** | SI/TA: no uppercase eyebrow |
| Search pill | — | **N** | White pill, e1, round orange action |
| Chip / filter chip / pill / badge | `MeritPill`, `MeritBadge`, `MeritSubjectBadge` / `Badge` | S | Hairline ink outline on filter chips; selected = violet fill |
| Input / OTP / phone | `MeritTextFormField` / `Input` | S | Hairline border, radius md, focus = violet ring |
| Progress bar / ring / stepper | `MeritProgressBar/Ring`, `MeritStepper` | S | Track = sunken, fill = orange (energy) / violet (calm) |
| Toggle / checkbox / radio | `MeritToggle` | S | D5 kept: selection violet, completion sage |
| Segmented tabs / language switcher | `MeritSegmentedTabs` | R | Recolour |
| Bottom tab bar | `main_screen` | S | Flat bar, e2, active violet pill |
| Gamer header / streak chip / coin chip | `MeritGamerHeader` | S | Orange flame, butter coin |
| Quiz option | `MeritQuizOption` | S | States kept; letter chip; correct sage, wrong red-subtle, revealed dashed sage |
| Timer | — | S | Neutral → butter → red |
| Grade seal / result | `AnimatedGradeBadge` | S | Sparkle burst, grade ramp |
| Flashcard | `FlippableStudyCard` | S | Category patch tint, pattern corner |
| Leaderboard row / podium | `MeritLeaderboardRow` | S / **N** | Podium with avatar rings |
| Tier card / quota meter / Achiever band | `premium_screen` | S / **N** | Violet band + orange cap + butter seal |
| Dialog / sheet / toast | `MeritDialog`, `MeritSnackBar` / `Dialog`, `sonner` | S | Elevation, no border |
| Empty / error / offline | `MeritEmptyData`, `MeritError`, `OfflineContainer` | S | Patchwork spot art |
| Skeleton | `MeritShimmer` / `Skeleton` | S | Borderless |
| Data table (compact) | — / `DataTable` | S | Hairline rows, no patchwork |
| Chart | analytics / `chart-1..5` | S | New categorical set |
| Avatar | `MeritAvatar` | S | Coloured ring |

## 3. Migration hotspots (from usage scan)

- Flutter `lib/features/**`: `MeritColors.` ×541 (69 files) — remap aliases centrally; `MeritBorders` ×115 (49 files) — biggest visual change (borders mostly disappear); Material `Icons.` ×143 → Phosphor; `fontSize:` literals ×113; `Color(0x…)` ×3 in `premium/ui/premium_screen.dart`.
- Frontend: `shadow-brutal-*` in 49 files; `check-design-tokens.mjs` soft-shadow ban must invert; `components/ui/button.tsx`, `card.tsx` carry `border-2`.
- Backend templ landing: hand-copied colour vars in `internal/web/templates/layout.templ` → vendor `merit-tokens.css`.
