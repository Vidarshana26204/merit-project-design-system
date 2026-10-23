# Wireframe boards

Both boards are generated from this repo and published as private claude.ai artifacts with a shared `picks`
database (pick buttons and notes save for everyone the artifact is shared with).

| Board | Source | Build | Artifact |
|---|---|---|---|
| Mobile (Flutter) | `wireframes.html` + `wireframes/wf.css`, round 15 block from `wireframes/r15_mobile.py` | `python3 wireframes/r15_mobile.py --splice` | https://claude.ai/artifact/Q6jsry2mnuUfD9csb1LB4X |
| Web (landing + student portal) | `wireframes/gen_web_board.py` (+ `gen_web.py`, `r12_*`, `r13_landing.py`, `r14_landing.py`, `r15_web.py`) | `python3 wireframes/gen_web_board.py > wireframes-web.html` | https://claude.ai/artifact/BSrqtke1qqxxvU1WzzpqSh |

Both are linked from the reference site sidebar (`Merit Design System.html`).

**Republish** from this repo with the same file path (keeps the URL and the picks). The files map is every asset the
page and its CSS/JS reference: `build/css/merit-tokens.css`, `wireframes/*.css|js`, `assets/v3/{brand,banners,motifs,
patterns,spots,patchwork-demo}/…` and `assets/fonts/GeneralSans-*.woff2` (General Sans may be self-hosted on our own
pages but not redistributed, so keep these artifacts private; the woff2 files are gitignored here).

**Picks and notes** live in the artifact database, not in git. Decisions taken from them are copied into
`wireframes/DECISIONS.md` (round 15 review, 2026-10-24).

The previous artifacts (web `6SeHPm6JhVrNV2ctgzhajn`, mobile `FqXHCEqumFTA2WNjKecHe2`) belong to another claude.ai
account and are frozen at round 13 (web) and round 10 (mobile).
