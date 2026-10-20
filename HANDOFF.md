# Handoff — 2026-10-20

Design system **v3.5.0** (branch `feat/design-system-v3`). Patchworks are done, the mobile wireframes are
decided, and the wireframe rulings shipped as 3.5.0 (D18–D20). **Next: the Flutter restyle** (MIGRATION §1,
branch `feat/design-system-v3` in the app, set up at `920b5bb`), alongside the backend gap work. The landing page
comes after.

## Where things stand

| Repo | Branch | State |
|---|---|---|
| `merit-project-design-system` (public) | `feat/design-system-v3` | v3.5.0: tokens, reference site, SKILL.md, patchwork engine v5, wireframe board |
| `merit-project-flutter` | `feat/design-system-v3` | v3.5.0 tokens, General Sans, theme remap, guard (`920b5bb`); screens next |
| `merit-content` (private) | `feat/patchworks` | Physics, Chemistry, Biology patchworks (296 nodes), icon maps, 62 subject colours, 30 avatars, release tooling |
| `merit-project-backend` | `feat/patchworks` | `hierarchy_patchworks` API, migrations 000046–000047, importer in the image, `CONTENT_CDN_BASE` in deploy |

None of the branches is merged. The backend deploy change only takes effect once `feat/patchworks` lands on `main`.

**Patchworks in one paragraph.** Every Subject, Topic and Subtopic has a generated tile: a
square-in-a-square quilt block. A subject's 4 patches gain a nested diamond at topic level (5)
and a square at subtopic level (6). The icon plate has as many sides as the tile has patches
(square, pentagon, hexagon). All colours derive from the subject's `color_hex`. Variants are
`tile`, `wash` (behind flashcards and notes) and `mono`. Rules: `SKILL.md` §12. Decisions:
`DECISIONS-v3.md` D16 revs 1–5. Specimens: reference site §21.

## Open items carried over

- **Patchworks go-live (manual):** merit-content `docs/PATCHWORKS-RELEASE.md`. One-time setup is
  still to do: public read on `content-assets/patchworks/*`, an upload key, and the GitHub
  variable `CONTENT_CDN_BASE`. Then push and import. merit-content CI warns until it's done.
- **Agricultural Science and ICT** have colours but no icon maps, so they have no patchworks yet.
- **Feature icons** (flashcards, notes, quiz modes…) are deferred, so the app uses Phosphor.
  The groundwork is `patchwork_jev.py --features`.
- **Jev icon audit:** 45 flagged and 61 weak remain (optional polish). Picker:
  `tools/run.sh tools/patchwork_review.py serve` in merit-content.
- **Landing:** decided: `merit-project-frontend` is canonical; the backend templ landing is being removed.
- **Clash Display licence:** the v2 Clash Display (FFL) files are still committed here (public). Remove them and
  decide on history before v3 ships (`assets/fonts/README.md`).

## Mobile wireframing (decided)

- **Board:** `wireframes.html` at the repo root (linked from the reference site §28). It uses `wireframes/{wf.css, wf.js, icons.js}`
  and is published as a private claude.ai artifact with a shared pick tracker (`picks/<screen>` in the artifact db).
  It covers 10 flows (00 shell → 09 states) at 360dp, with 3 candidates per screen.
- **Decisions so far:** `wireframes/DECISIONS.md`. Navigation is B (Today · Learn · Compete · Me), the subject hub has a tinted hero and
  type-scale sections, Learn is a patchwork quilt map, and quiz results share through a `MeritShareCard` template.
  Only subject content is localized; the UI stays English.
- **All screens are picked** (2026-10-20). Register and onboarding keep the existing flow, with v3 styling only.
- **Backend work surfaced:** `wireframes/BACKEND-GAPS.md` (daily-limit mismatch, achievements endpoint, grade prediction,
  avatar catalogue, reminders…).
- **DS rulings (done, 3.5.0):** mastery fill allowed as the §12 exception (D18); colour-only timer tokens
  `timer.text / warnText / criticalText` (D19); subject tint 0.30 light / 0.24 dark, checked for all 62 subjects with
  `npm run check:subjects` (D20).
- **Then:** `MIGRATION-v3.md` §1 from §1.3 (shared widgets), then screens in §1.6 order.

## Then: landing page

- **Spec:** reference site §29 (landing specimen): eyebrow, headline with one underlined word,
  one line of body, pill CTA, programme grid, CTA band. Uses the same tokens as the product,
  General Sans (self-hosted), and patchwork tiles as hero art.
- **Code:** `merit-project-frontend/app/(landing)` + `features/landing` (`MIGRATION-v3.md` §2.6),
  or the backend templ landing (§3). Decide which first.
- **Inputs to gather:** final copy (EN, and SI/TA if it ships trilingual), pricing (Wanderer vs
  Achiever), and app store links.

## How to work here

- `npm run build && npm run check` (tokens + contrast gate) before committing.
- Patchwork engine: `scripts/patchwork/`; run its tests with
  `python -m pytest -q scripts/patchwork` (needs fonttools).
- The licensed icon pack and production patchworks never enter this public repo, only the
  Phosphor demo set (`assets/v3/patchwork-demo/`).
