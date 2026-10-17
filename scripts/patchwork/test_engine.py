"""python -m pytest scripts/patchwork  (from the DS repo root, venv with fonttools + pytest)"""
from __future__ import annotations

import random
import re
import uuid

from patchwork import engine, geometry, patterns


def uid(rng: random.Random) -> str:
    return str(uuid.UUID(int=rng.getrandbits(128)))


def tree(seed: int = 7, subjects: int = 3, topics: int = 8, subtopics: int = 12) -> list[engine.Node]:
    """Parents precede children, like build.hierarchy()."""
    rng = random.Random(seed)
    out: list[engine.Node] = []
    for s in range(subjects):
        sid = f"subject:S{s}"
        out.append(engine.Node(sid, "subject", ["PHYSICS", "CHEMISTRY", "BIOLOGY"][s % 3]))
        for _ in range(topics):
            tid = uid(rng)
            out.append(engine.Node(tid, "topic", out[-1].subject if out[-1].level == "subject" else out[0].subject, parent=sid))
            for _ in range(subtopics):
                out.append(engine.Node(uid(rng), "subtopic", out[-1].subject, parent=tid))
    return out


def place_all(nodes: list[engine.Node], reg: engine.Registry) -> dict[str, engine.Composition]:
    placed: dict[str, engine.Composition] = {}
    for n in nodes:
        placed[n.id] = reg.place(n, None, placed.get(n.parent or ""))
    return placed


def test_patch_counts_and_inheritance():
    placed = place_all(tree(), engine.Registry())
    for n in tree():
        c = placed[n.id]
        assert len(c.styles) == engine.LEVEL_PATCHES[n.level] == len(c.rays)
        if n.parent:
            p = placed[n.parent]
            kept = c.styles[:c.added] + c.styles[c.added + 1:]
            assert kept == p.styles, "child keeps the parent's patches in order"
            assert c.styles[c.added].pattern not in {s.pattern for s in p.styles if s.pattern}


def test_every_patch_touches_the_centre():
    placed = place_all(tree(subjects=1, topics=2, subtopics=3), engine.Registry())
    for c in placed.values():
        for w, h in ((engine.TILE, engine.TILE), (engine.ROW_W, engine.ROW_H)):
            for p in c.layout(w, h).patches:
                assert p.poly[0] == (w / 2, h / 2)
                assert p.area > 0


def test_keys_unique_and_siblings_add_different_patches(tmp_path):
    reg = engine.Registry(tmp_path / "r.json")
    nodes = tree()
    placed = place_all(nodes, reg)
    keys = [c.key() for c in placed.values()]
    assert len(set(keys)) == len(keys)
    by_parent: dict[str, list[str]] = {}
    for n in nodes:
        if n.parent:
            by_parent.setdefault(n.parent, []).append(placed[n.id].added_key())
    for added in by_parent.values():
        assert len(set(added)) == len(added)
    reg.save()
    again = place_all(nodes[:40], engine.Registry(tmp_path / "r.json"))
    for n in nodes[:40]:
        assert again[n.id].key() == placed[n.id].key()


def test_deterministic_bytes():
    n = engine.Node("subject:X", "subject", "PHYSICS")
    a, b = engine.compose(n, None), engine.compose(n, None)
    for v in ("tile", "row", "wash"):
        assert engine.RENDERERS[v](a) == engine.RENDERERS[v](b)


def test_signature_depends_on_icon_checksum():
    n = engine.Node("x", "topic", "PHYSICS")
    assert engine.signature(n, "a" * 64) != engine.signature(n, "b" * 64)


def test_no_forbidden_svg():
    placed = place_all(tree(subjects=1, topics=3, subtopics=3), engine.Registry())
    for c in placed.values():
        for v in ("tile", "row", "wash"):
            svg = engine.RENDERERS[v](c)
            assert not re.search(r"<(pattern|filter|image|mask|radialGradient)\b", svg)
            if v == "tile":   # v3: no ink seams, one blend gradient per ray
                assert svg.count("<linearGradient") == len(c.rays)
                assert svg.count(f'stroke-width="{engine.SEAM}"') == 1   # the plate only


def test_children_add_a_pattern_and_get_a_wash():
    placed = place_all(tree(subjects=1, topics=3, subtopics=3), engine.Registry())
    for c in placed.values():
        if c.node.level == "subject":
            assert engine.render_wash(c) == ""
        else:
            assert c.styles[c.added].pattern
            assert "currentColor" in engine.render_wash(c)


def test_morph_dissolves_toward_seams():
    ks = [patterns.smoothstep(engine.MORPH * 0.15, engine.MORPH, d) for d in range(0, 30, 2)]
    assert ks[0] == 0 and ks[-1] == 1 and ks == sorted(ks)


def test_all_patterns_render():
    for name in patterns.PATTERNS:
        for angle in patterns.ANGLES:
            assert "<path" in patterns.render(name, (0, 0, 100, 80), 1, angle, "#000000")


def test_radial_layout_covers_frame():
    for rays in ([0, 24, 48, 72], [5, 20, 41, 60, 77, 90]):
        for w, h in ((256.0, 256.0), (1024.0, 256.0)):
            total = sum(p.area for p in geometry.radial_layout(rays, w, h).patches)
            assert abs(total - w * h) < 1e-6 * w * h
