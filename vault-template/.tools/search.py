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

Body mentions have diminishing returns and stay under one title hit, so
the file NAMED after a term beats a log that merely repeats it, while ten
mentions still rank above three.

Hits INSIDE a word count, for German compounds (`Vertrag` must find
`Rahmenvertrag`). They count LESS than a word start and are capped per
term, so `test` cannot flood a file that only says `fastest` to the top.
Terms shorter than 4 characters match at word starts only.

Accent-insensitive (cafe matches café, Strasse matches Straße). Output:
top-k files with matching lines — Claude then reads ONLY those files.
"""
import os, re, sys, unicodedata

# Windows writes redirected or piped output in the console codepage
# (cp1252/cp850), which has no `↳` (UnicodeEncodeError).
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
    """The scales THIS vault uses, read from its own CLAUDE.md (a translated
    vault writes `status: entwurf | gültig | überholt`). English is only
    the fallback."""
    m, v = set(MATURITY), set(VALIDITY)
    try:
        with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8-sig",
                  errors="ignore") as fh:
            rules = fh.read()
    except OSError:
        return m, v
    for key, target in (("maturity", m), ("status", v)):
        # the value ends at the `#` comment the schema line usually carries
        hit = re.search(rf"^{key}:[ \t]*([^\n#]*\|[^\n#]*?)[ \t]*(?:#.*)?$",
                        rules, re.M)
        if hit:
            target.update(w.strip().lower() for w in hit.group(1).split("|")
                          if w.strip())
    return m, v

# Kit infrastructure, not notes: counting them would inflate every number.
INFRA_FILES = {"CLAUDE.md", "index.md", "Home.md", "Deadlines.md",
               "About me.md", "About this vault.md", "Inbox rule.md",
               "README.md", "THIS-COPY.md"}

def plural(n, word):
    return f"{n} {word}" + ("" if n == 1 else "s")

UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})

def fold(text):
    """Lowercase, German umlauts as their two-letter spelling, other accents
    stripped, so a query matches however the note was written.

    `ä` is `ae`, not `a`: `länge` must find `interviewlaenge`, and
    schon/schön must stay different words. Composed first (NFC), because
    macOS hands out file names decomposed. cafe still matches café."""
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
            # Unknown flags are an error, not search terms. There is no
            # --root: the tool searches the vault it lives in.
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
        # hidden folders skipped as in hygiene.py (`.claude/skills/`,
        # `.private/` are not notes)
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
    """The `# heading` and the first lines of prose under it, where a note
    says what it is ABOUT. Counted like tags: once per term, so a note
    that says "lawyer" once here beats notes mentioning it on many lines."""
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
        # Only prose is a lead: a list or table is content, and a log's
        # first bullet is an event, not the subject.
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
    """The YAML block at the very top and nothing else, so YAML examples
    in code blocks are not read as fields."""
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
    """A template file, recognised by content, not name: a leading `_` alone
    (`_privat.md`) is an ordinary note. Templates next to notes
    (`40-decisions/_template.md`, translated `_vorlage.md`) still contain
    their `{{` placeholders, in any language."""
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as fh:
            return "{{" in fh.read(4000)
    except OSError:
        return False


def is_infra(rel, text=""):
    """Kit scaffolding: root/folder signposts and the raw/ readme.

    Three rules, in order of how well they survive translation: the
    `<!-- kit-page -->` marker; any file in the vault ROOT (notes live in
    numbered folders); the English name list for vaults built before the
    marker existed."""
    return (KIT_PAGE in text[:2000] or os.sep not in rel
            or os.path.basename(rel) in INFRA_FILES)

def git_reviews(root):
    """Review history, only if the vault IS a git repo: `git -C <vault> log`
    also answers from a PARENT repository."""
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
    # days, not commits: one review often makes several commits
    days = len(set(log))
    return f"reviews: {days} day{'s' if days != 1 else ''} (last {log[0]})"

def stats(root):
    """--stats: numbers about this vault (folders, maturity, age)."""
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
        # Diminishing returns: the first mention is worth a full W_BODY, the
        # hundredth almost nothing, and the total never reaches BODY_CAP. A
        # hard cap would tie every file with five or more mentions.
        score += BODY_CAP * hits / (hits + BODY_HALF) + inside_score
    return score, (starts + insides)[:3]

LINK_RE = re.compile(r"\[\[([^\]|#]+)|\]\(([^)#\s]+\.md)\)")


def last_changes(root):
    """{relpath: date of its last commit} in one pass over the history —
    file times lie (a fresh clone sets every one of them to today)."""
    import subprocess
    try:
        # quotePath=false: otherwise git prints "\303\234ber.md" for Über.md, and no note matches
        out = subprocess.run(["git", "-C", root, "-c", "core.quotePath=false", "log", "--format=@%as",
                              "--name-only", "--no-renames"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace",
                             timeout=30).stdout
    except Exception:
        return {}
    seen, day = {}, None
    for line in out.splitlines():
        if line.startswith("@"):
            day = line[1:]
        elif line.strip() and day:
            seen.setdefault(unicodedata.normalize("NFC", line.strip().strip('"')), day)
    return seen


def resurface(root, k=3, days=7, quiet=60):
    """--resurface: older notes connected to what this week is about. A
    note qualifies if THIS week's notes link to it or it links to them, and
    it has not been touched for two months."""
    import datetime
    top = subprocess_top(root)       # realpath("") would be the CURRENT folder, i.e. the vault itself
    if not top or os.path.realpath(top) != os.path.realpath(root):
        print("--resurface needs the vault's own git history (it is what says what changed when)")
        return 1
    changed = last_changes(root)
    today = datetime.date.today()
    nfc = lambda rel: unicodedata.normalize("NFC", rel)     # macOS may hand out either form of an umlaut
    age = lambda rel: (today - datetime.date.fromisoformat(changed[nfc(rel)])).days if nfc(rel) in changed else None
    notes = {rel.replace(os.sep, "/"): path for path, rel in walk_notes(root)}
    by_stem = {}
    for rel in notes:
        by_stem.setdefault(fold(os.path.splitext(os.path.basename(rel))[0]), rel)
    # is_infra reads the OS's own separator: on Windows "a/b.md" would look
    # like a root page
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
    """[(score, vault-relative path, sample lines)], best first. The CLI and
    exam.py both call this, so the exam measures the ranking an agent sees."""
    terms = [fold(t) for t in terms]
    scored = []
    for path, rel in walk_notes(root):
        text = read(path)
        if text is None:
            continue
        score, lines = score_file(text, fold(os.path.basename(rel)[:-3]), terms)
        if score:
            # Signposts are halved, not hidden: they mention every topic, so
            # a real note on the subject must win, while "where is X filed?"
            # stays answerable.
            scored.append((score * (0.5 if is_infra(rel, text) else 1.0), rel, lines))
    scored.sort(key=lambda s: (-s[0], s[1]))
    return scored

if __name__ == "__main__":
    sys.exit(main())
