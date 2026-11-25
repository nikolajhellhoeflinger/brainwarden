#!/usr/bin/env python3
"""The people in the brain: who can help with what, who is close right now,
and what to remember before you meet someone.

    python3 .tools/people.py who <topic words>     # who can I ask about this? three people, with the lines that say so
    python3 .tools/people.py close [--k 15]        # who is in your life right now (dated mentions, recent ones count most)
    python3 .tools/people.py brief <name>          # before a meeting: role, open points, the last things that happened
    python3 .tools/people.py upcoming [--days 7]   # dates in the next days that name a person
    python3 .tools/people.py contacts <file.vcf>   # address-book export: who is not in the brain yet
                    [--no-names] [--reveal 4,17]   #   …listed without names first, if a model is to sort them

(Windows: `py -3`.) A contact list knows that someone exists. A brain knows
what they did, what you agreed and when you last spoke — that is the part
that helps when you need someone who knows about tax law, or when a meeting
starts in ten minutes. But nobody remembers which of 40 people notes and 300
captures mention whom; so this reads them for you:

  who        ranks people by how much their own note and the lines that
             mention them say about the topic, nudged by how close they are,
             and prints the evidence — never a bare name.
  close      "closeness" is computed from dated mentions: captures, project
             logs, decisions, the person's own "Recent" lines. A mention
             counts in full today and half after 90 days. It is a view, not
             a verdict, and it is never written anywhere.
  brief      the person's note boiled down for the minute before a meeting.
  upcoming   dated lines in the top-level notes (Deadlines and the like) within the next days
             that name a person — the review puts them on Home with a link.
  contacts   breadth from the phone's address book (export as .vcf), without
             importing it: who has no note yet, with organisation and title.
             `--no-names` prints numbers instead of names, so a model can sort
             people by field without seeing who they are; `--reveal` maps the
             numbers back. The file stays where it is — keep it out of the vault.

The rules that keep this from turning into surveillance: it reads only the
vault and the file you hand it, sends nothing anywhere, stores no score, and
says nothing a note does not say. What goes INTO a person note stays the
review's rule: facts you could show them if they asked.

People are the notes in the people folder (`30-…/people/`, or its name in
the vault's language) and every note with `type: person` — and every entry
of a group note written as `- **Full Name** – role` (a team, a committee, a
client's staff): measured on a real brain, one such note held 15 people
that a note-per-person reading turned into a single "person". A person is
recognised by the note's name, its title and its `aliases:`, an entry by its
full name, a nickname in quotes and, after a title (`Hr. Brandt`), its
surname — whole words, umlauts folded like search.py. A first name alone
counts only when one known person carries it AND the note also names that
person's group subject (the group note's links and name): in 300 notes
"Anna" is three different people, but "Ben" in a note about the shop is the
Ben of the shop team. Python standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import os
import re
import sys
import unicodedata
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
PEOPLE_DIRS = {"people", "menschen", "personen", "personas", "personnes", "persone", "pessoas", "kontakte"}
HALF_LIFE = 90.0          # days until a mention counts half
UNDATED = 0.15            # a mention without any date: it happened, but when?
MIN_NAME = 3
SKIP_DIRS = {".git", ".obsidian", ".tools", ".trash", "_templates", "node_modules"}
# 2026-11-25, 25.11.2026 and 25.11. — but not the "1.3." of a version number "1.3.0"
DATE = re.compile(r"(?<![\d.])(\d{4})-(\d{2})-(\d{2})(?!\d)|(?<![\d.])(\d{1,2})\.(\d{1,2})\.(?:(\d{4})(?!\d)|(?![\d]))")


def utf8_stdout():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def _search():
    spec = importlib.util.spec_from_file_location("brain_search", VAULT / ".tools" / "search.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


fold = _search().fold


# ------------------------------------------------------------------ reading
def read(path):
    try:
        return unicodedata.normalize("NFC", Path(path).read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return ""


def front_and_body(text):
    front = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            key = None
            for line in text[3:end].splitlines():
                m = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
                if m:
                    key = m.group(1).lower()
                    front[key] = m.group(2).split(" #")[0].strip()
                elif key and re.match(r"\s+-\s+", line):
                    front[key] = (front[key] + "," if front[key] else "") + line.strip()[1:].strip()
            text = text[end + 4:]
    return front, text


def as_list(value):
    return [v.strip().strip("\"'") for v in (value or "").strip().strip("[]").split(",")
            if v.strip().strip("\"'") and not v.strip().startswith("<")]


def notes():
    for dirpath, dirnames, filenames in os.walk(VAULT):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d not in SKIP_DIRS]
        for f in filenames:
            if f.endswith(".md"):
                yield Path(dirpath) / f


def rel(path):
    return Path(path).relative_to(VAULT).as_posix()


def to_date(m, fallback_year=None):
    try:
        if m.group(1):
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        year = int(m.group(6)) if m.group(6) else fallback_year
        return dt.date(year, int(m.group(5)), int(m.group(4))) if year else None
    except (ValueError, TypeError):
        return None


def note_date(path, front):
    m = re.match(r"(\d{4}-\d{2}-\d{2})", Path(path).name)
    for cand in (m.group(1) if m else None, front.get("created", "")[:10]):
        try:
            return dt.date.fromisoformat(cand)
        except (TypeError, ValueError):
            continue
    return None


def clean(line, limit=150):
    line = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", lambda m: m.group(2), line)
    line = re.sub(r"\*\*|__|<!--.*?-->", "", line)
    line = re.sub(r"\s+", " ", line).strip().lstrip("-*# ").strip()
    return line if len(line) <= limit else line[:limit - 1].rstrip() + "…"


# ------------------------------------------------------------------- people
# A group note lists several people, one bold entry each — "- **Felix Daum** –
# lawyer in Vienna". Measured on a real brain: one such note held 15 people,
# and "who can I ask about a lawyer?" answered with the NOTE's name. Entries
# are people; bold attributes ("**Birthday:**", "**Acme GmbH** (…):") are not —
# hence the dash after the name, and no colon, digit or company form in it.
MEMBER = re.compile(r"^\s*[-*+]\s+\*\*(?P<name>[^*\n]{2,80}?)\*\*\s*(?:\([^)\n]{0,80}\)\s*)?[–—-]\s+\S")
TITLES = {"hr.", "fr.", "herr", "frau", "dr.", "mag.", "prof.", "mr.", "mrs.", "ms.", "sr.", "sra."}
ARTICLES = {"ein", "eine", "einer", "der", "die", "das", "a", "an", "the", "un", "une", "el", "la", "le",
            "il", "uno", "una", "my", "mein", "meine"}
COMPANY = re.compile(r"(?i)(?<!\w)(gmbh|ag|kg|og|ltd|inc|llc|e\.v\.|s\.a\.|srl|bv|plc|corp)(?!\w)")
LINK = re.compile(r"\[\[([^\]|#]+)")
# Words that name a kind of group, not its subject: "Ben" in any note that says
# "team" is not the Ben of the shop team.
GROUP_WORDS = {"team", "teams", "group", "gruppe", "family", "familie", "people", "leute", "menschen",
               "contacts", "kontakte", "committee", "komitee", "friends", "freunde", "colleagues", "kollegen",
               "beteiligte", "members", "mitglieder", "crew", "staff", "personas", "personnes", "persone"}


def member_name(raw):
    """(full name, nicknames) from the bold part of an entry, or None when it
    is not a person: "Michael („Michi“) Bachmann" → ("Michael Bachmann", ["Michi"])."""
    nicks = re.findall(r"[„\"“»«]([^“”\"»«]{2,30})[“”\"»«]", raw)
    name = re.sub(r"\s*\([^)]*\)", "", raw).strip()
    tokens = name.split()
    if not 1 <= len(tokens) <= 4 or name.endswith(":") or re.search(r"\d", name) or COMPANY.search(name):
        return None
    if tokens[0].lower() in ARTICLES:
        return None
    if not all(t[0].isupper() or t.lower() in TITLES or t.lower() in ("von", "van", "de", "da", "di", "zu")
               for t in tokens):
        return None
    return name, nicks


class Person:
    """A person note — or, with `group`, one entry in a group note."""

    def __init__(self, path, entry=None, group=None):
        self.path = Path(path)
        self.group = group
        self.mentions = []      # (date or None, path, line)
        if group is None:
            self.text = read(path)
            self.front, self.body = front_and_body(self.text)
            stem = self.path.stem
            title = self.front.get("title", "").strip("\"'")
            h1 = next((l[2:].strip() for l in self.body.splitlines() if l.startswith("# ")), "")
            self.name = h1 or (title if title and not title.startswith("<") else stem.replace("-", " "))
            names = {stem, stem.replace("-", " "), self.name}
            if title and not title.startswith("<"):
                names.add(title)
            names |= set(as_list(self.front.get("aliases")))
            self.firsts = set()
            self.lines = [l for l in self.body.splitlines()]
            self.members = []
            # what the note says ABOUT itself, without the entries that are other people
            self.context = {fold(w) for w in re.split(r"[\s_-]+", stem)
                            if len(w) >= MIN_NAME + 1 and fold(w) not in GROUP_WORDS}
            self.context |= {fold(m.strip()) for m in LINK.findall(self.body) if len(m.strip()) >= MIN_NAME + 1}
        else:
            name, nicks, lines = entry
            self.name, self.front, self.text = name, {}, "\n".join(lines)
            self.body, self.lines, self.members, self.context = self.text, lines, [], group.context
            tokens = name.split()
            titled = tokens[0].lower() in TITLES
            names = set(nicks)
            if len(tokens) > 1:
                names.add(name)
            if titled and len(tokens) > 1:
                names.add(" ".join(tokens[1:]))              # "Hr. Mürmann" is "Mürmann"
            # a first name alone is a person only where the group's subject is
            # in the same note (see collect) — "Ben" in a note about the shop
            self.firsts = {fold(tokens[0])} if not titled and len(tokens[0]) >= MIN_NAME else set()
        self.names = sorted({fold(n).strip() for n in names if len(n.strip()) >= MIN_NAME}, key=len, reverse=True)

    def where(self):
        return f"in {rel(self.path)}" if self.group else rel(self.path)

    def own_lines(self):
        taken = {l for m in self.members for l in m.lines}
        return [l for l in self.lines if l not in taken]

    def lead(self):
        for line in self.own_lines():
            s = line.strip()
            if s and not s.startswith(("#", "|", ">", "<!--", "---", "Related:")):
                return clean(s, 200)
        return ""

    def section(self, *titles):
        out, on = [], False
        for line in self.own_lines():
            if line.startswith("## "):
                on = fold(line[3:]).strip() in titles
                continue
            if on and line.strip().startswith(("-", "*")) and not line.strip().lstrip("-* ").startswith("<"):
                out.append(clean(line))
        return out


def entries(person):
    """The people a group note lists: each bold entry with its continuation
    lines (indented, or not starting a new item). Duplicates merge."""
    found, cur = {}, None
    for line in person.body.splitlines():
        m = MEMBER.match(line)
        if m:
            parsed = member_name(m.group("name").strip())
            cur = None
            if parsed:
                key = fold(parsed[0])
                if key in found:
                    found[key][2].append(line)
                    found[key][1].extend(n for n in parsed[1] if n not in found[key][1])
                else:
                    found[key] = (parsed[0], list(parsed[1]), [line])
                cur = key
            continue
        if cur and line.strip() and line[:1] in (" ", "\t") and not line.lstrip().startswith(("#",)):
            found[cur][2].append(line)
        else:
            cur = None
    return list(found.values())


def people():
    found = {}
    for path in notes():
        parts = {p.lower() for p in path.relative_to(VAULT).parts[:-1]}
        if path.name.lower() in ("index.md", "claude.md"):
            continue
        in_folder = bool(parts & PEOPLE_DIRS)
        if not in_folder:
            head = read(path)[:400]
            if not re.search(r"^type:\s*person\s*$", head, re.M | re.I):
                continue
        p = Person(path)
        if p.front.get("status", "").lower() != "deprecated" and p.names:
            p.members = [Person(path, entry=e, group=p) for e in entries(p)]
            found[str(path)] = p
    persons = list(found.values())
    # a group's subject is what it is ABOUT — a link to a person ([[Papa]]) is
    # not: with it, every note naming that person made "Ben" the group's Ben
    person_names = {n for p in persons for n in p.names}
    for p in persons:
        p.context -= person_names
    return persons + [m for p in persons for m in p.members]


class Directory:
    """Who a line names. Full names and aliases count everywhere; a first name
    counts only when exactly one known person carries it AND the note also
    names that person's group subject — in 300 notes "Anna" is three people,
    but "Ben" in a note about the licence project is the Ben of that project."""

    def __init__(self, persons):
        by_name = {}
        for p in persons:
            for n in p.names:
                by_name.setdefault(n, p)
        self.by_name = by_name
        self.full = re.compile(r"(?<!\w)(" + "|".join(re.escape(n) for n in sorted(by_name, key=len, reverse=True))
                               + r")(?!\w)") if by_name else None
        counts = {}
        for p in persons:
            for f in p.firsts | {n.split()[0] for n in p.names}:
                counts[f] = counts.get(f, 0) + 1
        self.first = {f: p for p in persons for f in p.firsts if counts.get(f) == 1}
        self.firsts = re.compile(r"(?<!\w)(" + "|".join(re.escape(f) for f in sorted(self.first, key=len, reverse=True))
                                 + r")(?!\w)") if self.first else None

    def in_line(self, folded_line, folded_note):
        hits = {self.by_name[m.group(1)] for m in self.full.finditer(folded_line)} if self.full else set()
        if self.firsts:
            for m in self.firsts.finditer(folded_line):
                p = self.first[m.group(1)]
                if p not in hits and any(w in folded_note for w in p.context):
                    hits.add(p)
        return hits


def collect(persons):
    """Every line that mentions a person, with the best date it has: the
    line's own date, else the date of the entry it belongs to, else the
    note's. A person's own text counts only where it is dated — the rest is
    who they ARE, not a moment you spent with them."""
    d = Directory(persons)
    if not d.full and not d.firsts:
        return
    notes_of = {str(p.path): p for p in persons if p.group is None}
    for path in notes():
        if path.name.lower() in ("index.md", "claude.md"):
            continue
        text = read(path)
        front, body = front_and_body(text)
        base = note_date(path, front)
        mine = notes_of.get(str(path))
        entry_of = {l: m for m in (mine.members if mine else []) for l in m.lines}
        folded_note = fold(text)
        year = base.year if base else dt.date.today().year
        section = None          # the date a log entry or a dated heading gave the lines below it
        for line in body.splitlines():
            if not line.strip() or line.lstrip().startswith(("<!--", "Related:")):
                continue
            m = DATE.search(line)
            when = to_date(m, year) if m else None
            head = line.lstrip()
            if head.startswith("#"):
                section = when
            elif when and DATE.match(head.lstrip("-*+> ").lstrip("*_ ")):
                section = when          # "- 25.11. …": the entry and its continuation lines
            hits = d.in_line(fold(line), folded_note)
            owner = entry_of.get(line) or mine           # whose own text this line is
            if owner:
                hits.add(owner)
            if not hits:
                continue
            # a project note created in July still logs November: an undated
            # line takes its entry's date before the note's own
            when = when or section
            for p in hits:
                if p is owner and not when:
                    continue
                if p is mine and owner is not mine:
                    continue        # an entry line is about that member, not the group
                p.mentions.append((when or (None if p is owner else base), path, line))


def closeness(p, today):
    score = 0.0
    for when, _, _ in p.mentions:
        if when is None:
            score += UNDATED
        else:
            age = max(0, (today - when).days)
            score += 0.5 ** (age / HALF_LIFE)
    return score


def last_seen(p, today):
    dates = [w for w, _, _ in p.mentions if w and w <= today]
    return max(dates) if dates else None


# ------------------------------------------------------------------ commands
def cmd_close(k):
    persons, today = people(), dt.date.today()
    if not persons:
        print("no people notes yet (a folder people/ — or its name in your language — or notes with type: person)")
        return 0
    collect(persons)
    # a group note with its people listed is a container, not someone you are close to
    ranked = sorted((p for p in persons if len(p.members) < 2), key=lambda p: closeness(p, today), reverse=True)
    print(f"closeness — {len(persons)} people, recent mentions count most (half after {int(HALF_LIFE)} days)")
    for p in ranked[:k]:
        last = last_seen(p, today)
        quiet = f"  (quiet since {last})" if last and (today - last).days > 120 else ""
        print(f"  {closeness(p, today):5.1f}  {p.name} — {p.where()} · {len(p.mentions)} mentions"
              f"{', last ' + last.isoformat() if last else ''}{quiet}")
    return 0


def cmd_who(terms, k, contacts_file):
    persons, today = people(), dt.date.today()
    # "hotels germany" as ONE argument (a quoted call) is two words, not one
    folded = [fold(w) for t in terms for w in t.split() if len(w) >= 2]
    if not folded:
        print("Usage: people.py who <topic words>")
        return 1
    collect(persons)
    ranked = []
    for p in persons:
        own = p.own_lines()
        own_set = set(own)
        own_lines = [l for l in own if any(t in fold(l) for t in folded)]
        evidence = [(path, line) for _, path, line in p.mentions
                    if not (path == p.path and line in own_set) and any(t in fold(line) for t in folded)]
        # what their own note says outweighs being mentioned near the topic: on a
        # real brain, "lawyer" put two people above the lawyers because both were
        # named in many lines about lawyers. Closeness only breaks near-ties
        # (at most +50 %) — an additive bonus put the most-mentioned family
        # member above the actual lawyer.
        relevance = 10 * min(len(own_lines), 2) + min(len(evidence), 5)
        if relevance:
            ranked.append((relevance * (1 + min(closeness(p, today), 10) / 20), p, own_lines, evidence))
    ranked.sort(key=lambda r: r[0], reverse=True)
    if not ranked:
        print(f"nobody in the brain is linked to: {' '.join(terms)}")
    for score, p, own_lines, evidence in ranked[:k]:
        last = last_seen(p, today)
        print(f"\n{p.name} — {p.where()} (close {closeness(p, today):.1f}{', last ' + last.isoformat() if last else ''})")
        for l in own_lines[:2]:
            print(f"    own note: {clean(l)}")
        for path, l in evidence[:2]:
            print(f"    {rel(path)}: {clean(l)}")
    if contacts_file:
        known = {n for p in persons for n in p.names}
        extra = [c for c in read_vcards(contacts_file) if fold(c["name"]).strip() not in known
                 and any(t in fold(" ".join((c["org"], c["title"], c["note"]))) for t in folded)]
        if extra:
            print("\nfrom your contacts (no note yet):")
            for c in extra[:k]:
                print(f"    {c['name']} — {', '.join(x for x in (c['org'], c['title']) if x)}")
    return 0


def find_person(persons, query):
    q = fold(query).strip()
    exact = [p for p in persons if q in p.names or q in p.firsts]
    if exact:
        return exact
    return [p for p in persons if any(q in n for n in p.names)]


def cmd_brief(query):
    persons, today = people(), dt.date.today()
    hits = find_person(persons, query)
    if not hits:
        print(f"no person note matches \"{query}\"")
        return 1
    if len(hits) > 1:
        print("several people match: " + ", ".join(f"{p.name} ({p.where()})" for p in hits[:8]))
        return 1
    p = hits[0]
    collect(persons)
    print(f"{p.name} — {p.where()}")
    if p.lead():
        print(f"  {p.lead()}")
    open_ = p.section("open", "offen", "abierto", "ouvert", "aperto")
    if open_:
        print("  open:")
        for l in open_[:4]:
            print(f"    - {l}")
    dated = sorted([m for m in p.mentions if m[0]], key=lambda m: m[0], reverse=True)
    if dated:
        print("  last things:")
        for when, path, line in dated[:5]:
            print(f"    - {when} {clean(line, 120)} ({rel(path)})")
    last = last_seen(p, today)
    if last:
        print(f"  last mention {(today - last).days} days ago")
    return 0


def cmd_upcoming(days):
    persons, today = people(), dt.date.today()
    d = Directory(persons)
    if not d.full and not d.firsts:
        return 0
    # the top-level notes where dates live (Deadlines and the like) — not Home,
    # whose dated lines are mostly WHEN a question was asked, not a meeting
    sources = [f for f in sorted(VAULT.glob("*.md")) if f.name.lower() not in ("claude.md", "home.md", "index.md")]
    seen, out = set(), []
    for src in sources:
        text = read(src)
        folded_note = fold(text)
        for line in text.splitlines():
            names = d.in_line(fold(line), folded_note)
            if not names:
                continue
            plain = re.sub(r"\[\[[^\]]*\]\]", " ", line)    # a date in a link is a note's name
            for m in DATE.finditer(plain):
                when = to_date(m, today.year)
                if when and today <= when <= today + dt.timedelta(days=days):
                    key = (when, clean(line, 80))
                    if key not in seen:
                        seen.add(key)
                        out.append((when, clean(line), sorted(names, key=lambda p: p.name)))
                    break
    if not out:
        print(f"no dates with people in the next {days} days")
        return 0
    for when, line, names in sorted(out, key=lambda o: o[0]):
        print(f"{when} {line}")
        for p in names:
            print(f"    → {p.name}: {p.where()}")
    return 0


# ----------------------------------------------------------------- contacts
def unfold_vcf(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n[ \t]", "", text)                              # RFC 6350 folding
    return re.sub(r"=\n", "", text)                                  # quoted-printable soft breaks (vCard 2.1)


def qp_decode(value, charset):
    raw = re.sub(rb"=([0-9A-Fa-f]{2})", lambda m: bytes([int(m.group(1), 16)]), value.encode("latin-1", "replace"))
    try:
        return raw.decode(charset or "utf-8", "replace")
    except LookupError:
        return raw.decode("utf-8", "replace")


def vcf_value(params, value):
    p = params.upper()
    if "QUOTED-PRINTABLE" in p:
        m = re.search(r"CHARSET=([\w-]+)", p)
        value = qp_decode(value, m.group(1).lower() if m else "utf-8")
    return value.replace("\\n", " ").replace("\\N", " ").replace("\\,", ",").replace("\\;", ";").strip()


def read_vcards(path):
    try:
        text = unfold_vcf(Path(path).expanduser().read_text(encoding="utf-8", errors="replace"))
    except OSError as e:
        raise SystemExit(f"cannot read {path}: {e}")
    cards = []
    for block in re.findall(r"BEGIN:VCARD(.*?)END:VCARD", text, re.S | re.I):
        c = {"name": "", "org": "", "title": "", "note": "", "n": ""}
        for line in block.split("\n"):
            m = re.match(r"(?:item\d+\.)?([A-Za-z-]+)((?:;[^:]*)?):(.*)$", line.strip())
            if not m:
                continue
            key, params, value = m.group(1).upper(), m.group(2), m.group(3)
            if key == "FN":
                c["name"] = vcf_value(params, value)
            elif key == "N":
                parts = [vcf_value(params, v) for v in value.split(";")]
                c["n"] = " ".join(x for x in (parts[1] if len(parts) > 1 else "", parts[0]) if x)
            elif key == "ORG":
                c["org"] = " ".join(vcf_value(params, v) for v in value.split(";") if v.strip())
            elif key == "TITLE":
                c["title"] = vcf_value(params, value)
            elif key in ("NOTE", "CATEGORIES"):
                c["note"] = (c["note"] + " " + vcf_value(params, value)).strip()
        c["name"] = c["name"] or c["n"]
        if c["name"]:
            cards.append(c)
    return cards


def cmd_contacts(path, no_names, reveal):
    persons = people()
    known = {n for p in persons for n in p.names}
    cards = read_vcards(path)
    new = [c for c in cards if fold(c["name"]).strip() not in known]
    if reveal:
        want = {int(x) for x in re.findall(r"\d+", reveal)}
        for i, c in enumerate(new, 1):
            if i in want:
                print(f"#{i}: {c['name']} — {', '.join(x for x in (c['org'], c['title']) if x) or '-'}")
        return 0
    print(f"{len(cards)} contacts, {len(cards) - len(new)} already in the brain, {len(new)} not yet"
          + (" — names withheld; `--reveal 3,7` shows who a number is" if no_names else ""))
    for i, c in enumerate(new, 1):
        who = f"#{i}" if no_names else c["name"]
        what = ", ".join(x for x in (c["org"], c["title"]) if x)
        if no_names and not what:
            continue             # without a name and without a field there is nothing to sort
        print(f"  {who} — {what or '-'}")
    return 0


def main(argv=None):
    utf8_stdout()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    w = sub.add_parser("who")
    w.add_argument("terms", nargs="+")
    w.add_argument("--k", type=int, default=3)
    w.add_argument("--contacts", help="an address-book export (.vcf) to look in as well")
    c = sub.add_parser("close")
    c.add_argument("--k", type=int, default=15)
    b = sub.add_parser("brief")
    b.add_argument("name", nargs="+")
    u = sub.add_parser("upcoming")
    u.add_argument("--days", type=int, default=7)
    v = sub.add_parser("contacts")
    v.add_argument("file")
    v.add_argument("--no-names", action="store_true")
    v.add_argument("--reveal")
    a = ap.parse_args(argv)
    if os.environ.get("BRAINWARDEN_UNATTENDED") and (a.cmd == "contacts" or getattr(a, "contacts", None)):
        # the address book lies outside the vault: that needs the person in the chat
        print("refused while unattended: contacts only in a normal chat")
        return 2
    if a.cmd == "who":
        return cmd_who(a.terms, a.k, a.contacts)
    if a.cmd == "close":
        return cmd_close(a.k)
    if a.cmd == "brief":
        return cmd_brief(" ".join(a.name))
    if a.cmd == "upcoming":
        return cmd_upcoming(a.days)
    if a.cmd == "contacts":
        return cmd_contacts(a.file, a.no_names, a.reveal)
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
