# v3 educational theming criteria

These are acceptance rules. Every v3 token, component and specimen must pass them. They come from
Merit's audience (Sri Lankan O/L and A/L students, aged 15–19), its product (exam prep with
gamification) and its constraints (tri-lingual, low-end Android, freemium).

## C1. Long-read comfort
Notes, past papers and explanations are read for 20+ minutes at a time.
- The reading surface is the warm canvas (`bg.app`) or white (`surface.default`). Long text is never
  set on violet or orange.
- Body is at least 16 px on mobile reading surfaces, line-height at least 1.5 for Latin and **at
  least 1.6 for SI/TA**. Measure is 60–75 characters on web.
- Text colour is ink-slate, not pure black, and at least 7:1 on reading surfaces (AAA is the target
  for body).
- LaTeX, tables and figures inherit text colours. Figures get a `surface.sunken` plate, not a
  border.

## C2. Exam calm vs. game energy
Merit is both a game and an exam room. The palette has to separate those two modes.
- **Calm mode** (quiz-taking, paper timer, notes reader): canvas or white, slate text, violet for
  selection and focus. No sparkles, no orange fills except the single primary action.
- **Energy mode** (home, streaks, rewards, results, leaderboard, landing): orange, coral, sparkles,
  patchwork and brush underlines are allowed.
- **Celebration** (grade reveal, level-up, streak milestone): the only place where motion goes above
  `duration.slow`. It respects reduced motion.
- **Timer:** the safe state is neutral and the warn state is butter. Only the critical state turns
  red, so students don't panic from minute one.

## C3. Accessibility (WCAG 2.2 AA minimum, enforced by the contrast gate)
- Text needs 4.5:1, large text 3:1, and UI parts and focus rings 3:1.
- **Brand orange cannot carry white text.** The reference `#FC661E` is 2.98:1 and the tuned `#F65E16` is 3.22:1, so it passes only for large text.
  Use ink text on orange (5.64:1) or a darker orange fill for white text. See DECISIONS-v3 D9.
- Orange is too light for a focus ring on canvas (2.85:1), so the focus ring is violet.
- Correct and wrong answers always pair colour with an icon (✓/✕) and a text label. The "revealed"
  state uses a dashed border.
- Touch targets are at least 48 dp. The smallest label is 11 px.
- Reduced motion: no shimmer, crossfade instead of flip, no sparkle twinkle.

## C4. Tri-lingual (EN / SI / TA)
- None of the candidate display faces contain Sinhala or Tamil. Every stack falls back to Noto Sans
  Sinhala and Noto Sans Tamil, as in v2.
- SI/TA overrides: tracking 0, **no uppercase eyebrows** (they render as normal case at label size),
  line-height at least 1.6 for body and 1.3 for display.
- Tamil runs about 30–40% longer, so buttons, chips and tabs wrap or flex and never truncate the
  primary label.
- The brush underline must work on SI/TA words. It is drawn as a decoration under the text box,
  not as a glyph.
- The language switcher shows each language in its own script (English / සිංහල / தமிழ்).

## C5. Device and context
- **Low-end Android:** patterns are SVG and cacheable, with no large raster textures. Soft shadows
  are capped at blur 16 and at most 2 layers. No backdrop-blur.
- **Bright outdoor use:** the canvas is not pure white (less glare). Tints keep at least 1.15:1
  luminance difference from the canvas, so patches stay visible in sunlight.
- **Dark mode** is a first-class theme. Its background is violet-black, not neutral grey, so it still
  feels like the brand.

## C6. Freemium tiers
- **Wanderer** (free) is neutral: white or canvas surfaces with an ink seal.
- **Achiever** (Pro) uses the deep-violet band with a butter seal and orange cap. It reads as
  premium without gradients.
- Quota meters say "12 of 50 questions today". The copy is neutral and never shaming. Upsell
  shows at most one band per screen.

## C7. Gamification without noise
- **Points/coins** are butter and **streak** is orange, each with a Phosphor Fill icon. Emoji are
  never used as UI icons.
- **Leaderboard:** the "You" row is violet-selected and sticky when off-screen.
- **Grades A–F** use a ramp from sage (A) through butter and coral to red (F). Every grade shows its
  letter, so colour is never the only signal.

## C8. Density
- The student app and landing are *expressive*: 16–24 padding, e1–e2 elevation, patchwork.
- The admin and contributor dashboards are *compact*: 8–12 padding, hairline borders, e0–e1, and no
  patchwork in tables. This carries v2 D7 forward.
