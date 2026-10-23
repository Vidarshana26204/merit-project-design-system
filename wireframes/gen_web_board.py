"""Build wireframes-web.html (the Merit web wireframes board).

Usage (from the design-system repo root):
    python3 wireframes/gen_web_board.py > wireframes-web.html

Reuses the frame helpers and round 11 frames from gen_web.py and adds the remaining tabs, so the web
board mirrors the mobile board's flows. The landing's Quilt Map concepts are live prototypes
(wireframes/qm.js, qm-tree.js, data in qm-data.js).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_web import *  # noqa: F401,F403  (frames, helpers, round 11 screens)


# ------------------------------------------------------------------ 00 Landing: Quilt Map concepts (live)
def live(kind):
    return f'<div class="qm-wrap"><div data-qm="{kind}" data-stream="al-science"></div><p class="qm-cap">Live prototype: click a subject, then a topic. Esc or the breadcrumb goes back. Stream chips switch the tree.</p></div>'


concept = screen("web-quilt-concept", "Quilt Map · concept (live prototypes)", [("energy", "Energy"), ("gap", "Pick one")],
    "Three ways to explore the real syllabus, all running on a snapshot of <code>GET /public/explore</code> (A/L Science: 6 subjects, real topic counts and exam shares; Combined Maths has no topics yet, so it shows \"coming soon\"). Every layout is deterministic: node ids are hashed, so a subject always looks the same. Reduced motion swaps every transition for an instant cut.",
    "GET /public/explore?lang= · CTA → /student/sign-up?subject=&lt;id&gt;",
    [cand("A", "Fractal tree", "Wild", live("tree"),
          "Your idea 1. The Merit mark is the root; each click flies the camera to a tip, which becomes the new root while a new tree grows (branches draw from the root, tips pop in). Branch colour flows from ink into each subject's colour, so the crown reads as the stream's palette. It tells the story of growing from one root into a whole syllabus.",
          "Wide levels (14+ topics) make a dense crown; tips are pushed apart and labels wrap to two lines, but 20+ items need the \"+N more\" fallback. Most build effort of the three (layout + grow/zoom choreography).",
          "<code>tree layout (pure fn)</code><code>grow: stroke-dashoffset</code><code>zoom: camera tween</code><code>plate root (D16 sides)</code>"),
     cand("B", "Circuit network", "Bold", live("net"),
          "Your idea 2, after the reference: a hexagon hub with nodes on circuit-style elbow wires, solder dots and decorative stubs (circles, triangles, squares, dash pairs). The clicked node travels to the centre and becomes the hub, then its children fly out along new wires. The hub's plate shape says the level: hexagon for Merit, square for a subject, pentagon for a topic.",
          "Reads more \"tech\" than \"quilt\"; decorative stubs must stay muted so they never look clickable.",
          "<code>scatter + relax layout</code><code>elbow wires (0°/45°)</code><code>hub morph</code><code>deco stubs</code>"),
     cand("C", "Orbit (round 11)", "Safe", live("orbit"),
          "The round 11 idea, now clickable for comparison: an even ring on dotted connectors around a hub, same hub-swap transition as B.",
          "Calm and clear, but the least memorable of the three.",
          "<code>ring layout</code><code>dotted connectors</code><code>hub swap</code>")])

phones = kit_screen("web-quilt-phone", "Quilt Map · phone (static)", [("energy", "Energy"), ("gap", "Approve")],
    "Below 640px the map does not animate. Each concept shows a static first level (your note for the tree) with the stream chips and one CTA; tapping a subject opens sign-up with it picked. Rendered by the same code with <code>data-static</code>, so it always matches the desktop map.",
    "",
    [(f"{k}", phone(f'<div class="rw"><span class="wmk sm2">MERIT<b>.</b></span><span class="sp"></span><button class="btn s" type="button">Start free</button></div><div class="h-lg">Every subject you sit, <span class="ul">stitched</span> together.</div><div class="chips"><span class="chip on">A/L Science</span><span class="chip">Commerce</span><span class="chip">Arts</span></div><div class="qm qm-phone" data-qm="{kind}" data-static></div><button class="btn full" type="button">Start free</button><span class="xs t3" style="text-align:center">Tap a subject to start with it</span>', 760), note)
     for k, kind, note in [("A · Tree", "tree", "Static image of level 0: the Merit root and the stream's subjects as tips."),
                           ("B · Network", "net", "Static network; wires and stubs as on desktop."),
                           ("C · Orbit", "orbit", "Static ring.")]])

# ------------------------------------------------------------------ 02 Today extras
DONE = app("Today", "Hi, Dilini", f'''<div class="w-2col"><div class="st" style="gap:18px"><div class="rw" style="gap:18px"><div class="ring" style="--v:100;--sz:96px;--th:9px;--ring-bg:var(--merit-bg-app);--c:var(--merit-feedback-success)"><svg class="i" style="font-size:36px;color:var(--merit-reward-streak)"><use href="#i-flame-fill"/></svg></div><div class="st" style="gap:4px"><span class="ey">Today · 3 of 3 done</span><h4 class="h-lg">13-day streak. <span class="ul">+30</span> for today's plan</h4></div></div>
<div class="card succ" style="flex-direction:row;align-items:center;gap:14px"><span class="mode-ic" style="background:var(--merit-sage-300)">{I("check")}</span><div class="st sp" style="gap:2px"><b class="h-sm">You're done for today</b><span class="sm t2">Come back tomorrow, or keep going: practice still earns points.</span></div><button class="btn gh s" type="button">Keep practising</button></div>
<b class="h-sm">Also good today</b><div class="list"><div class="li">{tile("current", 44)}<div class="sp st" style="gap:0"><span class="ttl">Electric current</span><span class="meta">Physics · read section 2 · 5 min</span></div>{I("caret-right")}</div><div class="li">{tile("cells", 44)}<div class="sp st" style="gap:0"><span class="ttl">Cell organelles</span><span class="meta">Biology · 3 cards fading · Revise</span></div>{I("caret-right")}</div></div></div>{RAIL}</div>''', "Good evening")
FIRST = app("Today", "Welcome, Dilini", f'''<div class="w-2col"><div class="st" style="gap:18px"><div class="card feat" style="gap:8px"><span class="ey" style="color:var(--merit-butter-300)">Day 1</span><b class="h-md">Your plan starts with 5 easy questions</b><span class="sm" style="opacity:.85">Biology · Introduction to Biology. Takes about 3 minutes and starts your streak.</span><button class="btn wh s" type="button" style="align-self:flex-start">Start my first 5</button></div>
<div class="list"><div class="li"><span class="chk"></span><div class="sp st" style="gap:0"><span class="ttl">5 questions · Introduction to Biology</span><span class="meta">3 min</span></div></div><div class="li"><span class="chk"></span><div class="sp st" style="gap:0"><span class="ttl">Read: What is biology?</span><span class="meta">4 min</span></div></div><div class="li"><span class="chk"></span><div class="sp st" style="gap:0"><span class="ttl">Learn 10 new cards</span><span class="meta">5 min</span></div></div></div></div>{RAIL}</div>''', "Good morning")
s_today = kit_screen("web-today-states", "Today · done for the day + first day", [("energy", "Energy"), ("gap", "Approve")],
    "Two moments the app also has: the plan finished (30 points once, D-open: daily plan done) and a brand-new student's first plan. Same shell as tab 01.",
    "GET /today/plan · /streak", [("Done for today", DONE, "The ring fills sage; the Start button becomes Keep practising."), ("First day", FIRST, "Onboarding ends here, with the first subject preselected from the landing CTA when there was one.")])

# ------------------------------------------------------------------ 03 Quiz dialogs
DLG = lambda t, b, a1, a2, inv=False: f'<div class="dlg" style="width:360px"><b class="h-sm">{t}</b><span class="sm t2">{b}</span><div class="rw" style="justify-content:flex-end"><button class="btn gh s" type="button">{a1}</button><button class="btn {"inv " if inv else ""}s" type="button">{a2}</button></div></div>'
qd = dk("meritproject.lk/student/quiz/8f2c…", f'<div class="w-app focus" style="place-items:center;min-height:420px"><div class="rw" style="gap:24px;flex-wrap:wrap;justify-content:center;padding:40px">{DLG("Submit the paper?", "46 of 50 answered. 4 are blank and 2 are flagged.", "Review blanks", "Submit")}{DLG("Pause this paper?", "Your answers are saved. The timer keeps running and you have 1:42 left.", "Keep going", "Pause", True)}</div></div>')
s_quizd = kit_screen("web-quiz-dialogs", "Quiz · submit and pause dialogs", [("calm", "Calm"), ("gap", "Approve")],
    "Same copy as the app. On the web, leaving the tab mid-paper keeps the timer running (it is server time).", "POST /quiz/sessions/:id/complete · /abandon", [("Dialogs", qd, "Esc closes a dialog; Enter confirms the primary.")])

# ------------------------------------------------------------------ 04 Study & notes
CARD = f'''<div class="w-focus"><div class="w-ftop"><span class="ibtn flat">{I("x")}</span><div class="bar thin calm sp"><i style="--v:33%"></i></div><b class="num sm">4/12</b></div>
<div class="w-flash"><div class="fc" style="min-height:260px"><span class="wash" style="--wash:url('assets/v3/patchwork-demo/leaf-wash.svg')"></span><span class="ey">Leaf structure</span><p class="q">What does the bundle sheath do in C4 plants?</p></div>
<div class="fc back" style="min-height:260px"><span class="ey">Answer</span><p class="q">It runs the Calvin cycle, with CO₂ concentrated away from oxygen, so photorespiration stays low.</p></div></div>
<div class="fsrs"><span class="ag">Again<small>1 · &lt;1 min</small></span><span class="hd2">Hard<small>2 · 6 min</small></span><span class="gd">Good<small>3 · 1 day</small></span><span class="ez">Easy<small>4 · 4 days</small></span></div>
<span class="xs t3" style="text-align:center">Space flips · 1–4 rate · Retention target 90% from your study plan</span></div>'''
cards = dk("meritproject.lk/student/cards/session", f'<div class="w-app focus">{CARD}</div>')
NOTE = f'''<div class="w-note"><aside class="w-outline"><span class="ey">Leaf structure</span><div class="stepper"><i class="d"></i><i class="d"></i><i class="c"></i><i></i></div><span class="xs t3">12 min · 2 of 4 done</span>
<a class="w-ol d">{I("check-circle-fill")}1. Overview</a><a class="w-ol d">{I("check-circle-fill")}2. The epidermis</a><a class="w-ol on">{I("circle-dashed")}3. Mesophyll</a><a class="w-ol">{I("circle-dashed")}4. Vascular bundles</a>
<div class="card flat tight"><span class="xs t2">{I("cards-three")} 14 flashcards from this note</span></div></aside>
<article class="w-read"><div class="crumb"><img class="mono" src="assets/v3/patchwork-demo/biology-mono.svg" alt="">Biology{I("caret-right")}<img class="mono" src="assets/v3/patchwork-demo/plants-mono.svg" alt="">Plant form{I("caret-right")}Leaf structure</div><h4 class="h-xl">3. Mesophyll</h4>
<div class="prose"><p>The mesophyll has two layers. <b>Palisade</b> cells sit under the upper epidermis. They are long, tightly packed and full of chloroplasts.</p><p><b>Spongy</b> cells below them are loosely arranged, with large air spaces for gas exchange.</p><div class="eqn">6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂</div><div class="callout">{I("lightbulb")}<span><b>Exam tip.</b> The 2019, 2021 and 2023 papers asked you to label palisade and spongy mesophyll on a T.S.</span></div></div>
<div class="chkpt"><svg class="i" style="font-size:22px;color:var(--merit-text-tertiary)"><use href="#i-check-circle"/></svg><span class="sp sm">Finished this section?</span><button class="btn s" type="button">Mark done · +5</button></div></article></div>'''
notes = dk("meritproject.lk/student/notes/leaf-structure", f'<div class="w-app focus">{NOTE}</div>')
s_study = kit_screen("web-study", "Study · card session + notes reader", [("calm", "Calm"), ("gap", "Approve")],
    "Mobile picks at desktop width. Cards: flip plus FSRS buttons with keyboard keys and the next interval. Notes: the section outline becomes a sticky left rail (mobile pick A's header stepper), reading column at ~68ch.",
    "POST /flashcards/reviews · GET /subtopics/:id/note · POST /notes/:id/sections/:sid/complete",
    [("Card session", cards, "Both faces shown here; live it flips (or crossfades under reduced motion)."), ("Notes reader", notes, "Revise badge (detour) shows on the outline when a read section is fading.")])

# ------------------------------------------------------------------ 05 Subjects extras
LEARN = '<div class="w-learn">' + "".join(
    f'<div class="card w-sj"><div class="ring" style="--v:{m};--sz:84px;--th:5px">{tile(t, 64)}</div><div class="st" style="gap:2px"><b class="h-sm">{n}</b><span class="sm t2">{m}% · {d}</span></div></div>'
    for n, t, m, d in [("Biology", "biology", 64, "12 cards due"), ("Chemistry", "chemistry", 41, "3 due"), ("Physics", "physics", 28, "nothing due"), ("General English", "languages", 72, "5 due")]) + \
    f'<div class="card w-sj add"><span class="mode-ic" style="background:var(--merit-surface-sunken)">{I("plus")}</span><div class="st" style="gap:2px"><b class="h-sm">Add a subject</b><span class="sm t2">1 slot left on Wanderer</span></div></div></div>'
learn = app("Learn", "Your subjects", LEARN, "Learn · 4 of 5", url="meritproject.lk/student/learn")
STATS = f'''{HUB_HERO.replace('<span class="on">' + I("path-fill") + 'Learn</span>', '<span>' + I("path") + 'Learn</span>').replace('<span>' + I("chart-line-up") + 'Stats</span>', '<span class="on">' + I("chart-line-up-fill") + 'Stats</span>')}
<div class="w-stats"><div class="card" style="flex-direction:row;align-items:center;gap:14px"><span class="slgrade" style="width:56px;height:56px;font-size:30px;border-radius:18px;background:var(--merit-sage-100)">B</span><div class="st" style="gap:2px"><span class="ey">If the exam were today</span><b class="h-sm">Likely a B (65–74%)</b><span class="sm t2">Medium confidence · 3 papers used</span></div></div>
<div class="card" style="gap:6px"><span class="ey">High-yield gap</span><b class="h-sm">Genetics · about 9 marks at stake</b><span class="sm t2">Comes up 1.8 times per paper and you're at 8%.</span><button class="btn s ac" type="button" style="align-self:flex-start">Practise Genetics</button></div>
<div class="card radar-lock" style="min-height:150px"><div class="ov">{I("lock-key-fill")}<b class="sm">Memory on exam day · Peers</b><span class="xs t2">See what you'll remember in August and how you pace against your cohort.</span><span class="badge pro">Achiever</span></div></div>
<div class="card" style="gap:6px"><span class="ey">Watch out</span><b class="h-sm">Circulation cards are fading</b><span class="sm t2">7 cards drop below 70% recall this week.</span><button class="btn s gh" type="button" style="align-self:flex-start">Review 7 cards</button></div></div>'''
stats = app("Learn", "Biology", STATS, "Learn", url="meritproject.lk/student/subjects/biology?tab=stats")
s_subj = kit_screen("web-subjects-more", "Subjects · Learn root + Stats tab", [("energy", "Energy"), ("gap", "Approve")],
    "Learn root lists enrolled subjects as tinted ring cards with the add tile (capacity from <code>/enrollments/capacity</code>). Stats follows mobile pick B (insights first, grade on top) with the detour cards; Achiever-only cards are locked teasers for Wanderer.",
    "GET /enrollments · /enrollments/capacity · /subjects/:id/prediction · /insights · /exam-insights · /peers",
    [("Learn root", learn, "Click a card to open the hub."), ("Stats tab", stats, "Two-column grid of insight cards at desktop width.")])

# ------------------------------------------------------------------ 06 Compete leaderboard
POD = f'<div class="card" style="gap:12px"><div class="podium"><div class="p2"><div class="av"></div><span class="nm">Kasun P.</span><span class="pt">4,610</span><div class="step">2</div></div><div class="p1">{I("crown-fill")}<div class="av lg" style="width:56px;height:56px"></div><span class="nm">Nethmi R.</span><span class="pt">4,820</span><div class="step">1</div></div><div class="p3"><div class="av"></div><span class="nm">Tharushi S.</span><span class="pt">4,390</span><div class="step">3</div></div></div></div>'
ROWS = "".join(f'<div class="lrow"><span class="rk">{r}</span><div class="av sm"></div><span class="nm">{n}<small>{s}-day streak</small></span><span class="pt">{p}</span></div>' for r, n, s, p in [(4, "Ravindu J.", 14, "4,120"), (5, "Ishara W.", 3, "3,980"), (6, "Sahan D.", 21, "3,760"), (7, "Hasini K.", 9, "3,610"), (8, "Pasindu M.", 2, "3,402")])
LB = f'''<div class="w-2col"><div class="st" style="gap:12px"><div class="segc" style="width:320px"><span>School</span><span class="on">District</span><span>Island</span></div>{POD}<div class="list">{ROWS}</div></div>
<aside class="w-rail"><div class="card feat" style="gap:6px"><span class="ey" style="color:var(--merit-butter-300)">Gampaha district</span><b class="num" style="font-size:40px;line-height:1">#38</b><span class="sm">12 points to pass #37. About 2 correct answers.</span></div><div class="lrow me"><span class="rk">38</span><div class="av sm"></div><span class="nm">You<small>12-day streak</small></span><span class="pt">1,240</span></div></aside></div>'''
lb = app("Compete", "Leaderboard", LB, "Compete", url="meritproject.lk/student/compete/leaderboard")
s_lb = kit_screen("web-leaderboard", "Compete · leaderboard page", [("energy", "Energy"), ("gap", "Approve")],
    "Mobile pick A (podium + you) at desktop width: the sticky \"You\" row moves into the right rail with the gap to the next rank.",
    "GET /leaderboards/districts/:name · /schools/:name · /global · /leaderboards/me/ranks", [("Leaderboard", lb, "Top 50 per scope, as the API serves.")])

# ------------------------------------------------------------------ 07 Premium limit dialog
LIM = f'''<div class="w-app focus" style="place-items:center;min-height:520px;background:color-mix(in srgb, var(--merit-ink-900) 45%, var(--merit-bg-app))"><div class="dlg" style="width:460px;gap:12px"><span class="ey">Daily limit reached</span><b class="h-md">That was question 50 for today</b><span class="sm t2">Your 9 of 10 just now earned 110 points. Keep the momentum going:</span>
<div class="list" style="box-shadow:none;background:var(--merit-surface-sunken)"><div class="li"><span class="mode-ic" style="background:var(--merit-violet-100)">{I("crown")}</span><div class="sp st" style="gap:0"><span class="ttl">Keep going with Achiever</span><span class="meta">14 days free in the app</span></div>{I("caret-right")}</div><div class="li"><span class="mode-ic" style="background:var(--merit-category-1)">{I("cards-three")}</span><div class="sp st" style="gap:0"><span class="ttl">Review 12 cards instead</span><span class="meta">Cards have no daily limit</span></div>{I("caret-right")}</div><div class="li"><span class="mode-ic" style="background:var(--merit-category-2)">{I("book-open")}</span><div class="sp st" style="gap:0"><span class="ttl">Read a note</span><span class="meta">Leaf structure, section 3</span></div>{I("caret-right")}</div></div>
<span class="xs t3" style="text-align:center">Questions reset at midnight (in 6 h 12 min)</span></div></div>'''
s_lim = kit_screen("web-limit", "Premium · limit dialog", [("energy", "Energy"), ("gap", "Approve")],
    "The app's limit sheet (pick C) as a centred dialog on the web. Opened by <code>DAILY_LIMIT_REACHED</code>; <code>PREMIUM_REQUIRED</code> opens the Achiever page.",
    "GET /quiz/daily-limits (resets_at)", [("Limit dialog", dk("meritproject.lk/student/quiz", LIM), "Achiever row goes to the Achiever page (buy in the app).")])

# ------------------------------------------------------------------ 08 Me extras
AV = f'''<div class="w-app focus" style="place-items:center;min-height:540px;background:color-mix(in srgb, var(--merit-ink-900) 45%, var(--merit-bg-app))"><div class="dlg" style="width:560px;gap:14px"><div class="rw"><b class="h-md sp">Pick your avatar</b><span class="ibtn flat">{I("x")}</span></div><div class="avgrid" style="grid-template-columns:repeat(10,1fr)">''' + "".join(f'<span class="av{" on" if k == 7 else ""}"></span>' for k in range(30)) + f'''</div><div class="rw"><button class="btn gh" type="button">{I("camera")}Upload a photo</button><span class="sp"></span><button class="btn" type="button">Use this one</button></div></div></div>'''
LANGS = '<div class="list" style="max-width:640px">' + "".join(f'<div class="li">{tile(t, 40)}<span class="sp ttl">{n}</span><div class="segc" style="padding:3px;width:180px">' + "".join(f'<span class="{"on" if l == on else ""}{" off" if l in off else ""}" style="padding:5px 6px;min-height:28px">{l}</span>' for l in ("EN", "සිං", "த")) + '</div></div>' for n, t, on, off in [("Biology", "biology", "සිං", ()), ("Chemistry", "chemistry", "සිං", ()), ("Physics", "physics", "EN", ()), ("General English", "languages", "EN", ("සිං", "த"))]) + '</div><span class="sm t3">The only place content language changes. Greyed options have no content yet (<code>available_languages</code>).</span>'
s_me2 = kit_screen("web-me-more", "Me · avatar picker", [("energy", "Energy"), ("gap", "Approve")],
    "Catalogue picker with photo upload kept as the secondary option. Subject languages are no longer on Me on the web (Gate 0, 2026-10-23): they switch in each subject's header (tab 05, round 15).",
    "GET /avatars · PUT /user {avatar_id}",
    [("Avatar picker", dk("meritproject.lk/student/me", AV), "30 catalogue avatars from merit-content.")])

# ------------------------------------------------------------------ 09 Auth & onboarding
def split(form):
    return dk("meritproject.lk/student/sign-in", f'''<div class="w-split"><div class="w-splitart"><span class="wmk">MERIT<b>.</b></span><div class="qm qm-art" data-qm="tree" data-static></div><b class="h-lg">Earn <span class="ul">Merit</span>.</b><span class="sm t2">Free forever. Streaks, points and quizzes in Sinhala, Tamil and English.</span></div><div class="w-splitform">{form}</div></div>''')
MOB = f'<div class="fld"><label>Mobile number</label><div class="inp focus"><span class="cc">+94</span><b style="font-weight:600">7</b>7 123 4567</div><span class="xs t3">Sri Lankan mobile numbers start with 7</span></div>'
SIGNIN = f'<b class="h-xl">Welcome back</b><div class="segc"><span class="on">Mobile</span><span>Email</span></div>{MOB}<div class="fld"><label>Password</label><div class="inp">••••••••<span class="sp"></span>{I("eye-slash")}</div></div><a class="lnk" style="align-self:flex-end">Forgot password?</a><button class="btn full" type="button">Sign in</button><span class="sm t2" style="text-align:center">New here? <a class="lnk">Create an account</a></span>'
REG = f'<b class="h-xl">Create your account</b><div class="fld"><label>Full name</label><div class="inp">Dilini Perera</div></div>{MOB}<div class="g2"><div class="fld"><label>Password</label><div class="inp">••••••••</div></div><div class="fld"><label>Confirm password</label><div class="inp ph-in">Type it again</div></div></div><div class="fld"><label>Preferred language</label><div class="segc"><span class="on">සිංහල</span><span>தமிழ்</span><span>English</span></div><span class="xs t3">For subject content. Change it per subject later.</span></div><div class="card flat tight" style="flex-direction:row;align-items:center;gap:10px">{tile("physics", 32)}<span class="sm sp">Starting with <b>Physics</b> from the subject map</span><a class="lnk">Change</a></div><button class="btn full" type="button">Create account</button>'
ONB = app("Learn", "Pick your subjects", f'''<div class="w-onb"><div class="rw"><div class="stepper sp"><i class="d"></i><i class="d"></i><i class="c"></i><i></i><i></i></div><span class="sm t3">3 of 5</span></div><span class="sm t2">Science · up to 5 · content starts in <b>Sinhala</b></span>
<div class="list">''' + "".join(f'<div class="li sjrow{" on" if c else ""}"><span class="ckb{" on" if c else ""}">{I("check") if c else ""}</span>{tile(t, 40)}<div class="sp st" style="gap:0"><span class="ttl">{n}</span>{"<span class=meta>From the subject map</span>" if n == "Physics" else ""}</div>' + (f'<div class="segc lseg"><span{" class=on" if l != "EN" else ""}>EN</span><span{" class=on" if l == "EN" else ""}>සිං</span><span>த</span></div>' if c else "") + '</div>' for n, t, c, l in [("Physics", "physics", 1, "x"), ("Chemistry", "chemistry", 1, "EN"), ("Biology", "biology", 1, "EN"), ("ICT", "ict", 0, ""), ("Agricultural Science", "plants", 0, "")]) + '</div><div class="rw"><button class="btn gh" type="button">Back</button><span class="sp"></span><button class="btn" type="button">Next</button></div></div>', "Onboarding", url="meritproject.lk/student/onboarding")
s_auth = kit_screen("web-auth", "Auth · sign in, register (with subject from the map), onboarding", [("calm", "Calm"), ("gap", "Approve")],
    "Split screen: brand art on the left (the picked Quilt Map concept, static), form on the right. Mobile field follows D22. Register keeps today's fields (round 8 decision); when the visitor came from the map, the chosen subject rides along and is pre-ticked in onboarding step 3.",
    "POST /auth/register · /auth/login · /auth/otp/* · POST /students/me · /enrollments",
    [("Sign in", split(SIGNIN), "Forgot password opens the 3-step flow from the app."), ("Register", split(REG), "?subject=&lt;id&gt; from the landing CTA."), ("Onboarding · step 3", ONB, "No sidebar until onboarding is finished; the shell is shown here for scale only.")])

# ------------------------------------------------------------------ 10 States
def st_card(img, t, b, cta):
    return f'<div class="card state" style="width:100%"><img src="assets/v3/spots/{img}.svg" alt=""><b class="h-sm">{t}</b><span class="sm t2">{b}</span><button class="btn gh s" type="button">{cta}</button></div>'
STATES = f'''<div class="w-states">{st_card("empty", "No attempts yet", "Your quiz history shows up here.", "Start a quiz")}{st_card("error", "Couldn't load Biology", "The server didn't answer. Your progress is safe.", "Try again")}{st_card("offline", "You're offline", "We'll reconnect automatically.", "Retry")}{st_card("not-found", "This paper was removed", "Try another year.", "All papers")}
<div class="card" style="gap:12px"><div class="rw"><div class="sk" style="width:56px;height:56px;border-radius:16px"></div><div class="st sp" style="gap:8px"><div class="sk" style="height:12px;width:70%"></div><div class="sk" style="height:8px"></div></div></div><div class="rw"><div class="sk" style="width:56px;height:56px;border-radius:16px"></div><div class="st sp" style="gap:8px"><div class="sk" style="height:12px;width:55%"></div><div class="sk" style="height:8px"></div></div></div></div>
<div class="dlg"><b class="h-sm">Please sign in again</b><span class="sm t2">For your security, you were signed out.</span><button class="btn s" type="button" style="align-self:flex-end">Sign in</button></div></div>'''
s_states = kit_screen("web-states", "States · empty, error, offline, loading, session", [("gap", "Approve")],
    "One spot, one line, one CTA; never a patchwork (DS §5). Same set as the app.", "", [("States", app("Learn", "Biology", STATES, "Learn"), "Skeletons match the real layout and stay static under reduced motion.")])

# ------------------------------------------------------------------ round 12 (one module per agent)
from r12_landing import concept, s_hero  # noqa: E402,F811  low-poly tree + hero A + phone hero
from r12_hub import s_hub, s_subj  # noqa: E402,F811  hub A with mobile section tabs
from r12_auth import s_auth  # noqa: E402,F811  step-aware split screen
from r15_web import s_acct, s_verify, s_lang, s_sys, s_results  # noqa: E402  round 15: §30 flows + Gate 0
from r14_landing import s_secs  # noqa: E402,F811  live sections + Mastery Engine + Merit Points, pricing/FAQ from rules (rounds 13-14)

# ------------------------------------------------------------------ page
NAVS = [("landing", "00", "Landing"), ("shell", "01", "Shell &amp; nav"), ("today", "02", "Today"), ("quiz", "03", "Quiz"), ("study", "04", "Study &amp; notes"),
        ("subjects", "05", "Subjects"), ("compete", "06", "Compete"), ("premium", "07", "Premium"), ("me", "08", "Me"), ("auth", "09", "Auth &amp; onboarding"), ("states", "10", "System states")]
LG = [("energy", "Energy mode"), ("calm", "Calm mode"), ("gap", "New / approve")]
flows = [
    flow("landing", "Landing", "The public page at <code>meritproject.lk</code>. First pick the Quilt Map concept (live prototypes, try them), then the hero composition and the sections below. Copy is trilingual via <code>?lang=en|si|ta</code>.", LG, [concept, phones, s_hero, s_secs], first=True),
    flow("shell", "Shell &amp; navigation", "Navigation B from the app (Today · Learn · Compete · Me). Below 768px the portal becomes the app layout with a bottom tab bar.", LG, [s_shell]),
    flow("today", "Today", "The app's Today plan on a wide screen. The main frame is in tab 01; these are the other two moments.", LG, [s_today]),
    flow("quiz", "Quiz", "Taking a quiz drops the sidebar (focus layout). Results follow round 10 pick A.", LG, [s_quiz, s_results, s_quizd]),
    flow("study", "Study &amp; notes", "Calm mode. Keyboard-first on the web.", LG, [s_study]),
    flow("subjects", "Subjects", "Learn root, the subject hub and its Stats tab.", LG, [s_hub, s_subj, s_lang]),
    flow("compete", "Compete", "Round 10 Compete at desktop width, plus the leaderboard page.", LG, [s_comp, s_lb]),
    flow("premium", "Premium", "No web checkout: the web sells, the app sells the subscription (store billing).", LG, [s_prem, s_lim]),
    flow("me", "Me", "D23: settings live on Me. Web adds the Theme row (D26).", LG, [s_me, s_me2, s_acct]),
    flow("auth", "Auth &amp; onboarding", "Same fields and steps as the app (round 8 decisions), laid out for a wide screen.", LG, [s_auth, s_verify]),
    flow("states", "System states", "One design each; no picks needed.", [("gap", "Approve")], [s_states, s_sys]),
]

HEAD = '''<meta charset="utf-8">
<title>Merit Web Wireframes</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Sans+Sinhala:wght@400;500;700&display=swap">
<link rel="stylesheet" href="wireframes/wf.css">
<link rel="stylesheet" href="wireframes/wf-web.css">
<link rel="stylesheet" href="wireframes/wf-r12-landing.css">
<link rel="stylesheet" href="wireframes/wf-r12-hub.css">
<link rel="stylesheet" href="wireframes/wf-r12-auth.css">
<link rel="stylesheet" href="wireframes/wf-r13-landing.css">
<link rel="stylesheet" href="wireframes/wf-r14-landing.css">
<link rel="stylesheet" href="wireframes/wf-r15-web.css">

<header class="wf-top">
  <div class="wf-top-row">
    <div class="wf-brand"><h1>Merit web wireframes</h1><span>v3 web · landing + student portal · round 15</span></div>
    <div class="wf-ctrls">
      <span class="wf-tally" aria-live="polite"></span>
      <div class="wf-seg" data-seg="width" role="group" aria-label="Frame width">
        <button type="button" data-val="1280" aria-pressed="true">1280</button>
        <button type="button" data-val="1024" aria-pressed="false">1024</button>
      </div>
      <div class="wf-seg" data-seg="theme" role="group" aria-label="Theme">
        <button type="button" data-val="system" aria-pressed="true">Auto</button>
        <button type="button" data-val="light" aria-pressed="false">Light</button>
        <button type="button" data-val="dark" aria-pressed="false">Dark</button>
      </div>
    </div>
  </div>
  <nav class="wf-flows" aria-label="Flows">
''' + "\n".join(f'    <a href="#{f}"><span class="n">{n}</span>{t}</a>' for f, n, t in NAVS) + '''
  </nav>
</header>

<main class="wf-main">
'''
TAIL = '''</main>

<script src="wireframes/icons.js"></script>
<script src="wireframes/wf.js"></script>
<script src="wireframes/qm-data.js"></script>
<script src="wireframes/qm.js"></script>
<script src="wireframes/qm-tree.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/delaunator@5.0.1/delaunator.min.js"></script>
<script src="wireframes/qm-lowpoly.js"></script>
<script src="wireframes/qm-ico.js"></script>
<script src="wireframes/qm-samples.js"></script>
<script src="wireframes/landing-live.js"></script>
<script src="wireframes/r14-live.js"></script>
'''

if __name__ == "__main__":
    print(HEAD + "\n".join(flows) + TAIL)
