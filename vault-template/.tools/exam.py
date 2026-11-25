#!/usr/bin/env python3
"""Does the brain find what you know is in it? A small exam, scored.

    python3 .tools/exam.py                       # run the exam: how many found, which missed
    python3 .tools/exam.py --record              # also keep the score and compare with last time
    python3 .tools/exam.py add "who checks the contract?" --terms "lawyer contract" \\
                               --expect 30-knowledge/people/Jane-Doe.md
    python3 .tools/exam.py --backend qmd         # same exam against qmd, to compare (optional)

(Windows: `py -3`.) "Works for me" is not a measurement. A vault answers
questions by first FINDING the right note, and that step fails silently: a
renamed note, a capture filed without the word you would search for, a
search change that ranks a log above the note it mentions — the answer is
then built on the wrong page, and it still sounds confident.

So every question here has three parts: the question as the person would
ask it, the terms an agent would search for (that is how `brain-ask` uses
`search.py`), and the note that must come out. The exam runs those terms
through the very ranking an agent gets (`search.py`'s `rank`) and counts a
question as answered when the expected note is among the first three.

Two numbers, both honest about what they are:
  found in top 3    the share of questions an agent would answer from the
                    right note on its first read
  MRR               mean reciprocal rank: 1.0 when the note is always
                    first, 0.5 when it is always second, 0 when missing

A question whose expected note no longer exists is reported as STALE, not
as a miss: the note moved, and the exam needs updating — counting it as a
search failure would blame the search for a rename.

The questions live in `.tools/exam.json`, part of the brain and committed
with it. The weekly review proposes one or two new ones from what was filed
that week; the person keeps or drops them. No model call, no network, no
cost. Python standard library only. Works on macOS, Windows and Linux.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
EXAM = VAULT / ".tools" / "exam.json"
HISTORY = VAULT / ".tools" / "logs" / "exam-history.tsv"
TOP = 3          # "answered" = in the first three an agent reads
DEPTH = 10       # ranks beyond this count as not found


def utf8_stdout():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def load():
    try:
        data = json.loads(EXAM.read_text(encoding="utf-8"))
        return data.get("questions", []) if isinstance(data, dict) else []
    except (OSError, ValueError):
        return []


def save(questions):
    EXAM.write_text(json.dumps({"questions": questions}, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def norm(rel):
    """One spelling per path. macOS stores `ö` in file names decomposed (o +
    combining diaeresis, NFD) while a typed question holds it composed (NFC):
    identical on screen, different as strings. Measured on a real vault —
    `Französisch-Problem.md` came second in the ranking and still counted as
    not found."""
    return unicodedata.normalize("NFC", rel.replace("\\", "/"))


# ----------------------------------------------------------------- backends
def search_backend():
    spec = importlib.util.spec_from_file_location("brain_search", VAULT / ".tools" / "search.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def ranked(terms):
        return [norm(rel) for _, rel, _ in mod.rank(str(VAULT), terms.split())]
    return "search.py", ranked


def qmd_backend(mode, collection):
    """tobi/qmd (MIT) as a comparison: `search` is its keyword mode and needs
    nothing extra; `query` adds embeddings and re-ranking (downloads ~2 GB of
    local models on first use). It ranks its own index of the vault, so the
    collection must exist: `qmd collection add <vault> --name brain`."""
    exe = shutil.which("qmd")
    if not exe:
        raise SystemExit("qmd is not installed — `npm install -g @tobilu/qmd`, then "
                         "`qmd collection add <this vault> --name brain` (and `qmd embed` for `query`).")

    def ranked(terms):
        r = subprocess.run([exe, mode, terms, "--json", "-n", str(DEPTH), "-c", collection, "--full-path"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        try:
            hits = json.loads(r.stdout or "[]")
        except ValueError:
            raise SystemExit(f"qmd gave no JSON: {(r.stderr or r.stdout).strip()[:200]}")
        out = []
        for h in hits if isinstance(hits, list) else hits.get("results", []):
            f = str(h.get("file", ""))
            try:
                out.append(norm(str(Path(f).resolve().relative_to(VAULT.resolve()))))
            except ValueError:
                out.append(norm(f))
        return out
    return f"qmd {mode}", ranked


# --------------------------------------------------------------------- exam
def run_exam(ranked):
    results = []
    for q in load():
        expect = [norm(e) for e in q.get("expect", [])]
        if not expect or not q.get("terms"):
            continue
        if not any((VAULT / e).exists() for e in expect):
            results.append(dict(q=q, rank=None, stale=True, top=[]))
            continue
        hits = ranked(q["terms"])[:DEPTH]
        rank = next((i + 1 for i, rel in enumerate(hits) if rel in expect), None)
        results.append(dict(q=q, rank=rank, stale=False, top=hits[:TOP]))
    return results


def summary(results):
    live = [r for r in results if not r["stale"]]
    found = sum(1 for r in live if r["rank"] and r["rank"] <= TOP)
    mrr = sum(1 / r["rank"] for r in live if r["rank"]) / len(live) if live else 0.0
    return len(live), found, round(mrr, 2), len(results) - len(live)


def last_record(backend):
    try:
        rows = [l.split("\t") for l in HISTORY.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    except OSError:
        return None
    rows = [r for r in rows if len(r) >= 5 and r[4] == backend]
    return rows[-1] if rows else None


def record(n, found, mrr, backend):
    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY.exists():
        HISTORY.write_text("date\tquestions\tfound_top3\tmrr\tbackend\n", encoding="utf-8")
    with open(HISTORY, "a", encoding="utf-8") as fh:
        fh.write(f"{dt.date.today().isoformat()}\t{n}\t{found}\t{mrr}\t{backend}\n")


def cmd_exam(a):
    if a.backend == "search":
        backend, ranked = search_backend()
    else:
        backend, ranked = qmd_backend(a.qmd_mode, a.collection)
    if not load():
        print("exam: no questions yet — the weekly review proposes them, or add one:\n"
              "  python3 .tools/exam.py add \"<question>\" --terms \"<search terms>\" --expect <note path>")
        return 0
    results = run_exam(ranked)
    n, found, mrr, stale = summary(results)
    line = f"exam ({backend}): {found} of {n} found in the top {TOP} · MRR {mrr}"
    if stale:
        line += f" · {stale} stale"
    previous = last_record(backend) if a.record else None
    print(line)
    for r in results:
        q = r["q"]
        if r["stale"]:
            print(f"  STALE  \"{q['terms']}\" — {', '.join(q['expect'])} no longer exists: update or drop the question")
        elif not r["rank"] or r["rank"] > TOP:
            where = f"rank {r['rank']}" if r["rank"] else f"not in the top {DEPTH}"
            print(f"  MISSED \"{q['terms']}\" → {q['expect'][0]} at {where}; first: {', '.join(r['top']) or '-'}")
    if a.record:
        record(n, found, mrr, backend)
        if previous:
            pn, pf = int(previous[1]), int(previous[2])
            before, now = pf / pn if pn else 0, found / n if n else 0
            verdict = "WORSE than" if now < before else "better than" if now > before else "same as"
            print(f"  {verdict} {previous[0]} ({pf} of {pn})")
    return 0


def cmd_add(a):
    expect = [norm(e) for e in a.expect]
    missing = [e for e in expect if not (VAULT / e).exists()]
    if missing:
        print(f"refused: {', '.join(missing)} does not exist in this vault (paths are relative to its root)")
        return 1
    questions = load()
    if any(q.get("terms") == a.terms and q.get("expect") == expect for q in questions):
        print("already in the exam")
        return 0
    questions.append({"q": a.question, "terms": a.terms, "expect": expect,
                      "added": dt.date.today().isoformat()})
    save(questions)
    _, ranked = search_backend()
    hits = ranked(a.terms)[:DEPTH]
    rank = next((i + 1 for i, rel in enumerate(hits) if rel in expect), None)
    print(f"added ({len(questions)} questions). Today: " + (f"rank {rank}" if rank else f"not in the top {DEPTH}"))
    return 0


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--record", action="store_true", help="keep the score in .tools/logs/exam-history.tsv")
    ap.add_argument("--backend", choices=["search", "qmd"], default="search")
    ap.add_argument("--qmd-mode", choices=["search", "query", "vsearch"], default="search")
    ap.add_argument("--collection", default="brain")
    sub = ap.add_subparsers(dest="cmd")
    ad = sub.add_parser("add")
    ad.add_argument("question")
    ad.add_argument("--terms", required=True)
    ad.add_argument("--expect", required=True, action="append")
    a = ap.parse_args()
    if os.environ.get("BRAINWARDEN_UNATTENDED") and (a.cmd == "add" or a.backend != "search"):
        # The unattended review may measure, nothing else: a new question
        # needs the person's OK, and another search program is another program.
        print("refused while unattended: only `exam.py --record` (add questions in a normal chat)")
        return 2
    return cmd_add(a) if a.cmd == "add" else cmd_exam(a)


if __name__ == "__main__":
    sys.exit(main())
