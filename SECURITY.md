# Security

Brainwarden is local-only: no server, no telemetry. It is Markdown
files, five Claude Code skills and seven Python scripts in every vault's
`.tools/` (`autoreview.py`, `exam.py`, `harvest.py`, `hygiene.py`,
`people.py`, `search.py`, `transcribe.py`; a company vault also has
`progress.py`). Three OPT-IN hooks (`capture_check.py`,
`session_queue.py`, `project_context.py`) are copied into
`<vault>/.tools/hooks/` but never run until you add an entry to your own
`settings.json`.

**Network.** The tools open only two connections: before an unattended
review, `autoreview.py` checks that https://api.anthropic.com/ is
reachable (then starts the `claude` CLI), and a speech engine downloads
its model the first time `transcribe.py` uses it. The scripts and the
skills never leave your machine. What Claude itself sends to Anthropic
is governed by your Claude Code settings, not by this kit.

**Written outside your vault:**
- your skills folder, `~/.claude/skills/`;
- one opt-in block in `~/.claude/CLAUDE.md`;
- only if you opt in: the scheduler entry `autoreview.py install`
  creates (LaunchAgent / Windows task / systemd timer) and the hooks'
  state files under `<config>/state/brainwarden-*`;
- with a second brain: one more vault folder, one more config directory
  (`~/.claude-work`; for a company vault `~/.claude-<company-slug>`,
  which keeps that vault's session transcripts) and one alias line in
  your shell profile (`workbrain` / `teambrain`).

Nothing else.

**Consent.** The setup asks before every boundary: touching
`~/.claude/CLAUDE.md`, scanning your computer during the interview
(explicit consent question, scope reported, veto honored), and anything
involving an existing vault.

**Reversal.** The vault is Git-versioned from the first commit.
[TROUBLESHOOTING.md](TROUBLESHOOTING.md) documents the full uninstall:
`autoreview.py uninstall` first if you scheduled the review, then three
deletions for one brain, plus the second vault, its config directory and
its shell alias if you set one up.

## Reporting a vulnerability

Open a
[GitHub issue](https://github.com/nikolajhellhoeflinger/brainwarden/issues),
or use GitHub's private vulnerability reporting on this repository if it
should not be public.
