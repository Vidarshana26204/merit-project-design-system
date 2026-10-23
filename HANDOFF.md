# Handoff — 2026-10-24

Design system **v3.7.0** (branch `feat/design-system-v3`). The pre-release plan is
`~/.claude/plans/as-per-the-handoff-md-zippy-seal.md`; it has a status table at the top. Read it first.

## Resume point

**Done in this session (2026-10-23 → 24):**
- Gate 0 owner decisions, the security and licence cleanup, and DS 3.7.0 (Step 1).
- Step 2 boards: round 14 Phase A and round 15.
- The round 15 board notes, the a11y audit, Flutter on 3.7 and the new Merit Points coin (D1).

**Waiting on the owner:**
- All picks are made (web results = A Scoreboard, 2026-10-24). Next is Step 3, the production build, with parallel Sonnet agents per repo; the main session orchestrates.

**Nothing is pushed** (unpushed commits: DS 41, Flutter 82, backend 14, merit-content 1, frontend 2).
Flutter CI's token-drift check fetches DS `c7ef050` (`.design-tokens-ref`), so push DS before or with Flutter.

## Boards (shared, picks in the artifact DB)

| Board | Artifact | Build |
|---|---|---|
| Mobile | https://claude.ai/artifact/Q6jsry2mnuUfD9csb1LB4X | `python3 wireframes/r15_mobile.py --splice` (round 15 + coin screens) |
| Web | https://claude.ai/artifact/BSrqtke1qqxxvU1WzzpqSh | `python3 wireframes/gen_web_board.py > wireframes-web.html` |

- Sources, file maps and republish notes are in `wireframes/BOARDS.md`. Both boards are linked from the reference-site sidebar.
- Picks and notes live in each artifact's `picks` collection: read them with `ArtifactData list`. Decisions copied out of
  them go into `wireframes/DECISIONS.md`.
- Republish with the same file path from this repo, passing only changed files. The artifacts are private.
- The older artifacts (web `6SeHPm…` at round 13, mobile `FqXHCE…` at round 10) belong to another claude.ai account.

## Decisions and picks (all rounds, as of 2026-10-24)

Sources:
- the boards' `picks` DB, read 2026-10-24;
- `wireframes/DECISIONS.md` (rounds 8–15, Gate 0);
- `DECISIONS-v3.md` (D0–D27, D21 rev 1).

### Mobile board picks (all built in Flutter unless noted)
| Screen | Pick | Option |
|---|---|---|
| Bottom navigation (`nav`) | B | Four tabs (Today · Learn · Compete · Me), subject hub |
| Home (`home`) | B | Today plan |
| Practise tab (`quiz-mode`) | A | Sectioned list |
| Taking a quiz (`quiz-take`) | A | Classic · paper mode |
| Attempt review (`quiz-review`) | A | Filtered list |
| Results (`r10-results`) | A | Calm card, full breakdown, inline review |
| Cards tab (`cards-home`) | A | Due hero |
| Card review session (`cards-session`) | A | Flip + four buttons, **shown as a visible stack** (note; built `432d93b`) |
| Learn: subject quilt (`learn`) | A | Topic map + inline subtopics |
| Subtopic (`subtopic`) | A | Bottom sheet over the quilt |
| Learn root (`subjects-list`) | A | Rows |
| Stats (`stats`) | B | Insights first |
| Compete root (`r10-compete`) | A | Rank ladder + week, with B's podium preview |
| Leaderboard (`leaderboard`) | A | Podium + sticky you |
| Points (`points`) | A | Summary + history |
| Achievements (`achievements`) | B | Tiered shelf |
| Paywall (`paywall`) | A | Band + plans (was C) |
| Mobile number (`r10-mobile`) | B | Block any first digit but 7 (`+94 7…`, D22) |
| Me (`r10-me`) | — | Round 10 approved (settings inline on Me, D23) |
| Points coin (`r16-coin`) | D → **D1** | Flat gold, brand-colour facets (shipped `b012184` / Flutter `89b53c7`) |

**Round 15 mobile notes:**
- `r15-maint`: one update sheet; Later shows only when skippable.
- `r15-onb`: O/L is blocked in this release.
- `r15-verify`: email verification is kept on the board, not in this release.

### Web board picks
| Screen | Pick | Option |
|---|---|---|
| Landing Quilt Map | A | Icosphere tree on a hill (round 12) |
| Landing hero | A + M | Copy left, icosphere tree behind/right; phone web has no tree |
| Landing sections | — | Rounds 13–14 live sections (try a question, flashcards, Mastery Engine, Merit Points, exam insights, pricing, FAQ) |
| Shell + Today (`web-shell`) | A | Sidebar + rail (navigation B on the web) |
| Subject hub (`web-hub`) | A | Tinted hero, topic quilt, docked side panel; tab double-underline fixed (note) |
| Compete (`web-compete`) | — | Approved; podium card balanced with the right column (note) |
| Quiz results (`web-results`) | **A** | Scoreboard: grade medallion, "You proved …" headline, 4 stat tiles (accuracy, time, streak, rank move), clickable question strip, points receipt, 3 next steps (replaces the round 10 web results) |

### Owner decisions
- **Gate 0 (2026-10-23):**
  - Rs 599/mo and Rs 4,990/yr, with a 14-day trial;
  - Sri Lanka midnight;
  - the plan "done" threshold is set in admin and applies the next day;
  - the prediction is hidden below 30% coverage;
  - badges retroactive, points not;
  - reminders hidden in v1;
  - v1 patchworks: Phy/Chem/Bio plus Agri and ICT, with the audit-UI icon pass;
  - the web language switch is on the subject page only.
- **2026-10-24:**
  - Pro A/L cap 5, the same as free;
  - CVD subject collisions left as is;
  - repo links only for the DS artifact;
  - coin D1.
- **Release scope:** no email verification, no push, no O/L.
- **Security:** no history scrub for now; the root dumps stay where they are (owner).
- **Earlier DS rulings still in force:**
  - D18 mastery fill;
  - D19 colour-only timer;
  - D20 subject tint 0.30 / 0.24;
  - D21 one coin family (rev 1 = D1);
  - D22 `+94 7`;
  - D23 Me absorbs Settings;
  - D24 14-day trial;
  - D25 username-only share card;
  - D26 Merit default web preset;
  - D27 Quilt Map landing.

## What changed (2026-10-23 → 24)

**Gate 0 decisions** (`wireframes/DECISIONS.md`):
- Achiever costs Rs 599/mo or Rs 4,990/yr (save 31%), with a 14-day trial.
- The day boundary is Sri Lanka midnight for caps, streaks and the plan.
- The daily-plan "done" threshold lives in `system_settings`, is edited in admin, and applies from the next day.
- The grade prediction is hidden below 30% topic coverage.
- Badges are awarded retroactively; their points are not.
- Push reminders are hidden for v1.
- v1 patchworks cover Phy/Chem/Bio plus Agri and ICT. After generation, mark nodes with no suitable icon in the audit
  UI, then generate icons for them.
- The web content-language switch sits on the subject page only.

**Owner answers (2026-10-24):**
- The Pro A/L subject cap stays **5**, the same as free; Achiever copy shows no subject count.
- The 6 colour-blind subject collisions are left as is.
- The DS artifact is links only: there is no published reference site.
- New points coin: picked **D1**.

**Release scope:**
- Email verification is not in this release (no backend); mobile verification comes first.
- O/L is blocked (no subject coverage).
- One update sheet, with "Later" shown only when the update can be skipped.

**Security / licences:**
- Untracked: Flutter `.env` and the old keystore (`da264b4`); backend `env/dev.env` and `env/test.env` (`c3211e5`; the
  `.example` files list the keys).
- Untracked here: Clash Display and School Times; Plus Jakarta now ships `OFL.txt` (`e47e66b`).
- **Not done (owner):** history scrub, rotating the dev `API_SECRET` and the old keystore if they were ever live, and
  moving the root DB dumps.

**DS 3.7.0** (`516f786..83d6ef0`):
- **Contrast gate:**
  - tiers text / large / ui; alpha compositing;
  - 222 checks, including focus on every surface;
  - `$exempt` documents the fills that always carry ink labels.
- **Fixes:**
  - `ink.500` #625F79;
  - `border.control` for the quiz idle edge;
  - `feedback.errorText`;
  - `focus.ringOnFeature` / `ringOnInverse`;
  - theme-following `chart.*` via `dataviz.cat*`.
- **New families:**
  - feedback and states: info, `warningSubtle`, `state.hover`/`pressed`, disabled colours;
  - surfaces: scrim, skeleton;
  - geometry and motion: focus-ring width and offset, `easing.enter`/`emphasized`, `duration.reduced`;
  - layout and charts: D7 density, data-viz seq/div ramps.
- **SI/TA:** `tokens/scripts.json` drives `:lang(si|ta)` in CSS and `MeritTypeScaleSet.of(lang)` in Dart. Noto woff2
  subsets are on the reference site; the KaTeX policy is in SKILL §3.
- **Reference site:**
  - §15 is the full state matrix;
  - §30 lists the flow specs.
- **`check:subjects`:** adds the dark rim and a CVD (deutan/protan) report. CI runs it on a fixture, plus the patchwork
  tests.
- **Housekeeping:** the deprecated timer-pill and `reward.points` tokens are removed by 2026-12-31; wash inks moved to
  primitives.

**Boards** (`9dc0b1f`, `e587303`, `c33cecc`):
- **Round 14 Phase A (web landing):**
  - Mastery Engine (`#mastery`) and Merit Points (`#points`) sections, live on the real `system_settings`/`tiers`
    snapshot (`build_samples.py` → `qm-samples.js`: `rules`, `plans`, `fsrs`).
  - Real FSRS intervals from the backend engine: a new card is 1 min / 6 min / 10 min / 16 days; the "Good" ladder is
    10 min → 4 d → 14 d → 45 d → 135 d.
- **Round 15 (§30 flows):**
  - mobile tab 10 (`r15_mobile.py`);
  - web Me account pages, email verification, the subject-header language switch, the prediction gate, and
    maintenance/404/error pages (`r15_web.py`).
- **Board notes applied:**
  - mobile: the update sheet, O/L, email;
  - web: the hub tab double underline, the Compete podium height, and a new `web-results` pick
    (A Scoreboard / B Quilt progress / C Recap).
- **a11y:** the `ux-ui-agent-skills:a11y-audit` real-render gates were run over every flow, light and dark.
  - Fixed failures in the store badges, toast actions, the API tag, error text on errorSubtle and fixed-tone badges.
  - Every interactive element passes in default/hover/focus.
  - Known gate limit: light-mode `color-mix()` tints can't be resolved (dark passes, and `check:subjects` covers
    them).

**Points coin** (`29a2f3a..b012184`):
- `scripts/brand/coin_concepts.py` builds concepts A–D, D1 and D2 from tokens (`assets/v3/brand/coin-concepts/`).
- `--final` writes the shipped family: `merit-coin{,-small,-dark,-small-dark}.svg` and the glyphs.
  - D1 is a flat gold disc with a deeper-gold rim, plus the Merit mark seen from above: four facets in the mark's
    colours with white gaps.
  - New **small-dark** cut.
- `build_v3_brand.py` no longer rebuilds the coin. D21 rev 1 is in `DECISIONS-v3.md`.

**Flutter** (`feat/design-system-v3`):
- `633bbdf`: vendored 3.7 tokens.
  - `MeritButton` disabled uses the disabled colours.
  - Error text uses `feedbackErrorText`.
  - Goldens regenerated.
- `432d93b`: the card session is a visible stack (the board note).
- `89b53c7`: the D1 coin with a small-dark cut in `MeritCoin`.
- Analyze is clean, all 219 tests pass, and `check_design_tokens` reports no violations.

## Step 3 scope (revised; details in the plan file)

**Backend:**
- `/public/plans` with `tiers.display_price_lkr` / `is_public` / order;
- `/public/samples`;
- `RateLimitByIPWindow` with a janitor, plus eviction on the old limiter; `/public/subjects` and `/public/explore` rate
  limits;
- the Sri Lanka day boundary;
- the plan threshold setting;
- `coverage_pct` and the 30% gate;
- retro badges without points;
- quick API gaps:
  - `avatar_id`, change-password, reset returns tokens;
  - per-day streak, weekly points, subtopic name in the session;
  - rank movement;
- B1 (content mirror) and B2 (`contentbackfill` in the Dockerfile).

**Frontend:**
- rebase onto v3 foundations (`feat/design-system-v3` `bda6f65`); v3 nav;
- the portal from the web picks;
- the landing with the round 14 sections on shared `components/merit/study/`;
- the subject-header language switch;
- account pages; maintenance/404/error pages; SEO and error files; dynamic `lang`;
- remove template routes and unused fonts;
- a React patchwork;
- F1 (deploy workflow) and F2 (HEALTHCHECK).

**Flutter:**
- v3 sheet styling for `update_dialog.dart`;
- hide the reminder row; the prediction gate;
- a11y: IconButton tooltips, text scale 2.0, reduced motion in transitions, required patchwork labels;
- the 4 swallowed errors;
- toggle/rating disabled colours;
- `MeritTypeScaleSet` for SI/TA content;
- token baselines to 0.

**Content:** Agri and ICT icon maps, then the audit UI pass and icons for the marked nodes.

**Not this release:** email verification, push, O/L.

## Facts worth keeping

`merit_rehearsal` holds the most recent data; read it with SELECTs only.

`system_settings`:
- free limits: mastery 50 and papers 2 a day;
- enrolment caps: A/L free 5 and Pro 5; O/L free 6 and Pro 10;
- points:
  - correct answer 10; accuracy bonus +20 at 80%; Pro ×1.5;
  - flashcard session +15 (cap 100 a day); note +25; unlock reward 50;
  - force-unlock 100 + 25 each, 20% burned;
- mastery weights: quiz .75 / notes .15 / cards .10; completion at 50;
- FSRS retention 0.9.

Other facts:
- `tiers` has no prices yet.
- Prices are decided (Gate 0) and live in `qm-samples.js` `plans` until Phase B.
- FSRS uses Flutter-parity weights in `service.newFsrsEngine`.

## Where things stand

| Repo | Branch | State |
|---|---|---|
| `merit-project-design-system` (public) | `feat/design-system-v3` @ `b012184` | v3.7.0 tokens + gate, reference site §15/§30, boards rounds 14–15 + coin, D1 coin family. 41 ahead, not pushed |
| `merit-project-flutter` | `feat/design-system-v3` @ `89b53c7` | All v3 screens; tokens 3.7; card stack; D1 coin. 219 tests. 82 ahead, not pushed |
| `merit-project-frontend` | `dev` @ `609a30b` (v3 foundations on `feat/design-system-v3` `bda6f65`) | Still v2 on `dev`; Step 3 rebuilds portal + landing. Not pushed |
| `merit-project-backend` | `feat/patchworks` @ `c3211e5` | Patchworks + explore + all earlier wireframe gaps; env files untracked. 14 ahead, not pushed |
| `merit-content` (private) | `feat/patchworks` @ `ed429a8d` | Phy/Chem/Bio patchworks; Agri/ICT icon maps still to do |

None of the branches is merged. Backend changes deploy only once `feat/patchworks` lands on `main` (24 one-way
migrations 000034–000057; snapshot first).

---

## History (older handoffs, kept for context)

**Patchworks in one paragraph.** Every Subject, Topic and Subtopic has a generated tile: a
square-in-a-square quilt block. A subject's 4 patches gain a nested diamond at topic level (5)
and a square at subtopic level (6). The icon plate has as many sides as the tile has patches
(square, pentagon, hexagon). All colours derive from the subject's `color_hex`. Variants are
`tile`, `wash` (behind flashcards and notes) and `mono`. Rules: `SKILL.md` §12. Decisions:
`DECISIONS-v3.md` D16 revs 1–5. Specimens: reference site §21.

## Mobile wireframing (decided)

- **Board:** `wireframes.html` (linked from the reference site §28), using `wireframes/{wf.css, wf.js, icons.js}`. It is
  published as a private claude.ai artifact with a shared pick tracker (`picks/<screen>`). 10 flows at 360dp, 3 candidates
  per screen, plus revised rows for rounds 8–9 (Compete root, Tasks & Quests, onboarding with language rows).
- **Decisions:** `wireframes/DECISIONS.md`. Navigation B (Today · Learn · Compete · Me), the subject hub with a tinted hero and
  type-scale sections, Learn as a patchwork quilt map with a subtopic sheet (recipe ring plus Read → Remember → Prove),
  and `MeritShareCard` for quiz results. Only subject content is localized; the UI stays English.
- **DS rulings (3.5.0):**
  - **D18:** patchwork mastery fill, the one allowed tile alteration.
  - **D19:** colour-only timer (`timer.text / warnText / criticalText`; the pill tokens are deprecated).
  - **D20:** subject tint 0.30 light / 0.24 dark, gated for all 62 subjects with `npm run check:subjects -- <subject-colors.json>`.
    The board's 58% mix failed on real mid-tone subject colours.

## Backend for the picked screens (`feat/patchworks`)

Status per feature: `wireframes/BACKEND-GAPS.md`.

**Migrations.** The patchwork migrations were renumbered to 000047–000048, because revenuecat-sandbox owns 000046.
New migrations 000049–000052 add achievements, avatars, daily plans and push/reminders. Local databases that ran the old
patchwork numbers need `migrate force 46` before migrating up.

**Error codes.** Error responses carry a top-level `code` the app branches on:
`DAILY_LIMIT_REACHED` opens the limit sheet, `PREMIUM_REQUIRED` opens the paywall. The others are `NOT_ENROLLED`,
`ENROLLMENT_LIMIT_REACHED`, `SUBTOPIC_LOCKED` and `INSUFFICIENT_POINTS`.

**New endpoints:**
- **Achievements:** `GET /students/me/achievements`. Quiz completion also returns `achievements_unlocked`.
- **Tasks:** `GET /tasks?state=pending|completed|expired|all`.
- **Avatars:** `GET /avatars`, and `PUT /user {"user": {"avatar_id"}}` to pick one.
- **Subtopic progress:** `GET /progress/subtopics/:id` returns `mastery_parts` (read / remember / prove). Default weights are
  notes 0.15, cards 0.10, quiz 0.75, so the ring must read them from the API.
- **Stats:** `GET /subjects/:id/prediction` and `GET /subjects/:id/insights`.
- **Today:** `GET /today/plan` (up to 3 items; 30 points once when all are done).
- **Notifications:** `POST|DELETE /devices`, `GET|PUT /students/me/reminders`, `POST /quests/notify-me`, and
  `cron send-reminders` every 15 minutes.
- **Enrollments:** both the create and the language update reject languages missing from `available_languages`.

**Removed:**
- The templ landing (`internal/web`, `web/static`, the templ build steps and dependency).
- 35 unreachable functions, 85 unused queries and 10 dead environment bindings.
- Swagger regenerates again.

**Verified:**
- Unit tests pass.
- Migrations ran up, down and up on a copy of the local database.
- Every new endpoint was called against a running server with a real student.

## Before the backend release

- **Root domain cutover:** deploy `merit-project-frontend` (port 3001) and point `meritproject.lk` and `www` at it in the
  same release (nginx block in the monorepo `Deployment.md`). Otherwise the root domain, `/privacy-policy` and
  `/terms-and-conditions` return 404. The frontend has no deploy workflow yet.
- **Push:** hidden for v1 (Gate 0), so skip this for now. For v1.1: create a Firebase project, mount a service-account
  JSON, set `FCM_PROJECT_ID` and `FCM_CREDENTIALS_FILE`, and add the cron line (`docs/cron-setup-guide.md`).
- **Patchworks go-live (manual):** merit-content `docs/PATCHWORKS-RELEASE.md`. One-time setup: public read on
  `content-assets/patchworks/*`, an upload key, and the GitHub variable `CONTENT_CDN_BASE`. Then push and run the importer
  with `--avatars`.

## Open decisions

All settled by Gate 0 (2026-10-23, `wireframes/DECISIONS.md`):
- plan "done" is an admin threshold that applies from the next day;
- prices are Rs 599 / Rs 4,990;
- the day boundary is Sri Lanka midnight;
- the prediction is hidden below 30% coverage;
- badges are retroactive, their points are not.

The share card was settled by D25.

## Open items carried over

- **Agricultural Science and ICT** have colours but no icon maps yet. Gate 0 puts them in v1: build the maps, mark
  nodes with no fitting icon in the audit UI, then generate icons for them.
- **Feature icons** (flashcards, notes, quiz modes…) are deferred; the app uses Phosphor.
  The groundwork is `patchwork_jev.py --features`.
- **Jev icon audit:** 45 flagged and 61 weak remain (optional polish). Picker:
  `tools/run.sh tools/patchwork_review.py serve` in merit-content.
- **Clash Display licence:** untracked on 2026-10-23 (`e47e66b`). The files remain in history; the owner chose not to
  scrub it for now.
- **Quests and structured questions** have no backend yet. Quests ships as a coming-soon tab.

## Flutter v3 (done)

Status, commit ranges and known gaps: `merit-project-flutter/docs/V3-PROGRESS.md`.

- **Batches 1–3** (merge heads `6525ec2`, `518a98a`, `7fbe293`): shell, Compete, Today, hub, Learn, quiz + results +
  review, study + notes, Points, Leaderboard, paywall + limit sheet, Me, avatar picker, auth, onboarding (5 steps).
  Trial is 14 days (user ruling, overrides the wireframes' 21).
- **Round 10** (device test 2026-10-22; merged into `wireframes.html`, picks in `wireframes/DECISIONS.md`; merges `355af91`,
  `6439bf3`): Learn int→double crash (`c7f94c5`), calm points card + inline "Review N mistakes", one `MeritCoin` asset,
  `+94 7…` mobile field, Settings folded into Me, Today subjects 1–2 rows / 3–4 tiles, Compete with podium preview,
  week bars, streak dots and achievements shelf.
- **Backend gaps found** (not built): change-password endpoint, `avatar_id` in the user payload, @handle, per-day
  activity (streak dots are inferred), weekly points total (sums newest 300 rows), rank gap beyond the top 50, rank
  movement, earned-points context on `DAILY_LIMIT_REACHED`, O/L in onboarding, District/School as lookups.
- **Left:** iOS simulator pass; push `feat/design-system-v3` when the release is ready.

## Next: web frontend (`merit-project-frontend`)

One Next.js 16 app, one origin: landing `/`, `/admin`, `/student`, `/contributor` (`lib/mode.ts`, `proxy.ts`). Admin
moved here from the retired `merit-project-admin`. Branch per MIGRATION §2: `feat/design-system-v3` from local `dev`.

**Progress (2026-10-22, plan approved):**
- **DS docs 3.6** (`d52f36d`): D21–D27 (one Merit coin, `+94 7` field, Me absorbs Settings, 14-day trial,
  username-only share card, Merit default web preset, Quilt Map landing). Tokens unchanged at 3.5.0. MIGRATION §2
  rewritten for this track.
- **Mobile board** (`wireframes.html`, artifact FqXHCEqumFTA2WNjKecHe2): round 10 merged, mobile only.
- **Web board** (`wireframes-web.html`, artifact https://claude.ai/artifact/6SeHPm6JhVrNV2ctgzhajn): tabs mirror the
  mobile board plus Landing. Landing opens with **live Quilt Map prototypes** (fractal tree `qm-tree.js`, circuit
  network and orbit in `qm.js`, data `qm-data.js` = trimmed `/public/explore` snapshot), then hero composition,
  phone statics and sections. Built by `python3 wireframes/gen_web_board.py > wireframes-web.html` (frames in
  `gen_web.py`, CSS in `wf-web.css`). **Waiting on picks.**
- **Backend** `GET /public/explore` merged into `feat/patchworks` (`c9725df`, `e46ba35`): streams → subjects →
  topics (counts, `exam_share_pct`, patchwork) → subtopic titles; in-process 1h cache. `/public/subjects` gains
  `patchwork`.
- **Frontend foundations** on `feat/design-system-v3` (`0e50b09..bda6f65`): v3 tokens + shadcn remap, Merit
  preset (default, `merit-color-theme`), next-themes on landing, General Sans, `shadow-elev` codemod, borderless
  `components/ui`, regular icons, `components/merit/*`, React Query, template cleanup, guard + drift + vitest.
  The landing itself is still v2 (remapped colours) until its rebuild; brand marks in `public/brand` are still v2.

**Next:** after picks, in fresh worktrees from frontend `feat/design-system-v3` (`bda6f65`):
1. **Agent L:** landing rebuild + the picked Quilt Map in `features/landing/quilt-map/`. Port the layout maths from
   `wireframes/qm.js` / `qm-tree.js` as pure tested functions; React + SVG + `motion`; data from
   `/public/explore` (server fetch, revalidate 1h); static SVG under 640px; reduced motion = instant.
2. **Agent S:** student portal per the board (routes and APIs in `MIGRATION-v3.md` §2.6a).
3. Then the admin look-over (palette classes → tokens, compact density, light/dark pass in Chrome).

**State to know:**
- Branches (all local, unpushed):
  - DS `feat/design-system-v3` `eb7caa6`;
  - backend `feat/patchworks` `e46ba35` (explore merged; `feat/web-explore` can be deleted);
  - frontend `feat/design-system-v3` `bda6f65` (`dev` stays `609a30b`);
  - Flutter `feat/design-system-v3` `be0a11b`.
  - Temporary worktrees are removed.
- Local stack:
  - API: `cd merit-project-backend && go run ./cmd/api` (:8085, DB `meritproject` at migration 57);
  - frontend: `pnpm dev` (:3001);
  - boards: `python3 -m http.server` in the DS dir, then `/wireframes.html` and `/wireframes-web.html`.
- Board sources:
  - mobile `wireframes.html` (+ `wf.css`);
  - web `python3 wireframes/gen_web_board.py > wireframes-web.html` (+ `wf-web.css`, `qm*.js`). Refresh
    `qm-data.js` from `/public/explore` if the syllabus changes.
- Republish:
  - web board with the same file path and the files map (assets, `wireframes/*`, `build/css/merit-tokens.css`);
  - mobile board to FqXHCEqumFTA2WNjKecHe2.
- **Frontend foundations still to do:**
  - `public/brand` marks are still v2;
  - a non-Merit preset flashes on load;
  - landing is still v2 markup until the rebuild.

**Open decisions for this track:**
- Resolved: `components/ui` may be edited (tweakcn picker kept, Merit default); web gets a wireframe round;
  contributor portal is out of this pass; web premium sells but purchase happens in the app; landing stays EN/SI/TA.
- Prices (Rs 4,990/yr and Rs 599/mo?) for the landing and the student premium page.

## How to work here

- `npm run build && npm run check` (tokens + contrast gate) before committing. After a token or subject-colour change,
  also run `npm run check:subjects -- ../merit-content/subjects/_subject-colors.json`.
- Patchwork engine: `scripts/patchwork/`; run its tests with `python -m pytest -q scripts/patchwork` (needs fonttools).
- The licensed icon pack and production patchworks never enter this public repo, only the Phosphor demo set
  (`assets/v3/patchwork-demo/`).

## Detour: core prerequisites (2026-10-21)

The Flutter reskin is paused to build learning-model prerequisites the screens depend on. Branch `feat/exam-intelligence`
in the backend (from `feat/patchworks`), Flutter (from `feat/design-system-v3`) and `merit-project-frontend` (admin; `merit-project-admin` is retired). Not pushed.

- **Past-paper analysis:** per topic/subtopic question distribution over official papers (all years, small floor for
  never-asked subtopics). Drives exam-weighted topic and subject mastery and the grade prediction.
- **Exam clock + recommendations:** exam months are settings (A/L August, O/L December; date = 1st of the month in
  `students.exam_year`). Everyone gets an exam-paced Today plan; Achiever gets the full engine and forecast.
- **Retention decay:** Remember = average FSRS retrievability normalized to desired retention, recomputed daily; below
  0.80 a note is flagged Revise and Read counts half. Paper and adaptive attempts now update mastery.
- **Peers:** percentile and weekly pace against subject + level + exam-year cohort, hidden under 20 students.
- **Insights:** high-yield gaps, trending topics, memory on exam day, paper pacing. All new Stats features are Achiever-only
  with locked teasers for free users.
- **Phases:** 0 foundations, 1 exam weights, 2 retention, 3 peers, 4 recommendations, 5 insights. Two agents in parallel
  (backend; clients + docs).
- **Status:** docs done; Flutter Phase 0 client fixes and Phase 1 past-paper analysis card built against the agreed JSON
  contract; admin settings fields and exam-weights page built. Later phases pending.
- **Checkpoint 3 (audit fixes):** Flutter analysis model realigned to the backend JSON (`by_year` list, `trend_slope_pp_per_year`,
  `has_data`, `weighted`, `min_papers`); hub header uses the weighted `mastery_percentage`; desired retention stays a fixed
  0.9 (superseded in checkpoint 6). Admin exam-weights page rebuilt in `merit-project-frontend` with grouped topic/subtopic rows, recompute toasts,
  plain-average badge and duplicate-paper warning.
- **Rulings:** duplicate papers get an admin warning only; thin data uses setting `exam_weight_min_papers` (default 8) and
  the plain-average roll-up below it; locked subtopics accrue and stay locked; admin moved to `merit-project-frontend`.
- **Contracts:** past-paper analysis, admin exam-weights and recompute are built; revise fields, peers and the
  duplicate/min-papers additions land with backend Phases 2-3; study plan and insights (Phases 4-5) pending. Full table:
  `merit-project-flutter/docs/V3-PROGRESS.md`.
- **Checkpoint 4:** Phase 4 Flutter client built (study-plan model, Stats forecast card, Practise "Recommended for you",
  Today exam countdown chip, questions/cards progress text). Phase 5 pending.
- **Checkpoint 5:** Phase 5 Flutter client built (high-yield, memory on exam day and paper pacing Stats cards from one
  `exam-insights` fetch; teaser copy updated). All detour phases have clients; end-to-end pass next.
- **Merged (2026-10-21):** each `feat/exam-intelligence` fast-forwarded into its base (backend `feat/patchworks`,
  Flutter `feat/design-system-v3`, frontend `dev`). Local only.
- **Checkpoint 6 (end-to-end + fixes):** all phases verified end to end on a scratch DB copy (migrations 44→57, crons,
  Pro gating, real responses parse in Flutter, Revise round trip, peers, admin). Two fixes from it: far from the exam the
  first recommendation slot (study-plan question set and Today quiz) goes to the best unlocked subtopic (backend
  `97717fb`); the retention target follows setting `flashcard_request_retention` instead of a fixed 0.9 (backend
  `62e8e67`, exposed as `study_plan.desired_retention`, used by Flutter FSRS in `05a3cc5`). Run `recompute-retention`
  after changing that setting. Remaining: iOS simulator pass of Stats (Pro, Wanderer) and Today; deployment blockers in
  root `Deployment.md` §13 are deferred until feature work is done.
