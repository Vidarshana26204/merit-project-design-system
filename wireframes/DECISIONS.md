# Mobile wireframe decisions (v3)

Picks recorded in the review board (`wireframes.html`, published as a private claude.ai artifact). Variant letters refer to the
candidates on that page. All screens are decided as of 2026-10-20. Round 8 revisions (same day) are folded into the rows below.

## Cross-cutting rules

- **Navigation B:** four tabs, Today · Learn · Compete · Me. Everything practice-related lives in the subject hub
  (Learn → subject → Learn / Practise / Cards / Stats). Quiz-taking, reviews, card sessions and the notes reader are
  full-screen with no tab bar.
- **Localization:** only subject content is localized (subject, topic and subtopic names, questions, flashcards, notes).
  The app UI stays English. Content language is set per subject enrollment, so no screen has an in-place language toggle.
  Register's Preferred language (`preferred_language`) seeds every enrollment's language. Onboarding step 3 lets the student
  override it per subject, and after that it changes only in Settings → Subject languages.
- **Timer:** colour-only states (text and icon), no pill. Proposed tokens are `timer.warnFg` (light orange-700, dark butter-300)
  and `timer.criticalFg` (light red-600, dark red-300). Butter text fails contrast on canvas.
- **Hierarchy navigation is a patchwork quilt:** topic tiles fill with mastery and subtopics open inline (Learn A).
- **`MeritShareCard`:** one reusable widget for shareable images (a light ticket on a violet ground, theme-independent, 1080×1350).
  It's used for quiz results first, then streak milestones, rank-ups and achievements.

## Screens

| Flow | Screen | Pick | Notes |
|---|---|---|---|
| 00 | Navigation | B | |
| 01 | Home | B | Plus A's subject tile row, placed before the Achiever band |
| 02 | Practise tab (mode select) | A | |
| 02 | Quiz taking | A | Timer revised to colour only |
| 02 | Quiz complete | A, revised | Stacked points bar, threshold line, ghost Achiever ×1.5, balance; Share → `MeritShareCard` |
| 02 | Attempt review | A | |
| 03 | Cards tab | A | |
| 03 | Card session | A | |
| 03 | Notes reader | A, revised | No language toggle. Progress bar, reading time and section count sit in the pinned header between Back and Save |
| 04 | Hub header | A + C's tabs | Tinted hero (`color_hex`) with type-scale section names; collapses to a 56dp bar. Dark mode uses a 24% tint on `night-850` plus a 40% subject rim (58% read as mid-grey) |
| 04 | Learn | A | Topic quilt map with inline subtopics |
| 04 | Subtopic | A, revised | Bottom sheet over the quilt, holding C's mastery recipe ring and B's Read → Remember → Prove rows (row bars match the ring arcs) |
| 04 | Subjects list | A | Rows plus "Add a subject" |
| 04 | Stats | B + C's card | Insights, with the "If the exam were today" predicted-grade card on top |
| 05 | Compete tab root | New (round 8) | Four rows: Points, Leaderboard, Tasks & Quests, Achievements, each with a teaser value |
| 05 | Tasks & Quests | New (round 8) | Two tabs. Tasks: state filter (All / Pending / Completed / Expired), surveys and referral milestones. Quests: coming-soon placeholder |
| 05 | Leaderboard | A | Podium + sticky "You" row, pushed from the Compete root |
| 05 | Points | A | Pushed from the Compete root |
| 05 | Achievements | B | Tiered list |
| 06 | Paywall | A + C | The limit-reached sheet (C) is the entry point at the moment of need; its "Keep going with Achiever" row opens the full paywall (A). Profile opens A directly |
| 07 | Me tab | A | Avatar opens the 30-avatar picker; settings via the Settings row |
| 08 | Register | A, revised | Existing fields and flow kept (incl. Confirm password, Preferred language → `preferred_language`); v3 styling only. Today's illustration (violet block, deco shapes, app icon) kept with a v3 container |
| 08 | Onboarding | A, revised | Existing 3 steps kept, no medium step. Step 1 compact: original cream illustration at 88dp, segmented level and year, District + School on one row. Step 2: v3 stream rows (category icon tile, text subject labels, radio), no patchworks. Step 3 (round 9): subject rows (40dp patchwork, §1.4a fallback) reusing the Settings → Subject languages row; ticking a subject reveals its EN / SI / TA switch, defaulting to `preferred_language` and sent per enrollment |

Shared, no pick needed: quiz states, card session end, hub pieces (collapsed header, unlock dialogs, enrol), streak pieces,
gates, avatar picker and settings, sign in / OTP / forgot password, system states.

## Design-system rulings (resolved in DS 3.5.0, 2026-10-21)

- **Patchwork mastery fill:** allowed as the one exception for tiles that show progress (D18, SKILL §12).
- **Timer:** `timer.text / warnText / criticalText` tokens (D19). The pill tokens are deprecated.
- **Subject tint:** 0.30 light / 0.24 dark into `subject.headerBase`, plus a 0.40 rim in dark (D20). The board's 58% used a
  pastel demo colour; real subject colours (e.g. Economics) failed at 58%. Header text is primary/secondary only.

## Round 10 (device test, 2026-10-22)

Board: merged into `wireframes.html` (round 10 blocks in the Quiz, Shell, Auth, Profile, Home and Compete flows; screen ids `r10-*`). Decisions D21–D24 in `DECISIONS-v3.md`.

- **Quiz results:** A. Points card on the normal surface (yellow only in the coin and bar, Achiever slice violet); "Review
  mistakes" row under it expands the review cards in place; Done is the only bottom action.
- **Points icon:** one `MeritCoin` from the brand coin asset (small cut ≤24dp, full cut above) everywhere points appear.
- **Mobile number:** B. "+94" prefix; the first digit must be 7, anything else shows "Sri Lankan mobile numbers start
  with 7".
- **Me:** Settings page removed; Study / App / Account sections live on Me. Subscription moves into Account.
- **Today · Your subjects:** 3 → tiles 88, 4 → tiles 68 (space-around), 5+ → 4 most recent, 1–2 → Learn rows.
- **Compete root:** A with B's podium preview: top-3 card with School / District / Island and a "You" row, then this
  week's points bars, streak week, achievements shelf, Tasks & Quests.
- **Trial length:** 14 days. The board copy now says 14.

## Web board (round 11, 2026-10-22)

Separate board: `wireframes-web.html` (artifact "Merit Web Wireframes"). Picks pending. Landing Quilt Map concepts are
live prototypes: A fractal tree, B circuit network, C orbit.

## Gate 0 — owner decisions before release (2026-10-23)

From the pre-release audit (`~/.claude/plans/as-per-the-handoff-md-zippy-seal.md`, A.7).

- **Prices (Achiever):** Rs 599 / month, Rs 4,990 / year (annual saves ≈ 31%). Stored in `tiers`, served by
  `GET /public/plans`, edited in admin. The landing's LKR 299/249 and "$0" copy is replaced.
- **Day boundary:** Sri Lanka midnight (Asia/Colombo, UTC+5:30) for daily caps, streaks and the daily plan. Backend
  moves off UTC; the "resets at midnight" copy stays.
- **Daily-plan "done":** a points threshold in `system_settings`, edited in admin. An edit takes effect from the next
  Sri Lanka day, never mid-day.
- **Grade prediction:** hidden below 30% topic coverage; show "Practise more to unlock your prediction" instead.
- **Retroactive achievements:** badges are awarded retroactively; their points are not (protects the leaderboard).
- **Push reminders:** hidden for v1 (no Firebase work; reminder toggles and pre-prompt removed from UI). v1.1.
- **v1 patchwork subjects:** Physics, Chemistry, Biology **plus Agricultural Science and ICT**. After generating the
  Agri/ICT icon maps, nodes with no suitable pool icon get marked in the patchwork-audit UI
  (`tools/patchwork_review.py serve`); new icons are then generated for the marked nodes. Other subjects use the §1.4a
  fallback.
- **Web content-language switch (EN/SI/TA):** on the subject page only (inline switch in the subject header). Not in
  Me › Preferences on web.

## Round 14 (landing) + round 15 (pre-release flows), 2026-10-24

- **Round 14 Phase A** is on the web board (Landing tab, "sections below the hero"): Mastery Engine (`#mastery`)
  and Merit Points (`#points`), live on the snapshot. Pricing and FAQ read `rules` / `plans` from
  `qm-samples.js` (`build_samples.py`, rehearsal `system_settings` + `tiers` + Gate 0 prices).
- **FSRS intervals are real** (backend `service.newFsrsEngine`, Flutter-parity weights, retention 0.9): new card
  Again 1 min · Hard 6 min · Good 10 min · Easy 16 days; Good when due: 10 min → 4 d → 14 d → 45 d → 135 d.
  The round 13 flashcard deck now shows these too (it showed example intervals).
- **Data to confirm:** rehearsal `pro_enrollment_limit_al` is **5**, the same as the free A/L cap (the round 14 plan
  assumed 6), and O/L is free 6 / Pro 10. The board shows the data as stored.
- **Round 15, mobile** (`wireframes.html`, tab 10): email verification, maintenance + update, subscription
  (active / cancelled / billing issue / restore), change password, sign-out confirm, two-step delete, session
  expired as a sheet (supersedes the dialog in tab 09), legal, help, onboarding back/skip with A/L 5 and O/L 4 steps
  (supersedes "3 steps"), prediction gate, Me without reminders, notification pre-prompt (v1.1).
- **Round 15, web** (`wireframes-web.html`): Me gets subscription status (read-only, store-managed), change
  password, sign-out, delete, legal, help; Auth gets email verification; Subjects gets the header language switch
  and the prediction gate; System states gets maintenance, 404 and error pages. Me's "Subject languages" screen and
  row are removed (Gate 0).

## Round 15 review (board notes, 2026-10-24)

Read from the boards' `picks` database (no comment threads).

**Mobile picks** (already built in Flutter): nav B, home B, quiz-mode A, quiz-take A, quiz-review A, learn A,
subtopic A, subjects-list A, leaderboard A, achievements B, points A, stats B, cards-home A, cards-session A,
paywall A (was C; already built), r10-results A, r10-mobile B, r10-compete A (with B's podium preview; built),
r10-me approved.

**Mobile notes, applied:**
- *cards-session:* the card session is a visible stack like the landing deck (vertical, cards behind show).
  Built in Flutter (`study_screen.dart`, `432d93b`).
- *r15-maint:* one update sheet; **Later** shows only when the update can be skipped (the separate "update
  available" frame is dropped). `update_dialog.dart` already behaves this way; it still needs v3 sheet styling.
- *r15-onb:* **O/L is blocked in this release** (no O/L subject coverage). Flutter already disables it.
- *r15-verify:* email verification is **not in this release** (no backend); mobile-number verification first.
  Screens kept for later.

**Mobile note, open:** *r10-coin:* "new points icon needs to be generated according to new design tokens". Asked the
owner whether this means a redesign or rebuilding the current coin from tokens.

**Web notes, applied:**
- *web-hub:* duplicate underline on the active hub tab fixed (the mobile tab border leaked into the web board).
- *web-compete:* the podium card now fills its column so it ends level with the right-hand stack; steps scale by
  one factor so the 1 : 2 : 3 ratio holds.
- *web-quiz:* results reworked as a new pick (`web-results`): A Scoreboard, B Quilt progress, C Recap and insight.
- *web-shell:* A picked.

**Accessibility audit** (`ux-ui-agent-skills:a11y-audit`, real-render gates over every flow, light + dark):
fixed store-badge captions (1.89:1), toast actions on the inverse surface in dark (1.26:1), the "Needs API" tag
(2.85:1), error text on errorSubtle (4.03:1, now `feedback.errorText`), a status bar on the feature phone, fixed-tone
badges and card text in dark. Every interactive element passes in default, hover and focus.

**Owner answers (2026-10-24):**
- *Points coin:* a **new coin design**. Draw 2–3 concepts in the v3 language on the board, owner picks, then generate
  the asset family (small, full, dark cut) and the Flutter asset.
- *Design System artifact:* repo links only (reference-site sidebar + `wireframes/BOARDS.md`); the reference site is
  not published.
- *Pro A/L subject cap:* stays **5**, the same as free. Achiever copy no longer lists a subject count.
- *Colour-blind subject collisions (6 pairs):* left as is; tiles always carry icons and names.

**Points coin picked (2026-10-24):** concept **D, coloured as D1** (brand facets). Generated as the shipped v3 coin
family; Flutter `MeritCoin` uses it (small/full × light/dark).

**Web quiz results picked (2026-10-24):** **A Scoreboard** (`web-results`). Rank move needs the API (rank movement);
without it the tile shows the streak only. Replaces the round 10 results frame on the web.
