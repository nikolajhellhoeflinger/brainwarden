---
type: knowledge
title: About this copy
created: {{DATE}}
tags: [meta]
owner: knowledge-owner
status: stable
audience: [all]
confidentiality: internal
review_due: {{DATE}}   # setup: today + 12 months — NOT today, or this page expires tomorrow
---

<!-- kit-page: copy-date -->
# About this copy

**This copy is from: {{DATE}}**

A folder, unlike a web page, ages separately on every machine it sits
on. This date is how you tell.

## For everyone: is your copy still fresh?

Compare the date above with today.

- **Less than four weeks old:** fine.
- **Older:** get a new one. Say to Claude:

  > **Is my copy of the company vault still current? If not, fetch the
  > latest one.**

  Claude checks and updates it when a pull path is set up. If none is,
  it tells you who to ask.

**Your own notes are safe.** `00-inbox/` and your drafts in
`00-inbox/suggestions/` live only on your machine and are not
overwritten. Submit the ones that are ready before you update.

**"Submit" needs a real route, and only your company can name it.** A
file in your own copy is invisible to everyone else until something
carries it back. Whoever set this vault up fills the marker below with
the actual route — the channel you would use for anything else (a shared
folder, a mail address, "drop it in the office"), not a new tool. Until
then, write your suggestions anyway and tell the person named under "Who
may release content" in [About this vault.md](About%20this%20vault.md)
that they exist.

> TO FILL IN (knowledge owner): Where does a finished suggestion go so
> that someone else sees it? Replace this line with the actual route.

## For whoever maintains the vault: how a new copy happens

1. Work the changes into the main copy and release them (`status: stable`
   plus `verified:`).
2. **Raise the date at the top of this file** — without it nobody can
   tell there is anything new. The weekly review (`brain-review`,
   company mode) prompts this step and the next; nothing else automates
   them.
3. Distribute: either everyone pulls from the shared remote, or you send
   a dated package.

> TO FILL IN (IT / knowledge owner): How is this actually distributed —
> shared access to the Git remote, or a ZIP by mail? And who sends it?
> Replace this line once it is decided.

**Distributing through Git with more than one committer?** Two people
editing the same note on the same day is a merge conflict. Keep one
writer: only the maintainer's copy is written to; everyone else's is
read-only, and their contributions travel as files in
`00-inbox/suggestions/`, never as commits (the release step in
[About this vault.md](About%20this%20vault.md) assumes this). Several
writers need a Git workflow (branches, pull requests), which this kit
does not teach.

A stale note looks exactly like a current one; this date is the only
thing that tells them apart.

## What changed recently

- **{{DATE}}** — first version.

<!-- One line per release, newest at the top: what changed that somebody
     would care about. Not every correction individually. -->
