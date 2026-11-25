#!/usr/bin/env python3
"""Brain search: deterministic pre-search over the vault (token saver).

    python3 ~/Brain/.tools/search.py real-rates gold
    python3 ~/Brain/.tools/search.py "chilling effect" --k 5
    python3 ~/Brain/.tools/search.py --stats
    python3 ~/Brain/.tools/search.py --resurface   # older notes tied to this week's

Scoring per file and term:

    title/filename   word start 5.0   inside a word 2.0
    tags             word start 3.0   inside a word 1.0
    body line        word start 1.0 for the first, less for each further
                     one, approaching 5.0 · inside a word 0.4 (max 3.0)

Body mentions have diminishing returns, and that is what keeps the ranking
honest: summed straight, a project log that happens to write "Vertrag" on a
hundred lines scored 100.0 and buried `Vertrag.md` — the note that IS about
contracts — at 11.0. On a 10 MB log it reached 132731.0. Repetition is not
aboutness. The total from body mentions now stays under one title hit, so
the file NAMED after the term always wins against one that merely says it
often — while ten mentions still rank above three.

Hits INSIDE a word count — German glues words together, so `Vertrag` has
to find `Rahmenvertrag`, `Kosten` has to find `Mehrkostenforderungen` and
`Straße` has to find `Taborstraße`. They count LESS than a word start and
are capped per term, so `test` still cannot be flooded to the top by a
file that only says `fastest`. Terms shorter than 4 characters match at
word starts only (`ei`, `an` would otherwise match everything).

Accent-insensitive (cafe matches café, Strasse matches Straße). Output:
top-k files with matching lines — Claude then reads ONLY those files.
"""
import os, re, sys, unicodedata

# Windows falls back to the console codepage (cp1252/cp850) the moment the
# output is redirected or piped — and `↳`, or any arrow inside a matched
# note line, does not exist there, so the search died with a
# UnicodeEncodeError. Console streams are utf-8 already; this fixes pipes.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

SKIP_DIRS = {".git", ".obsidian", ".tools", "_templates"}

W_NAME, W_NAME_IN = 5.0, 2.0        # title / filename
W_TAG, W_TAG_IN = 3.0, 1.0          # tags
W_LEAD, W_LEAD_IN = 3.0, 1.0        # the note's heading and first sentence (see lead_block)
W_BODY, W_BODY_IN = 1.0, 0.4        # body lines
BODY_CAP = 5.0                      # body word starts approach, never pass, this
BODY_HALF = 4.0                     # shape of that approach (see score_file)
BODY_IN_CAP = 3.0                   # max inside-word body score per term
MIN_IN_LEN = 4                      # shorter terms: word starts only

# Frontmatter vocabulary (see spec 4): `maturity` is the ripeness of a
# knowledge note, `status` is validity. Old vaults still write ripeness
# into `status:` — --stats reads both and flags the leftovers.
MATURITY = ("seed", "growing", "evergreen")
VALIDITY = ("draft", "stable", "deprecated")


def schema_scales(root):
    """The scales THIS vault uses, read from its own CLAUDE.md.

    A translated vault writes `status: entwurf | gültig | überholt` in its
    rules file and in every note. Comparing against the English words then
    reported every correct note as "outside the schema" — a permanent false
    finding in exactly the vault that followed its own rules. The rules file
    is the authority; the English words are only the fallback.
    """
    m, v = set(MATURITY), set(VALIDITY)
    try:
        with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8-sig",
                  errors="ignore") as fh:
            rules = fh.read()
    except OSError:
        return m, v
    for key, target in (("maturity", m), ("status", v)):
        # Der Wert endet am Zeilenkommentar: die Schema-Zeile trägt fast
        # immer eine Erklärung hinter `#`.
        hit = re.search(rf"^{key}:[ \t]*([^\n#]*\|[^\n#]*?)[ \t]*(?:#.*)?$",
                        rules, re.M)
        if hit:
            target.update(w.strip().lower() for w in hit.group(1).split("|")
                          if w.strip())
    return m, v

# Kit infrastructure, not notes. Counting these inflates every number and
# their code examples ("status: seed | growing | evergreen" in CLAUDE.md)
# used to be counted as real frontmatter.
INFRA_FILES = {"CLAUDE.md", "index.md", "Home.md", "Deadlines.md",
               "About me.md", "About this vault.md", "Inbox rule.md",
               "README.md", "THIS-COPY.md"}

def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")

UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})

def fold(text):
    """Lowercase, German umlauts as their two-letter spelling, other accents
    stripped — so a query matches however the note happened to be written.

    `ä` is `ae` in German, not `a`. Stripping it to `a` made `länge` miss a
    note named `interviewlaenge` (measured on a real vault, where file names
    are written ASCII and the text is not) and, worse, made different words
    the same one: schon/schön, zahlen/zählen, drucken/drücken. Composed first
    (NFC), because macOS hands out file names decomposed. Other accents keep
    being stripped: cafe still matches café."""
    text = unicodedata.normalize("NFC", text.lower()).translate(UMLAUT)
    text = unicodedata.normalize("NFKD", text)
    return "".join(c for c in text if not unicodedata.combining(c))

def parse_args(argv):
    terms, k, i = [], 8, 0
    while i < len(argv):
        a = argv[i]
        if a == "--k" and i + 1 < len(argv):
            try:
                k = int(argv[i + 1])
            except ValueError:
                pass
            i += 2
            continue
        if a.startswith("--") and a not in ("--stats", "--resurface"):
            # Anything else starting with `--` used to vanish without a word,
            # so `search.py --root /other/vault gold` searched THIS vault for
            # "gold" and looked like it had honoured the flag. There is no
            # --root here on purpose: the tool searches the vault it lives in.
            print(f"Unknown option: {a}\n"
                  "Usage: search.py <term> [term2 ...] [--k N] | --stats\n"
                  "(No --root: this tool searches the vault it sits in — run "
                  "the copy inside that vault.)")
            return None, k
        if not a.startswith("--"):
            terms.append(a)
        i += 1
    return terms, k

def walk_notes(root):
    """Every .md file in the vault, minus tooling folders. Yields (path, relpath)."""
    for dirpath, dirs, files in os.walk(root):
        # Hidden folders are skipped like in hygiene.py: a vault that ships
        # its own `.claude/skills/` would otherwise count five SKILL.md files
        # as notes, and `.private/` would surface in every search.
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            if f.startswith("_") and ist_vorlage(os.path.join(dirpath, f)):
                continue
            path = os.path.join(dirpath, f)
            yield path, os.path.relpath(path, root)

def read(path):
    """utf-8-sig: a byte-order mark would otherwise hide the frontmatter."""
    try:
        return open(path, encoding="utf-8-sig", errors="ignore").read()
    except OSError:
        return None

def tags_block(text):
    """Everything under a YAML `tags:` key, incl. multi-line list items."""
    m = re.search(r"^tags:(.*(?:\n[ \t]+-[^\n]*)*)", text, re.M)
    return m.group(0) if m else ""

def lead_block(text):
    """The `# heading` and the first lines of prose under it — where a note
    says what it is ABOUT. A person note named after the person says "lawyer,
    reviews the writing limit" once, right there; project notes that merely
    mention the lawyer say it on many lines and used to outrank it (measured:
    the person came fourth for exactly those words). Counted like tags: once
    per term, never more."""
    body = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    heading, prose = "", []
    for line in body.splitlines():
        s = line.strip()
        if not heading and s.startswith("# "):
            heading = s[2:]
            continue
        if not s:
            if prose:
                break
            continue
        # Only prose is a lead: a list or a table under the heading is the
        # note's content, and a project log's first bullet says what happened
        # once, not what the note is about.
        if s.startswith(("#", "|", ">", "```", "<!--", "- ", "* ", "+ ")) or re.match(r"\d+[.)] ", s) \
                or s.startswith(("**Datum", "**Date")):
            if prose:
                break
            continue
        prose.append(s)
        if sum(len(x) for x in prose) > 300:
            break
    return fold(" ".join([heading] + prose))[:400]

def frontmatter(text):
    """The YAML block at the very top — and nothing else.

    Reading fields with `^status:` over the WHOLE file matches YAML
    examples inside fenced code blocks; that is how a one-note vault
    reported two notes with a maturity each."""
    m = re.match(r"---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", text, re.S)
    return m.group(1) if m else ""

def fm_value(fm, key):
    """One frontmatter value, comment and quotes stripped (`in progress` stays whole)."""
    m = re.search(rf"^{key}:[ \t]*(.+?)[ \t]*$", fm, re.M)
    if not m:
        return None
    return (m.group(1).split(" #")[0].strip().strip("\"'").lower() or None)

KIT_PAGE = "<!-- kit-page"

def ist_vorlage(path):
    """Eine Vorlagendatei - erkannt am Inhalt, nicht am Namen.

    Bisher galt jede Datei mit fuehrendem `_` als Vorlage und wurde
    stillschweigend uebersprungen: `_privat.md` existierte fuer die Suche
    und fuer den Zustandsbericht schlicht nicht. Der Ordner `_templates/`
    ist ohnehin ausgeschlossen; hier geht es um die Vorlage, die daneben
    liegt (`40-decisions/_template.md`, uebersetzt `_vorlage.md`). Die
    erkennt man daran, dass ihre Platzhalter noch drinstehen - das gilt in
    jeder Sprache.
    """
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as fh:
            return "{{" in fh.read(4000)
    except OSError:
        return False


def is_infra(rel, text=""):
    """Kit scaffolding: root/folder signposts and the raw/ readme.

    Three rules, in order of how well they survive a translation. The
    `<!-- kit-page -->` marker is the reliable one — an HTML comment is an
    exact token that renaming and translating cannot break, the same reason
    `Home.md` addresses its blocks by marker and not by heading. Then the
    structural rule, then the English name list for vaults built before the
    marker existed.

    The name list only holds in an ENGLISH vault — a German one carries
    `Termine.md`, `Über mich.md`, `Inbox-Regel.md`. Those then counted as
    notes in `--stats` and, worse, were not halved in the ranking: a
    deadline page mentions every project in the vault at least once, so it
    outranked the note actually about the project. The structural rule
    survives every translation: a vault's own pages sit in its ROOT, its
    notes sit in a numbered folder."""
    return (KIT_PAGE in text[:2000] or os.sep not in rel
            or os.path.basename(rel) in INFRA_FILES)

def git_reviews(root):
    """Review history — only if the vault IS a git repo, not if it sits in one.

    `git -C <vault> log` happily answers from a PARENT repository, which
    would report someone else's commits as this vault's review history."""
    import subprocess
    try:
        top = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=5)
    except Exception:
        return "reviews: unknown (git not available)"
    if top.returncode != 0 or not top.stdout.strip():
        return "reviews: unknown (vault is not a git repo — no version history)"
    if os.path.realpath(top.stdout.strip()) != os.path.realpath(root):
        return ("reviews: unknown (vault is not its own git repo — it sits inside "
                + os.path.realpath(top.stdout.strip()) + ", whose history is not this vault's)")
    try:
        log = subprocess.run(["git", "-C", root, "log", "-i", "--grep", "review",
                              "--format=%as"], capture_output=True, text=True,
                             timeout=5).stdout.split()
    except Exception:
        return "reviews: unknown (git log failed)"
    if not log:
        return "reviews: 0 (no commit mentions a review yet)"
    # Days, not commits: one review often makes several commits (the
    # unattended runner adds a follow-up, a person may commit twice), and
    # counting each one inflated the number the review history rests on.
    days = len(set(log))
    return f"reviews: {days} day{'s' if days != 1 else ''} (last {log[0]})"

def stats(root):
    """--stats: honest numbers about this vault — folders, maturity, age."""
    import collections
    folders = collections.Counter()
    maturity, validity, other_status = collections.Counter(), collections.Counter(), collections.Counter()
    maturity_ok, validity_ok = schema_scales(root)
    words, infra, legacy = [], 0, []
    for path, rel in walk_notes(root):
        text = read(path)
        if is_infra(rel, text or ""):
            infra += 1
            continue
        folders[rel.split(os.sep)[0] if os.sep in rel else "(root)"] += 1
        if text is None:
            continue
        words.append(len(text.split()))
        fm = frontmatter(text)
        ripeness = fm_value(fm, "maturity")
        if ripeness:
            maturity[ripeness] += 1
        value = fm_value(fm, "status")
        if value:
            if value in maturity_ok:       # old schema: status held the ripeness
                legacy.append(rel)
                if not ripeness:
                    maturity[value] += 1
            elif value in validity_ok:
                validity[value] += 1
            else:
                other_status[value] += 1
    print(f"notes: {sum(folders.values())}" + (f" (+ {plural(infra, 'kit file')}, not counted)" if infra else ""))
    if not folders:
        print("  (no notes yet — everything here is still kit scaffolding)")
    for name, n in sorted(folders.items()):
        print(f"  {name}: {n}")
    if words:
        print(f"words/note: median {sorted(words)[len(words) // 2]}")
    if maturity:
        print("maturity: " + " · ".join(f"{s} {n}" for s, n in sorted(maturity.items())))
    if validity:
        print("status: " + " · ".join(f"{s} {n}" for s, n in sorted(validity.items())))
    if other_status:
        print("status (values outside the schema): "
              + " · ".join(f"{s} {n}" for s, n in sorted(other_status.items())))
        print("  ↳ expected: maturity: " + "|".join(sorted(maturity_ok))
              + " · status: " + "|".join(sorted(validity_ok))
              + " (read from this vault's CLAUDE.md)")
    if legacy:
        print(f"legacy schema: `status:` still used for maturity in {plural(len(legacy), 'note')} "
              f"(update path: rename it to `maturity:`) — e.g. " + ", ".join(legacy[:3]))
    print(git_reviews(root))
    return 0

def score_file(text, name, terms):
    """Score one file against all terms. Returns (score, up to 3 sample lines)."""
    tags = fold(tags_block(text))
    lead = lead_block(text)
    raw_lines = text.splitlines()
    folded_lines = [fold(l) for l in raw_lines]
    score, starts, insides = 0.0, [], []
    for t in terms:
        pat = re.compile(r"\b" + re.escape(t))
        inside_ok = len(t) >= MIN_IN_LEN
        if pat.search(name):
            score += W_NAME
        elif inside_ok and t in name:
            score += W_NAME_IN
        if pat.search(tags):
            score += W_TAG
        elif inside_ok and t in tags:
            score += W_TAG_IN
        if pat.search(lead):
            score += W_LEAD
        elif inside_ok and t in lead:
            score += W_LEAD_IN
        hits, inside_score = 0, 0.0
        for raw, line in zip(raw_lines, folded_lines):
            start_hit = bool(pat.search(line))
            if not start_hit and not (inside_ok and t in line):
                continue
            if start_hit:
                hits += 1
            else:
                inside_score = min(inside_score + W_BODY_IN, BODY_IN_CAP)
            clean = raw.strip()[:120]
            if clean and not raw.startswith("---"):
                bucket = starts if start_hit else insides
                if clean not in starts and clean not in insides and len(bucket) < 3:
                    bucket.append(clean)
        # Diminishing returns instead of a straight sum: the first mention is
        # worth a full W_BODY (1.0), the hundredth almost nothing, and the
        # total can never reach BODY_CAP. A plain cap would do the same job
        # against flooding but would make every file with five or more
        # mentions score IDENTICALLY, and ties get broken alphabetically —
        # that throws away real signal to fix a fake one.
        score += BODY_CAP * hits / (hits + BODY_HALF) + inside_score
    return score, (starts + insides)[:3]

LINK_RE = re.compile(r"\[\[([^\]|#]+)|\]\(([^)#\s]+\.md)\)")


def last_changes(root):
    """{relpath: date of its last commit} in one pass over the history —
    file times lie (a fresh clone sets every one of them to today)."""
    import subprocess
    try:
        out = subprocess.run(["git", "-C", root, "log", "--format=@%as", "--name-only", "--no-renames"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace",
                             timeout=30).stdout
    except Exception:
        return {}
    seen, day = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            day = line[1:]
        elif line.strip() and day:
            seen.setdefault(line.strip().strip('"'), day)
    return seen


def resurface(root, k=3, days=7, quiet=60):
    """--resurface: the older notes connected to what this week is about.
    A random revisit opens a note nobody needs this week; this one opens the
    note that THIS week's notes link to, or that links to them, and that has
    not been touched for two months — the decision behind a project that is
    moving again, the person note behind a new capture."""
    import datetime
    top = subprocess_top(root)       # realpath("") would be the CURRENT folder, i.e. the vault itself
    if not top or os.path.realpath(top) != os.path.realpath(root):
        print("--resurface needs the vault's own git history (it is what says what changed when)")
        return 1
    changed = last_changes(root)
    today = datetime.date.today()
    age = lambda rel: (today - datetime.date.fromisoformat(changed[rel])).days if rel in changed else None
    notes = {rel.replace(os.sep, "/"): path for path, rel in walk_notes(root)}
    by_stem = {}
    for rel in notes:
        by_stem.setdefault(fold(os.path.splitext(os.path.basename(rel))[0]), rel)
    # is_infra reads the OS's own separator: given "a/b.md" on Windows it saw a
    # root page in every note and skipped them all (seen in CI)
    skip = lambda rel: is_infra(rel.replace("/", os.sep)) or os.path.basename(rel).lower() in ("index.md", "claude.md") \
        or rel.split("/")[0].startswith("00-")
    week = {rel for rel in notes if not skip(rel) and age(rel) is not None and age(rel) <= days}
    if not week:
        print(f"nothing changed in the last {days} days — nothing to resurface from")
        return 0

    def targets(rel):
        out = set()
        for m in LINK_RE.finditer(read(notes[rel])):
            name = m.group(1) or m.group(2)
            hit = by_stem.get(fold(os.path.splitext(os.path.basename(name.strip()))[0]))
            if hit and hit != rel:
                out.add(hit)
        return out

    links = {rel: targets(rel) for rel in notes if not skip(rel)}
    ties = {}
    for rel, outs in links.items():
        for t in outs:
            if rel in week and t not in week:
                ties.setdefault(t, set()).add(rel)
            if t in week and rel not in week:
                ties.setdefault(rel, set()).add(t)
    cands = [(rel, why) for rel, why in ties.items() if not skip(rel) and (age(rel) or 0) >= quiet]
    if not cands:
        print(f"no older note is linked with this week's {len(week)} changed notes")
        return 0
    cands.sort(key=lambda c: (-len(c[1]), -(age(c[0]) or 0)))
    print(f"older notes tied to this week ({len(week)} notes changed in {days} days):")
    for rel, why in cands[:k]:
        print(f"  {rel} — untouched for {age(rel)} days — linked with {', '.join(sorted(why)[:3])}")
    return 0


def subprocess_top(root):
    import subprocess
    try:
        r = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel"], capture_output=True,
                           text=True, timeout=5)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "--stats" in sys.argv[1:]:
        return stats(root)
    if "--resurface" in sys.argv[1:]:
        return resurface(root)
    terms, k = parse_args(sys.argv[1:])
    if terms is None:               # unknown option — already explained
        return 1
    if not terms:
        print("Usage: search.py <term> [term2 ...] [--k N] | --stats"); return 1
    scored = rank(root, terms)
    if not scored:
        print("No hits."); return 0
    for score, rel, lines in scored[:k]:
        print(f"\n[{score:5.1f}] {rel}")
        for l in lines:
            print(f"        {l}")
    return 0

def rank(root, terms):
    """[(score, vault-relative path, sample lines)], best first. The CLI above
    and exam.py both call this — so the exam measures the very ranking an
    agent sees, not a copy of it that could drift."""
    terms = [fold(t) for t in terms]
    scored = []
    for path, rel in walk_notes(root):
        text = read(path)
        if text is None:
            continue
        score, lines = score_file(text, fold(os.path.basename(rel)[:-3]), terms)
        if score:
            # Signposts are halved, not hidden. They describe where things
            # live, so they mention every topic in the vault at least once —
            # and a folder map scoring above the note it points at is how a
            # duplicate check misses the twin it was looking for. Halving
            # keeps "where is X filed?" answerable while a real note on the
            # subject always wins.
            scored.append((score * (0.5 if is_infra(rel, text) else 1.0), rel, lines))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return scored

if __name__ == "__main__":
    sys.exit(main())
