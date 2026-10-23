"""Round 12 landing frames: the low-poly Quilt Map concept (live) and the hero (desktop tree, phone without it).
Must not import gen_web_board (circular)."""
from gen_web import *  # noqa: F401,F403

CAP = ('<p class="qm-cap">Live prototype: click a subject (or Enter), then a topic. Esc or the breadcrumb goes back. '
       'Stream chips switch the tree. Grows on load, then sways; the coin runs until your first interaction.</p>')
live_lp = f'<div class="qm-wrap"><div data-qm="lowpoly" data-stream="al-science"></div>{CAP}</div>'

SPEC_LP = (
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

SPEC_ICO = (
    "<b>Scene.</b> Projected 3D in SVG (no three.js) + GSAP. Design space 640 x 600 (16:9 stage: 1067 x 600 with the tree shifted right 427). The tree fills the frame: crown top at about 8% of the height, trunk base (410, 538), fork (352, 420); the trunk leans left towards the copy, forks into 3 to 4 angular branches, and stands on a grass hill. No card: the sky is the page background. "
    "<b>Projector.</b> Vertices are rotated by yaw then pitch about the crown pivot (330, 250) and perspective-projected (focal length 900). Back faces are culled (face normal against the vector to the camera); faces are painter-sorted by view depth, and so are whole objects (bark gets a 40 unit bias behind balls). "
    "<b>Shading.</b> Lambert against a key light from the top left, view-space (-0.5, -0.65, 0.58), quantised to 5 tones: lit < 0.2, 0.4, 0.6, 0.8, then brighter. Tone mixes of the ball's base colour: 30% black, 16% black, base, 20% white, 38% white (dark theme: 15% black, base, 12%, 26%, 44% white). "
    "<b>Crown mass.</b> One dense silhouette of icospheres (subdivision 0, 20 faces, about 10 visible, vertex radius jittered 0.9 to 1.1 so they look chunky). Six interactive balls r 90 to 102 sit in fixed slots whose neighbours overlap 25 to 40% and are layered in depth (z from -10 to +45); a smaller \"+N more\" ball (r 60) tops the crown; 3 to 5 decorative balls (r 58 to 90, z -70 to -90) fill the gaps behind (aria-hidden, no pointer events). Slots fill in the order that keeps the mass connected. "
    "<b>Palette</b> (dedicated vars <code>--qm-leaf-1..5</code>, not the grey sage tokens): <code>#1F7A4D #2FA35C #49C26B #8FD86A #C9E36B</code>, one per ball by hash; dark theme <code>#176339 #228247 #37A056 #6EB454 #A5BC55</code> (deeper, less luminous). Bark <code>--qm-bark #7A4A2A</code> with shadow faces <code>--qm-bark-dark #4E2E1A</code>, 5 tones. Grass gradient <code>#8FD86A</code> to <code>#2FA35C</code> (dark <code>#5FA83D</code> to <code>#1D7A47</code>). The hover tint to the subject colour is kept (0.35 s transition on the base colour, tones re-derived live). "
    "<b>Bark.</b> Tapered hexagonal prisms with a kink: trunk 28 to 15 units wide in 3 rings, branches 13 to 6 reaching into the crown. "
    "<b>Hill.</b> A grass mound over the right 60% of the stage, crest 16% of the height, with 14 low-poly tufts in front of the trunk base. "
    "<b>Items.</b> At most 6 interactive balls per level: subjects in data order, topics ranked by exam share (<code>x</code>) descending; with more, the \"+N more\" ball opens the full list in the panel (production: the Subjects page). "
    "<b>Labels.</b> Default: white bold text (15 units, about 15 px on screen at 1280) with a soft dark drop shadow, centred on the ball's lower face, no pill, 2 lines (3 only for names over 40 characters); long titles use short forms (ICT, Agri Science, Combined Maths...); labels live in one top layer and are nudged apart. On hover or focus a surface pill with a focus ring appears under the text. \"+N more\" keeps a small pill. "
    "<b>Interaction.</b> A ball is <code>&lt;g role=\"button\" tabindex=\"0\" aria-label=\"Physics, 11 topics\"&gt;</code>. "
    "<b>Recursion.</b> The trunk is the stream. Click or Enter on a subject: the camera (viewBox) tweens 0.65 s <code>power3.inOut</code> to the ball (5.2 x its radius wide); at 0.4 s its visible facets scatter 70 units outward with a random spin and fade (0.65 s, <code>power2.out</code>); at 0.75 s a new tree at 0.42 scale grows from the ball's centre, built from the subject's top 6 topics + \"+N more\" (same 1.8 s timeline, no hill or sign); at 1.3 s the camera eases 0.7 s to fit the new tree, offset to leave room for the panel (tree right of centre in the 16:9 concept where the panel is top-left; tree left and low in the hero where the panel is top-right), and the old tree fades to 5% opacity. A topic is the last level: the ball pulses (1.14, 0.2 s, yoyo) and the qm.js panel opens with counts, exam share and CTA \"Start practising X\" to sign-up with the subject. The breadcrumb (rings) and Esc go up one level: the child fades, the camera returns, the facets fly back together (0.5 s), then the camera returns home. Stream chips swap the root tree. "
    "<b>Sign.</b> \"Start here\": a plank (92 x 31 x 8, text centred) hanging 118 units below a long lower-left branch (257 units, reaching out into open sky toward the copy) on two parallel, near-vertical ropes from two points one plank width apart (never crossed), a real <code>&lt;a href=\"#\" aria-label=\"Start here, open sign-up\"&gt;</code> (production: sign-up) with a focus ring, swinging +/-5 degrees about the rope anchor, <code>sine.inOut</code>, 1.7 s per half cycle. "
    "<b>Motion.</b> Grow on load, about 1.8 s (<code>power2.out</code>): the hill fades in 0 to 0.45 s, the trunk extrudes (scaleY from the base) 0.25 to 0.8 s, branches extend from the fork at 0.65 s (70 ms apart), balls pop with <code>back.out(1.8)</code> from 0.95 s, 60 ms apart ordered by distance from the fork, labels fade in, and the sign drops in on its ropes at 1.35 s. Idle: balls bob +/-2 units, 2.2 to 3.6 s, phase from the hash; every ~8 s a gust spins each ball up to 0.2 rad, staggered left to right (a ripple across the crown). Parallax: the whole scene yaws +/-6 degrees and pitches +/-3 degrees following the pointer, eased 0.9 s. One render loop, re-projecting only when something changed. "
    "<b>Reduced motion:</b> finished and still: no parallax, no bob, swing or gust; the camera and the recursion jump."
)

CAP_ICO = ('<p class="qm-cap">Live prototype: hover or Tab to a ball, click or Enter to open it (it shatters into a new tree of topics). Esc or the breadcrumb goes back. '
           'Stream chips switch the tree. Move the pointer over the stage for parallax.</p>')
live_ico = f'<div class="qm-wrap"><div class="qm ico ico-stage" data-qm="ico" data-wide data-stream="al-science"></div>{CAP_ICO}</div>'

concept = screen("web-quilt-concept", "Quilt Map · icosphere tree vs low-poly tree (live)", [("energy", "Energy"), ("gap", "Pick one")],
    "Two takes on the picked tree, both live on a snapshot of <code>GET /public/explore</code> (A/L Science: 6 subjects; Combined Mathematics has no topics yet, so it is muted). "
    "A is the new round 12b direction: a Blender-style low-poly tree on a hill with chunky icosphere foliage, a hanging \"Start here\" sign and the fractal recursion you liked (a subject ball shatters and a smaller tree of its topics grows from it). "
    "B is the round 12a faceted tree, kept for comparison. Please say which one to take forward. Try both in light and dark. <br><br><b>A. Spec.</b> " + SPEC_ICO + "<br><br><b>B. Spec.</b> " + SPEC_LP,
    "GET /public/explore?lang= · CTA → /student/sign-up?subject=&lt;id&gt;",
    [cand("A", "Icosphere tree on a hill (12b)", "New", live_ico,
          "Picked direction from the reference: reads as a tree and a place, the sign is the one clear first action, and the recursion keeps the big picture (stream, subject, topic). Interactive balls take their subject colour on hover, so the green crown stays calm until you look at it.",
          "Needs the small projector (about 300 lines) instead of flat SVG; Arts (25 subjects) shows only 6 balls + \"+19 more\".",
          "<code>3D projector</code><code>Lambert 5 tones</code><code>hex prism bark</code><code>GSAP grow + parallax</code><code>shatter + regrow</code>",
          pick=False),
     cand("B", "Low-poly tree (12a)", "Comparison", live_lp,
          "The previous round: a faceted trunk with a sage crown and a subject-coloured patch per subject, zoom by camera.",
          "Flatter and busier than A; no sign or hill.", "<code>Delaunator canopy</code><code>viewBox camera</code>", pick=False)])

# ---- hero: A desktop (tree right) and phone (no tree)
hero_ico = dk("meritproject.lk", lnav() + f'''
<div class="w-hero ico-a"><div class="ico-copy st" style="gap:18px">{HERO_COPY}
<div class="rw"><button class="btn l" type="button">Start free</button><button class="btn gh l" type="button">{I("play-circle")}How it works</button></div>
<div class="rw xs t3" style="gap:14px"><span>62 subjects</span><span>·</span><span>Official past papers since 2012</span><span>·</span><span>Free forever</span></div>
<div class="ico-chips" id="r12-hero-chips"></div></div>
<div class="qm ico r12-hero-ico" data-qm="ico" data-stream="al-science" data-chips-in="#r12-hero-chips"></div></div>''')

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
    "Hero A is picked: copy left and vertically centred, the icosphere tree in the right half, anchored to the bottom-right corner with its hill bleeding off the frame and the crown leaning toward the copy. No card: the sky is the hero background. The tree is fully interactive here (the stream chips are one compact row in the copy column under the meta line, still wired to the tree; the breadcrumb shows only once you drill in, top-left of the tree area; the topic panel anchors top-right inside the tree area so it never covers the copy). The \"Start here\" sign is the hero's second CTA. On mobile web the tree is not shown at all: copy, CTA, stream chips, then a 3-up grid of subject tiles (patchwork), no sideways scroll; a tile opens sign-up with that subject.",
    "GET /public/explore?lang= · streams → subjects (counts, patchwork)",
    [cand("A", "Copy left, icosphere tree right", "Picked", hero_ico,
          "Reads like a classic hero with a living illustration. The tree uses the right 54%, fills about 85% of the hero height and fits a 1280 laptop without scrolling; at 1024 it scales with its column.",
          "", "<code>wordmark nav</code><code>display + brush underline</code><code>icosphere tree 640</code><code>stream chips under the copy</code>", pick=False),
     cand("M", "Phone web: no tree", "Picked", f'<div class="wf-vars-phone" style="display:grid;place-items:center">{hero_phone}</div>',
          "The map needs room to be legible, so phones get the same job as plain tiles: choose a stream, tap a subject.",
          "", "<code>copy</code><code>CTA</code><code>stream chips</code><code>3-up patchwork tile()</code>", pick=False)])
