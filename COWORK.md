# Using a Brainwarden vault in Claude Cowork

Cowork is Anthropic's desktop agent for people who do not use a
terminal: you point it at a folder and describe what you want. **The
vault works in Cowork; the skills and hooks do not.**

> **Whoever set the vault up:** this page lives in the kit repo, which
> you may delete. Step 7b of `SETUP-FOR-CLAUDE.md` copies it to
> `<vault>/.tools/COWORK.md` (not the vault root, where search would
> rank it among the notes) and sends it on. If the notes are not in
> English, translate the instruction block in step 3 and the sentences
> in step 4 first.

## What carries over

Everything that makes the vault navigable is plain Markdown in the
folder Cowork reads:

- **the notes;**
- **every `index.md` signpost** (what belongs in the folder and what does
  not). The per-folder `CLAUDE.md` only loads it into Claude Code; in
  Cowork an agent opens `index.md` directly;
- **the frontmatter** (`status`, `verified`, `owner`, `review_due`),
  which any agent can read and apply;
- **the vault's `CLAUDE.md`**: not loaded automatically, but a one-line
  project instruction makes Cowork read it.

## What does not carry over

| | Claude Code | Cowork |
|---|---|---|
| Skills from `.claude/skills/` in the folder | loaded | **not read** — Cowork loads skills enabled on your claude.ai account |
| `CLAUDE.md`, incl. per-folder ones | loaded, subfolder ones lazily | **not documented; assume no** |
| Hooks (`Stop`, `SessionEnd`) | supported | **not supported** (open feature request) |
| Running `.tools/*.py` directly | yes | only as scripts inside an uploaded skill |

So Cowork users lose the **capture net** and the **session queue**. Both
fill the vault; reading is unaffected. The usual split: the maintainer
uses Claude Code, everyone else Cowork.

## Setting it up in Cowork

1. **Put the vault folder on the machine**, not in a cloud-sync folder.
2. **Claude Desktop → Cowork → add the folder to a project.**
3. **Paste this into the project's instructions** (it stands in for the
   global rules block; it is read every time, so keep it short):

   ```
   This folder is a Brainwarden knowledge vault.
   Read index.md first — it is the folder map. Read CLAUDE.md before
   writing anything; it holds the schema and the rules.
   When you open a folder, read its index.md before its notes.
   Content counts as valid only with status: stable AND a filled verified:
   line. Everything else is a draft — say so when you quote it.
   Never invent a figure, a price, a condition or a deadline. "I don't
   know, ask the owner named in the note" is a correct answer.
   ```

4. **Hand over three first sentences**, in the vault's language. The
   vault does not contain them:

   - *"What is this folder, in three sentences?"* — it reads
     `About this vault.md` and answers.
   - *"How do we do <the thing you were hired to do> here?"* — "I don't
     know, ask <role>" is a correct answer.
   - *"Write a suggestion into 00-inbox/suggestions/: …"* — how you
     correct something. It stays a proposal until someone releases it.

   Readers need nothing else.

5. **Optional, the five verbs:** package each skill as a zip and enable
   it under Customize → Skills on claude.ai. Only the procedure carries
   over: every skill's retrieval step is `python3 .tools/search.py`, and
   `brain-review` also calls `hygiene.py`, `harvest.py --queue` and
   `git commit` (see the table's last row). Asking and capturing work;
   the weekly review needs Claude Code. Read-only users skip this.

   In `company` mode Step 4a copies the five skills into
   `<vault>/.claude/skills/`. Cowork does not read that folder; the
   copies are for whoever opens the vault in Claude Code.

## Claude Desktop chat and other apps (MCP)

Cowork and the Code tab open the folder themselves. The Chat tab and
other MCP apps need an MCP server. The kit recommends
[MCPVault](https://github.com/bitbonsai/mcpvault) (MIT), **read-only**:
it reads the folder directly (Obsidian need not run), opens no network
port, needs no API key and refuses `.git/`, `.obsidian/` and other
dot-folders. Version 0.18.4 with `--read-only` offers eleven reading
tools and refuses writes itself.

1. Install Node.js (LTS, 22.12 or later) from nodejs.org.
2. Claude Desktop → Settings → Developer → Edit Config. Add, with your
   vault's absolute path (Windows: `"C:\\Users\\YOU\\Brain"`, double
   backslashes):

   ```json
   {
     "mcpServers": {
       "brain": {
         "command": "npx",
         "args": ["-y", "@bitbonsai/mcpvault@0.18.4", "/Users/YOU/Brain", "--read-only"]
       }
     }
   }
   ```
3. Quit Claude Desktop completely and restart; `brain` appears under
   **+ → Connectors**. Not starting? On Windows use `"command": "cmd"`
   with `"/c", "npx",` in front of the arguments; with Node from
   Homebrew or nvm, put the full path of `npx` into `"command"`.
4. **Give it the rules.** Make a Claude Desktop Project for the vault and
   paste the instructions from step 3 of the Cowork setup, plus: *"You
   reach the vault only through the read-only "brain" connector. Read
   index.md and CLAUDE.md with it first. You cannot change the vault:
   when something should be added or corrected, write it out for me to
   file with Claude Code."* In a personal brain, drop the line about
   `status: stable` and `verified:`.

**Keep it read-only.** An MCP app loads none of the vault's skills or
hooks. Without the flag the server can overwrite, move and permanently
delete notes, and a note whose text reads like an instruction would have
tools to act on. Writing stays in Claude Code. The version is pinned;
raise it on purpose, after reading the changelog. Alternative: the
official filesystem server
(`@modelcontextprotocol/server-filesystem --read-only <vault>`, Node
24+), which knows nothing about Obsidian and shows `.git/` and
`.obsidian/` to the model.

**Obsidian's own formats** (wikilinks, properties, callouts, Bases,
Canvas) in Claude Code: `/plugin marketplace add obsidianmd/obsidian-skills`,
then `/plugin install obsidian@obsidian-skills` (MIT). Brainwarden decides
what goes where; those skills write it the way Obsidian reads it.

## Which one for whom

- **Cowork:** everyone who reads (sales, marketing, accounting,
  branches). No terminal, nothing to install beyond the app, access
  limited to the folder.
- **Claude Code:** the one maintainer, who runs the weekly review, uses
  `hygiene.py`, `harvest.py --queue` and (company vault) `progress.py`,
  and wants the capture net.

Both work on the same folder. Someone working from a *copy* should first
read `THIS-COPY.md` in the vault root: it carries the date the copy was
cut.

*Sources: Cowork pages on claude.com and support.claude.com; the hooks
gap is an open issue in the claude-code repository. If Cowork changes,
only this page needs updating.*
