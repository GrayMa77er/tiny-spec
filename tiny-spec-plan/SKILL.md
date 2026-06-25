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
`.spec/<ticket-id>/`. **Resolve the active ticket dir** from `.spec/ACTIVE` (if it's
absent and exactly one ticket dir exists, use it; if several exist, ask which). The
template ships in this skill's own `templates/` folder (alongside this file).
Requires `.spec/<active>/SPEC.md`.

## Harden the constitution (`constitution.md`) — do this first

The constitution is the spine of the whole flow and **project-wide** — it lives at
`.spec/constitution.md` (the root, shared across every ticket), and is injected whole
into every executor and reviewer. Make it strong and specific to *this* project, not
generic boilerplate. Fill in / sharpen all seven sections:

1. **Style** · 2. **Engineering standards** · 3. **Guiding invariants** ·
4. **Glossary** · 5. **Layout** · 6. **Definition of Done** ·
7. **Verification commands**.

Two sections carry the most weight — get them right:
- **Guiding invariants** — the non-negotiables a reviewer can *fail a task on*.
  Be concrete ("all timestamps are UTC ISO-8601", "no network calls in unit
  tests"), not aspirational ("write clean code").
- **Verification commands** — the exact, runnable gate (install → lint → test →
  build → run). The reviewer executes these literally, so they must actually work
  from a clean checkout. If setup is needed (e.g. install the package first), say
  so explicitly.

## Write `PLAN.md`

Copy this skill's `templates/PLAN.template.md` to
`.spec/<active>/PLAN.md` and fill it in:

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
