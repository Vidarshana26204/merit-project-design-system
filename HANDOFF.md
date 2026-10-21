# Handoff — 2026-10-21

Design system **v3.5.0** (branch `feat/design-system-v3`). Patchworks are done, the mobile wireframes are decided,
the wireframe rulings shipped as 3.5.0 (D18–D20), and the backend now serves everything the picked screens need.
**Next: the remaining Flutter screens** (batches 2-3, after the exam-intelligence detour below). The landing page
comes after.

## Where things stand

| Repo | Branch | State |
|---|---|---|
| `merit-project-design-system` (public) | `feat/design-system-v3` | v3.5.0: tokens, reference site, SKILL.md, patchwork engine v5, wireframe board, MIGRATION §1 rewritten to match the decisions |
| `merit-project-flutter` | `feat/design-system-v3` (from `origin/dev`), detour on `feat/exam-intelligence` | Setup `920b5bb`, then Phases 0-2 (data layer, shared and new widgets) and Phase 3 batch 1 (shell, Compete, Tasks & Quests, Achievements, Today, subject hub, Learn root) done, `ab1a91b..6525ec2`. Details: `merit-project-flutter/docs/V3-PROGRESS.md`. **Committed, not pushed.** Batches 2-3 next, after the detour |
| `merit-project-frontend` (admin) | `feat/exam-intelligence` (from `origin/dev`) | Admin lives here now (`app/admin/*`, `features/admin/*`): exam-intelligence settings form and per-subject Exam weights page. `merit-project-admin` is retired; its branch is abandoned. Not pushed |
| `merit-content` (private) | `feat/patchworks` | Physics, Chemistry, Biology patchworks (296 nodes), icon maps, 62 subject colours, 30 avatars, release tooling (now imports avatars too) |
| `merit-project-backend` | `feat/patchworks` (rebased onto `feat/revenuecat-sandbox`, pushed) | Patchworks API, templ landing removed, dead code cleared, all wireframe gaps built (below) |

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

## Next: Flutter screens

Status and commit ranges: `merit-project-flutter/docs/V3-PROGRESS.md`.

**Done (Flutter, branch `feat/design-system-v3`):** Phases 0-2 (data layer, shared widgets, new widgets) and Phase 3
batch 1 (shell, Compete, Tasks & Quests, Achievements, Today, subject hub, Learn root + Add a subject). The client
bugs listed in `BACKEND-GAPS.md` were fixed on dev before v3.

**Remaining:**
1. Batch 2: quiz taking (colour-only countdown timer + auto-submit, exit copy), quiz complete + `MeritShareCard`, review,
   study session with `MeritRatingButtons`, notes reader.
2. Batch 3: Points / Leaderboard restyle, Premium paywall + limit sheet, Me + settings (subject languages, reminders,
   avatar picker), auth / onboarding.
3. Optionally push `feat/design-system-v3` in the Flutter repo; lower the guard baselines in
   `tool/check_design_tokens.dart` as old uses fall.

## Then: landing page

- **Spec:** reference site §29 (landing specimen): eyebrow, headline with one underlined word, one line of body, pill CTA,
  programme grid, CTA band. Same tokens as the product, General Sans (self-hosted), patchwork tiles as hero art.
- **Code:** `merit-project-frontend/app/(landing)` + `features/landing` (`MIGRATION-v3.md` §2.6). The frontend is the
  canonical landing; the backend templ landing is gone (§3).
- **Inputs to gather:** final copy (EN, and SI/TA if it ships trilingual), pricing (Wanderer vs Achiever), app store links.

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
  0.9. Admin exam-weights page rebuilt in `merit-project-frontend` with grouped topic/subtopic rows, recompute toasts,
  plain-average badge and duplicate-paper warning.
- **Rulings:** duplicate papers get an admin warning only; thin data uses setting `exam_weight_min_papers` (default 8) and
  the plain-average roll-up below it; locked subtopics accrue and stay locked; admin moved to `merit-project-frontend`.
- **Contracts:** past-paper analysis, admin exam-weights and recompute are built; revise fields, peers and the
  duplicate/min-papers additions land with backend Phases 2-3; study plan and insights (Phases 4-5) pending. Full table:
  `merit-project-flutter/docs/V3-PROGRESS.md`.
- **Checkpoint 4:** Phase 4 Flutter client built (study-plan model, Stats forecast card, Practise "Recommended for you",
  Today exam countdown chip, questions/cards progress text). Phase 5 pending.
