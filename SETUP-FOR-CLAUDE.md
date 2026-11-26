# Setup runbook (for Claude Code — work through step by step)

You are setting up a "second brain" for your human: an Obsidian vault you
read and maintain in every session. The kit holds only structure. Build a
visible first win within minutes; the deep interview comes after it
(Step 8b).

The three modes, `personal`, `professional` and `company`, share these
steps. Unmarked instructions apply to all three.

**Substitute in every command and every file you write:**
- `<vault>` → the vault's real absolute path (e.g. `/Users/lena/Brain`).
- `<python>` → the python command that worked in Step 2 (`python3`,
  `python` or `py -3`).

Never leave `<vault>`, `<python>` or a default path like `~/Brain` in a
file for a vault that lives elsewhere.

## Step 0 — How you run this setup (posture — no questions yet)
The human may not know the kit, Obsidian or Git. You drive:
- Use the human's language from your first reply on. This runbook is
  English; the conversation is theirs.
- Explain each step in one sentence before doing it.
- Ask before writing anything outside the vault: `~/.claude/CLAUDE.md`,
  the skills directory and the shell profile (Step 4).
- Never guess an answer they have not given.
- Never say "mode", "personal/professional/company", "PARA" or
  "Zettelkasten" to them.

## Step 1 — Ask this FIRST: which brain is this?
Before anything else, send one short message:

> "One question before we start: is this brain for you personally, for
> your work, or one that several people in a company use together?
>
> 1 — **for me**: my life, school/studies, projects, private things
> 2 — **for my work**: my professional knowledge, kept apart from private
> 3 — **both, kept separate**: one for me, one for work
> 4 — **for a company**: several people share it and add to it"

Map the answer silently:

| Answer | Mode(s) | Vaults |
|---|---|---|
| 1 | `personal` | one |
| 2 | `professional` | one |
| 3 | `personal` + `professional` | **two** (Steps 3–9 run once per vault) |
| 4 | `company` | one |

Other combinations (e.g. "for me and for our company"): one vault per
purpose, built one after another, the personal one first. `company` is
always its own vault, never a folder inside a private one.

Unclear, or "I don't know"? Use `personal` and say: *"I'll build your
personal one — we can add a work brain any time."* The mode is recorded
in Step 6 and in the root `index.md`; later sessions read it there.

**What the mode changes:**

| | `personal` | `professional` | `company` |
|---|---|---|---|
| Folders | `00,10,20,30(+people),40,90` | the same **+ `50-processes/` + `60-contribution/`** | `00,30,40,50,60,70,80,90` — **no** projects/areas, **no** `people/` |
| Self page | `About me.md` | `About me.md` | `About this vault.md` |
| First win | first project + dates | + first workflow | first SOP + the role that owns it |
| Frontmatter | base schema | base **+ `ownership:`** (the one required field; `status:`/`confidentiality:` recommended) | base + `status:` + `owner:`/`audience:`/`confidentiality:`/`review_due:` |
| Interview | person track | person track, work only | process track (Step 8) |
| Who writes | the human | the human | anyone; published after approval |
| Modules 50–80 | free for their own | `50` and `60` taken, `70–80` free | all taken — no user modules |

A company vault has `60-roles/` (role descriptions) instead of
`30-knowledge/people/`: no dossiers on colleagues.

### 1a. Answer 3 — two brains, and how they stay apart
Tell them:

> "You'll get two separate brains: `claude` opens the private one,
> `workbrain` the work one — separate notes, separate rules, separate
> sessions. Nothing crosses over."

The second brain also gets its own Claude Code configuration directory
and a shell alias (Steps 4b, 6). Finish the private vault (Steps 3–9)
before starting the work vault.

### 1b. `company` only — four more questions, in ONE message
1. **What's the company called?** (used for the vault name and its
   front page)
2. **Which areas are there — who does what?** (2–8 in their words:
   sales, workshop, accounting, warehouse …)
3. **Who may approve content — who says "this is now the official
   version"?** (a name or a role; may be them)
4. **Is there knowledge that not everyone in the company may see?**

With question 4, say this, so they do not rely on protection the kit
does not give:

> "A field in the file can mark something as confidential, but it does not
> lock anything: everyone who can open the folder can read every file in
> it. Real separation only comes from a second, separate vault with its
> own access rights. So: is there anything that must be genuinely
> unreadable for part of the team? Then it belongs in its own vault, and
> we decide that now, not later."

Record the answers in `About this vault.md` (Step 5): the name replaces
`{{COMPANY}}` ("Whose knowledge this is"); the approver goes into "Who
may release content", the audience into "Who may read it", the areas
into a new `## Areas` section (one line each), the answer to question 4
into "What is in here — and what is not".

### 1c. `company` only — two things you say out loud once
Say both, as a pointer and not legal advice (the company's legal contact
or works council decides):
- **No usage tracking.** In Austria and Germany, logging who searched for
  what is regularly subject to works-council co-determination. The kit
  keeps no search log, per-person statistics or usage telemetry; keep it
  that way (the optional unattended review logs only its own vault
  changes; see TROUBLESHOOTING.md).
- **People must be able to tell it's an AI** (EU AI Act transparency
  obligation, inside companies too since August 2026): keep the first
  lines of `About this vault.md` saying Claude maintains the vault, and
  the `generated:` line on notes drafted by AI.

## Step 2 — Prerequisites
Check all of these before touching anything:
- Given only the repo URL? Clone the kit first:
  `git clone https://github.com/nikolajhellhoeflinger/brainwarden.git`
- **Obsidian** installed (if not: obsidian.md, wait).
- **git** available (`git --version`; if missing, guide the install — on
  macOS `xcode-select --install`), with an identity set
  (`git config user.name`; if empty, set name and email with their OK, or
  the first commit fails with "Please tell me who you are").
- **python**: try `python3 --version` → `python --version` → (Windows)
  `py -3 --version`. The first that works is `<python>` from now on.
  None? Guide the install (python.org, "Add to PATH" checked).
- No git? The setup still works: download the ZIP instead of cloning,
  skip the commit steps, and say so.

### 2a. Which shell these commands assume
All commands are for a **POSIX shell**: zsh or bash on macOS, bash on
Linux, **Git Bash** on Windows (Claude Code's Bash tool uses it there).
PowerShell and `cmd` lack `ls`, `grep`, `rm -rf`, `cp -R`, `find`, `sed`
and `~` expansion; a human there needs
[Git for Windows](https://git-scm.com/downloads/win) (default settings)
and a fresh terminal, and `claude doctor` must list Git Bash. Commands a
human types come with a PowerShell equivalent.
- Windows usually has no `python3`; without Python, a bare `python3`
  opens the Microsoft Store instead of failing. Use `<python>`.
- `sed` and `find` differ between macOS (BSD) and Linux/Git Bash (GNU),
  `sed -i` most of all. Do such edits in Python.

## Step 3 — Create the vault
Run this step once per vault; for answer 3, the private vault first,
through Step 9.

### 3a. Where it lives
Offer the default; never impose it:

| Mode | Default path | Started with |
|---|---|---|
| `personal` | `~/Brain` | `claude` (Step 4) |
| `professional` | `~/Brain-work` | `claude` — as a SECOND brain next to a private one: `workbrain` (Step 4b) |
| `company` | `~/Brain-<company-slug>` (e.g. `~/Brain-acme`) | `cd <vault> && teambrain` — the `cd` is not optional, see below |

**A company brain opens only with `cd <vault> && teambrain`:** it has no
global rules block (Step 6) and its skills sit inside the vault (Step
4a), so `teambrain` alone knows nothing about the vault. Say so at
handover and in the handover note; it is the most likely cause of "the
brain doesn't work".

**Target path exists?** Stop and ask: adopt it (3c), merge into it, or
pick another path. Never copy over an existing folder unasked.

**Their vault lives elsewhere** (iCloud folder, other name,
`~/Documents/Notes` …)? Don't move it: adopt it in place (3c) and record
its real path in Step 6's `Brain vault:` line. In iCloud, Dropbox or
OneDrive, say that Git there risks corruption and offer to move it, with
their OK, before Step 7. From here on, `<vault>` is the path you used.

### 3b. Fresh install (ONLY into an empty or non-existent folder)
From the kit folder:

```
<python> assemble.py <vault> <mode>
```

It copies the core, applies the mode's overlays from
`vault-template/modules/` in order (`processes/` for `professional` and
`company`, then `company/` for `company`; none for `personal`), leaves
out `modules/` and the files a shared vault must not carry, and never
overwrites a file that existed before it ran. In `company` mode it swaps
in the company rules, signposts and templates (listed in 3c); never
restore the seven personal templates it leaves out.

Check its output: the mode matches what they asked for, and the
"existing files left untouched" list is empty. Not empty? Not a fresh
install; switch to 3c.

### 3c. Adopting an existing vault — add only what is missing
**Never copy the template over an existing vault by hand:** `cp -R`
overwrites their own `Home.md`, `About me.md`, `index.md` …. Run the 3b
command:

    <python> assemble.py <vault> <mode>

It adds what is missing, deletes nothing, and lists the files it left
untouched and any paths a company vault must not carry. Confirm nothing
of theirs changed (`cd <vault> && git status` in a Git repo, otherwise
spot-check their `Home.md` and one note). Then, by hand:
- Map their folders onto this mode's rules (inbox? projects? areas?
  processes?) and add only what is missing.
- Structures clash badly? Offer the **quarantine path**: move their old
  notes into `<vault>/OLD_VAULT/`, untouched, and integrate them at
  reviews. Never delete or restructure existing notes without an
  explicit OK per change.
- Never delete a folder this mode does not use (3d); note it under
  Home's "Open questions".
- List notes still outside the core folders under Home's "Open
  questions" as a migration backlog. Tell them capture now writes to
  `00-inbox/`; note any old inbox file for merging at the first review.
- **Existing `Home.md`:** copy the four marker pairs from
  `vault-template/Home.md` into THEIR Home (`<!-- block:right-now -->` …
  `<!-- /block:right-now -->`, then `next-deadlines`, `open-questions`,
  `new-this-week`, each under a heading), their content kept around
  them. Thin Home? Offer the template with their links folded in. Do
  this BEFORE Step 5.
- **Existing `.gitignore`:** with their OK, append the lines of
  `vault-template/.gitignore` that theirs lacks (they keep exports and
  the runner's state out of the history). Never drop or reorder theirs.
- **Existing `CLAUDE.md` or root `index.md`:** it lacks the kit's rules
  (mode line, language line, note schema, red line, folder map). With
  their OK, fold in `vault-template/CLAUDE.md` (plus the mode overlay's;
  `company`: next bullet) and the root `index.md`, keeping their lines.
  `hygiene.py` must then report the right `mode:` ("not detected": the
  mode line is still missing).
- **`company`:** `head -1 <vault>/CLAUDE.md` must say *shared company
  knowledge vault*, and `hygiene.py` must report `mode: company`. Copy
  the company `CLAUDE.md`, `Home.md`, `Deadlines.md` and the six
  `index.md` (root, `00-inbox/`, `30-knowledge/`, `40-decisions/`,
  `90-archive/`, `_templates/`) over by hand, one OK per file. Never
  overwrite a Home with their content: copy the company one aside and
  fold their content into it, one OK per change.
- **`company`:** copy the company `_templates/knowledge-note.md`,
  `source-note.md`, `sop-note.md` and `40-decisions/_template.md` over
  existing ones; without this mode's four required fields, notes built
  from them land in `hygiene.py`'s **frontmatter gaps**. If they edited
  one, diff and port their changes.

### 3d. What must exist afterwards

| Mode | Folders |
|---|---|
| `personal` | `00-inbox/` (+`raw/`), `10-projects/`, `20-areas/`, `30-knowledge/` (+`people/`), `40-decisions/`, `90-archive/` |
| `professional` | the same **+ `50-processes/` + `60-contribution/`** |
| `company` | `00-inbox/` (+`raw/`, +`suggestions/`), `30-knowledge/`, `40-decisions/`, `50-processes/`, `60-roles/`, `70-onboarding/`, `80-partners/`, `90-archive/` — no `10-projects/`, no `20-areas/`, no `30-knowledge/people/` |

Plus, in every mode: `_templates/`, `.tools/` (with `search.py`,
`hygiene.py`, `harvest.py`, `INTERVIEW.md` and `hooks/`), `Home.md`,
`Deadlines.md`, `CLAUDE.md`, `index.md` and the self page (`About me.md`,
or `About this vault.md` in `company`). **`company` adds** `THIS-COPY.md`
in the root and `.tools/progress.py`. `modules/` must NOT exist in the
vault; if it does, the copy was made by hand.

A folder is missing? An overlay was skipped: apply it (3b). Never create
a module folder with `mkdir`; the overlay also brings its `index.md`,
`CLAUDE.md` and note template.

`00-inbox/suggestions/` (company only) is where colleagues without
release rights contribute: everything in there is a proposal by
definition, and the weekly review empties it together with the inbox.
Say that sentence when you hand over a company vault.

### 3e. Waypoints — two files per folder
Every folder that holds notes gets exactly two navigation files:

- `CLAUDE.md` — always exactly this content, nothing else:
  ```markdown
  <!-- Loaded automatically when Claude reads a file in this folder. -->
  @index.md
  ```
- `index.md` — the waypoint, max ~25 lines, in the vault language:
  ```markdown
  # <folder name>

  <one line: what lives here>

  **Rules here:** <only what differs from the vault rules>
  **NOT here:** <where that belongs instead, with a real path>

  ## Entry points
  * [note-name](note-name.md) - one line why you'd start here

  <!-- generated: YYYY-MM-DD -->
  ```

`index.md` rules: real relative paths, **never** `[[wikilinks]]` (an
agent cannot resolve them); no file names with spaces; entry points only,
never a full listing; nothing an agent could see for itself. Nothing to
list yet? Write
`* (none yet — the first note lands here)`.

The template ships both files for every folder it creates, `_templates/`
included. Write the pair yourself only for a folder you add later (a
module from 5c, a promoted project folder). `.tools/` gets none. After
Step 5, update the "Entry points" of every folder you filled.

The **root `index.md`** is the cold entry for any agent: mode, vault
language, a one-line map per folder, pointers to `Home.md` and
`CLAUDE.md`, the search command. Fill its `{{MODE}}` and `{{LANGUAGE}}`
in 5e (the company overlay ships its own). Its folder map must list
exactly the folders that exist.

### 3f. What survives deleting the repo
`assemble.py` (3b and 3c) copies `INTERVIEW.md` and `hooks/` (three hooks
and their README, see 8c) into `<vault>/.tools/` and lists them under
"kept for later". `.tools/` is kit infrastructure: search and the Step 9
placeholder check skip it. Never edit or fill anything there. The hooks
stay inactive until a human adds an entry to their own `settings.json`.

**Verify this step:** `<vault>/CLAUDE.md`, `<vault>/index.md`,
`<vault>/.tools/search.py` and `<vault>/.tools/INTERVIEW.md` exist.
Mention that they may delete the cloned repo folder after the setup.

## Step 4 — Install the skills
Installed the kit as a Claude Code plugin? The five skills are already
loaded; skip the copying, but read 4b if there are two brains.

### 4a. One brain (the normal case)
If `~/.claude/skills/brain-capture` (or `-ingest` / `-review` /
`-research` / `-ask`) exists, stop and ask; never overwrite a skill
silently. Then `mkdir -p ~/.claude/skills` and copy the five folders from
`skills/` into it. If you just created that directory, Claude Code needs
one restart before the first "capture:".

**`company`: put the skills INSIDE the vault instead,** and skip
`~/.claude/` entirely:

```bash
mkdir -p <vault>/.claude/skills && cp -R skills/. <vault>/.claude/skills/
```

They then travel with every copy, load only in that folder (never in a
private session) and leave with the vault. `capture:` works only inside
the vault; that is intended.

### 4b. Two brains — separate configuration directories
The first brain (the `personal` one if there is one) keeps `~/.claude`
and stays ambient. A `company` vault is **never** the ambient one. Each
further brain gets its own configuration directory: `~/.claude-work`
(professional) or `~/.claude-<company-slug>` (company).

1. `mkdir -p ~/.claude-work/skills`
2. Copy the same five skill folders in there (each configuration
   directory needs its own copy).
3. With their OK, add one line to their shell profile (`~/.zshrc` on
   macOS, `~/.bashrc` on most Linux/Git-Bash setups):
   ```bash
   alias workbrain='CLAUDE_CONFIG_DIR=~/.claude-work claude'
   ```
   (`company`: `alias teambrain='CLAUDE_CONFIG_DIR=~/.claude-acme claude'`
   — but do NOT copy the skills there: they already sit in
   `<vault>/.claude/skills/` from Step 4a.)
4. `source ~/.zshrc` (or open a new terminal). `workbrain` now starts
   Claude Code with only the work brain's rules, skills and sessions;
   `teambrain` only separates sessions and settings (3a).

Tell them in one sentence that the brains are cleanly separate, and the
two words they type: `claude` for private, `workbrain` for work. The
first start in a fresh configuration directory asks for a one-time
login; that is normal.

Only if they explicitly want everyday `claude` sessions brain-free: give
BOTH brains an alias (`brain` and `workbrain`, each with its own
configuration directory) and leave `~/.claude/CLAUDE.md` untouched.

## Step 5 — Adapt to the human + build the first win (the most important step)

### 5a. The questions — ONE short message, then you do the heavy lifting
`personal` / `professional`:
1. **What's your life right now?** (school / university / job / own
   business / mix — free text is fine) — in a work brain: what your work
   actually consists of.
2. **What's the first thing this brain should help you with?** (an exam,
   a project plan, an application, a decision to make … — this becomes
   the first project)
3. **Which language should your notes live in?** (the repo is English;
   the content can be German, anything)
4. **What's the next date you must not miss?** (one is enough — an exam,
   a submission, an appointment, a renewal, a trip)

`company` (the four questions from 1b are already answered):
1. **Which process should we write down first — something you could
   explain to a new colleague today?** (order intake, month-end closing,
   handling a complaint, onboarding a supplier …)
2. **Which language should the content live in?**
3. **Which fixed date must this vault not miss?** (audit, inventory,
   contract renewal, a recurring monthly deadline)

Without a real date, "Next deadlines" on `Home` stays empty. No answer?
Nudge ONCE with examples (*"exam · rent · a contract that renews · a
birthday · a doctor's appointment"*). Still none? Write `- (no dates yet)`
into that block and "collect the first dates" under Home's "Open
questions", then move on.

Ask nothing else before the first win.

### 5b. Build the first win — real notes, within minutes
Build from those answers, without further questions.

**House rules:**
- **One note = one file:** `10-projects/<slug>.md`, `20-areas/<slug>.md`,
  `50-processes/<slug>.md`. Only when a SECOND file belongs to a note
  does it become a folder: `10-projects/<slug>/` with `<slug>.md` and the
  two waypoint files (3e).
- **`maturity:`** (`seed` / `growing` / `evergreen`) only on knowledge
  notes in `30-knowledge/`. Project, area, process, role, partner and
  decision notes get `status:`, never maturity.
- **`status: draft | stable | deprecated`** on every note outside
  `00-inbox/` from `professional` upwards (recommended there; `hygiene.py`
  requires only `ownership:` in `professional`). `company` adds `owner:`,
  `audience:`, `confidentiality:` and `review_due:` (default: today + 12
  months; say that you set it).
- File names kebab-case, no spaces, no umlauts; content in their
  language.
- Every date you hear also goes into `Deadlines.md`: one line, date
  first.

**Adopting?** Run `search.py` for the project, areas or processes from
their answers first. Already there in the old structure? MOVE them into
place (one OK per move) and enrich them; never create a duplicate.

**`personal` / `professional`:**
1. **Propose 2–4 areas** from answer 1, in THEIR words ("I'd create
   these areas for you: … — rename anything"), then create one note per
   area in `20-areas/` from `_templates/area-note.md`, named like the
   area (`20-areas/studies.md`).
2. **Create the first project** in `10-projects/` from answer 2
   (`_templates/project-note.md`): the goal in their words, a concrete
   next step, every date from answer 4.
3. **`professional` additionally: the first workflow.** Write the
   recurring task from answer 1 that annoys them most into
   `50-processes/<slug>.md` (`_templates/sop-note.md`): trigger, 3–7
   steps in their words, who is involved, what usually goes wrong.
4. **Fill `Home.md`:** the project (as a `[[wikilink]]` with a one-line
   status) and any process in `right-now`; the "Areas:" line (carrying
   `<!-- keep:areas-line -->`) linking every area note, so none is an
   orphan; their dates in `next-deadlines`; anything unfilled in
   `open-questions`. Replace only what sits between a marker pair.

**`company`** (processes, roles and knowledge; no projects or areas):
1. **Write the first SOP** into `50-processes/<slug>.md`
   (`_templates/sop-note.md`): purpose in one line, trigger, 3–7 concrete
   steps in the company's own words, owner, what usually goes wrong.
   Write nothing they did not say.
2. **Create the role that owns it** in `60-roles/<role>.md`
   (`_templates/role-note.md`): responsibilities, the processes it owns,
   what it decides. The ROLE, never a person dossier.
3. **Onboarding entry:** add the SOP to `70-onboarding/onboarding-path.md`
   as the first step ("day one: read this"), with a real relative link.
4. **Fill `Home.md`:** the SOP in `right-now`, the role and the
   onboarding path as links, dates in `next-deadlines`, everything open
   (approval, areas without a process yet) in `open-questions`. Replace
   only what sits between a marker pair.
5. **Set the company frontmatter** on all three notes: `owner:` (1b
   question 3), `audience:`, `confidentiality:`, `review_due:`,
   `status: draft` until the person named in 1b confirms, and
   `generated:` on anything you drafted. `verified:` is never yours to
   fill.

Then, in every mode:
- **Update the waypoints** of the folders you filled (3e): new notes as
  "Entry points", `generated:` set to today. **`company` exception:**
  `50-processes/index.md` lists only stable, verified processes; leave
  the draft SOP off it. `Home.md` and the onboarding path link it
  (`hygiene.py`: `orphans: 0`, `not reachable from a signpost: 0`). At
  handover, say the empty list means "nothing released yet".
- **Show it:** have them open Obsidian ("Open folder as vault" →
  `<vault>`) and click **Home**.

### 5c. Offer the optional modules (`personal` / `professional` only)
Offer this list in one short message. Each pick becomes a numbered
top-level folder in the free range (`50–80` in `personal`, `70–80` in
`professional`):
- **`50-journal/`** — daily/weekly journaling (template ships with the
  kit: `_templates/journal-entry.md`)
- **`60-media/`** — reading/watch log (books, papers, videos with one-line
  verdicts)
- **`70-health/`** or **`70-training/`** — workouts, habits, metrics
- **`80-money/`** — budgets, subscriptions, financial decisions
- or anything they name themselves — their word, their folder

A module gets one intro note, the two waypoint files (3e) and a link from
`Home.md` ("How to use your brain" block). They can ask for one later
("add a journal module to my brain").

`company` has no user modules (`50–80` are processes, roles, onboarding,
partners); anything else fits one of those four or is a decision
(`40-decisions/`).

### 5d. What is fixed vs. free (tell them this!)
Fixed, because the tools read them as exact tokens:
- **The numbered prefixes** (`00-`, `10-` … `90-`).
- **The four `<!-- block:… -->` markers in `Home.md`**, every other
  `<!-- … -->` marker (`<!-- keep:… -->`, `<!-- short-notes-ok -->`,
  `<!-- kit-page -->`), and the `Kit version:` and `Mode:` labels.
- **The ORDER of the two frontmatter scales:** `maturity:` runs
  unfinished → worked out, `status:` runs draft → released → retired. The
  words may be translated (the tools read them from the vault's
  `CLAUDE.md`); the order may not change.
- **Three file names:** `CLAUDE.md`, `index.md` and `Home.md`. Their
  content and headings are free.

**Everything else is free:** folder names, the other kit pages
(`Deadlines.md`, `About me.md` / `About this vault.md`, `Inbox rule.md`),
headings, area names, modules, templates, the review day. A German vault
can have `40-entscheidungen/`, `90-archiv/`, `Termine.md`,
`Über mich.md`, `Inbox-Regel.md`. A renamed kit page keeps its
`<!-- kit-page -->` marker.
- **Translating an existing vault later?** Keep numbers and markers,
  rename the rest, then run `<python> <vault>/.tools/hygiene.py`: renames
  break the relative links in `index.md` and `Home.md`. Zero dead links
  means it worked.

### 5e. Language, name, and the remaining placeholders
1. **Language and mode:** replace `{{LANGUAGE}}` (the ENGLISH name of the
   language, e.g. `German`) and `{{MODE}}` (`personal`, `professional` or
   `company`) in `<vault>/CLAUDE.md` and the root `index.md`. In
   `company` mode both files already name the mode; only `{{LANGUAGE}}`
   is left.

   `company` also fills `{{COMPANY}}` and **every** `<…>` field (nine in
   all; `review_due:` gets today + 12 months):

   | File | Fill |
   |---|---|
   | `About this vault.md` | `{{COMPANY}}`, `owner:`, `review_due:`, and in the prose `**What it is for:**`, `**Who may read it:**`, `**Who may release content:**` |
   | `Deadlines.md` | `owner:`, `review_due:` |
   | `70-onboarding/onboarding-path.md` | `{{COMPANY}}`, `owner:`, `review_due:` |

   Neither the Step 9 `{{…}}` scan nor `hygiene.py` sees the `<…>` fields
   (`owner: <role that owns this vault>` passes as filled). Use:

       cd <vault> && <python> .tools/progress.py --open

   It lists each file with an unfilled `<…>` field and counts down to
   zero. A fresh company vault reports **11 open gaps in 4 files (9
   unfilled `<…>` fields, 2 marked TO FILL IN)**; more means notes of
   your own have open fields. Backticked command examples and the note
   templates are not counted. **Do not hunt these with `grep`:**
   `**What it is for:**` wraps across two lines, and the skills in
   `<vault>/.claude/skills/` are full of `<…>` by design (never edit
   them).
2. **Not English? Translate in two waves.**
   - **Before the handover:** `Home.md`, `Inbox rule.md`, the self page,
     `Deadlines.md`, the notes from Step 5b, and in `company` mode
     `THIS-COPY.md`.
   - **After the handover, same session, saying that you do it:**
     `_templates/`, `40-decisions/_template.md`, `00-inbox/raw/README.md`
     and every `index.md` waypoint. Keep the `{{…}}` tokens in them.
   - The vault's `CLAUDE.md` stays English (Claude reads it). In a
     company vault, translate it too if they ask.
   - **Keep untranslated** (5d): HTML marker comments; the `Kit version:`
     and `Mode:` labels (translated, they make the vault look pre-1.0 to
     the update path); the mode values `personal` / `professional` /
     `company`; frontmatter KEYS (`type:`, `status:`, `maturity:`,
     `owner:` …); the command words `capture:` and `brain review`.
   - **May be translated:** file and folder names, headings, prose, and
     frontmatter VALUES, if you translate them in the schema block of the
     vault's `CLAUDE.md` too and keep each scale's order. With
     `status: entwurf | gültig | überholt` there, `hygiene.py`,
     `search.py --stats` and `progress.py` follow; values translated only
     in the notes silently disable those checks.
   - Supersede keywords: write `Supersedes` / `Superseded by`, as the
     templates do (`Ersetzt durch` / `remplacé par` work only at the
     start of a line).
3. **Translate the four Home headings; keep the markers.** The skills
   refresh what sits between each marker pair
   (`<!-- block:right-now -->` … `<!-- /block:right-now -->`, likewise
   `next-deadlines`, `open-questions`, `new-this-week`), not the
   headings.
   - Leave every marker byte-identical, and never delete a line carrying
     `<!-- keep:… -->` (e.g. the "Areas:" line); update its content.
   - Adopted Home? Verify the markers from 3c before translating, or the
     first review overwrites the wrong lines.
4. **The first name** (`personal` / `professional`): ask once and write
   it in two places:
   - `About me.md`, first line under the heading: `**Name:** <first name>`
   - the `Human:` line of the Step 6 rules block.
   `company` records no name: no personal dossier in a shared vault, and
   decision records name the deciding **role**.
5. **`{{DATE}}`:** today's date in the self page and `Deadlines.md`; the
   real date in every note you created from a template.
   - **`professional`:** also `handover.md` in the vault root (one
     `{{DATE}}`).
   - **`company`:** also `THIS-COPY.md`, FOUR times. The copy's date,
     `created:` and the first changelog line get today; **`review_due:`
     gets today + 12 months** (today would mark the vault expired the
     next morning). Its two `TO FILL IN` lines are answered in Step 7a;
     if undecided, leave them, say so, and list them under Home's open
     questions. `progress.py` counts each as an open gap.
   - **Never fill the `{{DATE}}`/`{{NAME}}` tokens in the templates**
     (`_templates/`, `40-decisions/_template.md`) or anywhere in
     `.tools/`; templates are filled per note at creation time.
     Translating their surrounding prose is fine.

## Step 6 — Global rules

**`company`: skip this whole step.** A global line would point every
private session at company content; a session started in the vault finds
the mode in `<vault>/CLAUDE.md`. The rest applies to `personal` and
`professional`.

With their OK, write this block into the rules file **of this vault's
configuration directory**: `~/.claude/CLAUDE.md` for the ambient brain,
`~/.claude-work/CLAUDE.md` for a second brain (Step 4b). Create the file
if needed.

```markdown
## Brain (Obsidian vault + Claude working directory)
- Brain vault: <vault>   ← the actual path; every brain-* skill uses this
- Mode: <personal|professional|company> — <one line: what belongs in here>
- Human: <first name>
- **This vault is my context. Consult it BEFORE answering from general
  knowledge** whenever a question touches my life, my work, my projects,
  my people, my past decisions, or "what did we say about X". Do not
  guess and do not ask me things the vault already knows.
- **On a conflict, the vault wins.** If a note and your training data
  disagree about my situation, the note is right and you say so.
- Cold start in the vault: read `<vault>/index.md` (the folder map, one
  line each) — then `<vault>/CLAUDE.md` before writing anything.
- Retrieval: run `<python> <vault>/.tools/search.py <terms>` first, then
  read only the hits — never the whole vault. Landed in a folder? Its
  `index.md` says what belongs there and what does not. "What do I know
  about X?" → skill brain-ask.
- Capture triggers: whenever a session produces (a) a decision, (b) a
  deadline, (c) a milestone, (d) a new person, (e) a hard-won lesson →
  file it to <vault>/00-inbox/ immediately (brain-capture). One line of
  confirmation is enough; never let it interrupt what we were doing.
- Weekly ritual: "brain review" (inbox to zero, hygiene, refresh Home.md,
  git commit).
```

Substitute **every** `<vault>`, `<python>`, `<first name>` and `<mode>`,
including the paths in the retrieval and capture lines; a stale
`~/Brain/00-inbox/` there sends every capture to a folder that does not
exist. On most Windows machines `<python>` is `py -3`.

Two or more brains? Add one line to each block so no session writes into
the wrong vault:
```markdown
- Other brain on this machine: <other vault> (work) — started with
  `workbrain`; never write its content into this vault.
```

Check the file you wrote (`~/.claude-work/CLAUDE.md` for a second
brain); this must return nothing:
```bash
grep -nE "<(vault|python|first name|personal\|professional\|company)>|^- Mode: *$" ~/.claude/CLAUDE.md
```

Re-running the setup? `grep -n "Brain vault:"` that file first; if the
block exists, REPLACE it instead of appending a second one.

## Step 7 — Git: commit the clean scaffold
`cd <vault> && git init && git add -A && git commit -m "brain setup"`
(before the interview, so the first commit is the clean baseline).
If the git identity was missing in Step 2, set it **repo-local** here —
`cd <vault> && git config user.name "…" && git config user.email "…"` —
never `--global` without asking first.

### 7a. `company` only — how the other people actually get it
**Do not skip to Git.** Ask first, in one message:

> "Two things I can't decide for you. First: how do the other <n> people
> get this folder — is there a Git server you already use, or is a
> folder on the office drive plus a copy on each machine closer to how
> you work? Second: of those <n>, how many will actually open a terminal?"

The second answer decides the first:
- **Nearly nobody opens a terminal** (usual in a small company): one
  maintainer keeps the vault in Git and works in Claude Code. Everyone
  else gets a **copy** and reads it in Claude Cowork (`COWORK.md`, 7b),
  Obsidian or any text editor, and sends contributions as files in
  `00-inbox/suggestions/` back to the maintainer by a channel the
  company already uses.
- **Several people use Git:** a **private remote** everyone clones and
  pulls, never a synced cloud folder (Git plus Dropbox/OneDrive corrupts
  vaults). Still **one writer**: only the maintainer commits to the
  shared branch; the other clones are read-only and contribute through
  `00-inbox/suggestions/`. The kit has no conflict workflow; if they need
  several writers, say they need a Git workflow (branches, pull requests)
  outside this kit, or perhaps a wiki.

Before the first push or copy, check that the vault holds no credentials
and no personal data that does not belong there.

Then replace both markers in `THIS-COPY.md`, or say which one stays open
and put it under Home's open questions:
1. the distribution route (`TO FILL IN (IT / knowledge owner)`),
2. where a finished suggestion goes (`TO FILL IN (knowledge owner)`).

**Name the recurring chore; nothing automates it.** On every release the
maintainer raises the date at the top of `THIS-COPY.md`, adds a changelog
line there, and pushes or re-sends; `brain review` does none of this.
Tell the maintainer to do all three by hand on review day.

### 7b. `company` only — hand over `COWORK.md`, don't just mention it
`COWORK.md` tells colleagues without a terminal how to read the vault in
Claude Desktop. Do both:
- **Copy it into `<vault>/.tools/`** (`cp COWORK.md <vault>/.tools/`) and
  send it to them; the repo may be deleted. Not the vault root: there
  `search.py` ranks it among the notes and Obsidian lists it next to
  `Home.md`.
- **Translate the instruction block in its step 3** into the vault
  language and paste the vault's path into it; they copy it verbatim
  into Cowork.

## Step 8 — Two ways to deepen: the harvest, then the interview
Offer the harvest (8a) first; the interview (8b) then starts from real
material.

### 8a. The harvest — cold start from existing records (optional, `personal` and `professional` only)
Claude Code keeps session transcripts in `~/.claude/projects/`, 30 days
by default. `company`: skip this step; the transcripts are personal.

**Nothing is read without a yes; nothing is written without a second
yes.**

1. **Inventory, reading nothing.** `<python> <vault>/.tools/harvest.py`
   prints session counts, period and projects from file metadata only.
   Show it and ask whether to go on.
2. **State the expiry, once.** If `cleanupPeriodDays` is unset,
   transcripts older than 30 days are gone. Offer to raise it
   (`~/.claude/settings.json`); it is their configuration and needs an
   explicit yes.
3. **Pre-filter with no model.**
   `<python> <vault>/.tools/harvest.py --candidates --since <date>` drops
   harness injections, system plumbing, acknowledgements, duplicates and
   anything without a decision/date/milestone/lesson word.
4. **Judge a SAMPLE, not the archive.** Turn the newest ~20 candidates
   into proper notes and show them. Not convinced? Stop there.
5. **Only then the rest**, and only with their go.
6. **Every harvested note records its origin:** the date and session it
   came from.
7. **A harvested note is never a decision record.** A transcript line
   that *sounds* like a decision becomes a question to the human.

Cap: **at most 3 notes per session** harvested; "nothing worth keeping
in this one" is a correct and frequent result.

**Two more sources** — same tool, same two yeses, read-only, refused in
an unattended run:
- **Claude app chats.** The app's data export (Settings → Privacy →
  Export data; a .zip) holds every conversation.
  `<python> <vault>/.tools/harvest.py --claude-export <zip or folder>`
  lists date, title and how many messages THEY wrote, with no message
  text; `--grep <words>` and `--since <date>` narrow the list. They pick
  conversations; `--show <id>` prints only their own messages of one,
  never Claude's replies. Capture from that in the chat: origin in the
  note ("Claude export, <date>"), the cap of 3, never a decision record.
- **Their calendar.** `<python> <vault>/.tools/harvest.py --ics <file.ics>`
  prints the next 120 days (`--days N`) as `- YYYY-MM-DD Summary` lines,
  dates only. They pick: a deadline goes into `Deadlines.md`, a dentist
  appointment does not, and anything from a file goes under
  "Unconfirmed" until they confirm it. (Google Calendar exports a .zip
  with one .ics per calendar; unzip it and pass the right one.)

### 8b. The onboarding interview (recommended — but THEIR call)
Offer it; don't impose it. If the harvest ran, start with the gaps it
left.

> "Your brain is running. The next step is the onboarding interview
> (10–15 minutes) — it's what makes the brain really *know* you.
> Now or later?"

In `company` mode:

> "Your company brain is running. The next step is a walk-through of your
> processes (10–15 minutes): what runs how, who owns it, and the terms
> your company uses. Now or later?"

- **Now:** run `<vault>/.tools/INTERVIEW.md` (the vault's copy, not the
  repo's). Start with its Phase-0 consent question, then the track for
  this mode (person track for `personal`/`professional`, process track
  for `company`), in the vault language. Style models: the repo's
  `examples/`, or once it is deleted the vault's `_templates/`.
  Afterwards refresh `Home.md` and the waypoints, then commit.
- **Later:** write one note to `00-inbox/` ("run the onboarding interview
  — say: *interview me for my brain* — script: `.tools/INTERVIEW.md`")
  and list it under Home's "Open questions". Never pressure; it also
  works in pieces.

Either way, if anything changed after Step 7's baseline commit:
`cd <vault> && git add -A && git commit -m "onboarding"` — never hand over
a dirty tree.

### 8c. The safety net under capture (optional, mention it — do not install it)
`<vault>/.tools/hooks/` holds three optional Claude Code hooks:
- one checks at the end of a turn whether anything reached the inbox
  lately and, if not, makes Claude check the five capture triggers once;
- one writes a line per session end, so the weekly review can ask about
  sessions it never saw;
- `project_context.py`, at session start in a project's code folder,
  gives Claude a brief of what the brain knows about that project.

**Say they exist, in one sentence, and point at
`<vault>/.tools/hooks/README.md`.** Do not install them or ask a yes/no
question about them: a hook edits their global `settings.json`, which is
not part of the vault.

If they ask right away, install it, but read
`<vault>/.tools/hooks/README.md` first. On Windows use the entry form
from `TROUBLESHOOTING.md` (absolute path, doubled backslashes, the python
command that works there; `~` and `python3` both fail silently in
`settings.json`).

## Step 9 — Verify, then hand over
Run this checklist, show the results, and fix anything that fails.
Substitute `<vault>`, `<python>` and, for a second brain, the
configuration directory in every command. Run `hygiene.py` FIRST:

```
cd <vault> && <python> .tools/hygiene.py
```

Every rubric it prints must be `0`, and the `mode:` line must name this
vault's mode with nothing in brackets after it.
- **`portability`** flags a note in the wrong encoding (Windows Notepad
  "ANSI", PowerShell 5.1 `>`), two file names differing only in case, or
  a name Windows cannot create (`:` `?` `*` `"` `<` `>` `|`, or
  `aux`/`con`; such a name breaks `git clone` on Windows). Rename such
  files now.
- **`mode:` followed by `(NOT SET — …)`** means `{{MODE}}` was never
  replaced (5e), so the loosest schema applies and the vault reports
  clean by accident. Fix 5e and re-run.

**`company` also:** `cd <vault> && <python> .tools/progress.py`. It
reports how many notes carry `verified:` and how many gaps are open.
Both look bad at handover, since nothing is released yet. Say the
numbers out loud, explain them, and put the open gaps under Home's open
questions.

- [ ] `ls <vault>` shows exactly the folders of this mode (3d) plus their
      own modules — and **no `modules/` folder** (that one is kit
      scaffolding; if it is there, delete it — `rm -rf <vault>/modules`,
      PowerShell: `Remove-Item -Recurse -Force <vault>\modules`)
- [ ] every folder with notes has both waypoint files. `hygiene.py` names
      folders missing an `index.md`; this finds those missing the
      `CLAUDE.md`:
      ```
      cd <vault> && <python> -c "import os;[print('missing waypoint:',d) for d,_,f in os.walk('.') if 'index.md' in f and 'CLAUDE.md' not in f]"
      ```
- [ ] `<vault>/Home.md` names their real first project (`company`: their
      real first process) in the `right-now` block, not the template
      placeholder line
- [ ] `<vault>/Home.md` has a real entry in the `next-deadlines` block
      (or the explicit "no dates yet" line plus the open question from 5a)
- [ ] all four marker pairs survived editing and translation — this must
      print `8`:
      ```
      <python> -c "import re;print(len(re.findall(r'<!-- /?block:[a-z-]+ +-->', open('<vault>/Home.md', encoding='utf-8-sig').read())))"
      ```
- [ ] `<python> <vault>/.tools/search.py test` runs without error, and
      `ls <vault>/.tools/` shows all seven scripts — `autoreview.py`,
      `exam.py`, `harvest.py`, `hygiene.py`, `people.py`, `search.py`,
      `transcribe.py` — plus `INTERVIEW.md` and `hooks/` (`company`
      also: `progress.py` and the `COWORK.md` you copied in 7b)
- [ ] `company` only: `<python> <vault>/.tools/progress.py --open` reports
      **no unfilled `<…>` fields**. A remaining `TO FILL IN` marker is
      allowed if you named it out loud and put it under Home's open
      questions; an unfilled `<…>` field is not.
- [ ] The five brain-* skills are where THIS mode puts them:
      `ls <vault>/.claude/skills/` in `company`, otherwise
      `ls ~/.claude/skills/`; with two brains also
      `ls ~/.claude-work/skills/`
- [ ] `grep -n "Brain vault:"` in the file Step 6 wrote to
      (`~/.claude/CLAUDE.md`, or `~/.claude-work/CLAUDE.md` for a second
      brain) shows the block with the REAL path — not `<vault>`, and not
      `~/Brain` unless that is the real path. Do NOT grep for the word
      "Brain"; it matches unrelated lines. **`company`: skip this check;**
      there is no such line anywhere.
- [ ] `cd <vault> && git log --oneline` shows the setup commit
- [ ] `company` only: every note carries the company frontmatter. A note
      without `owner:`, `status:`, `audience:` or `confidentiality:`
      shows under `hygiene.py`'s **frontmatter gaps**, which must be `0`.
      That count also passes when `{{MODE}}` was never replaced, so
      confirm first that the `mode:` line says `company`.
- [ ] No setup placeholders outside the templates and tooling: the
      command below must print nothing. It skips `_templates/`,
      `40-decisions/_template.md`, `.tools/` and `.claude/` (in `company`
      the skills there carry `{{DATE}}` and `{{NAME}}` by design). Never
      "fix" a token inside those: editing `.tools/INTERVIEW.md`, a
      template or a skill breaks it. On the
      ADOPT path, a self page, `Deadlines.md` or `CLAUDE.md` that came
      fresh from the template still needs Step 5e's `{{LANGUAGE}}` and
      `{{DATE}}`.

The placeholder check. Run the block flush left: a `<<'PY'` heredoc
whose closing `PY` is indented never terminates.

```bash
cd <vault> && <python> - <<'PY'
import pathlib, re
SKIP = {"_templates", ".tools", ".git", ".obsidian", ".claude"}
token = re.compile(r"\{\{(NAME|LANGUAGE|DATE|MODE|COMPANY)\}\}")
for p in sorted(pathlib.Path(".").rglob("*.md")):
    if SKIP & set(p.parts) or p.name == "_template.md":
        continue
    for hit in sorted(set(token.findall(p.read_text(encoding="utf-8-sig",
                                                    errors="ignore")))):
        print(f"{p}: {{{{{hit}}}}}")
PY
```

Something failed mid-setup and can't be fixed? A FRESH install may be
removed (`rm -rf <vault>`; PowerShell:
`Remove-Item -Recurse -Force <vault>`) and restarted; say so rather than
leave a half-built vault. Never on an adopted vault: there that command
deletes their own notes.

Hand over with a 30-second demo of the five verbs, one line each:
**capture** (dump a thought) · **ingest** (drop a PDF into raw/) ·
**ask** ("what does my brain know about …") · **review** (weekly,
~10 min) · **research** ("research my brain" — fills open questions with
sourced facts). Two brains: add that `claude` opens the private one and
`workbrain` the work one. `company`: also say the sentences from 3a
(`cd <vault> && teambrain`), 3d (`00-inbox/suggestions/`) and 5b (the
SOP list), and send `COWORK.md` (7b).

Close with: "Ask me to add a module, rename an area, or change the
language — the structure grows with you." Optionally mention (don't set
it up unasked): "I can also schedule the weekly review to run itself —
ask me any time; it writes what it did to
`<vault>/.tools/logs/autoreview-YYYY-MM-DD.log`, and the auto-review
entry in TROUBLESHOOTING.md has the usage-cost trade-offs first." If they
say yes later: `<python> <vault>/.tools/autoreview.py install` (it refuses
a company vault unless the person confirms with `--force`).

## Updating a vault built with an older kit version

Never rebuild; update in place. An update replaces only kit
infrastructure (skills, tools, dashboard, waypoints, rules) and renames
frontmatter KEYS, never note content.

1. **Fresh clone** of this repo (if `git pull` on an old clone errors,
   delete it and re-clone). `grep "Kit version" <vault>/CLAUDE.md` shows
   the version you upgrade from (no marker: pre-1.0). Afterwards set the
   marker to this clone's version from `.claude-plugin/plugin.json`
   (top-level `version`), never from `CHANGELOG.md`, whose top heading
   says `[Unreleased]` between releases. The marker is its own line
   directly under the intro paragraph of the vault's `CLAUDE.md`, format
   `Kit version: X.Y.Z (…)`; add it if missing.
2. **Mode:** vaults from before 1.3 have none. Ask the Step-1 question
   once and record the answer in the Step-6 block (`Mode:` line), the
   root `index.md` and the `**Vault mode:**` line of `<vault>/CLAUDE.md`
   (otherwise `hygiene.py` measures the wrong schema). A vault with
   `10-projects/` + `20-areas/` and one person's content is `personal`
   unless they say otherwise; say what you assumed. Changing mode never
   deletes folders. A new work brain is a second vault, built fresh
   (Steps 3–9). To make an existing vault `professional`, run
   `<python> assemble.py <vault> professional`; it adds the two new
   folders and their files and leaves existing files alone, so add the
   `50-processes/` and `60-contribution/` lines to their root `index.md`
   by hand.
3. **Kit files — always, whatever the version line says.** From the new
   clone, run `<python> assemble.py <vault> <mode>` (adds missing kit
   files, overwrites nothing). Then copy every `vault-template/.tools/*.py`
   (`company`: also `vault-template/modules/company/.tools/progress.py`)
   over the vault's `.tools/` copies, and the kit's `hooks/` folder over
   `<vault>/.tools/hooks/`. Replace these, never edit them.
4. **Skills:** replace the old `brain-*` folders in `~/.claude/skills/`
   with the current five from `skills/`. Personalized skills (translated,
   custom paths)? Diff first and port the new features; ask, don't
   assume.
5. **Migrate `status:` → `maturity:` (renamed in 1.3).** The old kit
   used `status: seed|growing|evergreen` for maturity; `status:` now
   means validity (`draft|stable|deprecated`). Only the KEY changes,
   never a value or a line of note text.
   - **Do not use `sed`:** `sed -i ''` is macOS-only (GNU sed reads `''`
     as the script and silently does nothing), and `$`-anchored patterns
     miss CRLF lines, so Windows-written notes are skipped while the
     command reports success. Run this block **flush left** (an indented
     `PY` terminator never ends the heredoc):

```bash
cd <vault> && <python> - <<'PY'
import pathlib, re
old = re.compile(r"(?m)^status:[ \t]*(seed|growing|evergreen)[ \t]*(\r?)$")
front = re.compile(r"\A---[ \t]*\r?\n.*?^---[ \t]*\r?$", re.S | re.M)
changed, skipped = [], []
for p in sorted(pathlib.Path(".").rglob("*.md")):
    if ".git" in p.parts:
        continue
    raw = p.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        skipped.append(p); continue
    fm = front.match(text)          # the leading --- … --- block only
    if not fm:
        continue                    # no frontmatter: nothing to rename
    new = old.sub(r"maturity: \1\2", fm.group()) + text[fm.end():]
    if new != text:
        bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
        p.write_bytes(bom + new.encode("utf-8"))   # keeps CRLF and the BOM
        changed.append(p)
print(f"{len(changed)} notes migrated")
for p in changed: print("  ", p)
for p in skipped: print("   NOT UTF-8, left alone:", p)
PY
```

     It renames that key only inside each note's leading `---` … `---`
     frontmatter. `status: draft|stable|deprecated` and a `status: seed`
     in the body or a code block stay as they are; line endings and a
     byte-order mark survive, so the diff is one line per note.
   - Then `git diff --stat` and commit this alone
     (`git commit -m "migrate status → maturity"`), so it can be reverted
     on its own. Files listed as NOT UTF-8: see the `portability` rubric
     of `hygiene.py`.
   - A `status:` with any OTHER value (`draft`, `stable`, `deprecated`,
     or their own): leave it. List anything unclear and ask; never guess.
   - Tell them in one sentence: maturity ("how far is this note?") and
     validity ("is this still true?") are two questions that used to
     share one field.
6. **Backfill the waypoints (new in 1.3):** copy the `index.md`/`CLAUDE.md`
   pairs their mode ships (`vault-template/`, plus the overlays for
   `professional`/`company`), rewrite each `index.md`'s "Entry points"
   from the folder's real notes (never a full listing), and set the
   `generated:` marker. An `index.md` they wrote themselves is updated,
   never overwritten wholesale.
7. **Vault additions, never content changes:**
   - Add the four `<!-- block:… -->` marker pairs (5e.3) to `Home.md`
     around their existing four blocks. Never paste the English template
     over a translated Home; read `{{LANGUAGE}}`'s value from the vault
     `CLAUDE.md` and keep their language.
   - An old `Start here.md`? Fold its links into Home, update backlinks
     to it, then remove it.
   - Refresh `.tools/` (`search.py`, `hygiene.py`; the weekly review's
     hygiene step depends on `hygiene.py`, new in 1.3) and the interview
     script (3f).
   - Refresh the whole kit-owned vault `CLAUDE.md` from the current
     template, not just the Commands section, keeping their
     `{{LANGUAGE}}`/`{{MODE}}` values and personal edits (diff first, ask
     when unsure).
8. **Since 1.2.0 the skills follow the `Brain vault:` line** in the global
   rules. Make sure the block has one with their real vault path, plus
   the `Mode:` and `Human:` lines from Step 6.
9. Re-run the Step-9 checklist, then `git commit -m "kit update"`.
