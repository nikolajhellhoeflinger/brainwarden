---
name: brain-review
description: Weekly review of the Brain. Inbox to zero, correct the record, fix what hygiene.py finds, deepen thin notes, refresh Home, and close by naming what the brain can produce next. Use when the user says "brain review", "clean up my brain", "what's in the inbox", ideally on a fixed weekday.
---

# Brain review (5–10 minutes, weekly)

Steps 0–9 run every week; "Not every week" has its own triggers. Missed
weeks are normal: catch up in batches, never scold.

**Conventions:** `<vault>` = the vault this session runs in: the folder
it started in, or one above it, whose `CLAUDE.md` names a vault mode
(`personal`/`professional`/`company`) and that holds the kit's
`.tools/`. Otherwise the path on the `Brain vault:` line in your global
rules. Only when neither exists, `~/Brain`. `python3` = your working
python command (on most Windows machines `py -3`; the global rules name
it).

## Every week
0. **Load the vault rules:** `<vault>/CLAUDE.md` (schema, note anatomy,
   language, mode, red line) and `<vault>/index.md` if present. No
   `CLAUDE.md` → wrong path or unfinished setup: say so and stop.
1. **Inbox to ZERO** (hard rule): every file DIRECTLY in
   `<vault>/00-inbox/`. Never the kit's `Inbox rule.md`, `index.md`,
   `CLAUDE.md`, never `raw/` (`brain-ingest`'s queue), never a runner
   notice (`!`-prefixed files, `Set aside.md`, the hidden `.set-aside/`).
   One file may take SEVERAL exits (a decision + two dates + a
   question = four).
   - **(a) a note:** paraphrase it (frontmatter, vault language, the
     matching `_templates/` file, real placeholder values); file by
     ACTIONABILITY: project → `10-projects/` · area → `20-areas/` ·
     **settled question → `40-decisions/YYYY-MM-DD-slug.md`**
     (append-only) · keeper knowledge → `30-knowledge/` · person →
     `30-knowledge/people/` · **recurring task → `50-processes/`** ·
     **something you did, with evidence → `60-contribution/`** (last two:
     work brains only). Person notes, in EVERY mode: facts only (role,
     agreements, current work), never a judgement of character, mood or
     motive. Test: *could I show this to them if they asked?* Meeting
     notes file with what they are ABOUT.
   - **(b) a date:** a line in `Deadlines.md` (date first) + one in the
     log of its project or area, if it has one (a dentist appointment
     needs only `Deadlines.md`). Then delete the file; no knowledge note
     for a date.
   - **(c) deleted:** say so. A TASK ("call the insurer") goes to
     Home's `block:open-questions` **prefixed `TODO:`** (that block also
     holds open questions) or to its project's log; then delete the file.
   - **dedup:** `python3 <vault>/.tools/search.py <name/topic>` before
     writing; extend, never twin. **Triage:** reference material
     (links, clippings) = one note, tags, done; atomize only what the
     person builds on.

   **Empty-file rule, wins everywhere:** no body (0 bytes, whitespace,
   title line only) → DELETE and name it in the report; never file,
   never guess. Kit files excepted.
   **Contentless but not empty** (one word, a bare keyword, a link
   without context; the capture footer keeps these out of the empty
   rule): don't guess, don't file. Ask in one line: *"'Zettelkasten'
   from the 13th: was there something behind that?"* No answer: delete
   and say so.
   **Over ~20 files?** Batches by priority (dates → decisions → people →
   rest); report what remains, never half-process silently.
2. **Sweep the week (the guarantee):** four tracks, then compare with the
   vault.
   - **files:** `find <work folder> -type f -mtime -7 -not -path '*/.*' | head -40`.
     Work folders come from the self page (`About me.md`;
     `About this vault.md` in `company`, which has neither `About me.md`
     nor project notes), `Home.md` or project notes. Ask once, record
     them on the self page.
   - **repos, if any:** `git log --oneline --since="7 days ago"`.
   - **session queue, if it exists:**
     `python3 <vault>/.tools/harvest.py --queue` lists finished
     sessions; ask what came out of them since the last review. No
     queue → mention the SessionEnd hook ONCE (`hooks/README.md`).
   - **the human (never skip):** "what were the 3 most important things
     this week (decisions, dates, people, milestones)?" Cue recall: day
     by day · by counterpart (names in `30-knowledge/people/`,
     `60-roles/`, `80-partners/`) · by open loop (each date in
     `Deadlines.md`, each open question on `Home.md`: did it move?).
     Their answer outranks the machine tracks; the step never ends
     empty. Anything brain-worthy never captured goes to the inbox now,
     then through step 1.
3. **Correct the record: dates, then decisions.**
   - **Dates:** new → `Deadlines.md`, past ones out. **A moved date
     REPLACES its line, never appends:** find the old one
     (`python3 <vault>/.tools/search.py <old-date> <topic>`), correct
     every hit (`Deadlines.md`, the project's log, `Home.md`, any
     `index.md`), say which files you corrected.
   - **Contradictions:** hold this week's new/changed notes against
     `40-decisions/`; flag what contradicts a recorded decision
     ("clashes with [[2026-05-10-x]], decided because Y; revisit or
     comply?"). A reversal is a NEW record, written on BOTH sides: new
     file `## Status` + `Supersedes <path>`; old file's `## Status` BODY
     REPLACED by `Superseded by <path>` (append the section if missing)
     + `status: deprecated` in its frontmatter. No "in force" line above
     a supersede notice; nothing else in the old record changes.
4. **Vault state: run the tool, don't guess.**
   `python3 <vault>/.tools/hygiene.py` (orphans, dead links, near-empty,
   unreachable, missing `index.md`, frontmatter gaps, expired
   `stale_after`/`review_due`, one-sided supersede chains). Old vault
   without it: manual pass (`find <vault> -name '*.md' -size -1c`,
   spot-check this week's `[[links]]`) and report that it needs a newer
   kit. Fix what it lists; a `status:` holding a maturity value becomes
   `maturity:` (whole old vault:
   `grep -rln "^status: \(seed\|growing\|evergreen\)" <vault>`). Hand the
   human only what needs a decision:
   - **expired:** still true (push the date out, say why) or not
     (`status: deprecated`, or fix it). Never left expired.
   - **folder without `index.md`:** create one shaped like the root
     `index.md` (title · what lives here · `**Rules here:**`/`**NOT here:**`
     · `## Entry points` · trailing `<!-- generated: YYYY-MM-DD -->`)
     plus a two-line `CLAUDE.md` beside it:
     `<!-- Loaded automatically when Claude reads a file in this folder. -->`
     and `@index.md`. Report both.
   - **orphan cluster** (a folder of machine-written, link-less files:
     memory mirrors, app exports) → ONE generated map note linking every
     file, filed by actionability, linked from `Home.md`, regenerated
     every review. NEVER edit the foreign files; keep/delete/gitignore is
     the human's call.

   What the tool cannot see:
   - **signposts:** fix stale entry points you touched (a date quoted in
     an `index.md` is a second copy: correct or drop it). Add today's
     new ENTRY POINTS to each written-into folder's `index.md`: real
     relative paths, never `[[wikilinks]]`, under ~25 lines,
     `<!-- generated: -->` = today. Routine notes stay out of the index
     but must be reachable by a `[[link]]`.
   - **decay:** projects whose LOG has not moved in 30+ days. Judge by
     the newest date inside the note, never the file timestamp (this
     review just wrote the files; a fresh `git clone` dates them all
     today). `find <vault>/10-projects -name '*.md' -mtime +30` is a
     shortcut, never the whole answer. Ask ONE collected question,
     "archive to `90-archive/` or still active?". Archive beats delete
     for finished projects, delete beats archive for noise.
   - **findability:** `python3 <vault>/.tools/exam.py --record`; its first
     line goes in the report. MISSED → fix the NOTE, never the exam (put
     the searched-for words in its heading or first sentence, or link it
     from where people look). STALE → renamed note: update the path.
     "WORSE than" last time → say so first. Then propose one or two new
     questions from this week's notes, phrased as the person would ask,
     with an agent's search terms; add them only with their OK
     (`exam.py add "<question>" --terms "<terms>" --expect <path>`;
     autonomous mode: park the proposal as an open question).
5. **Deepen 2–3 notes:** the oldest or most-used `maturity: seed`/`growing`
   knowledge notes, frontier notes first (many outgoing `[[links]]`, few
   or no inbound). Grow them toward the note anatomy in the vault
   `CLAUDE.md`: missing `source:`, one concrete case or number, a limit
   or counter-position, the `[[links]]`. Research what is researchable
   (rules of `brain-research`). **What only the human can supply**
   (their reasoning, example, number): park as `open → ask: …`, add to
   Home's `block:open-questions`, LEAVE `maturity:` untouched. Never
   invent a case, number or opinion; bump `maturity:` only once the
   anatomy is met.
6. **Open loops and connections:** list 3–5 stalled things (projects
   without recent notes, `open → ask` markers), ask about them, offer
   `brain-research` for the researchable ones. Name 1–3 non-obvious
   connections between this week's notes and older ones; add a
   `[[link]]` only where it changes how a note reads.
7. **Refresh `Home.md`:** all four blocks, dropping nothing. **Address
   each block by its HTML marker, never by heading text**
   (`<!-- block:right-now -->` … `<!-- /block:right-now -->`, likewise
   `next-deadlines`, `open-questions`, `new-this-week`); rewrite only what
   sits BETWEEN a marker pair, never a line carrying `<!-- keep:… -->`.
   - **`right-now`:** active projects, one-line status each, AND the
     `Areas:` line linking every note in `20-areas/`, rebuilt from the
     folder listing every time.
   - **`next-deadlines`:** the next 3 dates from `Deadlines.md`; beside
     each date in the next 7 days that names a person
     (`python3 <vault>/.tools/people.py upcoming`), a link to their note.
   - **`open-questions`:** this review's open loops and parked questions.
   - **`new-this-week`:** the 3–5 newest or most-grown notes.
8. **The yield: end with output, not a filing report.** In order:
   - **What can the brain do now that it could not last week?** Name it
     from today's filing (a question it can answer, a draft it has
     material for), with the notes behind it. Nothing usable: say so;
     never manufacture a win.
   - **Ask "what are you working on next?"** Run
     `python3 <vault>/.tools/search.py <topic>` on the answer; lay out
     the notes, binding decisions and dates, and the gaps to fill first
     (offer `brain-research`).
   - **Offer the artifact** the material now supports (summary, draft,
     plan, checklist, study sheet); BUILD it on their go: file it with
     its project, link it from the project note, add it to that folder's
     `index.md` entry points and under its project in Home's
     `block:right-now`.
9. **Commit and report.** Check WHERE first:
   `cd <vault> && git rev-parse --show-toplevel`.
   - Prints the vault path → commit.
   - Prints a folder ABOVE the vault → **do not commit**, say so (the
     vault sits inside somebody else's repository).
   - Errors ("not a git repository") → `git init` and say versioning
     starts now (`assemble.py` alone creates no repo; only the setup
     runbook does).

   Then `git add -A && git commit -m "review YYYY-MM-DD"` and report:
   what was filed where, what was deleted, what needs their input,
   which "not every week" items ran, what the brain produces next.
   Every filing decision visible, all reversible via Git.

## Not every week
Trigger-based; say in the report which ones ran.
- **Structure check** (quarterly-ish, or when the sweep keeps producing
  material no folder fits): propose renaming or archiving an area or
  folder that no longer matches the person's life.
- **Maps of content** (past ~150 notes,
  `python3 <vault>/.tools/search.py --stats`): propose one map per
  strand, 2–3 sentences of framing each, never a bare list of links.
- **Revisit by context** (when the review ran short):
  `python3 <vault>/.tools/search.py --resurface` lists older notes linked
  to what changed this week and untouched for two months. Open ONE (no
  output: one random older note) and make one concrete improvement:
  stale, missing an obvious link, a near-twin to merge?

## Work mode (only when the vault `CLAUDE.md` names the mode `professional`)
- **Nothing stays `ownership: mixed`:** split or reclassify every mixed
  note from this week now.
- **Show-them test** on every person note you touched: role, work and
  agreements pass; character judgements and motive guesses are deleted,
  not rephrased.
- **Runbooks run this week** get a fresh `last_verified:`; past 12
  months → flag as unverified.
- **Contribution log, five minutes:** what shipped, reviewed, designed,
  documented, who you helped, what you learned; each number with its
  source on the same line. An empty week is a valid entry; never invent
  impact.

## Company mode (only when the vault `CLAUDE.md` names the mode `company`)
- **`00-inbox/suggestions/` goes to zero too** (step 1, second folder).
  One exit each: (a) the person who may release it says yes → move it to
  its folder, `status: stable`, THEY fill `verified:`; (b) needs a
  decision they cannot make today → leave it, name it in the report with
  who decides; (c) wrong or already covered → delete it, say why.
  Nothing sits unanswered through two reviews.
- People become ROLES in `60-roles/`, never personal dossiers.
- A NEW note you write goes to `00-inbox/suggestions/`; a note already
  in a folder is edited in place and drops to `status: draft`, never
  moved out. The human sets `verified: {by: human:<name>, at: YYYY-MM-DD}`,
  never you.
- Never invent an owner, a number or a field value. Missing stays
  missing.
- **Date the copy and send it** (no other recurring step does): raise
  the date at the top of `THIS-COPY.md`, add one changelog line, then
  distribute: `git push` if the vault has a remote, otherwise the
  agreed channel. Channel still an open `TO FILL IN` → say so in the
  report: nothing else in this mode matters until it is decided.
- **Report the number that matters:** `python3 <vault>/.tools/progress.py`
  shows notes carrying `verified:` first, gaps left second. Name the
  movement since last week ("2 more released"), or say plainly that
  nothing moved. Closed gaps are not progress; only a human's
  `verified:` makes a note something a colleague may act on. Put who to
  ask next (`--by-role`) in the report, never a guess.

## Autonomous mode (only when run unattended by a scheduler)
No human in the loop:
1. Delete nothing that isn't unambiguous junk; unsure → file it. The
   step-1 empty-file rule still wins (empty = delete + report).
2. Never archive without asking; list candidates as questions.
3. Route ALL questions to Home's `block:open-questions`, never to chat,
   including step 2's "3 most important things" and step 8's "what are
   you working on next".
4. Step 8 still runs: name what the brain can do now and list the
   artifact you would build, as an offer instead of building it.
5. Finish with the Home refresh and a short report as your final answer.

Started by `autoreview.py` (its prompt says it commits before and after
you): run no git. It writes your answer to
`<vault>/.tools/logs/autoreview-YYYY-MM-DD.log` (outside the notes; it
keeps the last 12) and commits the run's work itself. Started by any
other scheduler (a Desktop routine): end with the commit of step 9, as
in a normal review.
