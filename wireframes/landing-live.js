/* Landing round 13: live feature sections on real data.
   [data-lq]  Try a real question: a random past-paper MCQ (window.QM_SAMPLES, EN + SI), answer it, see why, +10.
   [data-lf]  Flashcard deck: real cards flip, rate Again / Hard / Good / Easy, the deck moves on.
   [data-li]  Exam insights: each topic's real share of exam marks (window.QM_DATA, the /public/explore snapshot).
   [data-faq] FAQ accordion, one open at a time.
   Motion uses the measured eases from qm-ico.js (QMIco.EASE); frames are at 30 fps. Reduced motion = state changes only.
   Production: the same components on GET /public/samples and /public/explore; maths renders with KaTeX there. */
(function () {
  "use strict";
  const S = window.QM_SAMPLES, D = window.QM_DATA, gsap = window.gsap, FR = 1 / 30;
  if (!S || !D || !gsap) { console.warn("landing-live: needs QM_SAMPLES, QM_DATA and gsap"); return; }
  const E = (window.QMIco && window.QMIco.EASE) || { softLand: "power3.out", snapSettle: "expo.out", glide: "power2.out", gentleIn: "power2.in", accelExit: "power3.in" };
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const I = (n) => '<svg class="i"><use href="#i-' + n + '"/></svg>';
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const h = (html) => { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstChild; };
  const subj = (id) => S.subjects.find((s) => s.id === id) || {};
  const shuffle = (a) => { const b = a.slice(); for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]]; } return b; };
  const short = (t) => t.replace("Information & Communication Technology", "ICT");

  /* ---- maths: a small LaTeX subset ($...$) to HTML (fractions, powers, subscripts, roots, Greek, arrows) */
  const SYM = { pi: "π", circ: "°", mu: "μ", times: "×", rho: "ρ", rightarrow: "→", to: "→", Delta: "Δ", delta: "δ", rightleftharpoons: "⇌", quad: " ", theta: "θ",
    lambda: "λ", alpha: "α", beta: "β", gamma: "γ", omega: "ω", Omega: "Ω", sigma: "σ", epsilon: "ε", cdot: "·", le: "≤", ge: "≥", leq: "≤", geq: "≥", approx: "≈",
    neq: "≠", pm: "±", infty: "∞", degree: "°", left: "", right: "", "%": "%", ",": " ", ";": " ", "!": "" };
  function tex(src) {
    let i = 0;
    const group = () => { // {...} or one token
      if (src[i] === "{") { i++; const out = run("}"); i++; return out; }
      if (src[i] === "\\") return cmd();
      return esc(src[i++] || "");
    };
    const cmd = () => {
      i++; let name = "";
      if (/[a-zA-Z]/.test(src[i])) while (i < src.length && /[a-zA-Z]/.test(src[i])) name += src[i++];
      else name = src[i++];
      if (name === "frac" || name === "dfrac" || name === "tfrac") { const a = group(), b = group(); return '<span class="tx-fr"><span>' + a + "</span><span>" + b + "</span></span>"; }
      if (name === "sqrt") return "√<span class=\"tx-rt\">" + group() + "</span>";
      if (name === "text" || name === "mathrm" || name === "mathbf" || name === "operatorname") return group();
      return name in SYM ? SYM[name] : esc(name);
    };
    const run = (stop) => {
      let out = "";
      while (i < src.length && src[i] !== stop) {
        const c = src[i];
        if (c === "\\") out += cmd();
        else if (c === "^") { i++; out += "<sup>" + group() + "</sup>"; }
        else if (c === "_") { i++; out += "<sub>" + group() + "</sub>"; }
        else if (c === "{") { i++; out += run("}"); i++; }
        else { out += esc(c); i++; }
      }
      return out;
    };
    return run(null);
  }
  const rich = (s) => (s || "").split(/(\$[^$]+\$)/g).map((p) => (p[0] === "$" && p.length > 1 ? '<span class="tx">' + tex(p.slice(1, -1)) + "</span>" : esc(p))).join("");

  const chips = (host, items, on, pick) => {
    host.innerHTML = "";
    items.forEach((s) => { const b = h('<button type="button" class="chip' + (s.id === on ? " on" : "") + '" aria-pressed="' + (s.id === on) + '">' + esc(short(s.t)) + "</button>"); b.addEventListener("click", () => pick(s.id)); host.appendChild(b); });
  };

  /* ---------------------------------------------------------------- Try a real question */
  function Question(root) {
    const left = root.querySelector("[data-lq-chips]"), src = root.querySelector("[data-lq-src]"), card = root.querySelector("[data-lq-card]");
    const subjects = S.subjects.filter((s) => s.q > 0);
    let sid = (subjects.find((s) => s.t === "Physics") || subjects[0]).id, lang = "en", queue = [], q = null, picked = 0;
    const deal = () => { if (!queue.length) queue = shuffle(S.questions.filter((x) => x.s === sid)); q = queue.pop(); picked = 0; };
    const meta = () => { const s = subj(q.s); src.innerHTML = "<b>" + q.year + " A/L " + esc(s.t) + "</b> · Question " + q.n + " · " + esc(q.topic); };
    function paint() {
      const t = q[lang], x = q[lang].x || q.en.x, xNote = lang === "si" && !q.si.x && q.en.x ? '<span class="xs t3">Explanation in English for now.</span>' : "";
      card.innerHTML = "";
      card.appendChild(h('<div class="lq-head"><span class="ey">' + q.year + " · " + esc(short(subj(q.s).t)) + " · Q" + q.n + "</span>" +
        '<div class="segc lq-lang" role="group" aria-label="Language"><button type="button" data-l="en" class="' + (lang === "en" ? "on" : "") + '">EN</button><button type="button" data-l="si" lang="si" class="' + (lang === "si" ? "on" : "") + '">සිං</button><button type="button" disabled title="Tamil is coming">த</button></div></div>'));
      card.appendChild(h('<p class="lq-q"' + (lang === "si" ? ' lang="si"' : "") + ">" + rich(t.q) + "</p>"));
      const opts = h('<div class="opts" role="group" aria-label="Answers"></div>');
      t.o.forEach((o, k) => {
        const b = h('<button type="button" class="opt" data-k="' + (k + 1) + '"' + (lang === "si" ? ' lang="si"' : "") + '><span class="k">' + (k + 1) + "</span><span>" + rich(o) + "</span></button>");
        b.addEventListener("click", () => answer(k + 1)); opts.appendChild(b);
      });
      card.appendChild(opts);
      card.appendChild(h('<div class="lq-x" hidden><b class="sm">Why</b><p class="sm t2">' + (x ? rich(x) : "Explanation coming soon for this question.") + "</p>" + xNote + "</div>"));
      card.appendChild(h('<div class="lq-foot"><span class="lq-pts" aria-live="polite"></span><span class="sp"></span><a class="lnk lq-go" href="#">Practise ' + esc(q.topic) + ' free →</a><button type="button" class="btn s lq-next">Next question</button></div>'));
      card.querySelectorAll(".lq-lang [data-l]").forEach((b) => b.addEventListener("click", () => { if (b.dataset.l === lang) return; lang = b.dataset.l; const p = picked; paint(); if (p) answer(p, true); }));
      card.querySelector(".lq-next").addEventListener("click", next);
      card.querySelector(".lq-go").addEventListener("click", (e) => e.preventDefault());
      meta();
    }
    function answer(k, instant) {
      if (picked && !instant) return;
      picked = k;
      const opts = [...card.querySelectorAll(".opt")], me = opts[k - 1], good = opts[q.ok - 1], right = k === q.ok;
      opts.forEach((b) => b.setAttribute("aria-disabled", "true"));
      const mark = () => {
        me.classList.add(right ? "ok" : "bad"); me.insertAdjacentHTML("beforeend", I(right ? "check-circle-fill" : "x-circle-fill"));
        if (!right) { good.classList.add("ok", "rev"); good.insertAdjacentHTML("beforeend", I("check-circle-fill")); }
        opts.filter((b) => b !== me && b !== good).forEach((b) => b.classList.add("dim"));
        const x = card.querySelector(".lq-x"), pts = card.querySelector(".lq-pts");
        pts.innerHTML = right ? '<span class="coin lg"></span><b class="num">+10</b><span class="xs t3">points in the app</span>' : '<span class="xs t2">The answer is ' + q.ok + ". Nothing lost: try the next one.</span>";
        x.hidden = false;
        if (instant || reduced()) return;
        gsap.fromTo(x, { height: 0, opacity: 0 }, { height: "auto", opacity: 1, duration: 12 * FR, ease: E.softLand, clearProps: "height" });
        if (right) gsap.fromTo(pts.querySelector(".coin"), { scale: 1.6, rotate: -20 }, { scale: 1, rotate: 0, duration: 11 * FR, ease: E.snapSettle });
        gsap.fromTo(pts, { y: 6, opacity: 0 }, { y: 0, opacity: 1, duration: 10 * FR, ease: E.softLand });
      };
      if (instant || reduced()) return mark();
      gsap.timeline().to(me, { scale: 0.97, duration: 2 * FR, ease: "power1.out" }).to(me, { scale: 1, duration: 6 * FR, ease: E.softLand }).add(mark, 3 * FR);
    }
    function next() {
      const go = () => { deal(); paint(); if (!reduced()) gsap.fromTo(card.children, { y: 12, opacity: 0 }, { y: 0, opacity: 1, duration: 12 * FR, ease: E.softLand, stagger: 2 * FR }); };
      if (reduced()) return go();
      gsap.to(card.children, { y: -8, opacity: 0, duration: 6 * FR, ease: E.gentleIn, stagger: FR, onComplete: go });
    }
    const pickSubject = (id) => { sid = id; queue = []; chips(left, subjects, sid, pickSubject); next(); };
    root.addEventListener("keydown", (e) => {
      if (/^[1-5]$/.test(e.key) && q && +e.key <= q.en.o.length) { e.preventDefault(); answer(+e.key); }
      else if (e.key === "Enter" && picked && e.target.tagName !== "BUTTON" && e.target.tagName !== "A") { e.preventDefault(); next(); }
    });
    chips(left, subjects, sid, pickSubject); deal(); paint();
  }

  /* ---------------------------------------------------------------- Flashcard deck */
  const TONES = ["", "sky", "butter", "violet", "coral"];
  const RATE = [["ag", "Again", "<1 min"], ["hd2", "Hard", "6 min"], ["gd", "Good", "1 day"], ["ez", "Easy", "4 days"]];
  function Deck(root) {
    const left = root.querySelector("[data-lf-chips]"), stage = root.querySelector("[data-lf-stage]"), rate = root.querySelector("[data-lf-rate]"), count = root.querySelector("[data-lf-count]");
    const subjects = S.subjects.filter((s) => s.f > 0);
    let sid = (subjects.find((s) => s.t === "Biology") || subjects[0]).id, deck = [], pos = 0, flipped = false, busy = false;
    const POSE = [{ x: 0, y: 0, rotate: 0, scale: 1 }, { x: 14, y: 10, rotate: 3, scale: 0.96 }, { x: 26, y: 20, rotate: 6, scale: 0.92 }];
    const cardEl = (c, k) => h('<div class="lf-card" data-k="' + k + '"><div class="lf-in"><div class="fc lf-face ' + TONES[k % TONES.length] + '"><span class="ey">' + esc(c.topic) + '</span><p class="q">' + rich(c.f) + '</p><span class="xs lf-hint">Click or press Space to flip</span></div>' +
      '<div class="fc back lf-face lf-back"><span class="ey">Answer</span><p class="q lf-a">' + rich(c.b) + "</p></div></div></div>");
    function lay(animate) {
      stage.innerHTML = "";
      const show = [0, 1, 2].map((d) => deck[(pos + d) % deck.length]);
      show.slice().reverse().forEach((c, ri) => { const d = 2 - ri, el = cardEl(c, pos + d); stage.appendChild(el); gsap.set(el, Object.assign({ zIndex: 3 - d }, animate && d < 2 ? POSE[d + 1] : POSE[d])); if (animate && d < 2 && !reduced()) gsap.to(el, Object.assign({ duration: 12 * FR, ease: E.softLand, delay: d * 2 * FR }, POSE[d])); });
      flipped = false; rate.classList.remove("on"); rate.setAttribute("aria-hidden", "true");
      count.textContent = (pos % deck.length) + 1 + " / " + deck.length + " · " + short(subj(sid).t);
      stage.lastChild.addEventListener("click", flip);
    }
    function flip() {
      if (busy) return;
      flipped = !flipped;
      const inner = stage.lastChild.querySelector(".lf-in");
      if (reduced()) gsap.set(inner, { rotateY: flipped ? 180 : 0 }); else gsap.to(inner, { rotateY: flipped ? 180 : 0, duration: 14 * FR, ease: E.softLand });
      rate.classList.toggle("on", flipped); rate.setAttribute("aria-hidden", String(!flipped));
    }
    function grade(n) {
      if (!flipped || busy) return;
      busy = true;
      const top = stage.lastChild, again = n === 0, done = () => { pos = (pos + 1) % deck.length; busy = false; lay(true); };
      if (reduced()) return done();
      gsap.to(top, { x: again ? -170 : 190, y: again ? 10 : -20, rotate: again ? -10 : 9, duration: 10 * FR, ease: E.accelExit, onComplete: done });
      gsap.to(top, { opacity: 0, duration: 4 * FR, delay: 6 * FR, ease: "none" });
    }
    rate.innerHTML = RATE.map(([c, l, t], k) => '<button type="button" class="' + c + '" data-g="' + k + '">' + l + "<small>" + (k + 1) + " · " + t + "</small></button>").join("");
    rate.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => grade(+b.dataset.g)));
    root.addEventListener("keydown", (e) => {
      if (e.key === " " && e.target.tagName !== "BUTTON") { e.preventDefault(); flip(); }
      else if (/^[1-4]$/.test(e.key)) { e.preventDefault(); grade(+e.key - 1); }
    });
    const pickSubject = (id) => { sid = id; deck = shuffle(S.flashcards.filter((c) => c.s === sid)); pos = 0; chips(left, subjects, sid, pickSubject); lay(true); };
    pickSubject(sid);
  }

  /* ---------------------------------------------------------------- Exam insights */
  function Insights(root) {
    const left = root.querySelector("[data-li-chips]"), chart = root.querySelector("[data-li-chart]"), note = root.querySelector("[data-li-note]"), cta = root.querySelector("[data-li-cta]");
    const st = D.streams.find((s) => s.code === "al-science"), subjects = st.ids.map((id) => D.subjects[id]).filter((s) => (s.topics || []).some((t) => t.x));
    let sid = (subjects.find((s) => s.t === "Physics") || subjects[0]).id, seen = false;
    function paint() {
      const s = D.subjects[sid], ts = s.topics.filter((t) => t.x).sort((a, b) => b.x - a.x), top = ts.slice(0, 8), rest = ts.slice(8).reduce((a, t) => a + t.x, 0), max = top[0].x;
      const rows = top.map((t) => ({ t: t.t, x: t.x, d: t.sc + " subtopics · " + t.q + " questions" })).concat(rest ? [{ t: "Other topics", x: Math.round(rest * 10) / 10, d: ts.length - 8 + " more topics" }] : []);
      chart.style.setProperty("--subj", s.c);
      chart.innerHTML = rows.map((r, k) => '<button type="button" class="li-row' + (k === rows.length - 1 && rest ? " rest" : "") + '" data-k="' + k + '"><span class="li-t">' + esc(r.t) + '</span><span class="li-bar"><i style="--v:' + ((r.x / max) * 100).toFixed(1) + '%"></i></span><b class="num">' + r.x + "%</b></button>").join("");
      const info = (r) => { note.innerHTML = "<b>" + esc(r.t) + "</b>: about " + r.x + "% of " + esc(s.t) + " Paper I marks over the last 12 years · " + esc(r.d); };
      chart.querySelectorAll(".li-row").forEach((b) => ["pointerenter", "focus"].forEach((ev) => b.addEventListener(ev, () => info(rows[+b.dataset.k]))));
      info(rows[0]);
      cta.textContent = "Start with " + top[0].t + " →";
      if (seen) grow();
    }
    const grow = () => { const bars = chart.querySelectorAll(".li-bar i"); if (reduced()) return; gsap.fromTo(bars, { scaleX: 0 }, { scaleX: 1, transformOrigin: "0 50%", duration: 14 * FR, ease: E.softLand, stagger: 2 * FR }); };
    const pickSubject = (id) => { sid = id; chips(left, subjects, sid, pickSubject); paint(); };
    cta.addEventListener("click", (e) => e.preventDefault());
    pickSubject(sid);
    new IntersectionObserver((es, o) => { if (es.some((e) => e.isIntersecting)) { seen = true; grow(); o.disconnect(); } }, { threshold: 0.35 }).observe(chart);
  }

  /* ---------------------------------------------------------------- FAQ */
  function Faq(root) {
    const items = [...root.querySelectorAll(".faq-i")];
    items.forEach((it) => {
      const b = it.querySelector("button"), a = it.querySelector(".faq-a");
      b.addEventListener("click", () => {
        const open = b.getAttribute("aria-expanded") !== "true";
        items.forEach((o) => { if (o !== it && o.querySelector("button").getAttribute("aria-expanded") === "true") toggle(o, false); });
        toggle(it, open);
      });
      function toggle(node, on) {
        const bb = node.querySelector("button"), aa = node.querySelector(".faq-a");
        bb.setAttribute("aria-expanded", String(on)); node.classList.toggle("on", on);
        if (reduced()) { aa.hidden = !on; return; }
        if (on) { aa.hidden = false; gsap.fromTo(aa, { height: 0, opacity: 0 }, { height: "auto", opacity: 1, duration: 10 * FR, ease: E.softLand, clearProps: "height" }); }
        else gsap.to(aa, { height: 0, opacity: 0, duration: 8 * FR, ease: E.gentleIn, onComplete: () => { aa.hidden = true; gsap.set(aa, { clearProps: "height,opacity" }); } });
      }
      it.toggle = (on) => toggle(it, on);
      a.hidden = b.getAttribute("aria-expanded") !== "true";
    });
  }

  const boot = () => {
    document.querySelectorAll("[data-lq]").forEach(Question);
    document.querySelectorAll("[data-lf]").forEach(Deck);
    document.querySelectorAll("[data-li]").forEach(Insights);
    document.querySelectorAll("[data-faq]").forEach(Faq);
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
