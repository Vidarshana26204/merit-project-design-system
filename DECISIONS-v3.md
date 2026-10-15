# Merit DS v3 decisions

These decisions continue the v2 log (D1–D7, SKILL.md §9).
- **Status:** ✅ approved · ❌ rejected. D8–D15 were approved as recommended on 2026-10-16.
- **Evidence:** `research/v3/*`, plus the live specimen `research/v3/specimen.html`

## Framing (approved 2026-10-16)

| ID | Decision | Status |
|---|---|---|
| D0a | **Full reinvention.** Purple/yellow/mint neo-brutalism is retired. The grammar comes from the reference (MindInventory "Online Learning", Dribbble 18955306). | ✅ |
| D0b | Shipped as **tokens v3.0.0** in the same DTCG pipeline. Semantic names stay wherever their meaning holds. Consumers keep their v2 pin until they migrate. | ✅ |
| D0c | **Phosphor stays** the one icon family on both platforms. | ✅ |
| D0d | The **display face is re-evaluated** (D8). | ✅ |

## Phase A checkpoint (approved as recommended)

| ID | Decision | Rationale | Status |
|---|---|---|---|
| D8 | **Display face is General Sans** (500/600/700 + italics), self-hosted. Body stays **Plus Jakarta Sans**. SI/TA fall back to Noto Sans Sinhala/Tamil as before. Alternative: Satoshi, which can also supply a Black Italic wordmark voice. | Scored 90/100 (see `display-face-evaluation.md`). It has a true italic for the emphasis word, a geometric voice that matches the reference, and the same ITF FFL licence as today's Clash Display. | ✅ 2026-10-16 |
| D9 | **Primary action is orange `#F65E16` with an ink label** (`#1E1B2E`, 5.22:1). White-on-orange is never used for text. A strong variant, burnt orange `#B23F06` with white (5.82:1), exists for dense or long-label contexts. | The reference orange `#FC661E` fails with white (2.98:1) and against the canvas (2.85:1). Shifting it to `#F65E16` keeps it visually identical while clearing 3:1 on the canvas. | ✅ 2026-10-16 |
| D10 | **Palette families:** a warm **canvas** (`#FBFAF4`); **ink-slate** text (`#1E1B2E` / `#4A4760` / `#68667F`); **orange to coral to sand** for energy; **violet** for depth, focus, selection, links and the Achiever tier (`#54306C` / `#663696`, with electric `#7E24DE` for sparkles only); **sage** for success; **butter** for rewards and coins; **blush/sky** for categories only; **red** for error. | Sampled from the reference and extended for gamification (butter) and subject categories. | ✅ 2026-10-16 |
| D11 | **Depth model:** no hard offset shadows. Soft elevation `e0`–`e3` (warm violet-tinted, at most 2 layers, blur ≤ 40). **Cards have no border.** Ink outlines (1–1.5 px) appear only on illustrative elements, filter chips and patchwork. Card radius is 24 and pills stay. | This matches the reference's flat and airy look. It drops the v2 signature, and that is the intended break. | ✅ 2026-10-16 |
| D12 | **Icons:** Phosphor **Regular** by default (it was Bold), **Fill** for active and selected states, **Duotone** on category and feature chips. The streak icon is `flame` (Fill, orange) and the points icon is `coins` (Fill, butter). | Regular's stroke weight matches the 1–1.5 px outline grammar, and Duotone echoes the patchwork. | ✅ 2026-10-16 |
| D13 | **Landing font:** School Times is retired. The landing uses the D8 display face, and the wordmark voice uses a heavy italic (General Sans Bold Italic or Satoshi Black Italic). | One display family across product and marketing, in the style of the reference's italic wordmark. | ✅ 2026-10-16 |
| D14 | **Illustration kit "patchwork":** rounded-square tiles cut into 3–5 patches, filled with a tint or a pattern (dots, stripes, checks, hatch), with ink outlines, a white focal patch and a Duotone glyph. The motifs are a 4-point sparkle, a brush underline and a dotted connector. Patterns are SVG and never raster. | It makes subjects instantly recognisable and powers the new **learning path map** (the hierarchy shown as connected tiles). | ✅ 2026-10-16 |
| D15 | **Modes:** *calm* (quiz-taking, notes: no sparkles, violet selection, at most one orange action) and *energy* (home, rewards, landing). **Dark mode** uses a violet-black base (`#17121F` / `#221B2C`) with orange lifted to `#FF8A4C` and violet links at `#C9B3EA`. **Compact density** for admin is carried over from v2 D7. | See `edu-theming-criteria.md` C2, C5 and C8. | ✅ 2026-10-16 |

## Carried over from v2 unchanged
- **D5:** form selection is violet (it was purple), completion is sage plus a ✓ (it was mint). Selected must never read as achieved.
- **D7:** compact density for admin and contributor screens.
- **§9b:** web layout and action rules. Header chrome moves from `shadow-brutal-2` to `e1` when consumers migrate.
