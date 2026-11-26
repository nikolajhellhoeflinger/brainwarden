#!/usr/bin/env python3
"""Brain hygiene: the link graph of the vault, as a report.

    python3 ~/Brain/.tools/hygiene.py
    python3 ~/Brain/.tools/hygiene.py --max 25
    python3 ~/Brain/.tools/hygiene.py --root /path/to/another/vault

Measures what the weekly review asks for, instead of a model guessing:

    orphans        notes nothing links to
    dead links     [[wikilinks]] and [markdown](links) whose target is gone
    near-empty     notes with almost no body (a folder whose index.md
                   carries `<!-- short-notes-ok -->` is exempt)
    unreachable    notes no index.md and no map of content points to (spec 3)
    folders        folders that carry notes but no index.md signpost
    frontmatter    missing type:/created:, or `status:` still used for maturity
    expired        notes past their own stale_after / review_due date
    supersede      "Supersedes X" without X saying "Superseded by" (spec 4.2)
    fences         an unclosed ``` fence
    portability    files that do not survive a move to another OS: not-UTF-8
                   notes, names differing only in case, names Windows refuses

Read-only, standard library only, exit code 0 even with findings (a
report, not a test). Code is masked before links are read, so an
`[[example]]` inside a rules file is not a dead link. Hidden folders
(`.git`, `.obsidian`, `.private` …) are not scanned, but links INTO them
still resolve if the file is there. While BRAINWARDEN_UNATTENDED is set it
checks only its own vault (`--max` is the one argument allowed).
"""
import collections, datetime, os, re, sys, unicodedata
from urllib.parse import unquote

# Windows writes redirected or piped output in the console codepage
# (cp1252/cp850), which has no `→` or `↳` (UnicodeEncodeError).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

SKIP_DIRS = {".git", ".obsidian", ".tools", "_templates", "node_modules",
             # kit only: overlays are half-vaults whose links resolve only
             # once copied onto a core
             "modules"}
NEAR_EMPTY_WORDS = 15
# Fallbacks only: the vault's own CLAUDE.md is the authority (schema_scale()),
# since a translated vault writes e.g. `entwurf | gültig | überholt`.
MATURITY = ("seed", "growing", "evergreen")
VALIDITY = ("draft", "stable", "deprecated")
INFRA_FILES = {"CLAUDE.md", "index.md", "Home.md", "Deadlines.md", "About me.md",
               "About this vault.md", "Inbox rule.md", "README.md",
               "THIS-COPY.md"}
# Orphans there are not a finding: captures are unlinked by definition and
# the archive is cold storage. Matched by number, not name, so translated
# folders (`90-archiv`) still count.
UNLINKED_PREFIXES = ("00-", "90-")
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "obsidian://", "ftp://", "//")

# `[text](target)` in both forms a vault contains: the angle form keeps its
# spaces (`<mit leer zeichen.md>`), the bare form allows one level of
# parentheses (`studie (2026).md`), and only a quoted "title" is dropped.
MD_LINK = re.compile(
    r"!?\[[^\]\n]*\]\("
    r"(?:<([^>\n]*)>|((?:[^()\n]|\([^()\n]*\))+?))"
    r"(?:[ \t]+(?:\"[^\"\n]*\"|'[^'\n]*'))?[ \t]*\)")

def norm(text):
    """Compare names the way a human would: case- and accent-insensitive."""
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))

# Windows refuses these: `KI: Schutz oder Überwachung.md` is fine on macOS and
# Linux, but git clone fails on it on Windows.
WIN_RESERVED = {"con", "prn", "aux", "nul"} | {f"com{i}" for i in range(1, 10)} \
                                            | {f"lpt{i}" for i in range(1, 10)}
WIN_CHARS = '<>:"|?*'

def windows_unsafe(name):
    """Why this file name cannot exist on Windows — or '' if it can."""
    hits = sorted({c for c in name if c in WIN_CHARS})
    if any(ord(c) < 32 for c in name):
        hits.append("control character")
    if hits:
        return "illegal on Windows: " + " ".join(hits)
    if name != name.rstrip(" .") and name not in (".", ".."):
        return "ends in a space or dot — Windows silently drops it"
    if os.path.splitext(name)[0].lower() in WIN_RESERVED:
        return "reserved device name on Windows"
    return ""

def mask_inline(line):
    return re.sub(r"`+[^`\n]*`+", lambda m: " " * len(m.group(0)), line)

def mask_code(text):
    """Blank out fenced blocks and `inline code`, keeping line numbers, so
    `[[wikilink]]` examples in rule files are not dead links.

    Returns (masked text, line number of an unterminated fence or None).
    After an unclosed ``` the rest is read as ordinary text and the fence
    is reported, so no link below it goes unchecked."""
    lines = text.split("\n")
    out, fence, opened_at = [], None, None
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if fence:
            out.append("")
            if stripped.startswith(fence):
                fence, opened_at = None, None
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            fence, opened_at = stripped[:3], i
            out.append("")
            continue
        out.append(mask_inline(line))
    if fence is not None:
        for i in range(opened_at, len(lines)):
            out[i] = mask_inline(lines[i])
        return "\n".join(out), opened_at + 1
    return "\n".join(out), None

# A field the setup has not filled in yet: `<YYYY-MM-DD>`, `{{DATE}}`,
# `TO FILL IN (role)`. The kit ships them; `progress.py` counts them.
PLACEHOLDER = re.compile(r"^(?:<[^>]*>|\{\{[^}]*\}\}|TO FILL IN\b|AUSFÜLLEN\b)",
                         re.I)

FRONTMATTER = re.compile(r"---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", re.S)

def frontmatter(text):
    m = FRONTMATTER.match(text)
    return m.group(1) if m else ""

def body(text):
    m = FRONTMATTER.match(text)
    return text[m.end():] if m else text

def aliases(fm):
    """`aliases:` from frontmatter, both YAML spellings.

        aliases: [Jonas Reuter, J. Reuter]
        aliases:
          - Jonas Reuter
    """
    m = re.search(r"^aliases:[ \t]*(.*)$", fm, re.M)
    if not m:
        return []
    inline = m.group(1).strip()
    if inline.startswith("["):
        return [a.strip().strip("\"'") for a in inline[1:].rstrip("]").split(",")
                if a.strip()]
    if inline:
        return [inline.strip("\"'")]
    out = []
    for line in fm[m.end():].splitlines():
        if re.match(r"^[ \t]+-[ \t]*\S", line):
            out.append(line.split("-", 1)[1].strip().strip("\"'"))
        elif line.strip():
            break
    return [a for a in out if a]


# Both directions of a supersede chain, including translated keywords
# ("Ersetzt durch"). Anchored at the START of a line (spec 4.2): `ersetzt` is
# an ordinary German verb, and a signpost entry `* [x.md](x.md) - supersedes
# the old flow` describes a replacement rather than declaring one.
LEAD = r"^[ \t]*(?:[-*>][ \t]*)?\**[ \t]*"
SUP = re.compile(LEAD + r"(supersedes\b|ersetzt(?! durch)\b|remplace\b)", re.I | re.M)
SUPBY = re.compile(LEAD + r"(superseded by\b|ersetzt durch\b|remplacé par\b)", re.I | re.M)


def schema_scale(root, key, fallback):
    """The values THIS vault uses for `maturity:` / `status:`, in the order
    its own CLAUDE.md declares them; English is only the fallback. The kit
    freezes the ORDER, not the words: position 0 is the unfinished state,
    the last position the retired one."""
    try:
        with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8-sig",
                  errors="ignore") as fh:
            rules = fh.read()
    except OSError:
        return list(fallback)
    # the value ends at the `#` comment the schema line usually carries
    hit = re.search(rf"^{key}:[ \t]*([^\n#]*\|[^\n#]*?)[ \t]*(?:#.*)?$", rules, re.M)
    if not hit:
        return list(fallback)
    values = [w.strip().lower() for w in hit.group(1).split("|") if w.strip()]
    return values or list(fallback)


def superseded_pattern(retired):
    """A note that has been replaced. Its folder's index.md drops it (the
    signpost lists what applies), so it is exempt from "unreachable"."""
    words = "|".join(re.escape(v) for v in dict.fromkeys(list(retired) + ["deprecated"]))
    return re.compile(SUPBY.pattern + rf"|^[ \t]*status:[ \t]*(?:{words})\b",
                      re.M | re.I)


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
    """Kit scaffolding rather than a note, by three rules in order of how
    well they survive translation: the `<!-- kit-page -->` marker; any file
    in the vault ROOT (notes live in numbered folders); the English name
    list (`Termine.md` in a German vault would miss it)."""
    return (KIT_PAGE in text[:2000] or os.sep not in rel
            or os.path.basename(rel) in INFRA_FILES)

def top_folder(rel):
    return rel.split(os.sep)[0] if os.sep in rel else "(root)"

def unlinked_ok(rel):
    return top_folder(rel).startswith(UNLINKED_PREFIXES)


def is_inbox(rel):
    return top_folder(rel).startswith("00-")


def is_material(rel):
    """The archive's raw folder holds the SOURCES an ingest was made from
    (PDFs, articles, transcripts): material, not notes, so every
    note-shaped check skips them. Matched by shape: any `90-*` folder, any
    subfolder whose name contains `raw` (`raw/`, `raw-verarbeitet/`)."""
    parts = rel.replace(os.sep, "/").split("/")
    return (len(parts) > 2 and parts[0].startswith("90-")
            and "raw" in parts[1].lower())


def read_ignores(root):
    """Folders another system writes into (an assistant's memory, a Zotero
    export, a plugin's daily notes), from `.hygieneignore` in the root.
    Their files never follow this schema and would drown the real findings.

    One folder path per line, `#` starts a comment. The header names the
    skipped folders and how many notes they hold."""
    path = os.path.join(root, ".hygieneignore")
    out = []
    try:
        with open(path, encoding="utf-8-sig", errors="ignore") as fh:
            for line in fh:
                line = line.split("#")[0].strip().strip("/")
                if line:
                    out.append(line.replace("\\", "/"))
    except OSError:
        pass
    return out

class Vault:
    """The vault as a link graph. Reads every note exactly once."""

    def __init__(self, root):
        self.root = root
        self.notes = {}     # rel -> raw text
        self.masked = {}    # rel -> same text, code blanked out
        self.files = set()  # every file (incl. attachments), for link resolution
        self.by_name = {}   # normalised name/stem -> rel (first wins, like Obsidian)
        self.by_path_ci = {}    # lowercased rel path -> real rel path
        self.by_nfc = {}        # NFC rel path -> real rel path: macOS may store "ü" as u + ¨
        self.unterminated = []  # notes with an unclosed ``` fence
        self.mojibake = []      # files that are not valid UTF-8
        self.case_clash = []    # names that differ only in case
        self.odd_names = []     # names that cannot exist on Windows
        # A path the walk cannot enter is unmeasured, not clean. os.walk
        # swallows the error by default; collect it for the header instead.
        self.unreadable = []
        for dirpath, dirs, files in os.walk(root, onerror=self.unreadable.append):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith("."))
            # folder names too (`Q&A: 2026`, `Notizen `)
            for d in dirs:
                bad = windows_unsafe(d)
                if bad:
                    self.odd_names.append(
                        os.path.relpath(os.path.join(dirpath, d), root) + f"/ — {bad}")
            for f in sorted(files):
                rel = os.path.relpath(os.path.join(dirpath, f), root)
                self.files.add(rel)
                self.by_nfc.setdefault(unicodedata.normalize("NFC", rel), rel)
                key_ci = rel.replace(os.sep, "/").lower()
                # Names differing only in case coexist on Linux but NOT on
                # macOS or Windows: a copy there silently loses one.
                if key_ci in self.by_path_ci:
                    self.case_clash.append(f"{self.by_path_ci[key_ci]}  vs  {rel}")
                else:
                    self.by_path_ci[key_ci] = rel
                bad = windows_unsafe(os.path.basename(rel))
                if bad:
                    self.odd_names.append(f"{rel} — {bad}")
                for key in {norm(f), norm(os.path.splitext(f)[0])}:
                    self.by_name.setdefault(key, rel)
                if f.endswith(".md") and not (f.startswith("_")
                                              and ist_vorlage(os.path.join(dirpath, f))):
                    try:
                        raw = open(os.path.join(dirpath, f), "rb").read()
                    except OSError as e:
                        # otherwise the note would be in no rubric at all
                        self.unreadable.append(e)
                        continue
                    # utf-8-sig: a byte-order mark would hide the frontmatter.
                    # A note saved as cp1252 or UTF-16 (Notepad "ANSI",
                    # PowerShell 5.1 `>`) is unreadable here and in Obsidian:
                    # report it.
                    try:
                        text = raw.decode("utf-8-sig")
                    except UnicodeDecodeError:
                        self.mojibake.append(rel)
                        text = raw.decode("utf-8-sig", errors="ignore")
                    else:
                        if "\x00" in text:      # UTF-16 without a BOM
                            self.mojibake.append(rel)
                    self.notes[rel] = text
                    self.masked[rel], fence_line = mask_code(text)
                    if fence_line:
                        self.unterminated.append(f"{rel}:{fence_line}")
                    # Obsidian resolves `aliases:`, so a link to one is live.
                    for alias in aliases(frontmatter(text)):
                        self.by_name.setdefault(norm(alias), rel)

    def links(self, rel, only_lines_matching=None):
        """Internal links of a note as (target, line number, raw form).

        `only_lines_matching`: a compiled regex — then only links on lines
        that match it are returned (used for the Supersedes/Superseded pairs)."""
        for n, line in enumerate(self.masked[rel].split("\n"), 1):
            if only_lines_matching and not only_lines_matching.search(line):
                continue
            # The substring guards prevent quadratic backtracking of the
            # link regex on long lines full of `[` without a closing `)`.
            if "[[" in line:
                for m in re.finditer(r"!?\[\[([^\]\n|#^]*)", line):
                    target = m.group(1).strip()
                    if target:
                        yield target, n, f"[[{target}]]"
            if "](" in line:
                for m in MD_LINK.finditer(line):
                    target = (m.group(1) if m.group(1) is not None else m.group(2)).strip()
                    target = unquote(target.split("#")[0]).strip()
                    if target and not target.startswith(EXTERNAL) and not target.startswith("#"):
                        yield target, n, f"({target})"

    def resolve(self, target, source):
        """Obsidian-style: by path (relative to the note, then to the vault
        root), otherwise by file name anywhere. Returns a rel path or None.

        The name fallback applies ONLY to bare names (`[[Some note]]`): a
        broken `../gone/index.md` must not land on some other `index.md`."""
        # backslashes from Windows, so all three systems give the same answer
        tgt = target.replace("\\", "/")
        # A leading `/` means the vault root, never the disk root: os.path.join
        # would resolve `[boot](/etc/passwd)` against the real filesystem.
        tgt = tgt.lstrip("/")
        if not tgt:
            return None
        for base in (os.path.dirname(source), ""):
            for suffix in ("", ".md"):
                cand = os.path.normpath(os.path.join(base, tgt + suffix))
                # `../../x` climbs OUT of the vault: never resolved
                if cand.startswith(".." + os.sep) or cand == "..":
                    continue
                if cand in self.files or self.exists_exact(cand):
                    return cand
                if unicodedata.normalize("NFC", cand) in self.by_nfc:
                    return self.by_nfc[unicodedata.normalize("NFC", cand)]
        if "/" in tgt or tgt.startswith("."):
            return None
        return self.by_name.get(norm(os.path.basename(tgt)))

    def exists_exact(self, cand):
        """Does this path exist with EXACTLY this spelling? `os.path.exists`
        accepts `ZIEL.md` for `Ziel.md` on macOS and Windows, not on Linux.
        Only files outside the walk (hidden folders) get here."""
        full = os.path.join(self.root, cand)
        if not os.path.exists(full):
            return False
        head, name = os.path.split(full)
        try:
            return name in os.listdir(head or ".")
        except OSError:
            return False

    def case_variant(self, target, source):
        """The real file a link would have hit if case were ignored, so the
        report can say "you wrote ZIEL.md, the file is Ziel.md"."""
        tgt = target.replace("\\", "/")
        for base in (os.path.dirname(source), ""):
            for suffix in ("", ".md"):
                cand = os.path.normpath(os.path.join(base, tgt + suffix))
                real = self.by_path_ci.get(cand.replace(os.sep, "/").lower())
                if real and real != cand:
                    return real
        return None

    def is_signpost(self, rel):
        """index.md, Home.md and maps of content — the way INTO a folder."""
        name = os.path.basename(rel)
        return (name in ("index.md", "Home.md")
                or "moc" in norm(os.path.splitext(name)[0]).replace("-", " ").replace("_", " ").split()
                or bool(re.search(r"^type:\s*moc\b", frontmatter(self.notes[rel]), re.M)))

def report(title, items, limit, note=""):
    print(f"\n{title}: {len(items)}{note}")
    for line in items[:limit]:
        print(f"  {line}")
    if len(items) > limit:
        print(f"  … and {len(items) - limit} more")

def vault_mode(root):
    """(mode, why) — personal | professional | company, from the vault's CLAUDE.md.

    The mode decides which frontmatter fields are required. `why` is empty
    when the mode was found, and explains the fallback otherwise: `personal`
    is the LOOSEST schema, so a silent fallback would hide missing fields."""
    try:
        text = open(os.path.join(root, "CLAUDE.md"), encoding="utf-8-sig",
                    errors="ignore").read()
    except OSError:
        return "personal", "not detected — no CLAUDE.md in the vault root"
    # The label may be translated ("Betriebsart:"), the VALUE is frozen by
    # the kit: match the value on a mode-declaration line.
    m = re.search(r"^\*\*[^\n:]{0,40}:\s*(personal|professional|company)\b",
                  text, re.M | re.I)
    if m and m.group(1).lower() in ("personal", "professional", "company"):
        return m.group(1).lower(), ""
    # A company overlay names itself in its heading before setup fills the
    # line (English only; a translated one falls through to the layout test).
    if re.search(r"^#.*company knowledge vault", text, re.M | re.I):
        return "company", ""
    # Layout fallback: `company` is the only mode with 70-/80- and without
    # 10-/20-.
    try:
        tops = {n[:3] for n in os.listdir(root)
                if os.path.isdir(os.path.join(root, n))}
    except OSError:
        tops = set()
    if tops & {"70-", "80-"} and not tops & {"10-", "20-"}:
        return "company", "not stated in CLAUDE.md — read from the folder layout"
    if "{{MODE}}" in text:
        return "personal", ("NOT SET — CLAUDE.md still contains {{MODE}}; "
                            "setup step 5e never ran")
    return "personal", "not detected — no mode line in CLAUDE.md"

def main():
    argv = sys.argv[1:]
    if os.environ.get("BRAINWARDEN_UNATTENDED") and any(a != "--max" and not a.isdigit() for a in argv):
        # unattended: THIS vault only; a path would report on a folder
        # outside it
        print("refused while unattended: only `hygiene.py` on this vault (other folders in a normal chat)")
        return 2
    limit, root = 10, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # A bare path is the vault, like --root.
    skip = False
    for i, a in enumerate(argv):
        if skip:
            skip = False
            continue
        if a == "--max" and i + 1 < len(argv):
            try:
                limit = max(1, int(argv[i + 1]))
            except ValueError:
                pass
            skip = True
        elif a == "--root" and i + 1 < len(argv):
            root = os.path.abspath(os.path.expanduser(argv[i + 1]))
            skip = True
        elif a.startswith("-"):
            print(__doc__.strip()); return 1
        else:
            root = os.path.abspath(os.path.expanduser(a))
    if not os.path.isdir(root):
        print(f"No vault at {root}"); return 1

    v = Vault(root)
    if not v.notes:
        print(f"hygiene — {root}\nNo notes found (is this a vault?)"); return 0

    ignores = read_ignores(root)

    def ignored(rel):
        """Inside a folder listed in `.hygieneignore`."""
        p = rel.replace(os.sep, "/")
        return any(p == i or p.startswith(i + "/") for i in ignores)

    ignored_notes = sorted(r for r in v.notes if ignored(r))
    ignored_folders = sorted({i for i in ignores
                              if any(r.replace(os.sep, "/").startswith(i)
                                     for r in ignored_notes)})

    signposts = {rel for rel in v.notes if v.is_signpost(rel)}
    inbound = collections.Counter()
    dead, signposted = [], set()
    graph = collections.defaultdict(set)
    for rel in sorted(v.notes):
        if ignored(rel):
            continue
        for target, line, raw in v.links(rel):
            hit = v.resolve(target, rel)
            if hit is None:
                variant = v.case_variant(target, rel)
                dead.append(f"{rel}:{line} → {raw}" + (
                    f"  [the file is {variant} — only the spelling differs, "
                    "which is a dead link on Linux]" if variant else ""))
            elif hit != rel:
                inbound[hit] += 1
                if hit in v.notes:
                    graph[rel].add(hit)

    # Reachable = a PATH of links leads here from some signpost; an index.md
    # lists only the ways in, not every file.
    queue = list(signposts)
    while queue:
        for nxt in graph.get(queue.pop(), ()):
            if nxt not in signposted:
                signposted.add(nxt)
                queue.append(nxt)

    # A folder may declare in its OWN index.md that its notes are short (a
    # glossary, quotes). Unlike `.hygieneignore`, only this rubric is muted.
    short_ok = set()
    for rel in v.notes:
        if os.path.basename(rel) == "index.md" and "<!-- short-notes-ok" in v.notes[rel]:
            short_ok.add(os.path.dirname(rel))

    orphans, near_empty, gaps, expired = [], [], [], []
    mode, mode_note = vault_mode(root)
    # both vocabularies: a half-translated vault has notes in each
    maturity_values = set(schema_scale(root, "maturity", MATURITY)) | set(MATURITY)
    validity_values = schema_scale(root, "status", VALIDITY)
    superseded = superseded_pattern([validity_values[-1], VALIDITY[-1]])
    today = datetime.date.today().isoformat()
    gap_counts = collections.Counter()
    for rel, text in sorted(v.notes.items()):
        if ignored(rel):
            continue
        if not is_infra(rel, text) and not unlinked_ok(rel) and not inbound[rel]:
            orphans.append(rel)
        words = len(body(text).split())
        # inbox captures are supposed to be short; flagging them would
        # discourage capturing
        if not is_infra(rel, text) and words < NEAR_EMPTY_WORDS \
                and not is_inbox(rel) and not is_material(rel) \
                and os.path.dirname(rel) not in short_ok:
            near_empty.append(f"{rel} ({words} words)")
        # Inbox captures and the raw sources `brain-ingest` files away need
        # no frontmatter.
        if is_infra(rel, text) or is_inbox(rel) or is_material(rel):
            continue
        fm, missing = frontmatter(text), []
        if not re.search(r"^type:\s*\S", fm, re.M):
            missing.append("no type:")
        if not re.search(r"^created:\s*\S", fm, re.M):
            missing.append("no created:")
        s = re.search(r"^status:\s*([^\s#]+)", fm, re.M)
        if s and s.group(1).lower() in maturity_values:
            missing.append("`status:` still used for maturity")
        # Mode-dependent required fields. `ownership:` decides what has to be
        # handed over when a job ends.
        if mode == "professional" and not re.search(r"^ownership:\s*\S", fm, re.M):
            missing.append("no ownership:")
        if mode == "company":
            for field in ("owner", "status", "audience", "confidentiality"):
                if not re.search(rf"^{field}:\s*\S", fm, re.M):
                    missing.append(f"no {field}:")
        if missing:
            gap_counts.update(missing)
            gaps.append(f"{rel} — {', '.join(missing)}")
        # Expiry dates. Quoted and unpadded ISO dates are read; any other
        # value (`01.01.2020`) is reported as unreadable, since it could
        # never expire.
        for field in ("stale_after", "review_due"):
            m = re.search(rf"^{field}:[ \t]*(.+?)[ \t]*$", fm, re.M)
            if not m:
                continue
            value = m.group(1).split(" #")[0].strip().strip("\"'")
            iso = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})$", value)
            if iso:
                day = "%04d-%02d-%02d" % tuple(int(g) for g in iso.groups())
                if day < today:
                    expired.append(f"{rel} — {field}: {value}")
            elif value and not PLACEHOLDER.match(value):
                # An UNFILLED placeholder is not reported: `progress.py`
                # counts `<…>` and `{{…}}`, and a fresh vault starts at zero.
                expired.append(f"{rel} — {field}: {value!r} is not a readable "
                               "date (YYYY-MM-DD) — nothing can ever expire it")

    # Reachability only means something where a folder HAS a signpost —
    # otherwise the missing index.md is the finding, not the notes.
    unreachable, no_index, folders = [], [], collections.defaultdict(list)
    for rel in v.notes:
        folders[os.path.dirname(rel)].append(rel)
    for folder, members in sorted(folders.items()):
        real = sorted(r for r in members
                      if not is_infra(r, v.notes[r]) and not unlinked_ok(r) and not ignored(r))
        if not real:
            continue
        if os.path.join(folder, "index.md") in v.notes:
            unreachable += [r for r in real if r not in signposted
                            and not superseded.search(v.notes[r])]
        else:
            no_index.append((len(real), f"{folder or '(root)'} ({len(real)} notes)"))
    no_index = [line for _, line in sorted(no_index, reverse=True)]

    chains, seen = [], set()
    # SUP / SUPBY: the same patterns the `unreachable` exemption uses.
    for rel in sorted(v.notes):
        for keyword, back, phrase in ((SUP, SUPBY, "Superseded by"), (SUPBY, SUP, "Supersedes")):
            for target, line, raw in v.links(rel, keyword):
                hit = v.resolve(target, rel)
                if not hit or hit not in v.notes or hit == rel:
                    continue
                partners = {v.resolve(t, hit) for t, _, _ in v.links(hit, back)}
                if rel not in partners and (rel, hit, phrase) not in seen:
                    seen.add((rel, hit, phrase))
                    chains.append(f'{rel}:{line} → {hit}, but {hit} has no "{phrase}" back to it')

    print(f"hygiene — {root}")
    print(f"mode: {mode}" + (f" ({mode_note})" if mode_note else ""))
    print(f"{len(v.notes)} notes scanned ({len([r for r in v.notes if is_infra(r, v.notes[r])])} kit files, "
          f"{len(signposts)} signposts)")
    if ignored_notes:
        # named, never silent: an invisible exemption looks like a dead check
        print(f"skipped via .hygieneignore: {len(ignored_notes)} notes in "
              f"{', '.join(ignored_folders)}")
    if v.unreadable:
        # Not a rubric: this says "the report is incomplete", not "the vault
        # has a defect".
        print(f"could not be read, so NOT checked — {len(v.unreadable)} path(s):")
        for e in v.unreadable[:limit]:
            path = getattr(e, "filename", None) or str(e)
            print(f"  {path} — {getattr(e, 'strerror', None) or 'unreadable'}")
        if len(v.unreadable) > limit:
            print(f"  … and {len(v.unreadable) - limit} more")
    report("orphans — nothing links here (excl. inbox 00-*, archive 90-*)", orphans, limit)
    report("dead links — target does not exist", dead, limit)
    report(f"near-empty — under {NEAR_EMPTY_WORDS} words of body", near_empty, limit)
    report("not reachable from a signpost (index.md / MOC / Home)", unreachable, limit)
    report("folders with notes but no index.md (spec 3)", no_index, limit)
    report("frontmatter gaps", gaps, limit,
           note=" (" + " · ".join(f"{k} {n}" for k, n in sorted(gap_counts.items())) + ")"
           if gap_counts else "")
    report("past their own expiry date (stale_after / review_due)", expired, limit)
    report("supersede chains without a back-reference (spec 4.2)", chains, limit)
    report("unterminated ``` fence — links below it were never checked",
           v.unterminated, limit)
    portability = ([f"{r} — not valid UTF-8 (save it as UTF-8; search cannot "
                    "read it and Obsidian shows rubbish)" for r in v.mojibake]
                   + [f"{c} — names differ only in case; macOS and Windows "
                      "cannot hold both" for c in v.case_clash]
                   + v.odd_names)
    report("portability — breaks on another operating system", portability, limit)
    return 0

if __name__ == "__main__":
    sys.exit(main())
