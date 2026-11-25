#!/usr/bin/env python3
"""Cold start: what your past sessions, chats and calendar could give the vault.

    python3 .tools/harvest.py                 # inventory only — reads nothing
    python3 .tools/harvest.py --candidates    # deterministic pre-filter
    python3 .tools/harvest.py --candidates --since 2026-07-01 --max 20
    python3 .tools/harvest.py --root ~/.claude-work/projects   # a second brain
    python3 .tools/harvest.py --queue         # what the hooks have recorded
    python3 .tools/harvest.py --claude-export ~/Downloads/data-export.zip
    python3 .tools/harvest.py --claude-export export/ --grep pruefung --since 2026-01-01
    python3 .tools/harvest.py --claude-export export.zip --show 0d1f2a3b
    python3 .tools/harvest.py --ics ~/Downloads/calendar.ics --days 90

A new vault is empty, and an empty vault is useless. But the machine has
been listening for months: Claude Code keeps session transcripts in
`~/.claude/projects/` as plaintext JSONL (30 days by default — see
`cleanupPeriodDays`). That is the richest material about how someone
actually works that exists on their disk.

The catch is well documented. An audit of 10,134 auto-captured memories in
another system found 97.8% of them worthless — system-prompt echoes, cron
noise, transient task state, duplicates, and hallucinated profiles of the
user (github.com/mem0ai/mem0/issues/4573). Over 70% of that junk is
recognisable WITHOUT a model, by shape alone. That is what this tool does:
it throws away the obvious garbage for free, so a model only ever looks at
what might be worth something.

WHAT THIS TOOL DOES NOT DO — on purpose:
  - it never writes into the vault
  - it never calls a model, and costs nothing
  - it never decides what is worth keeping; it decides what is obviously NOT

Everything it prints is a candidate for a human to look at. The judging
happens afterwards, on a small sample first, and only with consent.

TWO MORE SOURCES the person already has, both read-only like the rest:

  --claude-export PATH   The data export of the Claude app (Settings →
      Privacy → Export data): the .zip as downloaded, the unzipped folder,
      or the conversations.json inside it. By default it prints one line per
      conversation — last activity, how many messages the PERSON wrote, a
      short id, the title — newest first, and not one word of any message.
      A chat archive is the most private file most people own; listing it
      must not dump it. `--grep WORDS` narrows the list by title (every word
      must occur; case and umlauts do not matter, `pruefung` finds
      `Prüfung`), `--since` by last activity. `--show ID` prints the
      person's own messages of exactly that one conversation, each cut to a
      few hundred characters, so a capture can be written from it in a
      normal chat. Claude's replies are never printed, in no mode: they are
      the machine's words, and the premise of this tool is the human's.
  --ics PATH   A calendar export. Prints the events of the next 120 days
      (`--days N`) as lines in the Deadlines format, `- YYYY-MM-DD Summary`,
      sorted. Only the DATE is kept: times are dropped, and a time given in
      UTC (`...T233000Z`) counts as its UTC date, so a late-evening event
      far from UTC can land one day off. A repeating event is not expanded:
      it gets one line, marked "(repeats)", at its next date when the rule
      is plain (FREQ=YEARLY/MONTHLY/WEEKLY, optionally INTERVAL, COUNT,
      UNTIL and EXDATE), otherwise at its first date if that is still ahead.
      An event that started before today is past, however long it lasts.
      What a calendar says goes under "Unconfirmed" in Deadlines.md until
      the person confirms it — a file is not a human.

Both refuse to run unattended, like everything here except --queue.
"""
import argparse, collections, contextlib, io, itertools, json, os, re, sys, unicodedata, zipfile
from datetime import date, datetime, timedelta, timezone

# Same reason as in search.py: on Windows the output stream falls back to the
# console codepage as soon as it is piped or redirected, and `--candidates`
# prints `→` on every line — so the one command that fills an empty vault
# died with a UnicodeEncodeError exactly when someone tried to save its
# output to a file.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError, OSError):
        pass

# Follow CLAUDE_CONFIG_DIR: a second brain runs under its own config
# directory, and its transcripts live there too. Reading ~/.claude from a
# work vault would harvest the PRIVATE sessions into it — the exact
# crossover the two-brain setup exists to prevent.
CONFIG = os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))
SESSIONS = os.path.join(CONFIG, "projects")

MAX_LINES = 20_000        # per session; a runaway transcript must not eat RAM
EXCERPT = 300             # characters shown around the phrase that matched

# --- what is obviously not worth keeping, recognisable by shape alone ---
NOISE = [
    (re.compile(r"^\s*<(system-reminder|command-name|local-command|task-notification)", re.I),
     "system plumbing"),
    (re.compile(r"^\s*(Caveat: The messages below were generated|"
                r"This session is being continued from|"
                r"Your task is to create a detailed summary)", re.I),
     "harness scaffolding"),
    (re.compile(r"^\s*(ok|okay|yes|no|ja|nein|passt|danke|thanks|weiter|"
                r"go|stop|warte|hm+|👍|✅)\s*[.!]?\s*$", re.I),
     "acknowledgement"),
    (re.compile(r"^\s*(continue|weiter machen|mach weiter|fortsetzen)\s*$", re.I),
     "continuation"),
    # Injected by the harness, not typed by the human — these arrive as
    # "user" events and are the single biggest source of false candidates.
    (re.compile(r"^\s*(Base directory for this skill|"
                r"Stop hook feedback:|"
                r"Review this change for security|"
                r"Please write a|"
                r"Analyze this codebase and|"
                r"\[Request interrupted)", re.I),
     "injected by the harness"),
    (re.compile(r"^\s*(Changed files|Unified diff|"
                r"The user sent a new message while you were working)", re.I),
     "injected by the harness"),
    # Pasted back INTO the chat: the assistant's own output, a terminal, a
    # build log. The premise of this tool is "only what the human typed";
    # a paste of the machine's words is the machine's words, however it got
    # there. Measured on 1,542 real turns: removes 7 candidates, all junk.
    (re.compile(r"⏺|\[\.{3}Truncated text #|Claude is temporarily overloaded|"
                r"\bSearched for \d+ pattern|\bRecalled \d+ memor|"
                r"^\s*▎|\w+@[\w-]+ ~ %|=> \[internal\] load|"
                r"^\s*\[Image: source: /", re.M),
     "pasted machine output"),
    # A pasted DOCUMENT (two or more Markdown headings): a skill body, a
    # spec, terms and conditions. Documents are `brain-ingest`'s job —
    # they go to 00-inbox/raw/, not into a capture. Removes 6, all junk.
    (re.compile(r"^\s{0,3}#{1,3} \S[\s\S]*?^\s{0,3}#{1,3} \S", re.M),
     "pasted document (→ brain-ingest)"),
]

# Attachments and paths are stripped BEFORE the signal test. A screenshot
# called "Bildschirmfoto 2026-08-06 um 06.42.56.png" is not an appointment,
# and it used to become one the moment dates were recognised at all.
ATTACHMENT = re.compile(
    r"\[Image #\d+\]|\[Image: source:[^\]]*\]|https?://\S+|"
    r"@?\"/[^\"\n]+\"|"                                   # "…/a file.png"
    r"/[\w.-]+(?:(?:/|\\ )[\w.-]+)*\.\w{2,4}")            # /a/path/file.png


# A line has to carry one of these to be a candidate at all: it must be a
# statement about the human's world, not about the machine's state.
SIGNAL = re.compile(
    r"\b(decid|decision|entschied|entscheidung|beschlossen|"          # decisions
    r"deadline|frist|termin|due|until|bis zum|"                       # dates
    r"launched|live gegangen|released|geliefert|fertig geworden|"     # milestones
    r"lesson|gelernt|lektion|never again|nie wieder|merke|"           # lessons
    r"we agreed|wir haben.{0,20}(entschieden|vereinbart)|"
    r"from now on|ab jetzt|ab sofort|künftig|"
    r"turns out|stellt sich heraus|zeigt sich)\b|"
    # Real dates, not the word "date". An appointment is the one capture
    # trigger that is almost never announced with a trigger WORD — "our
    # conversation on Tuesday, 18.08., at 15:00" carried none of the above
    # and was dropped. Clock times alone are deliberately NOT here: they
    # matched "it is 22:33 now" and nothing worth keeping.
    r"(?<![\d.,])(?:0?[1-9]|[12]\d|3[01])\.\s?(?:0?[1-9]|1[0-2])\.(?![\d.])|"
    r"(?<![\d.,])(?:0?[1-9]|[12]\d|3[01])\.\s?(?:Jan|Feb|Mär|Maer|Mar|Apr|Mai|"
    r"May|Jun|Jul|Aug|Sep|Okt|Oct|Nov|Dez|Dec)|"
    r"\b\d{4}-\d{2}-\d{2}\b|"
    # The mirror of the line above for English ("August 18" vs "18. August").
    # It adds nothing on the corpus this was measured against — that corpus
    # is German — and it costs nothing there either: zero new candidates.
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? "
    r"\d{1,2}(?:st|nd|rd|th)?\b|"
    r"\b(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I)

def fold(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))

def iter_sessions(root):
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != "subagents"]   # sub-agent chatter
        for f in sorted(files):
            if f.endswith(".jsonl"):
                yield os.path.join(dirpath, f)

def session_day(path):
    try:
        return datetime.fromtimestamp(os.path.getmtime(path), timezone.utc).date()
    except OSError:
        return None

def human_lines(path, stats=None):
    """Only what the HUMAN typed. Everything the assistant said is a
    reformulation of it at best, and its own state at worst.

    Read line by line: a transcript can be tens of megabytes (mostly one
    enormous line per pasted image), and slurping it into a list to take
    the head costs the file's size in RAM for no gain."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            seen = 0
            for raw in itertools.islice(fh, MAX_LINES):
                seen += 1
                try:
                    ev = json.loads(raw)
                except (ValueError, TypeError):
                    continue
                if not isinstance(ev, dict) or ev.get("type") != "user":
                    continue
                msg = ev.get("message")
                if not isinstance(msg, dict):     # a format change must not crash us
                    continue
                content = msg.get("content")
                if isinstance(content, list):
                    content = " ".join(c.get("text", "") for c in content
                                       if isinstance(c, dict) and c.get("type") == "text")
                if not isinstance(content, str) or not content.strip():
                    continue
                yield content.strip()
            if stats is not None and seen == MAX_LINES:
                stats["truncated"] += 1       # named in the output, never silent
    except OSError:
        return

def classify(text):
    for pattern, label in NOISE:
        if pattern.search(text):
            return label
    if len(text) < 25:
        return "too short"
    return None

def excerpt(text, match):
    """Show the phrase that made this a candidate, not the first 200
    characters of the turn. In a 15,000-character turn those are almost
    never the same thing, and the head is what a reader used to get."""
    flat = re.sub(r"\s+", " ", text).strip()
    if len(flat) <= EXCERPT + 60:
        return flat
    hit = re.sub(r"\s+", " ", match).strip()
    at = flat.find(hit)
    if at < 0:
        at = 0
    start = max(0, at - EXCERPT // 4)
    end = min(len(flat), start + EXCERPT)
    if start:
        start = flat.find(" ", start) + 1 or start
    if end < len(flat):
        cut = flat.rfind(" ", start, end)
        end = cut if cut > start else end
    return ("…" if start else "") + flat[start:end] + ("…" if end < len(flat) else "")

def inventory(root):
    if not os.path.isdir(root):
        print(f"No session directory at {root} — nothing to harvest.")
        return 1
    by_month, by_project, total, bytes_ = collections.Counter(), collections.Counter(), 0, 0
    oldest = newest = None
    for path in iter_sessions(root):
        total += 1
        try:
            bytes_ += os.path.getsize(path)
        except OSError:
            pass
        day = session_day(path)
        if day:
            by_month[day.strftime("%Y-%m")] += 1
            oldest = day if oldest is None or day < oldest else oldest
            newest = day if newest is None or day > newest else newest
        rel = os.path.relpath(path, root).split(os.sep)[0]
        by_project[rel] += 1
    print(f"sessions: {total} · {bytes_ / 1e9:.1f} GB · {len(by_project)} projects")
    if oldest:
        print(f"range: {oldest} … {newest}")
    print("\nby month:")
    for m, n in sorted(by_month.items()):
        print(f"  {m}: {n}")
    print("\nlargest projects:")
    for p, n in by_project.most_common(8):
        print(f"  {n:5}  {p}")
    print("\nNothing was read. Run with --candidates to pre-filter, or see the")
    print("cold-start section of SETUP-FOR-CLAUDE.md for the full procedure.")
    print("Transcripts older than `cleanupPeriodDays` (default 30) are already gone.")
    return 0

def candidates(root, since, cap):
    if not os.path.isdir(root):
        # Without this, a typo in --root printed "0 turns looked at", which
        # reads as "your sessions hold nothing" rather than "wrong path".
        print(f"No session directory at {root} — nothing to harvest.")
        return 1
    kept, dropped, seen = [], collections.Counter(), set()
    stats = collections.Counter()
    for path in iter_sessions(root):
        day = session_day(path)
        if since and day and day < since:
            continue
        for text in human_lines(path, stats):
            reason = classify(text)
            if reason:
                dropped[reason] += 1
                continue
            probe = ATTACHMENT.sub(" ", text)
            m = SIGNAL.search(probe)
            if not m:
                dropped["no signal word"] += 1
                continue
            shown = excerpt(probe, m.group(0))
            key = fold(shown)[:180]
            if key in seen:
                dropped["duplicate"] += 1
                continue
            seen.add(key)
            kept.append((day, os.path.basename(path)[:8], shown))
    total = len(kept) + sum(dropped.values())
    print(f"human turns looked at: {total}")
    print(f"dropped without a model: {sum(dropped.values())} "
          f"({100 * sum(dropped.values()) // max(total, 1)}%)")
    for reason, n in dropped.most_common():
        print(f"  {n:6}  {reason}")
    if stats["truncated"]:
        print(f"\nNOTE: {stats['truncated']} session(s) were read only to their "
              f"first {MAX_LINES:,} lines — the rest was NOT looked at.")
    print(f"\ncandidates left: {len(kept)}")
    print("These are NOT findings — they are the only lines worth a model's time.")
    print("Each one is shown around the phrase that matched, not from the start.")
    print("Judge a sample first, then decide whether the rest is worth it.\n")
    for day, sid, text in kept[:cap]:
        print(f"[{day} {sid}] {text}")
    if len(kept) > cap:
        print(f"\n… and {len(kept) - cap} more (raise with --max)")
    return 0

def capture_check_state():
    """What the Stop hook has learnt, in plain language. It stores three
    numbers and no content; this is the only place they are readable."""
    path = os.path.join(CONFIG, "state", "brainwarden-capture-check")
    st = {}
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                key, sep, value = line.partition("=")
                if sep and not key.strip().startswith("#"):
                    try:
                        st[key.strip()] = float(value)
                    except ValueError:
                        pass
    except OSError:
        return
    level = int(st.get("level", 0))
    base = 240
    try:
        base = int(os.environ.get("BRAINWARDEN_CAPTURE_WINDOW", "") or 240)
    except ValueError:
        pass
    hours = base * (2 ** min(max(level, -2), 4)) / 60.0
    print("\ncapture check:")
    if level >= 5:
        print("  asleep — five asks in a row produced nothing. It wakes up by")
        print("  itself as soon as something lands in the inbox or decisions.")
    else:
        print(f"  level {level:+d} → asks at most every {hours:.0f}h "
              f"(base {base / 60:.0f}h)")
        print("  every empty answer halves that rate, every capture doubles it.")
    if st.get("last"):
        when = datetime.fromtimestamp(st["last"]).strftime("%Y-%m-%d %H:%M")
        print(f"  last spoke: {when}")

def show_queue(root_cfg):
    """The session queue, if the SessionEnd hook is installed.

    One line per finished session: when, project, id, why it ended. No
    content — the queue records THAT something happened, never what. The
    weekly review walks it and asks about the sessions it has not seen."""
    path = os.path.join(root_cfg, "state", "brainwarden-session-queue.tsv")
    if not os.path.exists(path):
        print("No session queue at " + path)
        print("Either the SessionEnd hook is not installed (see hooks/README.md),")
        print("or this is a place where hooks do not exist at all — Claude in the")
        print("browser, Cowork, a phone. In that case do NOT wait for a tool:")
        print("the week gets reconstructed by ASKING, and the question has to")
        print("carry the cues, because free recall over seven days is poor:")
        print("  · day by day, Monday through Sunday — not 'this week'")
        print("  · by counterpart: go through 30-knowledge/people/ (or 60-roles/,")
        print("    80-partners/) by name — 'anything with them this week?'")
        print("  · by open loop: every date in Deadlines.md and every open")
        print("    question on Home — 'what happened with this one?'")
        print("Phone work leaves no files and no commits, but it leaves people")
        print("and dates, and those the vault already knows.")
        capture_check_state()
        return 0
    rows = [l.split("\t") for l in
            open(path, encoding="utf-8", errors="ignore").read().splitlines() if l.strip()]
    # An EMPTY queue file is not the same story as a queue with nothing new in
    # it, and printing "sessions in queue: 0" told both stories in the same
    # calm voice. Measured on a live machine: the file existed, the hook was
    # installed and registered, sessions had been ending all day, and the
    # queue was zero bytes — the review would have read that as a quiet week.
    # A track that has died has to say so, or it is worse than no track.
    if not rows:
        print(f"sessions in queue: 0 — but the queue file EXISTS ({path})")
        try:
            age = (datetime.now() - datetime.fromtimestamp(
                os.path.getmtime(path))).days
            print(f"  last written {age} day(s) ago, and it is empty.")
        except OSError:
            pass
        stray = path + ".tmp"
        if os.path.exists(stray):
            print(f"  a half-finished trim is still lying next to it: {stray}")
        print("  So either no session has ended since it was emptied, or this")
        print("  track is broken. Check it before believing the zero:")
        print("    · is the SessionEnd hook still in settings.json?")
        print("      (hooks/README.md has the entry)")
        print("    · does it run? end a session and look at the file again")
        print("    · is CLAUDE_CONFIG_DIR the same for the hook and for this")
        print("      tool? A second brain writes its queue somewhere else.")
        print("  Until that is answered, treat the session track as MISSING and")
        print("  ask the cued questions instead (day by day · by counterpart ·")
        print("  by open deadline).")
        capture_check_state()
        return 0
    print(f"sessions in queue: {len(rows)}")
    by_project = collections.Counter(r[1] for r in rows if len(r) > 1)
    print("\nby project:")
    for name, n in by_project.most_common(10):
        print(f"  {n:4}  {name}")
    print("\nmost recent:")
    for r in rows[-15:]:
        when, project, sid = (r + ["", "", ""])[:3]
        print(f"  {when}  {project}  {sid[:8]}")
    print("\nThese are sessions, not findings. The weekly review asks what came")
    print("out of the ones it has not seen yet — that question is the point.")
    print("It is also only ONE track: whoever works in Cowork, in a browser or")
    print("on a phone never appears here, and gets asked the cued questions")
    print("instead (day by day · by counterpart · by open deadline).")
    capture_check_state()
    return 0

# --- the Claude app's data export -------------------------------------------
HUMAN = ("human", "user")   # "human" in the export; "user" if a format ever changes
SHOW_CHARS = 600            # per message in --show: enough to write a capture from

UMLAUT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})

def title_forms(text):
    """Two spellings of a title, so a typed word finds it either way.

    Titles are written with umlauts and searched without them: `pruefung`
    must find `Prüfung`, and so must `prufung`. The first form spells ä as
    ae (search.py's rule, see its fold()); the second strips the accent. A
    title list is short and read by a human, so a few extra hits cost
    nothing — a missed conversation is what costs."""
    text = unicodedata.normalize("NFC", text.lower())
    out = []
    for t in (text.translate(UMLAUT), text):
        t = unicodedata.normalize("NFKD", t)
        out.append("".join(c for c in t if not unicodedata.combining(c)))
    return out

def iter_json_array(fh, chunk=1 << 20):
    """The elements of a top-level JSON array, one at a time.

    conversations.json holds the whole chat history in one array — for a
    heavy user that can run to hundreds of megabytes, and several times that
    as Python objects. A listing needs a few fields per
    conversation, so it decodes one conversation, keeps what it needs and
    lets the rest go. An element cut off by the end of the buffer fails to
    decode; then more is read (twice as much each time, so one enormous
    conversation does not get parsed a hundred times) and it is tried again."""
    dec = json.JSONDecoder()
    buf, pos, eof, want = "", 0, False, chunk

    def refill(size):
        nonlocal buf, pos, eof
        data = fh.read(size)
        eof = not data
        buf, pos = buf[pos:] + data, 0

    def skip(chars):
        """Move past `chars`, reading on as needed; False at the end of the file."""
        nonlocal pos
        while True:
            while pos < len(buf) and buf[pos] in chars:
                pos += 1
            if pos < len(buf):
                return True
            if eof:
                return False
            refill(chunk)

    if not skip(" \t\r\n"):
        raise ValueError("the file is empty")
    if buf[pos] != "[":
        # Not an array at the top: an export format we have not seen. Take
        # it whole and look for the list where it would plausibly be.
        whole = json.loads(buf[pos:] + fh.read())
        if isinstance(whole, dict):
            whole = whole.get("conversations")
        if not isinstance(whole, list):
            raise ValueError("no list of conversations in it")
        yield from whole
        return
    pos += 1                                  # past the opening [
    while True:
        if not skip(" \t\r\n,"):
            raise ValueError("the file ends before its closing ]")
        if buf[pos] == "]":
            return
        try:
            item, end = dec.raw_decode(buf, pos)
            # A number at the very end of the buffer may be cut in half and
            # still decode; only a delimiter behind it proves it is whole.
            if end >= len(buf) and not eof:
                raise ValueError("maybe cut off")
        except ValueError:
            if eof:
                raise
            refill(want)
            want *= 2
            continue
        want = chunk
        yield item
        pos = end
        if pos > chunk:                       # forget what has been handed out
            buf, pos = buf[pos:], 0

def export_conversations(path):
    """Every conversation in an export, whichever of its three shapes PATH is.

    The app hands out a .zip; people unzip it, or point straight at the one
    file that matters. Refusing two of the three would only make someone
    unpack or re-pack a file containing their entire chat history."""
    with contextlib.ExitStack() as stack:
        if os.path.isdir(path):
            found = [os.path.join(d, "conversations.json") for d, _, files in os.walk(path)
                     if "conversations.json" in files]
            if not found:
                raise LookupError(f"no conversations.json in {path}")
            src = min(found, key=lambda p: p.count(os.sep))
            fh = stack.enter_context(open(src, encoding="utf-8-sig", errors="replace"))
        elif zipfile.is_zipfile(path):
            zf = stack.enter_context(zipfile.ZipFile(path))
            # "/" by the zip spec; some Windows tools write "\" anyway
            names = [n for n in zf.namelist()
                     if re.split(r"[/\\]", n)[-1] == "conversations.json"]
            if not names:
                raise LookupError(f"no conversations.json in {path}")
            raw = stack.enter_context(zf.open(min(names, key=lambda n: n.count("/"))))
            fh = stack.enter_context(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace"))
        elif os.path.isfile(path):
            fh = stack.enter_context(open(path, encoding="utf-8-sig", errors="replace"))
        else:
            raise LookupError(f"nothing at {path}")
        yield from iter_json_array(fh)

def stamp(value):
    """`2026-11-20T09:31:22` from whatever timestamp spelling the export
    uses, or "" — a missing or odd date must sort last, not crash."""
    if isinstance(value, str) and re.match(r"\d{4}-\d\d-\d\d", value):
        return value[:19].replace(" ", "T")
    return ""

def messages_of(conv):
    msgs = conv.get("chat_messages")
    return [m for m in msgs if isinstance(m, dict)] if isinstance(msgs, list) else []

def is_human(msg):
    """Unknown sender counts as NOT the person: when in doubt, print nothing."""
    return str(msg.get("sender") or msg.get("role") or "").lower() in HUMAN

def message_text(msg):
    """The message's words. Newer exports leave `text` empty and put them
    in content[] blocks; only blocks of type text are words someone typed."""
    text = msg.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    parts = msg.get("content")
    if not isinstance(parts, list):
        return ""
    return "\n".join(p["text"] for p in parts if isinstance(p, dict)
                     and p.get("type", "text") == "text" and isinstance(p.get("text"), str)).strip()

def printable(text):
    """Titles, messages and calendar entries come from outside and go to a
    terminal — and often straight into a model. An escape sequence in a title
    can rewrite the terminal, a right-to-left override can hide what a line
    says. Control and format characters go; a line break becomes a space."""
    return "".join(" " if c in "\n\r\t" else c for c in text if c in "\n\r\t"
                   or unicodedata.category(c)[0] != "C")

def conversation_title(conv):
    name = conv.get("name")
    name = re.sub(r"\s+", " ", printable(name)).strip() if isinstance(name, str) else ""
    return name[:100] or "(untitled)"

def last_activity(conv):
    """When the conversation last happened: its newest message. The
    conversation's own timestamps count only when it has no messages —
    they are bookkeeping of the app, and `--since` asks when someone wrote."""
    stamps = [stamp(m.get("created_at")) for m in messages_of(conv)]
    return max(stamps) if any(stamps) else (stamp(conv.get("updated_at"))
                                            or stamp(conv.get("created_at")))

def claude_export(path, since, words, cap):
    rows, broken, total_mine = [], None, 0
    try:
        for conv in export_conversations(path):
            if not isinstance(conv, dict):
                continue
            mine = sum(1 for m in messages_of(conv) if is_human(m))
            total_mine += mine
            rows.append((last_activity(conv), mine, printable(str(conv.get("uuid") or ""))[:8],
                         conversation_title(conv)))
    except (OSError, LookupError, ValueError, zipfile.BadZipFile) as e:
        if not rows:
            print(f"Could not read the export at {path}: {e}")
            return 1
        broken = str(e)
    rows.sort(key=lambda r: r[0], reverse=True)
    days = sorted(r[0][:10] for r in rows if r[0])
    print(f"Claude export: {len(rows)} conversations · {total_mine} messages from you"
          + (f" · {days[0]} … {days[-1]}" if days else ""))
    if broken:
        print(f"NOTE: the file broke off after {len(rows)} conversations ({broken}) — "
              f"the rest was NOT read. A cut-off download? Export again.")
    shown = rows
    if since:
        shown = [r for r in shown if r[0] and r[0][:10] >= since.isoformat()]
    if words:
        want = [title_forms(w)[0] for w in words]
        shown = [r for r in shown if all(any(w in f for f in title_forms(r[3])) for w in want)]
    if since or words:
        print(f"matching: {len(shown)}"
              + (f" · since {since}" if since else "")
              + (f" · title has {' '.join(words)!r}" if words else ""))
    print("No message text is printed here — titles only.\n")
    if shown:
        print("date        yours  id        title")
    for when, mine, sid, title in shown[:cap]:
        print(f"{(when[:10] or '?'):<10}  {mine:5}  {sid:<8}  {title}")
    if len(shown) > cap:
        print(f"\n… and {len(shown) - cap} more (raise with --max, narrow with --grep/--since)")
    print("\n--show <id> prints YOUR messages of one conversation, to write a capture")
    print("from it. Claude's replies are never printed.")
    return 0

def show_conversation(path, wanted, cap):
    """One conversation, the person's side only. A short id from the
    listing is enough, but only if exactly one conversation carries it —
    the wrong chat shown is a privacy slip, not a typo."""
    hits = []
    try:
        for conv in export_conversations(path):
            uid = str(conv.get("uuid") or "") if isinstance(conv, dict) else ""
            if uid and (uid == wanted or (len(wanted) >= 8 and uid.startswith(wanted))):
                hits.append(conv)
    except (OSError, LookupError, ValueError, zipfile.BadZipFile) as e:
        if not hits:
            print(f"Could not read the export at {path}: {e}")
            return 1
    exact = [c for c in hits if c.get("uuid") == wanted]
    hits = exact or hits
    if len(hits) > 1:
        print(f"{len(hits)} conversations start with {wanted!r} — give more of the id.")
        return 1
    if not hits:
        hint = " — give the 8 characters from the listing, or the whole id" if len(wanted) < 8 else ""
        print(f"No conversation with the id {wanted!r} in the export{hint}.")
        return 1
    conv = hits[0]
    mine = [m for m in messages_of(conv) if is_human(m)]
    print(f"{last_activity(conv)[:10] or '?'}  {conversation_title(conv)}  ({printable(str(conv.get('uuid')))})")
    print(f"your messages: {len(mine)} — Claude's replies are not printed\n")
    for m in mine[:cap]:
        text = re.sub(r"\s+", " ", printable(message_text(m)))
        if len(text) > SHOW_CHARS:
            text = text[:SHOW_CHARS].rsplit(" ", 1)[0] + " …"
        when = stamp(m.get("created_at"))[:16].replace("T", " ")
        print(f"[{when or '?'}] {text or '(no text — an attachment or image only)'}")
    if len(mine) > cap:
        print(f"\n… and {len(mine) - cap} more (raise with --max)")
    return 0

# --- a calendar export (.ics, RFC 5545) --------------------------------------
# NAME;PARAM=...;PARAM="...":VALUE. A colon inside a quoted parameter is not
# the separator: Outlook writes TZID="(UTC+01:00) Amsterdam, Berlin, ...",
# and splitting at the first colon would read "00) Amsterdam" as the start.
CONTENT_LINE = re.compile(r'((?:[^:"]|"[^"]*")*):(.*)')
WEEKDAYS = ("MO", "TU", "WE", "TH", "FR", "SA", "SU")

def ics_date(value):
    """The date of a DATE or DATE-TIME value; the time and zone are dropped."""
    m = re.match(r"\s*(\d{4})-?(\d\d)-?(\d\d)", value or "")
    try:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None
    except ValueError:
        return None

def ics_text(value):
    """`\\,` `\\;` `\\\\` are escapes, `\\n` a line break — one line here."""
    value = re.sub(r"\\([\\,;nN])", lambda m: " " if m.group(1) in "nN" else m.group(1), value)
    return re.sub(r"\s+", " ", printable(value)).strip()

def ics_events(text):
    """The properties of every VEVENT that matter here.

    A component stack, not a flag: a VALARM inside an event carries its own
    SUMMARY and DESCRIPTION, and a VTIMEZONE its own DTSTART (1970, usually).
    With a simple "inside an event" flag the reminder text replaced the
    event's title, and every time zone became an event."""
    stack, events, ev = [], [], None
    for line in text.split("\n"):
        m = CONTENT_LINE.match(line.rstrip("\r"))
        if not m:
            continue
        head, value = m.groups()
        name = head.split(";", 1)[0].strip().upper()   # TZID, VALUE=DATE: not needed for a date
        if name == "BEGIN":
            stack.append(value.strip().upper())
            if stack[-1] == "VEVENT":
                ev = {}
        elif name == "END":
            comp = value.strip().upper()
            while comp in stack and stack.pop() != comp:
                pass
            if comp == "VEVENT" and ev is not None:
                events.append(ev)
                ev = None
        elif ev is not None and stack and stack[-1] == "VEVENT":
            if name == "EXDATE":
                ev.setdefault("EXDATE", []).extend(value.split(","))
            elif name in ("SUMMARY", "DTSTART", "RRULE", "UID", "STATUS", "RECURRENCE-ID"):
                ev.setdefault(name, value)
    return events

def rrule_next(start, rrule, today, skip):
    """(next date on or after today, understood?) for a plain repeat rule.

    Plain means FREQ=YEARLY/MONTHLY/WEEKLY with INTERVAL, COUNT, UNTIL, and
    at most BY-parts that repeat what DTSTART already says (Google writes
    `FREQ=WEEKLY;BYDAY=TU` for an event that starts on a Tuesday). Anything
    else — DAILY, several weekdays, "the last Friday" — is not expanded:
    a half-right expansion would put dates into Deadlines.md that are not
    in the calendar. Dates that do not exist (31 April, 29 February in a
    common year) are skipped, as RFC 5545 says, never moved."""
    rule = {}
    for part in rrule.upper().split(";"):
        key, _, val = part.partition("=")
        if key.strip():
            rule[key.strip()] = val.strip()
    freq = rule.pop("FREQ", "")
    implied = {"WEEKLY": {"BYDAY": WEEKDAYS[start.weekday()]},
               "MONTHLY": {"BYMONTHDAY": str(start.day)},
               "YEARLY": {"BYMONTH": str(start.month), "BYMONTHDAY": str(start.day)}}
    if freq not in implied:
        return None, False
    for key, val in rule.items():
        if key not in ("INTERVAL", "COUNT", "UNTIL", "WKST") \
                and implied[freq].get(key) != val.lstrip("0"):
            return None, False
    try:
        interval = max(1, int(rule.get("INTERVAL") or 1))
        count = int(rule["COUNT"]) if rule.get("COUNT") else None
    except ValueError:
        return None, False
    until = ics_date(rule.get("UNTIL"))
    seen = 0
    for i in range(200_000):                  # a bound nobody reaches: 3,800 years of weeks
        if freq == "WEEKLY":
            day = start + timedelta(weeks=i * interval)
        else:
            y, m = divmod(start.month - 1 + i * interval * (12 if freq == "YEARLY" else 1), 12)
            try:
                day = date(start.year + y, m + 1, start.day)
            except ValueError:
                continue                      # no such day this month/year
        seen += 1                             # an EXDATE still counts toward COUNT
        if (count is not None and seen > count) or (until and day > until):
            return None, True                 # the series is over
        if day >= today and day not in skip:
            return day, True
    return None, True

def calendar(path, days):
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as e:
        print(f"Could not read {path}: {e}")
        return 1
    # Unfold BEFORE decoding: a folded line may be cut inside a multi-byte
    # character (RFC 5545 counts octets), and decoding the halves separately
    # turns one `ü` into two replacement characters.
    text = re.sub(rb"\r?\n[ \t]", b"", raw).decode("utf-8-sig", errors="replace")
    events = ics_events(text)
    if not events:
        print(f"No VEVENT in {path} — is this a calendar export (.ics)?")
        return 1
    today = date.today()
    end = today + timedelta(days=days)
    # One instance of a series that was moved or cancelled arrives as its
    # own VEVENT with the series' UID and a RECURRENCE-ID. The series must
    # not claim that date as well, or the old date stays in the list.
    moved = collections.defaultdict(set)
    for ev in events:
        if ev.get("UID") and ics_date(ev.get("RECURRENCE-ID")):
            moved[ev["UID"]].add(ics_date(ev["RECURRENCE-ID"]))
    lines, dropped = set(), collections.Counter()
    for ev in events:
        start = ics_date(ev.get("DTSTART"))
        if not start:
            dropped["no start date"] += 1
            continue
        if (ev.get("STATUS") or "").strip().upper() == "CANCELLED":
            dropped["cancelled"] += 1
            continue
        day, mark = start, ""
        if ev.get("RRULE") and not ev.get("RECURRENCE-ID"):
            mark = " (repeats)"
            skip = {d for d in map(ics_date, ev.get("EXDATE", [])) if d} | moved[ev.get("UID")]
            nxt, understood = rrule_next(start, ev["RRULE"], today, skip)
            if nxt:
                day = nxt
            elif not understood and start < today:
                dropped["repeating, rule too complex to expand"] += 1
                continue
        if day < today:
            dropped["past"] += 1
        elif day > end:
            dropped[f"after the next {days} days"] += 1
        else:
            lines.add((day, f"- {day.isoformat()} {ics_text(ev.get('SUMMARY', '')) or '(no title)'}{mark}"))
    print(f"calendar: {len(events)} events · {len(lines)} between {today} and {end}")
    for reason, n in dropped.most_common():
        print(f"  {n:6}  {reason}")
    print()
    for _, line in sorted(lines):
        print(line)
    print("\nDates only — times were dropped. These come from a file, not from the")
    print("person: they go under \"Unconfirmed\" in Deadlines.md until confirmed.")
    return 0

def main():
    if os.environ.get("BRAINWARDEN_UNATTENDED") and sys.argv[1:] != ["--queue"]:
        # Unattended, only the queue: when and where sessions ended. The
        # inventory and the candidates read the transcripts of every Claude
        # session on this machine, --claude-export the whole chat archive,
        # --ics the calendar — all of that needs the person in the chat.
        print("refused while unattended: only `harvest.py --queue` (transcripts in a normal chat)")
        return 2
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.split("\n")[0])
    source = ap.add_mutually_exclusive_group()
    source.add_argument("--queue", action="store_true",
                        help="show the session queue (needs the SessionEnd hook)")
    source.add_argument("--candidates", action="store_true",
                        help="pre-filter the transcripts (still writes nothing)")
    source.add_argument("--claude-export", metavar="PATH",
                        help="list the conversations of a Claude app export (.zip, folder "
                             "or conversations.json) — titles only, no message text")
    source.add_argument("--ics", metavar="PATH",
                        help="upcoming events of a calendar export as Deadlines lines")
    ap.add_argument("--since", help="only sessions / conversations from this date on (YYYY-MM-DD)")
    ap.add_argument("--grep", nargs="+", metavar="WORD",
                    help="with --claude-export: only titles containing every word")
    ap.add_argument("--show", metavar="ID",
                    help="with --claude-export: YOUR messages of this one conversation")
    ap.add_argument("--days", type=int, default=120, help="with --ics: how far ahead (default 120)")
    ap.add_argument("--max", type=int, default=40,
                    help="how many lines to print (candidates, conversations, messages)")
    ap.add_argument("--root", default=SESSIONS, help="session directory")
    a = ap.parse_args()
    if (a.grep or a.show) and not a.claude_export:
        ap.error("--grep and --show belong to --claude-export")
    if a.show and (a.grep or a.since):
        ap.error("--show takes one id; --grep and --since narrow the listing, not a conversation")
    if (a.days != 120 and not a.ics) or a.days < 0:
        ap.error("--days belongs to --ics and cannot be negative")
    if a.since and a.ics:
        ap.error("--since does not apply to --ics; the window starts today (--days sets its end)")
    since = None
    if a.since:
        try:
            since = datetime.strptime(a.since, "%Y-%m-%d").date()
        except ValueError:
            print("--since needs YYYY-MM-DD"); return 1
    if a.queue:
        return show_queue(CONFIG)
    if a.ics:
        return calendar(os.path.expanduser(a.ics), a.days)
    if a.claude_export:
        path = os.path.expanduser(a.claude_export)
        if a.show:
            return show_conversation(path, a.show.strip(), a.max)
        words = [w for g in (a.grep or []) for w in g.split()]
        return claude_export(path, since, words, a.max)
    root = os.path.expanduser(a.root)
    return candidates(root, since, a.max) if a.candidates else inventory(root)

if __name__ == "__main__":
    sys.exit(main())
