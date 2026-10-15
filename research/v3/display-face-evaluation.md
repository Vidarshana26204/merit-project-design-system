# v3 display face evaluation (→ D8)

The v2 display face is Clash Display (Fontshare, ITF Free Font License). It is a display-only cut
with no italic, and its tight, sharp shapes suit neo-brutalism. The reference uses a softer geometric
grotesk with an italic emphasis voice, so v3 re-evaluates the face.

**Body stays Plus Jakarta Sans** (OFL). It is already airy and geometric like the reference's body
copy, it has italics, and keeping it avoids a second font migration. The **School Times** landing face
is decided separately in D13.

## Criteria (weighted)

| # | Criterion | Weight |
|---|---|---|
| 1 | Matches the reference voice: geometric, friendly and confident without being childish | 25 |
| 2 | Legible at 20–32 px on mobile (x-height, open apertures, distinct `a e s`, `1 l I`) | 20 |
| 3 | Weights 500/600/700 plus a **true italic** for the emphasis word | 15 |
| 4 | Figures: tabular or even-width digits for timers, points and leaderboards | 15 |
| 5 | Pairs with Plus Jakarta Sans and with Noto Sans Sinhala/Tamil in mixed lines (similar x-height and colour) | 15 |
| 6 | Licence allows self-hosting (web) and bundling (Flutter); file size | 10 |

## Candidates

| Face | Source / licence | Italic | Weights | Notes |
|---|---|---|---|---|
| **Clash Display** (keep) | Fontshare, ITF FFL (already self-hosted) | ✕ | 200–700 | Zero migration cost. Too sharp and condensed for the reference; no italic. |
| **General Sans** | Fontshare, ITF FFL | ✓ | 200–700 | Neutral geometric neo-grotesk. Very close to the reference headline colour. |
| **Satoshi** | Fontshare, ITF FFL | ✓ | 300–900 | Geometric with a modernist warmth. 900 Black Italic is a candidate for the wordmark/eyebrow voice. |
| **Cabinet Grotesk** | Fontshare, ITF FFL | ✕ | 100–900 | Characterful and playful, but has no italic. |
| **Outfit** | Google Fonts, OFL | ✕ | 100–900 | Rounded geometric. Friendly, but generic, with a single-storey `a` at all sizes. |
| **Bricolage Grotesque** | Google Fonts, OFL | ✕ | 200–800 (variable, opsz) | Expressive and educational-feeling, but quirky at small sizes. |

**Licence note:** ITF FFL (Fontshare) is the licence Merit already uses for Clash Display. It
permits commercial use in apps and websites, but the font files must not be redistributed as fonts
in their own right. Re-check the exact FFL text before shipping. OFL faces have no restrictions.

## Method

`research/v3/specimen.html` renders each candidate in Merit content:
- the headline with a brush underline
- the eyebrow
- digits for the timer and points, with `tnum`
- mixed EN / සිංහල / தமிழ் lines
- a quiz question title
- a button label

It renders light and dark, so the faces can be compared side by side.

## Provisional scoring (desk review, before the specimen)

| Face | 1 | 2 | 3 | 4 | 5 | 6 | Total /100 |
|---|---|---|---|---|---|---|---|
| Clash Display | 12 | 15 | 0 | 12 | 11 | 10 | 60 |
| General Sans | 22 | 18 | 15 | 12 | 14 | 9 | **90** |
| Satoshi | 23 | 17 | 15 | 12 | 13 | 9 | **89** |
| Cabinet Grotesk | 18 | 15 | 0 | 11 | 12 | 9 | 65 |
| Outfit | 17 | 17 | 0 | 11 | 13 | 10 | 68 |
| Bricolage Grotesque | 19 | 14 | 0 | 11 | 12 | 10 | 66 |

**Provisional recommendation:** General Sans for display (500/600/700 plus italic). If the user
wants a branded heavy-italic voice, add Satoshi Black Italic for the wordmark and eyebrows only.
The final call is made at the Phase A checkpoint, after viewing the specimen, and is recorded as D8.
