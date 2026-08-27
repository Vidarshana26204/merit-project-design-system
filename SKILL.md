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

| Token | Hex | Role |
|---|---|---|
| **Purple** | `#8E55D7` | Primary — main actions, brand, active states |
| **Purple Deep** | `#6E36B8` | Primary pressed / deep shade |
| **Yellow** | `#FFCC00` | Accent — highlights, XP, rewards, secondary CTA |
| **Mint** | `#9ED5B7` | Support — success, "done", positive stats |
| **Cream** | `#FFEFD7` | Surface — light background, soft cards |
| **Ink** | `#312A31` | Charcoal — primary text, dark cards |
| **Ink-2** | `#1B161B` | Darkest — dark-mode background |
| **White** | `#FFFFFF` | Base surface |
| **Line / Border** | `#000000` | The black outline on *everything* |

### Extended palette (mobile app only)

| Token | Hex | Use |
|---|---|---|
| Yellow (soft) | `#F2D43B` | App accent fills where `#FFCC00` is too hot |
| Mint (soft) | `#9CE7C8` | App success / category |
| Pink | `#FFB3C8` | Category accent (e.g. Arts, Biology) |
| Blue | `#B3D8FF` | Category accent (e.g. Technology, ICT) |
| Cream (warm) | `#FFF7ED` | App surface-2 / page background |
| Text | `#29261B` | App body text |
| Text Dim | `#5A4A5A` | Secondary text |
| Text Mute | `#7A6C7A` | Tertiary / captions / placeholders |

### Flutter — `MeritColors`

```dart
import 'package:flutter/material.dart';

abstract final class MeritColors {
  static const purple     = Color(0xFF8E55D7);
  static const purpleDeep = Color(0xFF6E36B8);
  static const yellow     = Color(0xFFFFCC00);
  static const mint       = Color(0xFF9ED5B7);
  static const cream      = Color(0xFFFFEFD7);
  static const ink        = Color(0xFF312A31);
  static const ink2       = Color(0xFF1B161B);
  static const white      = Color(0xFFFFFFFF);
  static const line       = Color(0xFF000000);
  static const yellowSoft = Color(0xFFF2D43B);
  static const mintSoft   = Color(0xFF9CE7C8);
  static const pink       = Color(0xFFFFB3C8);
  static const blue       = Color(0xFFB3D8FF);
  static const creamWarm  = Color(0xFFFFF7ED);
  static const text     = Color(0xFF29261B);
  static const textDim  = Color(0xFF5A4A5A);
  static const textMute = Color(0xFF7A6C7A);
}
```

---

## 3. Typography

| Family | Where | Weights | Tracking |
|---|---|---|---|
| **Clash Display** | All headings, numbers, buttons, stat figures, labels-as-display | 500–800 | tight: `-0.02em` (display down to `-0.04em`) |
| **Plus Jakarta Sans** | Body copy, descriptions, form values, fine print | 400–700 | normal |

### Flutter typography

```dart
class MeritType {
  static const display = 'ClashDisplay';
  static TextStyle clash(double size, {FontWeight w = FontWeight.w700, Color? c}) =>
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
- Streak chip: white pill, 🔥 {n}, Clash 800
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

**Do:** outline everything · zero-blur hard shadows · Clash Display for loud text · six canonical colors · gamification everywhere · EN/SI/TA first-class.

**Don't:** soft/blurred Material shadows · gradients or new hues · unstyled Material widgets · freehand illustration (use geometric sticker kit) · overuse emoji.

---

## 8. Web / shadcn mapping (merit-project-frontend)

Added when the unified web frontend (`merit-project-frontend`) needed these
tokens expressed as shadcn/Tailwind v4 CSS variables. Applied in
`app/globals.css` — shadcn variable names are kept unprefixed so every
`components/ui/*` primitive restyles automatically; the raw merit-ds values
are also exposed as `--merit-*` for direct use outside the shadcn mapping.

| shadcn var | Light | Dark | merit-ds source |
|---|---|---|---|
| `--background` | `#FFEFD7` (cream) | `#1B161B` (ink-2) | `--bg` |
| `--card` / `--popover` | `#FFFFFF` | `#2A222A` | `--surface` |
| `--foreground` | `#29261B` | `#FFF7ED` | `--text` |
| `--primary` | `#8E55D7` (purple) | same | `--purple` |
| `--secondary` | `#9ED5B7` (mint) | `#9CE7C8` (mint-soft) | `--mint` |
| `--muted` | `#FFF7ED` (cream-warm) | `#241D24` | `--surface-2` |
| `--accent` | `#FFCC00` (yellow) | same | `--yellow` |
| `--destructive` | `#C4393A` | same | Flutter `MeritColors.error` (not yet in merit-ds.css root tokens — carried over from the mobile app for consistency) |
| `--border` / `--input` | `#000000` | `#FFF7ED` | `--line` (dark-mode flip is merit-ds.css's own rule) |
| `--radius` | `1.125rem` (18px) | same | §4 "Radius — card" |
| `--chart-1..5` | purple/yellow/mint/pink/blue | same | categorical accent set |

**Fonts:** Plus Jakarta Sans (body) and JetBrains Mono load via
`next/font/google` as `--font-merit-sans` / `--font-merit-mono`. **Clash
Display is not on Google Fonts** — self-hosting it (Fontshare license
permitting) is a follow-up; headings currently fall back to Plus Jakarta
Sans at weight 700 with tightened tracking.

**Known gaps, follow-up work:**
- Component border-width (2px per §4) isn't retrofitted onto every
  `components/ui/*` primitive yet — only the CSS variable color is mapped.
  Hard-offset shadows (§4) aren't applied to shadcn cards/buttons either.
- No square favicon/app-icon asset exists yet — `assets/logo.png` is a
  1536×1024 wordmark, not favicon-shaped.
- This section covers step 1 (setup + skeletons) of the frontend unification
  only. Full component-level parity with §5 (buttons/cards/inputs/pills/
  progress/toggles/tab bar) lands as the real admin/student/contributor UI
  gets built in later phases.
