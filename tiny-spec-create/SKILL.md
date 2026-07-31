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
`tasks.md`, `decisions.md`) live under `.spec/<slug>/`. The `SPEC.md` and
`constitution.md` skeletons are inline below — write them from there, no files to read.

## Pick your mode first — before doing anything else

This skill has three modes. **Decide which one you are in before you ask a single
question, create a directory, or touch git** — each mode forbids side effects the
others require, so getting here late means the damage is already done.

Check in this order; the first match wins:

| # | If | Mode | Go to |
|---|----|------|-------|
| 1 | `.spec/` exists but `.spec/constitution.md` does **not** | **reseed** | [Reseed a missing constitution](#reseed-a-missing-constitution) — repair only, then stop |
| 2 | `.spec/` does not exist | **fresh** (first run) | Seeded mode if `BREAKDOWN.md` exists, else Pick the slug → First run — scaffold → Write `SPEC.md` |
| 3 | the active ticket's `SPEC.md` already exists | **update** | [Update mode](#update-mode-re-run-on-an-existing-spec) — edit in place, never overwrite |
| 4 | otherwise (new ticket in an existing `.spec/`) | **fresh** (new ticket) | Seeded mode if `BREAKDOWN.md` exists, else Pick the slug → Write `SPEC.md` |

Rule 1 outranks everything, including **Seeded mode** — a missing constitution is a
repair, and repairs don't create work items. Rule 3 outranks rule 4 so that a re-run
on existing work can never overwrite it.

To evaluate rules 3 and 4 you need the **active ticket dir**. Resolve it **read-only**
first (see *Pick the slug* for the shared resolution order). Only *create* a dir once
you know you're in a fresh mode.

**If the user (or `tiny-spec-run`) says this is new work, skip the sole-dir fallback**
and go to rule 4. That fallback exists to find the ticket you're already on; letting
it match when someone asked for a *new* spec quietly retargets the run onto an old
ticket and marks its downstream artifacts stale for no reason.

## Reseed a missing constitution

Check this **before** anything else. The constitution is project-wide, so it can go
missing — deleted, or never committed — while a perfectly good `.spec/<slug>/` sits
next to it. Then it is unrecoverable: the scaffold below never fires, `tiny-spec-plan`
only *hardens* an existing one, and `tiny-spec-build` would inject nothing.

If `.spec/` exists but `.spec/constitution.md` does not, do **only** this:

1. Resolve the active ticket dir **read-only** — you may need its `SPEC.md`. There may
   be none; that's fine.
2. Write `.spec/constitution.md` using the skeleton in **First run — scaffold** below,
   filled in from whatever already exists, in this order of preference: a `BREAKDOWN.md`
   `## Decisions` block at the project root if there is one (Stack + Code-lives →
   **Style** and **Layout**; verification hints → **Verification commands**;
   cross-cutting → **Guiding invariants**), then `PRD.md`, then the active `SPEC.md`,
   then the codebase itself (its layout, test setup, and tooling). A *declared* source
   beats inference. Ask the user only what you genuinely cannot infer.
3. **Flag downstream work as unverified — across every ticket, not just the active
   one.** The constitution is project-wide, so *any* `[x]` task in *any* `.spec/*/`
   was built and reviewed against a document that did not exist. For each ticket dir
   whose `tasks.md` has checked tasks, set it `status: stale` and log a
   `decisions.md` entry in that ticket (`type: change`) saying the constitution was
   reseeded and the completed tasks were never checked against it. A constitution
   change makes tasks stale — and a reseed is the largest such change there is.
4. Report what you seeded, say plainly that it was **inferred and needs review** (it
   gets injected whole into every executor and reviewer, so a wrong Verification
   commands block silently corrupts every future gate), note that `SPEC.md`/`PLAN.md`
   and the branch were left untouched, and point the user at `tiny-spec-plan` to
   harden it. Then stop.

Do **not** run the interview, create a ticket dir, switch branches, or touch
`SPEC.md`. This is a repair, not a new spec. If the user also wants new work, that's
a separate run of this skill.

## Seeded mode (`BREAKDOWN.md` present)

**Fresh modes only** — reseed (rule 1) and update (rule 3) both outrank this.


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

**Fresh modes only** — in reseed or update mode the active dir already exists and you
resolve it read-only, as above. Do not run this section.

**If a ticket dir already resolves for the current branch, reuse it — don't invent a
new slug.** Asking for a slug when `.spec/PROJ-123/` already matches the branch is how
you end up with both `PROJ-123/` and `dark-mode/` matching `feature/PROJ-123-dark-mode`,
which makes the ticket permanently ambiguous for every downstream skill.

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
3. Seed the **shared constitution** at `.spec/constitution.md` (the **root**, not the
   ticket dir — it is project-wide), filling in what the interview already told
   you (Style, Layout, Verification commands at minimum). Leave the rest for
   `tiny-spec-plan` to harden — but never leave a section empty of intent. If
   `constitution.md` already exists (a prior ticket created it), **reuse it** — do
   not overwrite the project's constitution. Write it with this structure (drop the
   indentation when you write the file):

   ```markdown
   # Constitution

   > This is the strongest, most persistent document in the project. It is
   > **project-wide** — it lives at the `.spec/` root and anchors *every* ticket, not
   > any one of them. Every task is implemented and reviewed against it. Keep it true;
   > keep it lean. Project-specific richness belongs here — not scattered across tasks.

   ## Style
   <Formatting, naming, language idioms. The defaults a reader should assume.>

   <!-- conditional: the one section that may be omitted entirely. Include it only if
        this project has a visual surface; a CLI, library, or headless service should
        not carry a dead design heading. -->
   ## Design system
   <The project-wide UI contract, written as **named tokens** — never raw values. Every
   screen description and every line of UI code references these names, so a redesign
   edits one table instead of every file. Name them DTCG-style (`color.surface.raised`,
   `space.4`) so a token pipeline costs nothing to adopt later.
   - color:     <semantic roles → value, e.g. `color.surface.base` #FFFFFF, `color.text.muted` #6B7280>
   - space:     <one scale, e.g. `space.1`=4px … `space.8`=32px. A value off the scale is a violation.>
   - type:      <named steps → size/weight/line-height, e.g. `type.heading.lg` 24px/600/1.25>
   - radius:    <named steps, same rule>
   - elevation: <named steps, same rule>
   - states:    <what every interactive surface must define — default, hover, focus,
     disabled, loading, empty, error>
   >

   ## Engineering standards
   <Error handling, logging, testing approach, dependency policy, what "tested" means here.>

   ## Guiding invariants
   <The non-negotiables. "Never X." "Always Y." The rules a reviewer can fail a task on.>

   ## Glossary
   <Domain term — one-line definition. Keep the team speaking one language.>

   ## Layout
   <Where things live. Directory map. Where new code of each kind goes.>

   ## Definition of Done
   <The bar a task must clear to be checked off: e.g. code + tests + docs updated,
   gate green, no TODOs left, matches the invariants above.>

   ## Verification commands
   <The exact gate. The reviewer runs these. Example:
   - install: `...`
   - lint:    `...`
   - test:    `...`
   - build:   `...`
   - run:     `...`
   - visual:  `...`   # optional; only if there is a Design system above. The command
     that boots the UI so the reviewer can read back computed styles and geometry
     (e.g. a Playwright script that navigates to a route and prints
     getComputedStyle/getBoundingClientRect for the selectors it is given). Required
     before any task may carry a `design:` reference — a task that names one with no
     `visual:` command here is a blocker, not a silent pass.
   >
   ```

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

Write `.spec/<slug>/SPEC.md` with the structure below, filling it in:

```markdown
---
status: current
updated: <ISO date>
# Ticket binding (reference-only). Omit this whole block if there is no ticket.
ticket:
  provider: jira | github | ado | monday
  id: <PROJ-123 | #42 | AB#77 | item id>
  url: <link to the ticket>
  status: <optional manual mirror of the platform status, e.g. In Progress>
---

# <Project / feature name>

<!-- optional: omit if N/A -->
## Context

<Why now — the background, the problem, what prompted this. No solution detail.>

## Intent

<One paragraph: what this is and why it exists. The "what" and "why", never the "how".>

## Requirements

<Each REQ is one user-observable, testable capability. No implementation detail.
If a line hides two capabilities behind an "and", split it.>

- REQ-1 — <capability>
- REQ-2 — <capability>
- REQ-3 — <capability>

<!-- optional: omit if this ticket has no visual surface -->
## Design

<One `D<n>` entry per screen or surface this ticket touches. `layout`, `elements`, and
`states` may reference **only** token names defined in the constitution's Design
system — a raw value here (`24px`, `#3B82F6`) is a violation, because it is how
per-screen drift starts. Keep the source and export lines even when a design is
view-only: they are the provenance, and the sha256 is the staleness signal.

The `elements:` selectors are a **contract the code must match verbatim** — the
reviewer measures exactly these. Prefer a stable test id over a CSS class; classes get
renamed by refactors and mangled by CSS-in-JS, and a selector that silently stops
matching is the exact failure this prevents.>

- D1 — <screen / surface name>
  - source: <Figma URL#node-id, or the tool of record; "view-only" if you can't export from it>
  - export: design/<file>.png            # the committed artifact the reviewer can actually read
  - sha256: <hash of that export>        # changes when the design changes → this SPEC goes stale
  - layout: <the arrangement and the order — e.g. "single centered column, max 420px;
    title → field → error → submit". This is what the reviewer checks geometry against.>
  - elements:
    - <name>  `<selector>`  → <the tokens this element must satisfy>
    - <name>  `<selector>`  → <…>
  - states: <which of empty / loading / error / success this surface must render, and what each shows>

<!-- optional: omit if N/A -->
## Non-goals

<What this explicitly does NOT cover — scope boundaries that prevent creep.>

<!-- optional: omit if N/A -->
## Success criteria

<How we'll know the whole spec succeeded, beyond the per-requirement acceptance —
e.g. a metric, an end-to-end scenario, a stakeholder sign-off.>

<!-- optional: omit if N/A -->
## Open questions

<Unresolved questions that may change requirements. Resolve before/while planning.>

<!-- optional: omit if N/A -->
## Links

<Ticket, related specs, design docs, prior art.>
```

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

4. **Completed-work guardrail.** If a changed `REQ-N` is delivered by a task already
   `[x]` in `tasks.md` (follow its `req:` field), **uncheck it** and name the
   unchecked ids in the same `decisions.md` entry. `tiny-spec-build` resumes from the
   checkbox state, so a task left `[x]` is a task it will never revisit — never assume
   built work survived a requirement change.
5. Set `SPEC.md` `status: current` and bump `updated`. **Do this even if it was
   already `current`.** `SPEC.md` is the root of the chain and no other skill in the
   suite writes that flag, so a hand-edited `stale` SPEC is otherwise unclearable and
   the chain jams at the root — `tiny-spec-plan` and `tiny-spec-tasks` both clear their
   own flag this way; this one was the gap.

Tell the user which downstream docs went stale and to re-run `tiny-spec-plan` to
reconcile.

> **New spec?** To start a different piece of work (a new ticket or an ad-hoc
> change), re-run this skill on a new branch — it creates a new `.spec/<slug>/` that
> resolves by branch match. The shared `constitution.md` and `memory.md` carry over;
> the previous spec's artifacts stay untouched on disk.

## When done

Report the requirements captured and point the user at `tiny-spec-plan`.
