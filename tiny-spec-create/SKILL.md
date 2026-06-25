---
name: tiny-spec-create
description: Start or update a spec — capture intent and requirements into .spec/<slug>/SPEC.md, optionally bound to a ticket (or ad-hoc). On first run, scaffolds .spec/ and seeds the shared constitution (constitution.md) from a short interview. Re-run to update an existing spec in place.
---

# tiny-spec-create

Captures **what** the user wants and **why**, as testable `REQ-N` requirements.
This is the front door of the flow. A spec can be bound to a ticket or worked
**ad-hoc** — both are first-class (see below).

The suite works **one spec at a time**, namespaced per spec. Artifacts live
under `.spec/` in the **project root** (the user's cwd) — never in this skill's
directory. Two are **project-wide** and shared at the `.spec/` root
(`constitution.md`, `memory.md`); the per-spec ones (`SPEC.md`, `PLAN.md`,
`tasks.md`, `decisions.md`) live under `.spec/<slug>/`. Templates ship in this
skill's own `templates/` folder (alongside this file); read them from there.

## Pick the slug (resolve the active dir)

Each spec lives in its own directory `.spec/<slug>/`. At the start of the interview,
establish the slug. There are two paths — both are first-class:

- **Bound to a ticket.** Ask for the **provider** (`jira | github | ado | monday`),
  **id**, **url**, and optionally the current **status**. Derive the slug from the
  platform key: verbatim when filesystem-safe (`PROJ-123`); otherwise normalize —
  GitHub `#42`→`gh-42`, Monday item→`monday-<id>`, ADO `AB#77`→`ado-77`.
- **Ad-hoc (no ticket).** Perfectly supported — just confirm there's no ticket and
  use a short kebab-case slug of the feature name (e.g. `dark-mode`, `perf-pass`).
  The SPEC omits the `ticket:` frontmatter block, and commits drop the `Refs:`
  footer (everything else — namespacing, the constitution, the build loop — is
  identical). You can bind a ticket later by adding the block to `SPEC.md`.

Create `.spec/<slug>/` and write the slug as the single line of `.spec/ACTIVE` (the
pointer every downstream skill reads to find the active spec).

## First run — scaffold

If `.spec/` does not exist:

1. Create `.spec/` and the active ticket dir `.spec/<slug>/`, and write `.spec/ACTIVE`.
2. **Short interview** (keep it short — earned ceremony):
   - the ticket binding (above);
   - the intent in one paragraph;
   - the language/stack and where code lives;
   - the must-have requirements (the capabilities, not the design).
3. Seed the **shared constitution**: copy this skill's
   `templates/constitution.template.md` to `.spec/constitution.md` (the **root**, not
   the ticket dir — it is project-wide) and fill in what the interview already told
   you (Style, Layout, Verification commands at minimum). Leave the rest for
   `tiny-spec-plan` to harden — but never leave a section empty of intent. If
   `constitution.md` already exists (a prior ticket created it), **reuse it** — do
   not overwrite the project's constitution.

## Write `SPEC.md`

Copy this skill's `templates/SPEC.template.md` to `.spec/<slug>/SPEC.md` and fill
it in:

- the **ticket binding** frontmatter block (or omit it if there's no ticket);
- a one-paragraph **intent**;
- a `## Requirements` list — each `REQ-N` a single **user-observable, testable**
  capability with **no implementation detail** ("the CLI accepts a `--json` flag
  and prints valid JSON", not "add a json module");
- the optional sections (`Context`, `Non-goals`, `Success criteria`,
  `Open questions`, `Links`) where they add value — omit any that don't apply.

Number requirements `REQ-1, REQ-2, …`. Keep each atomic — if a line has an "and"
that hides two capabilities, split it.

## Update mode (re-run on an existing spec)

When the active ticket's `SPEC.md` already exists and the user wants a change to
requirements (resolve the active dir from `.spec/ACTIVE`):

1. Edit `.spec/<active>/SPEC.md` in place — add/alter/remove `REQ-N`, preserving
   existing ids where the requirement still exists.
2. Flip downstream **stale**: set `PLAN.md` and `tasks.md` frontmatter to
   `status: stale` (if they exist).
3. Log it: append a `decisions.md` entry to `.spec/<active>/decisions.md`, using the
   fixed skeleton (`type: change`, the affected `REQ-N`). Create the file if absent:

   ```
   ## D-NNN — <short title>
   - type: change
   - date: <ISO date>
   - affects: REQ-N
   - note: <what changed + why>
   ```

Tell the user which downstream docs went stale and to re-run `tiny-spec-plan` to
reconcile.

> **New spec?** To start a different piece of work (a new ticket or an ad-hoc
> change), re-run this skill — it creates a new `.spec/<slug>/` and repoints
> `.spec/ACTIVE`. The shared `constitution.md` and `memory.md` carry over; the
> previous spec's artifacts stay untouched on disk.

## When done

Report the requirements captured and point the user at `tiny-spec-plan`.
