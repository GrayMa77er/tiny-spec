---
name: tiny-spec-create
description: Start or update a spec — capture intent and requirements into .spec/<slug>/SPEC.md, optionally bound to a ticket (or ad-hoc). On first run, scaffolds .spec/ and seeds the shared constitution (constitution.md) from a short interview. If a BREAKDOWN.md (from tiny-spec-breakdown) is present, seeds the spec from a chosen story instead of a full interview. Re-run to update an existing spec in place.
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

## Seeded mode (`BREAKDOWN.md` present)

Before interviewing, check for **`BREAKDOWN.md`** at the project root (written by the
optional `tiny-spec-breakdown` skill). If it exists and the user is creating one of
its stories, **seed from it instead of running the full interview** — confirm, don't
re-ask:

1. **Pick the story.** Ask which story (or infer from the user's request); match it
   to its `## Feature:` → `Story:` entry by slug or title.
2. **Slug + binding.** Use the story's **slug** for `.spec/<slug>/`. Take the ticket
   provider from the Decisions **Platform** and the **id** from the story's tracker
   parent or the user (ask for the id if the placeholder is still blank; omit the
   `ticket:` block entirely if the platform is ad-hoc).
3. **Requirements.** Promote the story's **`AC:` lines into `REQ-N`** — verbatim where
   already atomic; split any that hide two capabilities behind an "and".
4. **Constitution (first run only).** Seed `constitution.md` from the **`## Decisions`**
   block instead of interviewing stack/layout: Stack + Code-lives → **Style** and
   **Layout**; any verification hints → **Verification commands**; cross-cutting
   concerns → **Guiding invariants**. If `constitution.md` already exists, reuse it.
5. Confirm the captured `REQ-N` with the user, then write `SPEC.md` as below.

Only the **project-wide** questions collapse — still confirm this story's binding and
requirements. If there is **no `BREAKDOWN.md`**, or no entry matches, run the **full
interview** below unchanged.

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

Create `.spec/<slug>/`.

**One branch per ticket — how the active ticket is resolved.** Work for a ticket
lives on a branch named after the slug (e.g. `PROJ-123` or
`feature/PROJ-123-dark-mode`); downstream skills resolve the active ticket from the
branch name, so several tickets can be in flight on separate branches at once. If the
user isn't already on such a branch, create one (e.g. `git switch -c <slug>`) so the
new spec resolves by branch match.

## First run — scaffold

If `.spec/` does not exist:

1. Create `.spec/` and the active ticket dir `.spec/<slug>/` (on the ticket branch — see above).
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
requirements (resolve the active dir by branch match — see the resolution order
downstream skills use):

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
> change), re-run this skill on a new branch — it creates a new `.spec/<slug>/` that
> resolves by branch match. The shared `constitution.md` and `memory.md` carry over;
> the previous spec's artifacts stay untouched on disk.

## When done

Report the requirements captured and point the user at `tiny-spec-plan`.
