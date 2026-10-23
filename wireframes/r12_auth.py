"""Round 12 auth + onboarding: one step-aware split screen for every auth frame.
Must not import gen_web_board (circular). Styles live in wf-r12-auth.css (.as-*)."""
from gen_web import *  # noqa: F401,F403

WM = '<span class="wmk">MERIT<b>.</b></span>'
SPOT = "assets/v3/spots/"


def stp(n, total=5):
    return "".join(f'<i class="{"d" if k < n else "c" if k == n else ""}"></i>' for k in range(1, total + 1))


def count(n, total=5, label="Step"):
    return f'<div class="as-count"><div class="stepper">{stp(n, total)}</div><span>{label} {n} of {total}</span></div>'


def panel(kind, hero, top="", foot=""):
    f = f'<div class="as-foot">{foot}</div>' if foot else ""
    return f'<aside class="as-art {kind}"><div class="as-top">{WM}{top}</div><div class="as-hero">{hero}</div>{f}</aside>'


def split(url, kind, hero, form, top="", foot=""):
    return dk(url, f'<div class="as-split">{panel(kind, hero, top, foot)}<div class="as-pane"><div class="as-form calm">{form}</div></div></div>')


def head(ey, h, sub=""):
    s = f'<span class="as-sub">{sub}</span>' if sub else ""
    return f'<span class="ey">{ey}</span><b class="as-h">{h}</b>{s}'


def chips(*items):
    return '<div class="as-chips">' + "".join(items) + "</div>"


STREAK = f'<span class="hchip fl">{I("flame-fill")}12-day streak</span>'
POINTS = '<span class="hchip cn"><span class="coin"></span>1,240 points</span>'

MOB = '<div class="fld"><label>Mobile number</label><div class="inp focus"><span class="cc">+94</span><b style="font-weight:600">7</b>7 123 4567</div><span class="xs t3">Sri Lankan mobile numbers start with 7</span></div>'
SO = '<span class="sm t2 as-alt">{}</span>'
OTP = '<div class="otp"><span>1</span><span>9</span><span class="f"></span><span></span><span></span><span></span></div>'

# ------------------------------------------------------------------ 1 sign in
SI_HERO = head("Welcome back", 'Pick up where you <span class="ul">left off</span>.', "Your streak and points are waiting for you.") + chips(STREAK, POINTS) + f'''
<div class="card as-last"><span class="ey">Last studied</span><div class="rw">{tile("physics", 48)}<div class="st sp" style="gap:2px"><b>Physics · Mechanics</b><span class="sm t2">Kinematics · 18 of 50 questions today</span></div></div><div class="bar thin calm"><i style="--v:36%"></i></div></div>
<span class="xs t3">Remembered from this browser. A new device shows the streak line only.</span>'''
SI_FORM = f'<b class="h-xl">Sign in</b><div class="segc"><span class="on">Mobile</span><span>Email</span></div>{MOB}<div class="fld"><label>Password</label><div class="inp">••••••••<span class="sp"></span>{I("eye-slash")}</div></div><a class="lnk" style="align-self:flex-end">Forgot password?</a><button class="btn full" type="button">Sign in</button><span class="sm t2 as-alt">New here? <a class="lnk">Create an account</a></span>'

# ------------------------------------------------------------------ 2 register
VP = "".join(f'<li><span class="as-ic">{I(ic)}</span><span><b>{t}</b><small>{s}</small></span></li>' for ic, t, s in [
    ("translate", "Sinhala, Tamil and English", "Subject content in your language, switchable per subject."),
    ("target", "Past papers with exam weighting", "Practise the topics the exam actually leans on."),
    ("flame", "Streaks, points and leaderboards", "Small daily wins that add up."),
])
REG_HERO = head("Free forever", 'Earn <span class="ul">Merit</span>.') + f'''<div class="as-from">{tile("physics", 32)}<span>Starting with <b>Physics</b></span></div>
<ul class="as-vp">{VP}</ul>
<div class="card as-mini"><div class="rw"><span class="ey sp">Today</span>{STREAK}</div><div class="rw">{tile("physics", 32)}<span class="sm sp"><b>Mechanics</b> · 10 questions</span>{I("caret-right")}</div><div class="rw"><span class="mode-ic as-mi" style="background:var(--merit-category-2)">{I("cards-three")}</span><span class="sm sp"><b>12 flashcards</b> due</span>{I("caret-right")}</div></div>'''
REG_FORM = f'''<b class="h-xl">Create your account</b>
<div class="fld"><label>Full name</label><div class="inp">Dilini Perera</div></div>
<div class="fld"><label>Email <span class="t3" style="font-weight:600">· optional</span></label><div class="inp ph-in">For password resets</div></div>{MOB}
<div class="g2"><div class="fld"><label>Password</label><div class="inp">••••••••<span class="sp"></span>{I("eye-slash")}</div></div><div class="fld"><label>Confirm password</label><div class="inp ph-in">Type it again</div></div></div>
<div class="fld"><label>Preferred language</label><div class="segc"><span class="on">සිංහල</span><span>தமிழ்</span><span>English</span></div><span class="xs t3">For subject content. Change it per subject later.</span></div>
<span class="xs t3">By continuing you agree to the Terms and Privacy Policy.</span>
<button class="btn full" type="button">Create account</button><span class="sm t2 as-alt">Have an account? <a class="lnk">Sign in</a></span>'''

# ------------------------------------------------------------------ 3 forgot password
def hints(cur):
    rows = [("Enter the mobile number you registered with.", "Send code"), ("Type the 6-digit code we texted you.", "Verify"), ("Choose a new password. You are signed in after.", "Reset")]
    return '<ol class="as-hints">' + "".join(f'<li class="{"on" if k == cur else "d" if k < cur else ""}"><i>{I("check") if k < cur else k}</i><span>{t}</span></li>' for k, (t, _) in enumerate(rows, 1)) + '</ol>'


FG_HERO = head("Account help", 'Back in <span class="ul">a minute</span>.', "Three short steps, and you keep your streak.") + f'<img class="as-spot" src="{SPOT}empty.svg" alt="">' + hints(2)
FG_FORM = f'<div class="rw"><span class="ibtn flat">{I("arrow-left")}</span><div class="stepper sp">{stp(2, 3)}</div><span class="sm t3">Step 2 of 3</span></div><b class="h-xl">Check your phone</b><span class="as-sub">Sent to +94 77 ••• 4567</span>{OTP}<button class="btn full" type="button">Verify</button><span class="sm t2 as-alt">Didn\'t get it? <a class="lnk">Resend code</a> <span class="t3">· 0:42</span></span><span class="sm t2 as-alt"><a class="lnk">Back to sign in</a></span>'

# ------------------------------------------------------------------ 4 onboarding
SUBS = [("Physics", "physics", "EN", 1), ("Chemistry", "chemistry", "සිං", 0), ("Biology", "biology", "සිං", 0)]
ONB_FOOT = "Your answers fill this in as you go."
NAVB = lambda nxt="Next", back=True: f'<div class="rw as-nav">{"<button class=" + chr(34) + "btn gh" + chr(34) + " type=" + chr(34) + "button" + chr(34) + ">Back</button>" if back else ""}<span class="sp"></span><button class="btn" type="button">{nxt}</button></div>'
OH = lambda t, s: f'<b class="h-xl">{t}</b><span class="as-sub">{s}</span>'

O1_HERO = head("Your exam", 'Plan around <span class="ul">your exam</span>.', "Today's plan is paced to this.") + '''<div class="card as-exam"><span class="ey">Exam</span><b class="num">A/L · 2027</b><div class="as-chips"><span class="chip">Gampaha</span><span class="chip as-ghost">School</span></div></div>'''
O1_FORM = OH("Let's personalise your journey.", "Tell us about your academic goals.") + '<div class="fld"><label>Exam level</label><div class="segc"><span class="off">O/L</span><span class="on">A/L</span></div><span class="xs t3">O/L opens later. Pick A/L to continue.</span></div><div class="fld"><label>Exam year</label><div class="segc"><span>This year</span><span class="on">2027</span><span>2028</span><span>2029</span></div></div><div class="g2"><div class="fld" style="min-width:0"><label>District <span class="t3" style="font-weight:600">· optional</span></label><div class="inp">Gampaha<span class="sp"></span>' + I("caret-down") + '</div></div><div class="fld" style="min-width:0"><label>School <span class="t3" style="font-weight:600">· optional</span></label><div class="inp ph-in">Search</div></div></div>' + NAVB(back=False)

O2_HERO = head("Your stream", 'Choose your <span class="ul">stream</span>.', "Subjects on the next step are filtered to it.") + f'''<span class="chip as-carry">A/L · 2027</span><div class="card as-stream"><span class="mode-ic" style="background:var(--merit-category-1)">{I("atom-fill")}</span><div class="st" style="gap:2px"><b class="h-md">Science</b><span class="sm t2">Bio · Chem · Phys · Maths</span></div></div>'''
STR = [("Science", "Bio · Chem · Phys · Maths", "atom-fill", 1, 1), ("Commerce", "Accounting · Econ · Business", "coins-fill", 4, 0), ("Arts", "History · Geo · Sinhala/Tamil Lit", "pen-nib-fill", 3, 0), ("Technology", "ICT · Engineering Tech · Bio Tech", "device-mobile-fill", 2, 0), ("Other", "Build a custom subject set", "sparkle-fill", 0, 0)]
O2_FORM = OH("Choose your stream.", "Select the A/L stream that matches your subjects.") + '<div class="st" style="gap:10px">' + "".join(f'<div class="srow{" on" if on else ""}"><span class="mode-ic" style="background:{"var(--merit-category-%d)" % c if c else "var(--merit-surface-sunken)"}">{I(ic)}</span><div class="st sp" style="gap:2px;min-width:0"><span class="nm">{n}</span><span class="sub">{s}</span></div><span class="radio{" on" if on else ""}">{I("check") if on else ""}</span></div>' for n, s, ic, c, on in STR) + '</div>' + NAVB()

QCELLS = "".join(f'<div class="as-cell">{tile(t, 64)}<b class="sm">{n}</b><span class="as-lang">{l}</span>{"<span class=as-from-map>" + I("map-trifold") + "From the map</span>" if m else ""}</div>' for n, t, l, m in SUBS) + '<div class="as-cell as-empty"><span class="as-slot">+</span><span class="sm t3">Add</span></div><div class="as-cell as-empty"><span class="as-slot">+</span><span class="sm t3">Add</span></div>'
O3_HERO = head("Your subjects", 'Build your <span class="ul">quilt</span>.', "Tiles join as you tick them, each with its content language.") + f'<div class="as-quilt">{QCELLS}</div><div class="rw"><span class="badge">3 of 5</span><span class="sm t2">Science · up to 5</span></div>'
SJ = [("Physics", "physics", 1, "EN", "From the subject map"), ("Chemistry", "chemistry", 1, "සිං", ""), ("Biology", "biology", 1, "සිං", ""), ("ICT", "ict", 0, "", ""), ("Agricultural Science", "plants", 0, "", "")]
O3_FORM = OH("Pick your subjects", "Content starts in <b>Sinhala</b>, your preferred language. Change it per subject.") + '<div class="rw"><span class="sm t2 sp">Science · up to 5</span><span class="badge">3 of 5</span></div><div class="list">' + "".join(f'<div class="li sjrow{" on" if c else ""}"><span class="ckb{" on" if c else ""}">{I("check") if c else ""}</span>{tile(t, 40)}<div class="sp st" style="gap:0;min-width:0"><span class="ttl">{n}</span>{"<span class=meta>" + m + "</span>" if m else ""}</div>' + (('<div class="segc lseg">' + "".join(f'<span class="{"on" if l == cur else ""}">{l}</span>' for l in ("EN", "සිං", "த")) + '</div>') if c else "") + '</div>' for n, t, c, cur, m in SJ) + '</div>' + NAVB("Finish enrollment")

O4_HERO = head("Friends", 'Better with <span class="ul">a friend</span>.', "A friend's code gives you both a points bonus.") + f'''<div class="card as-gift"><div class="rw" style="justify-content:center"><div class="av"></div><span class="as-plus">+</span><div class="av"></div></div><div class="rw" style="justify-content:center"><span class="coin lg" style="--coin:28px"></span><b class="num">Bonus for both</b></div></div>
<div class="as-recap">{"".join(tile(t, 32) for _, t, _, _ in SUBS)}<span class="sm t2">Enrolled</span></div>'''
O4_FORM = OH("Got a referral code?", "Enter a friend's code to say thanks. You'll both get a points bonus.") + '<div class="fld"><label>Referral code</label><div class="inp focus">MERIT-4821</div></div><button class="btn full" type="button">Apply code</button><button class="btn gh full" type="button">Skip</button>'

PLAN = "".join(f'<div class="as-plan-row">{tile(t, 36)}<span class="st sp" style="gap:0"><b class="sm">{n}</b><span class="xs t3">{m}</span></span>{I("caret-right")}</div>' for n, t, m in [("Physics · Mechanics", "physics", "10 questions"), ("Chemistry", "chemistry", "12 flashcards due"), ("Biology", "biology", "Read one note")])
O5_HERO = head("You're in", 'Your first day is <span class="ul">ready</span>.', "Here is what Today looks like on day one.") + f'<div class="card as-today"><div class="rw"><span class="ey sp">Today · Dilini</span><span class="badge pro">{I("crown-fill")}Achiever trial · 14 days</span></div>{PLAN}<div class="as-plan-row as-ghost"><span class="sm t3">More appears as you study</span></div></div>'
O5_FORM = OH("You're in.", "We've started your 14-day Achiever trial. Free, no card needed.") + f'<div class="card sel as-tier"><div class="rw"><b class="sp">Achiever</b><span class="badge pro">Activating for you</span></div><div class="rw" style="align-items:baseline"><b class="num as-price">Free</b><span class="sm t2">for 14 days</span></div><span class="sm t2">Then continues on Wanderer. No charge, ever.</span></div><div class="card flat as-tier"><b>Wanderer</b><div class="rw" style="align-items:baseline"><b class="num as-price">Free</b><span class="sm t2">forever</span></div><span class="sm t2">What you keep after the trial.</span></div><button class="btn full" type="button">Start learning</button>'

OB = lambda n, h, f: split(f"meritproject.lk/student/onboarding?step={n}", "ob", h, f, top=count(n), foot=ONB_FOOT)

# ------------------------------------------------------------------ phone (collapse)
PH_BODY = f'''<div class="as-band ob"><div class="rw">{WM}<span class="sp"></span><span class="sm t3">Step 3 of 5</span></div><div class="stepper">{stp(3)}</div><b class="as-bmsg">Build your <span class="ul">quilt</span>. Tiles join as you tick them.</b><div class="as-bchips">{"".join(tile(t, 28) for _, t, _, _ in SUBS)}<span class="badge">3 of 5</span></div></div>
<div class="as-pform calm"><b class="h-lg">Pick your subjects</b><span class="sm t2">Content starts in <b>Sinhala</b>. Change it per subject.</span><div class="list">''' + "".join(f'<div class="li sjrow{" on" if c else ""}"><span class="ckb{" on" if c else ""}">{I("check") if c else ""}</span>{tile(t, 36)}<div class="sp st" style="gap:0;min-width:0"><span class="ttl">{n}</span>{"<span class=meta>" + m + "</span>" if m else ""}</div>' + (('<div class="segc lseg">' + "".join(f'<span class="{"on" if l == cur else ""}">{l}</span>' for l in ("EN", "සිං", "த")) + '</div>') if c else "") + '</div>' for n, t, c, cur, m in SJ[:4]) + '</div></div><div class="as-pbar"><button class="btn full" type="button">Finish enrollment</button></div>'
PHONE = phone(f'<div class="as-pscr">{PH_BODY}</div>', 780)

s_auth = kit_screen("web-auth", "Auth & onboarding · step-aware split screen", [("calm", "Calm"), ("gap", "Approve")],
    "<b>One split layout for every auth frame</b>: sign in, register, forgot password (3 steps) and onboarding (5 steps, no app shell). "
    "<b>Layout:</b> panel 44% / form pane 56% (<code>grid-template-columns: 44fr 56fr</code>), min-height 640. The form column is max 480px, centred in its pane, calm mode, labels above fields, one primary button full width. "
    "<b>Panel:</b> wordmark <code>MERIT.</code> top left, then one hero block: eyebrow, a Plus Jakarta headline with the brush underline <code>.ul</code> on exactly one word, a one-line sub, then the step's content. "
    "Background is a token tint (violet for sign in and onboarding, butter for register, sage for forgot password) with one pattern from <code>assets/v3/patterns</code> (dots, checks, hatch, stripes) at 6% opacity, fading out downwards. No patchworks as decoration; subject tiles appear only as content the student chose. "
    "<b>Per step:</b> sign in = streak + points chips and the last-studied subject card. Register = 3 value props (trilingual content, past papers with exam weighting, streaks/points/leaderboards), a mini Today card, and a \"Starting with Physics\" tile when the visitor came from the map (<code>?subject=&lt;id&gt;</code>). "
    "Forgot password = a spot illustration from <code>assets/v3/spots</code> and a 3-line hint list with the current step highlighted. "
    "Onboarding = a live preview plus a step counter (stepper + \"Step n of 5\") in the panel's top right: 1 exam card (level, year, district), 2 stream label card, 3 mini quilt of the ticked subjects with their EN / සිං / த tags (empty dashed slots up to the cap), 4 referral bonus card, 5 Today plan taking shape with the Achiever trial badge. The preview updates on each choice. "
    "<b>Fields</b> mirror the app (round 8–10): mobile is <code>+94 | 7…</code> (D22), register keeps name, optional email, mobile, password, confirm, preferred language; onboarding is 5 steps (4 for O/L, which skips the stream step). "
    "<b>Collapse &lt; 768px:</b> the panel becomes a slim tinted band above the form: wordmark, step counter, the step's one-line message and (onboarding) the chosen tiles. The preview, value props and spot are dropped; the form fills the width with a sticky bottom button.",
    "POST /auth/register · /auth/login · /auth/otp/send|verify|resend · /auth/password/forgot → /verify → /reset · POST /students/me · GET /streams/all-with-subjects · /enrollments/capacity · POST /enrollments (bulk) · PUT /enrollments/:id/language · POST referral apply · trial activation · /complete-onboarding",
    [("Sign in", split("meritproject.lk/student/sign-in", "si", SI_HERO, SI_FORM), "Forgot password opens the 3-step flow. The last-studied card needs only a remembered subject id."),
     ("Register · from the map", split("meritproject.lk/student/register?subject=physics", "rg", REG_HERO, REG_FORM), "Without <code>?subject</code> the \"Starting with\" pill is hidden. Fields are today's, plus optional email as in the app."),
     ("Forgot password · step 2 of 3", split("meritproject.lk/student/forgot-password", "fg", FG_HERO, FG_FORM), "Same panel for all 3 steps; only the highlighted hint changes. Step 1: \"Forgot password?\" with the mobile field and Send code. Step 3: \"Set a new password\" with New and Confirm password, then Reset password, and the spot switches to <code>success.svg</code>."),
     ("Onboarding · 1 Exam", OB(1, O1_HERO, O1_FORM), "Level, year, optional district and school. O/L is shown but off, as in the app."),
     ("Onboarding · 2 Stream", OB(2, O2_HERO, O2_FORM), "A/L only. Panel shows the chosen stream label."),
     ("Onboarding · 3 Subjects", OB(3, O3_HERO, O3_FORM), "Physics is pre-ticked from <code>?subject=</code>. Per-subject language switch starts on <code>preferred_language</code>; the quilt in the panel fills as rows are ticked."),
     ("Onboarding · 4 Referral", OB(4, O4_HERO, O4_FORM), "Optional. Skip is always available."),
     ("Onboarding · 5 Plan", OB(5, O5_HERO, O5_FORM), "Trial auto-activates (14 days, D24). Start learning completes onboarding and opens Today in the app shell."),
     ("Below 768px · phone", PHONE, "Panel collapses to the tinted band with the step message; shown for onboarding step 3. Other steps swap only the message.")])
