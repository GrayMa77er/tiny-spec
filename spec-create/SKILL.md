---
name: spec-create
description: Start or update a spec — capture intent and requirements into .spec/SPEC.md. On first run, scaffolds .spec/ and seeds the constitution (conventions.md) from a short interview. Re-run to update an existing spec in place.
---

# spec-create

Captures **what** the user wants and **why**, as testable `REQ-N` requirements.
This is the front door of the flow.

All artifacts live under `.spec/` in the **project root** (the user's cwd) — never
in this skill's directory. Templates ship in this skill's own `templates/` folder
(alongside this file); read them from there.

## First run — scaffold

If `.spec/` does not exist:

1. Create `.spec/`.
2. **Short interview** (keep it short — earned ceremony):
   - the intent in one paragraph;
   - the language/stack and where code lives;
   - the must-have requirements (the capabilities, not the design).
3. Seed the **constitution**: copy this skill's
   `templates/conventions.template.md` to
   `.spec/conventions.md` and fill in what the interview already told you (Style,
   Layout, Verification commands at minimum). Leave the rest for `spec-plan` to
   harden — but never leave a section empty of intent.

## Write `SPEC.md`

Copy this skill's `templates/SPEC.template.md` to
`.spec/SPEC.md` and fill it in:

- a one-paragraph **intent**;
- a `## Requirements` list — each `REQ-N` a single **user-observable, testable**
  capability with **no implementation detail** ("the CLI accepts a `--json` flag
  and prints valid JSON", not "add a json module").

Number requirements `REQ-1, REQ-2, …`. Keep each atomic — if a line has an "and"
that hides two capabilities, split it.

## Update mode (re-run on an existing spec)

When `.spec/SPEC.md` already exists and the user wants a change to requirements:

1. Edit `SPEC.md` in place — add/alter/remove `REQ-N`, preserving existing ids
   where the requirement still exists.
2. Flip downstream **stale**: set `PLAN.md` and `tasks.md` frontmatter to
   `status: stale` (if they exist).
3. Log it: append a `decisions.md` entry (`type: change`, the affected `REQ-N`).
   Create `decisions.md` if absent.

Tell the user which downstream docs went stale and to re-run `spec-plan` to
reconcile.

## When done

Report the requirements captured and point the user at `spec-plan`.
