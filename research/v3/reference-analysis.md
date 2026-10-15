# v3 reference analysis

**Source:** MindInventory UI/UX, "Online Learning website and Mobile app", Dribbble shot 18955306.
<https://dribbble.com/shots/18955306-Online-Learning-website-and-Mobile-app>

The reference is inspiration only. We take its *grammar*: palette relationships, shape language and
motifs. We do not copy its layouts, illustrations or wordmark, and no reference imagery is committed
to this repo.

## 1. Palette (sampled from the shot's full-resolution images, 2026-10-16)

Pixels were sampled in-browser from the two 2048×1536 frames, after filtering out greys and
quantising to steps of 6. The values are approximate. The counts show how much area each colour
covers.

| Role in reference | Sampled | Notes |
|---|---|---|
| Canvas | `#FCFCF0`–`#FBFAF3` | Warm off-white, not cream. Lighter and less yellow than Merit v2 `#FFF7ED`. |
| Outline | `#000000` | Thin (≈1–1.5 px) ink lines on illustrations and some chips. Never on cards. |
| Deep violet | `#54306C`, `#4E2A66`, `#3C244E` | Footer and CTA bands, illustration shadows. The second-largest saturated area. |
| Mid violet | `#663696` | Illustration patches. |
| Electric violet | `#7E24DE` | 4-point sparkles only. Tiny area, high punch. |
| Lilac | `#905AA8` | Secondary patch. |
| Orange (CTA) | `#FC661E`, `#FC601E` | Buttons, search action, eyebrow labels, sparkles. v3 tunes it to `#F65E16` (D9). |
| Light orange | `#FF8442`, `#E4783C` | Brush underline, patches. |
| Coral | `#FC906C`, `#FC846C` | The largest warm patch area, plus the community "blob". |
| Sand / cream | `#FCE4C6`, `#F0DEC0`, `#E4D2B4` | Patch fills with halftone dots. |
| Sage | `#A2D2AE` | Patch fill. The only cool tint. |
| Slate text | `#3C3C60`, `#60607E` | Body and secondary text are a *blue-violet slate*, not neutral grey. |

**Takeaway:** the reference uses two hue families, **orange→coral→sand** (warm energy) and
**violet** (depth and authority), plus a single sage accent. All of them sit on a near-white warm
canvas, with ink outlines only on illustrative elements.

## 2. Typography

- **Headlines** are set in a clean geometric grotesk with medium-bold weight, tight but not
  compressed, sentence case and large sizes.
- **Emphasis:** one key word gets a hand-drawn **brush-stroke underline** in orange ("top
  *teachers*", "*free* courses", "*biggest* community"). Some section titles add an italic
  emphasis word.
- **Eyebrows** are tiny uppercase orange labels with wide tracking, for example "INTRODUCING
  INTERACTIVE", "100% FREE" or "BUILD UP THE COMMUNITY".
- **Wordmark** is a heavy italic condensed display set in uppercase, with an orange full stop.
- **Body** is a small, airy humanist sans in slate.

## 3. Shape and depth

- **Cards** are flat or almost flat, with no visible border and large radii (about 20–28 px). Depth
  comes from very soft, low-contrast shadows or a slight tint change.
- **Pills** are used for every button, search field, filter chip ("Class 7 / 8 / 9…") and email
  input.
- **Search** is a white pill with a round orange action button inside it and a soft shadow.
- **Bands:** the deep-violet CTA band has one end shaped as a large orange quarter-pill, which gives
  the dark band a warm "cap".
- There are **no hard offset shadows** and **no thick black borders on UI chrome**. This is the main
  break from Merit v2's neo-brutalism.

## 4. Illustration grammar ("patchwork")

- Each subject tile is a rounded square split into **3–5 geometric patches**. Each patch is filled
  with a flat tint or a **pattern**: halftone dots, diagonal stripes, small checks or cross-hatch.
- A **single ink line** outlines the whole tile and each patch. Inside, a simple object (tablet,
  target, keyboard, rocket, molecule) is drawn in ink line on white.
- **Dotted connector lines** with small circle nodes join tiles into a "learning path" or graph.
- **Sparkles:** 4-point stars in orange and violet, at 2–3 sizes, scattered around.
- **Avatars** sit in circular frames with a coloured ring, over a dotted world map.

## 5. Layout patterns worth adopting

| Pattern | Use in Merit |
|---|---|
| Eyebrow, then headline with an underlined word, then one line of body | Section headers on landing, home and empty states |
| Pill search with an orange action | Subject/topic search, notes search |
| Chip filter row | Grade/stream/medium filters, quiz mode select |
| Grid of patchwork tiles with a title and two lines of copy | Subject grid, topic grid, programme cards |
| Connected tiles on a dotted path | Hierarchy (Subject→Topic→Subtopic) progress map. A strong fit for Merit's existing animated tree hierarchy. |
| Deep-violet band with an orange cap | Premium/Achiever upsell, end-of-quiz CTA, newsletter |
| Mobile: hamburger, wordmark, pill CTA; illustration first, headline below | Landing on mobile |

## 6. What the reference does not cover (Merit must design these itself)

- Gamification: streaks, coins/points, leaderboards, tiers, grade seals and level-up.
- The exam surface: quiz options with correct/wrong/revealed states, the paper timer, LaTeX and
  figures, and long-form notes.
- Dark mode, tri-lingual (SI/TA) typography, and dense admin tables.

These need v3 solutions that stay inside the reference grammar. See `edu-theming-criteria.md` and
`feature-inventory.md`.
