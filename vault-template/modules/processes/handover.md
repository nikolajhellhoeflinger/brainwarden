---
type: knowledge
title: Handover view
created: {{DATE}}
tags: [handover, meta]
ownership: private
---

# Handover view

Not a folder — a query, so it is current on the day you need it.

## What belongs to the company

```
python3 .tools/search.py "ownership: company" --k 40
```

Everything that matches leaves with the job. In Germany and Austria
that includes your own notes on customers and projects, copies included;
only genuinely private records are exempt (§ 667 BGB analog; BAG
14.12.2011 – 10 AZR 283/10).

## What is handover-relevant

```
python3 .tools/search.py "handover_relevant: true" --k 40
```

Runbooks above all: what only you know how to run. Write down the tacit
part — why it is done this way, who to call when it breaks, which
workaround is load-bearing; that is what gets lost.

## What stays yours

`ownership: private` — your contribution log, your learning notes, your
own thinking. After leaving you may use what is in your head; keeping
company material is a different matter.

## Monthly, not weekly

One question: did a new responsibility arrive that has no runbook yet?
