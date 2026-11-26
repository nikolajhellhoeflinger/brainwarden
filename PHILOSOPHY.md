# Why this kit works (and why second brains usually die)

Most personal knowledge systems are abandoned within months, for four
recurring reasons. The kit is built against each of them.

## The four causes of death

1. **Capture friction.** If saving a thought takes effort, people stop.
   The kit has one inbox, one phrase ("capture: …") and no required
   metadata. Claude adds structure later.
2. **Over-engineering.** An elaborate taxonomy soon costs more to
   maintain than it returns. Tiago Forte: *"if your organizational
   system is as complex as your life, maintaining it will rob you of the
   time and energy you need to live that life."* The kit has six flat
   folders in a private brain, eight at most in a company one, files by
   **actionability** (which project or area needs this now?) and leaves
   the sorting to the weekly review.
3. **Collecting without using.** Notes go in and nothing comes out. The
   kit measures **output**: study sheets, drafts, plans, decisions.
   `brain-ask` makes taking out as easy as putting in, and the weekly
   review ends by offering to build your next piece of work from what it
   just filed.
4. **All setup, no payoff.** Beginners tune taxonomies, meet an empty
   vault and leave. The setup asks who the brain is for and four short
   questions, then writes your project, your deadlines and a filled
   `Home` dashboard, minutes in. After weeks away, the review catches up
   in batches.

## Built for agents first

An AI maintains the vault, in sessions that start cold and land in the
middle of your notes through a search. Each design choice answers one
question: **can an agent that lands here keep going without guessing?**

- **Signposts.** Search returns files, not orientation. Every folder
  with notes has an `index.md` of about 25 lines (purpose, what does not
  belong, where to start) that any tool can open, and a two-line
  `CLAUDE.md` that loads it into Claude's context. It lists entry
  points, never every file.
- **Real paths in signposts.** A `[[wikilink]]` resolves only inside
  Obsidian; an agent reading the raw file gets a name without a
  location. Notes keep wikilinks for the graph, signposts use relative
  paths.
- **Validity is a field.** A model reads "we used to do it that way" as
  an instruction. So `maturity:` says how worked out a note is and
  `status:` whether it still holds; a note can be `evergreen` and
  `deprecated` at once. `verified:` (a human confirmed it) is kept apart
  from `generated:` (a machine drafted it), and Claude never sets
  `verified:` on its own work.
- **Only the Markdown counts.** No database, no index, no sidecar file.
  When a note replaces another, both bodies say so, because an agent in
  the old file reads only that file. `.tools/hygiene.py` reports
  one-sided chains, orphans and dead links.

## Structural choices

- **PARA-inspired.** Projects, Areas and Archive come from PARA
  (fortelabs.com/blog/para). `30-knowledge` adds a Zettelkasten-style
  space; `40-decisions` is an append-only log, because decisions are the
  most valuable notes a person has.
- **Flat.** Links, tags and `.tools/search.py` do the finding. Search
  is deterministic, not embedding-based: the same query gives the same
  hits and nothing is sent anywhere. It matches inside words, which
  German compounds need.
- **Three shapes, one core.** Private, work and company brains share one
  core template and the five skills, with overlays on top. Two purposes
  never share a vault; a folder cannot keep them apart. A shared vault
  holds roles, not person notes: a role outlasts every hire, and nobody
  is assessed.
- **Numbered with gaps.** `00 10 20 30 40 … 90` keeps folders sorted and
  leaves 50–80 free, the useful half of Johnny Decimal. A private brain
  fills them as it likes (journal, media, health, money …); a work brain
  uses `50-processes/` and `60-contribution/`; a company vault uses all
  four for processes, roles, onboarding and partners.
- **The interview is a starting point.** Reviews may propose new
  structure as your life changes.
- **AI as maintainer, not author.** Claude files, links, prunes and
  reminds; the notes stay in your words ("The red line" in the vault's
  `CLAUDE.md`).
- **Every change is visible.** Every filing is reported, every change is
  a Git commit, and deleting is a normal operation.

## Why not a folder of Word files on the server?

With one writer, fewer than about fifty documents and clear file names,
a shared folder is enough and this kit is overkill. Beyond that, four
things break it:

- **A Word file cannot say whether it still applies.** `status: stable`
  with a filled `verified:` says who confirmed it and when; `review_due`
  and `stale_after` say when to stop trusting it, and `hygiene.py` lists
  what has expired.
- **People leave.** A folder named after a colleague dies with their
  departure; a note in `60-roles/` survives it.
- **File-server search misses compounds.** Windows search for `Vertrag`
  does not find `Rahmenvertrag`; `search.py` does.
- **Nobody tidies a shared folder**, which is why company wikis rot.
  Here filing, linking, deadlines and the weekly cleanup are the agent's
  job; the human only says what happened.

A wiki remains better at real access rights and at reaching people who
never clone anything. Knowledge that part of the team must not see needs
a second vault.

## Why a vault, and not just chats?

Chats disappear into scroll history. The vault is the lasting record the
AI reads and writes, so each new session starts with your context, and
the weekly review surfaces what you forgot to ask.

## Further reading
- Tiago Forte, *The PARA Method*: https://fortelabs.com/blog/para/
- Nick Milo, Linking Your Thinking: https://www.linkingyourthinking.com/
- Johnny Decimal: https://johnnydecimal.com/
