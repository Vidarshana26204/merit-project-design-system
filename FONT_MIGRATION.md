# Font Migration: Clash Display → School Times

## Summary

The display/heading typeface across Merit Project has been swapped from **Clash Display** to **School Times** (Khurasan, 2019). Body text (**Plus Jakarta Sans**) is untouched.

| Role | Before | After |
|---|---|---|
| Display / headings / buttons / stat figures | Clash Display (weights 500/600/700) | School Times (weight 400 only) |
| Body / long-form copy | Plus Jakarta Sans | Plus Jakarta Sans (unchanged) |

## The single-weight constraint

School Times ships **one weight — Regular — with no bold, medium, or italic variants**. Flutter and CSS can't synthesize a fake bold from a single font file, so:

- The same `SchoolTimes-Regular` file is registered under all four weight slots (400/500/600/700) in `pubspec.yaml` and via `font-weight:400 700` range in `@font-face` rules. This means `FontWeight.w700` calls resolve to School Times itself rather than silently falling back to a system font — but it will **always render visually as Regular**, not bold.
- Heading hierarchy that used to rely partly on weight now relies entirely on size, letter-spacing, and color. No code changes were made to existing `FontWeight` values — they were left as-is since they still resolve correctly and cost nothing to keep.

## Licensing — action required

School Times is a **commercial font by Khurasan** (`contact: khurasantype@gmail.com`, `www.khurasan.net`), not an open-source/OFL font like the Google Fonts it replaced. Before shipping this to production or the app stores, confirm the license you have covers your intended use (commercial app distribution, embedding in web assets, number of installs/seats, etc.) — check `Read me please.pdf` / `More Info.txt` in the original download, or contact Khurasan directly. Do not treat this the same as the previous Google Fonts (OFL) setup.

## Files changed

### `merit-project-flutter/`
- `assets/google_fonts/SchoolTimes-Regular.ttf` — new font asset
- `assets/google_fonts/ClashDisplay-{Medium,SemiBold,Bold}.ttf` — removed
- `assets/google_fonts/Nunito-*.ttf` (20 files), `OFL.txt`, `README.txt` — removed (bundled but never registered in `pubspec.yaml` or referenced in code; dead weight unrelated to this migration but cleaned up alongside it)
- `pubspec.yaml` — `ClashDisplay` font family block replaced with `SchoolTimes` (all 4 weight slots point at the same file)
- `lib/theme/merit_theme.dart` — `MeritTypography.displayFontFamily` changed from `'ClashDisplay'` to `'SchoolTimes'`; this is the single source of truth for the display font and propagates to every `TextStyle` built from it. In-file comments referencing "Clash Display" updated for accuracy.
- `lib/main.dart` — removed the `LicenseRegistry.addLicense` block that loaded `google_fonts/OFL.txt` (that file belonged to Nunito, which is now removed; loading it would have crashed at startup on a missing asset). Also dropped the now-unused `flutter/foundation.dart` import this left behind.

No other Flutter file references the font family by literal string — everywhere else uses the `MeritTypography.displayFontFamily` constant, so the single edit above covers all ~39 files that render display text.

### `merit-project-backend/`
- `web/static/fonts/SchoolTimes-Regular.otf` — new self-hosted font asset, served via the existing `/static` route (`server.go`)
- `internal/web/templates/layout.templ` — removed the Fontshare `<link>` (Clash Display isn't self-hostable via a free CDN the way it was set up); added a `@font-face` rule pointing at the new self-hosted file; every `font-family:'Clash Display'` occurrence (30 of them) replaced with `'School Times'`. Plus Jakarta Sans's Google Fonts `<link>` is untouched.
- `internal/web/templates/components/community.templ` — same replacement (1 occurrence)
- `internal/web/templates/layout_templ.go`, `internal/web/templates/components/community_templ.go` — regenerated via `make templ`

### `merit-design-system/` (reference doc, kept in sync)
- `assets/fonts/SchoolTimes-Regular.ttf` — new font asset
- `merit-ds.css` — `--font-display` token updated; `@font-face` rule added
- `Merit Design System.html` — Fontshare `<link>` replaced with a local `@font-face`; all prose/code-sample mentions of Clash Display updated to School Times, including the type-scale specimens (weight labels corrected from 700/800 to 400, since there's no bold)
- `SKILL.md` — typography table, Flutter code sample (`MeritType.display` renamed to `MeritType.schoolTimes` — `display` was already taken as a field name, so this avoids a naming collision in the sample) updated to match

## Regenerating derived artifacts

If you touch `layout.templ` or `community.templ` again, regenerate the Go output with:

```bash
cd merit-project-backend
make templ
```

## Verification performed

- `fvm flutter pub get` — succeeds, new font block is valid
- `fvm flutter analyze` — no new issues (pre-existing unrelated lints only)
- `go build ./...` (backend) — succeeds
- Grep sweep for `ClashDisplay|Clash Display|clash-display` across all three trees — zero hits
- Rendered `Layout()` via a throwaway Go test — confirmed `School Times` present and `Clash Display` absent in the generated HTML

## Not yet done (needs a running local stack)

Visual verification in a browser/simulator wasn't performed in this pass — that needs the Postgres/Redis/Typesense stack up (`docker-compose up -d`) plus `go run main.go` for the landing page, and `fvm flutter run` for the app. Load a headings-heavy screen (home, subject detail, landing page hero) and confirm School Times renders and Plus Jakarta Sans body text is unaffected.
