/* Merit wireframes board: flow tabs (hash), theme + width toggles, and the pick tracker.
   Picks live in the artifact's shared db ("picks/<screen>") when published; locally they
   fall back to localStorage so the board still works over file://. */
(function () {
  const root = document.documentElement;
  const ls = {
    get(k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage blocked */ } },
  };

  /* ---------- toggles ---------- */
  function bindSeg(name, apply) {
    const seg = document.querySelector('[data-seg="' + name + '"]');
    if (!seg) return;
    const saved = ls.get("wf-" + name);
    const set = (val) => {
      seg.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.val === val)));
      apply(val);
      ls.set("wf-" + name, val);
    };
    seg.addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) set(b.dataset.val); });
    set(saved || seg.querySelector('[aria-pressed="true"]').dataset.val);
  }
  bindSeg("theme", (v) => { if (v === "system") root.removeAttribute("data-theme"); else root.setAttribute("data-theme", v); });
  bindSeg("width", (v) => root.setAttribute("data-width", v));

  /* ---------- flows ---------- */
  const flows = [...document.querySelectorAll(".wf-flow")];
  const tabs = [...document.querySelectorAll(".wf-flows a")];
  function show(id) {
    if (!flows.some((f) => f.dataset.flow === id)) id = flows[0].dataset.flow;
    flows.forEach((f) => { f.hidden = f.dataset.flow !== id; });
    tabs.forEach((t) => (t.hash === "#" + id ? t.setAttribute("aria-current", "page") : t.removeAttribute("aria-current")));
  }
  tabs.forEach((t) => t.addEventListener("click", (e) => {
    e.preventDefault();
    show(t.hash.slice(1));
    try { history.replaceState(null, "", t.hash); } catch (err) { /* sandboxed */ }
    window.scrollTo({ top: 0 });
  }));
  show(location.hash.slice(1));
  window.scrollTo(0, 0);

  /* ---------- picks ---------- */
  const screens = [...document.querySelectorAll(".wf-screen[data-screen]")];
  const state = {};
  let col = null;

  function render() {
    let n = 0, total = 0;
    screens.forEach((s) => {
      const p = state[s.dataset.screen] || {};
      const cands = s.querySelectorAll(".wf-cand[data-v]");
      if (cands.length > 1) total++;
      if (p.variant && cands.length > 1) n++;
      cands.forEach((c) => {
        const on = c.dataset.v === p.variant;
        c.classList.toggle("is-picked", on);
        const b = c.querySelector(".wf-pick button");
        if (b) { b.setAttribute("aria-pressed", String(on)); b.textContent = on ? "Picked " + c.dataset.v : "Pick " + c.dataset.v; }
      });
      const ta = s.querySelector(".wf-feedback textarea");
      if (ta && document.activeElement !== ta && typeof p.note === "string") ta.value = p.note;
    });
    const tally = document.querySelector(".wf-tally");
    if (tally) tally.textContent = n + " of " + total + " screens picked";
  }

  async function save(id, patch) {
    const next = Object.assign({}, state[id] || {}, patch, { at: new Date().toISOString() });
    state[id] = next;
    render();
    const flag = document.querySelector('.wf-screen[data-screen="' + id + '"] .wf-saved');
    try {
      if (col) { await col.doc(id).set(next); if (flag) flag.textContent = "Saved for everyone with this link"; }
      else { ls.set("wf-picks", state); if (flag) flag.textContent = "Saved on this device only"; }
    } catch (e) {
      if (flag) flag.textContent = e && e.code === "not_granted" ? "You can view picks but not change them" : "Couldn't save. Try again in a moment.";
    }
  }

  screens.forEach((s) => {
    const id = s.dataset.screen;
    s.addEventListener("click", (e) => {
      const b = e.target.closest(".wf-pick button");
      if (!b) return;
      const v = b.closest(".wf-cand").dataset.v;
      save(id, { variant: (state[id] || {}).variant === v ? null : v });
    });
    const ta = s.querySelector(".wf-feedback textarea");
    if (ta) {
      let t = null;
      const flush = () => { clearTimeout(t); t = null; if (ta.value.trim() !== ((state[id] || {}).note || "")) save(id, { note: ta.value.trim() }); };
      ta.addEventListener("input", () => { clearTimeout(t); t = setTimeout(flush, 1200); });
      ta.addEventListener("blur", flush);
    }
  });

  Object.assign(state, ls.get("wf-picks") || {});
  render();

  if (window.claude && window.claude.use) {
    window.claude.use("db").then((db) => {
      if (!db) return;
      col = db.collection("picks");
      col.onSnapshot((snap) => {
        Object.keys(state).forEach((k) => delete state[k]);
        snap.docs.forEach((d) => { state[d.id] = d.data(); });
        render();
      }, () => { col = null; });
    });
  }
})();
