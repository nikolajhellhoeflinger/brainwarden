---
name: brain-capture
description: Frictionless capture into the Brain's inbox. Use when the user says "capture: …", "note this down", "remember this for my brain", or when a spontaneous idea, decision or date surfaces mid-session.
---

# Brain capture (zero friction)

A thought becomes a file in `<vault>/00-inbox/` IMMEDIATELY — no filing
questions, no tags. Sorting happens at the review.

**Conventions:** `<vault>` = **the vault this session runs in**: the
folder it was started in, or one above it, whose `CLAUDE.md` names a
vault mode (`personal`/`professional`/`company`) and that holds the
kit's `.tools/`. Otherwise the path on the `Brain vault:` line in your
global rules. Only when neither exists, `~/Brain` (a shared company
vault has no global line, so falling back to `~/Brain` there would
write into somebody's private vault). `python3` = your working python
command (on most Windows machines `py -3`; the global rules name it).

## Steps
0. **Read `<vault>/CLAUDE.md` before the session's first write** (once
   per session): vault language, schema and mode, which you lack unless
   the session started inside the vault. Not there? Wrong path or
   unfinished setup: say so; never write into a random folder.
1. Content = whatever follows "capture:" (or the thought from context
   when they say "capture that").
2. Write `<vault>/00-inbox/YYYY-MM-DD-<short-slug>.md`:
   ```markdown
   # <one-line title>

   <the thought, verbatim or lightly cleaned — fix voice-transcription
   typos, do NOT reinterpret the content. Write in the vault language.>

   _Captured: YYYY-MM-DD HH:MM · Context: <one line on where it came from>_
   ```
3. Confirm in ONE line, naming the destination on special cases:
   "✓ captured: <title> → Deadlines + Home". No essays.

## Special cases
- **Decisions — recognize them by MEANING, not keyword:** the human
  settles an open question ("decision: …", "Entscheidung: …",
  "décision :", "we're going with Postgres", "ok, no second supplier").
  In any language or wording, write a decision record to
  `<vault>/40-decisions/YYYY-MM-DD-slug.md` instead of an inbox file
  (template: `40-decisions/_template.md`): context, decision, rejected
  alternatives. Append-only.
  - **Reverses an earlier decision?** Search it first
    (`python3 <vault>/.tools/search.py <topic>`), then write both sides.
    New record: a `## Status` section with
    `Supersedes [40-decisions/<old>.md](40-decisions/<old>.md)`. OLD
    record: its `## Status` body is REPLACED by
    `Superseded by [<path>](<path>)` (append the section if it has
    none), and its frontmatter gets `status: deprecated`. Never leave an
    "in force" line above a supersede notice — an agent greps the first
    `## Status` and believes it. Nothing else in the old record changes;
    this section is the only exception to append-only.
  - **Only NARROWS an earlier decision?** An exception, a special case,
    a one-off rate is not a supersede (the old rule still holds
    elsewhere; `deprecated` would be false). New record:
    `Exception to [<path>](<path>)`; the old one's status line becomes
    `In force. Exception: [<path>](<path>)`. That is the only other
    change ever made to an old record.
  - **Either way, add the new record to `40-decisions/index.md` under
    entry points** and reset its `<!-- generated: -->` marker, or no
    signpost leads to it until the next review.
- **Dates:** a capture with a concrete date/deadline ALSO gets a
  one-liner in `<vault>/Deadlines.md` right away (date first). If it is
  among the next ~3 dates, refresh the "Next deadlines" block in
  `<vault>/Home.md` too. **A moved date REPLACES its line, never
  appended** — two dates for one appointment is worse than none. Find
  the old one (`python3 <vault>/.tools/search.py <old-date> <topic>`),
  update every hit (Deadlines.md, the project note's log, Home.md) and
  name the corrected files in your one line.
- **Reference material** ("keep this findable": a link, a quote, a
  recommendation): one inbox file; the review gives it the light
  treatment (tags, no atomization).
- **Several thoughts in one dump** (common with voice): split at clear
  topic boundaries, one file each.

When creating a note from a template, fill `{{DATE}}` (and `{{NAME}}`)
with real values — placeholders never leave `_templates/`.

## Company mode (only when the vault `CLAUDE.md` names the mode `company`)
Captures still go straight to the inbox. Anything about a person is
captured as a ROLE, not a dossier, and nothing you write becomes company
truth: a note leaving the inbox keeps `status: draft` until a human sets
`verified: {by: human:<name>, at: YYYY-MM-DD}`.

## Rules
- NEVER ask "where should I file this?" — the inbox is always right.
- One capture = one file. Two thoughts = two files.
- Capture what they said; never add a conclusion they didn't draw.
- Works from ANY session, whatever project is open.
