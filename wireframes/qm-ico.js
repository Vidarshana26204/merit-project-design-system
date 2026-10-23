/* Quilt Map concept A, round 12b: icosphere tree on a hill. Projected 3D in SVG (no three.js) + GSAP.
   Trunk and branches are tapered hexagonal prisms, the crown is flat-shaded icospheres (20 faces, about 10 visible).
   A tiny projector (yaw, pitch, perspective, back-face cull, painter's sort, Lambert vs a top-left key light, 5 tones)
   re-projects only when something changed. At most 6 interactive balls per level (+ a "+N more" ball) and 3-5 decorative ones.
   Recursion: a subject ball shatters and a smaller tree of its topics grows from that spot; a topic is the last level.
   Reuses qm.js (Explorer: data, chips, breadcrumb, topic panel, Esc). Mount: [data-qm="ico"] (data-stream, data-wide for 16:9,
   data-static for a still frame). Needs gsap and qm.js first. The pure geometry is exported for node tests. */
(function (root) {
  "use strict";
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const H = 600, B = [410, 538, 0], F = [352, 420, 0], PIV = [330, 250, 0], FOC = 900, AMB = 0.34;
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]], sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k], dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const unit = (v) => mul(v, 1 / (Math.hypot(v[0], v[1], v[2]) || 1)), mean = (P) => mul(P.reduce(add, [0, 0, 0]), 1 / P.length);
  const ry = (v, a) => [v[0] * Math.cos(a) + v[2] * Math.sin(a), v[1], -v[0] * Math.sin(a) + v[2] * Math.cos(a)];
  const rz = (v, a) => [v[0] * Math.cos(a) - v[1] * Math.sin(a), v[0] * Math.sin(a) + v[1] * Math.cos(a), v[2]];
  const LIGHT = unit([-0.5, -0.65, 0.58]); // view space: x right, y down, z toward the viewer; from the top left

  function geometry(hash) {
    const T = (1 + Math.sqrt(5)) / 2;
    const UV = [[-1, T, 0], [1, T, 0], [-1, -T, 0], [1, -T, 0], [0, -1, T], [0, 1, T], [0, -1, -T], [0, 1, -T], [T, 0, -1], [T, 0, 1], [-T, 0, -1], [-T, 0, 1]].map(unit);
    const UF = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]];
    // Faces carry an outward normal (oriented against a reference centre, so winding never matters).
    const face = (P, i, ref) => { const a = P[i[0]]; let n = unit(cross(sub(P[i[1]], a), sub(P[i[2]], a))); if (dot(n, sub(mean(i.map((k) => P[k])), ref)) < 0) n = mul(n, -1); return { i, n }; };
    function ball(c, r, seed) {
      const rot = hash(seed + "rot") * 3.14, pts = UV.map((v, k) => ry(mul(v, r * (0.9 + 0.2 * hash(seed + k))), rot));
      return { kind: "ball", pts, faces: UF.map((f) => face(pts, f, [0, 0, 0])), c: c.slice(), r, spin: 0, mid: [0, 0, 0] };
    }
    // Tapered hexagonal prism along a polyline, with a hex cap at the tip.
    function limb(path, radii, seed) {
      const pts = [], faces = [], rings = [];
      path.forEach((p, k) => {
        const t = unit(sub(path[Math.min(k + 1, path.length - 1)], path[Math.max(k - 1, 0)])), u = unit(cross(t, [0.3, 0.1, 1])), v = cross(t, u);
        const ph = hash(seed + "ph") * 1.05;
        for (let j = 0; j < 6; j++) { const a = ph + (j * Math.PI) / 3; pts.push(add(p, add(mul(u, radii[k] * Math.cos(a)), mul(v, radii[k] * Math.sin(a))))); }
      });
      for (let k = 0; k < path.length - 1; k++) for (let j = 0; j < 6; j++) {
        const i = [k * 6 + j, k * 6 + ((j + 1) % 6), (k + 1) * 6 + ((j + 1) % 6), (k + 1) * 6 + j];
        faces.push(face(pts, i, mul(add(path[k], path[k + 1]), 0.5)));
      }
      const e = path.length - 1; faces.push(face(pts, [e * 6, e * 6 + 1, e * 6 + 2, e * 6 + 3, e * 6 + 4, e * 6 + 5], path[e - 1]));
      return { kind: "limb", pts, faces, c: [0, 0, 0], spin: 0, mid: mean(pts) };
    }
    // Hanging plank, local to its rope anchor A (so it can swing about A).
    function plank(A, w, h, d, drop) {
      const x = w / 2, y0 = drop, y1 = drop + h, z = d / 2;
      const pts = [[-x, y0, -z], [x, y0, -z], [x, y1, -z], [-x, y1, -z], [-x, y0, z], [x, y0, z], [x, y1, z], [-x, y1, z]];
      const fs = [[4, 5, 6, 7], [1, 0, 3, 2], [0, 4, 7, 3], [5, 1, 2, 6], [0, 1, 5, 4], [7, 6, 2, 3]];
      return { kind: "plank", pts, faces: fs.map((f) => face(pts, f, [0, (y0 + y1) / 2, 0])), c: A.slice(), spin: 0, rz: 0, mid: [0, 80, 0], w, h, dz: z, drop };
    }
    const camera = (yaw, pitch) => {
      const cy = Math.cos(yaw), sy = Math.sin(yaw), cp = Math.cos(pitch), sp = Math.sin(pitch);
      const rot = (v) => { const x = v[0] * cy + v[2] * sy, z0 = -v[0] * sy + v[2] * cy; return [x, v[1] * cp - z0 * sp, v[1] * sp + z0 * cp]; };
      return { rot, view: (p) => rot(sub(p, PIV)), scr: (q) => { const s = FOC / (FOC - q[2]); return [PIV[0] + q[0] * s, PIV[1] + q[1] * s]; } };
    };
    const local = (o, p) => { let q = p; if (o.spin) q = ry(q, o.spin); if (o.rz) q = rz(q, o.rz); return q; };
    // Project one object: cull back faces, shade (Lambert, 5 tones), sort far to near. Also its screen centre and radius.
    function project(o, cam) {
      const Q = o.pts.map((p) => cam.view(add(local(o, p), o.c))), S = Q.map(cam.scr), out = [];
      o.faces.forEach((f, idx) => {
        const qc = mean(f.i.map((k) => Q[k])), n = cam.rot(local(o, f.n));
        if (dot(n, [-qc[0], -qc[1], FOC - qc[2]]) <= 0) return;
        out.push({ idx, pts: f.i.map((k) => S[k]), z: qc[2], tone: Math.min(4, Math.floor(Math.max(0, dot(n, LIGHT)) * 5)) });
      });
      out.sort((a, b) => a.z - b.z);
      const qm = cam.view(add(local(o, o.mid), o.c));
      return { faces: out, z: qm[2], c: cam.scr(qm), sr: o.r ? o.r * (FOC / (FOC - qm[2])) : 0 };
    }
    // At most 6 interactive items (topics by exam share, subjects in data order) and a "+N more" item.
    function rank(items, topic, id) {
      const a = items.slice();
      if (topic) a.sort((x, y) => ((y.ref && y.ref.x) || 0) - ((x.ref && x.ref.x) || 0));
      const vis = a.slice(0, 6);
      if (a.length > 6) vis.push({ id: id + ":more", more: true, label: "+" + (a.length - 6) + " more", meta: "", tile: "languages" });
      return vis;
    }
    // Crown slots [x, y, z, r], filled in this order so a short list still makes one connected mass (design space 640 x 600).
    const SLOT = [[395, 160, 10, 94], [275, 146, -10, 96], [372, 252, 45, 96], [160, 190, 15, 92], [505, 218, 25, 90], [245, 245, 20, 92]];
    const MORE = [515, 112, -5, 60], DECO = [[255, 175, -80, 72], [440, 205, -85, 78], [330, 205, -90, 82], [560, 170, -70, 58], [205, 262, -70, 60]];
    // Deterministic tree: a leaning trunk forking into 3-4 branches into a dense overlapping crown (6 balls + "+N more" + 3-5 decorative),
    // and a long lower-left branch that carries the sign into open sky.
    function layout(vis, id) {
      const j = (k, a) => (hash(id + k) - 0.5) * a, balls = [];
      vis.forEach((it, i) => {
        const sl = it.more ? MORE : SLOT[i];
        balls.push({ item: it, c: [sl[0] + j("bx" + i, 8), sl[1] + j("by" + i, 8), sl[2]], r: sl[3] + (it.more ? 0 : hash(id + "r" + i) * 6), hue: Math.floor(hash(id + "h" + i) * 5) });
      });
      const nd = vis.length >= 5 ? 5 : vis.length >= 3 ? 4 : 3, deco = DECO.slice(0, nd).map((d, k) => ({ item: null, c: [d[0] + j("dx" + k, 12), d[1] + j("dy" + k, 12), d[2]], r: d[3] + hash(id + "dr" + k) * 8, hue: Math.floor(hash(id + "dh" + k) * 5) }));
      const limbs = [{ path: [B, [B[0] - 16, 480, 10], F], radii: [28, 21, 15] }];
      const near = balls.filter((b) => !b.item.more).sort((a, b) => a.c[0] - b.c[0]), pick = near.length <= 4 ? near : [0, 1, 2, 3].map((k) => near[Math.round((k * (near.length - 1)) / 3)]);
      const tips = pick.map((b) => add(b.c, [0, b.r * 0.35, 0]));
      tips.forEach((t, k) => limbs.push({ path: [F, add(mul(add(F, t), 0.5), [j("k" + k, 14), 0, j("q" + k, 14)]), t], radii: [13, 9, 6] }));
      const S = add(F, [-257, -70, 50]), mid = add(F, [-128, -34, 30]), at = (t) => (t < 0.5 ? add(F, mul(sub(mid, F), t * 2)) : add(mid, mul(sub(S, mid), (t - 0.5) * 2)));
      limbs.push({ path: [F, mid, S], radii: [12, 8, 5] });
      const l = [at(0.52), at(0.89)]; // about one plank width apart, so the ropes hang parallel
      return { limbs, balls, deco, sign: { a: mul(add(l[0], l[1]), 0.5), l }, tips };
    }
    return { ball, limb, plank, camera, project, rank, layout };
  }
  const API = { geometry, LIGHT };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  if (typeof window === "undefined") return;
  root.QMIco = API;

  /* ------------------------------------------------------------ renderer */
  const Q = root.QM, gsap = root.gsap;
  if (!Q || !gsap) { console.warn("qm-ico: needs QM and gsap"); return; }
  const { el, hash } = Q, G = geometry(hash);
  const reduced = () => matchMedia("(prefers-reduced-motion: reduce)").matches;
  const SHORT = { "Information & Communication Technology": "ICT", "Agricultural Science": "Agri Science", "Combined Mathematics": "Combined Maths", "Logic & Scientific Method": "Logic & Method", "Communication & Media Studies": "Media Studies", "Greek & Roman Civilization": "Greek & Roman" };
  const short = (s) => SHORT[s] || s.replace(/^Drama & Theatre/, "Drama").replace(/^History of SL & (.*)$/, "SL & $1 History").replace("Technology", "Tech").replace("Civilization", "Civ.");
  const lines = (s) => { const n = s.length > 40 ? Math.ceil(s.length / 3) + 1 : s.length <= 12 ? 12 : Math.ceil(s.length / 2) + 1, o = []; s.split(" ").forEach((w) => { const l = o[o.length - 1]; if (l != null && (l + " " + w).length <= n) o[o.length - 1] = l + " " + w; else o.push(w); }); return o; };
  const transl = (o) => "translate(" + o.ox + " " + o.oy + ") scale(" + o.s + ")";

  class Ico {
    constructor(svg, ctl) {
      this.svg = svg; this.ctl = ctl; this.W = ctl.host.hasAttribute("data-wide") ? 1067 : 640; this.DX = this.W - 640;
      this.still = ctl.opts.static; this.yaw = 0; this.pitch = 0; this.dirty = true; this.root = this.child = this.sel = null;
      this.cam = { x: 0, y: 0, w: this.W, h: H }; this.view_();
      svg.setAttribute("aria-label", "Merit subject tree");
      const slot = ctl.top && ctl.host.dataset.chipsIn && document.querySelector(ctl.host.dataset.chipsIn);
      if (slot) { slot.appendChild(ctl.top); ctl.top.classList.add("moved"); } // stream chips live in the hero copy column, still wired to the tree
      if (!this.still && !reduced()) {
        const host = ctl.host;
        host.addEventListener("pointermove", (e) => { const r = host.getBoundingClientRect(); this.parallax(((e.clientX - r.left) / r.width) * 2 - 1, ((e.clientY - r.top) / r.height) * 2 - 1); });
        host.addEventListener("pointerleave", () => this.parallax(0, 0));
        gsap.ticker.add(() => { if (this.dirty) { this.dirty = false; [this.root, this.child].forEach((sc) => sc && sc.live && this.draw(sc)); } });
      }
    }
    parallax(nx, ny) { gsap.to(this, { yaw: nx * 6 * Math.PI / 180, pitch: ny * 3 * Math.PI / 180, duration: 0.9, ease: "power2.out", overwrite: true, onUpdate: () => (this.dirty = true) }); }
    view_() { const c = this.cam; this.svg.setAttribute("viewBox", [c.x, c.y, c.w, c.h].map((v) => v.toFixed(1)).join(" ")); this.svg.style.setProperty("--lp-z", (c.w / this.W).toFixed(3)); }
    camTo(box, dur) { return Object.assign({ duration: dur, ease: "power3.inOut", onUpdate: () => this.view_() }, box); }
    box(cx, cy, w) { return { x: cx - w / 2, y: cy - (w * H) / this.W / 2, w, h: (w * H) / this.W }; }
    home() { return { x: 0, y: 0, w: this.W, h: H }; }

    /* ---- scene building: o = {ox, oy, s, hill, sign, zv (final zoom, for label declutter)} */
    build(vis, level, o) {
      const sc = { objs: [], balls: [], tw: [], live: true, o, order: "", g: el("g", { class: "ico-scene", transform: transl(o), style: "--sc:" + o.s }, this.svg) };
      if (o.hill) this.hill(sc.g, sc);
      sc.world = el("g", {}, sc.g); sc.labs = el("g", { class: "lp-labs", "aria-hidden": "true" }, sc.g);
      const lay = G.layout(vis, level.id), reg = (m, cls) => { m.g = el("g", { class: cls }, sc.world); m.polys = m.faces.map(() => el("polygon", {}, m.g)); sc.objs.push(m); return m; };
      lay.limbs.forEach((l, i) => { const m = reg(G.limb(l.path, l.radii, level.id + i), "ico-limb"); if (!i) sc.trunk = m; else (sc.limbs = sc.limbs || []).push(m); });
      lay.deco.forEach((d) => { const m = reg(G.ball(d.c, d.r, level.id + d.hue + d.c[0]), "ico-ball deco h" + d.hue); m.g.setAttribute("aria-hidden", "true"); m.c0 = d.c[1]; });
      lay.balls.forEach((b) => {
        const m = reg(G.ball(b.c, b.r, b.item.id), "ico-ball h" + b.hue + (b.item.ref && b.item.ref.tc === 0 ? " soon" : "") + (b.item.more ? " more" : ""));
        Object.assign(m, { item: b.item, c0: b.c[1], hue: b.hue }); sc.balls.push(m);
        if (!this.still) this.wire(m);
        const lab = (m.lab = el("g", { class: "lp-lab" + (b.item.more ? " pill" : "") }, sc.labs)), ls = lines(short(b.item.label)), w = Math.max(...ls.map((l) => l.length)) * 8.6 + 16, h = ls.length * 18 + 8;
        el("rect", { x: -w / 2, y: -h / 2, width: w, height: h, rx: 11, class: "lp-pill ico-pill" }, lab);
        ls.forEach((t, i) => el("text", { x: 0, y: -h / 2 + 18 + i * 18 - 2, "text-anchor": "middle", class: "ico-t", text: t }, lab));
        lab.w = w; lab.h = h;
      });
      if (o.sign) this.sign(sc, lay.sign);
      if (o.hill) { this.tufts(sc.front); sc.g.insertBefore(sc.front, sc.labs); }
      sc.objs.forEach((m) => { if (m.kind === "ball" && !m.item) m.g.style.pointerEvents = "none"; });
      sc.zv = o.zv || 1;
      this.draw(sc);
      const rs = sc.balls.map((m) => ({ x: m.sx, y: m.sy + m.sr * 0.38 - (m.lab.h * sc.zv) / o.s / 2, w: m.lab.w * sc.zv / o.s, h: m.lab.h * sc.zv / o.s }));
      this.declutter(rs);
      sc.balls.forEach((m, i) => { m.nudge = rs[i].y + rs[i].h / 2 - (m.sy + m.sr * 0.38); });
      this.draw(sc);
      return sc;
    }
    declutter(rs) {
      for (let p = 0; p < 6; p++) {
        const o = rs.map((r, i) => i).sort((a, b) => rs[a].y - rs[b].y); let mv = false;
        for (let i = 0; i < o.length; i++) for (let j = i + 1; j < o.length; j++) {
          const a = rs[o[i]], b = rs[o[j]];
          if (Math.abs(a.x - b.x) < (a.w + b.w) / 2 + 3 && b.y < a.y + a.h + 3) { b.y = a.y + a.h + 3; mv = true; }
        }
        if (!mv) break;
      }
    }
    hill(g, sc) { // a wide grass mound over the right 60% of the stage, rising about 15% of the height; tufts go in front of the trunk base
      const id = "ico-gr" + (Ico.n = (Ico.n || 0) + 1), d = el("defs", {}, g), lg = el("linearGradient", { id, x1: 0, y1: 0, x2: 0, y2: 1 }, d);
      el("stop", { offset: 0, style: "stop-color:var(--qm-grass-a)" }, lg); el("stop", { offset: 1, style: "stop-color:var(--qm-grass-b)" }, lg);
      el("path", { d: "M240 660 C262 570 360 510 480 506 C580 503 660 510 800 466 L800 660Z", fill: "url(#" + id + ")", class: "ico-hill" }, g);
      el("path", { d: "M330 640 C400 574 480 552 570 552 C650 552 720 530 800 506 L800 660 L330 660Z", class: "ico-hill2" }, g);
      sc.front = el("g", {}, g);
    }
    tufts(g) {
      for (let i = 0; i < 14; i++) {
        const x = 290 + i * 32 + hash("tuft" + i) * 22, crest = x > 480 ? 506 - (x - 480) * 0.12 : 506 + (480 - x) * 0.33, y = crest + 8 + hash("ty" + i) * 34, t = el("g", { class: "ico-tuft" }, g);
        [-1, 0, 1].forEach((k) => { const h = 16 + hash("th" + i + k) * 14; el("polygon", { points: [x + k * 6 - 4, y, x + k * 6 + 4, y, x + k * 9, y - h].join(" "), class: "t" + (k + 1) }, t); });
      }
    }
    sign(sc, s) {
      const a = el("a", { href: "#", class: "ico-sign", "aria-label": "Start here, open sign-up" }, sc.world), ropes = [el("line", { class: "ico-rope" }, a), el("line", { class: "ico-rope" }, a)];
      const m = G.plank(s.a, 92, 31, 8, 118); m.g = a; m.polys = m.faces.map(() => el("polygon", {}, a)); m.ropes = ropes; m.anchors = s.l; m.kind = "plank";
      m.text = el("text", { class: "ico-sign-t", "text-anchor": "middle", "dominant-baseline": "central", text: "Start here" }, a);
      a.addEventListener("click", (e) => e.preventDefault());
      sc.objs.push(m); sc.sign = m;
    }
    wire(m) {
      const g = m.g, it = m.item, ctl = this.ctl, hot = (on) => { g.classList.toggle("hot", on); if (it.color && !it.more) g.style.setProperty("--c", on ? it.color : ""); m.lab.classList.toggle("hot", on); };
      g.setAttribute("role", "button"); g.setAttribute("tabindex", "0"); g.setAttribute("aria-label", it.label + (it.meta ? ", " + it.meta : ""));
      const go = () => ctl.open(it);
      g.addEventListener("click", go); g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
      ["pointerenter", "focus"].forEach((ev) => g.addEventListener(ev, () => hot(true))); ["pointerleave", "blur"].forEach((ev) => g.addEventListener(ev, () => hot(false)));
    }

    /* ---- projection -> DOM (only when dirty) */
    draw(sc) {
      const cam = G.camera(this.yaw, this.pitch), keys = [];
      sc.objs.forEach((m) => {
        const r = G.project(m, cam); m.z = r.z + (m.kind === "limb" ? -40 : 0);
        m.polys.forEach((p, i) => {
          const f = r.faces[i];
          if (!f) { p.style.display = "none"; return; }
          p.style.display = ""; p.setAttribute("points", f.pts.map((q) => q[0].toFixed(1) + "," + q[1].toFixed(1)).join(" ")); p.setAttribute("class", "ico-f t" + f.tone);
        });
        if (m.kind === "ball") {
          m.sx = r.c[0]; m.sy = r.c[1]; m.sr = r.sr;
          if (m.lab) m.lab.style.transform = "translate(" + m.sx.toFixed(1) + "px," + (m.sy + m.sr * 0.38 + (m.nudge || 0)).toFixed(1) + "px) scale(calc(var(--lp-z,1) / var(--sc,1)))";
        }
        if (m.kind === "plank") this.rig(m, cam);
        keys.push(m);
      });
      keys.sort((a, b) => a.z - b.z);
      const ord = keys.map((m) => sc.objs.indexOf(m)).join();
      if (ord !== sc.order) { sc.order = ord; keys.forEach((m) => sc.world.appendChild(m.g)); }
    }
    rig(m, cam) { // ropes from the branch to the plank's top corners, and the label on its front face
      const P = (p) => cam.scr(cam.view(add(local2(m, p), m.c))), tl = P([-m.w / 2, m.drop, m.dz / 2]), tr = P([m.w / 2, m.drop, m.dz / 2]), mid = P([0, m.drop + m.h / 2, m.dz / 2 + 0.5]);
      const sa = m.anchors.map((a) => cam.scr(cam.view(a))).sort((p, q) => p[0] - q[0]); // left anchor to the left corner: never crossed
      sa.forEach((s, i) => { const e = i ? tr : tl; m.ropes[i].setAttribute("x1", s[0].toFixed(1)); m.ropes[i].setAttribute("y1", s[1].toFixed(1)); m.ropes[i].setAttribute("x2", e[0].toFixed(1)); m.ropes[i].setAttribute("y2", e[1].toFixed(1)); });
      const ang = (Math.atan2(tr[1] - tl[1], tr[0] - tl[0]) * 180) / Math.PI, k = Math.hypot(tr[0] - tl[0], tr[1] - tl[1]) / m.w;
      m.text.setAttribute("transform", "translate(" + mid[0].toFixed(1) + " " + (mid[1] + k).toFixed(1) + ") rotate(" + ang.toFixed(1) + ") scale(" + k.toFixed(3) + ")");
    }

    /* ---- motion */
    popTimeline(sc, hill) { // about 1.8 s: hill, trunk up, branches out, balls pop trunk-outward, sign drops in
      const tl = gsap.timeline({ defaults: { ease: "power2.out" }, onUpdate: () => (this.dirty = true) });
      if (hill) tl.from(sc.g.querySelectorAll(".ico-hill,.ico-hill2,.ico-tuft"), { opacity: 0, duration: 0.45, stagger: 0.05 }, 0);
      tl.fromTo(sc.trunk.g, { scaleY: 0, svgOrigin: B[0] + " " + B[1] }, { scaleY: 1, duration: 0.55 }, 0.25);
      (sc.limbs || []).forEach((l, i) => tl.fromTo(l.g, { scale: 0, svgOrigin: F[0] + " " + F[1] }, { scale: 1, duration: 0.4 }, 0.65 + i * 0.07));
      const bs = sc.objs.filter((m) => m.kind === "ball").sort((a, b) => Math.hypot(a.c[0] - F[0], a.c[1] - F[1]) - Math.hypot(b.c[0] - F[0], b.c[1] - F[1]));
      bs.forEach((m, i) => { tl.fromTo(m.g, { scale: 0, svgOrigin: m.c[0] + " " + m.c[1] }, { scale: 1, duration: 0.45, ease: "back.out(1.8)" }, 0.95 + i * 0.06); if (m.lab) tl.from(m.lab, { opacity: 0, duration: 0.3 }, 1.3 + i * 0.05); });
      if (sc.sign) tl.fromTo(sc.sign.g, { y: -46, opacity: 0 }, { y: 0, opacity: 1, duration: 0.45, ease: "back.out(1.6)" }, 1.35);
      return tl;
    }
    idle(sc) {
      if (this.still || reduced()) return;
      sc.objs.forEach((m) => { if (m.kind !== "ball") return; const h = hash(m.c[0] + ":" + m.r); const o = { y: -2 }; sc.tw.push(gsap.to(o, { y: 2, duration: 2.2 + h * 1.4, yoyo: true, repeat: -1, ease: "sine.inOut", onUpdate: () => { m.c[1] = m.c0 + o.y; this.dirty = true; } }).progress(h)); });
      if (sc.sign) sc.tw.push(gsap.fromTo(sc.sign, { rz: -0.09 }, { rz: 0.09, duration: 1.7, yoyo: true, repeat: -1, ease: "sine.inOut", onUpdate: () => (this.dirty = true) }));
      const balls = sc.objs.filter((m) => m.kind === "ball").sort((a, b) => a.c[0] - b.c[0]);
      const gust = () => { sc.tw.push(gsap.to(balls, { spin: 0.2, duration: 0.7, yoyo: true, repeat: 1, ease: "sine.inOut", stagger: 0.07, onUpdate: () => (this.dirty = true) })); sc.gust = gsap.delayedCall(8, gust); };
      sc.gust = gsap.delayedCall(5, gust);
    }
    kill(sc) { sc.tw.forEach((t) => t.kill()); if (sc.gust) sc.gust.kill(); sc.live = false; sc.g.remove(); }

    /* ---- levels (Explorer calls render) */
    async render(level, from, mode) {
      this.ctl.host.classList.toggle("drilled", level.kind !== "root");
      if (level.kind === "root") return this.child && mode === "out" ? this.collapse() : this.rebuild(level, mode);
      if (level.kind === "subject") return this.child && mode === "out" ? this.pulse(null) : this.expand(level);
      return this.pulse(level);
    }
    async rebuild(level, mode) {
      if (this.root && mode === "swap" && !reduced()) await new Promise((r) => gsap.to(this.root.g, { opacity: 0, duration: 0.25, onComplete: r }));
      [this.root, this.child].forEach((sc) => sc && this.kill(sc)); this.child = null; this.cam = this.home(); this.view_();
      const sc = (this.root = this.build(G.rank(level.items, false, level.id), level, { ox: this.DX, oy: 0, s: 1, hill: true, sign: true }));
      this.live(sc, true);
      if (this.still || reduced()) { this.draw(sc); return; }
      const tl = this.popTimeline(sc, true);
      await new Promise((r) => tl.eventCallback("onComplete", r));
      this.idle(sc);
    }
    live(sc, on) { sc.g.style.pointerEvents = on ? "" : "none"; sc.balls.forEach((m) => m.g.setAttribute("tabindex", on ? "0" : "-1")); }
    async expand(level) {
      const sc = this.root, ball = sc.balls.find((m) => m.item.id === level.id);
      if (!ball) return;
      const s = 0.42, bx = sc.o.ox + ball.sx * sc.o.s, by = sc.o.oy + ball.sy * sc.o.s, w = this.W;
      const fw = Math.max(560 * s * 1.14, (500 * s * 1.14 * w) / H), fin = this.box(bx - 80 * s, by - 280 * s, fw); // final view of the new tree
      if (this.W > 640) fin.x -= fin.w * 0.2; else { fin.x += fin.w * 0.14; fin.y -= fin.h * 0.14; } // room for the panel: top-left (16:9) / top-right (hero)
      const ch = (this.child = this.build(G.rank(level.items, true, level.id), level, { ox: bx - B[0] * s, oy: by - B[1] * s, s, hill: false, sign: false, zv: fin.w / w }));
      this.live(sc, false); this.live(ch, true); ch.g.style.opacity = 0; this.chosen = ball;
      if (this.still || reduced()) { this.cam = fin; this.view_(); ch.g.style.opacity = 1; sc.g.style.opacity = 0; this.shatter(ball, true); return; }
      sc.live = false; // freeze the parent while its ball breaks up
      const tl = gsap.timeline({ onUpdate: () => (this.dirty = true) });
      tl.to(this.cam, this.camTo(this.box(bx, by, Math.max(170, ball.sr * sc.o.s * 5.2)), 0.65), 0);
      tl.add(() => this.shatter(ball), 0.4);
      tl.set(ch.g, { opacity: 1 }, 0.75).add(this.popTimeline(ch, false), 0.75);
      tl.to(this.cam, this.camTo(fin, 0.7), 1.3).to(sc.g, { opacity: 0.05, duration: 0.5 }, 1.3);
      await new Promise((r) => tl.eventCallback("onComplete", r));
      this.idle(ch);
    }
    shatter(ball, snap) { // facets scatter outward and fade; reassembled in collapse()
      ball.polys.forEach((p, i) => {
        if (p.style.display === "none") return;
        const q = p.getAttribute("points").split(" ").map((t) => t.split(",").map(Number)), cx = q.reduce((a, t) => a + t[0], 0) / q.length - ball.sx, cy = q.reduce((a, t) => a + t[1], 0) / q.length - ball.sy, l = Math.hypot(cx, cy) || 1;
        const v = { x: (cx / l) * 70, y: (cy / l) * 70 - 14, rotation: (hash("sh" + i) - 0.5) * 160, opacity: 0, duration: 0.65, ease: "power2.out" };
        snap ? gsap.set(p, v) : gsap.to(p, v);
      });
    }
    async collapse() {
      const ch = this.child, sc = this.root, ball = this.chosen, s = sc.o.s;
      this.child = null; this.sel = null;
      const bx = sc.o.ox + ball.sx * s, by = sc.o.oy + ball.sy * s;
      if (this.still || reduced()) { this.kill(ch); sc.g.style.opacity = 1; ball.polys.forEach((p) => gsap.set(p, { clearProps: "all" })); this.cam = this.home(); this.view_(); this.live(sc, true); sc.live = true; this.dirty = true; return; }
      const tl = gsap.timeline({ onUpdate: () => (this.dirty = true) });
      tl.to(ch.g, { opacity: 0, duration: 0.35 }, 0).to(this.cam, this.camTo(this.box(bx, by, Math.max(170, ball.sr * s * 5.2)), 0.5), 0).to(sc.g, { opacity: 1, duration: 0.4 }, 0.1);
      tl.to(ball.polys, { x: 0, y: 0, rotation: 0, opacity: 1, duration: 0.5, ease: "power2.inOut", stagger: 0.012, clearProps: "all" }, 0.35);
      tl.to(this.cam, this.camTo(this.home(), 0.65), 0.9);
      await new Promise((r) => tl.eventCallback("onComplete", r));
      this.kill(ch); sc.live = true; this.live(sc, true); this.dirty = true;
    }
    async pulse(level) { // topic = last level: the ball pulses and the Explorer panel opens
      const ch = this.child; if (!ch) return;
      ch.balls.forEach((m) => { const on = level && m.item.id === level.id; m.g.classList.toggle("sel", !!on); m.g.style.opacity = !level || on ? 1 : 0.45; m.lab.style.opacity = !level || on ? 1 : 0.45; });
      const b = level && ch.balls.find((m) => m.item.id === level.id);
      if (b && !reduced()) gsap.fromTo(b.g, { scale: 1, svgOrigin: b.sx + " " + b.sy }, { scale: 1.14, duration: 0.2, yoyo: true, repeat: 1, ease: "sine.inOut", clearProps: "transform" });
    }
  }
  const local2 = (m, p) => { let q = p; if (m.rz) q = rz(q, m.rz); return q; };

  const boot = () => document.querySelectorAll('[data-qm="ico"]').forEach((h) => { h.classList.add("ico"); new Q.Explorer(h, Ico, { static: h.hasAttribute("data-static") }); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})(typeof window !== "undefined" ? window : globalThis);
