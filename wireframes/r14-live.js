/* Landing round 14: the Mastery Engine and Merit Points sections, on real data.
   [data-lm]  Mastery Engine: one real Biology subtopic fills Read / Remember / Prove with the real weights
              (QM_SAMPLES.rules), a real flashcard with real FSRS intervals (QM_SAMPLES.fsrs) and a forgetting curve,
              and a real past-paper question. Passing the completion threshold unlocks the next subtopic.
   [data-lp]  Merit Points: the earn table from system_settings, an Achiever ×multiplier switch, the force-unlock
              spend rule, and a district board that re-ranks as points come in.
   Motion uses QMIco.EASE at 30 fps, like landing-live.js. Reduced motion = state changes only.
   Production: components/merit/study/{MasteryTile,FsrsIntervals,PointsPop} on GET /public/plans and /public/samples. */
(function () {
  "use strict";
  const S = window.QM_SAMPLES, gsap = window.gsap, FR = 1 / 30;
  if (!S || !S.rules || !S.fsrs || !gsap) { console.warn("r14-live: needs QM_SAMPLES.rules/.fsrs and gsap"); return; }
  const R = S.rules, F = S.fsrs;
  const E = (window.QMIco && window.QMIco.EASE) || { softLand: "power3.out", snapSettle: "expo.out", glide: "power2.out", gentleIn: "power2.in", accelExit: "power3.in" };
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const I = (n) => '<svg class="i"><use href="#i-' + n + '"/></svg>';
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const h = (html) => { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstChild; };
  const dur = (sec) => sec < 3600 ? Math.round(sec / 60) + " min" : sec < 86400 ? Math.round(sec / 3600) + " h" : Math.round(sec / 86400) + (sec < 2 * 86400 ? " day" : " days");

  /* ---------------------------------------------------------------- Mastery Engine */
  const W = { read: Math.round(R.mastery_weight_notes * 100), remember: Math.round(R.mastery_weight_flashcard * 100), prove: Math.round(R.mastery_weight_quiz * 100) };
  const bio = (S.subjects.find((s) => s.t === "Biology") || {}).id;
  const TOPIC = "Animal form and function";
  const card = S.flashcards.find((c) => c.s === bio && /acrosome/i.test(c.f)) || S.flashcards.find((c) => c.s === bio);
  const qs = S.questions.filter((q) => q.s === bio && q.topic === (card ? card.topic : TOPIC));

  function Mastery(root) {
    const ring = root.querySelector("[data-lm-ring]"), pctEl = root.querySelector("[data-lm-pct]"), pane = root.querySelector("[data-lm-pane]");
    const unlock = root.querySelector("[data-lm-unlock]"), tabs = [...root.querySelectorAll(".r14-tabs [data-t]")], steps = document.querySelectorAll("[data-lm-steps] li");
    const compact = root.hasAttribute("data-lm-compact");
    const done = { read: false, remember: false, prove: false };
    let tab = "read", flipped = false, rated = null, qi = 0, picked = 0, shown = { a: 0, b: 0, c: 0 };
    if (card) root.querySelector("[data-lm-title]").textContent = card.topic;

    const pct = () => (done.read ? W.read : 0) + (done.remember ? W.remember : 0) + (done.prove ? W.prove : 0);
    function paintRing(animate) {
      const to = { a: done.read ? W.read : 0, b: done.remember ? W.remember : 0, c: done.prove ? W.prove : 0 };
      const set = () => { // cumulative stops (a three-term calc() in a conic stop is dropped by Chrome)
        ring.style.setProperty("--a", shown.a + "%"); ring.style.setProperty("--ab", shown.a + shown.b + "%"); ring.style.setProperty("--abc", shown.a + shown.b + shown.c + "%");
      };
      if (!animate || reduced()) { Object.assign(shown, to); set(); } else gsap.to(shown, Object.assign({}, to, { duration: 11 * FR, ease: E.snapSettle, onUpdate: set }));
      const p = pct();
      pctEl.textContent = p + "% mastered" + (p < R.mastery_completion_threshold ? " · " + R.mastery_completion_threshold + "% unlocks the next subtopic" : "");
      ring.setAttribute("aria-label", "Mastery " + p + " percent");
      steps.forEach((li) => li.classList.toggle("done", done[li.dataset.s]));
      tabs.forEach((b) => b.classList.toggle("done", done[b.dataset.t]));
      if (p >= R.mastery_completion_threshold && unlock.hidden) {
        unlock.hidden = false;
        if (!reduced()) gsap.fromTo(unlock, { y: 12, opacity: 0 }, { y: 0, opacity: 1, duration: 12 * FR, ease: E.softLand });
      }
    }

    function curve() { // memory over time with "Good" at every due review: falls to retention, each review flattens the next fall
      const w = 300, hgt = 92, pad = 6, days = 60, X = (d) => pad + (d / days) * (w - 2 * pad), Y = (r) => pad + (1 - r) * (hgt - 2 * pad) / 0.14;
      let t0 = 0, d = "", dots = "";
      const ladder = F.good_ladder.map((s) => s / 86400), stab = F.stability_days;
      for (let k = 1; k < ladder.length && t0 < days; k++) {
        const S_ = stab[k], end = Math.min(t0 + ladder[k], days);
        for (let t = t0; t <= end + 1e-9; t += Math.max(0.25, (end - t0) / 40)) {
          const r = Math.pow(1 + F.factor * (t - t0) / S_, F.decay);
          d += (d ? "L" : "M") + X(t).toFixed(1) + " " + Y(Math.max(r, 0.86)).toFixed(1);
        }
        if (end < days) { dots += '<circle cx="' + X(end).toFixed(1) + '" cy="' + Y(F.retention).toFixed(1) + '" r="3.5"/>'; d += "L" + X(end).toFixed(1) + " " + Y(1).toFixed(1); }
        t0 = end;
      }
      return '<svg class="r14-curve" viewBox="0 0 ' + w + " " + hgt + '" role="img" aria-label="Memory curve: each review at 90% memory makes the next drop slower">' +
        '<line class="ret" x1="' + pad + '" x2="' + (w - pad) + '" y1="' + Y(F.retention) + '" y2="' + Y(F.retention) + '"/><path d="' + d + '"/><g class="dots">' + dots + "</g>" +
        '<text x="' + (w - pad) + '" y="' + (Y(F.retention) + 13) + '" text-anchor="end">' + Math.round(F.retention * 100) + "% memory</text></svg>" +
        '<span class="xs t3">Reviews land on days ' + ladder.slice(1, 5).reduce((a, x) => (a.push((a.length ? a[a.length - 1] : 0) + x), a), []).map((x) => Math.round(x)).join(", ") + ": each gap is longer than the last.</span>";
    }

    function paint() {
      pane.innerHTML = "";
      if (tab === "read") {
        pane.appendChild(h('<div class="st r14-read"><span class="ey">From the note · ' + esc(card ? card.topic : TOPIC) + '</span><p class="t2">' + esc(card ? card.b : "") + "</p>" +
          '<div class="chkpt">' + I(done.read ? "check-circle-fill" : "check-circle") + '<span class="sp sm">' + (done.read ? "Section done · +" + R.note_completion_points + " points" : "Finished this section?") + "</span>" +
          (done.read ? "" : '<button class="btn s" type="button" data-go>Mark done · +' + R.note_completion_points + "</button>") + "</div></div>"));
        const b = pane.querySelector("[data-go]");
        if (b) b.addEventListener("click", () => { done.read = true; paintRing(true); paint(); });
      } else if (tab === "remember") {
        const RATE = [["ag", "Again", F.new.again], ["hd2", "Hard", F.new.hard], ["gd", "Good", F.new.good], ["ez", "Easy", F.new.easy]];
        pane.appendChild(h('<div class="st r14-rem"><button type="button" class="fc r14-fc' + (flipped ? " back" : "") + '" data-flip aria-label="Flashcard. Press to ' + (flipped ? "hide" : "show") + ' the answer">' +
          '<span class="ey">' + (flipped ? "Answer" : esc(card.topic)) + '</span><span class="q">' + esc(flipped ? card.b : card.f) + "</span></button>" +
          (flipped ? '<div class="fsrs" role="group" aria-label="How well did you know it?">' + RATE.map((r, k) => '<button type="button" class="' + r[0] + (rated === k ? " on" : "") + '" data-r="' + k + '">' + r[1] + "<small>" + (k + 1) + " · " + dur(r[2]) + "</small></button>").join("") + "</div>"
            : '<span class="xs t3">Space or click to show the answer</span>') +
          (rated !== null ? '<div class="r14-sched"><span class="sm">' + (rated === 0 ? "Back in 1 minute, then again until it sticks." : "Next review in <b>" + dur(RATE[rated][2]) + "</b>.") + "</span>" + curve() + "</div>" : "") + "</div>"));
        pane.querySelector("[data-flip]").addEventListener("click", () => { flipped = !flipped; paint(); });
        pane.querySelectorAll("[data-r]").forEach((b) => b.addEventListener("click", () => {
          rated = +b.dataset.r; done.remember = true; paintRing(true); paint();
          const p = pane.querySelector(".r14-curve path");
          if (p && !reduced()) { const L = p.getTotalLength(); gsap.fromTo(p, { strokeDasharray: L, strokeDashoffset: L }, { strokeDashoffset: 0, duration: 24 * FR, ease: E.glide }); }
        }));
      } else {
        const q = qs[qi % qs.length];
        if (!q) { pane.textContent = "No sample question for this topic."; return; }
        pane.appendChild(h('<div class="st r14-prove"><span class="ey">' + q.year + " A/L · Q" + q.n + '</span><p class="lq-q">' + esc(q.en.q) + '</p><div class="opts">' +
          q.en.o.map((o, k) => '<button type="button" class="opt" data-k="' + (k + 1) + '"><span class="k">' + (k + 1) + "</span><span>" + esc(o) + "</span></button>").join("") + '</div><div class="r14-res" aria-live="polite"></div></div>'));
        const opts = [...pane.querySelectorAll(".opt")], res = pane.querySelector(".r14-res");
        opts.forEach((b) => b.addEventListener("click", () => {
          if (picked) return;
          picked = +b.dataset.k; const right = picked === q.ok;
          opts.forEach((o) => o.setAttribute("aria-disabled", "true"));
          b.classList.add(right ? "ok" : "bad"); if (!right) opts[q.ok - 1].classList.add("ok", "rev");
          if (right) { done.prove = true; paintRing(true); res.innerHTML = '<span class="coin"></span><b class="num">+' + R.points_per_correct_answer + "</b><span class=\"sm t2\">Proved. That's the biggest slice.</span>"; }
          else { res.innerHTML = '<span class="sm t2">Not this time. Proving needs a right answer.</span><button class="btn s gh" type="button" data-again>Another question</button>'; res.querySelector("[data-again]").addEventListener("click", () => { qi++; picked = 0; paint(); }); }
        }));
      }
      if (!reduced()) gsap.fromTo(pane.children, { y: 8, opacity: 0 }, { y: 0, opacity: 1, duration: 10 * FR, ease: E.softLand });
    }

    function select(t, focus) {
      tab = t; tabs.forEach((b) => { const on = b.dataset.t === t; b.classList.toggle("on", on); b.setAttribute("aria-selected", on); b.tabIndex = on ? 0 : -1; if (on && focus) b.focus(); });
      paint();
    }
    tabs.forEach((b, i) => {
      b.addEventListener("click", () => select(b.dataset.t));
      b.addEventListener("keydown", (e) => { const d = e.key === "ArrowRight" ? 1 : e.key === "ArrowLeft" ? -1 : 0; if (d) { e.preventDefault(); select(tabs[(i + d + tabs.length) % tabs.length].dataset.t, true); } });
    });
    root.addEventListener("keydown", (e) => {
      if (tab === "remember" && e.key === " " && e.target.tagName !== "BUTTON") { e.preventDefault(); flipped = !flipped; paint(); }
      if (tab === "remember" && flipped && /^[1-4]$/.test(e.key)) { const b = pane.querySelector('[data-r="' + (+e.key - 1) + '"]'); if (b) b.click(); }
    });
    if (compact) unlock.classList.add("compact");
    paintRing(false); select("read");
  }

  /* ---------------------------------------------------------------- Merit Points */
  const ME = "You", BASE = 1700;
  const PEERS = [["Sanduni W.", 2140], ["Kavindu P.", 1985], ["Nethmi R.", 1890], ["Ravindu J.", 1760], ["Ishara W.", 1650], ["Tharindu S.", 1590]];
  function Points(root) {
    const totalEl = root.querySelector("[data-lp-total]"), board = root.querySelector("[data-lp-board]"), proBtn = root.querySelector("[data-lp-pro]");
    const spendBtn = root.querySelector("[data-lp-spend]"), costEl = root.querySelector("[data-lp-cost]");
    let total = 0, pro = false, cardsToday = 0, unlocks = 0;
    const val = (base) => (pro ? Math.floor(base * R.pro_multiplier) : base);
    const cost = () => R.force_unlock_base_cost + R.force_unlock_cost_increment * unlocks;

    function paintBoard(animate) {
      const rows = PEERS.map(([n, p]) => ({ n, p })).concat({ n: ME, p: BASE + total, me: true }).sort((a, b) => b.p - a.p);
      const before = new Map([...board.querySelectorAll(".lrow")].map((el) => [el.dataset.n, el.getBoundingClientRect().top]));
      board.innerHTML = '<div class="rw"><b class="sm sp">Gampaha district · this week</b><span class="xs t3">demo</span></div>' + rows.map((r, i) =>
        '<div class="lrow' + (r.me ? " me" : "") + '" data-n="' + esc(r.n) + '"><span class="rk">' + (31 + i) + '</span><div class="av sm"></div><span class="nm">' + esc(r.n) + '</span><span class="pt">' + r.p.toLocaleString() + "</span></div>").join("");
      if (!animate || reduced()) return;
      board.querySelectorAll(".lrow").forEach((el) => { const b = before.get(el.dataset.n); if (b == null) return; const dy = b - el.getBoundingClientRect().top; if (dy) gsap.fromTo(el, { y: dy }, { y: 0, duration: 10 * FR, ease: E.glide }); });
    }
    function paintValues(animate) {
      root.querySelectorAll(".r14-v").forEach((el) => {
        const v = val(+el.dataset.base), from = +el.textContent.replace(/\D/g, "") || v, o = { n: from };
        const set = () => { el.textContent = "+" + Math.round(o.n); };
        if (!animate || reduced()) { o.n = v; set(); } else gsap.to(o, { n: v, duration: 10 * FR, ease: E.glide, onUpdate: set });
      });
      const capped = cardsToday >= R.flashcard_daily_points_cap;
      const cb = root.querySelector('[data-e="cards"] .r14-add'); cb.disabled = capped;
      root.querySelector('[data-e="cards"] .meta').textContent = capped ? "Daily cap reached (" + R.flashcard_daily_points_cap + ")" : "Up to " + R.flashcard_daily_points_cap + " a day · " + cardsToday + " so far";
      spendBtn.disabled = total < cost();
      costEl.textContent = cost() + " points" + (unlocks ? " (next one)" : "") + ", then +" + R.force_unlock_cost_increment + " each time · " + Math.round(R.force_unlock_burn_pct * 100) + "% (" + Math.round(cost() * R.force_unlock_burn_pct) + ") is burned";
    }
    function setTotal(n, animate) {
      const o = { n: total }; total = n;
      if (!animate || reduced()) totalEl.textContent = total.toLocaleString();
      else gsap.to(o, { n: total, duration: 10 * FR, ease: E.glide, onUpdate: () => { totalEl.textContent = Math.round(o.n).toLocaleString(); } });
      paintBoard(animate); paintValues(false);
    }
    root.querySelectorAll(".r14-erow").forEach((row) => row.querySelector(".r14-add").addEventListener("click", (e) => {
      let add = val(+row.querySelector(".r14-v").dataset.base);
      if (row.dataset.e === "cards") { add = Math.min(add, R.flashcard_daily_points_cap - cardsToday); cardsToday += add; }
      if (add <= 0) return;
      setTotal(total + add, true);
      if (!reduced()) { const pop = h('<span class="r14-pop num">+' + add + "</span>"); e.currentTarget.appendChild(pop); gsap.fromTo(pop, { y: 0, opacity: 1 }, { y: -22, opacity: 0, duration: 16 * FR, ease: E.glide, onComplete: () => pop.remove() }); }
    }));
    proBtn.addEventListener("click", () => { pro = !pro; proBtn.classList.toggle("on", pro); proBtn.setAttribute("aria-checked", pro); paintValues(true); });
    spendBtn.addEventListener("click", () => { const c = cost(); if (total < c) return; unlocks++; setTotal(total - c, true); });
    root.querySelector("[data-lp-reset]").addEventListener("click", () => { cardsToday = 0; unlocks = 0; setTotal(0, true); });
    paintValues(false); paintBoard(false);
  }

  const boot = () => { document.querySelectorAll("[data-lm]").forEach(Mastery); document.querySelectorAll("[data-lp]").forEach(Points); };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
