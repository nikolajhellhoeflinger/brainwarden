# Hooks — optional, opt-in

The five skills cover the moments you decide to capture or ask. These
three Claude Code hooks cover the moments you forget:

| Hook | Event | What it does |
|---|---|---|
| `capture_check.py` | `Stop` | asks Claude to capture when nothing has reached the vault for a while |
| `session_queue.py` | `SessionEnd` | notes one line per finished session for the weekly review |
| `project_context.py` | `SessionStart` | briefs a session in a project's code folder on what the brain knows |

The setup installs none of them. Add one yourself, or ask Claude
("install the capture check from brainwarden's hooks folder").

**Install:**
1. Copy the script to `<config>/hooks/`. `<config>` is `~/.claude`, or
   whatever `CLAUDE_CONFIG_DIR` points at; a second brain uses its own
   (e.g. `~/.claude-work`), so file, entry and path all go there.
2. Add the entry from the script's header to `<config>/settings.json`.
3. Where `~` is not expanded (Windows shells generally), write the path
   out in full, and use the Python command that works there, e.g.
   `py -3`. `TROUBLESHOOTING.md` has the Windows entry form.

The hooks need only Python 3, which the vault's tools already require,
and behave the same on macOS, Linux and Windows.

**Uninstall:** delete the file and its `settings.json` entry. The state
file named below may stay or go.

## `capture_check.py`

**What it does.** At the end of a turn it looks for a recently modified
`.md` file in `00-inbox/` or `40-decisions/`. If it finds one, it stays
silent. If not, it makes Claude check the five capture triggers once (a
decision, a date, a milestone, a new person, a lesson learned the hard
way) and capture what is worth keeping.

**Which vault.** The one the session runs IN: the folder, or one above
it, that has an inbox, the kit's `.tools/` and a `CLAUDE.md` naming its
mode (`personal`, `professional` or `company`). A code repository whose
rules file merely says "Mode:" never counts. Elsewhere it uses the
`Brain vault:` line in `<config>/CLAUDE.md` (bold or in backticks too),
and `~/Brain` when there is none.

**It backs off by itself:**

| what happened after it asked | what it does next |
|---|---|
| something landed in the vault | asks twice as often (floor: base ÷ 4) |
| nothing landed | asks half as often (ceiling: base × 16) |
| nothing, five times running | goes to sleep and stops asking |
| asleep, and the vault starts filling again | wakes up at the base interval |

With the default base of four hours, the interval runs from one hour to
about two and a half days. Ignoring it switches it off; capturing again
switches it back on.

It measures only file timestamps, not whether or what you answered. A
capture written by hand counts as a hit even though the hook did not
cause it; an interrupted turn counts as a miss.

**It never:**
- calls a model or the network: the pre-filter walks two folders
  comparing `mtime` and stops at the first recent file;
- writes into the vault, reads your conversation, sends anything
  anywhere, or decides what is worth keeping;
- asks twice in a row;
- speaks when it cannot write its state file (read-only config, a
  directory in its place). It stays silent instead.

**State:** `<config>/state/brainwarden-capture-check`, three numbers
(when it last spoke, when it last asked, the current level) and no
content. `python3 <vault>/.tools/harvest.py --queue` prints it in plain
language. Deleting the file resets it.

**Tuning:**
- `BRAINWARDEN_CAPTURE_WINDOW` (minutes, default 240) sets the base
  interval the ladder moves around.
- `BRAINWARDEN_CAPTURE_CHECK=off` silences it without uninstalling.
- Asks too often? Raise the base, or answer "nothing worth keeping" and
  let it back off.

## `session_queue.py`

**What it does.** When a session ends it appends one line to a queue:
four tab-separated fields, e.g.
`2026-08-11 17:04` · `lager` · `a1b2c3d4` · `clear` (when, project,
session id, why it ended). The weekly review reads the queue and asks
about sessions it has not seen: *what came out of this one?* That covers
weeks spent in an ERP, on the phone or in a warehouse, which leave no
files and no commits.

**It never:**
- records anything that was said, reads the transcript, or stores the
  transcript's path (the session id is enough to find a session again);
- calls a model. `SessionEnd` hooks share a 1.5-second budget (raised to
  match a longer per-hook `timeout`, up to 60 seconds);
- writes into the vault. Only the review turns a queue line into a note,
  with a human present.

**State:** `<config>/state/brainwarden-session-queue.tsv`, a rolling
window of the last 500 lines. Each session end is a single append; the
rare trim is written beside the file and moved into place with
`os.replace`, so a hook killed mid-write cannot empty the queue.

**Read it any time:** `python3 <vault>/.tools/harvest.py --queue`
**Uninstall:** delete the file, the settings entry and the queue.

## `project_context.py`

**What it does.** When a session starts in a folder that belongs to one
of the brain's projects, Claude gets a brief of at most ~550 tokens: the
project note and its first line, the open next steps, the three newest
decisions that mention the project (superseded ones left out), the next
three dates from the top-level notes, and the open questions from the
project note and from Home, each with the path to read before changing
direction.

**Which folder is which project:**
- explicitly, by a line in the project note's frontmatter:
  `folders: [~/code/shop, ~/code/shop-api]`;
- or by name: the repository's folder is called like the note (or one
  of its `aliases:`), ignoring case and spaces vs. hyphens. A suffix is
  dropped one hyphen at a time, so `acme-shop-api` finds
  `Acme-Shop.md`; never the reverse, so `~/code/acme` finds nothing.

**It is silent** in every folder that is not a project, inside the vault
(its own `CLAUDE.md` loads there), inside any other vault, on a resumed
session and on any error. A hook that pours the brain into every session
would leak private notes into client repositories and screen shares.

**It never** writes, calls a model, opens a connection or reads person
notes. The brief is the person's own notes handed over as material, and
says so in its first line.

**State:** none. **Uninstall:** delete the file and the settings entry.

## What no hook can see

Claude in the browser, Claude Cowork and a phone have no hooks (see
`COWORK.md`), and some people never open a terminal. For their weeks the
review asks the human, with cues, because free recall over seven days is
weak and favours yesterday:

- **day by day:** Monday through Sunday, one line each, instead of "the
  week";
- **by counterpart:** walk `30-knowledge/people/` (or `60-roles/`,
  `80-partners/`) by name: "anything with them this week?";
- **by open loop:** every date in `Deadlines.md` and every open question
  on `Home.md`: "what happened with this one?"

All three use what the vault already knows. `harvest.py --queue` prints
them when no queue exists.
