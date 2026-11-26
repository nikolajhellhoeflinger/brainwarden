# modules/ — mode overlays (kit only, NEVER part of a vault)

The vault template has ONE core. What a `professional` or `company`
vault adds lives here as an **overlay**: a folder tree shaped exactly
like a vault root, so applying it is a plain copy. `personal` gets no
overlay.

```
modules/
├── processes/   → professional AND company   (50-processes/ + the SOP template)
└── company/     → company only               (60/70/80, suggestions/, overrides)
```

This `README.md` must never reach a vault; it sits above the overlays,
so copying `modules/<name>/.` cannot pick it up.

## Applying an overlay (for SETUP-FOR-CLAUDE.md)

```
python3 assemble.py ~/Brain <personal|professional|company>
```

`assemble.py` (kit root) copies the core, then the mode's overlays in
order, skips `modules/` and leaves out what a shared vault must not
carry. It never overwrites a file that was already there (on the adopt
path too: the vault's own `About this vault.md`, `Home.md` or filled-in
`index.md` stay) and lists what it left alone.

- Keep overlays shaped like a vault root; the script relies on it.
- What company mode drops is listed in `COMPANY_DROPS` at the top of
  `assemble.py`, the one place to change it. It includes
  `person-note.md`: a vault whose rule is "roles, not people" gets no
  dossier template.
- An overlay ships a folder's `CLAUDE.md` only when it CREATES the
  folder; where it only overrides an `index.md`, the two-line
  `CLAUDE.md` is already there from the core.
- The company `Home.md` keeps the SAME four block markers as the core
  (`block:right-now`, `block:next-deadlines`, `block:open-questions`,
  `block:new-this-week`). The skills address them; never rename them per
  mode.

## What each overlay adds

| Overlay | Adds |
|---|---|
| `processes/` | `50-processes/` and `60-contribution/` (each index + CLAUDE.md), `handover.md`, `_templates/sop-note.md` + `meeting-note.md` + `contribution-entry.md` + `learning-note.md`, and two overriding files: `_templates/index.md` (lists the SOP template) and the root `index.md` (names the folder that defines this mode) |
| `company/` | `60-roles/`, `70-onboarding/` (incl. `onboarding-path.md`), `80-partners/`, `00-inbox/suggestions/`, `About this vault.md`, `THIS-COPY.md` (carries the date of a distributed copy), `.tools/progress.py` (how much of the vault is verified), `_templates/role-note.md` + `partner-note.md` + `onboarding-plan.md`, and the thirteen overriding files below |

**The company overlay OVERWRITES thirteen files**, twelve from the core
plus the processes overlay's `_templates/sop-note.md`:

- **Nine refer to folders a company vault lacks:** six `index.md` (root,
  `00-inbox/`, `30-knowledge/`, `40-decisions/`, `90-archive/`,
  `_templates/`), `Home.md` (the core one links `[[About me]]`, which
  company mode deletes), `Deadlines.md` and **`CLAUDE.md`**, the binding
  rules file. The core one describes projects, areas and person notes;
  left in place, it makes an agent create personnel dossiers.
- **Four note templates** whose core versions fail this mode's
  frontmatter check: `_templates/knowledge-note.md`,
  `_templates/source-note.md`, `_templates/sop-note.md`,
  `40-decisions/_template.md`. They carry `ownership: private` and lack
  `owner`, `audience`, `confidentiality`, `review_due`, so every note
  made from them would be a `hygiene.py` **frontmatter gap** (Step 9
  demands zero). Neither `hygiene.py` nor `progress.py` scans
  `_templates/`, so nothing would point at the cause.

## Placeholders the setup still has to fill
- `{{MODE}}` and `{{LANGUAGE}}` in the vault `CLAUDE.md`
- `{{MODE}}` and `{{LANGUAGE}}` in the root `index.md` (both variants)
- `{{DATE}}` in `About this vault.md` and **four times in `THIS-COPY.md`**
  (the date of the copy, its `created:`, its first changelog line, and
  `review_due:`, which gets today + 12 months, not today)
- `{{COMPANY}}` in `About this vault.md` and `70-onboarding/onboarding-path.md`
- the nine `<…>` fields in `About this vault.md`, `Deadlines.md` and
  `70-onboarding/onboarding-path.md`. `hygiene.py` cannot see them
  (`owner: <role that owns this vault>` is a non-empty value);
  `progress.py` counts them. Run it before handing the vault over.

## Adding another module later
Add a folder here shaped like a vault root and a row in the table above.
Every content folder it introduces brings its own `index.md` and
two-line `CLAUDE.md`, as in the core.
