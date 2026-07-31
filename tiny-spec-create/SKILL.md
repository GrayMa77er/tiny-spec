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
5. **Designs.** If the story carries `design:` paths, run the **Designs** section
   below against exactly those files — read them, seed or reuse the constitution's
   **Design system**, and write this story's `D<n>` entries. The breakdown named the
   files; it did not describe them, so you still have to open them.
6. Confirm the captured `REQ-N` with the user, then write `SPEC.md` as below.

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

## Designs (only if this project has a visual surface)

Wireframes and mockups are worth nothing to a build agent as loose files — they get
read once and forgotten. This section turns them into two durable things: a
**project-wide token system** in the constitution, and a **per-screen `D<n>` entry**
in `SPEC.md`. Skip the whole section for a CLI, library, or headless service.

1. **Find and read them.** Look for a `design/` directory at the project root (also
   accept paths the user hands you). **Actually read every file** — `Read` renders
   images, so look at the PNG/JPG/SVG, open the HTML mockup, read the Excalidraw.
   A design you did not open cannot be described, and a guessed description is worse
   than none because it reads as authoritative.

2. **First run only — propose the token system, don't measure it.** Read *all* the
   designs together and infer **one coherent scale** across them: semantic color
   roles, a single spacing step, a type scale, radii, elevation. Do **not** measure
   each screen and record its pixels — image-derived per-screen values are unreliable
   and produce no shared vocabulary. Snapping ragged wireframe values onto a clean
   scale is the point, not a loss of fidelity. Present the proposed system for
   approval, note anything you had to round, then fill in the constitution's
   **Design system** section. If the constitution already has one, **reuse it** —
   describe this ticket's screens in the existing tokens and flag any screen that
   genuinely needs a new token rather than inventing one silently.

3. **Ask for the `visual:` command** — how the reviewer boots this UI to read back
   computed styles (a Playwright script, a dev-server URL plus a snippet). Record it
   in **Verification commands**. Without it no task can carry a `design:` reference.

4. **Write one `D<n>` entry per screen this ticket touches**, with the source link,
   the committed export path, and its `sha256` (`shasum -a 256 <file>` — this is the
   staleness signal, so compute it, never invent it). Describe layout, elements, and
   states in **token names only**.

   **`elements:` is the part that makes the gate work, so give each one a selector.**
   The reviewer measures exactly the selectors you name; without them it has to guess
   which node is "the error line", and a wrong guess measures the wrong element and
   passes. Prefer a **stable test id** (`[data-testid="signup-email"]`) over a CSS
   class — classes get renamed by refactors and mangled by CSS-in-JS, and a selector
   that silently stops matching is the exact failure this is meant to prevent.

   List the elements the design actually constrains — the ones whose spacing, type,
   or color you'd notice being wrong. A wrapper `<div>` nobody can see does not need
   a row. Five to ten rows describes most screens; if you're past fifteen, the screen
   is probably two `D<n>` entries.

   **`layout:` carries the arrangement**, which no per-element row can express: the
   structure (single column, 3-col grid, sidebar + main), the max width, and the
   **order** elements appear in. This is what the reviewer compares geometry against.

5. **Link the requirements.** A `REQ-N` that this design bears on names its screen —
   `REQ-3 — the signup form validates email inline (D1)`. That is what makes
   `frame → REQ → task → files` greppable in both directions.

If the PRD/intent and a design **disagree**, do not silently pick one. Say what each
says, ask which wins, and record the answer in the `D` entry or `## Open questions`.

## Write `SPEC.md`

Copy this skill's `templates/SPEC.template.md` to `.spec/<slug>/SPEC.md` and fill
it in:

- the **ticket binding** frontmatter block (or omit it if there's no ticket);
- a one-paragraph **intent**;
- a `## Requirements` list — each `REQ-N` a single **user-observable, testable**
  capability with **no implementation detail** ("the CLI accepts a `--json` flag
  and prints valid JSON", not "add a json module");
- a `## Design` list — one `D<n>` per screen this ticket touches, if it has a visual
  surface (see **Designs** above). Omit the section entirely if it doesn't;
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
1b. **If there is a `## Design` section, re-hash every export** (`shasum -a 256`) and
   compare with the recorded `sha256`. A mismatch means the design moved under the
   spec: re-read that export, update the entry's layout/elements/states and hash, and
   treat it as a change like any other (steps 2–3 below). A **missing** export file is
   a broken anchor — say so loudly and stop rather than leaving an entry that points
   at nothing; a link that fails silently is worse than no link.

   This is also the entry point when designs arrive **after** the spec was written:
   run this skill in update mode, work through the **Designs** section above, and the
   screens get anchored without redoing the requirements.
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
