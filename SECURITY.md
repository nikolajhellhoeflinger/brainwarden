# Security

Brainwarden is a local-only kit: Markdown files, five Claude Code skills
and seven Python scripts in every vault's `.tools/` (`autoreview.py`,
`exam.py`, `harvest.py`, `hygiene.py`, `people.py`, `search.py`,
`transcribe.py`), `progress.py` additionally in a company one, plus three
OPT-IN hooks (`capture_check.py`, `session_queue.py`,
`project_context.py`) that are copied
into `<vault>/.tools/hooks/` but never run until you add an entry to your
own `settings.json` yourself. There is no server and no telemetry. The
tools open no network connection except two: before an unattended review
`autoreview.py` checks that https://api.anthropic.com/ is reachable (and
then starts the `claude` CLI), and a speech engine downloads its model the
first time `transcribe.py` uses it. Besides your vault it writes only your
skills folder (`~/.claude/skills/`), one opt-in block in
`~/.claude/CLAUDE.md` and — only if you opt in — the scheduler entry
`autoreview.py install` creates (LaunchAgent / Windows task / systemd
timer) and the hooks' state files under `<config>/state/brainwarden-*`.
Run a second brain alongside the first and it adds
one more vault folder, one more config directory (`~/.claude-work`; for
a company vault `~/.claude-<company-slug>`, which keeps that vault's
session transcripts) and one alias line in your shell profile
(`workbrain` / `teambrain`), nothing else.

Things worth knowing:

- **The setup asks before every boundary:** touching `~/.claude/CLAUDE.md`,
  scanning your computer during the interview (explicit consent question,
  scope reported, veto honored), and anything involving an existing vault.
- **The scripts and the skills never leave your machine.** What Claude
  itself sends to Anthropic is governed by your Claude Code settings, not
  by this kit.
- **Everything is reversible:** the vault is Git-versioned from the first
  commit, and [TROUBLESHOOTING.md](TROUBLESHOOTING.md) documents the full
  uninstall — `autoreview.py uninstall` first if you scheduled the review,
  then three deletions for one brain, plus the second vault,
  its config directory and its shell alias if you set one up.

## Reporting a vulnerability

Found something anyway? Please open a
[GitHub issue](https://github.com/nikolajhellhoeflinger/brainwarden/issues)
— or use GitHub's private vulnerability reporting on this repository if
it shouldn't be public.
