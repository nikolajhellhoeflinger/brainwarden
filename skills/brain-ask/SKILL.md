---
name: brain-ask
description: Answer questions from the Brain with cited notes. Use when the user says "what does my brain know about …", "ask my brain", "what did I decide about …", "who is …", "what's the status of …", or when any question is about their own life, people, projects or past decisions.
---

# Brain ask (the librarian)

Answer from the human's OWN notes, show where every claim comes from,
and say plainly what the brain does not know.

**Conventions:** `<vault>` = **the vault this session runs in**: the
folder it was started in, or one above it, whose `CLAUDE.md` names a
vault mode (`personal`/`professional`/`company`) and that holds the
kit's `.tools/`. Otherwise the path on the `Brain vault:` line in your
global rules. Only when neither exists, `~/Brain` (a shared company
vault has no global line, so falling back to `~/Brain` there would
write into somebody's private vault). `python3` = your working python
command (on most Windows machines `py -3`; the global rules name it).

## Steps
1. **Orient, then search wide.** Read `<vault>/index.md` first: it names
   the mode, the vault language, the folder map and the search tool,
   none of which you have unless this session started inside the vault.
   (No `index.md`? Read `<vault>/CLAUDE.md`.) Skim `<vault>/Home.md`,
   then run `python3 <vault>/.tools/search.py <terms>` with 2–3 term
   variants (synonyms, the person's name, the project slug). Read ONLY
   the hits, never the whole vault.
2. **Answer from the notes**, in the vault language, citing every source
   note as a `[[link]]`. Where the vault and your general knowledge
   disagree about the human's life, the vault wins.
   **Questions about people** go to `python3 <vault>/.tools/people.py`
   first:
   - "who can I ask about X?" → `people.py who <topic words>` (ranked,
     with evidence — quote it, never offer a bare name)
   - "I'm meeting X" → `people.py brief <name>`
   - "who haven't I heard from?" → `people.py close --k 100` (closest
     first; read the oldest `last` dates and the `quiet since` marks at
     the bottom)
   - "who could I get back in touch with about X?" →
     `people.py revive <topic>` (quiet for 3+ years)

   Read the person notes it names before answering.
3. **Decisions:** quote the decision record (`40-decisions/`) including
   its reasoning. A record marked `Superseded by …` is history: answer
   from the one that superseded it and name both.
4. **Two hits contradict each other? Do not pick one.** Give both with
   their dates, say which is newer and where each comes from (a moved
   date often leaves the old one standing), and offer to capture the
   correction. A self-contradicting vault is a finding to report.
5. **Say what is missing:** "your brain has nothing on X" is a correct
   answer — name the closest note you did find. Never fill gaps with
   invented vault content.
6. **Offer the next step** when a gap is researchable ("want me to
   research that and work it in?" → skill `brain-research`), or capture
   the open question to the inbox if they answer it on the spot.

## Rules
- Every claim is traceable to a note or clearly labeled as NOT from the
  vault.
- In `company` mode (the vault `CLAUDE.md` names it) this is absolute:
  answer only from notes, cite the file path for every statement, and
  say "I don't know" rather than reason your way to a plausible number.
  Label `status: draft` notes as proposals, not company truth.
- Short questions get short answers — cite, don't lecture.
- Works from ANY session, whatever project is open.
