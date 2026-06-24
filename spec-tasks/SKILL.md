---
name: spec-tasks
description: Slice .spec/PLAN.md into tasks.md — a flat, ordered checklist of small tasks, each with an acceptance outcome. Executed sequentially by spec-build. Re-run in update mode to reconcile after a plan change.
---

# spec-tasks

Turns the plan into `tasks.md`: a **flat, ordered checklist** of small, concrete
tasks. No waves, no parallelism, no `owns:` contracts — tasks run one at a time,
top to bottom.

All artifacts live under `.spec/` in the **project root**. The template ships in
this skill's own `templates/` folder (alongside this file). Requires
`.spec/PLAN.md`.

## Slice the plan into tasks

Walk the `## Approach` in `PLAN.md` and break it into tasks. Each task is:

- **Small and independently checkable** — one slice a single executor can finish
  and a reviewer can grade in one pass. If you can't write a one-line acceptance
  for it, it's too big — split it.
- **Ordered so each builds on the last.** Tasks run sequentially, so a later task
  may freely assume an earlier task's code already exists. Put foundational work
  (types, schema, scaffolding) first. Order by dependency, not by guesswork.
- **Right-sized, not fragmented.** Don't split a cohesive change into five files'
  worth of micro-tasks just to look granular. Earned ceremony: fewer, meaningful
  tasks beat many trivial ones.

For each task, write:

```
- [ ] T<n> — <imperative description>
  - acceptance: <one user-observable outcome that proves it's done>
  - files: <comma-separated hint of files it will touch>
```

The **acceptance** is what the reviewer checks against — make it observable
("`spec --version` prints the version and exits 0"), not internal ("version logic
added"). The **files** line is a hint to focus the executor and reviewer; it is
not enforced, so approximate paths are fine.

Cover **every** part of the approach — together the tasks must deliver all
`REQ-N`. Don't leave a requirement with no task.

## Write `tasks.md`

Copy this skill's `templates/tasks.template.md` to
`.spec/tasks.md`, fill in the `## Tasks` checklist with all tasks `[ ]`
unchecked, set frontmatter `status: current`, `updated: <today>`.

## Update mode (PLAN changed → tasks are stale)

When `tasks.md` is `status: stale`:

1. Read the latest `decisions.md` change entry.
2. Reconcile — add/alter/remove tasks to match the new plan, preserving existing
   `T<n>` ids where the task still exists; new tasks get the next free id.
3. **Completed-work guardrail:** if a change touches a task already `[x]`,
   **uncheck it** (`[ ]`) and record the unchecked ids in `decisions.md`
   (`type: change`) for human review. Never assume built work survived.
4. Set `status: current`, bump `updated`.

## When done

Report the task count and point the user at `spec-build` (one task at a time) or
note they can run it straight through.
