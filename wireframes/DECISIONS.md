# Mobile wireframe decisions (v3)

Picks recorded in the review board (`wireframes.html`, published as a private claude.ai artifact). Variant letters refer to the
candidates on that page. All screens are decided as of 2026-10-20.

## Cross-cutting rules

- **Navigation B:** four tabs, Today · Learn · Compete · Me. Everything practice-related lives in the subject hub
  (Learn → subject → Learn / Practise / Cards / Stats). Quiz-taking, reviews, card sessions and the notes reader are
  full-screen with no tab bar.
- **Localization:** only subject content is localized (subject, topic and subtopic names, questions, flashcards, notes).
  The app UI stays English. Content language is set per subject enrollment, so no screen has an in-place language toggle.
  Register's Preferred language (`preferred_language`) seeds every enrollment's language. After that it changes only in
  Settings → Subject languages.
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
| 03 | Notes reader | A | No language toggle |
| 04 | Hub header | A + C's tabs | Tinted hero (`color_hex`) with type-scale section names; collapses to a 56dp bar |
| 04 | Learn | A | Topic quilt map with inline subtopics |
| 04 | Subtopic | A | Bottom sheet over the quilt |
| 04 | Subjects list | A | Rows plus "Add a subject" |
| 04 | Stats | B + C's card | Insights, with the "If the exam were today" predicted-grade card on top |
| 05 | Leaderboard | A | Podium + sticky "You" row |
| 05 | Points | A | |
| 05 | Achievements | B | Tiered list |
| 06 | Paywall | A + C | The limit-reached sheet (C) is the entry point at the moment of need; its "Keep going with Achiever" row opens the full paywall (A). Profile opens A directly |
| 07 | Me tab | A | Avatar opens the 30-avatar picker; settings via the Settings row |
| 08 | Register | A, revised | Existing fields and flow kept (incl. Confirm password, Preferred language → `preferred_language`); v3 styling only |
| 08 | Onboarding | A, revised | Existing 3 steps kept, no medium step; patchworks on stream cards (30dp) and the subject grid (56dp), §1.4a fallback for subjects without art |

Shared, no pick needed: quiz states, card session end, hub pieces (collapsed header, unlock dialogs, enrol), streak pieces,
gates, avatar picker and settings, sign in / OTP / forgot password, system states.

## Needs a design-system ruling

- **Patchwork mastery fill** (Learn A, Home C, the subjects quilt). The tile is drawn twice, a grey base plus a colour copy clipped to the
  mastery percentage. SKILL §12 says tiles are theme-fixed and unaltered, so it needs an exception for progress display, or a
  ring or bar around an untouched tile instead.
- **`timer.warnFg` / `timer.criticalFg`** tokens (above).
- **Subject tint** `color-mix(color_hex 58%, bg.app)` for hub headers. It needs a dark-mode check per subject colour.
