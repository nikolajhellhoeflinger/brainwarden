#!/usr/bin/env python3
"""How far along is a company vault? — one number that means something.

    python3 .tools/progress.py            # the summary
    python3 .tools/progress.py --open     # every file still carrying gaps
    python3 .tools/progress.py --by-role  # who has to answer how much

A company vault ships as scaffolding with the house rules missing. Gaps
come in two shapes, both counted:

  - **`<angle-bracket>` fields**: `owner: <role that owns this vault>`,
    `**Who may release content:** <role(s)>`. `hygiene.py` cannot see
    them, since the placeholder is a non-empty value.
  - **`TO FILL IN (role)` markers** (a translated vault uses its own
    word, e.g. `AUSFÜLLEN`), where the gap is a whole decision rather
    than one field.

Command examples in backticks (`search.py <terms>`) are not counted, nor
are template files, which keep their placeholders.

The summary leads with **files verified**: a file counts only with
`status: stable` AND a `verified:` line (a human read it and said yes).
Nothing in this repo sets that automatically. **Gaps closed** only means
someone typed something into a field.

Read-only. Exit code is 0 unless something is actually wrong with the
vault.
"""
import argparse
import collections
import os
import re
import sys

# A real gap names who answers it: `TO FILL IN (bookkeeping): …`. The bare
# word mostly appears in prose ABOUT the gaps, which must not count.
GAP = re.compile(r"(?:TO FILL IN|AUSFÜLLEN)\s*\(([^)]{1,60})\)")
# A placeholder without a role: the marker in a quoted line, neither bold
# nor code. Case-SENSITIVE: German `ausfüllen` is an ordinary verb; only
# the upper-case spelling is the marker.
ORPHAN = re.compile(r"^\s*>.*(?<![*`])(?:TO FILL IN|AUSFÜLLEN)(?![*`])(?!\s*\()", re.M)
# An unfilled `<…>` field in a frontmatter line or a bold-label prose line;
# inside backticks it is a command example, never a gap. FIELD needs no
# closing `>`: a shipped field in `About this vault.md` wraps across lines.
FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*:[ \t]*<[^`\n]", re.M)
LABEL = re.compile(r"^\*\*[^*\n]+:\*\*[ \t]*<[^`\n]", re.M)
SKIP_DIRS = {".git", ".obsidian", ".tools", ".claude", "_templates"}
# The archive is cold storage: retired notes keep their markers. Matched by
# number, not name (`90-archiv`).
SKIP_PREFIXES = ("90-",)
# The rules sheet TALKS about gaps rather than carrying one. Every
# `_`-prefixed file is skipped too: a template (`_template.md`, translated
# `_vorlage.md`) keeps its tokens forever.
SKIP_FILES = {"CLAUDE.md"}
# Fallback only: the vault's own CLAUDE.md is the authority (status_scale()).
# Position 1 is the released state ("stable").
VALIDITY = ("draft", "stable", "deprecated")


def status_scale(vault):
    """The `status:` values THIS vault uses, in its own CLAUDE.md's order
    (a translated vault writes `status: entwurf | gültig | überholt`). The
    kit freezes the ORDER, not the words."""
    try:
        with open(os.path.join(vault, "CLAUDE.md"), encoding="utf-8-sig",
                  errors="ignore") as fh:
            rules = fh.read()
    except OSError:
        return list(VALIDITY)
    hit = re.search(r"^status:[ \t]*([^\n#]*\|[^\n#]*?)[ \t]*(?:#.*)?$", rules, re.M)
    if not hit:
        return list(VALIDITY)
    values = [w.strip().lower() for w in hit.group(1).split("|") if w.strip()]
    return values if len(values) >= 2 else list(VALIDITY)


def frontmatter(text):
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    return parts[1] if len(parts) > 2 else ""


def walk(vault):
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS
                   and not d.startswith(".") and not d.startswith(SKIP_PREFIXES)]
        for name in sorted(files):
            if not name.endswith(".md") or name in SKIP_FILES \
                    or name.startswith("_"):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, vault)
            try:
                with open(path, encoding="utf-8-sig", errors="ignore") as fh:
                    yield rel, fh.read()
            except OSError:
                continue


def main():
    for stream in (sys.stdout, sys.stderr):       # Windows pipes default to cp1252
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    # default: the vault this script lives in (.tools/..), like the other tools
    ap.add_argument("vault", nargs="?", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--open", action="store_true", help="list files with gaps")
    ap.add_argument("--by-role", action="store_true", help="group gaps by who answers")
    a = ap.parse_args()
    vault = os.path.expanduser(a.vault)

    released = status_scale(vault)[1]
    notes = verified = stable = 0
    gaps = collections.Counter()          # file -> gaps of both shapes
    roles = collections.Counter()
    unaddressed = fields = markers = 0

    scanned = 0
    for rel, text in walk(vault):
        scanned += 1
        # signposts, root pages and kit pages are scanned for gaps but are not
        # notes: counted, they keep "N of M verified" from ever reaching M
        is_note = os.sep in rel and os.path.basename(rel) != "index.md" and "<!-- kit-page" not in text[:400]
        notes += is_note
        fm = frontmatter(text)
        is_stable = re.search(rf"^status:\s*(?:{re.escape(released)}|stable)\b",
                              fm, re.M | re.I) is not None
        is_verified = re.search(r"^verified:\s*\S", fm, re.M) is not None
        stable += is_note and is_stable
        verified += is_note and is_stable and is_verified
        found = GAP.findall(text)
        orphans = ORPHAN.findall(text)
        # `<…>` fields: frontmatter lines are matched against the frontmatter
        # block only, so a `type: knowledge | source` example further down the
        # body cannot be mistaken for one.
        open_fields = len(FIELD.findall(fm)) + len(LABEL.findall(text))
        if found or orphans or open_fields:
            gaps[rel] = len(found) + len(orphans) + open_fields
            for who in found:
                for part in re.split(r"\s*/\s*", who.strip()):
                    roles[part.strip()] += 1
            unaddressed += len(orphans)
            fields += open_fields
            markers += len(found) + len(orphans)

    if not scanned:
        print(f"No notes found under {vault}")
        return 1

    total_gaps = sum(gaps.values())
    print(f"\n  {verified} of {notes} notes verified"
          f"   ({stable} stable, {verified} of those confirmed by a human)")
    print(f"  {total_gaps} open gaps in {len(gaps)} files"
          f"   ({fields} unfilled <…> fields, {markers} marked TO FILL IN)")
    if total_gaps and not verified:
        print("\n  Nothing is company truth yet. The first verified process")
        print("  note is the milestone — not the last deleted marker.")
    elif verified:
        share = 100.0 * verified / notes
        print(f"\n  {share:.0f}% of this vault can be acted on.")

    if a.by_role and (roles or fields):
        print("\n  Gaps by who has to answer:")
        for who, n in roles.most_common():
            print(f"    {n:4}  {who}")
        if unaddressed:
            print(f"    {unaddressed:4}  (no role named — these need one)")
        if fields:
            # A `<…>` field never names a role; the file it sits in does.
            # --open is the list that actually helps here.
            print(f"    {fields:4}  (unfilled <…> fields — see --open)")

    if a.open and gaps:
        print("\n  Files with open gaps (most first):")
        for rel, n in gaps.most_common():
            print(f"    {n:4}  {rel}")

    if not a.open and not a.by_role and gaps:
        print("\n  --open shows which files, --by-role shows who to ask.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
