"""Snapshot real past-paper questions and flashcards for the landing's live sections (round 13), plus the rules,
plans and FSRS intervals the round 14 sections quote.

Usage (from the design-system repo root):
    python3 wireframes/build_samples.py [--db merit_rehearsal] > /dev/null   # writes wireframes/qm-samples.js

Read-only: SELECTs against the rehearsal DB (the most recent subject data). Keeps only text-only content, single-answer
past-paper questions with both an English and a Sinhala translation, so the widget can toggle EN / SI. The order is a
stable pseudo-random (md5 of the id), so a rerun picks the same set. Also computes the facts the FAQ quotes
(paper years, counts) so the copy never claims more than the data has. Production reads GET /public/samples instead.

Round 14: `rules` is system_settings (what GET /public/plans will serve as `rules` and tier limits), `plans` is the tiers
table plus the Gate 0 prices (tiers has no price columns yet; Phase B adds display_price_lkr, edited in admin), and
`fsrs` holds intervals produced by the backend's own engine (service.newFsrsEngine, Flutter-parity weights) at the
configured retention. Python cannot run go-fsrs, so FSRS_* below are pasted from a one-off probe; rerun the probe
(see HANDOFF) if the weights or flashcard_request_retention change.
"""
import argparse
import json
import os
import subprocess
import sys

Q_PER_SUBJECT = 8
F_PER_SUBJECT = 15

SUBJECTS = """
select s.id, s.code, st.title, s.color_hex
from subjects s join subject_translations st on st.subject_id = s.id and st.language = 'en'
where s.is_active
"""

QUESTIONS = """
select coalesce(json_agg(r), '[]') from (
  select q.id, q.correct_option as ok, q.paper_question_number as n, ep.year, t.subject_id as subject, tt.title as topic,
         en.content as en_q, en.options as en_o, en.explanation as en_x,
         si.content as si_q, si.options as si_o, si.explanation as si_x
  from questions q
  join exam_papers ep on ep.id = q.exam_paper_id
  join subtopics sb on sb.id = q.subtopic_id
  join topics t on t.id = sb.topic_id
  join topic_translations tt on tt.topic_id = t.id and tt.language = 'en'
  join question_translations en on en.question_id = q.id and en.language = 'en'
  join question_translations si on si.question_id = q.id and si.language = 'si'
  where q.is_active and q.source = 'past_paper' and q.image_url is null and q.question_type = 'mcq'
    and (q.correct_options is null or cardinality(q.correct_options) <= 1)
    and t.subject_id = '{sid}'
  order by (en.explanation is null), md5(q.id::text)  -- explained questions first (no SI explanations exist yet)
  limit 300
) r
"""

FLASHCARDS = """
select coalesce(json_agg(r), '[]') from (
  select f.id, tt.title as topic, ft.front_content as front, ft.back_content as back
  from flashcards f
  join subtopics sb on sb.id = f.subtopic_id
  join topics t on t.id = sb.topic_id
  join topic_translations tt on tt.topic_id = t.id and tt.language = 'en'
  join flashcard_translations ft on ft.flashcard_id = f.id and ft.language = 'en'
  where f.is_active and f.front_image_url is null and f.back_image_url is null and t.subject_id = '{sid}'
  order by md5(f.id::text)
  limit 200
) r
"""

RULES = "select row_to_json(s) from system_settings s where id = 1"
TIERS = "select coalesce(json_agg(t order by t.id), '[]') from tiers t"

# qm-samples.js is public (this repo is public). Only the keys GET /public/plans will serve leave the DB; a new
# system_settings column stays private until it is added here on purpose.
PUBLIC_RULES = (
    "free_mastery_daily_limit", "free_paper_daily_limit",
    "free_enrollment_limit_al", "free_enrollment_limit_ol", "pro_enrollment_limit_al", "pro_enrollment_limit_ol",
    "points_per_correct_answer", "accuracy_bonus_threshold", "accuracy_bonus_points", "pro_multiplier",
    "mastery_completion_threshold", "progression_unlock_reward",
    "force_unlock_base_cost", "force_unlock_cost_increment", "force_unlock_burn_pct",
    "mastery_weight_quiz", "mastery_weight_notes", "mastery_weight_flashcard",
    "flashcard_session_points", "flashcard_daily_points_cap", "flashcard_request_retention", "note_completion_points",
)
PUBLIC_TIER = ("id", "code", "duration_days", "is_trial")

# Gate 0 (2026-10-23): owner-set launch prices. Moves to tiers.display_price_lkr in Phase B.
PRICES_LKR = {"PRO_MONTHLY": 599, "PRO_ANNUAL": 4990}
# go-fsrs v4 via service.newFsrsEngine(0.9, fuzz off), probe run 2026-10-23. Seconds.
FSRS_NEW = {"again": 60, "hard": 360, "good": 600, "easy": 16 * 86400}
FSRS_GOOD_LADDER = [600, 4 * 86400, 14 * 86400, 45 * 86400, 135 * 86400, 372 * 86400]  # "Good" every time, reviewed when due
FSRS_STABILITY = [3.26, 3.54, 13.73, 45.23, 134.55, 371.88]  # days, after each of those reviews

FACTS = """
select coalesce(json_agg(r), '[]') from (
  select ep.subject_id as subject, min(ep.year) as y0, max(ep.year) as y1, count(distinct q.id) as questions
  from questions q join exam_papers ep on ep.id = q.exam_paper_id
  where q.is_active and q.source = 'past_paper'
  group by ep.subject_id
) r
"""


def sql(db, query):
    out = subprocess.run(["psql", "-d", db, "-AtX", "-v", "ON_ERROR_STOP=1", "-c", query], capture_output=True, text=True)
    if out.returncode:
        sys.exit("psql failed: " + out.stderr.strip())
    return out.stdout.strip()


def text(blocks):
    """Joined text of a content block list, or None when any block is not plain text (tables, images, lists)."""
    if not blocks:
        return None
    if any(b.get("type") != "text" for b in blocks):
        return None
    s = " ".join(b.get("value", "").strip() for b in blocks).strip()
    return s or None


def options(opts):
    out = []
    for o in sorted(opts or [], key=lambda o: o.get("option_number", 0)):
        t = text(o.get("content"))
        if t is None:
            return None
        out.append(t)
    return out if len(out) >= 4 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="merit_rehearsal")
    db = ap.parse_args().db
    subjects = {}
    for line in sql(db, SUBJECTS).splitlines():
        sid, code, title, color = line.split("|")
        subjects[sid] = {"id": sid, "code": code, "t": title, "c": color}

    qs, cards = [], []
    for sid, s in subjects.items():
        picked = 0
        for r in json.loads(sql(db, QUESTIONS.format(sid=sid))):
            en, si = [text(r["en_q"]), options(r["en_o"])], [text(r["si_q"]), options(r["si_o"])]
            if None in en or None in si or len(en[1]) != len(si[1]) or not 1 <= r["ok"] <= len(en[1]):
                continue
            qs.append({"id": r["id"], "s": sid, "topic": r["topic"], "year": r["year"], "n": r["n"], "ok": r["ok"],
                       "en": {"q": en[0], "o": en[1], "x": text(r["en_x"])}, "si": {"q": si[0], "o": si[1], "x": text(r["si_x"])}})
            picked += 1
            if picked == Q_PER_SUBJECT:
                break
        got = 0
        for r in json.loads(sql(db, FLASHCARDS.format(sid=sid))):
            f, b = text(r["front"]), text(r["back"])
            if not f or not b or len(f) > 160 or len(b) > 260:
                continue
            cards.append({"id": r["id"], "s": sid, "topic": r["topic"], "f": f, "b": b})
            got += 1
            if got == F_PER_SUBJECT:
                break

    facts = {f["subject"]: f for f in json.loads(sql(db, FACTS))}
    used = sorted({q["s"] for q in qs} | {c["s"] for c in cards}, key=lambda i: subjects[i]["t"])
    out = {
        "source": db,
        "subjects": [dict(subjects[i], q=sum(q["s"] == i for q in qs), f=sum(c["s"] == i for c in cards),
                          y0=facts.get(i, {}).get("y0"), y1=facts.get(i, {}).get("y1"), pq=facts.get(i, {}).get("questions", 0)) for i in used],
        "questions": qs,
        "flashcards": cards,
    }
    row = json.loads(sql(db, RULES))
    rules = {k: row[k] for k in PUBLIC_RULES}
    tiers = [{k: t[k] for k in PUBLIC_TIER} for t in json.loads(sql(db, TIERS))]
    for t in tiers:
        t["price_lkr"] = PRICES_LKR.get(t["code"])
    out["rules"] = rules
    out["plans"] = tiers
    out["fsrs"] = {"retention": rules["flashcard_request_retention"], "new": FSRS_NEW, "good_ladder": FSRS_GOOD_LADDER,
                   "stability_days": FSRS_STABILITY, "decay": -0.5, "factor": 19 / 81}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "qm-samples.js")
    with open(path, "w") as fh:
        fh.write("/* Real past-paper questions (EN + SI) and flashcards for the landing's live sections. Generated by build_samples.py from "
                 + db + " (read-only). Do not edit by hand. */\nwindow.QM_SAMPLES = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";\n")
    for s in out["subjects"]:
        print(f'{s["t"]:<28} questions {s["q"]:>2}  cards {s["f"]:>2}  papers {s["y0"]}-{s["y1"]} ({s["pq"]} past-paper questions)', file=sys.stderr)
    print(f"wrote {path} ({os.path.getsize(path) // 1024} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
