"""Round 12 landing frames: the low-poly Quilt Map concept (live) and the hero (desktop tree, phone without it).
Must not import gen_web_board (circular)."""
from gen_web import *  # noqa: F401,F403

CAP = ('<p class="qm-cap">Live prototype: click a subject (or Enter), then a topic. Esc or the breadcrumb goes back. '
       'Stream chips switch the tree. Grows on load, then sways; the coin runs until your first interaction.</p>')
live_lp = f'<div class="qm-wrap"><div data-qm="lowpoly" data-stream="al-science"></div>{CAP}</div>'

SPEC = (
    "<b>Build.</b> 2.5D SVG + GSAP; every facet is a real <code>&lt;polygon&gt;</code>. Stage viewBox 800 x 700, trunk base (400, 598); the home camera is fitted to the real crown facet bounds, every cluster and the ground, +24 units padding and a 6 unit sway margin (plus room for the chips in the interactive mount), so the tree fills its column (about 560 x 490 in the hero). "
    "Layout is deterministic (FNV-1a hash of node ids; <code>grow()</code> ported from the picked tree): trunk 140 units, branches 130 x 0.82 per level, tips relaxed to at least 0.78 x cluster diameter apart (so clusters overlap). "
    "<b>Trunk and roots.</b> 44 wide at the base tapering to 15 at the first fork, plus 4 short root triangles spreading 26 to 50 units along the ground. "
    "<b>Branches.</b> 15 x 0.68<sup>depth-1</sup> wide (min 2.4), each a strip of 5 steps x 2 triangles with an S-bend of up to 6% of its length, plus 2 to 3 decorative twigs (1 on thin ones), thin triangles 11 to 22 long. Bark is warm brown, <code>orange-700 50% / ink-700</code> then 74% over <code>sand-300</code>, in 4 tones by facing (black 22% to white 34%). Twigs and bark are <code>aria-hidden</code>. "
    "<b>Crown.</b> One decorative foliage hull behind the bark, a domed cloud: bottom 0.9 R below the lowest tip, half-width = spread/2 + 0.5 R (the rim runs through the outer clusters), half-height at least 0.62 x half-width (it grows upward, never below the bottom). The outline has 4 and 7 lobe bulges (+/-9% and 5%) and an underside that rises about 34% towards the trunk, so sky shows between the crown and the branches; the bounds are about 1.9:1. 30 rim + 20 + 10 inner points + a crown point, triangulated with Delaunator into about 100 facets; <code>aria-hidden</code>, no pointer events. Sage ramp (<code>sage-500 62% / sage-700</code>), same six-tone light model but lower contrast (82% black to 75% white); dark theme uses <code>sage-700 / sage-900</code> lifted towards <code>sage-500</code>. "
    "<b>Subject clusters</b> sit in the crown and overlap its edge, as subject-coloured patches (the quilt nod): radius R = 1.3 x clamp(72 - 2.2n, 27, 62). Points: 12 outer (0.8 to 1.14 R, 1.12 wide), 8 mid ring (0.4 to 0.6 R) and a crown point, dome height up to 0.98 R; Delaunator gives about 28 to 32 facets. "
    "<b>Shading.</b> Facet normal from the 3D triangle dotted with a light from the top left (-0.55, -0.65, 0.5), plus +/-0.08 jitter, quantised to six tones at -0.05, 0.2, 0.4, 0.6, 0.8. Subject cluster colour: <code>subject 76% black</code> darkest, the subject colour in the middle, <code>subject 52% white</code> lightest (dark theme lifts the shadows: 90% black to 46% white). A subject with no topics uses 20% of its colour over <code>--merit-text-tertiary</code>, saturate(.5), and \"coming soon\" in its aria-label. "
    "<b>Labels.</b> Never clipped: long titles use short forms (ICT, Agri Science, Combined Maths, Media Studies...), then wrap onto as many lines as needed (11 characters per line for subjects, 12 for topics). All pills are drawn in one top layer after every cluster (also at topic level), so no cluster covers a label; overlapping pills are nudged down until clear. Pills (surface, 1.2 border, 17.5 px bold) sit just below the cluster centre toward its lower edge, and scale with the camera zoom so they stay about 12 to 14 px on screen. Streams with more than 12 subjects (Arts) show the label on hover or focus only. "
    "<b>Grow on load, about 1.8 s</b> (one GSAP timeline, <code>power2.out</code>): trunk <code>scaleY</code> 0 to 1 from the base, 0 to 0.5 s; branches scale 0 to 1 from their start point, 0.34 s each, depth d starting at 0.3 + 0.1 d; crown facets pop (<code>back.out(1.7)</code>, 0.3 s, 6 ms stagger, centre outward) from 0.8 s; then each subject cluster pops its facets (8 ms stagger) from 1.3 to 1.4 s by hash, its label fading in 0.3 s later. "
    "<b>Idle.</b> Each cluster sways +/-1 degree about a point 0.9 R below its centre, <code>sine.inOut</code>, 3 to 5.2 s per half cycle, phase from the hash of its id. The coin tour: every ~6 s a butter coin travels the branches to the Physics tip over 1.7 s (<code>sine.inOut</code>), the cluster bumps to 1.07, and \"+10\" rises 26 units and fades in 1 s; it stops for good at the first pointer, key or focus event. "
    "<b>Interaction.</b> Each cluster is <code>&lt;g role=\"button\" tabindex=\"0\" aria-label=\"Physics, 11 topics\"&gt;</code>; click or Enter/Space opens it. The camera (viewBox) tweens 0.8 s <code>power3.inOut</code> to a box fitting the new sub-tree; the crown, trunk, other subjects and the home branches fade out (the crown to 0, the rest to 10 to 18%, and they leave the tab order), the subject cluster shrinks to 0.4 and fades (0.45 s) while its topic sub-branches (bark coloured, with twigs; only the tip clusters carry the subject tint) grow out of the tip (0.3 s each) and one smaller cluster per topic (R = 36 - 0.7n, 21 to 31) pops in, 30 ms apart. Clicking a topic dims the others to 30%, rings the chosen one and fills the panel: counts, exam share, CTA \"Start practising X\" to sign-up with the subject. Esc or the breadcrumb reverses it (the crown grows back in place). "
    "<b>Reduced motion:</b> final state instantly, no sway, no coin, camera jumps. Lenis is production smooth scroll only; it is not used here."
)

concept = screen("web-quilt-concept", "Quilt Map · low-poly tree (live)", [("energy", "Energy"), ("gap", "Refined")],
    "The tree you picked in round 11, now low-poly: a faceted trunk and branches, a canopy cluster per subject, real data from a snapshot of <code>GET /public/explore</code> "
    "(A/L Science: 6 subjects; Combined Mathematics has no topics yet, so it is a muted \"coming soon\" cluster). Try it in both themes. <br><br>" + SPEC,
    "GET /public/explore?lang= · CTA → /student/sign-up?subject=&lt;id&gt;",
    [cand("A", "Low-poly tree", "Picked", live_lp,
          "Picked in round 11; refined. Reads as a tree at a glance (trunk, branches, canopy), keeps one DOM node per facet so focus, labels and tests work, and costs about 450 polygons on the first level (crown 100, 6 clusters x 30, bark and twigs).",
          "Streams with 25 subjects (Arts) get tiny clusters with hover labels; check them with the Arts chip.",
          "<code>Delaunator canopy</code><code>normal vs light shading</code><code>GSAP grow + sway</code><code>viewBox camera</code><code>pure layout fn</code>",
          pick=False)])

# ---- hero: A desktop (tree right) and phone (no tree)
hero_lp = dk("meritproject.lk", lnav() + f'''
<div class="w-hero lp-a"><div class="st" style="gap:18px;max-width:440px">{HERO_COPY}
<div class="rw"><button class="btn l" type="button">Start free</button><button class="btn gh l" type="button">{I("play-circle")}How it works</button></div>
<div class="rw xs t3" style="gap:14px"><span>62 subjects</span><span>·</span><span>Official past papers since 2012</span><span>·</span><span>Free forever</span></div></div>
<div class="st" style="align-items:center;gap:10px"><div class="qm qm-slot r12-hero-map" data-qm="lowpoly" data-stream="al-science" data-static data-grow></div>{STREAMS}</div></div>''')

TILES = [("Physics", "physics", "11 topics"), ("Chemistry", "chemistry", "14 topics"), ("Biology", "biology", "10 topics"),
         ("Agri. Science", "plants", "17 topics"), ("ICT", "ict", "14 topics"), ("Comb. Maths", "maths", "Soon")]
tiles = "".join(f'<div class="t">{tile(n, 64)}<span>{lab}</span><em>{m}</em></div>' for lab, n, m in TILES)
hero_phone = phone(
    '<div class="r12-phone"><div class="rw"><span class="wmk sm2">MERIT<b>.</b></span><span class="sp"></span><a class="lnk">Sign in</a></div>'
    '<span class="ey">O/L &amp; A/L · Sinhala · Tamil · English</span>'
    '<div class="h-lg">Every subject you sit, <span class="ul">stitched</span> together.</div>'
    '<span class="sm t2">Past papers, flashcards and notes for the Sri Lankan syllabus.</span>'
    '<button class="btn l full" type="button">Start free</button>'
    '<div class="chips"><span class="chip on">A/L Science</span><span class="chip">Commerce</span><span class="chip">Arts</span><span class="chip">Technology</span><span class="chip">O/L</span></div>'
    f'<div class="r12-tiles">{tiles}</div><span class="xs t3" style="text-align:center">Tap a subject to start with it</span></div>', 780)

s_hero = screen("web-hero", "Landing hero · copy left, tree right", [("energy", "Energy"), ("gap", "Picked")],
    "Hero A is picked: the promise and CTA first, the low-poly tree as proof, about 45% of the width. The tree grows on load and sways; it is a display here (<code>data-static data-grow</code>), "
    "the interactive version is on the Quilt Map tab. On mobile web the tree is not shown at all: copy, CTA, stream chips, then a 3-up grid of subject tiles (patchwork), no sideways scroll; a tile opens sign-up with that subject.",
    "GET /public/explore?lang= · streams → subjects (counts, patchwork)",
    [cand("A", "Copy left, tree right", "Picked", hero_lp,
          "Reads like a classic hero. The tree fits a 1280 laptop without scrolling and stays inside its column at 1024.",
          "", "<code>wordmark nav</code><code>display + brush underline</code><code>low-poly tree 560</code><code>stream chips</code>", pick=False),
     cand("M", "Phone web: no tree", "Picked", f'<div class="wf-vars-phone" style="display:grid;place-items:center">{hero_phone}</div>',
          "The map needs room to be legible, so phones get the same job as plain tiles: choose a stream, tap a subject.",
          "", "<code>copy</code><code>CTA</code><code>stream chips</code><code>3-up patchwork tile()</code>", pick=False)])
