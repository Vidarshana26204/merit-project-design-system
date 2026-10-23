"""Round 12 hub frames. Stub until its agent fills it; must not import gen_web_board (circular)."""
from gen_web import *  # noqa: F401,F403

_p = lambda sid, t: kit_screen(sid, t + " (round 12 in progress)", [("gap", "Pending")], "Being rebuilt.", "", [])
s_hub = _p("web-hub", "Student portal · subject hub")
s_subj = _p("web-subjects-more", "Subjects · more")
