"""Round 14 landing: the Mastery Engine (#mastery) and Merit Points (#points) sections, and pricing / FAQ that read the
`rules` and `plans` snapshot (build_samples.py), matching what GET /public/plans will serve. Must not import
gen_web_board (circular). Widgets: r14-live.js; styles: wf-r14-landing.css."""
from gen_web import *  # noqa: F401,F403
from r13_landing import (SAMPLES, SEC_TRY, SEC_CARDS, SEC_INSIGHTS, CTA, FOOT, Y1, OLDEST, PAPER_SUBJECTS, N_Q,  # noqa: F401
                         badges)

R = SAMPLES["rules"]
PLANS = {p["code"]: p for p in SAMPLES["plans"]}
MONTH, YEAR, TRIAL = PLANS["PRO_MONTHLY"], PLANS["PRO_ANNUAL"], PLANS["REGISTER_TRIAL"]
SAVE = round(100 * (1 - YEAR["price_lkr"] / (MONTH["price_lkr"] * 12)))
W = {"read": round(R["mastery_weight_notes"] * 100), "remember": round(R["mastery_weight_flashcard"] * 100), "prove": round(R["mastery_weight_quiz"] * 100)}
MULT = f'{R["pro_multiplier"]:g}'
lkr = lambda n: f"Rs {n:,}"

# ------------------------------------------------------------------ #mastery
SEC_MASTERY = f'''<section class="w-sec r13-sec r14-sec" id="mastery" data-lm><div class="r13-2col">
<div class="st r13-lead"><span class="ey">The Mastery Engine</span><h3 class="w-h2">Read it. Remember it. <span class="ul">Prove</span> it.</h3>
<p class="t2">Every subtopic fills in three ways. Reading the note is {W["read"]}%, keeping its cards fresh is {W["remember"]}%, and answering its questions is {W["prove"]}%. Reaching {R["mastery_completion_threshold"]:g}% unlocks the next subtopic.</p>
<p class="t2">Flashcards use spaced repetition: each card comes back just before you'd forget it, so a few minutes a day keeps what you learned.</p>
<ol class="r14-steps" data-lm-steps><li data-s="read"><b>Read</b><span>{W["read"]}%</span></li><li data-s="remember"><b>Remember</b><span>{W["remember"]}%</span></li><li data-s="prove"><b>Prove</b><span>{W["prove"]}%</span></li></ol>
<span class="xs t3">Try all three on a real Biology subtopic. Nothing here is saved.</span></div>
<div class="card r14-mcard"><div class="r14-mhead"><div class="r14-ring" data-lm-ring role="img" aria-label="Mastery 0 percent"><img class="tile" style="--s:62px" src="{PW}circulation-tile.svg" alt=""></div>
<div class="st" style="gap:2px"><span class="ey" data-lm-topic>Biology</span><b class="h-md" data-lm-title>Animal form and function</b><span class="sm t2" data-lm-pct aria-live="polite">0% mastered</span></div></div>
<div class="segc r14-tabs" role="tablist" aria-label="Mastery parts"><button role="tab" data-t="read" aria-selected="true" class="on">Read</button><button role="tab" data-t="remember" aria-selected="false">Remember</button><button role="tab" data-t="prove" aria-selected="false">Prove</button></div>
<div class="r14-pane" data-lm-pane role="tabpanel"></div>
<div class="r14-unlock" data-lm-unlock hidden><span class="mode-ic" style="background:var(--merit-sage-300)">{I("lock-open")}</span><div class="st sp" style="gap:2px"><b class="sm">Next subtopic unlocked</b><span class="xs t2">+{R["progression_unlock_reward"]} points for reaching {R["mastery_completion_threshold"]:g}%</span></div><span class="coin lg"></span></div>
</div></div></section>'''

# ------------------------------------------------------------------ #points
EARN = [
    ("correct", "check-circle", "Correct answer", f'+{R["points_per_correct_answer"]}', "Every question, every mode"),
    ("bonus", "target", f'Session at {R["accuracy_bonus_threshold"]:g}% or better', f'+{R["accuracy_bonus_points"]}', "Once per session"),
    ("cards", "cards-three", "Flashcard session", f'+{R["flashcard_session_points"]}', f'Up to {R["flashcard_daily_points_cap"]} a day'),
    ("note", "book-open", "Note finished", f'+{R["note_completion_points"]}', "Each note, once"),
    ("unlock", "lock-open", "Subtopic unlocked", f'+{R["progression_unlock_reward"]}', f'At {R["mastery_completion_threshold"]:g}% mastery'),
]
ROWS = "".join(f'<div class="li r14-erow" data-e="{k}"><span class="mode-ic">{I(i)}</span><div class="sp st" style="gap:0"><span class="ttl">{t}</span><span class="meta">{m}</span></div>'
               f'<b class="num r14-v" data-base="{v[1:]}">{v}</b><button class="btn s gh r14-add" type="button" aria-label="Earn: {t}">{I("plus")}</button></div>' for k, i, t, v, m in EARN)
SEC_POINTS = f'''<section class="w-sec r13-sec r14-sec" id="points" data-lp><div class="r13-2col rev">
<div class="st" style="gap:14px"><div class="card r14-earn"><div class="rw"><b class="h-sm sp">Earn</b><label class="r14-pro"><span class="sm">Achiever ×{MULT}</span><button class="tgl" type="button" role="switch" aria-checked="false" data-lp-pro></button></label></div>
<div class="list">{ROWS}</div>
<div class="rw r14-spend"><span class="mode-ic" style="background:var(--merit-coral-100)">{I("key")}</span><div class="sp st" style="gap:0"><b class="sm">Spend: unlock a subtopic early</b><span class="xs t2" data-lp-cost>{R["force_unlock_base_cost"]} points, then +{R["force_unlock_cost_increment"]} each time · {round(R["force_unlock_burn_pct"] * 100)}% is burned</span></div><button class="btn s gh" type="button" data-lp-spend>Unlock</button></div></div></div>
<div class="st r13-lead"><span class="ey">Merit Points</span><h3 class="w-h2">Every right answer <span class="ul">counts</span>.</h3>
<p class="t2">Points come from real study, not from tapping. Earn them, spend a few to skip ahead, and climb your school and district boards.</p>
<div class="card r14-board" data-lp-board aria-live="polite"></div>
<div class="rw r14-total"><span class="coin lg"></span><b class="num" data-lp-total>0</b><span class="sm t2">points this demo</span><span class="sp"></span><button class="lnk" type="button" data-lp-reset>Reset</button></div></div></div></section>'''

# ------------------------------------------------------------------ pricing + FAQ from rules / plans
PRICING = f'''<section class="w-sec r13-sec" id="pricing"><h3 class="w-h2" style="text-align:center">Free to start. <span class="ul">Achiever</span> when you're ready.</h3><div class="w-plans">
<div class="card w-plan"><span class="badge">Wanderer</span><b class="w-price">Free</b><span class="sm t2">Forever</span><ul class="w-ul"><li>{R["free_mastery_daily_limit"]} mastery questions a day</li><li>{R["free_paper_daily_limit"]} past papers a day</li><li>Flashcards and notes</li><li>Up to {R["free_enrollment_limit_al"]} subjects (A/L)</li></ul><button class="btn gh full" type="button">Start free</button></div>
<div class="card w-plan pro"><span class="badge pro">Achiever</span><b class="w-price">{lkr(YEAR["price_lkr"])}<small>/year</small></b><span class="sm">or {lkr(MONTH["price_lkr"])} a month · save {SAVE}% yearly · {TRIAL["duration_days"]} days free</span><ul class="w-ul"><li>Unlimited questions and papers</li><li>Adaptive mode and exam forecast</li><li>{MULT}× points on everything</li><li>Up to {R["pro_enrollment_limit_al"]} subjects (A/L)</li></ul><button class="btn wh full" type="button">Start your {TRIAL["duration_days"]} days free</button></div></div>
<p class="xs t3" style="text-align:center">Prices in Sri Lankan rupees, from <code>GET /public/plans</code> (edited in admin). Buying happens in the app, through the App Store or Google Play.</p></section>'''

FAQS = [
    ("Is Merit free?", f'Yes. The Wanderer plan is free forever: {R["free_mastery_daily_limit"]} mastery questions and {R["free_paper_daily_limit"]} past papers a day, plus flashcards and notes. Limits reset at midnight, Sri Lanka time. Achiever removes them.'),
    ("How much is Achiever?", f'{lkr(MONTH["price_lkr"])} a month or {lkr(YEAR["price_lkr"])} a year (save {SAVE}%), with the first {TRIAL["duration_days"]} days free. Cancel any time in the App Store or Google Play; you keep Achiever until the period ends.'),
    ("Which past papers are included?", f"Official A/L papers up to {Y1}, from {OLDEST['y0']} for {OLDEST['t']}, in {PAPER_SUBJECTS}: {N_Q:,} questions so far, each mapped to its topic. More subjects and years are being added."),
    ("Can I study in Sinhala or Tamil?", "Subject content comes in English, Sinhala and Tamil where it is available; switch it on each subject's page. The app's menus stay in English."),
    ("How do points work?", f'+{R["points_per_correct_answer"]} for every correct answer and +{R["accuracy_bonus_points"]} for a session at {R["accuracy_bonus_threshold"]:g}% or better; flashcards and notes earn too. Achievers earn {MULT}× on everything. Points move you up your school and district leaderboards.'),
    ("What is mastery?", f'Each subtopic\'s mastery is {W["prove"]}% questions, {W["read"]}% notes and {W["remember"]}% flashcards. At {R["mastery_completion_threshold"]:g}% the next subtopic unlocks.'),
    ("Is there an app?", "Yes, for iPhone and Android. Your progress, streak and points are the same on the app and the web."),
]
FAQ = ('<section class="w-sec r13-sec" id="faq" data-faq><div class="w-faq"><div class="st"><h3 class="w-h2">Questions</h3><p class="sm t2">Can\'t find yours? Write to us from the app.</p></div><div class="list r13-faq">'
       + "".join(f'<div class="faq-i{" on" if i == 0 else ""}"><button type="button" class="li" aria-expanded="{"true" if i == 0 else "false"}" aria-controls="faq-{i}"><span class="sp ttl">{q}</span>{I("caret-down")}</button>'
                 f'<div class="faq-a" id="faq-{i}" role="region"><p class="sm t2">{a}</p></div></div>' for i, (q, a) in enumerate(FAQS))
       + "</div></div></section>")

secs_desk = dk("meritproject.lk/#mastery", f'<div class="w-scroll r13">{SEC_TRY}{SEC_CARDS}{SEC_MASTERY}{SEC_POINTS}{SEC_INSIGHTS}{PRICING}{FAQ}{CTA}{FOOT}</div>')
secs_phone = phone(f'''<div class="r13 r13-ph r14-ph"><span class="ey">The Mastery Engine</span><b class="h-lg">Read it. Remember it. <span class="ul">Prove</span> it.</b>
<div class="card r14-mcard" data-lm data-lm-compact><div class="r14-mhead"><div class="r14-ring" data-lm-ring role="img" aria-label="Mastery 0 percent"><img class="tile" style="--s:52px" src="{PW}circulation-tile.svg" alt=""></div><div class="st" style="gap:2px"><span class="ey" data-lm-topic>Biology</span><b class="h-sm" data-lm-title>Animal form and function</b><span class="xs t2" data-lm-pct>0% mastered</span></div></div>
<div class="segc r14-tabs" role="tablist" aria-label="Mastery parts"><button role="tab" data-t="read" aria-selected="true" class="on">Read</button><button role="tab" data-t="remember" aria-selected="false">Remember</button><button role="tab" data-t="prove" aria-selected="false">Prove</button></div><div class="r14-pane" data-lm-pane role="tabpanel"></div><div class="r14-unlock" data-lm-unlock hidden><b class="sm sp">Next subtopic unlocked</b><span class="coin"></span><b class="num">+{R["progression_unlock_reward"]}</b></div></div>
<span class="ey" style="margin-top:12px">Merit Points</span><b class="h-lg">Every right answer <span class="ul">counts</span>.</b><div class="list">''' + "".join(
    f'<div class="li"><span class="sp ttl">{t}</span><b class="num">{v}</b></div>' for k, i, t, v, m in EARN) + f'</div><span class="xs t3">Achiever earns {MULT}× on all of these.</span></div>', 1200)

SPEC = (
    "<b>Data.</b> Every number comes from the snapshot of <code>system_settings</code> and <code>tiers</code> in <code>qm-samples.js</code> (<code>rules</code>, <code>plans</code>), the same values <code>GET /public/plans</code> will serve; the copy is assembled from them, never typed. "
    f"Prices are the Gate 0 values ({lkr(MONTH['price_lkr'])} / month, {lkr(YEAR['price_lkr'])} / year, save {SAVE}%) until <code>tiers.display_price_lkr</code> exists (Phase B). "
    "FSRS intervals are real: the backend engine (<code>service.newFsrsEngine</code>, Flutter-parity weights) at retention "
    f"{R['flashcard_request_retention']:g}: a new card is Again 1 min · Hard 6 min · Good 10 min · Easy 16 days; answering Good each time it is due spaces reviews 10 min → 4 d → 14 d → 45 d → 135 d. Production serves them per card from <code>/public/samples</code> and the due-cards API. "
    f"<b>Mastery Engine.</b> A real Biology subtopic tile with a three-colour ring (Read violet, Remember sky, Prove orange; weights {W['read']}/{W['remember']}/{W['prove']}). "
    "Read: a note paragraph and \"Mark done\" (+25, ring gains its Read slice). Remember: a real card flips (Space), four rating buttons show the real intervals, rating adds the Remember slice and draws the forgetting curve: memory falls to 90% at each review, and each review flattens the next fall. "
    "Prove: a real past-paper question on the same topic; a correct answer adds the full Prove slice (a wrong one adds nothing and offers another). "
    f"When the ring passes {R['mastery_completion_threshold']:g}% the unlock row rises (softLand 12 f) with +{R['progression_unlock_reward']}. Tabs are a real tablist (arrow keys); slices grow with snapSettle 11 f; reduced motion = instant. "
    "<b>Merit Points.</b> The earn table: each + adds that row to the running total and the district board re-ranks you (FLIP move, glide 10 f). The Achiever switch multiplies every row by "
    f"{MULT} (rounded down, as the backend does) and the values tick to the new number. Flashcard sessions stop paying at the daily cap ({R['flashcard_daily_points_cap']}). "
    f"Spend: unlocking early costs {R['force_unlock_base_cost']}, then +{R['force_unlock_cost_increment']} per unlock; {round(R['force_unlock_burn_pct'] * 100)}% of what you spend is burned (shown under the button), and it is disabled when you can't afford it. "
    "<b>Pricing and FAQ</b> now read the same snapshot; the FAQ gains \"How much is Achiever?\" and \"What is mastery?\"."
)

s_secs = screen("web-landing", "Landing · sections below the hero (rounds 13 + 14)", [("energy", "Energy"), ("gap", "New")],
    "Round 14 adds the Mastery Engine and Merit Points between the flashcards and exam insights, and makes pricing and the FAQ read the backend's rules and plans. Everything is live; try it. " + SPEC,
    "GET /public/plans (new: tiers, limits, rules, prices) · GET /public/samples?stream=&amp;lang= (new) · GET /public/explore",
    [cand("A", "Live sections", "New", secs_desk,
          "The two hardest ideas to sell, mastery and points, are now things a visitor does rather than reads: fill a real subtopic, rate a real card and see the real schedule, earn and spend points and watch the board move.",
          "Two more interactive blocks on a long page. They stay below the fold and load their script when scrolled near.",
          "<code>mastery ring</code><code>tabs</code><code>flashcard + FSRS curve</code><code>question card</code><code>earn table</code><code>switch</code><code>leaderboard</code>", pick=False),
     f'<div class="wf-cand"><div class="wf-cand-h"><b>m</b><span>Phone</span><em>Check</em></div>{secs_phone}<div class="wf-note"><p>The Mastery card is the same widget, compact. Points become a static table on phones.</p></div></div>'])
