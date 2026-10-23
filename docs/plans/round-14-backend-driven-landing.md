# Round 14: backend-driven plans, rules and samples; shared study components; Mastery Engine + Merit Points sections

## Context
Round 13 put live sections on the landing, but tiers, limits, benefits and prices are hard-coded, and the samples are a static snapshot. The user wants:
- plans and prices fetched from the backend;
- the new `GET /public/samples` limited per IP over a 6 h window;
- questions and flashcards rendered by the same shared components the student portal uses;
- the landing's flashcard stack and animation in the student portal too;
- two new landing sections: the **Mastery Engine** (Read → Remember → Prove, FSRS) and **Merit Points**.

User decisions:
- Rate limit: the same batch per IP for each 6 h window, plus a hard cap.
- Prices: stored in the backend `tiers` table and edited in admin.
- Flow: design the two new sections on the board first, then build.
- Production build: parallel Sonnet agents, orchestrated and reviewed in Chrome by me.

Findings that shape the plan:
- `system_settings` (rehearsal) already holds every rule the copy needs:
  - free limits: mastery 50 a day, papers 2 a day;
  - enrolments: A/L 5 free and 6 Pro, O/L 6 free and 5 Pro (stored this way);
  - points: 10 per correct answer; accuracy bonus +20 at 80%; Pro multiplier 1.5;
  - flashcard session +15 (cap 100 a day); note completion +25; unlock reward 50; force-unlock cost 100 plus 25 per unlock, 20% burned;
  - mastery weights: quiz 0.75 / notes 0.15 / cards 0.10, which give Prove 75 / Read 15 / Remember 10;
  - completion threshold 50; FSRS retention 0.9.
- The free-tier enrolment cap is **5** (CLAUDE.md's "2" is stale).
- The `tiers` table has only `code`, `duration_days`, `is_trial`. No prices exist anywhere.
- `RateLimitByIP` (`internal/api/middleware.go`) is a token bucket per IP. Its map never evicts entries.
- The backend schedules flashcards with `go-fsrs` v4, so it can return real next-review intervals.
- Frontend `feat/design-system-v3` (`bda6f65`) already has:
  - `components/question-block-renderer` (BlockList);
  - `components/content-blocks/math-text.tsx` (KaTeX is a dependency);
  - `features/student/notes/components/{question,flashcard}-set-runner.tsx`;
  - `motion`, and React Query.
- The `app/student/flashcards` and `app/student/quiz` pages are placeholders.
- The landing is still v2 (`features/landing/*`).

## Phase A: board round 14 (I do this, in this session)
1. **Mastery Engine section** (`#mastery`).
   - One real subtopic tile (patchwork) fills in three colours as you interact: Read 15%, Remember 10%, Prove 75%, using the real weights.
   - Each part demos its mechanic inline:
     - **Read:** a note section ticks done (+25 note points).
     - **Remember:** one flashcard is rated, and an FSRS strip shows real intervals for Again / Hard / Good / Easy and a forgetting curve at 90% retention.
     - **Prove:** one question is answered.
   - The tile's mastery ring reaches the completion threshold, and the next subtopic unlocks (+50 points).
   - Copy explains spaced repetition in plain words.
2. **Merit Points section** (`#points`).
   - An interactive "earn table": correct answer +10, 80% session bonus +20, flashcard session +15 (daily cap 100), note +25, unlock reward +50, and an Achiever ×1.5 toggle that recomputes everything.
   - A spend row: force-unlock costs 100, +25 each time, 20% burned.
   - A small district leaderboard fragment.
3. **Data stand-ins.** The board snapshot gains `rules` (from `system_settings`) and `plans` (from `tiers`), read-only from `merit_rehearsal` via `build_samples.py`. Pricing and FAQ read them, matching what the endpoints will serve. Prices stay "Rs —" until set.
4. The user reviews round 14 before Phase B starts.

## Phase B: production build (Sonnet agents in worktrees; I orchestrate and review)

### Agent B: backend (`merit-project-backend`, from `feat/patchworks`)
- **Migration.** Add `tiers.display_price_lkr numeric(10,2) null`, `tiers.is_public bool not null default false` and `tiers.display_order int`. Run `make sqlc`.
- **Admin.** `PUT /admin/tiers/:id` (price, public, order), alongside the existing `admin.GET("/tiers")`.
- **`GET /public/plans?lang=`** (1 h in-process cache, like explore). It returns:
  - the **free** tier: daily limits and A/L and O/L enrolment caps;
  - **achiever**: enrolment caps, multiplier, a feature-flag list (`adaptive`, `exam_forecast`, `unlimited`), trial days from `REGISTER_TRIAL`, and public prices (`PRO_MONTHLY`, `PRO_ANNUAL`, as LKR plus a period);
  - **rules**: the points values and the mastery weights listed above, plus FSRS retention.

  The client turns these structured values into copy, so it stays i18n-friendly.
- **`GET /public/samples?stream=&lang=`**:
  - It returns about 40 text-only, single-answer past-paper questions across the stream's subjects, explained ones first, with an `si` variant when `lang=si`.
  - It also returns about 20 flashcards, each with **real FSRS preview intervals** for a new card (go-fsrs `Repeat` at the configured retention).
  - The batch is fixed per IP per 6 h window: the seed is `hash(ip + floor(now/6h) + stream + lang)`, applied as `ORDER BY md5(id || seed)`, and the result is cached per (stream, lang, seed).
  - There is a hard cap of 30 requests per IP per 6 h → `429` with `Retry-After`.
- **Limiter.** New `RateLimitByIPWindow(n, window)` in `middleware.go`: a fixed-window counter keyed by `c.ClientIP()`. A janitor goroutine evicts expired windows, which the existing limiter lacks.
- **Flashcard sessions.** The student due-cards response gains the same `intervals` preview, so the portal shows real intervals.
- **Tests.** Handler tests for both endpoints (cache, seed stability within a window, change across windows, 429 after the cap), limiter tests and mapper tests. Run `make swagger` and `make mock`.

### Agent F: frontend (`merit-project-frontend`, from `feat/design-system-v3` `bda6f65`)
- **Shared study components** in `components/merit/study/`. They are built on `BlockList` / `math-text` (KaTeX) and v3 tokens, and are used by both the landing (demo mode: no writes, a `onAnswer` callback) and the student portal (API mode):
  - `QuestionCard`: options with keys 1–5; correct / wrong / reveal states; explanation; points pop; language toggle; the motion spec from the board.
  - `FlashcardDeck`: the board's 3-card stack, 3D flip, "Show answer", then Again / Hard / Good / Easy with **server intervals**, throw-off and rise animation, keyboard. The animation uses `motion`, with eases ported from `QMIco.EASE`.
  - `FsrsIntervals`, `PointsPop` and `MasteryTile` (the Read / Remember / Prove fill).
- **Student portal.**
  - `app/student/flashcards` becomes a real review session built on `FlashcardDeck`, using the study API with ratings posted.
  - `QuestionSetRunner` and `FlashcardSetRunner` in notes switch to the shared components.
  - `app/student/quiz` uses `QuestionCard` where it renders questions.
- **API clients.** `lib/api/public.ts` gains `getPlans()` and `getSamples()` (React Query, `skipAuth`). The pricing page, the landing pricing section, the FAQ facts and the Mastery and Points sections all read `getPlans()`. Nothing is hard-coded.
- **Admin.** The Tiers page gets price, public and order editing.
- The landing rebuild itself (hero tree, sections) remains Agent L's job, using these shared components.

### Orchestration
- Agent B starts first. It publishes the response shapes (swagger) early, so Agent F builds against typed contracts, using a mock until the backend lands.
- Each agent works in its own worktree. I review the diffs, run `make unit-test`, `pnpm lint` and `pnpm test`, and check the landing and student flashcards in Chrome (light, dark, phone).
- Nothing is pushed until the user says so.

## Verification
- **Board:** the two new sections are interactive in Chrome; numbers match `system_settings`; no console errors.
- **Backend:** the same IP gets the same batch within a window and a new batch after it; the 31st call in a window returns 429 with `Retry-After`; `/public/plans` reflects an admin price edit after cache expiry.
- **Frontend:** the landing and the student portal render the same `QuestionCard` and `FlashcardDeck`; KaTeX maths renders; ratings post and the deck advances; intervals come from the server.
