---
name: tiny-spec-plan
description: Turn the active ticket's SPEC.md into a technical design — produce PLAN.md and harden the shared constitution.md (the constitution). Re-run in update mode to reconcile after a SPEC change.
---

# tiny-spec-plan

Decides **how** the requirements get built, and — just as important — hardens the
**constitution** (`constitution.md`) that every task will be implemented and
reviewed against.

Artifacts live under `.spec/`: the **shared** constitution at the root
(`.spec/constitution.md`), the per-ticket `SPEC.md`/`PLAN.md` under
`.spec/<ticket-id>/`. **Resolve the active ticket dir** from the current git branch:
the `.spec/<slug>/` whose slug matches the branch name (one branch per ticket). If
none matches, use the sole ticket dir if there's exactly one; else ask which. The
`PLAN.md` skeleton is inline below — write it from there, no file to read.
Requires `.spec/<active>/SPEC.md`.

**Two cases pre-empt that order — ask instead of applying it:** more than one dir
matches the branch (there is no defined tie-break, and inventing one here would
silently disagree with every other skill), or ticket dirs exist while you are on
`main`/`master` with no name match (the usual cause is a forgotten `git switch`, and
the sole-dir fallback would otherwise swallow it). Detached HEAD or no git repo is a
**degraded** case, not an ask case — branch match is simply unavailable, so fall
through to sole-dir and ask as written.

## Harden the constitution (`constitution.md`) — do this first

The constitution is the spine of the whole flow and **project-wide** — it lives at
`.spec/constitution.md` (the root, shared across every ticket), and is injected whole
into every executor and reviewer. Make it strong and specific to *this* project, not
generic boilerplate. Fill in / sharpen all seven fixed sections:

1. **Style** · 2. **Engineering standards** · 3. **Guiding invariants** ·
4. **Glossary** · 5. **Layout** · 6. **Definition of Done** ·
7. **Verification commands**.

Plus **Design system** — the one *conditional* section. Present only when the project
has a visual surface; leave it absent otherwise rather than filling it with filler.

Two sections carry the most weight — get them right:
- **Guiding invariants** — the non-negotiables a reviewer can *fail a task on*.
  Be concrete ("all timestamps are UTC ISO-8601", "no network calls in unit
  tests"), not aspirational ("write clean code").
- **Verification commands** — the exact, runnable gate (install → lint → test →
  build → run). The reviewer executes these literally, so they must actually work
  from a clean checkout. If setup is needed (e.g. install the package first), say
  so explicitly.

**Harden the Design system if there is one.** `tiny-spec-create` seeds it by inferring
a scale from the wireframes; your job is to make it enforceable:

- **Every token needs a concrete value.** "a consistent spacing scale" fails nothing.
  `space.1`=4px … `space.8`=32px fails a `padding: 19px`. A token with no value is
  worse than no token, because it looks like a contract and isn't one.
- **Check the `SPEC.md` `D<n>` entries resolve.** Every token a screen names must
  exist here. An entry naming `color.accent.primary` when the system defines no such
  token is a broken anchor — add the token or fix the entry, don't leave it dangling.
- **Sanity-check the `elements:` selectors against the codebase you're planning for.**
  They are a contract the code must match verbatim, so a selector that assumes markup
  this project can't produce (a class a component library owns and mangles, an id that
  collides) becomes a build-time blocker. Prefer stable test ids, and say in the
  `## Approach` where they get added.
- **Confirm the `visual:` command actually runs.** It is the gate for every task
  carrying `design:`; an aspirational command means the visual gate silently never
  fires. If it doesn't work from a clean checkout, fix it or drop the `design:` refs.
- Add the scale as a **guiding invariant** where it matters ("no raw color or spacing
  values in UI code — reference a token"), since that is the line a reviewer fails on.

## Write `PLAN.md`

Write `.spec/<active>/PLAN.md` with the structure below, filling it in:

```markdown
---
status: current
updated: <ISO date>
---

# Plan — <project / feature name>

## Approach

<The design narrative: how the requirements will be met. Key decisions, the shape
of the solution, notable trade-offs. Enough that someone could derive the tasks
from it. Optional `### Phase` headings are fine for readability — they do NOT
parallelize or gate anything.>

<!-- optional: omit if N/A -->
## Architecture

<The moving parts and how they fit: components, data flow, key interfaces or
modules. A small diagram or bullet map is fine. Skip for changes too small to need it.>

## Requirement coverage

<Every REQ-N maps to where it's addressed. No requirement left unaddressed.>

- REQ-1 — <where/how addressed>
- REQ-2 — <where/how addressed>
- REQ-3 — <where/how addressed>

<!-- optional: omit if N/A -->
## Risks & mitigations

<What could go wrong (technical risk, unknowns, fragile areas) and how the plan
de-risks it.>

<!-- optional: omit if N/A -->
## Test strategy

<How the work will be verified beyond the constitution's gate — what to test, at
what level, and any fixtures/data needed.>

<!-- optional: omit if N/A -->
## Open questions

<Design questions still unresolved. A question that blocks tasks must be answered
here or routed back to tiny-spec-create before tiny-spec-tasks runs.>
```

- `## Approach` *(required)* — the design narrative: the shape of the solution, key
  decisions, trade-offs. Detailed enough that `tiny-spec-tasks` can derive a task list
  from it. Optional `### Phase` headings are allowed for readability only.
- `## Requirement coverage` *(required)* — map **every** `REQ-N` to where it's
  addressed. A requirement with no home is a gap: fix the approach or route back to
  `tiny-spec-create`.
- Optional sections (`Architecture`, `Risks & mitigations`, `Test strategy`,
  `Open questions`) where they add value — omit any that don't apply.

Keep it proportional: a small change is a few paragraphs, not a phased epic.

## Update mode (SPEC changed → PLAN is stale)

When `PLAN.md` is `status: stale`:

1. Read the latest `.spec/<active>/decisions.md` change entry to see what moved.
2. Reconcile `.spec/<active>/PLAN.md` and the shared `.spec/constitution.md` — adjust
   only what the change requires; preserve the rest.
3. Flip `.spec/<active>/tasks.md` to `status: stale` (if it exists) and extend the
   `decisions.md` entry.
4. Set `PLAN.md` `status: current`, bump `updated`.

## When done

Confirm the constitution is hardened and every `REQ-N` is covered, then point the
user at `tiny-spec-tasks`.
