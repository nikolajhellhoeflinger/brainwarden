# The onboarding interview

For Claude: offered in setup Step 8b, or whenever the human says
"interview me for my brain". Optional; it can wait and works a block at
a time.

In a vault this script lives at `<vault>/.tools/INTERVIEW.md`. It is not
a note: no frontmatter, never filled in. If a check flags it, fix the
check.

## Which track

Before the first question, take the mode from the first source that
has it:

1. the `Mode:` line in the global rules block
2. `**Vault mode: …**` in the vault's `CLAUDE.md` (the reliable one: a
   company vault has no global rules block)
3. the root `index.md`

The label may be translated (`Betriebsart:`, `Modus:`); the value is
always `personal`, `professional` or `company`. Nothing found? Ask once
and write the answer into the vault's `CLAUDE.md`.

- `personal`: Track **A** (person track), all blocks.
- `professional`: Track **A** (person track), work blocks only. Skip
  everything private (family, hobbies, health, plans); offer their
  personal brain for it.
- `company`: Track **B** (process track). Never a person's life.

## Phase 0: ask this first (verbatim, before any question)

**Track A (`personal` / `professional`):**

> "Before the interview: may I look around this computer — folders like
> Documents and your projects, and my own past sessions with you — to
> pre-fill your brain with what I find? I'll list everything I looked at,
> nothing leaves this machine, and you can veto any note. Yes or no is
> both fine — the interview works either way."

**If yes:** spend a few minutes on what the permissions allow
(`~/Documents`, `~/Desktop`, project folders, git repos with their
authors and READMEs, past Claude sessions). Draft notes on the people,
projects, deadlines, interests and tools found
(`source: local discovery`, today's real date). Open with **"I saw X —
tell me about it"**, list every location you touched, delete whatever
they veto.

**If no:** skip silently, never mention it again.

**Track B (`company`): stricter, default no.** A work machine holds
other people's data. Ask instead:

> "Is there a specific folder with process descriptions, checklists or
> handbooks I should look at — one you're allowed to share with the team?
> If not, we'll do it entirely by conversation."

Read only the folder they name, never mailboxes or colleagues' personal
folders; report every file used.

## How to interview

- Block by block, any order; voice dumps welcome, skipping allowed.
- **Never leave a thin answer thin.** On "hmm, not much", offer three
  concrete options (the nudges below); ask for names, dates, numbers.
- React before moving on ("you mentioned a brother: what's his name?").
- Invent nothing; mark gaps as "open → ask later".
- "Private" means: don't write it down, don't probe.
- Afterwards: atomic notes, one idea each, all linked; search first,
  extend instead of twinning, real values in template placeholders.
  After the track's processing list: refresh `Home.md` (new projects,
  deadlines, open questions) only between the `<!-- block:… -->` marker
  pairs (never delete a `<!-- keep:… -->` line), update the `index.md`
  entry points of every folder you filled, `git commit`, ask 3–5
  follow-up questions about the biggest gaps.

---

# Track A: the human

**In a `professional` vault, Block 4 is the interview.** Start there,
then 2, 3, 5, 6, 7, 8 trimmed. Block 1 stays at role and employer; ask
nothing twice.

## Block 1: You at a glance *(professional: question 1 only, short)*
1. Who are you in three sentences: name, age, where you live, what you
   mainly do now (school / university / job / your own thing)?
   *(professional: role and employer only; the work is Block 4.)*
2. How would you describe yourself, and which part would others
   instantly confirm? *(personal only; working style is Block 7.)*
   *Nudge: night owl or early bird? builder or planner? starter or
   finisher?*

## Block 2: Your people *(professional: work people only)*
3. Who counts as family, and who plays a role in your daily life (who
   lives where, with whom)? *(personal only)*
4. Your closest friends: names plus one line each. *(personal only)*
5. Who matters at school, university or work (mentor, boss, teacher,
   business partner)?
   *Nudge: who would you call first with a problem? who do you learn
   most from? anyone you avoid?*

## Block 3: Everyday life & obligations *(professional: the work week)*
6. A normal week: what's fixed, what's flexible?
7. Which dates, deadlines or exams come in the next 3 months, official
   ones included?
   *Nudge: exams · applications · renewals/contracts · trips · family
   dates · anything governmental (license, service, visa, taxes).
   Professional: submissions, reviews, audits, contract dates.*
8. Which ongoing duties are you carrying, and which are you pushing
   ahead of you?

## Block 4: Zoom in on your work or studies *(core block in professional)*
Narrow down, then go deep. `personal`: ask whether they study, work or
both; take the fitting branch. `professional`: "If working" only,
without asking (studies belong in their personal brain).

**If working:**
- What does your work consist of, concretely?
  *Nudge: activities, not the title. "I check price lists, answer
  customer mails, prepare orders" beats "sales".*
- Which tasks come back every week?
  *Nudge: reports? invoices? stock checks? the same three mails? Get
  the full list; it is this block's main yield.*
- Where does most of your time go, and which part annoys you most?
- Which tools do you use daily, and which fights you most?
- Who do you work with most closely (names, roles)?

**If studying (school or university):**
- Where are you (school or university, year), and what's the big goal
  (final exams, degree, a grade)?
- Which subjects or courses demand the most now?
- What eats most of your learning time?
  *Nudge: summarizing? memorizing? writing? putting off one subject?*
- Which exams, submissions or presentations are coming, with dates?
- Which apps or tools do you use for school (notes, flashcards,
  calendar)?

## Block 5: Projects & goals *(professional: work projects only)*
9. What are you working on now (work, school, personal), and which
   project is closest to your heart?
   *Nudge: side projects too, what you learn at night, what you
   promised someone.*
10. What should be different 12 months from now?
11. Where do you want to be in about 5 years? What is a dream, what
    already a plan?

## Block 6: Knowledge & interests *(professional: expertise only)*
12. What are you genuinely good at? What do people come to you for?
13. What do you want to learn next?
    *Nudge: a skill for work/school · a language · a tool (AI? coding?) ·
    something physical (sport, instrument, license)?*
14. What do you consume regularly and gladly (books, podcasts, channels,
    creators), and which of it shapes your thinking?
    *(professional: trade press, standards, communities.)*
15. Which hobbies do you REALLY do regularly, and which exist only on
    paper? *(personal only)*
    *Nudge: what did you do last weekend? what do friends say you always
    talk about?*

## Block 7: Working style & energy *(both)*
16. When in the day are you most productive, and what is your real (not
    ideal) sleep and energy rhythm?
17. How do you actually learn or work best?
18. What currently eats most of your time or nerves?
    *Nudge: a duty? a person? commuting? your phone? something you keep
    postponing?*
19. What should Claude do more often in your collaboration, and less?

## Block 8: Closing *(both)*
20. What do you have genuine respect for in the coming year?
21. What else should your brain know that I didn't ask about?
22. Are there areas that stay fundamentally "private"? (I'll create a
    no-go note so future sessions respect it too.)

## After Track A (mandatory processing)
- Merge with the Phase-0 drafts; on conflicts the interview wins.
- People: one note each in `30-knowledge/people/`
  (`_templates/person-note.md`). Facts, principles, goals: atomic notes
  in `30-knowledge/` or `10-projects/` (`knowledge-note.md`,
  `project-note.md`).
- Recurring tasks from Block 4: `personal`, one note per area in
  `20-areas/`; `professional`, one process note per task in
  `50-processes/` (trigger, steps, owner, what usually goes wrong).
- Dates into `Deadlines.md`, one line each, date first. Self-image into
  `About me.md` as a hub with links and a "remaining gaps" list; keep
  the `**Name:**` line from setup at the top.
- Frontmatter: `maturity:` only in `30-knowledge/`. `professional`:
  every note outside the inbox also carries
  `status: draft | stable | deprecated`.

---

# Track B: the company

Interview whoever knows the area; several short sessions with different
people beat one long one. Record **roles, not people**: "the person who
does the invoicing" becomes `60-roles/invoicing.md`.

## Block C1: The company at a glance
1. What does the company do, for whom? Three sentences a newcomer
   would understand.
2. How big is it, which areas exist? (Confirm the setup answer.)
3. What goes wrong most often when someone new starts; what gets
   explained over and over?
   *Nudge: that answer is usually the second SOP to write.*

## Block C2: The processes (the core of this track)
Area by area; for EACH process get all five:
4. What is it called internally, and what triggers it (a customer mail,
   a date, an order, month-end …)?
5. What happens then? 3 to 7 steps, in the company's own words.
6. Who owns it, and who must be involved?
7. What typically goes wrong, and what does one do then?
8. Which tools or systems are involved, and where do their files live?
   *Nudge: walk me through the last real case, from the first mail to
   done.*

## Block C3: The questions that keep coming back
9. Which questions do customers ask again and again, and what do you
   always answer?
   *Nudge: open the last few mails or messages; the same three
   questions are usually there.*
10. Which questions do colleagues ask each other over and over?
    *Nudge: "how do I do X again?" · "who is responsible for Y?" ·
    "where do I find Z?"*
11. Which answers differ depending on who you ask? (Do those first.)

## Block C4: What only lives in one head
Ask without blame: this is about resilience, not judging a person.
12. If one person were out for four weeks, what would stall, and what
    would nobody know how to do?
13. Who is the only one who can do a particular thing (a system, a
    customer, a machine, a supplier relationship)?
14. What knowledge exists only as experience ("you just know that after
    two years"), and what of it can be written down?
    *Nudge: exceptions ("customer X always gets …", "with supplier Y you
    have to …") are exactly this.*

## Block C5: Roles and responsibilities
15. Which roles exist, and who decides what?
16. Which decisions may be made alone, and which need whose approval?
17. Which role owns which process from C2? *(Role names, not people,
    even when one person holds the role.)*

## Block C6: Language and terms
18. Which words would an outsider misread (product names,
    abbreviations, shorthand, customer categories)?
19. Which terms mean different things in two areas?

## Block C7: Partners and suppliers
20. Which suppliers, service providers or partners matter, and for what?
21. Who is the contact for each, and which agreements or deadlines exist
    (contracts, renewals, notice periods)?

## Block C8: Onboarding
22. What does someone new need in their first week, in which order?
23. Which three documents or explanations would you hand them first?

## Block C9: Rules, approval and confidentiality
24. Who says "this version is now official"? (Confirm the setup answer.)
25. How often should content be reviewed? A rhythm per area?
26. Which content is confidential, and towards whom? Say once:
    `confidentiality:` is a **label**, not a lock; anyone with folder
    access reads everything. Content part of the team must not see
    needs a separate vault.
27. Which fixed dates must the company hit (audits, inventory,
    reporting, contract dates)?

## After Track B (mandatory processing)
- Process: a note in `50-processes/` (`_templates/sop-note.md`) with
  purpose, trigger, steps, owner, what goes wrong, tools.
- Role: a note in `60-roles/` (`_templates/role-note.md`) with
  responsibility, owned processes, decision rights. No `people/`
  folder, no dossiers.
- C3, C4: a procedure becomes an SOP, the rest an atomic note in
  `30-knowledge/`. Differing answers: ONE note naming the
  contradiction, the decision question on `Home`. Holder absent: an
  open question on `Home`.
- C6: a glossary, one note per term in `30-knowledge/`, cross-linked
  where areas use a word differently.
- C7: one note per partner in `80-partners/`
  (`_templates/partner-note.md`); contract dates into `Deadlines.md`.
- C8: `70-onboarding/onboarding-path.md`
  (`_templates/onboarding-plan.md`), a short route with real relative
  links to the SOPs.
- Decisions that came up: dated records in `40-decisions/`.
- Frontmatter on EVERY note: base schema + `status:`, `owner:`,
  `audience:`, `confidentiality:`, `review_due:` (default 12 months);
  `generated: {by: …, at: …}` on your drafts. Never fill `verified:`;
  that is the confirming human's.
- All stays `status: draft` until the person named in C9 confirms it.
  Material from someone without release rights goes to
  `00-inbox/suggestions/` until released.
- With the follow-up questions, name the areas with no process note yet.
