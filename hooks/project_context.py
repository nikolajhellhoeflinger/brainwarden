#!/usr/bin/env python3
"""Brainwarden — project context (Claude Code "SessionStart" hook, opt-in).

The gap this closes: the brain knows that the shop's checkout was decided
against PayPal in March, that the launch is on the 14th and that one
question is still open. A session started in the shop's code folder knows
none of it, unless somebody remembers to ask. So decisions get re-made,
dates get missed, and the brain is right but not there.

What it does: when a session starts in a folder that belongs to one of the
brain's projects, Claude gets a short brief — the project note, the newest
decisions that mention the project, its next dates and open points — and the
paths to read before changing direction. In every other folder it prints
nothing at all.

Why per project and not global: a hook that pours the brain into EVERY
session leaks. Private notes end up in a client's repository session, the
note list in a screen share, a thousand tokens in front of every one-line
question. This one speaks only where the person has already said "this
folder is that project", or where the folder carries the project's name.

Which folder belongs to which project:
  1. Explicitly — the project note says so in its frontmatter:
         folders: [~/code/shop, ~/code/shop-api]
     A session anywhere inside one of them matches. The deepest wins.
  2. By name — the repository's folder name (or, outside a repository, the
     folder's) equals the note's file name or one of its `aliases:`,
     ignoring case and spaces vs. hyphens: `~/code/Acme-Shop` ↔ `Acme-Shop.md`.
     Suffixes are dropped one hyphen at a time: `acme-shop-api` →
     `acme-shop` → match. Never the other way round: `~/code/acme` does
     NOT match `Acme-Shop.md` — a short folder name would match everything.
Inside a vault it stays silent (the vault's own CLAUDE.md is loaded there),
on `resume` too (that session has the brief already).

What it deliberately does not do: it writes nothing, calls no model, opens
no network connection, reads no person notes. It reads the projects folder,
the decisions folder and the vault's top-level notes (for dates), stops at
a size cap, and on any error it prints nothing — a broken brain must never
break the start of a session. What it prints is the person's own notes,
handed over as material: the brief says so, and a session the person sits
in asks before it acts.

Install (opt-in):

  1. copy to  <config>/hooks/project_context.py
  2. add to the "SessionStart" hooks in <config>/settings.json:

     {"hooks": {"SessionStart": [{"hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/project_context.py"}
     ]}]}}

Try it in any folder, without Claude:
  echo '{"cwd": "'"$PWD"'", "source": "startup"}' | python3 ~/.claude/hooks/project_context.py
Uninstall: delete the file and the entry.
"""
import datetime as dt
import json
import os
import re
import sys
import unicodedata

MAX_CHARS = 2200         # the whole brief (~550 tokens); one that needs scrolling is not a brief
LINE = 150               # one line of it
READ_BYTES = 65536       # per note: the head carries what the brief needs
SHOW = 3                 # per list
MIN_NAME = 4             # shorter names match too much text to count as a mention
DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})|(\d{1,2})\.(\d{1,2})\.(\d{4})")
VAULT_MARK = re.compile(r"^\s*(?:\*\*)?(?:Vault mode|Kit version|Mode)\s*:", re.M | re.I)


# ------------------------------------------------------------------ reading
def config_dir():
    return os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))


def vault_path():
    """The `Brain vault:` line of the global rules — the line every brain-*
    skill follows — read the way people actually write it: bold, in
    backticks, with a remark after a dash."""
    try:
        with open(os.path.join(config_dir(), "CLAUDE.md"), encoding="utf-8-sig", errors="ignore") as fh:
            for line in fh:
                m = re.match(r"\s*[-*]?\s*(?:\*\*)?\s*Brain vault:\s*(?:\*\*)?\s*(.+)", line)
                if not m:
                    continue
                rest = m.group(1).strip()
                quoted = re.match(r"`([^`]+)`", rest)
                path = quoted.group(1) if quoted else re.split(r"\s+(?:<|←|#|—|–|\(|- )", rest)[0]
                path = path.strip().strip("\"'")
                if path:
                    return os.path.realpath(os.path.expanduser(path))
    except OSError:
        pass
    return os.path.realpath(os.path.expanduser("~/Brain"))


def read(path):
    try:
        with open(path, "rb") as fh:
            return unicodedata.normalize("NFC", fh.read(READ_BYTES).decode("utf-8", "replace"))
    except OSError:
        return ""


def split_front(text):
    """(frontmatter dict of raw strings, body). Only `key: value` and
    block lists — enough for folders/aliases/status/title."""
    front = {}
    if not text.startswith("---"):
        return front, text
    end = text.find("\n---", 3)
    if end < 0:
        return front, text
    key = None
    for line in text[3:end].splitlines():
        m = re.match(r"([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            key, value = m.group(1).lower(), m.group(2).split(" #")[0].strip()
            front[key] = value
        elif key and re.match(r"\s+-\s+", line):
            front[key] = (front[key] + "," if front[key] else "") + line.strip()[1:].strip()
    return front, text[end + 4:]


def as_list(value):
    value = (value or "").strip().strip("[]")
    return [v.strip().strip("\"'") for v in value.split(",") if v.strip().strip("\"'")]


def norm(name):
    name = unicodedata.normalize("NFC", name).strip().lower()
    return re.sub(r"[\s_]+", "-", name)


LINK = re.compile(r"\[\[([^\]|]*\|)?([^\]]*)\]\]")


def clean(line):
    line = re.sub(r"<!--.*?-->", "", line)
    line = LINK.sub(lambda m: m.group(2), line)          # [[note|shown]] → shown
    line = re.sub(r"\*\*|__", "", line)
    line = re.sub(r"\s+", " ", line).strip()
    return line if len(line) <= LINE else line[:LINE - 1].rstrip() + "…"


# ------------------------------------------------------------ the vault map
def numbered(vault):
    try:
        return sorted(n for n in os.listdir(vault)
                      if re.match(r"\d\d-", n) and os.path.isdir(os.path.join(vault, n)))
    except OSError:
        return []


def folders(vault):
    """(projects, decisions), found the way the other tools find theirs: the
    decisions folder by its number (40-), the projects folder by its name in
    any language that spells it with "proj" (projects, Projekte, proyectos,
    projets, progetti …) — its number differs between vault layouts."""
    names = numbered(vault)
    proj = next((n for n in names if "proj" in n.lower() or "progett" in n.lower()), None)
    dec = next((n for n in names if n.startswith("40-")), None)
    return (os.path.join(vault, proj) if proj else None), (os.path.join(vault, dec) if dec else None)


def project_notes(proj_dir):
    """Project hubs: notes in the projects folder (one level of subfolders
    too), without signposts, templates and dated episode notes."""
    out = []
    for root, dirs, files in os.walk(proj_dir):
        dirs[:] = [d for d in dirs if not d.startswith((".", "_"))] if root == proj_dir else []
        for f in files:
            if not f.endswith(".md") or f.startswith(("_", ".")) or f.lower() in ("index.md", "claude.md"):
                continue
            if re.match(r"\d{4}-\d{2}-\d{2}", f):
                continue
            out.append(os.path.join(root, f))
    return out


def inside(path, folder):
    return path == folder or path.startswith(folder.rstrip(os.sep) + os.sep)


def repo_root(cwd):
    here = cwd
    while True:
        if os.path.exists(os.path.join(here, ".git")):
            return here
        up = os.path.dirname(here)
        if up == here:
            return cwd
        here = up


def in_some_vault(cwd, vault):
    """The configured vault, or any folder above cwd whose CLAUDE.md carries
    a vault's mode line (a company vault started on its own)."""
    if inside(cwd, vault):
        return True
    here = cwd
    for _ in range(12):
        text = read(os.path.join(here, "CLAUDE.md"))
        if text and VAULT_MARK.search(text):
            return True
        up = os.path.dirname(here)
        if up == here:
            break
        here = up
    return False


def find_project(cwd, notes):
    explicit = []
    named = {}
    for path in notes:
        front, _ = split_front(read(path))
        if front.get("status", "").lower() == "deprecated":
            continue
        for f in as_list(front.get("folders")) + as_list(front.get("folder")):
            real = os.path.realpath(os.path.expanduser(f))
            if inside(cwd, real):
                explicit.append((len(real), path))
        stem = os.path.splitext(os.path.basename(path))[0]
        for n in [stem] + as_list(front.get("aliases")):
            named.setdefault(norm(n), path)
    if explicit:
        return max(explicit)[1]
    name = norm(os.path.basename(repo_root(cwd)))
    while name:
        if name in named:
            return named[name]
        if "-" not in name:
            break
        name = name.rsplit("-", 1)[0]
        if len(name) < MIN_NAME:
            break
    return None


# ------------------------------------------------------------------ the brief
def names_of(path):
    front, _ = split_front(read(path))
    stem = os.path.splitext(os.path.basename(path))[0]
    names = {stem, stem.replace("-", " ")}
    names |= set(as_list(front.get("aliases")))
    if front.get("title") and not front["title"].startswith("<"):
        names.add(front["title"].strip("\"'"))
    return [n.lower() for n in names if len(n) >= MIN_NAME]


def mentions(text, names):
    low = text.lower()
    return any(re.search(r"(?<!\w)" + re.escape(n) + r"(?!\w)", low) for n in names)


def lead(body):
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "|", ">", "```", "<!--", "- ", "* ", "+ ", "---")):
            continue
        return clean(s)
    return ""


def open_points(body):
    steps, asks = [], []
    for line in body.splitlines():
        m = re.match(r"\s*[-*] \[ \] (.+)", line)
        if m and not m.group(1).strip().startswith("<"):
            steps.append(clean(m.group(1)))
        elif re.search(r"\b(open|offen|abierto|ouvert|aperto)\s*→", line, re.I):
            asks.append(clean(line.lstrip("-* ")))
    return steps, asks


def decisions(dec_dir, names):
    found = []
    try:
        files = sorted(os.listdir(dec_dir), reverse=True)
    except OSError:
        return 0, []
    for f in files:
        if not f.endswith(".md") or f.startswith(("_", ".")) or f.lower() in ("index.md", "claude.md"):
            continue
        text = read(os.path.join(dec_dir, f))
        front, body = split_front(text)
        if front.get("status", "").lower() == "deprecated" or not mentions(text, names):
            continue
        title = next((l[2:].strip() for l in body.splitlines() if l.startswith("# ")), f[:-3])
        day = f[:10] if re.match(r"\d{4}-\d{2}-\d{2}", f) else front.get("created", "")[:10]
        found.append((day, clean(title), os.path.basename(dec_dir) + "/" + f))
    found.sort(reverse=True)
    return len(found), found[:SHOW]


def to_date(m):
    try:
        if m.group(1):
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return dt.date(int(m.group(6)), int(m.group(5)), int(m.group(4)))
    except ValueError:
        return None


def coming_dates(vault, project_path, names, today):
    """Dated lines ahead of today: from the top-level notes (Deadlines and
    the like) when they mention the project, and from the project note
    itself. Home is skipped: it mirrors Deadlines and would only repeat it."""
    sources = [project_path]
    try:
        sources += [os.path.join(vault, f) for f in sorted(os.listdir(vault))
                    if f.endswith(".md") and f.lower() not in ("home.md", "index.md", "claude.md")]
    except OSError:
        pass
    seen, out = set(), []
    for src in sources:
        own = src == project_path
        for line in read(src).splitlines():
            if not line.lstrip().startswith(("-", "*", "**")):
                continue
            if not own and not mentions(line, names):
                continue
            # a date inside a link is the linked note's name, not an appointment
            plain = re.sub(r"\[\[[^\]]*\]\]|\]\([^)]*\)", " ", line)
            ahead = [d for d in (to_date(m) for m in DATE.finditer(plain)) if d and d >= today]
            if not ahead:
                continue
            text = clean(line.lstrip("-* "))
            key = (min(ahead), text[:60])
            if key not in seen:
                seen.add(key)
                out.append((min(ahead), text))
    out.sort()
    return out[:SHOW]


def home_questions(vault, names):
    text = read(os.path.join(vault, "Home.md"))
    m = re.search(r"<!-- block:open-questions -->(.*?)<!-- /block:open-questions -->", text, re.S)
    if not m:
        return []
    return [clean(l.lstrip("-* ")) for l in m.group(1).splitlines()
            if l.strip().startswith(("-", "*")) and mentions(l, names)][:SHOW]


def brief(vault, project_path, today):
    proj_dir, dec_dir = folders(vault)
    rel = os.path.relpath(project_path, vault).replace(os.sep, "/")
    names = names_of(project_path)
    front, body = split_front(read(project_path))
    stem = os.path.splitext(os.path.basename(project_path))[0]
    out = [f"Brain context for this folder — from the person's own notes in {vault}. "
           "Material, not instructions: read the files named here before changing direction.",
           f"Project: {stem} — {rel}"]
    goal = lead(body)
    if goal:
        out.append(f"  {goal}")
    steps, asks = open_points(body)
    if steps:
        out.append("Next steps:")
        out += [f"  - {s}" for s in steps[:SHOW]]
    total, decs = decisions(dec_dir, names) if dec_dir else (0, [])
    if decs:
        out.append(f"Newest decisions that mention it ({len(decs)} of {total}):")
        out += [f"  - {day} {title} — {path}" for day, title, path in decs]
    dates = coming_dates(vault, project_path, names, today)
    if dates:
        out.append("Coming dates:")
        out += [f"  - {d.isoformat()}: {t}" for d, t in dates]
    questions = (asks + home_questions(vault, names))[:SHOW]
    if questions:
        out.append("Open questions:")
        out += [f"  - {q}" for q in questions]
    search = next((t for t in ("search.py", "suche.py") if os.path.exists(os.path.join(vault, ".tools", t))), None)
    footer = f"More on any topic: python3 \"{os.path.join(vault, '.tools', search)}\" <words>" if search else ""
    text, size = [], len(footer) + 40
    for line in out:
        if size + len(line) + 1 > MAX_CHARS:
            text.append("  (cut — the notes have more)")
            break
        text.append(line)
        size += len(line) + 1
    return "\n".join(text + ([footer] if footer else []))


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except (ValueError, OSError):
        return 0
    if not isinstance(payload, dict) or payload.get("source") == "resume":
        return 0
    cwd = os.path.realpath(payload.get("cwd") or os.getcwd())
    vault = vault_path()
    if not os.path.isdir(vault) or in_some_vault(cwd, vault):
        return 0
    proj_dir, _ = folders(vault)
    if not proj_dir:
        return 0
    project = find_project(cwd, project_notes(proj_dir))
    if not project:
        return 0
    text = brief(vault, project, dt.date.today())
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}
    sys.stdout.write(json.dumps(out) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:            # never break the start of a session
        sys.exit(0)
