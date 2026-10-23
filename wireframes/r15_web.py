"""Round 15 (web): the pre-release flows from DS §30 that the web board was missing, plus the Gate 0 changes
(subject-page language switch, 30% prediction gate). Must not import gen_web_board (circular).
Built from board classes only (wf.css, wf-web.css, wf-r12-*.css)."""
from gen_web import *  # noqa: F401,F403
from r12_auth import split as asplit, head as ahead, OTP  # noqa: F401
from r12_hub import hub_head, URL  # noqa: F401
from r14_landing import MONTH, YEAR, lkr

GAP = [("gap", "Approve")]
SPOT = "assets/v3/spots/"


def dlg_page(url, body, active="Me", title="Account"):
    return dk(url, f'<div class="w-app" style="position:relative">{side(active)}<div class="w-col">{head(title)}<main class="w-main" style="opacity:.35">'
                   f'<div class="card" style="height:160px"></div><div class="card" style="height:120px"></div></main></div>'
                   f'<div style="position:absolute;inset:0;display:grid;place-items:center;background:var(--merit-scrim, color-mix(in srgb, var(--merit-ink-900) 45%, transparent))">{body}</div></div>')


def li(icon, t, meta="", right=None):
    m = f'<span class="meta">{meta}</span>' if meta else ""
    r = I("caret-right") if right is None else right
    return f'<div class="li">{I(icon)}<div class="sp st" style="gap:0"><span class="ttl">{t}</span>{m}</div>{r}</div>'


def alert(kind, icon, html):
    bg = {"err": "var(--merit-feedback-error-subtle)", "warn": "var(--merit-feedback-warning-subtle)", "info": "var(--merit-feedback-info-subtle)"}[kind]
    fg = {"err": "var(--merit-feedback-error-text)", "warn": "var(--merit-feedback-warning-text)", "info": "var(--merit-feedback-info-text)"}[kind]
    return f'<div class="card" style="flex-direction:row;gap:10px;align-items:flex-start;background:{bg};box-shadow:none"><span style="color:{fg}">{I(icon)}</span><span class="sm">{html}</span></div>'


# ------------------------------------------------------------------ Me › Account
SUB = f'''<div class="w-2col"><div class="st" style="gap:16px">
<div class="card feat" style="gap:6px"><span class="badge pro">{I("crown-fill")}Achiever</span><b class="h-md">Yearly · {lkr(YEAR["price_lkr"])}</b><span class="sm" style="opacity:.85">Renews 23 Oct 2027 · bought in the Android app (Google Play)</span></div>
{alert("info", "info-fill", "Your subscription is managed by Google Play. To change plan, cancel or update payment, open Merit on your phone, or Google Play › Subscriptions.")}
<div class="list">{li("receipt", "Manage on Google Play", "Opens play.google.com/store/account/subscriptions")}{li("arrows-clockwise", "Refresh status", "Bought a moment ago? Check again", "")}</div>
<span class="xs t3">The web never sells or cancels a subscription (store billing, round 11). A web-only account without one sees the Achiever page with \"Get it in the app\".</span></div>
<aside class="w-rail"><div class="card tight" style="gap:6px"><span class="ey">Cancelled?</span><span class="sm t2">The card says \"Cancelled · access until 23 Oct 2027\". Billing issue shows an error alert with the store's grace date.</span></div></aside></div>'''
CHPW = f'''<div class="st" style="gap:14px;max-width:440px"><div class="fld"><label>Current password</label><div class="inp">••••••••<span class="sp"></span>{I("eye-slash")}</div></div>
<div class="fld"><label>New password</label><div class="inp focus">••••••••••<span class="sp"></span>{I("eye-slash")}</div><span class="xs" style="color:var(--merit-feedback-success-text)">Strong · at least 8 characters with a number</span></div>
<div class="fld"><label>Confirm new password</label><div class="inp" style="box-shadow:inset 0 0 0 1.5px var(--merit-feedback-error)">•••••••••</div><span class="xs" style="color:var(--merit-feedback-error-text)">{I("warning-fill")} Passwords don't match.</span></div>
<div class="rw"><button class="btn gh" type="button">Cancel</button><button class="btn" type="button">Save password</button></div><span class="xs t3">Phone-only accounts (OTP sign-up) see \"Set a password\" with just the two new fields.</span></div>'''
SIGNOUT = dlg_page("meritproject.lk/student/me", f'<div class="dlg" style="width:400px"><b class="h-sm">Sign out of Merit?</b><span class="sm t2">Your progress is saved to your account. You can sign back in on any device.</span><div class="rw" style="justify-content:flex-end"><button class="btn gh s" type="button">Cancel</button><button class="btn inv s" type="button">Sign out</button></div></div>')
DEL1 = f'''<div class="st" style="gap:14px;max-width:560px"><b class="h-lg">Before you go</b><span class="t2">Deleting your account permanently removes:</span>
<div class="list">{li("chart-line-up", "Progress, mastery and your 12-day streak", right="")}{li("coins", "4,610 Merit Points and your district rank", right="")}{li("cards-three", "Flashcard history", right="")}</div>
{alert("warn", "warning-fill", "You have Achiever through Google Play. Cancel it there first, or it keeps renewing after your account is gone.")}
<div class="rw"><button class="btn gh" type="button">Keep my account</button><button class="btn gh" type="button">Continue</button></div></div>'''
DEL2 = dlg_page("meritproject.lk/student/me/delete", f'<div class="dlg" style="width:440px;gap:12px"><b class="h-sm">Type DELETE to confirm</b><span class="sm t2">This can\'t be undone. We delete your data within 30 days.</span><div class="fld"><label>Confirmation</label><div class="inp focus">DELETE</div></div><div class="rw" style="justify-content:flex-end"><button class="btn gh s" type="button">Cancel</button><button class="btn s" type="button" style="background:var(--merit-feedback-error);color:var(--merit-text-on-error)">Delete my account</button></div></div>')
LEGAL = f'''<div class="w-note"><aside class="w-outline"><span class="ey">Legal</span><a class="w-ol on">Privacy policy</a><a class="w-ol">Terms of use</a><a class="w-ol">Refunds and subscriptions</a><span class="xs t3">Updated 1 Oct 2026</span></aside>
<article class="w-read"><h4 class="h-xl">Privacy policy</h4><div class="prose"><p>We collect your name, mobile number, school and district, the answers you give and the time you spend studying.</p><p>We use them to run Merit, rank leaderboards and improve questions. We never sell your data.</p><h5 class="h-md">Students under 18</h5><p>Shared images show only your username and score.</p></div></article></div>'''
HELP = f'''<div class="w-2col"><div class="st" style="gap:12px"><div class="inp">{I("magnifying-glass")}<span class="t3">Search help</span></div>
<div class="list">{li("question", "How do points work?")}{li("question", "Why did my streak reset?", "Days end at midnight, Sri Lanka time")}{li("question", "How do I cancel Achiever?")}{li("question", "How do I change my subject's language?", "On the subject page, top right")}</div></div>
<aside class="w-rail"><div class="card" style="gap:10px"><b class="h-sm">Still stuck?</b>{li("chat-circle-text", "WhatsApp us", "Replies within a day")}{li("envelope", "Email support")}<div class="fld"><label>Report a problem</label><div class="inp" style="min-height:96px;align-items:flex-start">At least 10 characters</div><span class="xs t3">0 / 500</span></div><button class="btn s" type="button">Send</button></div></aside></div>'''
s_acct = kit_screen("web-r15-account", "Me · subscription status, password, sign out, delete, legal, help", GAP,
    "Me › Account on the web (D23). Subscription is read-only for app purchases, with the store's manage link; the price is the Gate 0 value. Change password, sign-out confirm and two-step deletion mirror the app (mobile r15). Legal and help are in-portal pages; help shares its FAQ with the landing.",
    "GET /subscriptions/me · PUT /auth/password (needs API) · POST /auth/logout · DELETE /users/me · GET /public/legal/:slug · GET /public/faq",
    [("Subscription status", app("Me", "Subscription", SUB, "Me · Account", url="meritproject.lk/student/me/subscription"), "Info alert carries the store rule; Refresh re-reads RevenueCat."),
     ("Change password", app("Me", "Change password", CHPW, "Me · Account", url="meritproject.lk/student/me/password"), "Errors inline per field (DS §15)."),
     ("Sign-out confirm", SIGNOUT, "Esc cancels; Enter confirms."),
     ("Delete · step 1", app("Me", "Delete account", DEL1, "Me · Account", url="meritproject.lk/student/me/delete"), "Consequences with real numbers, then Continue."),
     ("Delete · step 2", DEL2, "Delete stays disabled until the field reads DELETE."),
     ("Legal pages", app("Me", "Privacy policy", LEGAL, "Me · About", url="meritproject.lk/legal/privacy"), "Public routes too (<code>/legal/*</code>), linked from the landing footer and sign-up."),
     ("Help", app("Me", "Help", HELP, "Me · Help", url="meritproject.lk/student/help"), "FAQ rows expand in place (landing accordion).")])

# ------------------------------------------------------------------ Auth: email verification
VER_HERO = ahead("One last step", 'Check your <span class="ul">inbox</span>.', "We sent a 6-digit code to dil•••@gmail.com.") + f'<img class="as-spot" src="{SPOT}empty.svg" alt="">'
VER_FORM = f'<b class="h-xl">Verify your email</b><span class="as-sub">The code expires in 10 minutes.</span>{OTP}<span class="sm t3">Resend in 0:42 · <a class="lnk" style="display:inline">Change email</a></span><button class="btn full" type="button">Verify</button><a class="lnk" style="align-self:center">Do this later</a>'
BANNER = f'''<div class="st" style="gap:16px">{alert("info", "envelope", "<b>Verify your email</b> so you can reset your password by email. <a class=lnk style=display:inline>Verify now</a>")}
<div class="card" style="gap:8px"><span class="ey">Today's plan</span><b class="h-md">3 things, about 15 minutes</b></div></div>'''
s_verify = kit_screen("web-r15-verify", "Auth · email verification", GAP,
    "Only for accounts that added an email (phone sign-ups are verified by OTP). Same split screen as tab 09; \"Do this later\" leaves an info banner on Today until verified.",
    "POST /auth/email/verify/send · /auth/email/verify (needs API)",
    [("Verify", asplit("meritproject.lk/student/verify-email", "fg", VER_HERO, VER_FORM), "Wrong code: error edge and \"That code didn't match. 2 tries left.\""),
     ("Today banner", app("Today", "Hi, Dilini", BANNER, "Good morning", url="meritproject.lk/student"), "Dismiss hides it for 7 days.")])

# ------------------------------------------------------------------ Subjects: language switch in the header (Gate 0) + prediction gate
LANG_SEG = ('<div class="segc" role="group" aria-label="Content language" style="width:220px;padding:3px">'
            '<span style="padding:5px 4px;min-height:28px">EN</span><span class="on" lang="si" style="padding:5px 4px;min-height:28px">සිංහල</span>'
            '<span class="off" lang="ta" style="padding:5px 4px;min-height:28px;opacity:.45" title="Tamil content is coming">தமிழ்</span></div>')
HH = hub_head("Learn").replace('<span class="hchip fl">', LANG_SEG + '<span class="hchip fl">', 1)
LANG_BODY = f'''{HH}<div class="hh-body"><div class="st" style="gap:12px;max-width:640px"><div class="card" lang="si" style="gap:6px"><span class="ey">සෛල ජීව විද්‍යාව</span><b class="h-md">සෛල ඉන්ද්‍රියිකා</b><span class="sm t2">ප්‍රශ්න 24 · සටහන් 3</span></div>
{alert("info", "translate", "Biology content is now in Sinhala. Your progress carries over; questions and cards switch with it. Menus stay in English.")}</div></div>'''
PRED = f'''{hub_head("Stats")}<div class="hh-body"><div class="w-stats"><div class="card" style="gap:8px"><span class="ey">Predicted grade</span><b class="h-md">Practise more to unlock your prediction</b>
<span class="sm t2">We need at least 30% topic coverage to predict fairly. You're at 18%.</span><div class="bar calm"><i style="--v:60%"></i></div><span class="xs t3">18% of 30% · about 6 more subtopics</span><button class="btn s" type="button" style="align-self:flex-start">Continue Cell biology</button></div>
<div class="card" style="gap:6px"><span class="ey">High-yield gap</span><b class="h-sm">Genetics · about 9 marks at stake</b><span class="sm t2">Comes up 1.8 times per paper and you're at 8%.</span></div></div></div>'''
s_lang = kit_screen("web-r15-subject", "Subjects · content language in the subject header, prediction gate", GAP,
    "Gate 0: on the web, a subject's content language (EN / සිංහල / தமிழ්) is switched only in that subject's header, not in Me. A language the subject doesn't have yet is disabled with a tooltip. The switch sets <code>lang</code> on the content container, so DS 3.7 <code>:lang(si|ta)</code> type rules apply; UI chrome stays English. "
    "The predicted grade is hidden below 30% topic coverage (Gate 0) and shows progress toward unlocking it.",
    "PUT /enrollments/:id/language · GET /subjects/:id/prediction (coverage_pct)",
    [("Header language switch", dk(URL + "learn", f'<div class="w-app">{side("Learn")}<div class="w-col"><main class="w-main">{LANG_BODY}</main></div></div>'), "Switching shows a one-time info alert; no reload of the shell."),
     ("Prediction locked", dk(URL + "stats", f'<div class="w-app">{side("Learn")}<div class="w-col"><main class="w-main">{PRED}</main></div></div>'), "Above 30% the card becomes the grade card from tab 05.")])

# ------------------------------------------------------------------ System: maintenance, 404, error
def full(url, img, t, b, cta, extra=""):
    return dk(url, f'<div class="w-app focus" style="place-items:center;min-height:520px"><div class="st" style="gap:12px;align-items:center;text-align:center;max-width:420px;padding:40px"><span class="wmk">MERIT<b>.</b></span><img src="{SPOT}{img}.svg" alt="" style="width:180px"><b class="h-lg">{t}</b><span class="t2">{b}</span>{cta}{extra}</div></div>')


s_sys = kit_screen("web-r15-system", "System · maintenance, not found, error", GAP,
    "Pages the frontend lacks today (no <code>not-found.tsx</code>, <code>error.tsx</code> or <code>global-error.tsx</code>). One spot, one line, one action; never a patchwork. Maintenance replaces the portal when the API answers 503 with a maintenance flag; the landing stays up.",
    "API 503 {maintenance, eta} · app/not-found.tsx · app/error.tsx · app/global-error.tsx",
    [("Maintenance", full("meritproject.lk/student", "error", "Merit is getting an upgrade", "We're back by about 10:30 pm. Your progress and streak are safe.", '<button class="btn gh" type="button">Try again</button>', '<span class="xs t3">Streaks don\'t break during maintenance.</span>'), "Auto-retries every 60 s while the tab is visible."),
     ("Not found (404)", full("meritproject.lk/student/papers/2009", "not-found", "We couldn't find that page", "It may have moved, or the link is old.", '<div class="rw"><button class="btn gh" type="button">Go back</button><button class="btn" type="button">Go to Today</button></div>'), "Public 404 swaps Today for Home."),
     ("Error", full("meritproject.lk/student/learn", "error", "Something went wrong", "It's on our side, and your progress is safe.", '<button class="btn" type="button">Reload</button>', '<span class="xs t3">Error ID 7f3c-21 · include it if you write to us</span>'), "global-error.tsx renders the same without the app shell.")])


# ------------------------------------------------------------------ Quiz results rework (web-quiz note: "looks boring")
QD = [1, 1, 0, 1, 1, 1, 1, 0, 1, 1]  # the session: 8 of 10
SEC = [38, 51, 94, 22, 41, 30, 47, 118, 26, 35]  # seconds per question
DOTS = "".join(f'<a class="r15-qd {"ok" if r else "x"}" href="#" aria-label="Question {k + 1}: {"correct" if r else "wrong"}">{k + 1}</a>' for k, r in enumerate(QD))
RECEIPT = f'''<div class="r15-rcpt"><div class="rw"><span class="sm t2 sp">8 correct × 10</span><b class="num">+80</b></div><div class="rw"><span class="sm t2 sp">Accuracy 80% bonus</span><b class="num">+20</b></div>
<div class="rw r15-dim"><span class="sm sp">{I("crown")} With Achiever ×1.5</span><b class="num">+150</b></div><div class="rw r15-total"><span class="coin lg" style="--coin:28px"></span><b class="sp">Points earned</b><b class="num" style="font-size:30px">+100</b></div></div>'''
NEXT = f'''<div class="list r15-next"><div class="li">{tile("leaf", 40)}<div class="sp st" style="gap:0"><span class="ttl">Review 2 mistakes</span><span class="meta">Q3 and Q8 · both on stomata</span></div>{I("caret-right")}</div>
<div class="li"><span class="mode-ic" style="background:var(--merit-sage-300)">{I("lock-open")}</span><div class="sp st" style="gap:0"><span class="ttl">Next: Transpiration unlocked</span><span class="meta">+50 when you reach 50% here · you're at 64%</span></div>{I("caret-right")}</div>
<div class="li"><span class="mode-ic" style="background:var(--merit-sky-300)">{I("cards-three")}</span><div class="sp st" style="gap:0"><span class="ttl">6 cards due on Leaf structure</span><span class="meta">About 3 min</span></div>{I("caret-right")}</div></div>'''

RES_A = f'''<div class="r15-res a"><div class="r15-hero"><div class="r15-medal"><span class="r15-spark s1">{I("sparkle-fill")}</span><span class="r15-spark s2">{I("sparkle-fill")}</span><div class="grade">A</div></div>
<div class="st" style="gap:6px"><span class="ey">Mastery · Leaf structure</span><b class="h-xl">You proved <span class="ul">Leaf structure</span>.</b><span class="t2">8 of 10 right, faster than your last three sessions.</span>
<div class="r15-stats"><div><b class="num">80%</b><span>accuracy</span></div><div><b class="num">6:12</b><span>time</span></div><div><b class="num">{I("flame-fill")}13</b><span>day streak</span></div><div><b class="num">#36</b><span>Gampaha · up 2</span></div></div></div></div>
<div class="r15-grid"><div class="card" style="gap:12px"><span class="ey">Your answers</span><div class="r15-qds">{DOTS}</div><span class="xs t3">Click a number to review that question</span>{RECEIPT}</div>
<div class="card" style="gap:12px"><span class="ey">What's next</span>{NEXT}<div class="rw"><button class="btn gh" type="button">{I("share-network")}Share</button><span class="sp"></span><button class="btn" type="button">Done</button></div></div></div></div>'''

RES_B = f'''<div class="r15-res b"><div class="r15-quiltwrap"><div class="r15-big"><div class="ring" style="--v:64;--sz:200px;--th:12px;--c:var(--merit-dataviz-cat2)"><img class="tile" style="--s:148px" src="{PW}leaf-tile.svg" alt=""></div>
<span class="r15-delta">52% → <b>64%</b></span></div><div class="st" style="gap:10px;max-width:420px"><span class="ey">Prove · Leaf structure</span><b class="h-xl">+12% mastery in one session.</b>
<span class="t2">Proving is 75% of a subtopic. Two more good sessions and Leaf structure is complete.</span>
<div class="r15-mini">{"".join(tile(t, 44) for t in ("cells", "plants", "leaf", "circulation"))}<span class="r15-lock">{I("lock")}</span></div><span class="xs t3">Plant form &amp; function · 3 of 5 subtopics past 50%</span></div></div>
<div class="r15-strip"><div class="rw" style="gap:10px"><span class="coin lg" style="--coin:32px"></span><b class="num" style="font-size:28px">+100</b><span class="sm t2">80 for answers · 20 accuracy bonus</span></div><div class="r15-qds sm">{DOTS}</div>
<div class="rw" style="gap:10px"><button class="btn gh" type="button">Review 2 mistakes</button><button class="btn" type="button">Done</button></div></div></div>'''

mx = max(SEC)
BARS = "".join(f'<div class="r15-tb {"ok" if r else "x"}"><i style="--h:{round(100 * s / mx)}%"></i><span>{k + 1}</span></div>' for k, (r, s) in enumerate(zip(QD, SEC)))
RES_C = f'''<div class="r15-res c"><div class="rw" style="gap:16px;align-items:center"><div class="grade" style="width:72px;height:72px;font-size:36px;border-radius:22px">A</div><div class="st sp" style="gap:2px"><span class="ey">Mastery · Leaf structure</span><b class="h-lg">8 of 10 · 6 min 12 s</b></div>
<div class="r15-pill"><span class="coin"></span><b class="num">+100</b></div></div>
<div class="r15-grid"><div class="card" style="gap:10px"><div class="rw"><span class="ey sp">Time per question</span><span class="xs t3">avg 50 s</span></div><div class="r15-time">{BARS}</div>
<div class="r15-legend"><span><i class="ok"></i>Right</span><span><i class="x"></i>Wrong</span></div></div>
<div class="st" style="gap:12px"><div class="card r15-insight" style="gap:4px"><span class="ey">Pattern</span><b class="h-sm">Both misses were on stomata</b><span class="sm t2">And they took you twice as long. A 4-minute note section covers it.</span><button class="btn s ac" type="button" style="align-self:flex-start">Read: Stomata · 4 min</button></div>
<div class="card r15-insight" style="gap:4px"><span class="ey">Speed</span><b class="h-sm">Fastest on epidermis (22 s)</b><span class="sm t2">You're ready for timed paper questions on this topic.</span></div></div></div>
<div class="rw"><button class="btn gh" type="button">Review 2 mistakes</button><span class="sp"></span><button class="btn gh" type="button">{I("share-network")}Share</button><button class="btn" type="button">Done</button></div></div>'''

res = lambda body: dk("meritproject.lk/student/quiz/8f2c…/results", f'<div class="w-app focus">{body}</div>', 600)
s_results = screen("web-results", "Quiz · results, reworked (pick one)", [("energy", "Energy"), ("gap", "Pick one")],
    "Your note: the round 10 results card \"looks boring\" on a wide screen. Three directions that use the width and make the session feel like progress, not a receipt. All three keep round 10's rules: points from <code>points_breakdown</code> (the Achiever row is a teaser for Wanderers), review opens in place, Done is the primary action, share shows username + score only (D25). Energy mode; reduced motion shows the final state.",
    "GET /quiz/sessions/:id (answers, time_spent_seconds) · result.points_breakdown · GET /progress/subtopics/:id (mastery before/after) · /leaderboards/me/ranks",
    [cand("A", "Scoreboard", "Bold", res(RES_A),
          "The session as a win: grade medallion with two sparkles, a headline that names what you proved, four stat tiles (accuracy, time, streak, rank move), a question strip you can click into review, the points receipt, and three concrete next steps.",
          "Most content of the three; needs the rank move (needs API: rank movement) or it shows streak only.",
          "<code>grade</code><code>stat tiles</code><code>question strip</code><code>points receipt</code><code>next-step list</code>"),
     cand("B", "Quilt progress", "Wild", res(RES_B),
          "The subtopic's patchwork fills its Prove ring from the old to the new mastery (52% → 64%), and the topic's mini quilt shows where it sits and what is still locked. Points and answers sit in one quiet strip below. Ties every session to the hierarchy and the Mastery Engine story on the landing.",
          "Least \"numbers first\": a student who wants the score sees it second. Paper mode (no subtopic) needs a fallback (paper tile, marks instead of mastery).",
          "<code>ring 200</code><code>patchwork tile</code><code>mini quilt</code><code>points strip</code>"),
     cand("C", "Recap and insight", "Safe", res(RES_C),
          "A coach's recap: time per question as bars (wrong ones red), then two plain-language insights from this session with one action each. Points are a single pill; nothing celebrates loudly, so it suits Paper mode too.",
          "Insights need rules on the backend (or simple client rules: same-subtopic misses, slowest vs average).",
          "<code>time bars</code><code>insight cards</code><code>points pill</code>")])
