---
name: spec-plan
description: Turn .spec/SPEC.md into a technical design — produce PLAN.md and harden conventions.md (the constitution). Re-run in update mode to reconcile after a SPEC change.
---

# spec-plan

Decides **how** the requirements get built, and — just as important — hardens the
**constitution** (`conventions.md`) that every task will be implemented and
reviewed against.

All artifacts live under `.spec/` in the **project root**. The template ships in
this skill's own `templates/` folder (alongside this file). Requires
`.spec/SPEC.md`.

## Harden the constitution (`conventions.md`) — do this first

The constitution is the spine of the whole flow: it is injected whole into
every executor and reviewer. Make it strong and specific to *this* project, not
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
`.spec/PLAN.md` and fill it in:

- `## Approach` — the design narrative: the shape of the solution, key decisions,
  trade-offs. Detailed enough that `spec-tasks` can derive a task list from it.
  Optional `### Phase` headings are allowed for readability only.
- `## Requirement coverage` — map **every** `REQ-N` to where it's addressed. A
  requirement with no home is a gap: fix the approach or route back to
  `spec-create`.

Keep it proportional: a small change is a few paragraphs, not a phased epic.

## Update mode (SPEC changed → PLAN is stale)

When `PLAN.md` is `status: stale`:

1. Read the latest `decisions.md` change entry to see what moved.
2. Reconcile `PLAN.md` and `conventions.md` — adjust only what the change
   requires; preserve the rest.
3. Flip `tasks.md` to `status: stale` (if it exists) and extend the
   `decisions.md` entry.
4. Set `PLAN.md` `status: current`, bump `updated`.

## When done

Confirm the constitution is hardened and every `REQ-N` is covered, then point the
user at `spec-tasks`.
