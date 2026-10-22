/* Quilt Map concept A: deterministic fractal tree.
   The current node is the root at the bottom; its children are the branch tips.
   Clicking a tip flies the camera to it, the tip becomes the new root and a new tree grows.
   Branch split, angles, lengths and bends come from FNV-1a hashes of node ids, so a subject
   always grows the same tree. Needs qm.js (window.QM) loaded first. */
(function () {
  "use strict";
  const Q = window.QM;
  const { el, hash, tween, lerp, node, hub, clip } = Q;
  const R = { x: 500, y: 548 };

  function groupsOf(items, depth) {
    const n = items.length;
    const k = n <= 3 ? n : depth === 0 && n >= 5 ? 3 : 2;
    const out = [];
    let start = 0;
    for (let i = 0; i < k; i++) {
      const size = Math.round((n - start) / (k - i));
      out.push(items.slice(start, start + size));
      start += size;
    }
    return out;
  }
  // Recursively split items into branches. Each branch gets an angular sector sized by its leaf count.
  function grow(items, p, dir, len, depth, a0, a1, segs, tips) {
    if (items.length === 1 && depth > 0) { tips.push({ it: items[0], x: p.x, y: p.y, seg: segs[segs.length - 1] }); return; }
    const total = items.length;
    let acc = a0;
    for (const g of groupsOf(items, depth)) {
      const span = ((a1 - a0) * g.length) / total, s0 = acc, s1 = acc + span;
      acc = s1;
      const h = hash(g.map((x) => x.id).join("|"));
      const d = lerp(dir, (s0 + s1) / 2, 0.92) + (h - 0.5) * 0.08;
      const L = len * (0.95 + h * 0.2);
      const end = { x: p.x + L * Math.cos(d), y: p.y + L * Math.sin(d) };
      const perp = d + Math.PI / 2, bend = (h - 0.5) * L * 0.3;
      const c = { x: (p.x + end.x) / 2 + bend * Math.cos(perp), y: (p.y + end.y) / 2 + bend * Math.sin(perp) };
      segs.push({ p, c, end, depth: depth + 1, items: g });
      grow(g, end, d, len * 0.82, depth + 1, s0, s1, segs, tips);
    }
  }
  // Push tips apart until no two are closer than D, then re-aim each tip's last branch at it.
  function relax(tips, D) {
    for (let k = 0; k < 80; k++) {
      let moved = false;
      for (let i = 0; i < tips.length; i++) for (let j = i + 1; j < tips.length; j++) {
        const a = tips[i], b = tips[j];
        let dx = b.x - a.x, dy = b.y - a.y;
        const d = Math.hypot(dx, dy) || 0.01;
        if (d < D) {
          if (Math.abs(dx) < 0.01) dx = j % 2 ? 1 : -1;
          const push = (D - d) / 2, ux = dx / d, uy = dy / d;
          a.x -= ux * push; a.y -= uy * push * 0.35; b.x += ux * push; b.y += uy * push * 0.35;
          moved = true;
        }
      }
      for (const t of tips) { t.x = Math.max(70, Math.min(930, t.x)); t.y = Math.max(132, Math.min(R.y - 150, t.y)); }
      if (!moved) break;
    }
    for (const t of tips) {
      const s = t.seg;
      if (!s) continue;
      s.c = { x: (s.p.x + t.x) / 2 + (s.c.x - (s.p.x + s.end.x) / 2) * 0.5, y: (s.p.y + t.y) / 2 + (s.c.y - (s.p.y + s.end.y) / 2) * 0.5 };
      s.end = { x: t.x, y: t.y };
    }
  }
  function hexOf(c) { return /^#[0-9a-f]{6}$/i.test(c) ? c : null; }
  function avg(items, fallback) {
    const hs = items.map((i) => hexOf(i.color)).filter(Boolean);
    if (!hs.length) return fallback;
    const ch = [1, 3, 5].map((o) => Math.round(hs.reduce((a, h) => a + parseInt(h.substr(o, 2), 16), 0) / hs.length));
    return "#" + ch.map((v) => v.toString(16).padStart(2, "0")).join("");
  }

  class TreeRenderer {
    constructor(svg, ctl) { this.svg = svg; this.ctl = ctl; this.scene = null; }
    layout(level) {
      const items = level.items;
      const segs = [], tips = [];
      if (!items.length) return { segs, tips, maxD: 1 };
      const h = hash(level.id);
      const T = { x: R.x + (h - 0.5) * 16, y: R.y - 120 };
      segs.push({ p: R, c: { x: R.x + (h - 0.5) * 30, y: (R.y + T.y) / 2 }, end: T, depth: 0, items });
      const spread = Math.min(Math.PI - 0.22, 1.5 + items.length * 0.11);
      grow(items, T, -Math.PI / 2, 150, 0, -Math.PI / 2 - spread / 2, -Math.PI / 2 + spread / 2, segs, tips);
      // Fit everything above the root into the stage, keeping the root fixed.
      let minY = R.y, maxDX = 1;
      const pts = segs.flatMap((s) => [s.end, s.c]).concat(tips);
      for (const q of pts) { minY = Math.min(minY, q.y); maxDX = Math.max(maxDX, Math.abs(q.x - R.x)); }
      const s = Math.min((R.y - 110) / (R.y - minY), 420 / maxDX, 1.6);
      const map = (q) => ({ x: R.x + (q.x - R.x) * s, y: R.y + (q.y - R.y) * s });
      segs.forEach((sg) => { sg.p = map(sg.p); sg.c = map(sg.c); sg.end = map(sg.end); });
      tips.forEach((t) => Object.assign(t, map(t)));
      relax(tips, Math.max(118, 70 + 330 / Math.max(1, items.length)));
      return { segs, tips, maxD: Math.max(...segs.map((x) => x.depth)) };
    }
    build(level) {
      const g = el("g", { class: "qm-scene" }, this.svg);
      const { segs, tips, maxD } = this.layout(level);
      el("path", { d: "M120 " + (R.y + 2) + "H880", class: "qm-ground" }, g);
      const br = el("g", {}, g);
      for (const s of segs) {
        const col = avg(s.items, level.color && hexOf(level.color) ? level.color : "#8a7fa8");
        const ink = Math.round(100 - Math.min(100, (s.depth / maxD) * 100));
        const w = Math.max(2, 15 * Math.pow(0.6, s.depth));
        el("path", {
          d: "M" + s.p.x.toFixed(1) + " " + s.p.y.toFixed(1) + "Q" + s.c.x.toFixed(1) + " " + s.c.y.toFixed(1) + " " + s.end.x.toFixed(1) + " " + s.end.y.toFixed(1),
          pathLength: 1, class: "qm-branch qm-draw", "data-d": s.depth,
          style: "stroke-width:" + w.toFixed(1) + ";stroke:color-mix(in srgb, var(--merit-text-primary) " + ink + "%, " + col + ")",
        }, br);
        if (s.items.length > 1 && s.depth > 0) {
          const fh = hash(s.items[0].id + "fork");
          if (fh < 0.35) el("path", { d: spark(s.end.x, s.end.y - 10, 7), class: "qm-spark qm-fade", "data-d": s.depth }, br);
          else el("circle", { cx: s.end.x, cy: s.end.y, r: Math.max(2.5, w * 0.55), class: "qm-fork qm-fade", "data-d": s.depth, style: "fill:color-mix(in srgb, var(--merit-text-primary) " + ink + "%, " + col + ")" }, br);
        }
      }
      if (!level.items.length) el("text", { x: R.x, y: R.y - 160, class: "qm-meta", "text-anchor": "middle", text: "Topics are on the way for this subject" }, g);
      const leaf = level.kind === "topic";
      const size = level.kind === "root" ? 62 : Math.max(40, 58 - level.items.length * 1.2);
      const nodes = tips.map((t) => ({ g: node(g, t.it, t.x, t.y, size, this.ctl, { above: true, nometa: true }), t }));
      // Root badge: Merit mark on level 0, then the selected subject or topic plate.
      const rootG = el("g", { class: "qm-root" }, g);
      if (level.kind === "root") {
        el("circle", { cx: R.x, cy: R.y, r: 46, class: "qm-plate" }, rootG);
        el("image", { href: "assets/v3/brand/merit-mark.svg", x: R.x - 34, y: R.y - 36, width: 68, height: 68 }, rootG);
      } else {
        hub(rootG, level, R.x, R.y - 6, 62);
        if (!this.ctl.opts.static) el("text", { x: R.x + 46, y: R.y + 2, class: "qm-lab", "text-anchor": "start", text: clip(level.label, 30) }, rootG);
      }
      return { g, nodes, rootG, leaf };
    }
    async render(level, from, mode) {
      const old = this.scene;
      if (old && mode === "in" && from) {
        const hit = old.nodes.find((n) => n.t.it.id === from.id);
        const T = hit ? hit.t : R;
        [...old.g.children].forEach((c) => { if (c !== (hit && hit.g)) c.dataset.fade = "1"; });
        await tween(560, (t) => {
          const cx = lerp(R.x, T.x, t), cy = lerp(R.y, T.y, t), k = lerp(1, 1.9, t);
          old.g.setAttribute("transform", "translate(" + R.x + " " + R.y + ") scale(" + k + ") translate(" + -cx + " " + -cy + ")");
          old.g.querySelectorAll("[data-fade]").forEach((e) => (e.style.opacity = 1 - t));
          if (hit) hit.g.style.opacity = 1 - Math.max(0, t - 0.7) / 0.3;
        });
      } else if (old) {
        await tween(mode === "none" ? 0 : 380, (t) => {
          old.g.style.opacity = 1 - t;
          old.g.setAttribute("transform", "translate(" + R.x + " " + R.y + ") scale(" + lerp(1, mode === "out" ? 0.45 : 0.9, t) + ") translate(" + -R.x + " " + -R.y + ")");
        });
      }
      if (old) old.g.remove();
      const sc = (this.scene = this.build(level));
      if (this.ctl.opts.static) return;
      const draws = sc.g.querySelectorAll(".qm-draw"), fades = sc.g.querySelectorAll(".qm-fade");
      draws.forEach((d) => { d.style.strokeDasharray = "1"; d.style.strokeDashoffset = "1"; });
      fades.forEach((f) => (f.style.opacity = 0));
      sc.nodes.forEach((n) => n.g.querySelector(".qm-pop").setAttribute("transform", "scale(0)"));
      sc.rootG.style.opacity = mode === "in" ? 1 : 0;
      await tween(950, (t) => {
        sc.rootG.style.opacity = Math.max(+sc.rootG.style.opacity, Math.min(1, t * 4));
        draws.forEach((d) => { const dd = +d.dataset.d; d.style.strokeDashoffset = 1 - Math.max(0, Math.min(1, (t - dd * 0.11) / 0.32)); });
        fades.forEach((f) => { const dd = +f.dataset.d; f.style.opacity = Math.max(0, Math.min(1, (t - dd * 0.11 - 0.2) / 0.2)); });
        sc.nodes.forEach((n, i) => {
          const k = Math.max(0, Math.min(1, (t - 0.5 - i * 0.025) / 0.3));
          n.g.querySelector(".qm-pop").setAttribute("transform", "scale(" + (k < 1 ? k * (1.12 - 0.12 * k) : 1).toFixed(3) + ")");
        });
      });
    }
  }
  function spark(x, y, r) {
    const q = r * 0.28;
    return "M" + x + " " + (y - r) + "Q" + (x + q) + " " + (y - q) + " " + (x + r) + " " + y + "Q" + (x + q) + " " + (y + q) + " " + x + " " + (y + r) + "Q" + (x - q) + " " + (y + q) + " " + (x - r) + " " + y + "Q" + (x - q) + " " + (y - q) + " " + x + " " + (y - r) + "Z";
  }

  window.QMTree = TreeRenderer;
  const boot = () => document.querySelectorAll('[data-qm="tree"]').forEach((h) => new Q.Explorer(h, TreeRenderer, { static: h.hasAttribute("data-static") }));
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
