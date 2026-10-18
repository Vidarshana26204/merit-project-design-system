"""python -m pytest scripts/patchwork  (from the DS repo root, venv with fonttools + pytest)"""
from __future__ import annotations

import dataclasses
import random
import re
import uuid

from patchwork import engine, geometry, palette, patterns


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
        assert len(c.styles) == engine.LEVEL_PATCHES[n.level] == len(c.layout().patches)
        if n.parent:
            p = placed[n.parent]
            assert c.added == len(p.styles) and c.styles[:-1] == p.styles, "child nests one patch inside its parent's"
            assert c.styles[c.added].pattern not in {s.pattern for s in p.styles if s.pattern}


def test_plate_shape_follows_level():
    placed = place_all(tree(subjects=1, topics=1, subtopics=1), engine.Registry())
    assert {c.node.level: c.plate for c in placed.values()} == {"subject": "square", "topic": "pentagon", "subtopic": "hexagon"}
    for c in placed.values():                            # sides = patches
        assert geometry.PLATE_SIDES[c.plate] == len(c.styles)


def test_subject_colour_drives_the_whole_branch():
    nodes = [dataclasses.replace(n, color="#10B981") for n in tree(subjects=1, topics=2, subtopics=3)]
    pal = palette.palette("#10B981")
    allowed = set(pal.tints) | set(pal.solids)
    placed = place_all(nodes, engine.Registry())
    for c in placed.values():
        assert c.family == "#10B981"
        assert {s.tint for s in c.styles} <= allowed
        assert (c.accent, c.accent_shade) in pal.accents
    other = place_all([dataclasses.replace(n, color="#EF4444") for n in nodes], engine.Registry())
    n0 = nodes[0].id
    assert other[n0].signature != placed[n0].signature   # a colour change re-signs every node


def test_palette_round_trips_and_stays_in_gamut():
    for h in ("#EF4444", "#10B981", "#0EA5E9", "#F43F5E", "#3B82F6", "#663696", "#808080"):
        assert palette.from_oklch(*palette.to_oklch(h)) == h
        pal = palette.palette(h)
        assert len(pal.tints) >= 6 and pal.solids and len(pal.accents) == 3
        for t in pal.tints:                               # tints stay light enough for ink patterns
            assert palette.to_oklch(t)[0] > 0.84
    assert palette.palette("#EF4444").solids[0] == "#EF4444"   # a mid-light subject colour is used as is


def test_touching_patches_never_share_a_tint():
    placed = place_all(tree(), engine.Registry())
    for c in placed.values():
        tints = [s.tint for s in c.styles]
        assert len(set(tints[:4])) == 4                  # the subject's four roles all touch
        for role, near in geometry.NEIGHBOURS.items():
            if role < len(tints):
                assert tints[role] not in {tints[r] for r in near}


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
    for v in engine.RENDERERS:
        assert engine.RENDERERS[v](a) == engine.RENDERERS[v](b)


def test_signature_depends_on_icon_checksum():
    n = engine.Node("x", "topic", "PHYSICS")
    assert engine.signature(n, "a" * 64) != engine.signature(n, "b" * 64)


def test_no_forbidden_svg():
    placed = place_all(tree(subjects=1, topics=3, subtopics=3), engine.Registry())
    for c in placed.values():
        assert "row" not in engine.RENDERERS
        for v in ("tile", "wash"):
            svg = engine.RENDERERS[v](c)
            assert not re.search(r"<(pattern|filter|image|mask|radialGradient|linearGradient)\b", svg)
            if v == "tile":   # no ink seams: the plate is the only seam-weight stroke
                assert svg.count(f'stroke-width="{engine.SEAM}"') == 1


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


def test_layout_is_symmetric_and_nested():
    s = 256.0
    for n in (4, 5, 6, 7):
        lay = geometry.square_in_square(n, s)
        assert sorted(p.role for p in lay.patches) == list(range(n))
        assert abs(sum(p.area for p in lay.patches[:2]) - s * s) < 1e-6      # the X tiles the square
        pts = {p.role: {(round(x, 6), round(y, 6)) for poly in p.polys for x, y in poly} for p in lay.patches}
        for role, ps in pts.items():                                          # half-turn symmetric
            assert ps == {(round(s - x, 6), round(s - y, 6)) for x, y in ps}
        assert pts[3] == {(round(s - x, 6), y) for x, y in pts[2]}                      # corner pairs mirror
    # each level's new shape sits inside the frame and is visible outside the plate
    for kind in ("hexagon", "pentagon", "square"):
        assert geometry.plate_inradius(kind, s) < s * geometry.SQUARE
