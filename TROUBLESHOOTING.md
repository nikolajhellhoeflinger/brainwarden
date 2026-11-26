# FAQ & troubleshooting

On Windows, write `py -3` wherever this page says `python3`.

## Getting started

**Obsidian shows nothing.** Obsidian → "Open folder as vault" → pick
`~/Brain`. Obsidian and Claude work on the same files.

**Do I need to know Markdown?** No. Say "capture: …"; Claude adds the
structure. In Obsidian you click [[links]].

**iCloud or Dropbox?** No. Cloud sync plus Git on one folder corrupts
vaults. For your phone, use Obsidian Sync (see
[mobile](#capturing-on-the-go-mobile)).

**Can my brain be in German (or another language)?** Yes. Setup asks for
the vault language and translates the starter pages. Folder names may be
translated too: the tools find folders by number (`00-`, `40-`, `90-`).

**I already have an Obsidian vault.** Say so during setup. Claude adopts
your structure (scan, map, add only what is missing) and overwrites
nothing.

**Setup died halfway.** Delete a fresh install and start again:
`rm -rf ~/Brain` (PowerShell: `Remove-Item -Recurse -Force ~\Brain`).
Only `~/.claude/skills/` and the rules block in `~/.claude/CLAUDE.md`
changed besides, and both are safe to re-run. For an adopted vault, ask
Claude to undo its last changes via Git.

**Claude doesn't know my brain in a new session.** Test with "search my
brain for X". If nothing happens, check that the rules block exists and
names your real vault path: `grep "Brain vault:" ~/.claude/CLAUDE.md`.
Grepping for just "Brain" proves nothing; it matches unrelated lines.

## Daily use

**Inbox overflowing, or I stopped for weeks.** Say "brain review". It
processes the inbox to zero, catches up in prioritized batches (deadlines
first), sweeps what the missed weeks produced and refreshes `Home`.

**Claude filed something wrong, or I want to undo.** Every review and
ingest reports what went where. Tell Claude ("move that note", "undo the
last review") or use Git: `cd ~/Brain && git log --oneline` shows the
history, `git checkout -- <file>` restores a file.

**`Home` looks stale.** The weekly review refreshes all four blocks
(projects, deadlines, open questions, new notes); a deadline capture
updates its block at once. Still stale? Say "refresh Home".

**What are the `<!-- block:… -->` comments in `Home`?** Invisible markers
Claude uses to find each block, so headings can be in your language.
When editing `Home` yourself, never delete a marker line or a line marked
`<!-- keep:… -->` (that keeps the "Areas:" line); change its content
instead. A block stopped updating? Say "repair Home's block markers".

**What does NOT belong in the brain?** Operational knowledge of active
code projects (that goes in the repo's CLAUDE.md), and anything you call
"private".

**Canvas and Bases?** They work; the vault is plain Markdown. For Claude
to build canvases (visual maps) or bases (table views), install
Obsidian's official Claude skills for markdown/canvas/bases and ask
("build me a canvas map of my thesis project").

## Folders and fields

**A folder has no `index.md` (or no two-line `CLAUDE.md`).** Every folder
with notes needs both: `index.md` says what belongs there and where to
start, the `CLAUDE.md` loads it into Claude's context. Say *"backfill the
missing index files in my brain"*. Folders you create by hand need the
pair too. `python3 .tools/hygiene.py` (run inside the vault) lists
folders with notes but no `index.md`, notes no signpost leads to,
orphans, dead links, near-empty notes, frontmatter gaps, expired dates,
one-sided supersede chains, unclosed code fences and portability
problems.

**After the update some notes still say `status: seed`.** Maturity
(`seed`/`growing`/`evergreen`) now lives in `maturity:`; `status:` means
validity (`draft`/`stable`/`deprecated`). Say *"finish the status →
maturity migration"*. Claude lists the affected notes first, renames only
the field name (never a value or your text) and commits it separately.
Notes with `status: draft`/`stable`/`deprecated` stay untouched.

**Why do the numbers jump from 40 to 90?** 50–80 are slots for optional
modules (journal, media log, health, money …); ask Claude to add one. A
work brain uses `50-processes/` and `60-contribution/`. A company brain
uses all of 50–80 (processes, roles, onboarding, partners), so new
content goes into one of those.

**Why do my brains have different folders?** The mode. Private: projects
and areas. Work: adds `50-processes/` (recurring workflows) and
`60-contribution/` (what you actually did). Company: no projects, areas
or person notes; processes, roles, onboarding and partners instead. Each
folder's `index.md` explains it.

**Can I rename folders?** Yes, if top-level folders keep their numbers
(`00-` … `90-`): the tools find the inbox, decisions and archive by
number. Area folders already carry your words from setup. Only
`CLAUDE.md`, `index.md` and `Home.md` keep their names.

## Two brains

**One brain for private, one for work?** That is the normal setup: two
vault folders, each with its own rules, its own Claude Code configuration
directory and a start command. Ask Claude; it adds a line like
`alias workbrain='CLAUDE_CONFIG_DIR=~/.claude-work claude'` to your shell
profile.

**`claude` vs `workbrain`?** Same program, different configuration
directory. `claude` has the private brain's rules, skills and sessions;
`workbrain` has the work vault's rules, its own copy of the skills and
its own sessions. Nothing crosses over. A new one may ask you to log in
once.

**The skills write into the wrong brain.** Check in this order:
1. The command. `claude` started outside a vault folder writes to the
   brain in `~/.claude/CLAUDE.md`, never to the work vault; a session
   started inside a vault writes to that vault.
2. The `Brain vault:` lines:
   `grep "Brain vault:" ~/.claude/CLAUDE.md ~/.claude-work/CLAUDE.md`
3. The skills: each configuration directory needs its own copy of the
   five `brain-*` skills.

Then tell Claude to move misfiled notes ("move that note into my work
brain"), or `git checkout` them away.

## Updating and uninstalling

**Update to a newer kit version.** Tell Claude: *"Update my brainwarden
setup from https://github.com/nikolajhellhoeflinger/brainwarden — follow
the Updating section in SETUP-FOR-CLAUDE.md."* Notes are never touched;
only skills, the search tool and the dashboard scaffolding are replaced.

**Uninstall completely.**
1. Scheduled the unattended review? Run
   `python3 .tools/autoreview.py uninstall` inside the vault first, or
   its scheduler entry (LaunchAgent / Windows task / systemd timer)
   outlives the vault.
2. `rm -rf ~/Brain` (PowerShell: `Remove-Item -Recurse -Force ~\Brain`),
   or keep it; it is just Markdown.
3. Delete the five `brain-*` folders from `~/.claude/skills/`.
4. Remove the "Brain" block from `~/.claude/CLAUDE.md`.
5. Hooks: delete each file and its `settings.json` entry; state files
   under `~/.claude/state/brainwarden-*` are safe to delete.
6. Second brain: `rm -rf` its vault and its configuration directory
   (`~/.claude-work`; a company vault's is `~/.claude-<company-slug>`,
   which also holds its session transcripts), and delete the
   `alias workbrain=…` (or `teambrain=…`) line from `~/.zshrc` or
   `~/.bashrc`.

Nothing else is touched.

## Unattended weekly review

**Can Claude run the weekly review on its own?** Yes, opt-in. Know first:
- **It spends your subscription** like a normal session. Weekly is
  cheap; never run it more than daily.
- **It edits and commits unattended**, under the review skill's
  autonomous rules: it deletes nothing uncertain, archives nothing
  unasked and parks questions in Home's "Open questions" block. Every
  change is one `git checkout` from undo.
- **It logs** to `<your vault>/.tools/logs/autoreview-YYYY-MM-DD.log`
  (one file per day, last 12 kept): runner lines plus the model's report
  (filed, left alone, questions). The folder is excluded from search and
  the Obsidian graph and safe to delete. Nothing about who read or
  searched what is recorded.
- **It is a convenience.** The manual "brain review" stays the ritual; a
  phone reminder is the free alternative.

**Setting it up.**
- Easiest: **Claude Code Desktop → Routines** (macOS, Windows, Linux):
  New routine → Local → your `~/Brain` → instructions "run the
  brain-review skill on this vault" → Weekly.
- Hardened (terminal): ask *"set up an automatic weekly brain review"*;
  Claude runs `python3 .tools/autoreview.py install`. A check runs every
  20 minutes (launchd / Task Scheduler / systemd), the review once a
  week. A failed run gets one immediate retry, then waits for the next
  day; only a run cut off by sleep may retry the same day.

**What the hardened runner does:**
- **Starts only when you are at the computer** and keeps it awake while
  it runs; a slept-through run is caught up, not reported as an error.
  Linux needs `xprintidle` (X11) for this; without it the runner starts
  anyway.
- **Commits before and after:** your captures first, then the review as
  one commit `Review YYYY-MM-DD (unattended)`, partial work included if
  the run aborts. The model runs no git. These commits skip your Git
  hooks and `fsmonitor`; after each model run the cache
  `.tools/__pycache__` is cleared.
- **`python3 .tools/autoreview.py undo`** reverts exactly the last
  unattended review's commit (`git revert`), never earlier captures.
- **Failures leave a file:** `!Review failed.md` in the inbox says what
  happened and what to do; `!Review overdue.md` appears on the 11th day
  without a success (`patience_days`, default 10). Both vanish after the
  next success; macOS and Linux also notify.
- **Notes that would abort it are set aside, never lost.** A note dense
  with, say, offensive-security tool names can trip the model's
  safeguards. Such captures move to `00-inbox/.set-aside/`, listed in
  `Set aside.md`. Word list: `.tools/set-aside-terms.txt`;
  `set-aside --restore` brings them back.
- **A note cannot take over the run.** The model gets only the vault's
  own tools, each limited to the command line the review needs, and a
  move/delete confined to the vault: no free shell, git, web or MCP
  servers, and no writes to kit files, Git hooks or config (also of a
  nested repository), `.vscode/`, Obsidian plugins, `.mcp.json` or any
  `CLAUDE.md` in any letter case. Read-only commands Claude Code always
  allows (like `git log`) still work.
- **Tampering rolls the run back.** Those files are fingerprinted and
  copied first; if any changed, all are written back byte for byte,
  untracked ones too. What the run created or changed is first kept in
  `.git/brainwarden-rolled-back/<date>/` (outside notes and history),
  each copy ending in `.kept` so it cannot run; drop the ending to use
  one. Git's config is restored before any git command.
  `!Review failed.md` says where, and to look for a note with text aimed
  at the AI. Plugin settings (`data.json`) are put back as they were.
- **Limit:** text from a note can still reach a signpost or Home, which a
  later session reads. A session you sit in asks before it acts.
- **Your own scripts:** allow them by name in `.tools/autoreview.json`,
  e.g. `"tools": ["mine.py"]`. Only plain names of files in `.tools/`
  count (no paths, links or kit scripts); the folder is protected, so no
  note can extend the list. The model may pass any arguments, so list
  only scripts that stay inside the vault whatever they get.
- **`status`** shows the last run, why none since, and which scripts were
  accepted. **`uninstall`** removes the schedule and nothing else.

## Company brains

**How do several people share one vault?** One maintainer keeps it in
Git and is the only writer. Everyone else reads a copy in Claude Cowork
(`COWORK.md`), Obsidian or a text editor, and sends contributions as
files in `00-inbox/suggestions/`. Where several people know Git, a
private remote everyone clones and pulls also works, still with one
writer. Never a synced cloud folder (Git plus Dropbox/OneDrive corrupts
vaults).

**Can I control who sees what?** Not inside one vault. `confidentiality:`
is a **label**: it satisfies the marking duty for trade secrets but locks
nothing; anyone who can open the folder reads every file. Real
separation means a second vault with its own repository and access
rights. Decide before filling the vault.

**Does the kit track who searched what?** No: no search log, no
per-person statistics, no telemetry. Such records can monitor
performance and in Austria and Germany are regularly subject to
works-council co-determination. The unattended review logs only what it
changed. Not legal advice; your legal contact or works council decides.

**Do colleagues have to know an AI maintains the vault?** Yes. Since
August 2026 the EU AI Act's transparency obligation applies inside
companies: people working with an AI system must be able to tell.
`About this vault.md` says so in its first lines and AI-drafted notes
carry `generated:`. Leave both in place.

**Someone can contribute but not release.** They write into
`00-inbox/suggestions/`; everything there is a proposal. The release
authority named in `About this vault.md` turns it into `status: stable`
with a filled `verified:`. The weekly review empties that folder.

**Why no notes about people?** A shared vault describes roles: `60-roles/`
holds what a role is responsible for and decides, never a dossier on a
named employee. Notes about people belong in a private brain (data
protection).

## Windows quirks

**Short version.** Install Git for Windows (default settings). Stay on
native Windows; skip WSL unless you already use it (Obsidian handles WSL
paths badly). After installing Claude Code, `claude doctor` should list
Git Bash.

**`claude` "not recognized" after a successful install.** Re-run the
install from CMD, not PowerShell:
`curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd`

**Setup hangs at `mkdir`/copy, or paths look mangled (`C:Userscl`).**
Almost always Git for Windows is missing. Install
[Git for Windows](https://git-scm.com/downloads/win) (default settings),
open a fresh terminal, restart `claude`; `claude doctor` should find Git
Bash.

**`python3` "not recognized".** Windows Python usually ships only
`python` and `py`. Tell Claude *"python3 doesn't exist here, use
py -3"*; it also fixes the search command in your global CLAUDE.md.

**A command does nothing at all.** Without Python installed, `python3`
opens the Microsoft Store. Install Python from python.org with "Add
python.exe to PATH" ticked, then check `py -3 --version`.

**Which terminal?** Commands with `ls`, `grep`, `rm -rf`, `cp -R` or
`~/Brain` are for **Git Bash**, the shell Claude Code uses on Windows.
PowerShell does not understand them or expand `~/Brain`:

| Git Bash | PowerShell |
|---|---|
| `ls ~/Brain` | `dir ~\Brain` |
| `rm -rf ~/Brain` | `Remove-Item -Recurse -Force ~\Brain` |
| `grep "Brain vault:" ~/.claude/CLAUDE.md` | `Select-String "Brain vault:" ~\.claude\CLAUDE.md` |
| `cd ~/Brain && git log --oneline` | `cd ~\Brain; git log --oneline` |
| `py -3 .tools/hygiene.py` | `py -3 .tools\hygiene.py` |

The Python tools (`search.py`, `hygiene.py`, `harvest.py`) behave the
same in all of them, `cmd` included.

**Installing the optional hooks on Windows.** The snippet in each hook
script's header (see `hooks/README.md`) reads
`"command": "python3 ~/.claude/hooks/capture_check.py"`. **Both halves
fail on Windows** (no `python3`, no `~` expansion), and the hook then
fails silently every turn. Use an absolute path, your working Python
command, and doubled backslashes in `settings.json`:

```json
{"hooks": {"Stop": [{"hooks": [
  {"type": "command",
   "command": "py -3 C:\\Users\\YourName\\.claude\\hooks\\capture_check.py"}
]}]}}
```

Test it; it must print a JSON line or nothing, never an error:
`echo {} | py -3 C:\Users\YourName\.claude\hooks\capture_check.py`

**A note shows as gibberish and search never finds it.** Wrong encoding:
PowerShell 5.1 writes UTF-16 with `>`, Notepad's old "ANSI" setting
writes cp1252; the vault expects UTF-8. `py -3 .tools/hygiene.py` lists
such files under **portability**. Re-save each as UTF-8 (the kit never
rewrites your notes). Append with `Out-File -Encoding utf8` instead of
`>`, or let Claude write.

**Cloning fails with an invalid-path error.** Windows cannot hold names
with `: ? * " < > |`, names ending in a space or dot, or the reserved
words `con`, `prn`, `aux`, `nul`, `com1`–`com9`, `lpt1`–`lpt9`. Typical
culprit: `KI: Schutz oder Überwachung.md`. `hygiene.py` lists them under
**portability**; rename them on a machine that can still see them, before
the vault reaches Windows.

**On WSL, Obsidian can't open the vault or is slow.** Obsidian handles
`\\wsl$` paths badly. Put the vault on the Windows side
(`C:\Users\You\Brain` = `/mnt/c/Users/You/Brain` from WSL).

## macOS quirks

**A link works on my Mac and is dead elsewhere.** macOS disks are
case-insensitive by default: a link to `ZIEL.md` opens `Ziel.md`, Linux
finds nothing. `hygiene.py` compares spellings exactly and reports:
`→ (30-knowledge/ZIEL.md)  [the file is 30-knowledge/Ziel.md — only the
spelling differs, which is a dead link on Linux]`. Fix the link, not the
file name.

**Two notes with almost the same name.** `Klugoro.md` and `klugoro.md`
are two files on Linux and one on macOS and Windows; cloning onto a Mac
silently loses one. `hygiene.py` lists the pairs under **portability**;
rename one before the vault travels.

**Commands that end in `sed -i ''`.** macOS ships BSD `sed`, `find` and
`date`, whose arguments differ from GNU's (Linux, Git Bash): `sed -i ''`
is required on macOS and silently does nothing on GNU. The kit never
asks you to run `sed`.

**Does Gatekeeper block the scripts?** No. They are text files run by
`python3` and `sh`, not apps. Files from `git clone` carry no quarantine
flag, and scripts from a downloaded ZIP run normally from the terminal.
If a command fails, the cause is something else.

**iCloud.** Keep the vault out of iCloud Drive, including "Desktop &
Documents Folders" sync: a vault in `~/Documents` is in iCloud. The
default `~/Brain` is outside it.

## Capturing on the go (mobile)

1. **Obsidian Sync** (easiest, ~$4/month): Obsidian app on the phone,
   Sync enabled for the vault. **Git on the desktop, Sync to the phone;
   never both on one device against the same folder.**
2. **Quick-capture shortcut into `00-inbox/`** (free): an iOS Shortcut or
   Android automation that appends to an inbox file. It still needs a
   sync (way 1, or iCloud with its Git caveats) to reach the desktop.
3. **Phone notes app** (free, no setup): type or dictate there; at the
   computer, tell Claude *"capture: [paste]"*.

**Voice memos.** Get the recording into `00-inbox/` by any of these, or
"Save to Files" into the synced vault (iPhone: Voice Memos → Share → Save
to Files; Android: the recorder's Share → the synced folder; Syncthing on
Android, Obsidian Sync or iCloud on iPhone). Then
`python3 .tools/transcribe.py` turns every m4a/mp3/ogg/… in the inbox
into a capture, moves the recording to `90-archive/voice/` and embeds it
in the note.
- It uses the first local speech engine found (mlx-whisper on Apple
  Silicon, whisper.cpp, faster-whisper, openai-whisper). Nothing is
  uploaded.
- It needs ffmpeg (ffmpeg.org; macOS: `brew install ffmpeg`) to convert
  recordings to WAV. `--check` names the engine and says if ffmpeg is
  missing.
- Run it once by hand (the first run downloads the speech model), then
  `transcribe.py --auto on` lets the runner's 20-minute tick do it.
- Speech models invent sentences on silence; check names and numbers
  against the recording.

Not supported: real-time sync everywhere, zero cost with zero setup, or
Git on the phone (Working Copy/MGit can, at far more setup than this kit
asks for).
