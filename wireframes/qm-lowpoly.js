/* Quilt Map concept A, round 12: low-poly tree (2.5D SVG + GSAP, facets from Delaunator).
   Same data and controller as qm.js (Explorer: chips, breadcrumb, topic panel, Esc). This file is the renderer:
   a faceted trunk, tapered faceted branches, and one canopy cluster per subject at its branch tip. Opening a
   subject tweens the viewBox to its cluster, which splits into one sub-cluster per topic on sub-branches.
   Layout is deterministic: FNV-1a hashes of node ids (grow() is ported from qm-tree.js). Shading: each facet gets
   a tone from its normal against a light from the top left. Mount: [data-qm="lowpoly"] (data-stream, optional
   data-static = no chips/panel/clicks, final frame; add data-grow to animate a static mount).
   Needs gsap, Delaunator and qm.js (window.QM) loaded first. The pure geometry is exported for node tests. */
(function (root) {
  "use strict";
  const W = 800, H = 700, BASE = { x: 400, y: 598 };
  const lerp = (a, b, t) => a + (b - a) * t, clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const unit = (v) => { const m = Math.hypot(v[0], v[1], v[2] || 0) || 1; return v.map((x) => x / m); };
  const LIGHT = unit([-0.55, -0.65, 0.5]); // from the top left, toward the viewer

  /* ------------------------------------------------------------ pure geometry */
  function geometry(hash, Delaunator) {
    function groupsOf(items, depth) {
      const n = items.length, k = n <= 3 ? n : depth === 0 && n >= 5 ? 3 : 2, out = [];
      let start = 0;
      for (let i = 0; i < k; i++) { const size = Math.round((n - start) / (k - i)); out.push(items.slice(start, start + size)); start += size; }
      return out;
    }
    // Recursively split items into branches; each gets an angular sector sized by its leaf count. par = parent seg index.
    function grow(items, p, dir, len, depth, a0, a1, segs, tips, par, d0) {
      if (items.length === 1 && depth > 0) { tips.push({ it: items[0], x: p.x, y: p.y, seg: par }); return; }
      let acc = a0;
      for (const g of groupsOf(items, depth)) {
        const span = ((a1 - a0) * g.length) / items.length, s0 = acc, s1 = acc + span;
        acc = s1;
        const h = hash(g.map((x) => x.id).join("|"));
        const d = lerp(dir, (s0 + s1) / 2, 0.92) + (h - 0.5) * 0.08, L = len * (0.95 + h * 0.2);
        const end = { x: p.x + L * Math.cos(d), y: p.y + L * Math.sin(d) }, bend = (h - 0.5) * L * 0.42;
        const c = { x: (p.x + end.x) / 2 + bend * Math.cos(d + Math.PI / 2), y: (p.y + end.y) / 2 + bend * Math.sin(d + Math.PI / 2) };
        segs.push({ p, c, end, depth: depth + 1 + d0, items: g, par });
        grow(g, end, d, len * 0.82, depth + 1, s0, s1, segs, tips, segs.length - 1, d0);
      }
    }
    // Push tips apart (mostly sideways) until none is closer than D, then re-aim each tip's last branch at it.
    function relax(tips, segs, D, box) {
      for (let k = 0; k < 90; k++) {
        let moved = false;
        for (let i = 0; i < tips.length; i++) for (let j = i + 1; j < tips.length; j++) {
          const a = tips[i], b = tips[j];
          let dx = b.x - a.x, dy = b.y - a.y;
          const d = Math.hypot(dx, dy) || 0.01;
          if (d < D) {
            if (Math.abs(dx) < 0.01) dx = j % 2 ? 1 : -1;
            const m = (D - d) / 2, ux = dx / d, uy = dy / d;
            a.x -= ux * m; a.y -= uy * m * 0.4; b.x += ux * m; b.y += uy * m * 0.4; moved = true;
          }
        }
        if (box) for (const t of tips) { t.x = clamp(t.x, box[0], box[1]); t.y = clamp(t.y, box[2], box[3]); }
        if (!moved) break;
      }
      for (const t of tips) {
        const s = segs[t.seg];
        if (!s) continue;
        const mx = (s.p.x + s.end.x) / 2, my = (s.p.y + s.end.y) / 2;
        s.c = { x: (s.p.x + t.x) / 2 + (s.c.x - mx) * 0.5, y: (s.p.y + t.y) / 2 + (s.c.y - my) * 0.5 };
        s.end = { x: t.x, y: t.y };
      }
    }
    // o: {o:origin, dir, trunk:{len}|null, stub, len, scale:(pts)=>k, D, box, d0}
    function layout(items, id, o) {
      const segs = [], tips = [];
      if (!items.length) return { segs, tips };
      const h = hash(id);
      let p = o.o, par = -1;
      const dir = o.dir;
      if (o.trunk) {
        const T = { x: p.x + (h - 0.5) * 18, y: p.y - o.trunk };
        segs.push({ p, c: { x: p.x + (h - 0.5) * 34, y: (p.y + T.y) / 2 }, end: T, depth: 0, items, par: -1 });
        p = T; par = 0;
      } else {
        const T = { x: p.x + 30 * Math.cos(dir), y: p.y + 30 * Math.sin(dir) };
        segs.push({ p, c: { x: (p.x + T.x) / 2 + (h - 0.5) * 6, y: (p.y + T.y) / 2 }, end: T, depth: o.d0, items, par: -1 });
        p = T; par = 0;
      }
      const spread = Math.min(Math.PI - 0.22, o.spread != null ? o.spread : 1.5 + items.length * 0.11);
      grow(items, p, dir, o.len, 0, dir - spread / 2, dir + spread / 2, segs, tips, par, o.d0);
      const k = o.scale(segs.flatMap((s) => [s.end, s.c]).concat(tips)), O = o.o;
      const map = (q) => ({ x: O.x + (q.x - O.x) * k, y: O.y + (q.y - O.y) * k });
      segs.forEach((s) => { s.p = map(s.p); s.c = map(s.c); s.end = map(s.end); });
      tips.forEach((t) => Object.assign(t, map(t)));
      relax(tips, segs, o.D, o.box);
      tips.forEach((t) => { t.chain = []; for (let i = t.seg; i >= 0; i = segs[i].par) t.chain.unshift(segs[i]); });
      return { segs, tips };
    }
    // Delaunay over [x,y,z] points; one tone (0 dark .. 5 lit) per triangle from its normal against the light.
    function shade(P, seed, cx, cy) {
      const tri = Delaunator.from(P, (p) => p[0], (p) => p[1]).triangles, out = [];
      for (let i = 0; i < tri.length; i += 3) {
        const a = P[tri[i]], b = P[tri[i + 1]], c = P[tri[i + 2]];
        const u = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], v = [c[0] - a[0], c[1] - a[1], c[2] - a[2]];
        let n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
        if (n[2] < 0) n = n.map((x) => -x);
        n = unit(n);
        const lit = n[0] * LIGHT[0] + n[1] * LIGHT[1] + n[2] * LIGHT[2] + (hash(seed + "j" + i) - 0.5) * 0.16;
        const tone = lit < -0.05 ? 0 : lit < 0.2 ? 1 : lit < 0.4 ? 2 : lit < 0.6 ? 3 : lit < 0.8 ? 4 : 5;
        const mx = (a[0] + b[0] + c[0]) / 3, my = (a[1] + b[1] + c[1]) / 3;
        out.push({ pts: [a, b, c].map((q) => q[0].toFixed(1) + "," + q[1].toFixed(1)).join(" "), tone, d: Math.hypot(mx - cx, my - cy) });
      }
      return out.sort((x, y) => x.d - y.d);
    }
    // Rings of jittered points: rings = [[count, radius fraction, dome height fraction, angle jitter]], then a crown point.
    function blob(cx, cy, rx, ry, hz, seed, rings) {
      const P = [], rot = hash(seed + "rot") * 6.283;
      rings.forEach((rg, k) => {
        for (let i = 0; i < rg[0]; i++) {
          const a = rot + k * 0.4 + (i / rg[0]) * 6.283 + (hash(seed + "a" + k + i) - 0.5) * rg[3], f = rg[1] * (k ? 1 : 0.8 + 0.34 * hash(seed + "o" + i)) * (k ? 0.8 + 0.4 * hash(seed + "q" + k + i) : 1);
          P.push([cx + rx * f * Math.cos(a), cy + ry * f * Math.sin(a) - (k ? hz * 0.05 : 0), hz * (k ? rg[2] * (0.8 + 0.4 * hash(seed + "y" + k + i)) : rg[2] * hash(seed + "z" + i))]);
        }
      });
      P.push([cx + (hash(seed + "cx") - 0.5) * rx * 0.2, cy - ry * 0.12, hz * 0.98]);
      return shade(P, seed, cx, cy);
    }
    // Subject cluster: outer ring + mid ring + crown point, about 28 to 32 facets.
    function canopy(cx, cy, r, seed, nOut, nMid) { return blob(cx, cy, r * 1.12, r * 0.94, r, seed, [[nOut, 1, 0.12, 0.4], [nMid, 0.5, 0.78, 0.5]]); }
    // Unified crown behind the clusters: a domed cloud (4 + 7 lobe bulges, underside rising towards the trunk), about 90 facets.
    // Returns the real facet bounds in box so the camera can fit them.
    function crown(tips, R, seed) {
      const xs = tips.map((t) => t.x), ys = tips.map((t) => t.y);
      const x0 = Math.min(...xs), x1 = Math.max(...xs), bot = Math.max(...ys) + R * 0.9;
      const rx = (x1 - x0) / 2 + R * 0.5, ry = Math.max((bot - (Math.min(...ys) - R * 1.1)) / 2, rx * 0.62), cx = (x0 + x1) / 2, cy = bot - ry, hz = Math.min(rx, ry) * 0.9, phi = hash(seed + "phi") * 6.283;
      const P = [];
      [[30, 1, 0.1], [20, 0.7, 0.45], [10, 0.38, 0.8]].forEach((rg, k) => {
        for (let i = 0; i < rg[0]; i++) {
          const th = ((i / rg[0]) * 6.283 + k * 0.3 + (hash(seed + "a" + k + i) - 0.5) * (k ? 0.35 : 0.18)) % 6.283;
          const bump = 1 + 0.09 * Math.cos(4 * th + phi) + 0.05 * Math.cos(7 * th + phi * 2) + (hash(seed + "r" + k + i) - 0.5) * (k ? 0.12 : 0.07);
          const dn = Math.sin(th) > 0 ? Math.exp(-Math.pow((th - 1.5708) / 0.8, 2)) : 0, u = 1 - 0.34 * dn * (0.5 + 0.5 * rg[1]);
          P.push([cx + rx * rg[1] * bump * Math.cos(th), cy + ry * rg[1] * bump * u * Math.sin(th), hz * rg[2]]);
        }
      });
      P.push([cx, cy - ry * 0.1, hz * 0.98]);
      const px = P.map((q) => q[0]), py = P.map((q) => q[1]);
      return { cx, cy, rx, ry, fs: shade(P, seed, cx, cy), box: [Math.min(...px), Math.min(...py), Math.max(...px), Math.max(...py)] };
    }
    // Nudge label rects {x centre, y top, w, h} down until none overlap another (stable, top first).
    function declutter(rs) {
      for (let pass = 0; pass < 6; pass++) {
        const o = rs.map((r, i) => i).sort((a, b) => rs[a].y - rs[b].y);
        let moved = false;
        for (let i = 0; i < o.length; i++) for (let j = i + 1; j < o.length; j++) {
          const a = rs[o[i]], b = rs[o[j]];
          if (Math.abs(a.x - b.x) < (a.w + b.w) / 2 + 3 && b.y < a.y + a.h + 3) { b.y = a.y + a.h + 3; moved = true; }
        }
        if (!moved) break;
      }
      return rs;
    }
    // Short decorative twigs on a seg (thin triangles off the curve).
    function twigs(s, seed, count, wBase) {
      const out = [];
      for (let j = 0; j < count; j++) {
        const t = 0.3 + 0.45 * hash(seed + "tt" + j), m = 1 - t;
        const x = m * m * s.p.x + 2 * m * t * s.c.x + t * t * s.end.x, y = m * m * s.p.y + 2 * m * t * s.c.y + t * t * s.end.y;
        const ang = Math.atan2(2 * m * (s.c.y - s.p.y) + 2 * t * (s.end.y - s.c.y), 2 * m * (s.c.x - s.p.x) + 2 * t * (s.end.x - s.c.x)) + (j % 2 ? 1 : -1) * (0.55 + 0.5 * hash(seed + "ta" + j));
        const L = 11 + 11 * hash(seed + "tl" + j), hw = Math.max(1.1, wBase * 0.16), ca = Math.cos(ang), sa = Math.sin(ang);
        const pts = [[x - sa * hw, y + ca * hw], [x + sa * hw, y - ca * hw], [x + ca * L, y + sa * L]];
        const lit = ca * LIGHT[0] + sa * LIGHT[1];
        out.push({ pts: pts.map((q) => q[0].toFixed(1) + "," + q[1].toFixed(1)).join(" "), tone: clamp(Math.floor(lit * 2 + 2), 0, 3) });
      }
      return out;
    }
    // Root flare: short triangles spreading from the trunk base along the ground.
    function roots(b, w) {
      const out = [];
      [-1, 1].forEach((sd) => [0, 1].forEach((k) => {
        const tip = [b.x + sd * (w * 0.5 + 26 + k * 24), b.y + 5 - k * 2], a = [b.x + sd * w * 0.18, b.y - 40 - k * 6], c = [b.x + sd * w * (0.5 - k * 0.18), b.y + 4];
        out.push({ pts: [a, tip, c].map((q) => q[0].toFixed(1) + "," + q[1].toFixed(1)).join(" "), tone: sd < 0 ? 2 + k : k });
      }));
      return out;
    }
    // Tapered faceted strip along a seg's quadratic curve: 2 triangles per step, 4 wood tones by facing.
    function strip(s, w0, w1, seed, wob) {
      const K = 5, A = [], B = [], out = [], amp = (wob || 0) * Math.hypot(s.end.x - s.p.x, s.end.y - s.p.y) * (hash(seed + "wb") - 0.5) * 2;
      for (let i = 0; i <= K; i++) {
        const t = i / K, m = 1 - t;
        const tx = 2 * m * (s.c.x - s.p.x) + 2 * t * (s.end.x - s.c.x), ty = 2 * m * (s.c.y - s.p.y) + 2 * t * (s.end.y - s.c.y), l = Math.hypot(tx, ty) || 1;
        const w = lerp(w0, w1, t) / 2, nx = -ty / l, ny = tx / l, o = Math.sin(t * 6.283) * amp; // S-bend, zero at both ends
        const x = m * m * s.p.x + 2 * m * t * s.c.x + t * t * s.end.x + nx * o, y = m * m * s.p.y + 2 * m * t * s.c.y + t * t * s.end.y + ny * o;
        A.push([x + nx * w, y + ny * w, nx, ny]); B.push([x - nx * w, y - ny * w]);
      }
      const f = (q) => q[0].toFixed(1) + "," + q[1].toFixed(1), tn = (lit, j) => clamp(Math.floor((lit * 0.5 + 0.5 + (hash(seed + j) - 0.5) * 0.3) * 4), 0, 3);
      for (let i = 0; i < K; i++) {
        const lit = A[i][2] * LIGHT[0] + A[i][3] * LIGHT[1];
        out.push({ pts: [A[i], B[i], A[i + 1]].map(f).join(" "), tone: tn(lit, "a" + i) });
        out.push({ pts: [B[i], B[i + 1], A[i + 1]].map(f).join(" "), tone: tn(-lit, "b" + i) });
      }
      return out;
    }
    return { grow, relax, layout, canopy, crown, declutter, strip, twigs, roots, groupsOf };
  }
  const API = { geometry, LIGHT };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  if (typeof window === "undefined") return;
  root.QMLowpoly = API;

  /* ------------------------------------------------------------ renderer */
  const Q = root.QM;
  if (!Q || !root.gsap || !root.Delaunator) { console.warn("qm-lowpoly: needs QM, gsap and Delaunator"); return; }
  const { el, hash, clip } = Q, G = geometry(hash, root.Delaunator), gsap = root.gsap;
  const BARK = "color-mix(in srgb, color-mix(in srgb, var(--merit-orange-700) 50%, var(--merit-ink-700)) 74%, var(--merit-sand-300))";
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  // Short forms for long subject titles; labels are wrapped, never clipped.
  const SHORT = { "Information & Communication Technology": "ICT", "Agricultural Science": "Agri Science", "Combined Mathematics": "Combined Maths", "Logic & Scientific Method": "Logic & Method", "Communication & Media Studies": "Media Studies", "Greek & Roman Civilization": "Greek & Roman" };
  const short = (s) => SHORT[s] || s.replace(/^Drama & Theatre/, "Drama").replace(/^History of SL & (.*)$/, "SL & $1 History").replace("Technology", "Tech").replace("Civilization", "Civ.");
  const lines = (s, n) => {
    const out = [];
    s.split(" ").forEach((w) => { const l = out[out.length - 1]; if (l != null && (l + " " + w).length <= n) out[out.length - 1] = l + " " + w; else out.push(w); });
    return out;
  };

  class LowPoly {
    constructor(svg, ctl) {
      this.svg = svg; this.ctl = ctl; this.cam = { x: 0, y: 0, w: W, h: H }; this.tw = []; this.scene = null; this.sub = null;
      this.still = ctl.opts.static && !ctl.host.hasAttribute("data-grow");
      svg.setAttribute("viewBox", "0 0 " + W + " " + H);
      svg.setAttribute("aria-label", "Merit subject tree");
      if (!ctl.opts.static) ["pointerdown", "keydown", "focusin"].forEach((ev) => ctl.host.addEventListener(ev, () => this.stopCoin(), true));
    }
    T(t) { this.tw.push(t); return t; }
    done(tl) { return new Promise((res) => tl.eventCallback("onComplete", res)); }
    cam_(box, dur) {
      const c = this.cam, svg = this.svg;
      const apply = () => { svg.setAttribute("viewBox", [c.x, c.y, c.w, c.h].map((v) => v.toFixed(1)).join(" ")); svg.style.setProperty("--lp-z", (c.w / W).toFixed(3)); };
      gsap.killTweensOf(c);
      if (dur <= 0 || reduced()) { Object.assign(c, box); apply(); return Promise.resolve(); }
      return new Promise((res) => gsap.to(c, Object.assign({ duration: dur, ease: "power3.inOut", onUpdate: apply, onComplete: () => { apply(); res(); } }, box)));
    }
    // Box that fits points (+ pad) at the stage aspect; content sits left of centre when the panel is showing.
    fit(pts, pad, flat) {
      const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
      const x0 = Math.min(...xs) - pad, x1 = Math.max(...xs) + pad, y0 = Math.min(...ys) - pad, y1 = Math.max(...ys) + pad;
      const w = Math.max(x1 - x0, ((y1 - y0) * W) / H, 300), h = (w * H) / W, shift = this.ctl.opts.static || flat ? 0 : w * 0.1;
      return { x: (x0 + x1) / 2 - w / 2 + shift, y: (y0 + y1) / 2 - h / 2, w, h };
    }

    /* ---- drawing */
    facets(parent, list, cls) {
      return list.map((f) => el("polygon", { points: f.pts, class: "lp-f " + cls + f.tone }, parent));
    }
    // Bark strips (+ short twigs). Width: trunk 44 tapering to 15 at the first fork, then 15 x 0.68 per level (min 2.4).
    branches(parent, segs, col, twigs) {
      return segs.map((s) => {
        const g = el("g", { class: "lp-br", "aria-hidden": "true", style: "--c:" + col }, parent);
        const w = (d) => (d <= 0 ? 44 : Math.max(2.4, 15 * Math.pow(0.68, d - 1)));
        const seed = s.items[0].id + s.depth;
        G.strip(s, w(s.depth), w(s.depth + 1), seed, s.depth ? 0.06 : 0.02).forEach((f) => el("polygon", { points: f.pts, class: "lp-f w" + f.tone }, g));
        if (twigs && s.depth) G.twigs(s, seed, s.depth > 3 ? 1 : 2 + Math.floor(hash(seed + "n") * 2), w(s.depth)).forEach((f) => el("polygon", { points: f.pts, class: "lp-f w" + f.tone }, g));
        g._seg = s;
        return g;
      });
    }
    label(parent, item, x, y, big, hidden) {
      const ls = lines(short(item.label), big ? 11 : 12), n = Math.max(...ls.map((l) => l.length));
      const g = el("g", { class: "lp-lab" + (hidden ? " hov" : "") }, parent);
      const w = n * 9.6 + 14, h = ls.length * 20 + 7;
      el("rect", { x: -w / 2, y: 0, width: w, height: h, rx: 11, class: "lp-pill" }, g);
      ls.forEach((l, i) => el("text", { x: 0, y: 19 + i * 20, "text-anchor": "middle", class: "lp-t", text: l }, g));
      g._r = { x, y, w, h, hidden };
      return g;
    }
    // All pills live in one top layer; declutter them at zoom z (their on-screen size is zoom independent).
    place(labs, z) {
      const live = labs.filter((l) => !l._r.hidden), rs = G.declutter(live.map((l) => ({ x: l._r.x, y: l._r.y, w: l._r.w * z, h: l._r.h * z })));
      live.forEach((l, i) => { l._r.y = rs[i].y; });
      labs.forEach((l) => { l.style.transform = "translate(" + l._r.x.toFixed(1) + "px," + l._r.y.toFixed(1) + "px) scale(var(--lp-z,1))"; });
    }
    // One clickable cluster. Returns {node, pop, cl, facets, x, y, r}.
    cluster(parent, item, x, y, r, o) {
      const soon = o.soon;
      const node = el("g", { class: "lp-node" + (soon ? " soon" : ""), style: "--c:" + (soon ? "color-mix(in srgb," + item.color + " 20%, var(--merit-text-tertiary))" : item.color) }, parent);
      if (!this.ctl.opts.static) {
        node.setAttribute("role", "button"); node.setAttribute("tabindex", "0");
        node.setAttribute("aria-label", item.label + (item.meta ? ", " + item.meta : ""));
        const go = () => this.ctl.open(item);
        node.addEventListener("click", go);
        node.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
      }
      el("title", { text: item.label }, node);
      el("circle", { cx: x, cy: y, r: r * 1.12, class: "lp-ring" }, node);
      const pop = el("g", {}, node), cl = el("g", { class: "lp-cl" }, pop);
      const fs = this.facets(cl, G.canopy(x, y, r, item.id, o.nOut, o.nMid), "t");
      const lab = this.label(o.layer, item, x, y + r * (o.big ? 0.45 : 0.72), o.big, o.hideLab);
      if (o.hideLab) ["mouseenter", "focus"].forEach((ev, i) => { node.addEventListener(ev, () => lab.classList.add("show")); node.addEventListener(["mouseleave", "blur"][i], () => lab.classList.remove("show")); });
      return { node, pop, cl, fs, lab, x, y, r, item };
    }
    sway(c) {
      if (this.still || reduced()) return;
      const o = c.x + " " + (c.y + c.r * 0.9), h = hash(c.item.id + "sway");
      const t = gsap.fromTo(c.cl, { rotation: -1, svgOrigin: o }, { rotation: 1, svgOrigin: o, duration: 3 + h * 2.2, yoyo: true, repeat: -1, ease: "sine.inOut" });
      t.progress(h); this.T(t);
    }
    // Pop a cluster's facets in from its tip outward (centre first).
    popIn(tl, c, at, each) {
      gsap.set(c.fs, { scale: 0 });
      tl.to(c.fs, { scale: 1, duration: 0.3, ease: "back.out(1.7)", stagger: each || 0.008 }, at);
    }

    /* ---- scenes */
    build(level) {
      const items = level.items, n = items.length, g = el("g", { class: "lp-scene" }, this.svg);
      const sc = { g, subj: new Map(), br: [], tips: [] };
      el("ellipse", { cx: BASE.x, cy: BASE.y + 6, rx: 170, ry: 13, class: "lp-shadow" }, g);
      el("path", { d: "M90 " + (BASE.y + 4) + "H710", class: "qm-ground" }, g);
      const R = clamp(72 - n * 2.2, 27, 62) * 1.3, many = n > 12;
      const lay = G.layout(items, level.id, {
        o: BASE, dir: -Math.PI / 2, trunk: 140, len: 130, d0: 0, D: Math.max(2 * R * 0.78, many ? 0 : 124), box: [R + 20, W - R - 20, 130 + R * 0.3, BASE.y - 190],
        scale: (pts) => { let minY = BASE.y, dx = 1; pts.forEach((q) => { minY = Math.min(minY, q.y); dx = Math.max(dx, Math.abs(q.x - BASE.x)); }); return Math.min((BASE.y - 190) / (BASE.y - minY), 300 / dx, 1.7); },
      });
      sc.lay = lay;
      lay.tips.sort((a, b) => a.y - b.y);
      // Crown first so it sits behind the bark; decorative.
      const cr = G.crown(lay.tips, R, level.id + "crown");
      sc.crown = el("g", { class: "lp-crown", "aria-hidden": "true" }, g);
      sc.crownF = this.facets(sc.crown, cr.fs, "t");
      const wood = BARK;
      const trunk = this.branches(g, lay.segs.slice(0, 1), wood)[0];
      trunk.classList.add("lp-trunk");
      G.roots(BASE, 44).forEach((f) => el("polygon", { points: f.pts, class: "lp-f w" + f.tone }, trunk));
      sc.br = this.branches(g, lay.segs.slice(1), wood, true);
      sc.coin = el("g", { class: "lp-coinlayer" }, g);
      const layer = el("g", { class: "lp-labs", "aria-hidden": "true" });
      lay.tips.forEach((t) => {
        const soon = !t.it.ref.tc;
        const c = this.cluster(g, t.it, t.x, t.y, R, { soon, big: true, nOut: many ? 8 : 12, nMid: many ? 4 : 8, hideLab: many, layer });
        c.tip = t; sc.subj.set(t.it.id, c);
      });
      // Home camera: the real crown bounds, every cluster and the ground, + 24 units (+ 6 sway margin), at the stage aspect.
      const cb = cr.box, pts = [[cb[0], cb[1]], [cb[2], cb[3]], [BASE.x - 150, BASE.y + 16], [BASE.x + 150, BASE.y + 16]];
      lay.tips.forEach((t) => pts.push([t.x - R * 1.3, t.y - R * 1.3], [t.x + R * 1.3, t.y + R * 1.3]));
      if (!this.ctl.opts.static) pts.push([cr.cx, cb[1] - 44]); // room for the stream chips
      sc.home = this.fit(pts, 30, true);
      const plate = el("g", { class: "lp-plate" }, g);
      el("circle", { cx: BASE.x, cy: BASE.y - 1, r: 19, class: "qm-plate" }, plate);
      el("image", { href: "assets/v3/brand/merit-mark.svg", x: BASE.x - 14, y: BASE.y - 16, width: 28, height: 28 }, plate);
      g.appendChild(layer);
      Object.assign(sc, { trunk, plate, labs: layer });
      this.place([...sc.subj.values()].map((c) => c.lab), sc.home.w / W);
      return sc;
    }
    teardown() {
      this.stopCoin(true);
      this.tw.forEach((t) => t.kill()); this.tw = [];
      if (this.scene) this.scene.g.remove();
      this.scene = this.sub = null;
    }
    async rebuild(level, mode) {
      if (this.scene && mode === "swap" && !reduced()) await new Promise((res) => gsap.to(this.scene.g, { opacity: 0, duration: 0.25, onComplete: res }));
      this.teardown();
      const sc = (this.scene = this.build(level)), cs = [...sc.subj.values()];
      this.cam_(sc.home, 0);
      if (this.still || reduced()) { cs.forEach((c) => this.sway(c)); this.live(); return; }
      // Grow on load, about 1.8 s: trunk up from the base, branches by depth, crown facets pop centre-out, then the subject clusters.
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } }); this.T(tl);
      gsap.set(sc.trunk, { scaleY: 0, svgOrigin: BASE.x + " " + BASE.y });
      tl.to(sc.trunk, { scaleY: 1, duration: 0.5 }, 0);
      sc.br.forEach((b) => { gsap.set(b, { scale: 0, svgOrigin: b._seg.p.x + " " + b._seg.p.y }); tl.to(b, { scale: 1, duration: 0.34 }, 0.3 + (b._seg.depth - 1) * 0.1); });
      gsap.set(sc.plate, { opacity: 0 }); tl.to(sc.plate, { opacity: 1, duration: 0.3 }, 0.1);
      this.popIn(tl, { fs: sc.crownF }, 0.8, 0.006);
      cs.forEach((c) => { gsap.set(c.lab, { opacity: 0 }); const at = 1.3 + hash(c.item.id + "pop") * 0.1; this.popIn(tl, c, at); tl.to(c.lab, { opacity: 1, duration: 0.25 }, at + 0.3); });
      cs.forEach((c) => this.sway(c));
      await this.done(tl);
      this.live();
      this.startCoin();
    }
    live(on) { // only clusters of the visible level can take focus
      const act = on == null ? !this.sub : on;
      this.scene.subj.forEach((c) => { c.node.style.pointerEvents = act ? "" : "none"; if (c.node.hasAttribute("role")) c.node.setAttribute("tabindex", act ? "0" : "-1"); });
    }
    async render(level, from, mode) {
      if (level.kind === "root") return this.scene && mode === "out" ? this.collapse() : this.rebuild(level, mode);
      if (level.kind === "subject") return this.sub && mode === "out" ? this.pick(null) : this.expand(level);
      return this.pick(level);
    }
    async expand(level) {
      const sc = this.scene, c = sc.subj.get(level.id), items = level.items;
      this.live(false);
      sc.subj.forEach((o) => { if (o !== c) { this.fade(o.node, 0.1); this.fade(o.lab, 0); } });
      sc.br.concat([sc.trunk]).forEach((b) => this.fade(b, 0.18));
      this.fade(sc.plate, 0.1); this.fade(sc.crown, 0);
      if (!items.length) { this.fade(c.lab, 1); return this.cam_(this.fit([[c.x - c.r * 1.6, c.y - c.r * 1.6], [c.x + c.r * 1.6, c.y + c.r * 1.6]], 20), 0.7); }
      const n = items.length, dir = Math.atan2(c.tip.y - c.tip.chain[c.tip.chain.length - 1].p.y, c.tip.x - c.tip.chain[c.tip.chain.length - 1].p.x);
      const Rmax = clamp(80 + n * 17, 120, 250), r = clamp(36 - n * 0.7, 21, 31);
      const lay = G.layout(items, level.id, {
        o: { x: c.x, y: c.y }, dir: clamp(dir, -Math.PI * 0.8, -Math.PI * 0.2), stub: 30, len: 62, d0: 3, spread: Math.min(2.6, 1.7 + n * 0.08), D: 104,
        scale: (pts) => { let m = 1; pts.forEach((q) => { m = Math.max(m, Math.hypot(q.x - c.x, q.y - c.y)); }); return clamp(Rmax / m, 0.6, 1.5); },
      });
      const g = el("g", { class: "lp-sub" }, sc.g), layer = el("g", { class: "lp-labs", "aria-hidden": "true" });
      const brs = this.branches(g, lay.segs, BARK, true), tops = lay.tips.map((t) => this.cluster(g, t.it, t.x, t.y, r, { big: false, nOut: 8, nMid: 4, layer }));
      g.appendChild(layer);
      this.sub = { g, topics: tops };
      const pts = lay.tips.map((t) => [t.x, t.y]).concat([[c.x, c.y]]);
      const box = this.fit(pts.concat(lay.tips.map((t) => [t.x, t.y + r + 40]), lay.tips.map((t) => [t.x, t.y - r])), 30);
      this.place(tops.map((t) => t.lab), box.w / W);
      const tl = gsap.timeline({ defaults: { ease: "power2.out" } }); this.T(tl);
      tl.to(c.pop, { opacity: 0, scale: 0.4, svgOrigin: c.x + " " + c.y, duration: 0.45 }, 0.1);
      gsap.set(c.lab, { opacity: 1 }); tl.to(c.lab, { opacity: 0, duration: 0.2 }, 0);
      brs.forEach((b) => { gsap.set(b, { scale: 0, svgOrigin: b._seg.p.x + " " + b._seg.p.y }); tl.to(b, { scale: 1, duration: 0.3 }, 0.3 + b._seg.depth * 0.08); });
      tops.forEach((t, i) => { gsap.set(t.lab, { opacity: 0 }); this.popIn(tl, t, 0.65 + i * 0.03); tl.to(t.lab, { opacity: 1, duration: 0.25 }, 0.95 + i * 0.03); this.sway(t); });
      if (reduced()) tl.progress(1);
      await Promise.all([this.cam_(box, 0.8), reduced() ? 0 : this.done(tl)]);
    }
    fade(e, o) { if (reduced()) e.style.opacity = o; else this.T(gsap.to(e, { opacity: o, duration: 0.4 })); }
    // Highlight one topic cluster (or none) in the opened subject.
    async pick(level) {
      if (!this.sub) return;
      this.sub.topics.forEach((t) => {
        const on = !level || t.item.id === level.id;
        t.node.classList.toggle("sel", !!level && on);
        this.fade(t.node, on ? 1 : 0.3); this.fade(t.lab, on ? 1 : 0.3);
      });
    }
    async collapse() {
      const sc = this.scene, sub = this.sub;
      this.sub = null;
      if (sub) { this.fade(sub.g, 0); setTimeout(() => sub.g.remove(), reduced() ? 0 : 420); sub.topics.forEach((t) => t.node.setAttribute("tabindex", "-1")); }
      sc.subj.forEach((c) => { this.fade(c.node, 1); this.fade(c.lab, 1); gsap.set(c.pop, { clearProps: "opacity,transform" }); });
      sc.br.concat([sc.trunk, sc.plate, sc.crown]).forEach((b) => this.fade(b, 1));
      await this.cam_(sc.home, 0.8);
      this.live(true);
    }

    /* ---- idle coin tour: a coin rides branch to branch to a Physics tip every ~6 s, then pops +10; dies at first interaction */
    startCoin() {
      if (reduced() || this.coinDead) return;
      const sc = this.scene, tip = [...sc.subj.values()].find((c) => c.item.label === "Physics" || c.item.ref.tc);
      if (!tip) return;
      const chain = tip.tip.chain;
      const pos = (t) => {
        const f = clamp(t, 0, 0.9999) * chain.length, s = chain[Math.floor(f)], u = f % 1, m = 1 - u;
        return [m * m * s.p.x + 2 * m * u * s.c.x + u * u * s.end.x, m * m * s.p.y + 2 * m * u * s.c.y + u * u * s.end.y];
      };
      const coin = el("g", { class: "lp-coin", opacity: 0 }, sc.coin), txt = el("text", { class: "lp-plus", "text-anchor": "middle", opacity: 0, text: "+10" }, sc.g);
      el("circle", { r: 11 }, coin); el("circle", { r: 6.5, class: "in" }, coin);
      const run = () => {
        if (this.coinDead || this.ctl.path.length || this.ctl.busy) { this.coinCall = gsap.delayedCall(6, run); return; }
        const o = { t: 0 };
        this.coinTw = gsap.timeline({ onComplete: () => { this.coinCall = gsap.delayedCall(5, run); } })
          .set(coin, { opacity: 1 })
          .to(o, { t: 1, duration: 1.7, ease: "sine.inOut", onUpdate: () => { const p = pos(o.t); coin.setAttribute("transform", "translate(" + p[0].toFixed(1) + " " + p[1].toFixed(1) + ")"); } })
          .set(coin, { opacity: 0 })
          .fromTo(tip.pop, { scale: 1 }, { scale: 1.07, svgOrigin: tip.x + " " + tip.y, duration: 0.18, yoyo: true, repeat: 1, ease: "sine.inOut" }, "<")
          .set(txt, { attr: { x: tip.x, y: tip.y - tip.r - 6 } }, "<")
          .fromTo(txt, { opacity: 1, y: 0 }, { opacity: 0, y: -26, duration: 1, ease: "power1.out" }, "<");
      };
      this.coinCall = gsap.delayedCall(2.2, run);
    }
    stopCoin(soft) {
      if (!soft) this.coinDead = true;
      if (this.coinCall) this.coinCall.kill();
      if (this.coinTw) { this.coinTw.kill(); this.coinTw = null; }
      if (this.scene) this.scene.g.querySelectorAll(".lp-coin,.lp-plus").forEach((e) => e.setAttribute("opacity", 0));
    }
  }

  const boot = () => document.querySelectorAll('[data-qm="lowpoly"]').forEach((h) => { h.classList.add("lp"); new Q.Explorer(h, LowPoly, { static: h.hasAttribute("data-static") }); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})(typeof window !== "undefined" ? window : globalThis);
