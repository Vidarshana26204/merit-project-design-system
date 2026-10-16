# Fonts

| Family | Licence | In git? | Use |
|---|---|---|---|
| **General Sans** (Medium, Semibold, Bold + italics) | ITF Free Font License (Fontshare) | **No**, gitignored | v3 display face (D8) and wordmark (D13) |
| Plus Jakarta Sans | SIL OFL 1.1 | Yes | Body |
| Clash Display | ITF Free Font License (Fontshare) | Yes (v2, legacy). See the note below | v2 display face only |
| School Times | Check its licence | Yes (v2, legacy) | v2 landing only. Retired in v3 (D13) |

## Getting General Sans locally

The ITF Free Font License allows self-hosting on your own sites and embedding in your own
apps. It **forbids redistribution**, and that explicitly includes a "repository" or a
"publicly accessible server". This repo is public, so the files stay out of git.

1. Download the family from <https://www.fontshare.com/fonts/general-sans>.
2. From `Fonts/WEB/fonts/`, copy these into this folder as both `.ttf` and `.woff2`:
   `GeneralSans-{Medium,Semibold,Bold,MediumItalic,SemiboldItalic,BoldItalic}`.

`scripts/brand/build_v3_brand.py` needs the `.ttf` files to outline the wordmark. The
reference site loads the local `.woff2` files and falls back to the Fontshare CDN when they
are missing.

The apps bundle their own copies. Flutter puts them in `assets/google_fonts/` (a private repo,
embedded in the app, which the licence allows). The web frontend self-hosts them from its
deployment.

> **Open issue:** the v2 Clash Display (FFL) files are committed to this public repo and are in
> its history. Before v3 ships, decide whether to make the repo private or to remove them.
