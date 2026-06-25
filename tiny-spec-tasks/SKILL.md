---
name: tiny-spec-tasks
description: Slice the active ticket's PLAN.md into tasks.md — a flat, ordered checklist of small tasks, each with an acceptance outcome. Executed sequentially by tiny-spec-build. Re-run in update mode to reconcile after a plan change.
---

# tiny-spec-tasks

Turns the plan into `tasks.md`: a **flat, ordered checklist** of small, concrete
tasks. No waves, no parallelism, no `owns:` contracts — tasks run one at a time,
top to bottom.

Artifacts live under `.spec/`; `PLAN.md` and `tasks.md` are per-ticket. **Resolve
the active ticket dir** from the current git branch: the `.spec/<slug>/` whose slug
matches the branch name (one branch per ticket). If none matches, use the sole
ticket dir if there's exactly one; else ask which. The template ships in this skill's own
`templates/` folder (alongside this file). Requires `.spec/<active>/PLAN.md`.

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
  - type: feat            # optional; Conventional Commit type (defaults to feat)
  - req: REQ-n            # optional; the REQ-N this task delivers
  - files: <comma-separated hint of files it will touch>
```

The **acceptance** is what the reviewer checks against — make it observable
("`spec --version` prints the version and exits 0"), not internal ("version logic
added"). **type** picks the Conventional Commit type `tiny-spec-build` uses for this
task's code commit (`feat | fix | docs | refactor | test | chore | build | ci | perf | style`);
set it when the task is clearly not a feature (e.g. `fix`, `docs`, `refactor`),
otherwise omit and it defaults to `feat`. **req** ties the task to the requirement
it satisfies (traceability). The **files** line is a hint to focus the executor and
reviewer; it is not enforced, so approximate paths are fine.

Cover **every** part of the approach — together the tasks must deliver all
`REQ-N`. Don't leave a requirement with no task.

## Write `tasks.md`

Copy this skill's `templates/tasks.template.md` to
`.spec/<active>/tasks.md`, fill in the `## Tasks` checklist with all tasks `[ ]`
unchecked, set frontmatter `status: current`, `updated: <today>`.

## Update mode (PLAN changed → tasks are stale)

When `tasks.md` is `status: stale`:

1. Read the latest `.spec/<active>/decisions.md` change entry.
2. Reconcile — add/alter/remove tasks to match the new plan, preserving existing
   `T<n>` ids where the task still exists; new tasks get the next free id.
3. **Completed-work guardrail:** if a change touches a task already `[x]`,
   **uncheck it** (`[ ]`) and record the unchecked ids in
   `.spec/<active>/decisions.md` for human review, using the fixed skeleton. Never
   assume built work survived.

   ```
   ## D-NNN — <short title>
   - type: change
   - date: <ISO date>
   - affects: T<n>, T<m>
   - note: <which tasks were unchecked and why>
   ```
4. Set `status: current`, bump `updated`.

## When done

Report the task count and point the user at `tiny-spec-build` (one task at a time) or
note they can run it straight through.
