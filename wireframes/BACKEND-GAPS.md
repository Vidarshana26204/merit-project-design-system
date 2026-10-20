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

## Missing endpoints / features

| Feature | Used by | What's needed |
|---|---|---|
| Achievements | 05 Achievements B, share card, 07 Me | `GET /students/me/achievements` (tier, progress_current/target, points_reward), unlock events → `achievement_unlock` ledger. Tables already exist. |
| Grade prediction | 04 Stats (picked B + C card) | A per-subject predicted A/B/C/S/F grade from mastery, with calibrated bands |
| Stats insights | 04 Stats B | Rule-based insight cards (trend, fading cards, Bloom pattern) |
| Avatar catalogue | 07 avatar picker, onboarding | List of the 30 avatars (merit-content CDN) and `PUT /user {avatar_id}`, instead of photo upload |
| Daily plan / quest | 01 Home B ("2 of 3 done") | Server definition of the daily set. The `daily_challenge` points reason exists but has no mechanism |
| Study reminders | 07 Settings, onboarding B | Push (FCM) plus a reminder-time preference |
| Weekly leagues | 05 Leaderboard C (not picked) | Cohorts, weekly reset, history. `leaderboard_snapshots` is unused |
| Mastery weights | 04 Subtopic C (not picked) | Expose `mastery_weight_*` and per-part scores |
| Multi-subtopic mastery quiz | 02 Practise C (not picked) | `hierarchy_ids[]` on `POST /quiz/sessions/mastery` |
| Section quick check | 03 Notes B (not picked) | A question linked to each note section |
| Mistake re-queue | 02 Complete C, Review B (not picked) | Schedule wrong answers for a later quiz |
| Structured questions | 02 quiz states | UI for self-marking plus a scoring endpoint (the types exist in the model) |
| Passwordless register | 08 Register B (if picked) | OTP-verified register without a password |
| Points → Achiever | 05 Points B (not picked) | Student endpoint for the `MERIT_POINTS` subscription type |

## Open product questions

- **Prices:** the DS specimen says Rs 4,990/yr and Rs 599/mo, but the Profile card says "$4.99/mo". Which is right?
- **Share card privacy:** is it OK to show username, school and district on shared images?
- **Daily plan:** what counts as "done for today"?
