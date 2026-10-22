/* Quilt Map prototypes for the web wireframes board (landing hero concepts).
   Core + controller shared by three renderers: tree (qm-tree.js), net and orbit (here).
   Data: window.QM_DATA (qm-data.js), a trimmed /public/explore snapshot.
   Everything is deterministic: positions come from FNV-1a hashes of node ids. */
(function () {
  "use strict";
  const NS = "http://www.w3.org/2000/svg";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)");

  function el(tag, attrs, parent) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs || {}) {
      if (k === "text") e.textContent = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    if (parent) parent.appendChild(e);
    return e;
  }
  function hash(str) {
    let h = 0x811c9dc5;
    for (let i = 0; i < str.length; i++) { h ^= str.charCodeAt(i); h = Math.imul(h, 0x01000193); }
    // murmur3 fmix32: spread small input differences across all bits
    h ^= h >>> 16; h = Math.imul(h, 0x85ebca6b); h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35); h ^= h >>> 16;
    return (h >>> 0) / 4294967295;
  }
  const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
  const lerp = (a, b, t) => a + (b - a) * t;
  function tween(ms, fn) {
    if (reduce.matches || ms <= 0) { fn(1); return Promise.resolve(); }
    return new Promise((res) => {
      const t0 = performance.now();
      function f(now) {
        const t = Math.min(1, (now - t0) / ms);
        fn(ease(t));
        if (t < 1) requestAnimationFrame(f); else res();
      }
      requestAnimationFrame(f);
    });
  }
  const TOPIC_TILES = ["kinetics", "waves", "thermal", "current", "magnetism", "cells", "circulation", "leaf", "plants"];
  const tileUrl = (n) => "assets/v3/patchwork-demo/" + n + "-tile.svg";
  const clip = (s, n) => (s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s);
  const plural = (n, one, many) => n + " " + (n === 1 ? one : many);
  // Up to two lines of at most n chars, breaking on spaces; the second line is clipped.
  function wrap(s, n) {
    if (s.length <= n) return [s];
    const words = s.split(" ");
    let a = "";
    while (words.length && (a + " " + words[0]).trim().length <= n) a = (a + " " + words.shift()).trim();
    if (!a) return [clip(s, n)];
    return [a, clip(words.join(" "), n + 2)];
  }

  /* ---------------------------------------------------------- model */
  // A level is {kind, id, label, color, tile, items:[{id,label,color,tile,leaf,meta,ref}]}
  function rootLevel(streamCode) {
    const D = window.QM_DATA;
    const st = D.streams.find((s) => s.code === streamCode) || D.streams[0];
    return {
      kind: "root", id: "merit:" + st.code, label: "Merit", stream: st.title,
      items: st.ids.map((id) => {
        const s = D.subjects[id];
        return { id, label: s.t, color: s.c, tile: s.tile, ref: s, meta: s.tc ? plural(s.tc, "topic", "topics") : "Coming soon" };
      }),
    };
  }
  function subjectLevel(s) {
    const topics = s.topics || [];
    return {
      kind: "subject", id: s.id, label: s.t, color: s.c, tile: s.tile, ref: s,
      items: topics.map((t, i) => ({
        id: t.id, label: t.t, ref: t, subject: s,
        color: "color-mix(in srgb, " + s.c + " " + (70 + Math.round(hash(t.id) * 30)) + "%, var(--merit-bg-app))",
        tile: TOPIC_TILES[Math.floor(hash(t.id) * TOPIC_TILES.length)],
        meta: plural(t.sc, "subtopic", "subtopics"),
      })),
    };
  }
  function topicLevel(t, s, tile) {
    return {
      kind: "topic", id: t.id, label: t.t, color: s.c, tile, ref: t, subject: s,
      items: (t.subs || []).map((name, i) => ({ id: t.id + ":" + i, label: name, leaf: true, color: s.c })),
    };
  }

  /* ---------------------------------------------------------- controller */
  class Explorer {
    constructor(host, Renderer, opts) {
      this.host = host; this.opts = opts || {};
      this.stream = host.dataset.stream || "al-science";
      this.path = [];
      this.busy = false;
      host.innerHTML = "";
      host.classList.add("qm");
      if (!this.opts.static) {
        this.top = document.createElement("div"); this.top.className = "qm-top"; host.appendChild(this.top);
        this.crumb = document.createElement("nav"); this.crumb.className = "qm-crumb"; this.crumb.setAttribute("aria-label", "Where you are"); host.appendChild(this.crumb);
        this.panel = document.createElement("div"); this.panel.className = "qm-panel"; this.panel.hidden = true; host.appendChild(this.panel);
        this.live = document.createElement("p"); this.live.className = "qm-live"; this.live.setAttribute("aria-live", "polite"); host.appendChild(this.live);
        this.renderChips();
        host.addEventListener("keydown", (e) => { if (e.key === "Escape" && this.path.length) { e.preventDefault(); this.up(); } });
      }
      this.svg = el("svg", { class: "qm-svg", viewBox: "0 0 1000 600", role: "group", "aria-label": "Merit subject map" }, host);
      this.r = new Renderer(this.svg, this);
      this.show(rootLevel(this.stream), null, "none");
    }
    level() { return this.path.length ? this.path[this.path.length - 1] : rootLevel(this.stream); }
    renderChips() {
      this.top.innerHTML = "";
      for (const st of window.QM_DATA.streams) {
        const b = document.createElement("button");
        b.type = "button"; b.className = "chip" + (st.code === this.stream ? " on" : "");
        b.textContent = "A/L " + st.title; b.setAttribute("aria-pressed", st.code === this.stream);
        b.addEventListener("click", () => { if (this.busy || st.code === this.stream) return; this.stream = st.code; this.path = []; this.renderChips(); this.show(rootLevel(st.code), null, "swap"); });
        this.top.appendChild(b);
      }
    }
    renderCrumb() {
      const parts = [{ label: "Merit", depth: 0 }].concat(this.path.map((l, i) => ({ label: clip(l.label, 26), depth: i + 1 })));
      this.crumb.innerHTML = "";
      parts.forEach((p, i) => {
        if (i) { const s = document.createElement("span"); s.textContent = "›"; s.setAttribute("aria-hidden", "true"); this.crumb.appendChild(s); }
        const b = document.createElement("button"); b.type = "button"; b.textContent = p.label;
        if (i === parts.length - 1) b.setAttribute("aria-current", "location");
        else b.addEventListener("click", () => this.up(parts.length - 1 - i));
        this.crumb.appendChild(b);
      });
    }
    renderPanel(level) {
      if (!this.panel) return;
      const p = this.panel; p.innerHTML = "";
      if (level.kind === "root") { p.hidden = true; return; }
      p.hidden = false;
      const s = level.kind === "subject" ? level.ref : level.subject;
      const h = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; e.textContent = txt; p.appendChild(e); return e; };
      if (level.kind === "subject") {
        h("span", "ey", "A/L · " + this.streamTitle());
        h("b", "h-md", s.t);
        h("span", "sm t2", s.tc ? plural(s.tc, "topic", "topics") + " · " + plural(s.sc, "subtopic", "subtopics") + " · " + plural(s.q, "question", "questions") : "Topics are on the way for this subject.");
        const b = h("button", "btn s full", "Start free with " + clip(s.t, 22)); b.type = "button";
      } else {
        const t = level.ref;
        h("span", "ey", clip(s.t, 28));
        h("b", "h-md", t.t);
        h("span", "sm t2", plural(t.sc, "subtopic", "subtopics") + " · " + plural(t.q, "question", "questions"));
        if (t.x != null) h("span", "sm qm-share", "About " + t.x + "% of Paper I marks");
        const b = h("button", "btn s full", "Start practising " + clip(t.t, 24)); b.type = "button";
        h("span", "xs t3", "Free. Opens sign-up with " + s.t + " picked.");
      }
    }
    streamTitle() { return (window.QM_DATA.streams.find((s) => s.code === this.stream) || {}).title || ""; }
    announce(level) {
      if (!this.live) return;
      this.live.textContent = level.kind === "root" ? level.stream + " stream, " + plural(level.items.length, "subject", "subjects")
        : level.label + ", " + plural(level.items.length, level.kind === "subject" ? "topic" : "subtopic", level.kind === "subject" ? "topics" : "subtopics");
    }
    async show(level, from, mode) {
      this.busy = true;
      await this.r.render(level, from, mode);
      this.busy = false;
      if (this.crumb) { this.renderCrumb(); this.renderPanel(level); this.announce(level); }
    }
    open(item) {
      if (this.busy || this.opts.static) return;
      const cur = this.level();
      if (item.more) { this.showMore(cur); return; }
      let next = null;
      if (cur.kind === "root") next = subjectLevel(item.ref);
      else if (cur.kind === "subject") next = topicLevel(item.ref, item.subject, item.tile);
      if (!next) return; // subtopic beads are the last level
      this.path.push(next);
      this.show(next, item, "in");
    }
    showMore(level) {
      const p = this.panel; p.innerHTML = ""; p.hidden = false;
      const b = document.createElement("b"); b.className = "h-sm"; b.textContent = "All " + level.items.length + (level.kind === "root" ? " subjects" : level.kind === "subject" ? " topics" : " subtopics"); p.appendChild(b);
      const ul = document.createElement("ul"); ul.className = "qm-list";
      level.items.forEach((it) => { const li = document.createElement("li"); li.textContent = it.label; ul.appendChild(li); });
      p.appendChild(ul);
    }
    up(n) {
      if (this.busy || !this.path.length) return;
      const leaving = this.path[this.path.length - 1];
      this.path.splice(this.path.length - (n || 1));
      this.show(this.level(), leaving, "out");
    }
  }

  /* ---------------------------------------------------------- shared node drawing */
  function polygon(cx, cy, r, sides, rot) {
    const pts = [];
    for (let i = 0; i < sides; i++) {
      const a = (rot || -Math.PI / 2) + (i * 2 * Math.PI) / sides;
      pts.push((cx + r * Math.cos(a)).toFixed(1) + "," + (cy + r * Math.sin(a)).toFixed(1));
    }
    return pts.join(" ");
  }
  // A clickable node: tile image (or bead for leaves) + label. Returns the <g>.
  function node(parent, item, x, y, size, ctl, opts) {
    const o = opts || {};
    const g = el("g", { class: "qm-node" + (item.leaf ? " leaf" : ""), transform: "translate(" + x + " " + y + ")" }, parent);
    if (!item.leaf && !o.decor) {
      g.setAttribute("tabindex", "0"); g.setAttribute("role", "button");
      g.setAttribute("aria-label", item.label + (item.meta ? ", " + item.meta : ""));
      const go = () => ctl.open(item);
      g.addEventListener("click", go);
      g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
    }
    const inner = el("g", { class: "qm-pop" }, g);
    if (item.leaf) {
      el("polygon", { points: polygon(0, 0, 9, 6, 0), class: "qm-bead", style: "fill:" + item.color }, inner);
    } else {
      el("rect", { x: -size / 2 - 4, y: -size / 2 - 4, width: size + 8, height: size + 8, rx: size * 0.18, class: "qm-ring" }, inner);
      el("image", { href: tileUrl(item.tile), x: -size / 2, y: -size / 2, width: size, height: size, class: "qm-tile" }, inner);
    }
    if (!o.nolabel) {
      const ly = o.above ? (item.leaf ? -16 : -size / 2 - 12) : item.leaf ? 22 : size / 2 + 18;
      const anchor = o.anchor || "middle";
      const lx = o.anchor === "start" ? 16 : o.anchor === "end" ? -16 : 0;
      const lines = wrap(item.label, item.leaf ? 18 : 14);
      const tx = el("text", { x: item.leaf ? lx : 0, y: item.leaf && o.anchor ? 4 : ly, class: "qm-lab" + (item.leaf ? " sm" : ""), "text-anchor": item.leaf ? anchor : "middle" }, inner);
      lines.forEach((ln, i) => el("tspan", { x: item.leaf ? lx : 0, dy: i ? "1.15em" : o.above ? -(lines.length - 1) * 1.15 + "em" : 0, text: ln }, tx));
      el("title", { text: item.label }, g);
      if (item.meta && !item.leaf && !o.nometa) el("text", { x: 0, y: ly + 15 * lines.length, class: "qm-meta", "text-anchor": "middle", text: item.meta }, inner);
    }
    return g;
  }
  function hub(parent, level, x, y, size) {
    const g = el("g", { class: "qm-hub", transform: "translate(" + x + " " + y + ")" }, parent);
    const sides = level.kind === "root" ? 6 : level.kind === "subject" ? 4 : 5; // DS D16: plate sides name the level
    el("polygon", { points: polygon(0, 0, size * 0.78, sides, sides === 4 ? -Math.PI / 4 : -Math.PI / 2), class: "qm-plate" }, g);
    if (level.kind === "root") el("image", { href: "assets/v3/brand/merit-mark.svg", x: -size * 0.42, y: -size * 0.42, width: size * 0.84, height: size * 0.84 }, g);
    else el("image", { href: tileUrl(level.tile), x: -size * 0.4, y: -size * 0.4, width: size * 0.8, height: size * 0.8, class: "qm-tile" }, g);
    return g;
  }

  /* ---------------------------------------------------------- net + orbit renderer */
  class NetRenderer {
    constructor(svg, ctl) { this.svg = svg; this.ctl = ctl; this.mode = ctl.opts.mode || "net"; this.scene = null; this.C = { x: 500, y: 300 }; }
    layout(level) {
      const items = level.items.slice();
      let more = 0;
      const cap = level.kind === "topic" ? 12 : 11;
      if (items.length > cap) { more = items.length - (cap - 1); items.length = cap - 1; items.push({ id: level.id + ":more", label: "+" + more + " more", more: true, tile: "languages", meta: "" }); }
      const n = items.length, C = this.C, out = [];
      items.forEach((it, i) => {
        const h = hash(it.id + level.id);
        let a, rx, ry;
        if (this.mode === "orbit") { a = -Math.PI / 2 + (i * 2 * Math.PI) / n; rx = 330; ry = 215; }
        else {
          a = -Math.PI / 2 + (i * 2 * Math.PI) / n + (h - 0.5) * 0.35;
          const ring = i % 2 ? 1.0 : 0.78;
          rx = (300 + h * 70) * ring + 40; ry = (205 + h * 30) * ring + 10;
        }
        out.push({ it, x: C.x + rx * Math.cos(a), y: Math.max(80, Math.min(505, C.y + ry * Math.sin(a))), a });
      });
      // Keep nodes apart and out of the info panel corner (bottom right) below the root level.
      const D = level.kind === "topic" ? 104 : 128;
      for (let k = 0; k < 60; k++) {
        let moved = false;
        for (let i = 0; i < out.length; i++) for (let j = i + 1; j < out.length; j++) {
          const p = out[i], q2 = out[j], dx = q2.x - p.x, dy = q2.y - p.y, d = Math.hypot(dx, dy) || 0.01;
          if (d < D) { const m = (D - d) / 2; p.x -= (dx / d) * m; p.y -= (dy / d) * m; q2.x += (dx / d) * m; q2.y += (dy / d) * m; moved = true; }
        }
        for (const p of out) {
          p.x = Math.max(80, Math.min(920, p.x)); p.y = Math.max(80, Math.min(505, p.y));
          if (Math.hypot(p.x - C.x, (p.y - C.y) * 1.3) < 150) { const a = Math.atan2(p.y - C.y, p.x - C.x); p.x = C.x + 160 * Math.cos(a); p.y = C.y + 125 * Math.sin(a); }
          if (level.kind !== "root" && !this.ctl.opts.static && p.x > 700 && p.y > 400) p.y = 400;
        }
        if (!moved) break;
      }
      out.forEach((p) => (p.a = Math.atan2(p.y - C.y, p.x - C.x)));
      return out;
    }
    wire(p, size) {
      const C = this.C, ca = Math.cos(p.a), sa = Math.sin(p.a);
      const E = { x: C.x + 56 * ca, y: C.y + 54 * sa };
      const stop = (q, r) => { const dx = p.x - q.x, dy = p.y - q.y, d = Math.hypot(dx, dy) || 1; return { x: p.x - (dx / d) * r, y: p.y - (dy / d) * r }; };
      if (this.mode === "orbit") { const e = stop(E, size * 0.62); return { d: "M" + E.x + " " + E.y + "L" + e.x + " " + e.y, solder: null }; }
      const P1 = { x: C.x + 112 * ca, y: C.y + 100 * sa };
      const dx = p.x - P1.x, dy = p.y - P1.y;
      let P2;
      if (Math.abs(dx) >= Math.abs(dy)) P2 = { x: p.x - Math.sign(dx) * Math.abs(dy), y: P1.y };
      else P2 = { x: P1.x, y: p.y - Math.sign(dy) * Math.abs(dx) };
      const e = stop(P2, size * 0.62);
      return { d: "M" + E.x.toFixed(1) + " " + E.y.toFixed(1) + "L" + P1.x.toFixed(1) + " " + P1.y.toFixed(1) + "L" + P2.x.toFixed(1) + " " + P2.y.toFixed(1) + "L" + e.x.toFixed(1) + " " + e.y.toFixed(1), solder: P1 };
    }
    decor(g, pts, level) {
      if (this.mode === "orbit" || pts.length < 3) return;
      const C = this.C;
      for (let i = 0; i < pts.length; i++) {
        const a0 = pts[i].a, a1 = i + 1 < pts.length ? pts[i + 1].a : pts[0].a + 2 * Math.PI;
        const h = hash(level.id + "deco" + i);
        if (h < (pts.length > 7 ? 0.6 : 0.3)) continue;
        const a = (a0 + a1) / 2, r0 = 72, r1 = 128 + h * 60;
        const x0 = C.x + r0 * 1.2 * Math.cos(a), y0 = C.y + r0 * Math.sin(a), x1 = C.x + r1 * 1.35 * Math.cos(a), y1 = C.y + r1 * Math.sin(a);
        const dg = el("g", { class: "qm-deco" }, g);
        const xm = C.x + r1 * 0.8 * 1.2 * Math.cos(a), ym = C.y + r1 * 0.8 * Math.sin(a);
        el("path", { d: "M" + x0 + " " + y0 + "L" + xm + " " + ym + "L" + x1 + " " + ym, pathLength: 1, class: "qm-draw" }, dg);
        const kind = Math.floor(h * 4);
        const yE = ym, s = Math.cos(a) < 0 ? -1 : 1, xe = x1 + s * 9;
        if (kind === 0) el("circle", { cx: xe, cy: yE, r: 9 }, dg);
        else if (kind === 1) el("polygon", { points: polygon(xe, yE, 10, 3, -Math.PI / 2) }, dg);
        else if (kind === 2) el("rect", { x: xe - 8, y: yE - 8, width: 16, height: 16, rx: 3 }, dg);
        else { el("path", { d: "M" + (x1 + s * 8) + " " + (yE - 5) + "h" + s * 30 + "M" + (x1 + s * 8) + " " + (yE + 5) + "h" + s * 18 }, dg); }
      }
    }
    build(level) {
      const g = el("g", { class: "qm-scene" }, this.svg);
      const size = level.kind === "root" ? 66 : level.kind === "subject" ? 54 : 0;
      const pts = this.layout(level);
      const wires = el("g", {}, g);
      this.decor(wires, pts, level);
      const nodes = [];
      pts.forEach((p) => {
        const w = this.wire(p, p.it.leaf ? 26 : size);
        if (this.mode === "orbit") el("path", { d: w.d, class: "qm-wire dotted" }, wires);
        else el("path", { d: w.d, pathLength: 1, class: "qm-wire qm-draw" }, wires);
        if (w.solder) el("circle", { cx: w.solder.x, cy: w.solder.y, r: 4.5, class: "qm-solder" }, wires);
        const anchor = p.it.leaf ? (Math.cos(p.a) < -0.2 ? "end" : Math.cos(p.a) > 0.2 ? "start" : null) : null;
        const ng = node(g, p.it, p.x, p.y, size, this.ctl, { anchor, nometa: level.kind !== "root" });
        nodes.push({ g: ng, p });
      });
      const hb = hub(g, level, this.C.x, this.C.y, level.kind === "root" ? 92 : 80);
      if (level.kind !== "root" && !this.ctl.opts.static) {
        el("text", { x: this.C.x, y: this.C.y + 62, class: "qm-lab", "text-anchor": "middle", text: clip(level.label, 26) }, g);
      }
      return { g, nodes, hub: hb, pts };
    }
    async render(level, from, mode) {
      const old = this.scene;
      const C = this.C;
      if (old && mode === "in" && from) {
        const hit = old.nodes.find((n) => n.p.it.id === from.id);
        await tween(520, (t) => {
          old.nodes.forEach((n) => {
            if (n === hit) { const x = lerp(n.p.x, C.x, t), y = lerp(n.p.y, C.y, t); n.g.setAttribute("transform", "translate(" + x + " " + y + ") scale(" + lerp(1, 1.45, t) + ")"); }
            else n.g.style.opacity = 1 - t;
          });
          old.g.querySelectorAll(".qm-wire,.qm-deco,.qm-solder,.qm-hub,text:not(.qm-node text)").forEach((e) => (e.style.opacity = 1 - t));
        });
      } else if (old) {
        await tween(mode === "none" ? 0 : 360, (t) => {
          old.g.style.opacity = 1 - t;
          old.g.setAttribute("transform", "translate(" + C.x + " " + C.y + ") scale(" + lerp(1, mode === "out" ? 0.7 : 0.92, t) + ") translate(" + -C.x + " " + -C.y + ")");
        });
      }
      if (old) old.g.remove();
      const sc = (this.scene = this.build(level));
      if (this.ctl.opts.static) return;
      const draws = sc.g.querySelectorAll(".qm-draw");
      draws.forEach((d) => { d.style.strokeDasharray = "1"; d.style.strokeDashoffset = "1"; });
      sc.nodes.forEach((n) => (n.g.style.opacity = 0));
      sc.hub.style.opacity = mode === "in" ? 1 : 0;
      await tween(mode === "none" ? 650 : 700, (t) => {
        sc.hub.style.opacity = Math.max(+sc.hub.style.opacity, Math.min(1, t * 3));
        draws.forEach((d) => (d.style.strokeDashoffset = 1 - Math.min(1, t * 1.6)));
        sc.nodes.forEach((n, i) => {
          const k = Math.max(0, Math.min(1, (t - 0.25 - i * 0.035) / 0.5));
          n.g.style.opacity = k;
          n.g.setAttribute("transform", "translate(" + lerp(C.x, n.p.x, k) + " " + lerp(C.y, n.p.y, k) + ")");
        });
      });
    }
  }

  window.QM = { el, hash, tween, lerp, ease, polygon, node, hub, clip, plural, tileUrl, Explorer, NetRenderer, rootLevel };

  function boot() {
    document.querySelectorAll("[data-qm]").forEach((host) => {
      const kind = host.dataset.qm;
      const st = host.hasAttribute("data-static");
      if (kind === "net") new Explorer(host, NetRenderer, { mode: "net", static: st });
      if (kind === "orbit") new Explorer(host, NetRenderer, { mode: "orbit", static: st });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
