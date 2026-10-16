"""python -m pytest scripts/patchwork  (from the DS repo root, venv with fonttools + pytest)"""
from __future__ import annotations

import random
import re
import uuid

from patchwork import engine, patterns


def nodes(n: int, seed: int = 7) -> list[engine.Node]:
    rng = random.Random(seed)
    subjects = ["PHYSICS", "CHEMISTRY", "BIOLOGY", "ICT"]
    return [engine.Node(str(uuid.UUID(int=rng.getrandbits(128))), "subtopic", rng.choice(subjects)) for _ in range(n)]


def test_deterministic_bytes():
    node = nodes(1)[0]
    a, b = engine.compose(node, None), engine.compose(node, None)
    for v in ("tile", "row", "corner"):
        assert engine.RENDERERS[v](a) == engine.RENDERERS[v](b)


def test_signature_depends_on_icon_checksum():
    node = nodes(1)[0]
    assert engine.signature(node, "a" * 64) != engine.signature(node, "b" * 64)


def test_registry_keys_unique_and_reproducible(tmp_path):
    reg = engine.Registry(tmp_path / "r.json")
    ns = nodes(1500)
    comps = [reg.place(n, None) for n in ns]
    keys = [c.key() for c in comps]
    assert len(set(keys)) == len(keys)
    reg.save()
    again = engine.Registry(tmp_path / "r.json")
    for n, c in zip(ns[:50], comps[:50]):
        assert again.place(n, None).key() == c.key()


def test_no_forbidden_svg():
    for node in nodes(40, seed=3):
        comp = engine.compose(node, None)
        for v in ("tile", "row", "corner"):
            svg = engine.RENDERERS[v](comp)
            assert not re.search(r"<(pattern|filter|image|linearGradient|radialGradient)\b", svg)


def test_all_patterns_render():
    for name in patterns.PATTERNS:
        for angle in patterns.ANGLES:
            assert "<path" in patterns.render(name, (0, 0, 100, 80), 1, angle, "#000000")
