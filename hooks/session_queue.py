#!/usr/bin/env python3
"""Brainwarden — session queue (Claude Code "SessionEnd" hook, opt-in).

When a session ends it appends one line to a queue file: when, in which
project, which session, why it ended. The weekly review reads the queue and
asks about sessions it has not seen: "what came out of this?" This covers
work that leaves no changed files or git logs behind.

It never:

  - reads the transcript or records its path (the session id is enough);
  - calls a model (`SessionEnd` hooks share a 1.5-second budget);
  - writes into the vault (the queue lives next to the config; only the
    review turns it into notes, with a human present);
  - records content.

It appends instead of rewriting, and trims via a temp file plus
`os.replace`, so a hook killed at the 1.5-second mark cannot truncate the
queue.

Install (opt-in):

  1. copy to  <config>/hooks/session_queue.py
  2. add to the "SessionEnd" hooks in <config>/settings.json:

     {"hooks": {"SessionEnd": [{"hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/session_queue.py"}
     ]}]}}

Uninstall: delete the file, remove the entry, delete the queue.
Read it any time:  python3 <vault>/.tools/harvest.py --queue
"""
import json
import os
import re
import sys
from datetime import datetime, timezone

MAX_LINES = 500          # a rolling window; older lines fall off the top
TRIM_BYTES = 200_000     # only then is it worth rewriting the file at all


def config_dir():
    return os.path.expanduser(os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"))


def queue_path():
    return os.path.join(config_dir(), "state", "brainwarden-session-queue.tsv")


def clean(value):
    """One field, one line, no tabs — the file has to stay `cut`-able."""
    return re.sub(r"\s+", " ", str(value)).strip() or "?"


def trim(path):
    """Keep the last MAX_LINES. Written beside the file and moved into
    place, so an interrupted trim leaves the old queue intact."""
    tmp = path + ".tmp"
    try:
        # A trim killed at the 1.5-second mark leaves a stale `.tmp`; clear
        # it so it is not mistaken for a current failure later
        # (`harvest.py --queue` reports one if it finds it).
        if os.path.exists(tmp):
            os.remove(tmp)
        with open(path, encoding="utf-8", errors="ignore") as fh:
            lines = fh.read().splitlines()
        if len(lines) <= MAX_LINES:
            return
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines[-MAX_LINES:]) + "\n")
        os.replace(tmp, path)
    except OSError:
        try:
            os.remove(tmp)
        except OSError:
            pass


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
    raw = read_stdin()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {}
    if not isinstance(payload, dict):      # valid JSON, unexpected shape
        payload = {}

    # Documented reasons: `clear`, `resume`, `logout`, `prompt_input_exit`,
    # `bypass_permissions_disabled`, `other`. A resumed session has not ended.
    reason = payload.get("reason") or "other"
    if clean(reason) == "resume":
        return 0

    session = payload.get("session_id") or "?"
    cwd = payload.get("cwd") or os.getcwd()
    project = os.path.basename(str(cwd).rstrip(os.sep)) or "?"
    when = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")

    # Tabs, not JSON: a human can read this file, and so can `cut`.
    line = "\t".join(clean(x) for x in (when, project, session, reason))

    path = queue_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        if os.path.getsize(path) > TRIM_BYTES:
            trim(path)
    except OSError:
        pass          # a queue that cannot be written must never break a session

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                      # a hook must never break a session
        sys.exit(0)
