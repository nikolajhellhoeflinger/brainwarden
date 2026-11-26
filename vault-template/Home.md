<!-- Machine anchors: each dashboard block sits between
     `<!-- block:NAME -->` and `<!-- /block:NAME -->`. Address blocks by
     MARKER, never by heading text (headings get translated). A refresh
     replaces only the lines BETWEEN a marker pair; markers, headings and
     everything below the `---` stay. A line carrying `<!-- keep:… -->`
     survives every refresh: update its content, never delete it. For
     paths rather than prose, read index.md. -->

Your brain at a glance; every path leads back here. Claude fills and
updates this page, starting during setup. (No heading: Obsidian shows
the file name as the title.)

## Right now
<!-- block:right-now -->
<!-- Claude: active projects as wikilinks with a one-line status each, e.g. "- exam-prep-biology - next: summarize chapter 3". The "Areas:" line below is the ONLY inbound link the area notes have — refresh its links, never drop the line. -->
- *(your first project appears here during setup)*
- <!-- keep:areas-line -->Areas: *(your areas appear here during setup)*
<!-- /block:right-now -->

## Next deadlines
<!-- block:next-deadlines -->
<!-- Claude: mirror the next 3 dates from Deadlines.md; the full list stays there -->
- *(none yet — every date lives in [[Deadlines]])*
<!-- /block:next-deadlines -->

## Open questions
<!-- block:open-questions -->
<!-- Claude: "open → ask later" markers and stalled loops from the last review -->
- *(fills up as the brain learns what it doesn't know)*
<!-- /block:open-questions -->

## New this week
<!-- block:new-this-week -->
<!-- Claude: the 3-5 most recently added or grown notes as wikilinks, refreshed at every review -->
- *(updated at every brain review)*
<!-- /block:new-this-week -->

---

## How to use your brain
- **Dump a thought** → tell Claude `capture: …` (lands in [[Inbox rule|00-inbox]] — no sorting, ever)
- **Feed it a source** → drop PDFs/transcripts into `00-inbox/raw/` → say `ingest`
- **Ask it something** → *"what does my brain know about …?"*
- **Once a week, fixed day** → `brain review` (~10 min — Claude does the work, you answer questions)
- Me: [[About me]] · People: `30-knowledge/people/` · Rules: [[CLAUDE|CLAUDE.md]]

*The success metric is output — texts, plans, study sheets, decisions.
Never note count.*
