---
type: decision
title: <title>
created: {{DATE}}
tags: []
owner: <role that made the call — the ROLE, not only the person>
status: stable
audience: [all]
confidentiality: internal
review_due: <YYYY-MM-DD — at the latest one year out>
verified:
---

# Decision: <title>

**Date:** {{DATE}} · **Decided by:** <role from 60-roles/> ({{NAME}})

## Context
<Why did this decision come up? 2–4 sentences.>

## Decision
<What was decided — concrete, with numbers/names.>

## Alternatives (rejected)
- <option> — <why not>

## Status
In force.

<!-- Company mode: `owner`, `audience`, `confidentiality` and `review_due`
     are required. `owner:` is the ROLE that made the call (a person's
     name loses its owner when they leave). `status: stable` is correct
     from the start, but the record is company truth only once a human
     fills `verified:`. No `ownership:` field in a shared vault.

     When this record is replaced, this section is REWRITTEN, not extended:
     the line above becomes `Superseded by [<path>](<path>)` and the
     frontmatter gets `status: deprecated`. Never two `## Status`
     sections — an agent greps the first and believes it. The new record
     gets its own `## Status` with
     `Supersedes [40-decisions/<old-file>.md](<old-file>.md)`.
     Rewriting THIS section is the single exception to append-only. -->
