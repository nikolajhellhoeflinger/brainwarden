# Brain — shared company knowledge vault

One folder, two windows: an Obsidian vault AND a Claude Code working
directory on the same Markdown files. Several people read it, few people
release into it.

Kit version: 1.3.0 (brainwarden — updates read this line to know what
they're upgrading from, and set it to the new version afterwards)

**Vault language: {{LANGUAGE}}**. Write all notes, titles and links in
this language. Folder and kit page names may be translated too: the
tools find the inbox, decisions and archive by NUMBER (`00-`, `40-`,
`90-`) and a kit page by its `<!-- kit-page -->` marker. Only
`CLAUDE.md`, `index.md` and `Home.md` keep their names (loaded by name).

**Vault mode: company**. A SHARED vault: how the company works, not
what one person is up to. No projects, no areas, no dossiers on
colleagues; `index.md` in this folder is the map of THIS vault.

## Navigation: read the signpost before you write
Every folder has an `index.md` (what belongs there, what does NOT, the
entry points) as the signpost for ANY agent; the two-line `CLAUDE.md`
beside it loads it for Claude.
- Landed in a folder via search or glob? Read its `index.md` FIRST.
- Created a note others should start from? Add it to that `index.md`
  under "Entry points" and bump its `generated:` marker.
- Links inside an `index.md` are **real relative paths**, never
  `[[wikilinks]]` (an agent cannot resolve a link without a path). In
  normal notes `[[wikilinks]]` stay the rule.
- An `index.md` lists only the ways in, never every file.

## Folder map
| Folder | Contains | Rule of thumb |
|---|---|---|
| `00-inbox/` | Raw captures, one file per thought | zero after each review |
| `00-inbox/suggestions/` | Contributions that are NOT company truth yet | released, or dropped |
| `30-knowledge/` | Shared knowledge: terms, facts, how-things-work | "what should everyone be able to look up?" |
| `40-decisions/` | Decision records (`YYYY-MM-DD-slug.md`) | append-only |
| `50-processes/` | Procedures: how we actually do things (SOPs) | "how is this done here?" |
| `60-roles/` | Role descriptions: tasks, responsibility, cover | roles, never people |
| `70-onboarding/` | First hour / first week / first 30 days | "what does a new person need?" |
| `80-partners/` | Suppliers, service providers, contacts | organisations, not persons |
| `90-archive/` | Retired items, kept for the record | cold storage |

**No `10-projects/`, no `20-areas/`, no `30-knowledge/people/`**, and no
free number gaps (50–80 are taken), so no user modules. A person's own
projects belong in their own private vault.

**Core sorting principle:** file by the QUESTION it answers, not by who
wrote it. Findability comes from `index.md`, `[[links]]`, tags and
search, not folder depth.

## Note schema (machine-readable)
Required on every note OUTSIDE the inbox:
```yaml
---
type: knowledge | source | decision | sop | role | partner
title: <human readable>
created: YYYY-MM-DD
tags: [kebab-case, lowercase, few]
owner: <role that answers for this content>
status: draft | stable | deprecated
audience: [<role>, <role>]        # or [all]
confidentiality: internal | restricted
review_due: YYYY-MM-DD
---
```
Optional. Add a field the moment it applies, never "just because":
```yaml
maturity: seed | growing | evergreen   # knowledge notes: how worked out is it?
source: <URL/book/person>              # one external source
sources: [{resource: <uri>, title: <str>}]      # several sources
stale_after: YYYY-MM-DD                 # from this date on, distrust it
verified: {by: human:<name>, at: YYYY-MM-DD}     # a human confirmed it
generated: {by: <agent>/<model>, at: YYYY-MM-DD} # an AI produced it
version: <n>                            # SOPs: counts up on every release
valid_from: YYYY-MM-DD                  # SOPs: since when this version applies
```

**`verified` vs `generated`: the most important distinction here.**
`verified` = a human read it and said "yes, that is right". `generated`
= a machine wrote it and nobody has checked it. **Content is company
truth only with `status: stable` AND a filled `verified:`;** everything
else is a proposal, however confident it reads. Never set `verified:`
yourself (it belongs to whoever may release): what you write carries
`generated:` and stays `draft` until a human replaces it.

**The two scales above are this vault's authority:** `hygiene.py`,
`search.py --stats` and `progress.py` read the `maturity:` and
`status:` lines from THIS file. Translate their values
(`status: entwurf | gültig | überholt`) here AND in the notes, never
only in the notes, and keep the order: `maturity` runs unfinished →
worked out, `status` draft → released → retired. Otherwise the checks
silently stop matching.

**`maturity` vs `status`.** `maturity` (knowledge notes): how worked
out? `seed` · `growing` · `evergreen`. `status`: does it still hold?
A note can be `evergreen` and `deprecated` at once. The old spelling
`status: seed|growing|evergreen` is now `maturity:`; rename it.

**`confidentiality:` is a LABEL, not access control.** Everyone who can
open this folder can read every file; only a separate vault with its
own access rights separates. Never tell anyone a note is protected
because of this field.

**Superseding: write it on BOTH files, as plain text,** so an agent
landing in the OLD file finds the pointer.
- New file: a `## Status` section with
  `Supersedes [40-decisions/2026-05-10-old.md](40-decisions/2026-05-10-old.md)`.
- Old file: its `## Status` body is REPLACED by
  `Superseded by [<path>](<path>)` (append the section if it has none),
  and its frontmatter gets `status: deprecated`. Never leave an "in
  force" line above it. Real relative paths, rest of the file untouched.

- Inbox captures need NO frontmatter (zero friction); it is added at
  review time.
- File names: descriptive, kebab-case; date-prefixed only for episodic notes.

## Thinking rules
- **Atomic:** one idea per note; one role = one note (`60-roles/`).
- **Own words:** processing means paraphrasing. Copying is collecting,
  not understanding.
- **Processing duty:** the inbox goes to ZERO at every weekly review.
  File it or delete it, never "later".
- **Success metric is output:** fewer questions asked twice, faster
  onboarding, procedures someone can actually follow. Never note count.
- **Link rule:** add `[[links]]` only when note A truly changes how you
  read note B.
- **Never invent a figure, a condition, a price or a deadline**:
  somebody will act on it. Not in a note and not in a source → "I don't
  know, ask <owner>".
- Maps of content only after ~150 notes; no new top-level folders without
  a deliberate decision.

## Note anatomy (target depth per type)
- **Procedure / SOP** (`50-processes/`): purpose in one sentence → scope
  (who and when) → roles involved → numbered steps, one action each →
  exceptions and what to do when they hit → revision history. A
  stand-in can follow it without asking.
- **Role note** (`60-roles/`): tasks, what this role decides alone, what
  it must escalate, who covers when it is away, what knowledge it
  needs. Describes the ROLE; it stays when the holder changes.
- **Partner note** (`80-partners/`): what they deliver, how to reach
  them, where the terms are filed, experience worth knowing. No
  judgements about named individuals.
- **Knowledge note** (`30-knowledge/`, target `evergreen`): the idea in
  your own words → the evidence (`source:` + where in it) → one concrete
  case, number or example → a limit or counter-position where one exists
  → the `[[links]]`. Aim ~100–400 words.
- **Decision** (`40-decisions/`): terse and append-only. Context → what
  was decided → why → what follows from it.
- **Onboarding** (`70-onboarding/`): a path, not a pile. First hour,
  first week, first 30 days, each step pointing at a real note.
- **Principle:** depth comes from revision rounds (the review), not the
  first draft.

## The red line: Claude drafts, humans release
- Add researched facts only WITH a source and only marked as research
  (`source:` or an inline "(researched YYYY-MM-DD)").
- Never rewrite a released note (`status: stable` + `verified:`) on your
  own. Propose the change in `00-inbox/suggestions/`, name what would
  change; the owner decides.
- Never write anything about a named employee beyond "currently holds
  role X": no performance, conduct, health, salary (personnel data in
  a shared vault is a legal problem).
- No usage tracking: who searched for what, and when, is not recorded
  (in Austria and Germany usually subject to works-council
  co-determination).

## Instructions for Claude
- Retrieval: ALWAYS run `python3 .tools/search.py <terms>` from this
  folder first, then read only the hits, never the whole vault
  (`--stats` for the numbers). Search before creating a note too:
  extend instead of duplicating.
- **Answer with the source:** cite the note behind every statement,
  with its `status:`. If the only hit is `draft` or a suggestion, say so
  before answering. "I don't know" is a correct answer here.
- `Home.md` is the HUMAN's dashboard. Address a block by its
  `<!-- block:… -->` marker, never by heading text, and replace only
  what sits between a marker pair. `index.md` is the agents'
  equivalent: Home is prose, `index.md` is paths.
- Incoming sources: files in `00-inbox/raw/` → skill `brain-ingest`.
- Templates: SOP → `_templates/sop-note.md` · role → `role-note.md` ·
  partner → `partner-note.md` · knowledge → `knowledge-note.md` ·
  source → `source-note.md` · onboarding → `onboarding-plan.md` ·
  decision → `40-decisions/_template.md`. Fill the DATE/NAME
  placeholders with real values; the template files keep their tokens
  forever. Never rewrite a decision record; append.
- Inside `30-knowledge/` at most ONE level of subfolders; elsewhere no
  new subfolder without a reason.
- Review hygiene: `python3 .tools/hygiene.py` reports orphans, dead
  links, near-empty notes, notes no signpost reaches, folders without an
  `index.md`, frontmatter gaps, expired `stale_after`/`review_due`,
  one-sided supersede chains, unclosed code fences and portability
  problems (encodings, file names another system cannot hold).
- Retired procedure / former partner → `90-archive/`, and remove it
  from the source folder's `index.md` entry points.

## Sync
- Versioning: local Git. One maintainer writes; everyone else reads a
  copy (Cowork, Obsidian, any editor) or a read-only clone of a private
  Git remote, and contributes through `00-inbox/suggestions/`. No cloud
  sync folder (corruption risk with Git, and no review step before
  content becomes truth).

## Commands
- **brain-capture**: frictionless thought → inbox (from any session)
- **brain-ingest**: source from raw/ → triaged notes
- **brain-ask**: answer questions from the vault, with cited notes
- **brain-review**: weekly inbox to zero, contradiction check,
  connections, hygiene, refresh Home, git commit
- **brain-research**: fill open questions and thin notes with verified,
  sourced facts
