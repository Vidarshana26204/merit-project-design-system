"""Round 13 landing: store badges, live feature sections on real data (try a question, flashcards, exam insights),
pricing, FAQ and the closing CTA. Must not import gen_web_board (circular). Widgets: landing-live.js; styles: wf-r13-landing.css;
data: qm-samples.js (build_samples.py, read-only from merit_rehearsal) and qm-data.js (/public/explore snapshot)."""
import json
import os

from gen_web import *  # noqa: F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
_raw = open(os.path.join(HERE, "qm-samples.js")).read()
SAMPLES = json.loads(_raw[_raw.index("= ") + 2:].rstrip().rstrip(";"))

# Store badges. Board stand-ins: production uses the official Apple and Google badge artwork and follows their guidelines.
PLAY = ('<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4.6 2.9c-.3.3-.5.7-.5 1.2v15.8c0 .5.2.9.5 1.2l8.9-9.1L4.6 2.9zm9.9 8.1 2.6-2.6L6.4 2.3c-.3-.2-.6-.3-.9-.3l9 9zm0 2-9 9c.3 0 .6-.1.9-.3l10.7-6.1-2.6-2.6zm5.6-2.9-2.2-1.3-2.8 2.9 2.8 2.9 2.2-1.3c.9-.5.9-2.7 0-3.2z"/></svg>')


def badges(cls=""):
    return (f'<div class="r13-badges {cls}">'
            f'<a class="r13-badge" href="#" aria-label="Download on the App Store">{I("apple-logo")}<span><small>Download on the</small>App Store</span></a>'
            f'<a class="r13-badge" href="#" aria-label="Get it on Google Play">{PLAY}<span><small>Get it on</small>Google Play</span></a></div>')


# ---- facts the copy may claim (computed from the snapshot, never hand-written)
SUBJ = SAMPLES["subjects"]
Y0 = min(s["y0"] for s in SUBJ if s["y0"])
Y1 = max(s["y1"] for s in SUBJ if s["y1"])
OLDEST = min((s for s in SUBJ if s["y0"]), key=lambda s: s["y0"])
PAPER_SUBJECTS = ", ".join(s["t"].replace("Information & Communication Technology", "ICT") for s in SUBJ if s["pq"])
N_Q = sum(s["pq"] for s in SUBJ)

# ---- sections
SEC_TRY = f'''<section class="w-sec r13-sec" id="try" data-lq><div class="r13-2col">
<div class="st r13-lead"><span class="ey">Real past papers</span><h3 class="w-h2">Try one. It's a <span class="ul">real</span> exam question.</h3>
<p class="t2">Every question comes from an official A/L paper, with the answer explained. Pick a subject and give it a go: no account needed.</p>
<div class="r13-chips" data-lq-chips></div><span class="sm t3" data-lq-src></span><span class="xs t3">Keys 1 to 5 answer · Enter for the next one</span></div>
<div class="card r13-qcard" data-lq-card tabindex="0" aria-label="Past-paper question"></div></div></section>'''

SEC_CARDS = f'''<section class="w-sec r13-sec" id="cards" data-lf><div class="r13-2col rev">
<div class="r13-deck"><div class="r13-stage" data-lf-stage tabindex="0" aria-label="Flashcard: click or press Space to flip"></div>
<div class="fsrs r13-rate" data-lf-rate role="group" aria-label="Flashcard actions"></div></div>
<div class="st r13-lead"><span class="ey">Flashcards</span><h3 class="w-h2">Cards come back right <span class="ul">before</span> you forget.</h3>
<p class="t2">Flip a card, say how well you knew it, and Merit schedules the next review. Easy ones wait longer; hard ones return sooner.</p>
<div class="r13-chips" data-lf-chips></div><span class="sm t3" data-lf-count></span><span class="xs t3">Space flips · keys 1 to 4 rate · real intervals for a new card</span></div></div></section>'''

SEC_INSIGHTS = f'''<section class="w-sec r13-sec" id="insights" data-li><div class="r13-2col">
<div class="st r13-lead"><span class="ey">Exam insights</span><h3 class="w-h2">See what each paper <span class="ul">really</span> asks.</h3>
<p class="t2">Every past-paper question is mapped to its topic, so you can see where the marks are and spend your time there.</p>
<div class="r13-chips" data-li-chips></div><a class="btn s r13-licta" href="#" data-li-cta></a></div>
<div class="card r13-chart"><div data-li-chart class="li-chart"></div><p class="sm t2 li-note" data-li-note aria-live="polite"></p></div></div></section>'''

PRICING = f'''<section class="w-sec r13-sec" id="pricing"><h3 class="w-h2" style="text-align:center">Free to start. <span class="ul">Achiever</span> when you're ready.</h3><div class="w-plans">
<div class="card w-plan"><span class="badge">Wanderer</span><b class="w-price">Free</b><span class="sm t2">Forever</span><ul class="w-ul"><li>50 mastery questions a day</li><li>2 past papers a day</li><li>Flashcards and notes</li><li>Subjects: cap to confirm (2 or 5)</li></ul><button class="btn gh full" type="button">Start free</button></div>
<div class="card w-plan pro"><span class="badge pro">Achiever</span><b class="w-price">Rs —<small>/year</small></b><span class="sm">or Rs — a month · 14 days free</span><ul class="w-ul"><li>Unlimited questions and papers</li><li>Adaptive mode and exam forecast</li><li>1.5× points on everything</li><li>Bought in the Merit app</li></ul>{badges("on-feature")}</div></div>
<p class="xs t3" style="text-align:center">Prices to be confirmed. Buying happens in the app, through the App Store or Google Play.</p></section>'''

FAQS = [
    ("Is Merit free?", "Yes. The Wanderer plan is free forever: 50 mastery questions and 2 past papers a day, plus flashcards and notes. Achiever removes the limits."),
    ("Which past papers are included?", f"Official A/L papers up to {Y1}, from {OLDEST['y0']} for {OLDEST['t']}, in {PAPER_SUBJECTS}: {N_Q:,} questions so far, each mapped to its topic. More subjects and years are being added."),
    ("Can I study in Sinhala or Tamil?", "Subject content comes in English, Sinhala and Tamil where it is available, and you can pick the language per subject. The app's menus stay in English."),
    ("Is there an app?", "Yes, for iPhone and Android. Your progress, streak and points are the same on the app and the web."),
    ("What does Achiever add?", "Unlimited questions and papers, adaptive practice that finds your weak spots, your exam forecast and 1.5× points. It starts with 14 days free and you buy it in the app."),
    ("How do points work?", "+10 for every correct answer and +20 for a session at 80% or better. Achievers earn 1.5× on everything. Points move you up your school and district leaderboards."),
    ("Does it cover O/L?", "The A/L streams come first. O/L subjects are on the way; the subject map shows what's ready today."),
]
FAQ = ('<section class="w-sec r13-sec" id="faq" data-faq><div class="w-faq"><div class="st"><h3 class="w-h2">Questions</h3><p class="sm t2">Can\'t find yours? Write to us from the app.</p></div><div class="list r13-faq">'
       + "".join(f'<div class="faq-i{" on" if i == 0 else ""}"><button type="button" class="li" aria-expanded="{"true" if i == 0 else "false"}" aria-controls="faq-{i}"><span class="sp ttl">{q}</span>{I("caret-down")}</button>'
                 f'<div class="faq-a" id="faq-{i}" role="region"><p class="sm t2">{a}</p></div></div>' for i, (q, a) in enumerate(FAQS))
       + "</div></div></section>")
CTA = f'''<section class="w-sec"><div class="band cta w-band r13-band"><div><span class="ey">Merit Project</span><h4>Start free, earn your first badge today.</h4><p>Takes a minute. No card needed.</p></div><div class="r13-bandcta"><button class="btn wh" type="button">Start free</button>{badges("on-feature")}</div></div></section>'''
FOOT = f'<footer class="w-foot"><span class="wmk">MERIT<b>.</b></span><span class="sp"></span><a>Privacy</a><a>Terms</a><a>Contact</a>{badges("sm")}</footer>'

secs_desk = dk("meritproject.lk/#try", f'<div class="w-scroll r13">{SEC_TRY}{SEC_CARDS}{SEC_INSIGHTS}{PRICING}{FAQ}{CTA}{FOOT}</div>')
secs_phone = phone(f'''<div class="r13 r13-ph"><span class="ey">Real past papers</span><b class="h-lg">Try one. It's a <span class="ul">real</span> exam question.</b>
<div class="r13-ph-q" data-lq><div class="r13-chips" data-lq-chips></div><span class="xs t3" data-lq-src></span><div class="card r13-qcard" data-lq-card tabindex="0"></div></div>
<b class="h-md" style="margin-top:8px">Questions</b><div class="list r13-faq" data-faq>''' + "".join(
    f'<div class="faq-i"><button type="button" class="li" aria-expanded="false"><span class="sp ttl">{q}</span>{I("caret-down")}</button><div class="faq-a" hidden><p class="sm t2">{a}</p></div></div>' for q, a in FAQS[:4]) + "</div></div>", 1100)

SPEC = (
    "<b>Data.</b> Everything shown is real. Questions: text-only, single-answer, official past-paper MCQs with both English and Sinhala text "
    f"(snapshot: 8 per subject for {len([s for s in SUBJ if s['q']])} subjects, explained ones first; maths in <code>$...$</code> renders with KaTeX in production, a small subset here). "
    "Flashcards: English cards for Biology, Chemistry and Physics (ICT and Agri have none yet). Exam insights: each topic's real share of Paper I marks over the last 12 years from <code>/public/explore</code>. "
    "FAQ facts (years, subjects, counts) are computed from the same data, never hand-written. "
    "<b>Production endpoint (new).</b> <code>GET /public/samples?stream=&amp;lang=</code> on the <code>/public</code> group next to <code>/public/explore</code>: about 40 random text-only single-answer past-paper questions across the stream's subjects (with explanations first) and about 20 flashcards, same 1 h in-process cache. "
    "<b>Try a question.</b> Subject chips; the card shows year, subject and question number; EN / සිං toggle (Tamil disabled until content lands; a Sinhala question without a Sinhala explanation shows the English one with a note). "
    "Picking an option: options lock, the pick squashes to 0.97 for 2 f, at 3 f right turns sage and wrong turns error-red with the correct answer revealed, the others dim; the explanation expands (softLand 12 f); a correct answer pops the coin from 1.6x (snapSettle 11 f) with +10 (the real points rule). "
    "Next question: the card's rows leave up 8 (gentleIn 6 f, 1 f stagger) and the new one rises from 12 below (softLand 12 f, 2 f stagger); no repeats until the subject's set is used. Keys 1 to 5 answer, Enter goes next. "
    "<b>Flashcards.</b> A stack of three (poses offset 14/26 x, 10/20 y, 3/6 degrees, 0.96/0.92 scale). Click or Space flips with a 3D <code>rotateY</code> (softLand 14 f), then Again / Hard / Good / Easy appear with example intervals; rating throws the card left (Again) or right (accelExit 10 f, opacity in the last 4 f) and the stack moves up a pose (softLand 12 f, 2 f stagger). Keys 1 to 4 rate. "
    "<b>Exam insights.</b> Subject chips; top 8 topics by exam share plus \"Other topics\", bars in the subject colour grow in when scrolled into view (IntersectionObserver at 35%, scaleX softLand 14 f, 2 f stagger); hover or focus a row for the detail line; the CTA starts the top topic. "
    "<b>FAQ.</b> Real <code>button[aria-expanded]</code> rows controlling a region, one open at a time, height softLand 10 f open / gentleIn 8 f close. "
    "<b>Store badges.</b> Official Apple and Google badge artwork in production (these are stand-ins); both badges everywhere, including phones. Prices show \"Rs —\" until they are final. "
    "<b>Reduced motion:</b> every state change happens without movement."
)

s_secs = screen("web-landing", "Landing · sections below the hero (round 13)", [("energy", "Energy"), ("gap", "New")],
    "Below the hero the page proves the product with live components on real data: answer a real past-paper question, flip real flashcards, and see what each paper asks. Then pricing, the FAQ and the closing CTA with the store badges. All of it works here; try it. " + SPEC,
    "GET /public/samples?stream=&amp;lang= (new) · GET /public/explore",
    [cand("A", "Live sections", "New", secs_desk,
          "The landing stops describing Merit and lets a visitor use it for a minute: one real question with the real explanation, a few real cards, the real exam weighting. That is the strongest argument a student or parent can get before signing up.",
          "Needs the small <code>/public/samples</code> endpoint and KaTeX for maths. Questions with figures or tables are left out of the sample.",
          "<code>question card</code><code>flashcard stack</code><code>exam-share bars</code><code>FAQ accordion</code><code>store badges</code>", pick=False),
     f'<div class="wf-cand"><div class="wf-cand-h"><b>m</b><span>Phone</span><em>Check</em></div>{secs_phone}<div class="wf-note"><p>Same components stacked in one column; the question card keeps its keys hidden and uses taps. The FAQ uses the same accordion.</p></div></div>'])
