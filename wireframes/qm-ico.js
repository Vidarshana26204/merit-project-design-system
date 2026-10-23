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
    // Node crowns [x, y, z, r]: small, in a wide fan, each at the end of its own twig (design space 640 x 600). Filled centre-out.
    const SLOT = [[330, 92, 40, 60], [178, 142, 30, 58], [486, 136, 34, 60], [92, 238, 22, 56], [546, 236, 22, 56], [262, 236, 46, 58]];
    const MORE = [420, 236, 40, 40];
    // Neutral background crowns: bigger, further back, never interactive. They make the canopy one mass behind the nodes.
    const BG = [[330, 172, -120, 108], [228, 150, -100, 92], [440, 150, -105, 96], [138, 214, -85, 78], [532, 206, -90, 80], [330, 92, -110, 74],
      [200, 82, -95, 66], [470, 80, -95, 68], [90, 286, -70, 56], [580, 284, -70, 54], [382, 262, -80, 72], [258, 272, -75, 62]];
    // Three boughs leave the fork; a node's twig starts on the bough nearest it, so the structure reads at a glance.
    const BOUGH = [[226, 300, 12], [346, 236, 18], [470, 286, 12]];
    const boughOf = (x) => (x < 250 ? 0 : x > 420 ? 2 : 1);
    // Deterministic tree: a leaning trunk, three boughs fanning wide, one twig per node crown, neutral crowns behind,
    // and a long lower-left branch that carries the sign into open sky.
    function layout(vis, id) {
      const j = (k, a) => (hash(id + k) - 0.5) * a, balls = [];
      vis.forEach((it, i) => {
        const sl = it.more ? MORE : SLOT[i];
        balls.push({ item: it, c: [sl[0] + j("bx" + i, 8), sl[1] + j("by" + i, 8), sl[2]], r: sl[3] + (it.more ? 0 : hash(id + "r" + i) * 4), hue: Math.floor(hash(id + "h" + i) * 5) });
      });
      const nd = vis.length >= 5 ? 12 : vis.length >= 3 ? 10 : 8;
      const deco = BG.slice(0, nd).map((d, k) => ({ item: null, c: [d[0] + j("dx" + k, 12), d[1] + j("dy" + k, 12), d[2]], r: d[3] + hash(id + "dr" + k) * 8, hue: k % 3 }));
      const limbs = [{ role: "trunk", path: [B, [B[0] - 16, 480, 10], F], radii: [28, 21, 15] }];
      BOUGH.forEach((b, k) => limbs.push({ role: "bough", path: [F, add(mul(add(F, b), 0.5), [j("bk" + k, 16), -8, j("bq" + k, 10)]), b], radii: [14, 11, 8] }));
      balls.forEach((b, i) => {
        const s0 = BOUGH[boughOf(b.c[0])], t = add(b.c, [0, b.r * 0.45, 0]);
        limbs.push({ role: "twig", ball: i, path: [s0, add(mul(add(s0, t), 0.5), [j("tk" + i, 12), j("ty" + i, 8), 0]), t], radii: [7.5, 5.5, 3.8] });
      });
      const S = add(F, [-257, -70, 50]), mid = add(F, [-128, -34, 30]), at = (t) => (t < 0.5 ? add(F, mul(sub(mid, F), t * 2)) : add(mid, mul(sub(S, mid), (t - 0.5) * 2)));
      limbs.push({ role: "sign", path: [F, mid, S], radii: [12, 8, 5] });
      const l = [at(0.52), at(0.89)]; // about one plank width apart, so the ropes hang parallel
      return { limbs, balls, deco, sign: { a: mul(add(l[0], l[1]), 0.5), l } };
    }
    return { ball, limb, plank, camera, project, rank, layout };
  }
  // Measured eases (motionmaxxing references/motion.md): landings decelerate, exits accelerate.
  const bez = (x1, y1, x2, y2) => {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx, cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const X = (t) => ((ax * t + bx) * t + cx) * t, Y = (t) => ((ay * t + by) * t + cy) * t, dX = (t) => (3 * ax * t + 2 * bx) * t + cx;
    return (p) => {
      if (p <= 0) return 0; if (p >= 1) return 1;
      let lo = 0, hi = 1, t = p;
      for (let i = 0; i < 8; i++) { const e = X(t) - p, d = dX(t); if (Math.abs(e) < 1e-6) return Y(t); if (Math.abs(d) < 1e-6) break; t -= e / d; }
      for (let i = 0; i < 40; i++) { t = (lo + hi) / 2; if (X(t) < p) lo = t; else hi = t; }
      return Y(t);
    };
  };
  const EASE = { softLand: bez(0.22, 0.9, 0.3, 1), snapSettle: bez(0.12, 0.95, 0.2, 1), glide: bez(0.33, 0.75, 0.4, 1), gentleIn: bez(0.55, 0, 0.85, 0.45), accelExit: bez(0.6, 0, 0.9, 0.35) };
  const API = { geometry, LIGHT, EASE };
  if (typeof module !== "undefined" && module.exports) module.exports = API;
  if (typeof window === "undefined") return;
  root.QMIco = API;

  /* ------------------------------------------------------------ renderer */
  const Q = root.QM, gsap = root.gsap;
  if (!Q || !gsap) { console.warn("qm-ico: needs QM and gsap"); return; }
  const { el, hash } = Q, G = geometry(hash), FR = 1 / 30;
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
      (Ico.all = Ico.all || []).push(this);
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
      sc.limbs = []; sc.twigs = [];
      lay.limbs.forEach((l, i) => {
        if ((l.role === "trunk" && o.trunk === false) || (l.role === "sign" && !o.sign)) return; // a child tree grows from the opened crown: no trunk, no sign
        const m = reg(G.limb(l.path, l.radii, level.id + i), "ico-limb");
        Object.assign(m, { role: l.role, base: l.path[0], end: l.path[l.path.length - 1] });
        if (l.role === "trunk") sc.trunk = m; else sc.limbs.push(m);
        if (l.role === "twig") sc.twigs[l.ball] = m;
      });
      sc.bg = lay.deco.map((d) => { const m = reg(G.ball(d.c, d.r, level.id + d.hue + d.c[0]), "ico-ball deco bg b" + d.hue); m.g.setAttribute("aria-hidden", "true"); m.c0 = d.c[1]; return m; });
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
      // Hover lift: up 4 units and to 1.04 (glide 6 f in, 8 f out). Skipped while a transition owns the transforms.
      const lift = (on) => { if (this.busy || reduced()) return; gsap.to(g, { y: on ? -4 : 0, scale: on ? 1.04 : 1, svgOrigin: m.sx + " " + m.sy, duration: (on ? 6 : 8) * FR, ease: EASE.glide, overwrite: "auto" }); };
      g.addEventListener("click", go); g.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); go(); } });
      ["pointerenter", "focus"].forEach((ev) => g.addEventListener(ev, () => { hot(true); lift(true); })); ["pointerleave", "blur"].forEach((ev) => g.addEventListener(ev, () => { hot(false); lift(false); }));
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
          if (m.lab) m.lab.style.transform = "translate(" + m.sx.toFixed(1) + "px," + (m.sy + m.sr * 0.38 + (m.nudge || 0) + (m.ldy || 0)).toFixed(1) + "px) scale(calc(var(--lp-z,1) / var(--sc,1)))";
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

    /* ---- motion. Frame counts are at 30 fps (FR = 1 f). Rules from motionmaxxing: landings decelerate (softLand, snapSettle),
       exits accelerate (accelExit, gentleIn), siblings overlap on uneven 1-3 f gaps, opacity is only a 4-6 f helper, one spring
       per transition, and the opened crown is the carried object: its facets become the child crowns. */
    popTimeline(sc, hill) { // about 1.8 s: hill, trunk up, boughs and twigs out, neutral crowns then node crowns pop, sign drops in
      const tl = gsap.timeline({ defaults: { ease: EASE.softLand }, onUpdate: () => (this.dirty = true) });
      if (hill) tl.from(sc.g.querySelectorAll(".ico-hill,.ico-hill2,.ico-tuft"), { opacity: 0, y: 10, duration: 14 * FR, stagger: 0.04 }, 0);
      if (sc.trunk) tl.fromTo(sc.trunk.g, { scaleY: 0, svgOrigin: B[0] + " " + B[1] }, { scaleY: 1, duration: 16 * FR }, 0.25);
      sc.limbs.forEach((l, i) => tl.fromTo(l.g, { scale: 0, svgOrigin: l.base[0] + " " + l.base[1] }, { scale: 1, duration: 12 * FR }, l.role === "twig" ? 0.82 + i * 0.04 : 0.62 + i * 0.07));
      const d = (m) => Math.hypot(m.c[0] - F[0], m.c[1] - F[1]);
      sc.bg.slice().sort((a, b) => d(a) - d(b)).forEach((m, i) => tl.fromTo(m.g, { scale: 0.6, opacity: 0, svgOrigin: m.c[0] + " " + m.c[1] }, { scale: 1, opacity: 1, duration: 12 * FR }, 0.86 + i * 0.035));
      sc.balls.slice().sort((a, b) => d(a) - d(b)).forEach((m, i) => {
        tl.fromTo(m.g, { scale: 1.25, opacity: 0, svgOrigin: m.c[0] + " " + m.c[1] }, { scale: 1, duration: 11 * FR, ease: EASE.snapSettle }, 1.18 + i * 0.07).to(m.g, { opacity: 1, duration: 4 * FR, ease: "none" }, 1.18 + i * 0.07);
        tl.fromTo(m, { ldy: 6 }, { ldy: 0, duration: 10 * FR }, 1.28 + i * 0.07).from(m.lab, { opacity: 0, duration: 4 * FR, ease: "none" }, 1.28 + i * 0.07);
      });
      if (sc.sign) tl.fromTo(sc.sign.g, { y: -46, opacity: 0 }, { y: 0, opacity: 1, duration: 14 * FR, ease: EASE.snapSettle }, 1.5);
      return tl;
    }
    idle(sc) {
      if (this.still || reduced()) return;
      sc.objs.forEach((m) => { // node crowns bob +-2; neutral crowns half as far and slower
        if (m.kind !== "ball") return; const h = hash(m.c[0] + ":" + m.r), a = m.item ? 2 : 1, o = { y: -a };
        sc.tw.push(gsap.to(o, { y: a, duration: (m.item ? 2.2 : 3.4) + h * 1.4, yoyo: true, repeat: -1, ease: "sine.inOut", onUpdate: () => { m.c[1] = m.c0 + o.y; this.dirty = true; } }).progress(h));
      });
      if (sc.sign) sc.tw.push(gsap.fromTo(sc.sign, { rz: -0.09 }, { rz: 0.09, duration: 1.7, yoyo: true, repeat: -1, ease: "sine.inOut", onUpdate: () => (this.dirty = true) }));
      const balls = sc.objs.filter((m) => m.kind === "ball").sort((a, b) => a.c[0] - b.c[0]);
      const gust = () => { sc.tw.push(gsap.to(balls, { spin: 0.2, duration: 0.7, yoyo: true, repeat: 1, ease: "sine.inOut", stagger: 0.05, onUpdate: () => (this.dirty = true) })); sc.gust = gsap.delayedCall(8, gust); };
      sc.gust = gsap.delayedCall(5, gust);
    }
    kill(sc) { sc.tw.forEach((t) => t.kill()); if (sc.gust) sc.gust.kill(); sc.live = false; sc.g.remove(); }

    /* ---- levels (Explorer calls render). One transition at a time: a new request makes the running one finish at 2x. */
    async render(level, from, mode) {
      if (this.busy) { if (this.tl) this.tl.timeScale(2); await this.busy; }
      const run = (this.busy = this.render_(level, mode));
      try { await run; } finally { if (this.busy === run) this.busy = null; }
    }
    async render_(level, mode) {
      this.ctl.host.classList.toggle("drilled", level.kind !== "root");
      if (level.kind === "root") return this.child && mode === "out" ? this.collapse() : this.rebuild(level, mode);
      if (level.kind === "subject") return this.child && mode === "out" ? this.pulse(null) : this.expand(level);
      return this.pulse(level);
    }
    async rebuild(level, mode) {
      if (this.root && mode === "swap" && !reduced()) await new Promise((r) => gsap.to(this.root.g, { opacity: 0, y: 8, duration: 8 * FR, ease: EASE.gentleIn, onComplete: r }));
      [this.root, this.child].forEach((sc) => sc && this.kill(sc)); this.child = null; this.cam = this.home(); this.view_();
      const sc = (this.root = this.build(G.rank(level.items, false, level.id), level, { ox: this.DX, oy: 0, s: 1, hill: true, sign: true }));
      this.live(sc, true);
      if (this.still || reduced()) { this.draw(sc); return; }
      const tl = (this.tl = this.popTimeline(sc, true));
      await new Promise((r) => tl.eventCallback("onComplete", r));
      this.idle(sc);
    }
    live(sc, on) { sc.g.style.pointerEvents = on ? "" : "none"; sc.balls.forEach((m) => m.g.setAttribute("tabindex", on ? "0" : "-1")); }
    wood(sc) { return [sc.trunk, ...sc.limbs].filter(Boolean).map((m) => m.g).concat(sc.sign ? [sc.sign.g] : [], [...sc.g.querySelectorAll(".ico-hill,.ico-hill2,.ico-tuft")]); }
    // The child tree's view: its crown framed with room for the panel (top-left on the 16:9 stage, top-right in the hero).
    childView(ox, oy, s) {
      const w = Math.max(640 * s * 1.22, (440 * s * 1.22 * this.W) / H), v = this.box(ox + 330 * s, oy + 230 * s, w);
      if (this.W > 640) v.x -= v.w * 0.16; else v.y -= v.h * 0.14;
      return v;
    }
    async expand(level) {
      const sc = this.root, ball = sc.balls.find((m) => m.item.id === level.id);
      if (!ball) return;
      const s = 0.56, bx = sc.o.ox + ball.sx, by = sc.o.oy + ball.sy + ball.sr * 0.45, ox = bx - F[0] * s, oy = by - F[1] * s, fin = this.childView(ox, oy, s);
      // The child tree's fork sits on the opened crown: it grows out of it.
      const ch = (this.child = this.build(G.rank(level.items, true, level.id), level, { ox, oy, s, hill: false, sign: false, trunk: false, zv: fin.w / this.W }));
      this.live(sc, false); this.live(ch, true); this.chosen = ball;
      const facets = ball.polys.filter((p) => p.style.display !== "none");
      if (this.still || reduced()) { this.cam = fin; this.view_(); gsap.set(this.wood(sc).concat(sc.balls.map((m) => m.g), sc.bg.map((m) => m.g), sc.balls.map((m) => m.lab)), { opacity: 0 }); return; }
      sc.live = false; // freeze the parent's projection while its crown becomes the child tree
      const f = FR, tl = (this.tl = gsap.timeline({ onUpdate: () => (this.dirty = true) })), o = (m) => m.sx + " " + m.sy, dist = (m) => Math.hypot(m.sx - ball.sx, m.sy - ball.sy);
      // child starts hidden: limbs folded, crowns and labels off
      ch.limbs.forEach((l) => gsap.set(l.g, { scale: 0, svgOrigin: l.base[0] + " " + l.base[1] }));
      gsap.set(ch.balls.map((m) => m.g).concat(ch.bg.map((m) => m.g), ch.balls.map((m) => m.lab)), { opacity: 0 });
      // 1. press: squash 2 f, the crown answers a frame later
      tl.to(ball.g, { scale: 0.94, svgOrigin: o(ball), duration: 2 * f, ease: "power1.out" }, 0).to(ball.g, { scale: 1.02, svgOrigin: o(ball), duration: 5 * f, ease: EASE.softLand }, 3 * f);
      // 2. siblings leave nearest first on uneven gaps, accelerating outward; neutral crowns recede slower and half as far
      const gaps = [2, 1, 3, 2, 2, 1, 2];
      sc.balls.filter((m) => m !== ball).sort((a, b) => dist(a) - dist(b)).forEach((m, i) => {
        const at = (2 + gaps.slice(0, i).reduce((a, b) => a + b, 0)) * f, l = dist(m) || 1;
        tl.to(m.g, { x: ((m.sx - ball.sx) / l) * 40, y: ((m.sy - ball.sy) / l) * 40, scale: 0.7, svgOrigin: o(m), duration: 12 * f, ease: EASE.accelExit }, at)
          .to(m.g, { opacity: 0, duration: 5 * f, ease: "none" }, at + 7 * f).to(m.lab, { opacity: 0, duration: 4 * f, ease: "none" }, at);
      });
      sc.bg.forEach((m, i) => {
        const at = (3 + (i % 4)) * f, l = dist(m) || 1;
        tl.to(m.g, { x: ((m.sx - ball.sx) / l) * 20, y: ((m.sy - ball.sy) / l) * 20, scale: 0.85, svgOrigin: o(m), duration: 15 * f, ease: EASE.accelExit }, at).to(m.g, { opacity: 0, duration: 6 * f, ease: "none" }, at + 9 * f);
      });
      tl.set(ball.lab, { opacity: 0 }, 8 * f); // the name moves to the breadcrumb (a state change: hard cut)
      // 3. camera: one move, fast front and a long soft tail; the parent's wood is swept away inside it
      tl.to(this.cam, Object.assign({ duration: 20 * f, ease: EASE.snapSettle, onUpdate: () => this.view_() }, fin), 3 * f);
      const twig = sc.twigs[sc.balls.indexOf(ball)], path = [sc.trunk, twig, sc.limbs.find((l) => l.role === "bough" && twig && l.end[0] === twig.base[0] && l.end[1] === twig.base[1])].filter(Boolean).map((m) => m.g);
      tl.to(this.wood(sc).filter((g) => !path.includes(g)), { opacity: 0.05, duration: 12 * f, ease: EASE.gentleIn }, 3 * f);
      // 4. bloom: boughs grow from the crown's centre, each twig carries a share of the crown's facets out to a child crown
      ch.limbs.filter((l) => l.role === "bough").forEach((l, k) => tl.to(l.g, { scale: 1, duration: 10 * f, ease: EASE.softLand }, (8 + k * 2) * f));
      const stag = [0, 2, 4, 7, 8, 10, 12], kids = ch.balls, P = (x, y) => [ox + x * s - sc.o.ox, oy + y * s - sc.o.oy]; // child design point -> parent-local
      kids.forEach((k, i) => {
        const t0 = (12 + stag[i]) * f, land = t0 + 10 * f, tw = ch.twigs[i];
        if (tw) tl.to(tw.g, { scale: 1, duration: 12 * f, ease: EASE.softLand }, t0);
        const last = i === kids.length - 1;
        tl.fromTo(k.g, { scale: 1.25, svgOrigin: o(k) }, { scale: last ? 0.92 : 1, duration: (last ? 8 : 11) * f, ease: EASE.snapSettle }, land).to(k.g, { opacity: 1, duration: 4 * f, ease: "none" }, land);
        if (last) tl.to(k.g, { scale: 1, svgOrigin: o(k), duration: 6 * f, ease: "back.out(3)" }, land + 8 * f); // the one spring
        tl.fromTo(k, { ldy: 6 }, { ldy: 0, duration: 10 * f, ease: EASE.softLand }, land + 3 * f).to(k.lab, { opacity: 1, duration: 4 * f, ease: "none" }, land + 3 * f);
        // this crown's facets travel the bough then the twig, shrinking into it
        const mid = tw ? P(tw.base[0], tw.base[1]) : P(F[0], F[1]), tgt = [ox + k.sx * s - sc.o.ox, oy + k.sy * s - sc.o.oy];
        facets.filter((_, j) => j % kids.length === i).forEach((p) => {
          const q = p.getAttribute("points").split(" ").map((t) => t.split(",").map(Number)), cx = q.reduce((a, t) => a + t[0], 0) / q.length, cy = q.reduce((a, t) => a + t[1], 0) / q.length;
          tl.to(p, { x: mid[0] - cx, y: mid[1] - cy, scale: 0.7, transformOrigin: "50% 50%", duration: 5 * f, ease: EASE.gentleIn }, t0)
            .to(p, { x: tgt[0] - cx, y: tgt[1] - cy, scale: 0.4, duration: 5 * f, ease: EASE.softLand }, t0 + 5 * f)
            .to(p, { opacity: 0, duration: 3 * f, ease: "none" }, land);
        });
      });
      const bgAt = (12 + stag[Math.min(2, kids.length - 1)] + 10) * f; // neutral crowns fill in behind, last
      ch.bg.forEach((m, i) => tl.fromTo(m.g, { scale: 0.85, svgOrigin: o(m) }, { scale: 1, duration: 12 * f, ease: EASE.softLand }, bgAt + (i % 2 ? 2 : 1) * i * f * 0.5).to(m.g, { opacity: 1, duration: 4 * f, ease: "none" }, bgAt + (i % 2 ? 2 : 1) * i * f * 0.5));
      await new Promise((r) => tl.eventCallback("onComplete", r));
      this.idle(ch);
    }
    async collapse() { // a designed reverse, not a rewind (about 0.8 s)
      const ch = this.child, sc = this.root, ball = this.chosen, f = FR, o = (m) => m.sx + " " + m.sy;
      this.child = null;
      const facets = ball.polys.filter((p) => p.style.display !== "none"), sibs = sc.balls.filter((m) => m !== ball), dist = (m) => Math.hypot(m.sx - ball.sx, m.sy - ball.sy);
      const reset = () => { this.kill(ch); gsap.set(facets, { clearProps: "all" }); gsap.set(sc.balls.map((m) => m.g).concat(sc.bg.map((m) => m.g)), { clearProps: "opacity" }); sc.live = true; this.live(sc, true); this.dirty = true; };
      if (this.still || reduced()) { gsap.set(this.wood(sc).concat(sc.balls.map((m) => m.g), sc.bg.map((m) => m.g), sc.balls.map((m) => m.lab)), { opacity: 1, x: 0, y: 0, scale: 1 }); this.cam = this.home(); this.view_(); reset(); return; }
      const tl = (this.tl = gsap.timeline({ onUpdate: () => (this.dirty = true) }));
      tl.set(ch.balls.map((m) => m.lab), { opacity: 0 }, 0); // labels off: hard cut
      // child crowns leave toward the fork, farthest first; their facets fly home and reassemble the crown
      const fork = [F[0], F[1]], fd = (m) => Math.hypot(m.sx - fork[0], m.sy - fork[1]), gaps = [1, 2, 1, 2, 1, 2];
      const kids = ch.balls.map((k, i) => ({ k, i })).sort((a, b) => fd(b.k) - fd(a.k));
      kids.forEach(({ k, i }, n) => {
        const at = gaps.slice(0, n).reduce((a, b) => a + b, 0) * f;
        tl.to(k.g, { scale: 0.4, opacity: 0, svgOrigin: o(k), duration: 7 * f, ease: EASE.gentleIn }, at);
        facets.filter((_, j) => j % ch.balls.length === i).forEach((p) => tl.set(p, { opacity: 1 }, at).to(p, { x: 0, y: 0, scale: 1, duration: 10 * f, ease: EASE.softLand }, at));
      });
      ch.bg.forEach((m) => tl.to(m.g, { opacity: 0, scale: 0.85, svgOrigin: o(m), duration: 6 * f, ease: EASE.gentleIn }, 0));
      ch.limbs.forEach((l) => tl.to(l.g, { scale: 0, duration: 8 * f, ease: EASE.accelExit }, (l.role === "twig" ? 3 : 7) * f));
      tl.to(ball.g, { scale: 1, svgOrigin: o(ball), duration: 8 * f, ease: EASE.softLand }, 4 * f);
      // camera: two pushes, an accelerating start then a soft tail home
      const h = this.home(), c = Object.assign({}, this.cam), m30 = { x: c.x + (h.x - c.x) * 0.3, y: c.y + (h.y - c.y) * 0.3, w: c.w + (h.w - c.w) * 0.3, h: c.h + (h.h - c.h) * 0.3 };
      tl.to(this.cam, Object.assign({ duration: 6 * f, ease: EASE.gentleIn, onUpdate: () => this.view_() }, m30), 2 * f).to(this.cam, Object.assign({ duration: 14 * f, ease: EASE.softLand, onUpdate: () => this.view_() }, h), 8 * f);
      tl.to(this.wood(sc), { opacity: 1, duration: 14 * f, ease: EASE.softLand }, 6 * f);
      // siblings and neutral crowns come back to their slots from 0.85, nearest first
      sibs.sort((a, b) => dist(a) - dist(b)).forEach((m, i) => {
        const at = (10 + i * 2 + (i % 2)) * f;
        tl.set(m.g, { scale: 0.85, x: 0, y: 0, svgOrigin: o(m) }, at).to(m.g, { scale: 1, svgOrigin: o(m), duration: 12 * f, ease: EASE.softLand }, at).to(m.g, { opacity: 1, duration: 4 * f, ease: "none" }, at).to(m.lab, { opacity: 1, duration: 4 * f, ease: "none" }, at + 3 * f);
      });
      sc.bg.forEach((m, i) => tl.set(m.g, { scale: 0.85, x: 0, y: 0, svgOrigin: o(m) }, (8 + (i % 3)) * f).to(m.g, { scale: 1, opacity: 1, svgOrigin: o(m), duration: 12 * f, ease: EASE.softLand }, (8 + (i % 3)) * f));
      tl.to(ball.lab, { opacity: 1, duration: 4 * f, ease: "none" }, 14 * f);
      await new Promise((r) => tl.eventCallback("onComplete", r));
      reset();
    }
    async pulse(level) { // topic = last level: squash, a 1.06 pulse, the rest dims; the Explorer panel opens
      const ch = this.child, f = FR; if (!ch) return;
      ch.balls.forEach((m) => { const on = !level || m.item.id === level.id; m.g.classList.toggle("sel", !!(level && on)); gsap.to([m.g, m.lab], { opacity: on ? 1 : 0.45, duration: 8 * f, ease: EASE.glide }); });
      const b = level && ch.balls.find((m) => m.item.id === level.id);
      if (!b || reduced()) return;
      const tl = (this.tl = gsap.timeline());
      tl.to(b.g, { scale: 0.94, svgOrigin: b.sx + " " + b.sy, duration: 2 * f, ease: "power1.out" }).to(b.g, { scale: 1.06, duration: 4 * f, ease: EASE.glide }).to(b.g, { scale: 1, duration: 6 * f, ease: EASE.glide });
      await new Promise((r) => tl.eventCallback("onComplete", r));
    }
  }
  const local2 = (m, p) => { let q = p; if (m.rz) q = rz(q, m.rz); return q; };

  // Review hook: drive and scrub a mount's transitions (QMIco.debug(i).drill("Physics"), then .seek(0.25)).
  API.debug = (i) => { const x = Ico.all[i]; return {
    drill: (name) => { const m = (x.child || x.root).balls.find((b) => b.item.label === name || b.item.id === name); if (m) x.ctl.open(m.item); return !!m; },
    seek: (p) => { if (x.tl) { x.tl.pause(); x.tl.progress(p); x.dirty = true; } }, play: () => x.tl && x.tl.play(), labels: () => (x.child || x.root).balls.map((b) => b.item.label) }; };
  const boot = () => document.querySelectorAll('[data-qm="ico"]').forEach((h) => { h.classList.add("ico"); new Q.Explorer(h, Ico, { static: h.hasAttribute("data-static") }); });
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})(typeof window !== "undefined" ? window : globalThis);
