---
name: merit-design-system
description: >-
  The Merit Project design system — a playful, neo-brutalist, gamified
  education brand for Sri Lankan O/L & A/L students. Use this skill whenever
  building or styling ANY Merit Project surface: the Flutter mobile app, the
  marketing/landing website, or supporting graphics. It defines the canonical
  color tokens, typography, the signature hard-shadow + black-border look,
  component recipes (buttons, cards, inputs, pills, progress, badges, toggles,
  tab bars), decorative motifs, dark-mode rules, and copy voice — with ready-to-
  paste Flutter (Dart) and HTML/CSS snippets.
---

# Merit Project — Design System

> **Learn it. Level up. Earn Merit.**
> A gamified exam-prep platform for Sri Lankan **O/L** and **A/L** students —
> quizzes, flashcards, past papers, streaks and adaptive practice across
> **Sinhala, Tamil and English**.

This skill is the single source of truth for the Merit brand across the
**Flutter app** and the **landing page**. When the two references disagree, the
priority order is: **Brand Board → Mobile App Screens → Landing**.

---

## 1. Brand essence

Merit is **bold, playful, and unmistakably game-like** — but built for serious
study. The look is **neo-brutalist**: flat saturated color blocks, **solid black
2px outlines on everything**, and **hard offset drop-shadows** (no blur). It
feels like a sticker sheet, an arcade, and a study planner at once.

**Three pillars to keep in every screen:**
1. **Outlined & chunky** — black borders + hard shadows give physical, tactile weight.
2. **Gamified** — streaks 🔥, merit points 🪙, tiers, starbursts, leaderboards, progress bars.
3. **Tri-lingual & local** — EN / SI / TA toggles are first-class; content is Sri-Lanka-specific (A/L streams, districts, schools).

**Voice:** confident, encouraging, short. "Keep your streak alive." "Earn it."
"Hit your weak spots first." Never corporate, never condescending. Emoji are
**on-brand** but used sparingly as accents (🔥 streak, 🪙 coins/points, ★ rating/quiz).

---

## 2. Color tokens (canonical)

These six tones + black are the **whole system. No remix, no new hues.**
Marketing (landing page) and the mobile app use two different literal
yellows for the same "Yellow" role — see the note below the table.

| Token | Hex | Role |
|---|---|---|
| **Purple** | `#8E55D7` | Primary — main actions, brand, active states |
| **Purple Deep** | `#6E36B8` | Primary pressed / deep shade |
| **Yellow** | `#FFCC00` (marketing) / `#F2D43B` (app) | Accent — highlights, XP, rewards, secondary CTA |
| **Mint** | `#9CE7C8` (app) / `#9ED5B7` (marketing) | Support — success, "done", positive stats |
| **Cream** | `#FFF7ED` (app) / `#FFEFD7` (marketing) | Surface — light background, soft cards |
| **Ink** | `#29261B` (app) / `#312A31` (marketing) | Charcoal — primary text, dark cards |
| **Ink Deep** | `#1B161B` | Darkest — dark-mode background |
| **White** | `#FFFFFF` | Base surface |
| **Line / Border** | `#000000` (light mode) / cream (dark mode) | The outline on *everything* — flips per theme, see §6 |

> **Marketing vs. app yellow:** the landing page (`layout.templ`) uses the
> brighter `#FFCC00`; the Flutter app uses the softer `#F2D43B` so large
> fills stay comfortable to look at during long study sessions. Both are
> "Yellow" — don't introduce a third value.

### Extended palette (mobile app only)

| Token | Hex | Use |
|---|---|---|
| Purple Light | `#EDE4F8` | Selected/container tint (Material `primaryContainer`) |
| Mint Light / Mint Dark | `#D5F5E9` / `#2D6649` | Success container tint / on-dark-success text |
| Pink | `#FFB3C8` | Category accent (e.g. Arts, Biology) |
| Blue | `#B3D8FF` | Category accent (e.g. Technology, ICT) |
| Text | `#29261B` | App body text |
| Text Dim | `#5A4A5A` | Secondary text |
| Text Mute | `#7A6C7A` | Tertiary / captions / placeholders |
| Hairline | `#EADCD0` | Light-mode dividers |
| Streak Orange | `#FF6B2B` | Streak flame / gamification accent (app-specific, not a new hue — a fixed semantic token) |
| Grade Orange | `#FF9800` | Grade-D badge in quiz results |
| Error | `#C4393A` | Validation errors, destructive actions |

**Contrast-safe text/icon variants** — the raw fills above (`yellow`,
`mint`, `blue`, `pink`) fail WCAG contrast for small text/icons on white.
Use these instead whenever a fill color needs to render as text or an icon
glyph on a light surface:

| Token | Hex | Contrast on white |
|---|---|---|
| Yellow Text | `#7A5F00` | ~6.5:1 |
| Mint Text | `#1E5C42` | ~7.5:1 |
| Blue Text | `#1A4A7A` | ~7.2:1 |
| Pink Text | `#8A2240` | ~6.1:1 |

### Flutter — `MeritColors` (source of truth: `lib/theme/merit_theme.dart`)

```dart
import 'package:flutter/material.dart';

abstract final class MeritColors {
  static const purple      = Color(0xFF8E55D7);
  static const purpleDeep  = Color(0xFF6E36B8);
  static const purpleLight = Color(0xFFEDE4F8);
  static const yellow      = Color(0xFFF2D43B); // app yellow — see note above
  static const yellowLight = Color(0xFFFFF5CC);
  static const mint        = Color(0xFF9CE7C8);
  static const mintLight   = Color(0xFFD5F5E9);
  static const mintDark    = Color(0xFF2D6649);
  static const pink        = Color(0xFFFFB3C8);
  static const blue        = Color(0xFFB3D8FF);
  static const cream       = Color(0xFFFFF7ED);
  static const ink         = Color(0xFF29261B);
  static const inkDeep     = Color(0xFF1B161B);
  static const white       = Color(0xFFFFFFFF);

  static const textDim  = Color(0xFF5A4A5A);
  static const textMute = Color(0xFF7A6C7A);
  static const hairline = Color(0xFFEADCD0);

  // Contrast-safe fill→text/icon variants (use on light surfaces)
  static const yellowText = Color(0xFF7A5F00);
  static const mintText   = Color(0xFF1E5C42);
  static const blueText   = Color(0xFF1A4A7A);
  static const pinkText   = Color(0xFF8A2240);

  // App-specific semantic colors
  static const streakOrange = Color(0xFFFF6B2B);
  static const gradeOrange  = Color(0xFFFF9800);
  static const error        = Color(0xFFC4393A);
}
```

---

## 3. Typography

| Family | Where | Weights | Tracking |
|---|---|---|---|
| **School Times** | All headings, numbers, buttons, stat figures, labels-as-display | single weight (400), no true bold | tight: `-0.02em` (display down to `-0.04em`) |
| **Plus Jakarta Sans** | Body copy, descriptions, form values, fine print | 400–700 | normal |

### Flutter typography

```dart
class MeritType {
  static const display = 'SchoolTimes';
  static TextStyle schoolTimes(double size, {FontWeight w = FontWeight.w700, Color? c}) =>
      TextStyle(fontFamily: display, fontSize: size, fontWeight: w,
                letterSpacing: size >= 64 ? -size * 0.04 : -size * 0.02,
                height: 1.0, color: c);
  static TextStyle body(double size, {FontWeight w = FontWeight.w500, Color? c}) =>
      GoogleFonts.plusJakartaSans(fontSize: size, fontWeight: w, height: 1.5, color: c);
  static TextStyle label() => GoogleFonts.plusJakartaSans(
      fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 1.8,
      color: MeritColors.textMute);
}
```

---

## 4. The signature look — borders, shadows, radii

| Property | Value | Notes |
|---|---|---|
| **Border** | `2px solid #000` | 3px on large/hero frames, 1.5px on tiny chips |
| **Hard shadow — small** | `2px 2px 0` / `3px 3px 0` | chips, inputs |
| **Hard shadow — card** | `4px 4px 0` / `5px 5px 0` | content cards |
| **Hard shadow — hero** | `6px 6px 0` … up to `14px 14px 0` | bigger = more important |
| **Radius — pill** | `999px` | buttons, toggles, tags, progress bars |
| **Radius — card** | `18–28px` | content cards |
| **Radius — large frame** | `32–46px` | phone bezel, image frames |
| **Radius — icon chip** | `8–16px` | square-ish badges/icons |

### Flutter — `meritBox`

```dart
BoxDecoration meritBox({
  Color fill = MeritColors.white,
  double radius = 18,
  double offset = 4,
  Color border = MeritColors.line,
  Color? shadow,
}) => BoxDecoration(
  color: fill,
  borderRadius: BorderRadius.circular(radius),
  border: Border.all(color: border, width: 2),
  boxShadow: [
    BoxShadow(color: shadow ?? MeritColors.line,
              offset: Offset(offset, offset), blurRadius: 0),
  ],
);
```

---

## 5. Components (quick reference)

### Buttons
- **Primary** — purple fill, white text
- **Accent** — yellow fill, ink text
- **Dark** — ink fill, cream text, yellow circular arrow chip
- **Ghost** — transparent, ink border
- **Link** — purple underline, no border

### Cards
`meritBox` + padding 14–26px. White/cream = neutral, purple/ink = featured, yellow = reward, mint = success.

### Inputs
Radius 14px (not pill). UPPERCASE micro-label above. Focus → purple border + shadow.

### Pills
`.p` purple · `.y` yellow · `.m` mint · `.k` ink — 1.5–2px border, 99px radius.

### Progress
Bordered track, accent fill, **black right-edge divider** on fill. Stepper: done=mint, current=purple, todo=white.

### Toggles
46×24 pill, ink→mint. Checkbox: 22×22 rounded-7px, mint+✓ when on.

### Tab bar
`meritBox(radius:20, offset:3)`, 5 items. Active = purple chip with white glyph.

### Gamification
- Streak chip: white pill, 🔥 {n}, School Times
- Coins chip: yellow pill, 🪙 {points}
- Streak ribbon: done=purple ✓, today=yellow !, future=dashed
- Leaderboard: dark card, "You" row highlighted purple, points yellow ★
- Tier starburst: purple multi-point SVG

---

## 6. Dark mode

| | Light | Dark |
|---|---|---|
| Background | `#FFEFD7` | `#1B161B` |
| Surface | `#FFFFFF` | `#2A222A` |
| Text | `#29261B` | `#FFF7ED` |
| Border | `#000000` | `#FFF7ED` (cream!) |

**Key rule:** black outline → cream outline in dark mode.

---

## 7. Do / Don't

**Do:** outline everything · zero-blur hard shadows · School Times for loud text · six canonical colors · gamification everywhere · EN/SI/TA first-class.

**Don't:** soft/blurred Material shadows · gradients or new hues · unstyled Material widgets · freehand illustration (use geometric sticker kit) · overuse emoji.

---

## 8. Accessibility & motion (non-negotiable, both surfaces)

**Touch targets & feedback**
- Every tappable control ≥44×44pt (`ComponentSizes.minTouchTarget` in Flutter). Icon-only circle buttons below that size get their *hit area* expanded without growing the visible circle — see `MeritCircleOutlineButton` in `merit_circle_button.dart` for the pattern.
- Every tap gets visible feedback (`InkWell` ripple, not a bare `GestureDetector` with no state change). `MeritTouchable` (press-opacity) is an accepted neo-brutalist alternative to ripple.
- Icon-only controls (back/close/more, theme toggle, burger menu) need a `Semantics`/`aria-label` — a visual icon is not an accessible name.

**Reduced motion**
- Any animation that loops or auto-plays without user interaction (confetti, ticker, spinning decorations, pulsing hints) must check the platform's reduced-motion flag and skip or become static. Flutter: `context.isReducedMotionEnabled` (`build_context_extension.dart`). Web: `@media (prefers-reduced-motion: reduce)`.
- Short (150–300ms) tap/press micro-interactions are exempt — those aren't the pattern reduced-motion targets.

**Dynamic type / text scale**
- Don't pin `textScaleFactor`/`textScaler` to `1` except where required by a rendering constraint (e.g. LaTeX layout in `latex_text.dart`) — document the exception inline when you do.
- Fixed-height chrome (tab bars, pill buttons) should tolerate the app's clamped max text scale (see `main.dart` `MediaQuery` override) without clipping.

**Color tokens in dark mode**
- Never hardcode `#000000` borders on a component that also has a dark-mode variant — use `MeritBorders.resolve(context)` / the `--line` → cream swap (§6). A literal black border you forgot to flip is invisible on an ink background.
