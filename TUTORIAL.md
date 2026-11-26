# Tutorial: from zero to a running brain

About 20 minutes plus an optional interview, for people new to Obsidian
and Claude Code. Each stage ends with a checkpoint.

## Stage 1 — Install the tools (10 min)

1. **Obsidian:** [obsidian.md](https://obsidian.md) → download →
   install → open. Configure nothing yet.
2. **Claude Code** needs a Claude subscription with Claude Code access
   ([claude.com](https://claude.com)). Open a terminal (Mac: `Cmd+Space`
   → "Terminal" · Windows: Start → "PowerShell" · Linux: any shell) and
   install it as described at
   [claude.com/claude-code](https://claude.com/claude-code).
   **On Windows**, first install
   [Git for Windows](https://git-scm.com/downloads/win) with default
   settings; the setup needs it. Problems: see the Windows section of
   [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
3. Type `claude` and sign in.

Prefer no terminal? Claude Code also ships as a desktop app for Mac and
Windows, and every step below works the same there. In an editor, use
the [Claude Code extension for VS Code](https://code.claude.com/docs/en/vs-code).

**Checkpoint:** Claude greets you with a prompt.

## Stage 2 — Start the setup (5–10 min, ends with your first win)

Claude downloads the kit itself. Start `claude` and say:

> Set up the second brain from this GitHub repo for me:
> https://github.com/nikolajhellhoeflinger/brainwarden — clone it and
> follow SETUP-FOR-CLAUDE.md step by step.

(Or clone the repo yourself, `cd` into it, start `claude` and say: "Read
SETUP-FOR-CLAUDE.md and set up my brain accordingly.")

Claude first asks: **is this brain for you, for your work, for both kept
apart, or for a company?** Unsure? Say "for me"; a work brain can be
added later. Then four short questions: your situation, the first thing
the brain should help with, your notes' language (German works fine)
and the next date you must not miss. From the answers Claude writes your
areas, a first project, deadlines and a `Home` page (company: one
procedure and the role that owns it).

**Checkpoint:** `ls ~/Brain` (or the path Claude named; PowerShell:
`dir ~\Brain`) shows numbered folders from `00-inbox` to `90-archive`,
depending on your answer, plus `_templates` with the note blueprints.
The `index.md` and two-line `CLAUDE.md` in each folder are Claude's
signposts; you can ignore them. Claude confirms your first project
(company: first procedure) is in place. If "capture:" is not recognized,
restart Claude Code once so the new skills load.

With "both, kept separate", `claude` opens the private brain and
`workbrain` the work one; Claude builds the private one first.

## Stage 3 — See it in Obsidian (2 min)

Obsidian → **"Open folder as vault"** → your vault folder (`~/Brain` by
default, `~/Brain-work` for a work brain) → **Home**.

**Checkpoint:** `Home` names your first project under "Right now"
(company: your first procedure), and you can click through to
[[Deadlines]].

## Stage 4 — The onboarding interview (10–15 min, optional)

Claude offers it at the end of setup, now or later. It teaches the brain
your people, goals and working style. Talk freely, skip anything, and
say "private" for what should stay out. A work brain skips the private
questions; a company brain asks about processes, roles and terms
instead.

**Checkpoint:** "About me" and people notes under
`30-knowledge/people/` exist, and the graph view shows first
connections. Company brain: "About this vault" and roles under
`60-roles/`, no notes about people. Skipped it? It waits as an open
question on `Home`.

## Stage 5 — Practice the five verbs (5 min)

| Verb | Say |
|---|---|
| **Capture** (any session) | `capture: idea for the next project — draft the outline by Friday` |
| **Ingest** (a PDF in `~/Brain/00-inbox/raw/`) | `ingest` |
| **Ask** (answers only from your notes) | `what does my brain know about my first project?` |
| **Review** (weekly, or now to test) | `brain review` |
| **Research** (fills open questions with sourced facts) | `research my brain` |

**Checkpoint:** after the review, `00-inbox/` holds only
`Inbox rule.md`, `index.md`, `CLAUDE.md` and `raw/`. **Those always
stay**: a permanent instruction sheet and the drop zone for PDFs. Each
capture is now a linked note, listed on `Home` under "New this week",
and the review reports the orphans and dead links it fixed.

## Your first week

| Day | What to do |
|---|---|
| Day 1 | Setup (this tutorial); interview now or later |
| Day 2–4 | Only **capture**: every idea, date, person. No sorting. |
| Day 5 | First **"brain review"** |
| Day 6–7 | Ask for the first **output** ("Build me a study sheet / project plan / draft for X from my notes") and try **"research my brain"** |

Then: capture as you go and review ten minutes a week; after a month
away, the next review catches up. **Measure it by output:** no text,
plan or study sheet after two weeks? Tell Claude exactly that.

## If something breaks

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md), or ask Claude ("why isn't
my inbox empty?").
