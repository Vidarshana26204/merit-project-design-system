# Run from anywhere: python3 wireframes/gen_web_r11.py > /tmp/web.html, then splice into wireframes.html before </main>.
"""Generate the Web round (round 11) section for wireframes.html.

Prints an HTML fragment (a <section data-flow="web">) to stdout. Geometry for the
Quilt Map frames is computed here so connectors and nodes line up.
"""
import math

PW = "assets/v3/patchwork-demo/"
I = lambda n: f'<svg class="i"><use href="#i-{n}"/></svg>'


def tile(name, s, extra=""):
    return f'<img class="tile" style="--s:{s}px{extra}" src="{PW}{name}-tile.svg" alt="">'


# ---------------------------------------------------------------- quilt map
SUBJECTS = [  # (label, tile, topics, subtopics, questions)
    ("Physics", "physics", 11, 60, 500),
    ("Chemistry", "chemistry", 14, 93, 500),
    ("Biology", "biology", 10, 104, 600),
    ("Combined Maths", "maths", 12, 71, 450),
    ("ICT", "ict", 9, 48, 320),
    ("General English", "languages", 8, 36, 240),
]
PHYS_TOPICS = [  # (label, tile, subtopics, questions, exam share)
    ("Measurement", "waves", 3, 20, "4%"),
    ("Mechanics", "kinetics", 8, 124, "24.5%"),
    ("Oscillations &amp; waves", "waves", 6, 61, "11%"),
    ("Thermal physics", "thermal", 5, 48, "9%"),
    ("Electric fields", "current", 6, 52, "10%"),
    ("Magnetic fields", "magnetism", 5, 41, "8%"),
]
MECH_SUBS = ["Kinematics", "Newton's laws", "Momentum", "Work &amp; energy", "Circular motion", "Statics"]


def pol(cx, cy, r, deg):
    a = math.radians(deg)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def qmap(w, h, state="idle", tour=True, scale=1.0):
    """state: idle | subject | topic"""
    cx, cy = w / 2, h / 2
    r1 = min(w, h) * 0.34
    nodes, lines, extra = [], [], []
    sel = 0  # Physics
    # camera: when a subject is open, pull the stage so Physics sits left of centre
    shift_x = 0
    if state in ("subject", "topic"):
        shift_x = -r1 * 0.55
    angs = [-90 + i * 60 for i in range(6)]
    # Physics sits at 0° (right) so topics fan out to the right
    angs = [0, 60, 120, 180, 240, 300]
    mark = 76 * scale
    lines_svg = []
    for i, (lab, t, tp, st, q) in enumerate(SUBJECTS):
        x, y = pol(cx + shift_x, cy, r1, angs[i])
        dim = state != "idle" and i != sel
        lines_svg.append(f'<line x1="{cx+shift_x:.1f}" y1="{cy:.1f}" x2="{x:.1f}" y2="{y:.1f}" class="qc{" dim" if dim else ""}{" on" if (state!="idle" and i==sel) else ""}"/>')
        s = 64 * scale if not (state != "idle" and i == sel) else 78 * scale
        cls = "qn" + (" dim" if dim else "") + (" sel" if (state != "idle" and i == sel) else "")
        nodes.append(f'<button class="{cls}" style="left:{x:.1f}px;top:{y:.1f}px" type="button" aria-expanded="{"true" if (state!="idle" and i==sel) else "false"}">{tile(t, int(s))}<span>{lab}</span></button>')
    if state in ("subject", "topic"):
        px, py = pol(cx + shift_x, cy, r1, 0)
        r2 = min(w, h) * 0.30
        tang = [-75, -45, -15, 15, 45, 75]
        for j, (lab, t, st, q, share) in enumerate(PHYS_TOPICS):
            x, y = pol(px, py, r2, tang[j])
            on = state == "topic" and j == 1
            dim = state == "topic" and j != 1
            lines_svg.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{x:.1f}" y2="{y:.1f}" class="qc t{" dim" if dim else ""}{" on" if on else ""}"/>')
            s = 50 * scale if not on else 60 * scale
            nodes.append(f'<button class="qn t{" sel" if on else ""}{" dim" if dim else ""}" style="left:{x:.1f}px;top:{y:.1f}px" type="button">{tile(t, int(s))}<span>{lab}</span></button>')
            if state == "subject" and j == 1:
                extra.append(f'<div class="qtip" style="left:{x+30*scale:.1f}px;top:{y+6*scale:.1f}px"><b>Mechanics</b><span>8 subtopics · 124 questions</span><span class="ok">About 24.5% of Paper I marks</span></div>')
        if state == "topic":
            mx, my = pol(px, py, r2, tang[1])
            r3 = min(w, h) * 0.17
            for k, lab in enumerate(MECH_SUBS):
                x, y = pol(mx, my, r3, -150 + k * 42)
                lines_svg.append(f'<line x1="{mx:.1f}" y1="{my:.1f}" x2="{x:.1f}" y2="{y:.1f}" class="qc b"/>')
                nodes.append(f'<span class="qb" style="left:{x:.1f}px;top:{y:.1f}px"><i></i><span>{lab}</span></span>')
    if tour and state == "idle":
        x, y = pol(cx, cy, r1 * 0.55, 0)
        extra.append(f'<span class="qcoin" style="left:{x:.1f}px;top:{y:.1f}px"><span class="coin"></span><b>+10</b></span>')
    svg = f'<svg class="qlines" viewBox="0 0 {w} {h}" aria-hidden="true">{"".join(lines_svg)}</svg>'
    center = f'<span class="qmark" style="left:{cx+shift_x:.1f}px;top:{cy:.1f}px;--m:{mark:.0f}px"><img src="assets/v3/brand/merit-mark.svg" alt="Merit"></span>'
    return f'<div class="qmap" style="width:{w}px;height:{h}px">{svg}{center}{"".join(nodes)}{"".join(extra)}</div>'


STREAMS = '<div class="w-chips"><span class="chip on">A/L Science</span><span class="chip">Commerce</span><span class="chip">Arts</span><span class="chip">Technology</span><span class="chip">O/L</span></div>'


# ---------------------------------------------------------------- frames
def dk(url, body, h=None):
    style = f' style="min-height:{h}px"' if h else ""
    return f'<div class="wdk"><div class="wdk-bar"><i></i><i></i><i></i><span>{url}</span></div><div class="wdk-body"{style}>{body}</div></div>'


def lnav():
    return ('<nav class="w-lnav"><span class="wmk">MERIT<b>.</b></span><span class="sp"></span>'
            '<a>Subjects</a><a>How it works</a><a>Pricing</a><span class="w-lang">EN · සිං · த</span>'
            '<a class="lnk">Sign in</a><button class="btn s" type="button">Start free</button></nav>')


def cand(letter, name, kind, frame, pro, con, comps, pick=True):
    pk = f'<div class="wf-pick"><button type="button" aria-pressed="false">Pick {letter}</button></div>' if pick else ""
    cc = f'<p class="con">{con}</p>' if con else ""
    return (f'<div class="wf-cand" data-v="{letter}"><div class="wf-cand-h"><b>{letter}</b><span>{name}</span><em>{kind}</em></div>'
            f'{frame}<div class="wf-note"><p class="pro">{pro}</p>{cc}<div class="wf-comps">{comps}</div>{pk}</div></div>')


def screen(sid, title, tags, desc, data, cands, desk=True, fb=True):
    tg = "".join(f'<span class="tag {c}">{t}</span>' for c, t in tags)
    d = f'<span class="wf-data">{data}</span>' if data else ""
    f = (f'<div class="wf-feedback"><label for="fb-{sid}">Notes on {title.split(" ·")[0]}</label>'
         f'<textarea id="fb-{sid}" rows="2"></textarea><span class="wf-saved"></span></div>') if fb else ""
    return (f'<article class="wf-screen" data-screen="{sid}"><div class="wf-screen-h"><h3>{title}</h3>{tg}<p>{desc}</p>{d}</div>'
            f'<div class="wf-vars{" desk" if desk else ""}">{"".join(cands)}</div>{f}</article>')


HERO_COPY = ('<span class="ey">O/L &amp; A/L · Sinhala · Tamil · English</span>'
             '<h1 class="w-h1">Every subject you sit, <span class="ul">stitched</span> together.</h1>'
             '<p class="w-lede">Past papers, flashcards and notes for the Sri Lankan syllabus. Explore your stream and see exactly what each paper asks.</p>')

hero_a = dk("meritproject.lk", lnav() + f'''
<div class="w-hero a"><div class="st" style="gap:18px;max-width:440px">{HERO_COPY}
<div class="rw"><button class="btn l" type="button">Start free</button><button class="btn gh l" type="button">{I("play-circle")}How it works</button></div>
<div class="rw xs t3" style="gap:14px"><span>62 subjects</span><span>·</span><span>Official past papers since 2012</span><span>·</span><span>Free forever</span></div></div>
<div class="st" style="align-items:center;gap:10px"><div class="qm qm-slot" data-qm="tree" data-static style="max-width:560px"></div>{STREAMS}</div></div>''')

hero_b = dk("meritproject.lk", lnav() + f'''
<div class="w-hero b"><div class="st" style="align-items:center;text-align:center;gap:14px;max-width:640px;margin:0 auto">{HERO_COPY}{STREAMS}</div>
<div style="display:grid;place-items:center"><div class="qm qm-slot" data-qm="tree" data-static style="max-width:820px"></div></div>
<div class="rw" style="justify-content:center"><button class="btn l" type="button">Start free</button><a class="lnk">Skip the map</a></div></div>''')

hero_c = dk("meritproject.lk", lnav() + f'''
<div class="w-hero c"><div class="w-cstage"><div class="qm qm-slot" data-qm="tree" data-static style="max-width:1100px"></div></div>
<div class="w-ccard">{HERO_COPY}<div class="rw"><button class="btn" type="button">Start free</button><a class="lnk">Skip the map</a></div></div>
<div class="w-cchips">{STREAMS}</div></div>''')

s_hero = screen("web-hero", "Landing hero · Quilt Map composition", [("energy", "Energy"), ("gap", "New")],
    "Same Quilt Map in all three; only the composition differs. Real counts come from <code>GET /public/explore</code> (A/L Science shown: 6 subjects). The coin on the Physics connector is the idle tour: every ~6 s it travels a connector and pops +10, and stops for good at the first interaction. Reduced motion shows the static ring.",
    "GET /public/explore?lang= · streams → subjects (counts, patchwork) → topics (counts, exam_share_pct, patchwork) → subtopic titles",
    [cand("A", "Copy left, map right", "Safe", hero_a,
          "Reads like a classic hero: the promise and CTA are first, the map is the proof. The map fits a 1280 laptop without scrolling.",
          "The map gets ~45% of the width, so topic rings must zoom inside a smaller stage.", "<code>wordmark nav</code><code>display + brush underline</code><code>QuiltMap 560</code><code>stream chips</code>"),
     cand("B", "Map on stage", "Bold", hero_b,
          "The map is the hero: centred under one line of copy, with room for topics to fan out without zooming. Stream chips sit with the headline, so choosing a stream is the first action.",
          "The CTA lands below the map (~760px down); needs the nav CTA to carry conversions.", "<code>centred copy</code><code>QuiltMap 900</code><code>skip link</code>"),
     cand("C", "Full-bleed map, copy card", "Wild", hero_c,
          "Most immersive: the whole fold is the syllabus, and the copy floats on a card like a legend on a map. Feels like an app, not a brochure.",
          "Copy over an interactive stage needs care: the card must never cover a node, and keyboard users meet the card first.", "<code>QuiltMap 1100</code><code>floating copy card e2</code><code>chips on stage</code>")])

# ---- Quilt Map states
st_idle = f'<div class="st" style="align-items:center;gap:8px">{qmap(520, 430, scale=.85)}<span class="sm t3">1 · Idle: coin tour on a connector, ring of the stream\'s subjects</span></div>'
st_subj = f'<div class="st" style="align-items:center;gap:8px">{qmap(520, 430, "subject", scale=.85)}<span class="sm t3">2 · Physics opened: stage pans, topics fan out, others dim. Hover or focus shows real counts</span></div>'
st_topic = f'''<div class="st" style="align-items:center;gap:8px">{qmap(520, 430, "topic", scale=.85)}
<div class="qpanel"><span class="ey">Physics · Mechanics</span><b class="h-sm">8 subtopics · 124 questions</b><span class="sm t2">About 24.5% of Paper I marks over the last 12 years.</span><button class="btn s full" type="button">Start practising Mechanics</button><span class="xs t3">Free. Takes you to sign-up with Physics picked.</span></div>
<span class="sm t3">3 · Mechanics opened: subtopic beads + start panel. Esc goes back a level</span></div>'''
mob = f'''<div class="ph" style="height:760px"><div class="ph-sb"><span>9:41</span><span class="dots"><i></i><i></i></span></div>
<div class="scr calm" style="gap:14px"><div class="rw"><span class="wmk sm2">MERIT<b>.</b></span><span class="sp"></span><button class="btn s" type="button">Start free</button></div>
<div class="h-lg">Every subject you sit, <span class="ul">stitched</span> together.</div>
<div class="chips"><span class="chip on">A/L Science</span><span class="chip">Commerce</span><span class="chip">Arts</span></div>
<div class="qpath">
<div class="qp on">{tile("physics", 52)}<div class="st sp" style="gap:0"><b class="sm">Physics</b><span class="xs t3">11 topics · 500 questions</span></div>{I("caret-up")}</div>
<div class="qsub"><div class="rw">{tile("waves", 32)}<span class="sp sm">Measurement</span><span class="xs t3">4%</span></div><div class="rw on">{tile("kinetics", 32)}<span class="sp sm"><b>Mechanics</b></span><span class="xs t3">24.5%</span></div><div class="rw">{tile("thermal", 32)}<span class="sp sm">Thermal physics</span><span class="xs t3">9%</span></div><a class="lnk">All 11 topics</a></div>
<div class="qp">{tile("chemistry", 52)}<div class="st sp" style="gap:0"><b class="sm">Chemistry</b><span class="xs t3">14 topics · 500 questions</span></div>{I("caret-down")}</div>
<div class="qp">{tile("biology", 52)}<div class="st sp" style="gap:0"><b class="sm">Biology</b><span class="xs t3">10 topics · 600 questions</span></div>{I("caret-down")}</div>
<div class="qp">{tile("maths", 52)}<div class="st sp" style="gap:0"><b class="sm">Combined Maths</b><span class="xs t3">12 topics · 450 questions</span></div>{I("caret-down")}</div>
</div></div><div class="ph-gest"></div></div>'''
s_quilt = (f'<article class="wf-screen" data-screen="web-quilt"><div class="wf-screen-h"><h3>Quilt Map · interaction states + phone</h3><span class="tag energy">Energy</span><span class="tag gap">Approve</span>'
           f'<p>One design whichever hero wins. Keyboard: arrows move round the ring, Enter opens, Esc goes back, a live region announces "Physics, 11 topics". Topic exam share is hidden when a subject has too few papers (<code>exam_weight_min_papers</code>). Under 640px the orbit becomes a vertical learning path (DS §19) with accordions.</p>'
           f'<span class="wf-data">same payload as the hero · CTA → /student/sign-up?subject=&lt;id&gt;</span></div>'
           f'<div class="wf-kit">{st_idle}{st_subj}{st_topic}<div class="st" style="gap:8px">{mob}<span class="sm t3">Phone: vertical path, one subject open at a time</span></div></div>'
           f'<div class="wf-feedback"><label for="fb-web-quilt">Notes on the Quilt Map</label><textarea id="fb-web-quilt" rows="2"></textarea><span class="wf-saved"></span></div></article>')

# ---- landing sections
prog = '''<section class="w-sec"><div class="w-prog"><h3 class="w-h2">Three ways to <span class="ul">practise</span></h3><div class="w-items">
<div class="w-it"><span class="mode-ic" style="background:var(--merit-category-4)">%s</span><b>Paper mode</b><span class="sm t2">Sit a real past paper against the clock, then review every answer.</span></div>
<div class="w-it"><span class="mode-ic" style="background:var(--merit-category-1)">%s</span><b>Mastery mode</b><span class="sm t2">One subtopic at a time, explained as you go.</span></div>
<div class="w-it"><span class="mode-ic" style="background:var(--merit-category-5)">%s</span><b>Adaptive mode</b><span class="sm t2">Merit finds your weak spots and drills them. Achiever.</span></div></div></div></section>''' % (I("timer"), I("target"), I("brain"))
pricing = '''<section class="w-sec"><h3 class="w-h2" style="text-align:center">Free to start. <span class="ul">Achiever</span> when you're ready.</h3><div class="w-plans">
<div class="card w-plan"><span class="badge">Wanderer</span><b class="w-price">Free</b><span class="sm t2">Forever</span><ul class="w-ul"><li>50 mastery questions a day</li><li>2 past papers a day</li><li>Flashcards and notes, unlimited</li><li>Up to 5 subjects</li></ul><button class="btn gh full" type="button">Start free</button></div>
<div class="card w-plan pro"><span class="badge pro">Achiever</span><b class="w-price">Rs 4,990<small>/year</small></b><span class="sm">or Rs 599 a month · 14 days free</span><ul class="w-ul"><li>Unlimited questions and papers</li><li>Adaptive mode and exam forecast</li><li>1.5× points on everything</li><li>6 subjects</li></ul><button class="btn wh full" type="button">Get it in the app</button></div></div>
<p class="xs t3" style="text-align:center">Prices from the store at checkout. Buying happens in the Merit app.</p></section>'''
cta = '''<section class="w-sec"><div class="band cta w-band"><div><span class="ey">Merit Project</span><h4>Start free, earn your first badge today.</h4><p>Takes a minute. No card needed.</p></div><button class="btn wh" type="button">Start free</button></div></section>'''
faq = '''<section class="w-sec"><div class="w-faq"><h3 class="w-h2">Questions</h3><div class="list"><div class="li"><span class="sp ttl">Is it really free?</span>%s</div><div class="li"><span class="sp ttl">Which papers are included?</span>%s</div><div class="li"><span class="sp ttl">Can I study in Sinhala or Tamil?</span>%s</div><div class="li"><span class="sp ttl">Does it work on my phone?</span>%s</div></div></div></section>''' % ((I("plus"),) * 4)
foot = '<footer class="w-foot"><span class="wmk">MERIT<b>.</b></span><span class="sp"></span><a>Privacy</a><a>Terms</a><a>Contact</a><span class="w-store">Google Play</span><span class="w-store">App Store</span></footer>'

secs_a = dk("meritproject.lk/#pricing", f'<div class="w-scroll">{prog}{pricing}{faq}{cta}{foot}</div>')
story = f'''<section class="w-sec"><div class="w-story"><div class="st" style="gap:10px"><span class="ey">How Merit works</span><h3 class="w-h2">Read. Remember. <span class="ul">Prove</span>.</h3><p class="t2">Every subtopic fills up the same way: read the note, keep the cards fresh, then prove it on past-paper questions. Your quilt shows it.</p></div>
<div class="w-recipe"><div class="w-step"><span class="mode-ic" style="background:var(--merit-category-2)">{I("book-open")}</span><b>Read</b><span class="sm t2">Short notes with exam tips</span></div><div class="w-step"><span class="mode-ic" style="background:var(--merit-category-1)">{I("cards-three")}</span><b>Remember</b><span class="sm t2">Flashcards on a memory schedule</span></div><div class="w-step"><span class="mode-ic" style="background:var(--merit-category-4)">{I("target")}</span><b>Prove</b><span class="sm t2">Past-paper questions, marked instantly</span></div></div></div></section>
<section class="w-sec"><div class="w-numbers"><div><b>62</b><span>subjects</span></div><div><b>12</b><span>years of papers</span></div><div><b>3</b><span>languages</span></div><div><b>1.5×</b><span>points for Achievers</span></div></div></section>'''
secs_b = dk("meritproject.lk/#how", f'<div class="w-scroll">{story}{prog}{pricing}{cta}{foot}</div>')
s_secs = screen("web-landing", "Landing · sections below the hero", [("energy", "Energy")],
    "What follows the hero. Trilingual via <code>?lang=en|si|ta</code> (SI/TA copy never uppercased). Pricing shows the 14-day trial (D24) and sends Achiever to the app (no web checkout). Today's Ticker, Community and Testimonials sections are dropped unless we have real quotes.",
    "GET /public/explore (counts) · store links",
    [cand("A", "Classic stack", "Safe", secs_a, "Short and familiar: modes, pricing, FAQ, CTA band. Everything a parent looks for, in order.", "Doesn't explain the Read → Remember → Prove loop that makes Merit different.", "<code>programme grid</code><code>plan cards ×2</code><code>FAQ accordion</code><code>band.cta</code>"),
     cand("B", "Story then pricing", "Bold", secs_b, "Teaches the learning loop with the same words the app uses, then real numbers, then modes and pricing. Pairs well with the Quilt Map hero.", "One more section to scroll; numbers must be live or kept honest by hand.", "<code>recipe steps ×3</code><code>number strip</code><code>programme grid</code><code>plan cards</code>")])


# ---------------------------------------------------------------- student shell
NAV = [("sun", "Today"), ("books", "Learn"), ("trophy", "Compete"), ("user-circle", "Me")]


def side(active):
    items = "".join(f'<a class="{"on" if l == active else ""}">{I(i + ("-fill" if l == active else ""))}{l}</a>' for i, l in NAV)
    return (f'<aside class="w-side"><span class="wmk">MERIT<b>.</b></span><nav>{items}</nav>'
            f'<div class="w-side-foot"><span class="badge">Wanderer</span><span class="xs t3">14 days of Achiever free</span></div></aside>')


def head(title, eyebrow=""):
    ey = f'<span class="ey">{eyebrow}</span>' if eyebrow else ""
    return (f'<header class="w-head"><div class="st" style="gap:2px">{ey}<h4 class="h-lg">{title}</h4></div><span class="sp"></span>'
            f'<span class="w-search">{I("magnifying-glass")}Search topics, papers…<kbd>⌘K</kbd></span>'
            f'<span class="hchip fl">{I("flame-fill")}12</span><span class="hchip cn"><span class="coin"></span>1,240</span><div class="av sm"></div></header>')


def app(active, title, body, eyebrow="", url="meritproject.lk/student", topnav=False):
    if topnav:
        tabs = "".join(f'<a class="{"on" if l == active else ""}">{I(i + ("-fill" if l == active else ""))}{l}</a>' for i, l in NAV)
        inner = (f'<header class="w-top"><span class="wmk">MERIT<b>.</b></span><nav>{tabs}</nav><span class="sp"></span>'
                 f'<span class="hchip fl">{I("flame-fill")}12</span><span class="hchip cn"><span class="coin"></span>1,240</span><div class="av sm"></div></header>'
                 f'<main class="w-main narrow"><div class="st" style="gap:2px"><span class="ey">{eyebrow}</span><h4 class="h-lg">{title}</h4></div>{body}</main>')
        return dk(url, f'<div class="w-app top">{inner}</div>')
    return dk(url, f'<div class="w-app">{side(active)}<div class="w-col">{head(title, eyebrow)}<main class="w-main">{body}</main></div></div>')


PLAN = f'''<div class="list"><div class="li"><span class="chk done">{I("check")}</span><div class="sp st" style="gap:0"><span class="ttl" style="text-decoration:line-through;color:var(--merit-text-tertiary)">Review 12 due cards</span><span class="meta">Biology · done 7:20 am</span></div><b class="num xs t3">+24</b></div>
<div class="li"><span class="chk done">{I("check")}</span><div class="sp st" style="gap:0"><span class="ttl" style="text-decoration:line-through;color:var(--merit-text-tertiary)">Read: Leaf structure §3</span><span class="meta">Biology · done 8:05 am</span></div><b class="num xs t3">+5</b></div>
<div class="li" style="background:var(--merit-surface-selected)"><span class="chk"></span><div class="sp st" style="gap:0"><span class="ttl">10 questions on Rates of reaction</span><span class="meta">Chemistry · weakest high-yield topic · 8 min</span></div><button class="btn s" type="button">Start</button></div></div>'''
SUBJ3 = f'<div class="w-subj3">' + "".join(f'<div class="st" style="align-items:center;gap:6px">{tile(t, 88)}<span class="sm">{n}</span><b class="num xs">{p}%</b></div>' for n, t, p in [("Biology", "biology", 64), ("Chemistry", "chemistry", 41), ("Physics", "physics", 28)]) + '</div>'
TODAY_MAIN = f'''<div class="rw" style="gap:18px"><div class="ring" style="--v:66;--sz:96px;--th:9px;--ring-bg:var(--merit-bg-app)"><svg class="i" style="font-size:36px;color:var(--merit-reward-streak)"><use href="#i-flame-fill"/></svg></div><div class="st" style="gap:4px"><span class="ey">Today · 2 of 3 done</span><h4 class="h-lg">One more keeps your <span class="ul">12-day</span> streak</h4></div></div>{PLAN}'''
RAIL = f'''<aside class="w-rail"><div class="card tight"><span class="ey">A/L 2027 · Biology stream</span><div class="rw" style="align-items:baseline;gap:6px"><b class="num" style="font-size:36px;line-height:1">286</b><span class="t2">days to your exam</span></div><span class="xs t3">Pace: on track for a B in Biology</span></div>
<div class="card tight"><div class="rw"><b class="sm sp">Your subjects</b><a class="lnk">All</a></div>{SUBJ3}</div>
<div class="card flat tight quota"><div class="rw"><span class="t2 sm">Mastery questions</span><b class="num sm">18 of 50</b></div><div class="bar thin"><i style="--v:36%"></i></div><div class="rw"><span class="t2 sm">Past papers</span><b class="num sm">1 of 2</b></div><div class="bar thin"><i style="--v:50%"></i></div></div>
<div class="band achiever"><div><span class="ey">Achiever</span><h4>Practise without limits</h4><p>14 days free in the app</p></div></div></aside>'''

shell_a = app("Today", "Hi, Dilini", f'<div class="w-2col"><div class="st" style="gap:20px">{TODAY_MAIN}</div>{RAIL}</div>', "Good morning")
shell_b = app("Today", "Hi, Dilini", f'<div class="st" style="gap:20px">{TODAY_MAIN}<div class="w-3up">{RAIL.replace("<aside class=\"w-rail\">", "").replace("</aside>", "")}</div></div>', "Good morning", topnav=True)
mob_shell = f'''<div class="ph" style="height:760px"><div class="ph-sb"><span>9:41</span><span class="dots"><i></i><i></i></span></div><div class="scr"><div class="hd"><div class="av sm"></div><span class="sp h-sm">Hi, Dilini</span><span class="hchip cn"><span class="coin"></span>1,240</span></div>{TODAY_MAIN}</div>
<nav class="tabbar"><a class="on">{I("sun-fill")}Today</a><a>{I("books")}Learn</a><a>{I("trophy")}Compete</a><a>{I("user-circle")}Me</a></nav><div class="ph-gest"></div></div>'''
s_shell = screen("web-shell", "Student portal · shell + Today", [("energy", "Energy"), ("gap", "Replaces placeholder")],
    "Navigation B from the app (Today · Learn · Compete · Me). Today reuses the picked mobile Today plan; the wide screen adds a rail with the exam countdown (study plan), the Today-subjects rule (3 → large tiles) and the daily quota. Below 768px both variants become the app layout with a bottom tab bar (right).",
    "GET /today/plan · /students/me/study-plan (exam countdown) · /enrollments · /progress/summary · /quiz/daily-limits · /streak · /points/summary",
    [cand("A", "Sidebar + rail", "Safe", shell_a, "Matches the admin shell the repo already has (shadcn sidebar), so it's cheap. The rail keeps the one next action in the main column.", "Three columns on a 1280 laptop is dense; the rail drops under the plan below 1100px.", "<code>sidebar (pill items)</code><code>header chips</code><code>⌘K search</code><code>rail cards</code>"),
     cand("B", "Top tabs, single column", "Bold", shell_b, "Closest to the app: four tabs, one column, nothing to learn twice. More room for content width.", "Loses the sidebar pattern shared with admin; rail cards become a row under the plan.", "<code>top tab bar</code><code>3-up cards</code>"),
     f'<div class="wf-cand"><div class="wf-cand-h"><b>m</b><span>Phone (both)</span><em>Check</em></div>{mob_shell}<div class="wf-note"><p>Below 768px: bottom tab bar replaces the sidebar or top tabs, header keeps the coin chip only. Same as the Flutter app.</p></div></div>'])

# ---- subject hub
HUB_HERO = f'''<div class="w-hubhero" style="--subj:#4E9A52"><div class="ring" style="--v:64;--sz:104px;--th:6px">{tile("biology", 80)}</div><div class="st sp" style="gap:2px"><span class="ey" style="color:var(--merit-text-secondary)">A/L · Biology stream</span><h4 class="h-xl">Biology</h4><span class="sm t2"><b class="num">64%</b> mastered · 4 of 10 topics · 12 cards due</span></div>
<div class="ftabs"><span class="on">{I("path-fill")}Learn</span><span>{I("target")}Practise</span><span>{I("cards-three")}Cards</span><span>{I("chart-line-up")}Stats</span></div></div>'''
QUILT = '<div class="w-quilt">' + "".join(
    f'<div class="tnode"><div class="pw{" cur" if c else ""}" style="--m:{m}"><img class="base" src="{PW}{t}-tile.svg" alt=""><img class="fill" src="{PW}{t}-tile.svg" alt="">{"<span class=\"ck\">" + I("check") + "</span>" if m == 100 else ""}</div><span class="nm">{n}</span>{"" if m == 100 else f"<span class=\"pc\">{m}%</span>"}</div>'
    for n, t, m, c in [("Introduction", "cells", 100, 0), ("Chemical &amp; cellular basis", "kinetics", 100, 0), ("Evolution &amp; diversity", "circulation", 88, 0), ("Plant form &amp; function", "plants", 52, 1), ("Animal form &amp; function", "thermal", 30, 0), ("Genetics", "magnetism", 8, 0)]) + \
    f'<div class="tnode"><div class="pw lock">{I("lock")}</div><span class="nm t3">Molecular biology</span></div><div class="tnode"><div class="pw lock">{I("lock")}</div><span class="nm t3">Environmental biology</span></div></div>'
PANEL = f'''<aside class="w-panel"><div class="rw"><div class="sp st" style="gap:2px"><span class="ey">Plant form &amp; function</span><b class="h-md">Leaf structure</b></div><span class="ibtn flat">{I("x")}</span></div>
<div class="rw" style="gap:14px"><div class="recipe" style="--sz:120px;margin:0"><div class="st" style="align-items:center;gap:2px">{tile("leaf", 50)}<b class="num" style="font-size:17px">64%</b></div></div><div class="st sp" style="gap:6px"><span class="lg" style="--c:var(--merit-sky-500)">Read · 15</span><span class="lg" style="--c:var(--merit-sage-500)">Remember · 10</span><span class="lg" style="--c:var(--merit-action-primary)">Prove · 75</span></div></div>
<div class="card tight flat" style="flex-direction:row;align-items:center"><span class="mode-ic" style="background:var(--merit-category-2)">{I("book-open")}</span><div class="sp st" style="gap:2px"><b class="sm">1 · Read</b><span class="xs t3">Note finished</span></div></div>
<div class="card tight flat" style="flex-direction:row;align-items:center"><span class="mode-ic" style="background:var(--merit-category-1)">{I("cards-three")}</span><div class="sp st" style="gap:2px"><b class="sm">2 · Remember</b><span class="xs t3">6 cards due · <span class="badge warn">Revise</span></span></div></div>
<div class="card tight flat" style="flex-direction:row;align-items:center"><span class="mode-ic" style="background:var(--merit-category-4)">{I("target")}</span><div class="sp st" style="gap:2px"><b class="sm">3 · Prove</b><span class="xs t3">Best quiz 80%</span></div></div>
<button class="btn full" type="button">Review 6 due cards</button></aside>'''
hub_a = app("Learn", "Biology", f'{HUB_HERO}<div class="w-2col wide">{QUILT}{PANEL}</div>', "Learn", url="meritproject.lk/student/subjects/biology?tab=learn")
TREE = f'''<aside class="w-tree"><b class="sm t3">10 topics</b>''' + "".join(
    f'<div class="w-tn{" on" if o else ""}">{tile(t, 28)}<span class="sp">{n}</span><span class="xs t3">{m}</span></div>' for n, t, m, o in [("Introduction", "cells", "100%", 0), ("Cellular basis", "kinetics", "100%", 0), ("Evolution", "circulation", "88%", 0), ("Plant form", "plants", "52%", 1), ("Animal form", "thermal", "30%", 0), ("Genetics", "magnetism", "8%", 0)]) + \
    '<div class="w-tn t3">' + I("lock") + '<span class="sp">Molecular biology</span></div></aside>'
SUBS = '<div class="w-subgrid">' + "".join(f'<div class="card tight">{tile(t, 56)}<b class="sm">{n}</b><div class="bar thin"><i style="--v:{m}%"></i></div><span class="xs t3">{m}%{x}</span></div>' for n, t, m, x in [("Leaf structure", "leaf", 64, " · 6 due"), ("Photosynthesis", "plants", 43, ""), ("Plant hormones", "waves", 100, " · done"), ("Transpiration", "current", 0, " · locked")]) + '</div>'
hub_b = app("Learn", "Biology", f'''<div class="w-hubbar" style="--subj:#4E9A52">{tile("biology", 44)}<b class="h-md sp">Biology</b><b class="num">64%</b><div class="segc" style="width:360px"><span class="on">Learn</span><span>Practise</span><span>Cards</span><span>Stats</span></div></div>
<div class="w-2col tree">{TREE}<div class="st" style="gap:14px"><div class="rw"><div class="st sp" style="gap:2px"><span class="ey">Topic 4</span><h4 class="h-lg">Plant form &amp; function</h4></div><button class="btn" type="button">Continue Leaf structure</button></div>{SUBS}</div></div>''', "Learn", url="meritproject.lk/student/subjects/biology?tab=learn")
s_hub = screen("web-hub", "Student portal · subject hub", [("energy", "Energy")],
    "The app's hub (tinted header, Learn quilt with mastery fill D18, Read → Remember → Prove sheet, Revise badge) at desktop width. Practise and Stats tabs use the same layout family; Stats carries the Achiever-only detour cards (forecast, high-yield, memory on exam day, peers).",
    "GET /subjects/:id/hierarchy · /progress/subjects/:id · /progress/subtopics/:id (mastery_parts) · /subjects/:id/study-plan · /prediction · /insights · /exam-insights",
    [cand("A", "Tinted hero + quilt + side panel", "Safe", hub_a, "Same hub as the phone, so students moving between devices recognise it. The subtopic sheet docks as a right panel, so the quilt stays visible.", "The hero costs ~180px before content; collapses to a bar on scroll.", "<code>subject tint (D20)</code><code>ring + tile 80</code><code>floating tabs</code><code>quilt (D18)</code><code>side panel</code>"),
     cand("B", "Topic list + subtopic grid", "Bold", hub_b, "Uses the width like a course site: topics stay listed on the left, the open topic's subtopics fill the right. Faster to jump around before a term test.", "Drops the quilt picture that ties web to app; two-pane needs ≥1100px.", "<code>compact tinted bar</code><code>topic list</code><code>subtopic cards</code>")])

# ---- quiz focus + results
QUIZ = f'''<div class="w-focus"><div class="w-ftop"><span class="ibtn flat">{I("x")}</span><span class="sm t3 sp">Question 7 of 50 · 2023 Paper I</span><span class="timer">{I("timer")}1:42:10</span><span class="ibtn flat">{I("flag")}</span><span class="ibtn flat">{I("squares-four")}</span></div><div class="bar thin calm"><i style="--v:14%"></i></div>
<p class="qbody" style="font-size:20px">Which tissue in a dicotyledonous leaf has the most chloroplasts per cell?</p>
<div class="opts"><div class="opt"><span class="k">1</span>Upper epidermis</div><div class="opt sel"><span class="k">2</span>Palisade mesophyll</div><div class="opt"><span class="k">3</span>Spongy mesophyll</div><div class="opt"><span class="k">4</span>Guard cells</div><div class="opt"><span class="k">5</span>Xylem parenchyma</div></div>
<div class="rw"><span class="xs t3 sp">Keys 1–5 pick · Enter next · F flag</span><button class="btn gh" type="button">Previous</button><button class="btn" type="button">Next</button></div></div>'''
RES = f'''<div class="w-focus"><div class="rw" style="gap:16px"><div class="grade">A</div><div class="st sp" style="gap:2px"><span class="ey">Mastery · Leaf structure</span><h4 class="h-lg">Great session!</h4><span class="sm t2">8 of 10 · 80% · 6 min 12 s</span></div><span class="ibtn flat">{I("share-network")}</span></div>
<div class="card" style="gap:12px"><div class="rw"><span class="ey sp" style="color:var(--merit-text-secondary)">Points earned</span><span class="coin lg" style="--coin:28px"></span><b class="num" style="font-size:28px">+100</b></div>
<div class="pbar"><i style="width:53%;background:var(--merit-action-primary)"></i><i style="width:13%;background:var(--merit-butter-500)"></i><i class="ghost" style="width:34%"></i></div>
<div class="rw xs t2" style="gap:14px"><span>80 correct answers</span><span>+20 accuracy bonus (80%+)</span><span class="t3">+50 with Achiever</span></div></div>
<button class="btn gh full" type="button">{I("caret-down")}Review 2 mistakes</button><div class="rw"><span class="sp"></span><button class="btn" type="button">Done</button></div></div>'''
quiz_frame = dk("meritproject.lk/student/quiz/8f2c…", f'<div class="w-app focus">{QUIZ}</div>', 560)
res_frame = dk("meritproject.lk/student/quiz/8f2c…/results", f'<div class="w-app focus">{RES}</div>', 560)
s_quiz = screen("web-quiz", "Student portal · quiz focus + results", [("calm", "Calm"), ("energy", "Energy"), ("gap", "Approve")],
    "Quiz taking drops the sidebar (focus layout, 720px column) and adds keyboard keys. Results follow round 10 pick A: calm points card from <code>points_breakdown</code>, review opens in place, Done is the only action. Share = username + score (D25).",
    "POST /quiz/sessions/{paper|mastery|adaptive} · /answers · /complete · GET /quiz/sessions/:id",
    [f'<div class="wf-cand"><div class="wf-cand-h"><b>1</b><span>Taking (paper)</span><em>Approve</em></div>{quiz_frame}<div class="wf-note"><p>Colour-only timer (D19), counts down, auto-submits at 0:00. Pause/submit dialogs as mobile.</p></div></div>',
     f'<div class="wf-cand"><div class="wf-cand-h"><b>2</b><span>Results</span><em>Approve</em></div>{res_frame}<div class="wf-note"><p>Same card as the app after round 10. Limit reached → limit sheet (dialog on web); Adaptive for Wanderer → plans page.</p></div></div>'])

# ---- compete
PODIUM = f'''<div class="card" style="gap:12px"><div class="rw"><b class="h-sm sp">Gampaha top 3</b><div class="segc" style="width:240px"><span>School</span><span class="on">District</span><span>Island</span></div></div>
<div class="podium"><div class="p2"><div class="av"></div><span class="nm">Kasun P.</span><span class="pt">4,610</span><div class="step">2</div></div><div class="p1">{I("crown-fill")}<div class="av lg" style="width:56px;height:56px"></div><span class="nm">Nethmi R.</span><span class="pt">4,820</span><div class="step">1</div></div><div class="p3"><div class="av"></div><span class="nm">Tharushi S.</span><span class="pt">4,390</span><div class="step">3</div></div></div>
<div class="lrow me"><span class="rk">38</span><div class="av sm"></div><span class="nm">You<small>12 behind #37</small></span><span class="pt">1,240</span></div><a class="lnk">Full leaderboard</a></div>'''
WEEK = '<div class="card" style="gap:10px"><div class="rw"><span class="coin"></span><b class="h-sm sp">This week</b><b class="num">+610</b></div><div class="w-bars">' + "".join(f'<div><i style="--h:{h}%"{" class=\"t\"" if d == "S" and k == 5 else ""}></i><span>{d}</span></div>' for k, (d, h) in enumerate([("M", 30), ("T", 55), ("W", 20), ("T", 70), ("F", 40), ("S", 85), ("S", 0)])) + '</div></div>'
STREAKC = f'<div class="card" style="gap:10px"><div class="rw">{I("flame-fill")}<b class="h-sm sp">12-day streak</b><span class="xs t3">Best 21</span></div><div class="week"><div><i class="d">{I("check")}</i>M</div><div><i class="d">{I("check")}</i>T</div><div><i class="d">{I("check")}</i>W</div><div><i class="d">{I("check")}</i>T</div><div><i class="d">{I("check")}</i>F</div><div><i class="t">{I("flame")}</i>S</div><div><i></i>S</div></div></div>'
SHELF = f'<div class="card" style="gap:10px"><div class="rw"><b class="h-sm sp">Achievements</b><a class="lnk">7 of 24</a></div><div class="rw" style="gap:14px"><span class="medal" style="background:var(--merit-butter-300)">{I("flame-fill")}</span><span class="medal" style="background:var(--merit-sage-300)">{I("cards-three-fill")}</span><span class="medal" style="background:var(--merit-sky-300)">{I("exam-fill")}</span><span class="medal off">{I("book-open")}</span><span class="medal off">{I("users")}</span></div></div>'
TASKS = f'<div class="list"><div class="li"><span class="mode-ic" style="background:var(--merit-category-2)">{I("chat-circle-text-fill")}</span><div class="sp st" style="gap:0"><span class="ttl">Quick survey: study habits</span><span class="meta">About 3 min · ends in 4 days</span></div><b class="num">+50</b><button class="btn s" type="button">Start</button></div><div class="li"><span class="mode-ic" style="background:var(--merit-category-6)">{I("user-plus-fill")}</span><div class="sp st" style="gap:0"><span class="ttl">Study Squad · 2 of 5 friends</span><span class="meta">Code DILINI7</span></div><b class="num">+500</b></div></div>'
compete = app("Compete", "Compete", f'<div class="w-2col even"><div class="st" style="gap:16px">{PODIUM}</div><div class="st" style="gap:16px">{WEEK}{STREAKC}{SHELF}</div></div><b class="h-sm">Tasks</b>{TASKS}', "Gampaha · A/L 2027", url="meritproject.lk/student/compete")
s_comp = screen("web-compete", "Student portal · Compete", [("energy", "Energy"), ("gap", "Approve")],
    "Round 10 Compete (A with B's podium preview) laid out in two columns: rank on the left, this week on the right, Tasks below. Same data limits as the app (week bars from history, streak dots inferred, gap only within the top 50).",
    "GET /leaderboards/me/ranks · /leaderboards/districts/:name · /points/summary · /points/history · /streak · /students/me/achievements · /tasks",
    [f'<div class="wf-cand"><div class="wf-cand-h"><b>1</b><span>Compete root</span><em>Approve</em></div>{compete}<div class="wf-note"><p>Leaderboard, Points, Achievements and Tasks open as their own pages with the same layouts as the app.</p></div></div>'])

# ---- me
ME_LEFT = f'''<div class="card" style="align-items:center;text-align:center;gap:8px"><div style="position:relative"><div class="av lg" style="width:96px;height:96px"></div><span class="ibtn" style="position:absolute;right:-6px;bottom:-4px;width:34px;height:34px;font-size:16px">{I("pencil-simple")}</span></div><b class="h-md">Dilini Perera</b><span class="sm t3">dilini_p · A/L 2027 · Gampaha</span><span class="badge">Wanderer</span>
<div class="stat3" style="width:100%"><div><b>1,240</b><span class="xs t3">Points</span></div><div><b>12</b><span class="xs t3">Streak</span></div><div><b>#38</b><span class="xs t3">District</span></div></div></div>
<div class="band achiever"><div><span class="ey">Achiever</span><h4>Practise without limits</h4><p>14 days free in the app</p></div></div>'''
def sec(h, rows):
    return f'<span class="set-h">{h}</span><div class="list">' + "".join(rows) + '</div>'
ME_RIGHT = (sec("Study", [f'<div class="li">{I("translate")}<div class="sp st" style="gap:0"><span class="ttl">Content language</span><span class="meta">Switch it on each subject&rsquo;s page (Gate 0). The study reminder is hidden for v1.</span></div></div>'])
            + sec("App", [f'<div class="li">{I("moon")}<span class="sp ttl">Appearance</span><div class="segc" style="width:200px;padding:3px"><span>Light</span><span>Dark</span><span class="on">Auto</span></div></div>',
                          f'<div class="li">{I("sliders")}<div class="sp st" style="gap:0"><span class="ttl">Theme</span><span class="meta">Merit (default) · other colour themes</span></div>{I("caret-right")}</div>'])
            + sec("Account", [f'<div class="li">{I("user")}<span class="sp ttl">Account details</span>{I("caret-right")}</div>', f'<div class="li">{I("crown")}<div class="sp st" style="gap:0"><span class="ttl">Subscription</span><span class="meta">Wanderer · manage in the app</span></div>{I("caret-right")}</div>',
                              f'<div class="li">{I("key")}<span class="sp ttl">Change password</span>{I("caret-right")}</div>', f'<div class="li">{I("sign-out")}<span class="sp ttl">Log out</span></div>', f'<div class="li" style="color:var(--merit-feedback-error)">{I("trash")}<span class="sp ttl">Delete account</span></div>']))
me = app("Me", "Me", f'<div class="w-2col me"><div class="st" style="gap:16px">{ME_LEFT}</div><div class="st" style="gap:10px">{ME_RIGHT}</div></div>', url="meritproject.lk/student/me")
s_me = screen("web-me", "Student portal · Me", [("energy", "Energy"), ("gap", "Approve")],
    "D23 on the web: profile card left, Study / App / Account sections right, no Settings page. Web adds a Theme row (D26: Merit default, other tweakcn presets opt-in). Subscription is read-only here; managing it happens in the store.",
    "GET /user · /students/me · /enrollments · /students/me/reminders · /avatars · PUT /user · PUT /enrollments/:id/language",
    [f'<div class="wf-cand"><div class="wf-cand-h"><b>1</b><span>Me</span><em>Approve</em></div>{me}<div class="wf-note"><p>Avatar picker opens as a dialog with the 30-avatar grid plus "Upload a photo", as in the app.</p></div></div>'])

# ---- premium
QR = '<div class="w-qr">' + "".join(f'<i class="{"b" if (k * 7 + k // 9) % 3 == 0 or k % 11 == 0 else ""}"></i>' for k in range(81)) + '</div>'
prem = app("Me", "Achiever", f'''<div class="w-2col even"><div class="st" style="gap:14px"><div class="band achiever"><div><span class="ey">Achiever</span><h4>Study without limits</h4><p>Everything in Wanderer, plus more</p></div></div>
<div class="benefit"><span class="mode-ic" style="background:var(--merit-category-4)">{I("infinity")}</span><div class="st" style="gap:0"><b class="sm">Unlimited questions and papers</b><span class="sm t3">You used 48 of 50 today</span></div></div>
<div class="benefit"><span class="mode-ic" style="background:var(--merit-category-5)">{I("brain")}</span><div class="st" style="gap:0"><b class="sm">Adaptive mode and exam forecast</b><span class="sm t3">Practise exactly where you're weak</span></div></div>
<div class="benefit"><span class="mode-ic" style="background:var(--merit-butter-100)"><span class="coin"></span></span><div class="st" style="gap:0"><b class="sm">1.5× points on everything</b><span class="sm t3">Today's 124 would have been 186</span></div></div></div>
<div class="card" style="gap:12px;align-items:center;text-align:center"><b class="h-md">Get Achiever in the Merit app</b><span class="sm t2">14 days free, then Rs 4,990 a year or Rs 599 a month. Your web account unlocks as soon as you subscribe.</span>{QR}<span class="xs t3">Scan with your phone</span><div class="rw"><span class="w-store">Google Play</span><span class="w-store">App Store</span></div></div></div>''', url="meritproject.lk/student/premium")
s_prem = screen("web-premium", "Student portal · Achiever (buy in the app)", [("energy", "Energy"), ("gap", "Approve")],
    "No web checkout this pass. The page sells with the student's own numbers (paywall A), then hands off to the app with a QR code and store links. Achiever status from the backend unlocks web features straight away.",
    "GET /students/me/subscription · /quiz/daily-limits · /points/summary",
    [f'<div class="wf-cand"><div class="wf-cand-h"><b>1</b><span>Achiever page</span><em>Approve</em></div>{prem}<div class="wf-note"><p>Locked features (Adaptive, Stats cards) and limit dialogs link here.</p></div></div>'])


# ---------------------------------------------------------------- board helpers (shared by gen_web_board.py and r12_*.py)
def kit_screen(sid, title, tags, desc, data, frames):
    tg = "".join(f'<span class="tag {c}">{t}</span>' for c, t in tags)
    d = f'<span class="wf-data">{data}</span>' if data else ""
    body = "".join(f'<div class="wf-cand"><div class="wf-cand-h"><b>{i + 1}</b><span>{n}</span><em>Approve</em></div>{f}<div class="wf-note"><p>{note}</p></div></div>' for i, (n, f, note) in enumerate(frames))
    return (f'<article class="wf-screen" data-screen="{sid}"><div class="wf-screen-h"><h3>{title}</h3>{tg}<p>{desc}</p>{d}</div>'
            f'<div class="wf-vars desk">{body}</div><div class="wf-feedback"><label for="fb-{sid}">Notes on {title.split(" ·")[0]}</label>'
            f'<textarea id="fb-{sid}" rows="2"></textarea><span class="wf-saved"></span></div></article>')


def flow(fid, title, intro, legend, screens, first=False):
    lg = "".join(f'<span class="tag {c}">{t}</span>' for c, t in legend)
    return (f'<!-- ======================================================= {fid.upper()} -->\n'
            f'<section class="wf-flow web" data-flow="{fid}"{"" if first else " hidden"}>\n'
            f'<div class="wf-intro"><h2>{title}</h2><p>{intro}</p><div class="wf-legend">{lg}</div></div>\n'
            + "\n".join(screens) + "\n</section>\n")


def phone(body, h=720, tab=None):
    nav = ""
    if tab:
        nav = '<nav class="tabbar">' + "".join(f'<a class="{"on" if l == tab else ""}">{I(i + ("-fill" if l == tab else ""))}{l}</a>' for i, l in NAV) + '</nav>'
    return f'<div class="ph" style="height:{h}px"><div class="ph-sb"><span>9:41</span><span class="dots"><i></i><i></i></span></div><div class="scr">{body}</div>{nav}<div class="ph-gest"></div></div>'
