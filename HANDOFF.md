# Handoff — 2026-10-22

Design system **v3.5.0** (branch `feat/design-system-v3`). Patchworks, mobile wireframes, the exam-intelligence detour
and the **Flutter v3 reskin are all done** (batches 1–3 plus device-test round 10, merged locally).
**Next: `merit-project-frontend`: landing, admin and student portals on v3** (see "Next: web frontend" below).

## Where things stand

| Repo | Branch | State |
|---|---|---|
| `merit-project-design-system` (public) | `feat/design-system-v3` | v3.5.0: tokens, reference site, SKILL.md, patchwork engine v5, wireframe board, MIGRATION §1 rewritten to match the decisions |
| `merit-project-flutter` | `feat/design-system-v3` (from `origin/dev`); detour merged in (ff to `05a3cc5`); batches 2-3 merged; round 10 merged (head `be0a11b`) | All v3 screens done and device-tested on Android (round 10 fixes merged). Analyze clean, 219 tests, token guard 118/10/3. Details: `merit-project-flutter/docs/V3-PROGRESS.md`. **Committed, not pushed.** |
| `merit-project-frontend` (admin) | `dev` (local `609a30b`, 2 commits ahead of `origin/dev`) | Landing (`app/(landing)`), admin (`app/admin`), student (`app/student`) and contributor (`app/contributor`) on one origin. Admin has the exam-intelligence settings and Exam weights page. **Still on DS v2.1.0 tokens.** `merit-project-admin` is retired. Not pushed |
| `merit-content` (private) | `feat/patchworks` | Physics, Chemistry, Biology patchworks (296 nodes), icon maps, 62 subject colours, 30 avatars, release tooling (now imports avatars too) |
| `merit-project-backend` | `feat/patchworks` (rebased onto `feat/revenuecat-sandbox`, pushed; local now `9e16053` with the detour + batch 2 API additions, ahead of origin) | Patchworks API, templ landing removed, dead code cleared, all wireframe gaps built (below) |

None of the branches is merged. The backend changes only deploy once `feat/patchworks` lands on `main`.

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
- **Push:** create a Firebase project, mount a service-account JSON, and set `FCM_PROJECT_ID` and `FCM_CREDENTIALS_FILE`.
  Then add the cron line (`docs/cron-setup-guide.md`). Until then reminders are a no-op.
- **Patchworks go-live (manual):** merit-content `docs/PATCHWORKS-RELEASE.md`. One-time setup: public read on
  `content-assets/patchworks/*`, an upload key, and the GitHub variable `CONTENT_CDN_BASE`. Then push and run the importer
  with `--avatars`.

## Open decisions

- **Daily plan "done":** built as "every item done", which pays 30 points. Confirm it.
- **Prices:** Rs 4,990/yr and Rs 599/mo, or the "$4.99/mo" on the current Profile screen.
- **Share card privacy:** can username, school and district appear on shared images?
- **Day boundary:** streaks and the daily plan use the UTC day, so it rolls over at 05:30 Sri Lanka time. Decide whether to
  switch both to Sri Lanka midnight.
- **Grade prediction with little data:** it shows a low-confidence grade (often F) for new students. Consider hiding the
  grade below some coverage level.
- **Achievement points for existing students:** they get retroactive unlocks and points on their first evaluation.

## Open items carried over

- **Agricultural Science and ICT** have colours but no icon maps, so they have no patchworks yet. They use the
  §1.4a fallback.
- **Feature icons** (flashcards, notes, quiz modes…) are deferred; the app uses Phosphor.
  The groundwork is `patchwork_jev.py --features`.
- **Jev icon audit:** 45 flagged and 61 weak remain (optional polish). Picker:
  `tools/run.sh tools/patchwork_review.py serve` in merit-content.
- **Clash Display licence:** the v2 Clash Display (FFL) files are still committed here (public repo). Remove them and
  decide on history before v3 ships (`assets/fonts/README.md`).
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

**Next:** after picks, Agent L (landing + Quilt Map) and Agent S (student portal) in parallel worktrees from
`feat/design-system-v3`, then the admin look-over. Plan: `~/.claude/plans/takeover-form-handoff-md-plan-compiled-deer.md`.

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
