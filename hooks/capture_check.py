#!/usr/bin/env python3
"""Brainwarden — capture check (Claude Code "Stop" hook, opt-in).

At the end of a turn it checks whether a `.md` file in the vault's inbox
(`00-*`) or decisions (`40-*`) folder changed recently. If yes, it stays
silent. If no, it asks Claude once to check the five capture triggers and
capture what is worth keeping.

It backs off by itself. After asking, it checks whether anything landed:

    yes  ->  asks twice as often   (down to BASE/4)
    no   ->  asks half as often    (up to 16x BASE)
             after five empty answers in a row it sleeps until the
             vault fills again.

It compares file timestamps only and cannot tell what you answered: a
capture written by hand counts as a hit, an interrupted turn as a miss.

State: three numbers in `<config>/state/brainwarden-capture-check` (last
spoke, last asked, level). Delete the file to reset;
`python3 <vault>/.tools/harvest.py --queue` prints it.

It never calls a model or the network, never writes into the vault and
records no content. If it cannot write its state file it stays silent,
since it could not remember that it already asked.

Install (opt-in — the setup does not do this for you):

  1. copy this file to  <config>/hooks/capture_check.py
     (<config> is ~/.claude, or whatever CLAUDE_CONFIG_DIR points at)
  2. add it to the "Stop" hooks in <config>/settings.json:

     {"hooks": {"Stop": [{"hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/capture_check.py"}
     ]}]}}

     On Windows use the python command that works there, e.g. `py -3`.
  3. that's it — no other dependency

Uninstall: delete the file, remove the entry. Nothing else changes.
Silence it without uninstalling: `BRAINWARDEN_CAPTURE_CHECK=off`.

Tuning: BRAINWARDEN_CAPTURE_WINDOW (minutes, default 240) sets the BASE
interval the back-off moves around. If it still asks too often, raise it.
"""
import json
import os
import re
import sys
import time

DEFAULT_WINDOW = 240             # minutes — the base the back-off moves around
MIN_LEVEL, MAX_LEVEL = -2, 4     # BASE/4  …  BASE*16
DORMANT = MAX_LEVEL + 1          # asleep: only ever checks for a reason to wake
RESOLVE_AFTER = 30 * 60          # seconds before an unanswered ask counts as empty


def base_window():
    """Minutes. A junk value in the environment must not kill the turn."""
    try:
        n = int(os.environ.get("BRAINWARDEN_CAPTURE_WINDOW", "") or DEFAULT_WINDOW)
    except ValueError:
        return DEFAULT_WINDOW
    return n if n > 0 else DEFAULT_WINDOW


def window_seconds(level):
    """The interval for a level. Dormant checks at the slowest cadence."""
    level = min(max(level, MIN_LEVEL), DORMANT)
    return base_window() * 60 * (2 ** min(level, MAX_LEVEL))


def config_dir():
    return os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))


def state_path():
    return os.path.join(config_dir(), "state", "brainwarden-capture-check")


def vault_path():
    """The vault from the `Brain vault:` line in the global rules (the line
    every brain-* skill follows); ~/Brain when no line is set."""
    rules = os.path.join(config_dir(), "CLAUDE.md")
    try:
        with open(rules, encoding="utf-8-sig", errors="ignore") as fh:
            for line in fh:
                # accepts bold, backticks and a trailing remark, like
                # project_context.py
                m = re.match(r"\s*[-*]?\s*(?:\*\*)?\s*Brain vault:\s*(?:\*\*)?\s*(.+)", line)
                if not m:
                    continue
                rest = m.group(1).strip()
                quoted = re.match(r"`([^`]+)`", rest)
                path = quoted.group(1) if quoted else re.split(r"\s+(?:<|←|#|—|–|\(|- )", rest)[0]
                path = path.strip().strip("\"'")
                if path:
                    return os.path.expanduser(path)
    except OSError:
        pass
    return os.path.expanduser("~/Brain")


# a kit vault states its mode as a VALUE (the label may be translated)
MODE_LINE = re.compile(r"^\*\*[^\n:]{0,40}:\s*(personal|professional|company)\b", re.M | re.I)


def session_vault(cwd):
    """The vault this session works in, if any: cwd or a parent with a kit
    mode line in its CLAUDE.md, the kit's tools and an inbox. All three are
    required, so a code repository whose rules mention a mode never
    receives private captures."""
    here = os.path.abspath(cwd) if cwd else ""
    for _ in range(12):
        if not here:
            break
        try:
            with open(os.path.join(here, "CLAUDE.md"), encoding="utf-8-sig", errors="ignore") as fh:
                text = fh.read(65536)
        except OSError:
            text = ""
        if MODE_LINE.search(text) and os.path.isfile(os.path.join(here, ".tools", "hygiene.py")) \
                and watched_folders(here)[0]:
            return here
        up = os.path.dirname(here)
        if up == here:
            break
        here = up
    return None


def watched_folders(vault):
    """(inbox, decisions), found by number prefix, not by name, so
    translated folders such as `40-entscheidungen` are still watched."""
    inbox = decisions = None
    try:
        for name in sorted(os.listdir(vault)):
            if not os.path.isdir(os.path.join(vault, name)):
                continue
            if inbox is None and name.startswith("00-"):
                inbox = os.path.join(vault, name)
            elif decisions is None and name.startswith("40-"):
                decisions = os.path.join(vault, name)
    except OSError:
        pass
    return inbox, decisions


def landed_since(folders, cutoff):
    """Any .md file in there modified at or after `cutoff`? Stops at the
    first hit."""
    for folder in folders:
        if not os.path.isdir(folder):
            continue
        for dirpath, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for name in files:
                if not name.endswith(".md"):
                    continue
                try:
                    if os.path.getmtime(os.path.join(dirpath, name)) >= cutoff:
                        return True
                except OSError:
                    continue
    return False


def read_state():
    """`key=value` lines, editable by hand. A bare epoch (old format) still
    parses as `last`."""
    st = {"last": 0.0, "asked": 0.0, "level": 0}
    path = state_path()
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            raw = fh.read()
    except OSError:
        return st
    parsed = False
    for line in raw.splitlines():
        key, sep, value = line.partition("=")
        key = key.strip()
        if not sep or key not in st:
            continue
        try:
            st[key] = int(float(value)) if key == "level" else float(value)
            parsed = True
        except ValueError:
            continue
    if not parsed:                      # older marker file: one bare epoch
        try:
            st["last"] = float(raw.strip())
        except ValueError:
            try:
                st["last"] = os.path.getmtime(path)
            except OSError:
                pass
    st["level"] = min(max(st["level"], MIN_LEVEL), DORMANT)
    return st


def write_state(st):
    """True only if the state reached the disk. A hook that cannot remember
    that it spoke must not speak, or it repeats on every turn."""
    path = state_path()
    body = (
        "# brainwarden capture check — delete this file to reset\n"
        "# level: -2 = asks 4x as often, 0 = base, 4 = 16x rarer, 5 = asleep\n"
        f"last={int(st['last'])}\n"
        f"asked={int(st['asked'])}\n"
        f"level={int(st['level'])}\n"
    )
    tmp = path + ".tmp"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(body)
        os.replace(tmp, path)
        return True
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass
        return False


def read_stdin():
    """The payload as text. A closed stdin (`0<&-`) makes `sys.stdin` None.
    The raw bytes are decoded as utf-8 (JSON is utf-8); the text layer would
    use the locale encoding and garble non-ASCII paths on a cp1252 Windows
    console."""
    stream = sys.stdin
    if stream is None:
        return ""
    try:
        if stream.isatty():                 # interactive: nothing is piped in
            return ""
    except (AttributeError, ValueError, OSError):
        pass
    try:
        return stream.buffer.read().decode("utf-8", "replace")
    except (AttributeError, ValueError, OSError):
        pass
    try:
        return stream.read()
    except (OSError, UnicodeDecodeError):
        return ""


def main():
    if os.environ.get("BRAINWARDEN_CAPTURE_CHECK", "").strip().lower() in (
            "off", "0", "false", "no"):
        return 0

    raw = read_stdin()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {}
    if not isinstance(payload, dict):     # valid JSON, unexpected shape
        payload = {}

    cwd = payload.get("cwd") if isinstance(payload.get("cwd"), str) else os.getcwd()
    vault = session_vault(cwd) or vault_path()
    inbox, decisions = watched_folders(vault)
    folders = [f for f in (inbox, decisions) if f]

    # No vault on this machine (someone else's computer)? Stay silent.
    if not inbox or not os.path.isdir(inbox):
        return 0

    now = time.time()
    st = read_state()
    from_our_block = bool(payload.get("stop_hook_active"))

    # 1. Score the open ask, if any: did anything land after we asked?
    if st["asked"]:
        if from_our_block or now - st["asked"] >= RESOLVE_AFTER:
            hit = landed_since(folders, st["asked"])
            st["level"] = min(max(st["level"] + (-1 if hit else 1),
                                  MIN_LEVEL), DORMANT)
            st["asked"] = 0.0
            write_state(st)

    # Never block twice in a row — the turn we just caused must end.
    if from_our_block:
        return 0

    # 2. At most one action per interval of the current level.
    if now - st["last"] < window_seconds(st["level"]):
        return 0
    st["last"] = now

    # 3. Something reached the brain within the interval: stay silent, and
    #    wake up if asleep.
    if landed_since(folders, now - window_seconds(st["level"])):
        if st["level"] == DORMANT:
            st["level"] = 0
        write_state(st)
        return 0

    if st["level"] == DORMANT:            # asleep, nothing to wake up for
        write_state(st)
        return 0

    # 4. Ask — but only if we can record that we asked.
    st["asked"] = now
    if not write_state(st):
        return 0

    hours = window_seconds(st["level"]) / 3600.0
    left = DORMANT - st["level"]
    backoff = (f"If there is nothing, this check asks half as often next time "
               f"({left} more empty answer{'s' if left != 1 else ''} and it "
               f"sleeps until the vault fills again) — so an honest 'nothing' "
               f"is a useful answer, not a failure.")
    reason = (
        f"Capture check (automatic hook, currently at most once every "
        f"{hours:.0f}h): nothing has reached the brain for a while. Check the "
        "capture triggers for THIS session once: (a) was a decision settled? "
        "(b) was a date or deadline named? (c) did something go live? (d) did "
        "a new person come up? (e) was a lesson learned the hard way? If YES: "
        f"run brain-capture now (inbox: {inbox}"
        + (f", decisions as a record in {decisions}" if decisions else "")
        + "), then end the turn normally. If NO: just end the turn "
        "— invent nothing. Say in one line what you captured, or that there "
        f"was nothing worth keeping. {backoff} If the human asks to stop being "
        f"asked at all, set level=5 in {state_path()} and tell them deleting "
        "that file undoes it."
    )
    print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                     # a hook must never break a session
        sys.exit(0)
