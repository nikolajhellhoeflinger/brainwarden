# Contributing

1. **Stay lean.** Every addition must make the start easier, not
   heavier. New mandatory folders, plugins or services need a strong
   case.
2. **Claude does the work.** Anything a human would have to do belongs
   in `SETUP-FOR-CLAUDE.md` for Claude to do. Test changes by running the
   setup once from scratch.
3. **No personal data.** Templates and examples stay generic
   ({{NAME}} placeholders). PRs with real names or addresses are
   rejected.

## Process
- **Bug or idea:** an issue (English preferred), short and concrete.
- **PR:** fork → branch → PR with 2–3 sentences: what, why, how tested.

## Style
- Markdown, about 80 characters per line, no HTML tricks.
- Examples follow `examples/` (frontmatter + "Related:" links, marked as
  demo content).

## Before you open a pull request

Run `./check.sh`. It assembles all three vault modes from the template
and checks dead links, orphans, missing signposts, dashboard markers and
version agreement, in seconds and without an account. GitHub runs the
same script on every push and pull request on macOS, Linux and Windows
(`.github/workflows/check.yml`). There are no CI-only checks: whatever
fails there, `./check.sh` reproduces locally.
