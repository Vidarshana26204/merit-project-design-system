"""Round 12 auth frames. Stub until its agent fills it; must not import gen_web_board (circular)."""
from gen_web import *  # noqa: F401,F403

_p = lambda sid, t: kit_screen(sid, t + " (round 12 in progress)", [("gap", "Pending")], "Being rebuilt.", "", [])
s_auth = _p("web-auth", "Auth & onboarding")
