"""Round 12 hub frames: subject hub A (tinted hero + quilt + docked panel) with the mobile app's
text-only section tabs (MeritHubHeader), four tabs + collapsed state, and the Learn root.
Must not import gen_web_board (circular)."""
from gen_web import *  # noqa: F401,F403

URL = "meritproject.lk/student/subjects/biology?tab="
SECTIONS = ["Learn", "Practise", "Cards", "Stats"]


def _tabs(active):
    return '<nav class="htabs" role="tablist">' + "".join(
        f'<a class="{"on" if s == active else ""}" role="tab" aria-selected="{"true" if s == active else "false"}"><span>{s}</span></a>' for s in SECTIONS) + '</nav>'


def hub_head(active, collapsed=False):
    bar = (f'<div class="hh-bar"><span class="ibtn" aria-label="Back">{I("arrow-left")}</span>'
           f'<div class="mini">{tile("biology", 32)}<b class="t">Biology</b><b class="num">64%</b></div><span class="fill"></span>'
           f'<span class="hchip fl">{I("flame-fill")}12</span><span class="ibtn" aria-label="More">{I("dots-three")}</span></div>')
    hero = (f'<div class="hh-hero"><div class="ring" style="--v:64;--sz:104px;--th:6px">{tile("biology", 80)}</div>'
            f'<div class="st sp" style="gap:2px"><span class="ey">A/L · Biology stream</span><h4>Biology</h4>'
            f'<span class="sm"><b class="num">64%</b> mastered · 4 of 10 topics · 12 cards due</span></div></div>')
    return f'<header class="hh{" col" if collapsed else ""}" style="--subj:#4E9A52">{bar}{hero}{_tabs(active)}</header>'


def hub(active, body, collapsed=False):
    return app("Learn", "Learn", f'{hub_head(active, collapsed)}<div class="hh-body">{body}</div>', "", url=URL + active.lower())


# ------------------------------------------------------------------ Learn
learn_body = f'<div class="w-2col wide">{QUILT}{PANEL}</div>'

# ------------------------------------------------------------------ Practise
def _paper(y, meta, right):
    return (f'<div class="li"><span class="mode-ic" style="background:var(--merit-category-2)">{I("exam")}</span>'
            f'<div class="sp st" style="gap:0"><span class="ttl">{y} · Paper I</span><span class="meta">{meta}</span></div>{right}</div>')

def _attempt(ic, col, ttl, meta, pct, cls=""):
    return (f'<div class="li"><span class="mode-ic" style="background:var(--merit-category-{col})">{I(ic)}</span>'
            f'<div class="sp st" style="gap:0"><span class="ttl">{ttl}</span><span class="meta">{meta}</span></div><span class="badge {cls}">{pct}</span></div>')

practise_body = f'''<div class="hp-quota">{I("hourglass")}32 mastery questions and 1 paper left today<span class="badge">Wanderer</span><span class="sp" style="flex:1"></span><span class="xs t3">+10 per correct · +20 at 80% or above · ×1.5 Achiever</span></div>
<div class="hp-modes">
<div class="card hp-mode"><span class="mode-ic" style="background:var(--merit-category-1)">{I("target")}</span><div class="st" style="gap:2px"><b class="h-sm">Mastery by topic</b><span class="sm t2">Pick a topic or subtopic. Answers are explained as you go.</span></div><span class="grow"></span><span class="xs t3">Suggested: Leaf structure · 64%</span><button class="btn" type="button">Start 10 questions</button></div>
<div class="card hp-mode"><span class="mode-ic" style="background:var(--merit-category-2)">{I("exam")}</span><div class="st" style="gap:2px"><b class="h-sm">Paper mode</b><span class="sm t2">Timed past papers, 50 MCQ in 2 hours. Pick a year below.</span></div><span class="grow"></span><span class="xs t3">12 papers · 1 paused</span><button class="btn gh" type="button">Choose a paper</button></div>
<div class="card hp-mode lock"><span class="mode-ic" style="background:var(--merit-category-5)">{I("brain")}</span><div class="st" style="gap:2px"><b class="h-sm">Adaptive</b><span class="sm t2">Questions from your 5 weakest subtopics.</span></div><span class="grow"></span><span class="badge pro" style="align-self:flex-start">{I("lock-key-fill")}Achiever</span><button class="btn gh dis" type="button">Try 14 days free</button></div>
</div>
<div class="hp-2"><div class="st" style="gap:10px"><div class="sec-h"><b class="h-sm">Past papers</b><a class="lnk">All 12</a></div>
<div class="hp-years"><span class="on">2023</span><span>2022</span><span>2021</span><span>2020</span><span>2019</span><span>2018</span><span>2017</span><span>+5</span></div>
<div class="list">{_paper("2023", "50 MCQ · 2 hours · Official", '<span class="badge ok">Best 72%</span>')}{_paper("2022", "50 MCQ · 2 hours · Official", '<span class="badge">New</span>')}{_paper("2021", "Paused at Q23 · 48 min left", '<button class="btn gh s" type="button">Resume</button>')}</div></div>
<div class="st" style="gap:10px"><div class="sec-h"><b class="h-sm">Recent attempts</b><a class="lnk">All 18</a></div>
<div class="list">{_attempt("target", 1, "Mastery · Leaf structure", "Today · 8 of 10 · 6 min", "80%", "ok")}{_attempt("exam", 2, "Paper · 2022 Paper I", "Yesterday · 31 of 50", "62%")}{_attempt("target", 1, "Mastery · Photosynthesis", "Mon · 6 of 10", "60%")}{_attempt("exam", 2, "Paper · 2021 Paper I", "Last week · 29 of 50", "58%")}</div></div></div>'''

# ------------------------------------------------------------------ Cards
def _deck(tone, wash, badge, name, n, extra=""):
    return (f'<div class="card" style="background:var(--merit-flashcard-{tone}-bg);color:var(--merit-ink-900)"><span class="wash" style="--wash:url(\'{PW}{wash}-wash.svg\');--wash-ink:var(--merit-flashcard-{tone}-wash);opacity:.3"></span>'
            f'{badge}<b class="h-sm">{name}</b><span class="xs">{n} cards{extra}</span></div>')

_b = lambda t, c="hot": f'<span class="badge {c}" style="position:absolute;top:12px;left:12px">{t}</span>'
cards_body = f'''<div class="card hc-cta"><span class="mode-ic" style="background:var(--merit-category-1);width:56px;height:56px;font-size:28px">{I("cards-three-fill")}</span><div class="sp st" style="gap:2px"><span class="ey">Remember</span><b class="h-md">12 cards due across 3 sets</b><span class="sm t2">About 5 minutes. Spaced review keeps what you read from fading.</span></div><button class="btn l" type="button">{I("cards-three-fill")}Study all due · 12</button></div>
<div class="sec-h"><b class="h-sm">Card sets by topic</b><span class="xs t3">Sorted by due, then topic order</span></div>
<div class="hc-deck">{_deck("sage", "leaf", _b("6 due"), "Leaf structure", 14)}{_deck("sky", "cells", _b("3 due"), "Cell organelles", 22)}{_deck("coral", "circulation", _b("3 due"), "Circulation", 18)}{_deck("violet", "magnetism", _b("10 new", ""), "Enzymes", 10)}
{_deck("butter", "plants", _b("Done", ""), "Plant hormones", 16)}
<div class="card" style="background:var(--merit-surface-sunken);box-shadow:none"><span class="badge" style="position:absolute;top:12px;left:12px">{I("lock")}Locked</span><b class="h-sm t3">Transpiration</b><span class="xs t3">Unlocks at 70% Leaf structure</span></div>
<div class="card" style="background:var(--merit-surface-sunken);box-shadow:none"><span class="badge" style="position:absolute;top:12px;left:12px">{I("lock")}Locked</span><b class="h-sm t3">Genetics</b><span class="xs t3">Unlocks at 70% Animal form</span></div>
<div class="card" style="box-shadow:inset 0 0 0 1.5px var(--merit-border-subtle);background:transparent;align-items:center;justify-content:center;text-align:center"><span class="mode-ic" style="background:var(--merit-surface-sunken)">{I("plus")}</span><b class="sm">Make your own set</b></div></div>'''

# ------------------------------------------------------------------ Stats
_topics = [("cells", "Introduction", 100), ("kinetics", "Cellular basis", 100), ("circulation", "Evolution &amp; diversity", 88), ("plants", "Plant form &amp; function", 52), ("thermal", "Animal form &amp; function", 30), ("magnetism", "Genetics", 8)]
_rows = "".join(f'<div class="hs-row">{tile(t, 28)}<div class="nm"><span>{n}</span><div class="bar thin"><i style="--v:{m}%"></i></div></div><b class="num">{m}%</b></div>' for t, n, m in _topics)
_pts = [(0, 118), (60, 110), (120, 104), (180, 92), (240, 84), (300, 70), (360, 66), (420, 52), (480, 48), (540, 38)]
_line = " ".join(f"{x},{y}" for x, y in _pts)
_trend = (f'<div class="hs-trend"><svg viewBox="0 0 540 140" preserveAspectRatio="none"><g stroke="var(--merit-border-subtle)" stroke-width="1" vector-effect="non-scaling-stroke"><path d="M0 20H540M0 70H540M0 120H540"/></g>'
          f'<polyline points="{_line}" fill="none" stroke="var(--merit-action-primary)" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"/>'
          f'<circle cx="540" cy="38" r="5" fill="var(--merit-action-primary)"/></svg></div>')

def _lock(ey, ttl, txt):
    return (f'<div class="card hs-lock"><div class="top"><span class="ey">{ey}</span><span class="sp"></span><span class="badge pro">{I("lock-key-fill")}Achiever</span></div>'
            f'<b class="h-sm">{ttl}</b><span class="sm t2">{txt}</span></div>')

stats_body = f'''<div class="hs"><div class="hs-col">
<div class="card"><div class="rw"><div class="sp st" style="gap:2px"><span class="ey">Mastery over time</span><b class="h-md">64% now, up 9 points in 4 weeks</b></div><div class="segc" style="width:200px"><span>4 wk</span><span class="on">12 wk</span><span>All</span></div></div>{_trend}<div class="rw xs t3" style="justify-content:space-between"><span>Aug</span><span>Sep</span><span>Oct</span></div></div>
<div class="card"><div class="rw"><b class="h-sm sp">Topic breakdown</b><a class="lnk">All 10 topics</a></div>{_rows}</div></div>
<div class="hs-col"><div class="card" style="flex-direction:row;align-items:center;gap:14px"><span class="slgrade" style="width:56px;height:56px;font-size:30px;border-radius:18px;background:var(--merit-sage-100)">B</span><div class="st" style="gap:2px"><span class="ey">If the exam were today</span><b class="h-sm">Likely a B (65–74%)</b><span class="sm t2">Medium confidence · 3 papers used</span></div></div>
<div class="card" style="gap:6px"><span class="ey">Watch out</span><b class="h-sm">Circulation cards are fading</b><span class="sm t2">7 cards drop below 70% recall this week.</span><button class="btn s gh" type="button" style="align-self:flex-start">Review 7 cards</button></div>
<div class="sec-h"><b class="h-sm">Go deeper</b><span class="xs t3">Achiever</span></div>
<div class="hs-detour">{_lock("Forecast", "Grade forecast", "Where your grade lands by August, with a range.")}{_lock("High-yield", "Genetics · about 9 marks", "Topics that come up most that you have not covered.")}{_lock("Exam day", "Memory on exam day", "What you will still remember when the paper starts.")}{_lock("Peers", "Peers", "How your pace compares with your cohort.")}</div>
<span class="xs t3">Wanderer sees one line of each as a teaser. 14 days of Achiever are free.</span></div></div>'''

# ------------------------------------------------------------------ frames
f_learn, f_prac, f_cards, f_stats = (hub(t, b) for t, b in [("Learn", learn_body), ("Practise", practise_body), ("Cards", cards_body), ("Stats", stats_body)])
f_col = hub("Learn", f'<div class="hh-fade"><div class="w-2col wide">{QUILT}{PANEL}</div></div>', collapsed=True)

SPEC = ("<b>Section tabs</b> (port of <code>MeritHubHeader</code> / <code>_SectionTabs</code>, mobile value in brackets): text only, no icons or chips, "
        "Learn · Practise · Cards · Stats, left-aligned on the header's 24px inset [16], baseline-aligned. General Sans 600, line-height 1.2, letter-spacing -0.01em. "
        "<b>Expanded:</b> active 28px [24] in <code>text.primary</code>, idle 16px [15] in <code>text.secondary</code>, gap 24px [18], row height 52 [46], 8px below [6]. "
        "<b>Collapsed:</b> active 20px [18], idle 14px [13], gap 18px [14], row height 40 [34], 5px below [4]. "
        "Each tab's min-height is max(active × 1.4, 30). Active tab carries the brush underline (<code>assets/v3/motifs/brush-underline.svg</code>, colour <code>decor.underline</code>): "
        "height 0.3 × font-size, bottom -0.1 × size, 0.04 × size wider each side. Whole label is the hit target; use <code>role=tablist</code> and <code>aria-selected</code>. "
        "<b>Header:</b> sticky at the top of the main column (below the app's top bar, so it never leaves the screen), subject tint (30% subject over bg) with a 1.5px rim, bottom radius 36 [32] collapsing to 26 [24], shadow e0 to e1. "
        "Expanded height is 240 [208]: bar 64 [56] + hero 124 [106] + tabs 52 [46]. Hero: mastery ring 104 [92] (6px stroke) around a 80 [72] tile, eyebrow, 38px title [32], summary 15px [13]. "
        "<b>Collapse:</b> t = clamp(scroll ÷ 136px) [118], where 136 is expanded minus collapsed height (240 − 104). Hero opacity = 1 − 1.8t (gone by t≈0.55) and slides up 24t; "
        "the compact bar content (tile 32, title 20px, % figure 16px) fades in from t 0.55 to 1; the streak chip leaves with the hero. Collapsed height is 104 [90]: bar 64 + tabs 40. "
        "All text on the tint is <code>text.primary</code> or <code>text.secondary</code> only. The right-hand panel on Learn docks beside the quilt and stays sticky below the header.")

_note = lambda s: s
s_hub = kit_screen("web-hub", "Student portal · subject hub", [("energy", "Energy"), ("gap", "Hub A picked")],
    "Hub A (tinted hero, topic quilt, docked side panel) is the pick. The tab switcher now matches the mobile app: text-only sections where the active name grows and carries the brush underline, replacing the icon chips. "
    "Four tabs at 1280, then the collapsed-on-scroll state. " + SPEC,
    "GET /subjects/:id/hierarchy · /progress/topics · /flashcards/due · /quiz/daily-limits · /quiz/attempts · /subjects/:id/prediction · /insights · /exam-insights · /peers",
    [("Learn", f_learn, "Quilt plus docked panel. The panel opens on the selected topic (Read → Remember → Prove)."),
     ("Practise", f_prac, "Mastery by topic, Paper mode with years, Adaptive locked for Wanderer. Mirrors the mobile Practise frame; recent attempts sit beside the papers."),
     ("Cards", f_cards, "One primary action (study all due), then per-topic sets with due counts. Locked sets show what unlocks them."),
     ("Stats", f_stats, "Mastery over time and topic breakdown for everyone; forecast, high-yield, exam-day memory and peers are Achiever teasers."),
     ("Collapsed on scroll", f_col, "Scrolled past 136px: hero gone, 32px tile + title + % in the bar, tabs shrink and stay pinned. Content scrolls underneath.")])

# ------------------------------------------------------------------ Learn root
_sj = [("Biology", "biology", 64, "12 cards due", "#4E9A52"), ("Chemistry", "chemistry", 41, "3 due", "#03999A"), ("Physics", "physics", 28, "nothing due", "#4C88D3"), ("English", "languages", 72, "5 due", "#9884F3")]
LEARN12 = '<div class="hl-list">' + "".join(
    f'<div class="card hl-sj" style="--subj:{c}"><div class="ring" style="--v:{m};--sz:96px;--th:6px">{tile(t, 74)}</div><div class="sp st" style="gap:2px"><span class="ey">A/L · Science</span><b class="h-md">{n}</b><span class="sm t2"><b class="num">{m}%</b> mastered · {d}</span></div>{I("caret-right")}</div>'
    for n, t, m, d, c in _sj) + \
    f'<div class="card hl-sj add"><span class="mode-ic" style="background:var(--merit-surface-sunken);width:56px;height:56px">{I("plus")}</span><div class="sp st" style="gap:2px"><b class="h-md">Add a subject</b><span class="sm t2">1 slot left on Wanderer</span></div></div></div>'
learn_root = app("Learn", "Your subjects", LEARN12, "Learn · 4 of 5", url="meritproject.lk/student/learn")

s_subj = kit_screen("web-subjects-more", "Subjects · Learn root", [("energy", "Energy"), ("gap", "Approve")],
    "Learn root lists enrolled subjects as cards tinted with each subject's colour, with the mastery ring around the tile, so a card is the hub header in miniature. "
    "The add tile shows free slots (capacity from <code>/enrollments/capacity</code>). Stats moved into the hub as a tab. Opening a card lands on <code>?tab=learn</code>.",
    "GET /enrollments · /enrollments/capacity · /progress/summary",
    [("Learn root", learn_root, "Click a card to open its hub on the Learn tab.")])
