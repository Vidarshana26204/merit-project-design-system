# Backend gaps found while wireframing

Things the v3 mobile wireframes rely on that `merit-project-backend` doesn't provide yet. Screens tagged "Needs API" in
`wireframes.html` point here. Bugs come first, then gaps in order of how many picked screens depend on them.

## Bugs / mismatches

- **Daily limits:** the Flutter app hardcodes 20 mastery questions and 1 paper per day, while `system_settings` has
  `free_mastery_daily_limit` 50 and `free_paper_daily_limit` 2. The UI should read `GET /daily-limits`.
- **Adaptive mode** isn't gated on the client. Free users only see a server error snackbar.
- **Limit reached** shows only an error snackbar. It should open the contextual paywall sheet (06 gates).
- **Paper timer** counts up and ignores `duration_minutes`. It should count down and auto-submit at 0:00.
- **Pause copy:** the exit dialog says "progress lost", but sessions resume.
- **Premium:** the purchase-success flag is commented out, so the success state never shows.
- **Forgot password** button is a stub. The endpoints exist (`/auth/password/forgot → /verify → /reset`).
- **Notes:** there's no reader. The Notes button does nothing, and the endpoints exist.
- **Enrol after onboarding:** no UI. `POST /enrollments` and `/enrollments/capacity` exist.

## Backend status (2026-10-21, `merit-project-backend` branch `feat/patchworks`)

The bugs above are client-side: the server already enforces limits, gates adaptive mode and expires paper sessions.
Error responses now carry a stable `code` so the app can react: `DAILY_LIMIT_REACHED` (with `limit`, `used`,
`resets_at`) opens the limit sheet, `PREMIUM_REQUIRED` opens the paywall, and `NOT_ENROLLED`,
`ENROLLMENT_LIMIT_REACHED`, `SUBTOPIC_LOCKED` and `INSUFFICIENT_POINTS` are also coded. Paper sessions expose
`duration_minutes` and `started_at` for a countdown.

| Feature | Used by | Status |
|---|---|---|
| Achievements | 05 Achievements B, Compete root, quiz complete | **Done.** `GET /students/me/achievements`: 6 families × 4 tiers, progress, `newly_unlocked`, points through the ledger. Quiz completion returns `achievements_unlocked`. Admin CRUD at `/admin/achievements` |
| Task history | 05 Tasks & Quests | **Done.** `GET /tasks?state=pending\|completed\|expired\|all` with `state`, `ends_at`, `completed_at`, `points_awarded`. Referral tiers come from `GET /students/me/referrals` |
| Avatar catalogue | 07 avatar picker | **Done.** `GET /avatars` (30, CDN URLs) and `PUT /user {"user": {"avatar_id"}}`; imported by `patchworksimport --avatars` |
| Mastery weights + parts | 04 Subtopic sheet (ring + rows) | **Done.** `GET /progress/subtopics/:id` → `mastery_parts.{read,remember,prove}` with weight, percentage, contribution. Defaults are 0.15 / 0.10 / 0.75, not the 20/30/50 drawn |
| Grade prediction | 04 Stats C card | **Done.** `GET /subjects/:id/prediction`: grade, estimate, low–high band, confidence, basis; `grade: null` with `not_enough_data` |
| Stats insights | 04 Stats B | **Done.** `GET /subjects/:id/insights`: up to 3 cards (fading cards, weak subtopic, weekly trend, Bloom for Achiever, cards due) |
| Daily plan | 01 Home B | **Done.** `GET /today/plan`: up to 3 items with live progress; all done pays 30 points (`daily_challenge`) once |
| Study reminders + push | 07 Settings, Quests "Notify me" | **Done, needs Firebase.** `POST/DELETE /devices`, `GET/PUT /students/me/reminders`, `POST /quests/notify-me`; `cron send-reminders` every 15 min. Inactive until `FCM_PROJECT_ID` + `FCM_CREDENTIALS_FILE` are set |
| Enrollment language | 08 step 3, 07 Subject languages | **Done.** Per-subject `language` on `POST /enrollments`; both create and `PUT /enrollments/:id/language` reject languages missing from `available_languages` |
| Quests | 05 Quests tab | Not started (coming-soon placeholder only) |
| Weekly leagues | 05 Leaderboard C (not picked) | Not planned. `leaderboard_snapshots` has no code left |
| Structured questions | 02 quiz states | Not started |
| Points → Achiever | 05 Points B (not picked) | Not planned |

## Open product questions

- **Prices:** the DS specimen says Rs 4,990/yr and Rs 599/mo, but the Profile card says "$4.99/mo". Which is right?
- **Share card privacy:** is it OK to show username, school and district on shared images?
- **Daily plan:** implemented as "all of today's items done" (30 points); confirm or change.
