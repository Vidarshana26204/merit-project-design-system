#!/usr/bin/env python3
"""Hierarchy patchwork pipeline.

    VENV=…/venv (fonttools); run from the DS repo root:
    $VENV/bin/python -m scripts.patchwork.build index    --icons ../Assets/patchwork-icons --content ../merit-content
    $VENV/bin/python -m scripts.patchwork.build suggest  --content ../merit-content --subject BIOLOGY
    $VENV/bin/python -m scripts.patchwork.build generate --content ../merit-content [--subject PHYSICS …]
    $VENV/bin/python -m scripts.patchwork.build audit    --content ../merit-content
    $VENV/bin/python -m scripts.patchwork.build demo     (public demo set from MIT Phosphor glyphs)

The icon pack is licensed (Envato Elements): it may ship inside our products but must not
be redistributed. This public repo holds code only. `index` copies the deduped SVGs into
the PRIVATE merit-content repo and every later step reads them from there.

Layout under <content>/patchworks/:
    icons/<set>/<name>.svg            deduped canonical icons
    icon-index.json                   [{id, set, name, sha256, view, tags}]
    maps/<SUBJECT>.json               curation: node code → {icon, how: curated|pool, why}
    registry.json                     signatures, salts, composition keys (append-only)
    out/<node_key>/{tile,mono,wash}.svg     (wash: nodes that added a patch; v4 dropped row)
    manifest.json                     node_key → {level, subject, code, signature, icon, variants}
    index.html                        contact sheet for review
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from patchwork import engine, icon as iconlib  # type: ignore
else:
    from . import engine, icon as iconlib

LEVEL_ORDER = {"subject": 0, "topic": 1, "subtopic": 2}
STOP = {"and", "the", "of", "in", "a", "an", "to", "for", "with", "on", "its", "their", "by", "as", "at", "from"}
# Sets ranked for pool fallback (science-adjacent first).
SET_RANK = ["Science", "Chemistry", "Medical", "Healthy", "Ecology", "Sea", "Space", "GlobalWarming", "AirPollution",
            "Photography", "MusicAndMultimedia", "PlasticPollution", "Food", "PetShop", "Family", "Cleaning",
            "ComputerTechnology", "InternetOfThings", "Artificial_Intelligence", "Education",
            "Communications", "Logistics", "Office", "Startup", "Fintech", "BusinessAndFinance", "Insurance"]


def pw(content: Path) -> Path:
    return content / "patchworks"


# ── index ─────────────────────────────────────────────────────────────────────────────────
def cmd_index(a: argparse.Namespace) -> None:
    """Dedup the pack by byte checksum. Canonical ids already in icon-index.json are kept,
    so adding sets never renames an icon that a map references."""
    src, out = Path(a.icons), pw(Path(a.content))
    prev_path = out / "icon-index.json"
    prev = {e["sha256"]: e["id"] for e in json.loads(prev_path.read_text())} if prev_path.exists() else {}
    found: dict[str, list[tuple[str, str, bytes]]] = {}     # sha → [(set, name, bytes)]
    avatars = 0
    for d in sorted(p for p in src.iterdir() if p.is_dir()):
        line = re.fullmatch(r"30 (.+) Icons", d.name)
        if line:                             # "30 X Icons" packs: Colorline + Outline pairs
            for set_name, name, raw in _line_pack(d):
                found.setdefault(iconlib.sha256_bytes(raw), []).append((set_name, name, raw))
            continue
        if "avatar" in d.name.lower():       # student avatars: own catalogue, never in the node pool
            avatars = _avatars(d, out)
            continue
        numbered = re.fullmatch(r"\d+ - (\w+) - .+", d.name)
        if numbered:                         # "146 - Chemistry - 13.Linear Multicolor (…)": SVG/<nnnn - Name>.svg
            for f in sorted((d / "SVG").glob("*.svg")):
                name = re.sub(r"^\d+ - ", "", f.stem).strip().replace(" ", "_")
                raw = f.read_bytes()
                found.setdefault(iconlib.sha256_bytes(raw), []).append((numbered.group(1), name, raw))
            continue
        set_name = re.sub(r"-FilledOutline(-\d+)?$", "", d.name)
        svg_dir = d / "svg"
        if not svg_dir.is_dir():
            continue
        for f in sorted(svg_dir.iterdir()):
            raw = f.read_bytes()
            if not raw.lstrip().startswith((b"<svg", b"<?xml")):
                continue                     # .DS_Store and friends
            name = f.name[:-4] if f.name.endswith(".svg") else f.name
            found.setdefault(iconlib.sha256_bytes(raw), []).append((set_name, name, raw))
    entries, dupes = [], 0
    if (out / "icons").exists():
        shutil.rmtree(out / "icons")
    for sha, copies in found.items():
        dupes += len(copies) - 1
        keep = next((c for c in copies if f"{c[0]}/{c[1]}" == prev.get(sha)), copies[0])
        set_name, name, raw = keep
        icon_id = f"{set_name}/{name}"
        dst = out / "icons" / set_name / f"{name}.svg"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(raw)
        ic = iconlib.load(dst, icon_id)
        tags = sorted({t.lower() for t in re.split(r"[-_\s]+", name)
                       if t and t.lower() not in STOP and not t.isdigit()})
        entries.append({"id": icon_id, "set": set_name, "name": name, "sha256": sha, "view": ic.view, "tags": tags})
    entries.sort(key=lambda e: e["id"])
    lost = sorted(set(prev.values()) - {e["id"] for e in entries})
    prev_path.write_text(json.dumps(entries, indent=1) + "\n")
    print(f"✓ {len(entries)} unique icons ({dupes} byte-identical duplicates dropped) → {out / 'icons'}")
    if avatars:
        print(f"✓ {avatars} avatars → {out / 'avatars'}")
    if lost:
        print(f"  ! {len(lost)} previously indexed icons are gone: {', '.join(lost[:5])}…", file=sys.stderr)


def _line_pack(d: Path) -> list[tuple[str, str, bytes]]:
    """A "30 X Icons" pack ships Colorline (coloured strokes and fills) and Outline (black
    strokes) as separate files. Stack them, colour first and the bare outline on top, so
    icon.py reads the same filled-outline structure as the other sets."""
    base = re.sub(r"\W", "", re.fullmatch(r"30 (.+) Icons", d.name).group(1))  # type: ignore[union-attr]
    filled = {re.sub(r"-FilledOutline(-\d+)?$", "", p.name) for p in d.parent.iterdir() if "FilledOutline" in p.name}
    set_name = f"{base}Line" if base in filled else base           # Ecology → EcologyLine
    color, outline = d / "Svg" / "Expand" / "Colorline", d / "Svg" / "Expand" / "Outline"
    out, seen = [], {}
    for f in sorted(color.glob("*.svg")):
        o = outline / f.name
        if not o.exists():
            continue
        name = re.sub(r"^\d+-", "", f.stem.strip()).strip().replace(" ", "_")
        seen[name.lower()] = seen.get(name.lower(), 0) + 1
        if seen[name.lower()] > 1:
            name = f"{name}_{seen[name.lower()]}"
        inner = lambda b: re.search(rb"<svg[^>]*>(.*)</svg>", b, re.S).group(1)  # noqa: E731
        raw = (b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><g id="color">'
               + inner(f.read_bytes()) + b'</g><g id="outline">' + inner(o.read_bytes()) + b"</g></svg>\n")
        out.append((set_name, name, raw))
    return out


AVATAR_GENERIC = {"kid", "children", "avatar", "person", "youth"}


def _avatars(d: Path, out: Path) -> int:
    """Copy an avatar pack verbatim (full colour, not restyled) to avatars/ with a catalogue.
    Files are named by their tag list ("girl, kid, children, avatar, freckles.svg"); the id
    keeps the distinguishing tags: girl_freckles."""
    dst = out / "avatars"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    cat, seen = [], {}
    for f in sorted((d / "SVG").glob("*.svg")):
        tags = list(dict.fromkeys(t.strip().lower() for t in f.stem.split(",") if t.strip()))
        key = "_".join(t for t in tags if t not in AVATAR_GENERIC) or "avatar"
        seen[key] = seen.get(key, 0) + 1
        aid = key if seen[key] == 1 else f"{key}_{seen[key]}"
        raw = f.read_bytes()
        (dst / f"{aid}.svg").write_bytes(raw)
        cat.append({"id": aid, "sha256": iconlib.sha256_bytes(raw), "tags": tags})
    (dst / "avatars.json").write_text(json.dumps(cat, indent=1) + "\n")
    return len(cat)


def load_index(content: Path) -> dict[str, dict]:
    return {e["id"]: e for e in json.loads((pw(content) / "icon-index.json").read_text())}


# ── hierarchy ─────────────────────────────────────────────────────────────────────────────
def hierarchy(content: Path, subject: str) -> list[engine.Node]:
    sdir = content / "subjects" / subject
    meta = json.loads((sdir / "subject.json").read_text())
    h = json.loads((sdir / "hierarchy.json").read_text())
    sid = f"subject:{meta['code']}"
    nodes = [engine.Node(sid, "subject", subject, meta["code"], meta.get("name", subject))]
    for t in sorted(h["topics"], key=lambda t: t.get("display_order", 0)):
        if not t.get("is_active", True):
            continue
        nodes.append(engine.Node(t["id"], "topic", subject, t["code"], t["translations"]["en"]["title"], parent=sid))
        for st in sorted(t.get("subtopics", []), key=lambda s: s.get("display_order", 0)):
            if st.get("is_active", True):
                nodes.append(engine.Node(st["id"], "subtopic", subject, st["code"],
                                         st["translations"]["en"]["title"], parent=t["id"]))
    return nodes


def subjects(content: Path) -> list[str]:
    return sorted(p.name for p in (content / "subjects").iterdir() if (p / "hierarchy.json").exists())


# ── suggest: tag-overlap draft for curation ──────────────────────────────────────────────
def words(s: str) -> set[str]:
    out = set()
    for w in re.findall(r"[a-z]+", s.lower()):
        if w in STOP or len(w) < 3:
            continue
        out.add(w)
        if w.endswith("s") and len(w) > 4:
            out.add(w[:-1])
    return out


def cmd_suggest(a: argparse.Namespace) -> None:
    content = Path(a.content)
    idx = load_index(content)
    for n in hierarchy(content, a.subject):
        ws = words(n.title)
        ranked = sorted(idx.values(), key=lambda e: (-len(ws & set(e["tags"])), SET_RANK.index(e["set"]) if e["set"] in SET_RANK else 99))
        top = [e["id"] for e in ranked[:4] if ws & set(e["tags"])]
        print(f"{n.level:8} {n.code:52} {n.title[:40]:40} → {', '.join(top) or '—'}")


# ── generate ─────────────────────────────────────────────────────────────────────────────
def node_key(n: engine.Node) -> str:
    return n.id if n.level != "subject" else n.id.replace(":", "_")


def assign_icons(content: Path, subject: str, nodes: list[engine.Node], idx: dict[str, dict],
                 global_subject_icons: set[str]) -> dict[str, tuple[str, str, str]]:
    """node.id → (icon_id, how, why). Curated first, then deterministic pool picks.

    Rules: subject icons are unique across all subjects; topic/subtopic icons are unique
    within their subject (they may repeat in another subject).
    """
    mp = pw(content) / "maps" / f"{subject}.json"
    curated: dict[str, dict] = json.loads(mp.read_text()) if mp.exists() else {}
    used: set[str] = set(load_features(content).values())     # feature icons are reserved
    out: dict[str, tuple[str, str, str]] = {}

    def take(n: engine.Node, icon_id: str, how: str, why: str) -> bool:
        if icon_id not in idx or icon_id in used:
            return False
        if n.level == "subject" and icon_id in global_subject_icons:
            return False
        used.add(icon_id)
        if n.level == "subject":
            global_subject_icons.add(icon_id)
        out[n.id] = (icon_id, how, why)
        return True

    for n in nodes:                                   # pass 1: curated, in hierarchy order
        c = curated.get(n.code)
        if c and c.get("icon"):
            if not take(n, c["icon"], "curated", c.get("why", "")):
                print(f"  ! {subject} {n.code}: curated icon {c['icon']} missing or already used → pool", file=sys.stderr)
    pool = sorted(idx, key=lambda i: (SET_RANK.index(idx[i]["set"]) if idx[i]["set"] in SET_RANK else 99, i))
    for n in nodes:                                   # pass 2: pool, deterministic per node
        if n.id in out:
            continue
        h = int(hashlib.sha256(n.id.encode()).hexdigest(), 16)
        # prefer the science-adjacent head of the pool, then everything
        head = [i for i in pool[:180] if i not in used] or [i for i in pool if i not in used]
        take(n, head[h % len(head)], "pool", "")
    return out


def cmd_generate(a: argparse.Namespace) -> None:
    content = Path(a.content)
    base = pw(content)
    idx = load_index(content)
    reg = engine.Registry(base / "registry.json")
    manifest_path = base / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    subs = a.subject or subjects(content)
    global_subject_icons: set[str] = set()
    # Subject icons of subjects not being regenerated still count toward global uniqueness.
    for k, m in manifest.items():
        if m["level"] == "subject" and m["subject"] not in subs:
            global_subject_icons.add(m["icon"])
    count = 0
    for subject in subs:
        nodes = hierarchy(content, subject)     # parents always precede their children
        icons = assign_icons(content, subject, nodes, idx, global_subject_icons)
        placed: dict[str, engine.Composition] = {}
        for n in nodes:
            icon_id, how, why = icons[n.id]
            e = idx[icon_id]
            ic = iconlib.load(base / "icons" / e["set"] / f"{e['name']}.svg", icon_id)
            comp = reg.place(n, ic, placed.get(n.parent or ""))
            placed[n.id] = comp
            key = node_key(n)
            variants = {}
            for v, fn in engine.RENDERERS.items():
                svg = fn(comp)
                if not svg:
                    continue
                p = base / "out" / key / f"{v}.svg"
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(svg)
                variants[v] = {"path": f"out/{key}/{v}.svg", "sha256": iconlib.sha256_bytes(svg.encode()), "bytes": len(svg.encode())}
                if v == "wash":
                    variants[v]["ink"] = engine.wash_inks(comp)
            for old in (base / "out" / key).glob("*.svg"):
                if old.stem not in variants:     # a retired variant (v3 row) or a lost wash
                    old.unlink()
            manifest[key] = {"node_id": n.id, "parent": n.parent, "level": n.level, "subject": subject,
                             "code": n.code, "title": n.title, "patches": len(comp.styles),
                             "signature": comp.signature, "icon": icon_id, "icon_sha256": ic.sha256,
                             "how": how, "why": why, "family": comp.family, "engine_version": engine.ENGINE_VERSION,
                             "variants": variants}
            count += 1
    reg.save()
    if reg.over_budget:
        print(f"  ! {len(reg.over_budget)} nodes kept their smallest over-budget candidate", file=sys.stderr)
    manifest_path.write_text(json.dumps(dict(sorted(manifest.items())), indent=1, ensure_ascii=False) + "\n")
    contact_sheet(content, manifest)
    nf = render_features(content, idx)
    print(f"✓ {count} nodes × {len(engine.RENDERERS)} variants → {base / 'out'}" + (f", {nf} feature icons" if nf else ""))
    audit(content)


# ── features ──────────────────────────────────────────────────────────────────────────────
FEATURE_TINT = "orange.300"   # one brand accent so feature icons read as a set


def load_features(content: Path) -> dict[str, str]:
    """maps/_features.json: app feature → pack icon (picked in the icon review page).
    Reserved: no node may use a feature icon, and features never share one."""
    fp = pw(content) / "maps" / "_features.json"
    return {k: v["icon"] for k, v in json.loads(fp.read_text()).items()} if fp.exists() else {}


def render_features(content: Path, idx: dict[str, dict]) -> int:
    """out/features/<key>/{color,mono}.svg + features.json. Colour: white fills, the brand
    accent, ink outline, the icon's own square box. Mono: outline in currentColor."""
    base = pw(content)
    fp = base / "maps" / "_features.json"
    if not fp.exists():
        return 0
    feats = json.loads(fp.read_text())
    if (base / "out" / "features").exists():
        shutil.rmtree(base / "out" / "features")
    manifest = {}
    for key, f in feats.items():
        e = idx[f["icon"]]
        ic = iconlib.load(base / "icons" / e["set"] / f"{e['name']}.svg", f["icon"])
        tint = FEATURE_TINT
        colors = {**engine.ICON_COLORS_BASE, "accent": engine.C[tint],
                  "accentShade": engine.C[engine.ACCENT_SHADE.get(tint, tint)]}
        vb = f"0 0 {patterns_f(ic.view)} {patterns_f(ic.view)}"
        title = f"<title>{f.get('title', key)}</title>"
        svgs = {
            "color": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img">{title}'
                     f'{iconlib.markup(ic, colors, engine.C["patchwork.iconLine"])}</svg>\n',
            "mono": f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" fill="currentColor" role="img">{title}'
                    f'{iconlib.markup(ic, {}, engine.INK, mono=True)}</svg>\n',
        }
        variants = {}
        for v, svg in svgs.items():
            out = base / "out" / "features" / key / f"{v}.svg"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(svg)
            variants[v] = {"path": f"out/features/{key}/{v}.svg", "sha256": iconlib.sha256_bytes(svg.encode()),
                           "bytes": len(svg.encode())}
        manifest[key] = {"title": f.get("title", key), "icon": f["icon"], "icon_sha256": ic.sha256, "tint": tint,
                         "variants": variants}
    (base / "features.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n")
    return len(manifest)


def patterns_f(v: float) -> str:
    return f"{v:g}"


def contact_sheet(content: Path, manifest: dict) -> None:
    by_sub: dict[str, list[tuple[str, dict]]] = {}
    for k, m in manifest.items():
        by_sub.setdefault(m["subject"], []).append((k, m))
    parts = ['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
             '<title>Hierarchy patchworks</title><style>'
             'body{font:14px/1.4 system-ui,sans-serif;background:#FAF7F2;color:#1E1B2E;margin:0;padding:16px}'
             'h2{margin:28px 0 8px}h3{margin:18px 0 6px;font-size:15px}'
             '.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}'
             '.c{background:#fff;border-radius:14px;padding:8px;font-size:12px}.c img{width:100%;display:block}'
             '.b{display:inline-block;padding:1px 6px;border-radius:99px;font-size:10px;margin-right:4px}'
             '.curated{background:#C8E3C5}.pool{background:#FFD9C7}'
             '.t{display:flex;gap:12px;align-items:flex-start;flex-wrap:wrap}.t img.tile{width:150px}.m{color:#5b5868;font-size:11px;word-break:break-all}'
             '</style><h1>Hierarchy patchworks</h1>'
             '<p>Review the icon choice per node. Badge <span class="b curated">curated</span> = from maps/&lt;SUBJECT&gt;.json, '
             '<span class="b pool">pool</span> = deterministic fallback. Edit the map, then rerun <code>generate</code>.</p>']
    for sub in sorted(by_sub):
        items = by_sub[sub]
        subj = [m for _, m in items if m["level"] == "subject"]
        parts.append(f"<h2>{html.escape(sub)}</h2>")
        for k, m in [(k, m) for k, m in items if m["level"] == "subject"]:
            parts.append(_card(k, m, wide=True))
        topics = [(k, m) for k, m in items if m["level"] == "topic"]
        subs_by_topic: dict[str, list] = {}
        h = json.loads((content / "subjects" / sub / "hierarchy.json").read_text())
        parent = {st["id"]: t["id"] for t in h["topics"] for st in t.get("subtopics", [])}
        for k, m in items:
            if m["level"] == "subtopic":
                subs_by_topic.setdefault(parent.get(m["node_id"], ""), []).append((k, m))
        for k, m in topics:
            parts.append(f'<h3>{html.escape(m["title"])}</h3>{_card(k, m, wide=True)}<div class="g">')
            parts.extend(_card(sk, sm) for sk, sm in subs_by_topic.get(m["node_id"], []))
            parts.append("</div>")
        del subj
    (pw(content) / "index.html").write_text("".join(parts))


def _card(k: str, m: dict, wide: bool = False) -> str:
    badge = f'<span class="b {m["how"]}">{m["how"]}</span>'
    meta = f'<div>{badge}<b>{html.escape(m["title"])}</b></div><div class="m">{html.escape(m["code"])} · {html.escape(m["icon"])}</div>'
    if wide:    # subjects and topics: tile + meta + wash + mono
        return (f'<div class="t"><img class="tile" src="out/{k}/tile.svg" alt=""><div style="flex:1;min-width:260px">'
                f'{meta}</div>' +
                (f'<img src="out/{k}/wash.svg" width="64" alt="" style="color:#1E1B2E;background:#fff">' if "wash" in m["variants"] else "") +
                f'<img src="out/{k}/mono.svg" width="28" alt=""></div>')
    return f'<div class="c"><img src="out/{k}/tile.svg" alt="">{meta}</div>'


# ── demo (public, licence-safe) ───────────────────────────────────────────────────────
DEMO_NODES = [  # (id, level, subject family key, title, Phosphor glyph, parent id) — parents first
    ("demo:physics", "subject", "PHYSICS", "Physics", "atom", None),
    ("demo:chemistry", "subject", "CHEMISTRY", "Chemistry", "flask", None),
    ("demo:biology", "subject", "BIOLOGY", "Biology", "dna", None),
    ("demo:maths", "subject", "MATHS", "Combined Maths", "function", None),
    ("demo:ict", "subject", "ICT", "ICT", "cpu", None),
    ("demo:languages", "subject", "LANGUAGES", "Languages", "translate", None),
    ("demo:waves", "topic", "PHYSICS", "Oscillations and waves", "wave-sine", "demo:physics"),
    ("demo:magnetism", "topic", "PHYSICS", "Magnetic field", "magnet", "demo:physics"),
    ("demo:current", "subtopic", "PHYSICS", "Electromagnetic induction", "lightning", "demo:magnetism"),
    ("demo:thermal", "subtopic", "PHYSICS", "Thermal waves", "thermometer", "demo:waves"),
    ("demo:kinetics", "topic", "CHEMISTRY", "Chemical kinetics", "test-tube", "demo:chemistry"),
    ("demo:plants", "topic", "BIOLOGY", "Plant form and function", "plant", "demo:biology"),
    ("demo:leaf", "subtopic", "BIOLOGY", "Leaf structure", "leaf", "demo:plants"),
    ("demo:cells", "subtopic", "BIOLOGY", "Plant cells", "microscope", "demo:plants"),
    ("demo:circulation", "subtopic", "BIOLOGY", "Water transport", "heartbeat", "demo:plants"),
]


def cmd_demo(a: argparse.Namespace) -> None:
    """Patchworks from MIT Phosphor glyphs + one swatch per pattern → assets/v3/patchwork-demo/."""
    from . import patterns
    root = Path(__file__).resolve().parents[2]
    out = root / "assets/v3/patchwork-demo"
    if out.exists():
        shutil.rmtree(out)
    glyphs = Path(__file__).resolve().parent / "demo-icons"
    reg = engine.Registry()
    placed: dict[str, engine.Composition] = {}
    for nid, level, subject, title, glyph, parent in DEMO_NODES:
        ic = iconlib.load(glyphs / f"{glyph}.svg", f"phosphor/{glyph}")
        comp = reg.place(engine.Node(nid, level, subject, nid, title, parent), ic, placed.get(parent or ""))
        placed[nid] = comp
        for v, fn in engine.RENDERERS.items():
            svg = fn(comp)
            if not svg:
                continue
            p = out / f"{nid.split(':')[1]}-{v}.svg"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(svg)
    tints = ["coral.300", "butter.300", "sage.300", "sky.300", "violet.100", "orange.300", "blush.300", "sand.300"]
    for i, name in enumerate(patterns.PATTERNS):
        tint = engine.C[tints[i % len(tints)]]
        ink = engine.mix(tint, engine.INK, 0.42)
        body = patterns.render(name, (0, 0, 96, 96), 1, 0, ink, 0.6)
        (out / f"pattern-{name}.svg").write_text(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 96 96" width="96" height="96" role="img">'
            f'<title>{name}</title><defs><clipPath id="c"><rect width="96" height="96" rx="16"/></clipPath></defs>'
            f'<g clip-path="url(#c)"><rect width="96" height="96" fill="{tint}"/>{body}</g>'
            f'<rect x="1" y="1" width="94" height="94" rx="15" fill="none" stroke="{engine.INK}" stroke-width="2"/></svg>\n')
    print(f"✓ {len(DEMO_NODES)} demo nodes × {len(engine.RENDERERS)} variants + {len(patterns.PATTERNS)} pattern swatches → "
          f"{out.relative_to(root)}")


# ── audit ────────────────────────────────────────────────────────────────────────────────
def audit(content: Path) -> None:
    base = pw(content)
    manifest = json.loads((base / "manifest.json").read_text())
    reg = json.loads((base / "registry.json").read_text())
    errors: list[str] = []
    keys = [reg["nodes"][m["node_id"]]["key"] for m in manifest.values()]
    if len(set(keys)) != len(keys):
        errors.append("duplicate composition keys")
    subj_icons = [m["icon"] for m in manifest.values() if m["level"] == "subject"]
    if len(set(subj_icons)) != len(subj_icons):
        errors.append("subject icons not globally unique")
    per_sub: dict[str, list[str]] = {}
    for m in manifest.values():
        per_sub.setdefault(m["subject"], []).append(m["icon"])
    for s, ics in per_sub.items():
        if len(set(ics)) != len(ics):
            errors.append(f"{s}: icons repeat within subject")
    feats = load_features(content)
    if len(set(feats.values())) != len(feats):
        errors.append("feature icons repeat")
    clash = sorted(set(feats.values()) & {m["icon"] for m in manifest.values()})
    if clash:
        errors.append(f"feature icons also used by nodes: {clash[:3]}")
    for k, m in manifest.items():
        for v, info in m["variants"].items():
            svg = (base / info["path"]).read_text()
            if v in engine.BUDGET and info["bytes"] > engine.BUDGET[v]:
                errors.append(f"{k}/{v}: {info['bytes']} B over budget")
            if re.search(r"<(pattern|filter|image|mask|radialGradient)\b", svg):
                errors.append(f"{k}/{v}: forbidden element")
    total = sum(i["bytes"] for m in manifest.values() for i in m["variants"].values())
    curated = sum(1 for m in manifest.values() if m["how"] == "curated")
    print(f"audit: {len(manifest)} nodes, {len(set(keys))} unique keys, {curated} curated / {len(manifest) - curated} pool, "
          f"{total / 1e6:.1f} MB total — {'OK' if not errors else 'FAIL'}")
    for e in errors:
        print("  ✗", e)
    if errors:
        sys.exit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("index"); p.add_argument("--icons", required=True); p.add_argument("--content", required=True)
    p = sp.add_parser("suggest"); p.add_argument("--content", required=True); p.add_argument("--subject", required=True)
    p = sp.add_parser("generate"); p.add_argument("--content", required=True); p.add_argument("--subject", action="append")
    p = sp.add_parser("audit"); p.add_argument("--content", required=True)
    sp.add_parser("demo")
    a = ap.parse_args()
    {"index": cmd_index, "suggest": cmd_suggest, "generate": cmd_generate, "demo": cmd_demo,
     "audit": lambda a: audit(Path(a.content))}[a.cmd](a)


if __name__ == "__main__":
    main()
