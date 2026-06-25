---
name: tiny-spec-build
description: Build the spec — run the per-task loop plan→implement→review→commit, one task at a time. Implements with a fresh executor, grades with an independent reviewer running the real gate, commits per passed task, keeps a lean memory. Resumes from the checkbox state.
---

# tiny-spec-build

The heart of the flow. Walks the active ticket's `tasks.md` top to bottom and runs each task through a
tight loop: **plan → implement → review → commit**. The constitution
(`constitution.md`) anchors every step; the thing that writes the code is never the
thing that grades it.

Artifacts live under `.spec/`: the **shared** constitution and memory at the root
(`.spec/constitution.md`, `.spec/memory.md`), the per-ticket `tasks.md`/`SPEC.md`/
`decisions.md` under `.spec/<ticket-id>/`. The memory template ships in this skill's
own `templates/` folder (alongside this file). The two subagents dispatched below
(`tiny-spec-build-executor`, `tiny-spec-build-reviewer`) are referenced by name — install them
alongside this skill (see the suite README).

## Inputs

1. **Resolve the active ticket dir** from the current git branch: the `.spec/<slug>/`
   whose slug matches the branch name (one branch per ticket). If none matches, use
   the sole ticket dir if there's exactly one; else ask which. Call it `<active>`.
2. Read `.spec/constitution.md` (**the shared constitution**), `.spec/memory.md` if
   it exists (**shared**), and `.spec/<active>/tasks.md`. The constitution + memory
   get injected **whole** into every executor and reviewer. Also note the `ticket`
   binding in `.spec/<active>/SPEC.md` — it supplies the commit `Refs:` footer.
3. Refuse to start if `tasks.md` is `status: stale` — tell the user to re-run
   `tiny-spec-tasks` to reconcile first.
4. Pick the **first unchecked `[ ]`** task. If all are `[x]`, jump to **Completion**.

## The per-task loop

For the selected task, run these steps in order. **Do not tick a task until its
reviewer passes.**

### 1. PLAN (inline, brief)
Restate the task as a 2–4 step micro-plan against the constitution: which
**invariants** apply, which files it touches, which **Definition of Done** items
and **Verification commands** it must satisfy. This is the executor's brief — keep
it short and concrete.

### 2. IMPLEMENT (dispatch `tiny-spec-build-executor`)
Spawn one **`tiny-spec-build-executor`** with a fresh, self-contained prompt:

- the task id, description, and **acceptance**;
- the `files:` hint;
- the **whole** `.spec/constitution.md`;
- the **whole** `.spec/memory.md` if it exists;
- only the specific existing files the task starts from, named explicitly (so it
  edits with the real current contents, not blind).

Do **not** pass the plan, sibling tasks, or other chatter. It returns a structured
report (`STATUS`, `CHANGES`, `DECISIONS`, `BLOCKER`). A `STATUS: blocked` →
**Blockers** below; do not proceed with this task.

### 3. REVIEW (dispatch `tiny-spec-build-reviewer` — independent)
Spawn one **`tiny-spec-build-reviewer`**, **blind to step 2**, with:

- the task id, description, and **acceptance**;
- the **whole** `.spec/constitution.md`;
- the list of changed files (from the executor's `CHANGES`) to read;
- the **Verification commands** from the constitution to run.

It runs the real gate end-to-end, checks the code against the constitution's
**Definition of Done** and **invariants**, confirms the **acceptance** actually
holds (exercised, not inferred), and returns `VERDICT: PASS | FAIL` + findings.

> Why independent: unit-green ≠ working, and the author is the worst judge of its
> own blind spots. The reviewer running the gate from a clean state is the
> safeguard that keeps scope and quality honest without an ownership contract.

### 4. CONVERGE (on FAIL)
Re-dispatch the **executor** with the reviewer's findings appended to its brief.
Bound this to **2 fix attempts**. If it still fails after that, stop and treat it
as a **blocker** (below) — don't keep grinding or hand-fix past the loop silently.

### 5. COMMIT + TICK (on PASS)
Two commits, in order (keeps code history clean of planning churn), both in
**Conventional Commits** format:

1. **Code commit** — stage only the source/test files the executor produced;
   message `<type>(<scope>): <task description>`. The **type** is the task's `type:`
   field, defaulting to `feat`; **scope** is optional (a component, or the ticket
   id). A breaking change uses `!` and/or a `BREAKING CHANGE:` footer.
2. **Bookkeeping commit** — tick the task `[x]` in `.spec/<active>/tasks.md` (bump
   `updated`), add any `decisions.md` entry; message `chore(spec): tick T<n>`.

**`Refs:` footer (ticket linking).** If `.spec/<active>/SPEC.md` has a `ticket`
binding, append a `Refs:` footer to **both** commits so the platform auto-links the
work (omit it entirely if there's no ticket). Always end with the `Co-Authored-By`
trailer:

```
<type>(<scope>): <description>

Refs: <ticket-ref>
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

Build `<ticket-ref>` from the binding's provider: Jira → `PROJ-123`,
GitHub → `#123`, ADO → `AB#123`, Monday → the item URL. The **closing** keyword
(`Closes #123`, `Fixes AB#123`) is reserved for the final / PR commit, **not** the
per-task commits.

Never commit a red gate. Never tick a task the reviewer did not pass.

### 6. DISTILL (memory)
If steps 2–4 surfaced a **forward-acting operational lesson** (a toolchain quirk,
a flaky/precondition gate, an abandoned approach, a fragile area), append a curated
entry to the **shared** `.spec/memory.md` (the root — lessons are project-wide) —
creating it from this skill's `templates/memory.template.md` on first use, and
pruning any entry the new one supersedes. Skip code-style rules (→ shared
`constitution.md`) and one-off history (→ the ticket's `decisions.md`). Keep it lean.

### 7. NEXT
Report the task outcome (built, reviewed, committed). Then:
- **Interactive default:** continue to the next unchecked task. Pausing for the
  user between tasks is fine and expected.
- If the user asked to **run it through** ("do it all", "build everything"), keep
  looping until done or a blocker stops you — committing per passed task as you go.

There is **no** separate autonomous mode and **no** checkpoint config: one commit
per passed task, always, on the current branch. (If the user wants a feature
branch, create it once up front — that's their call, not a knob here.)

## Blockers (never hack around)

When the executor reports `BLOCKER`, or convergence (step 4) exhausts its attempts:

1. Leave the task `[ ]`.
2. Log it to `.spec/<active>/decisions.md` using the fixed skeleton (`type: blocker`,
   naming the upstream doc to fix in `note:`, and the affected `REQ-N`/`T<n>` in
   `affects:`). Create the file if absent:

   ```
   ## D-NNN — <short title>
   - type: blocker
   - date: <ISO date>
   - affects: REQ-N, T<n>
   - note: <what stopped you; which upstream doc must change>
   ```
3. **Surface and route upstream:** `tiny-spec-plan` (a design gap) or `tiny-spec-create` (a
   requirement is wrong/impossible), in update mode. After the upstream fix and a
   `tiny-spec-tasks` reconcile, re-run `tiny-spec-build` — it resumes from the checkbox state.

A genuine fork the plan doesn't pin down → don't guess: present the options + your
recommendation, get the user's call, record it in `decisions.md`, then continue.

## Completion

When every task in `tasks.md` is `[x]`:

1. **Final smoke** — run the constitution's **Verification commands** once more
   against the whole project, exercised the way a user would (after the documented
   setup — install/build, not a test-runner shortcut). There is no separate
   verify skill — this final smoke confirms the requirements actually work end-to-end, not
   just that tasks are ticked.
2. **Report** — what was built, the commits made (with the branch), and any open
   `decisions.md` items (blockers, tasks unchecked by a reconcile). If the final
   smoke reveals a gap, it's a bug to fix now (new/edited task) or a blocker to
   route upstream — not a pass.
3. **Close the ticket (reference-only).** If a ticket is bound, this is where the
   **closing** keyword belongs — on the final / PR commit, not the per-task ones:
   GitHub `Closes #123`, ADO `Fixes AB#123`. Jira/Monday have no closing keyword,
   so move the ticket's status manually (active auto-transitions are an opt-in layer
   — see [INTEGRATIONS.md](INTEGRATIONS.md)). The suite makes **no API calls**.
