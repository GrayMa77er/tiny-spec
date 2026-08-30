---
name: tiny-spec-build
description: Build the spec — run the per-task loop plan→implement→review→commit, one task at a time. Implements with a fresh executor, grades with an independent reviewer running the real gate, commits per passed task, keeps a lean memory. Halts on a blocker, a spent convergence budget, a task's pause: point, or a genuine fork, and names which. Resumes from the checkbox state.
---

# tiny-spec-build

The heart of the flow. Walks the active ticket's `tasks.md` top to bottom and runs each task through a
tight loop: **plan → implement → review → commit**. The constitution
(`constitution.md`) anchors every step; the thing that writes the code is never the
thing that grades it.

Artifacts live under `.spec/`: the **shared** constitution and memory at the root
(`.spec/constitution.md`, `.spec/memory.md`), the per-ticket `tasks.md`/`SPEC.md`/
`decisions.md` under `.spec/<ticket-id>/`. The `memory.md` skeleton is inline below —
write it from there, no file to read. The two subagents dispatched below
(`tiny-spec-build-executor`, `tiny-spec-build-reviewer`) are referenced by name — install them
alongside this skill (see the suite README).

## Inputs

1. **Resolve the active ticket dir** from the current git branch: the `.spec/<slug>/`
   whose slug matches the branch name (one branch per ticket). If none matches, use
   the sole ticket dir if there's exactly one; else ask which. Call it `<active>`.
   **Two cases pre-empt that order — ask instead of applying it:** more than one dir
   matches the branch (there is no defined tie-break, and inventing one here would
   silently disagree with every other skill), or ticket dirs exist while you are on
   `main`/`master` with no name match (the usual cause is a forgotten `git switch`, and
   the sole-dir fallback would otherwise swallow it). Detached HEAD or no git repo is a
   **degraded** case, not an ask case — branch match is simply unavailable, so fall
   through to sole-dir and ask as written.
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

**Before step 1, check the task's `pause:` field.** If it has one and the user hasn't
waived it for this run, **halt `paused`** (see **Halting** below): leave the task
`[ ]`, dispatch nothing, and don't touch `tasks.md`. A pause stops *before* the work so
the approach gets reviewed while redirecting it is still cheap.

A pause can be waived or added for the current run only, conversationally — "skip the
pause on T5", "also stop before T9". Honor it for this run and **never write it back
into `tasks.md`**: the file records the standing intent, not one run's override.

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
- **if the task has a `design:` field** — that `D<n>` entry copied verbatim from
  `.spec/<active>/SPEC.md` plus its `export:` path, so the executor can look at the
  design instead of guessing at it;
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
- the **Verification commands** from the constitution to run;
- **if the task has a `design:` field** — the same `D<n>` entry and `export:` path
  you gave the executor, so it grades against the contract rather than its taste.

It runs the real gate end-to-end, checks the code against the constitution's
**Definition of Done** and **invariants**, confirms the **acceptance** actually
holds (exercised, not inferred), and returns `VERDICT: PASS | FAIL` + findings.
On a `design:` task it also runs the constitution's `visual:` command, measures the
selectors the `D<n>` names against the Design system tokens, exercises the states it
names, and finally **looks at the render beside the design export** — catching what
numbers can't reach, like an element that measures perfectly and shows up invisible.
It fails on what it measured or saw, and merely flags what is taste.

> Why independent: unit-green ≠ working, and the author is the worst judge of its
> own blind spots. The reviewer running the gate from a clean state is the
> safeguard that keeps scope and quality honest without an ownership contract.

### 4. CONVERGE (on FAIL)
Re-dispatch the **executor** with the reviewer's findings appended to its brief.
Bound this to **2 fix attempts**. If it still fails after that, stop and **halt
`exhausted`** (see **Halting** below) — don't keep grinding or hand-fix past the loop
silently. `exhausted` is recorded as a blocker, because a task that three attempts
couldn't turn green is a signal the upstream document is wrong — but name it
`exhausted`, not `blocked`: the executor never said it couldn't proceed, it just
never got there.

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
pruning any entry the new one supersedes. Skip code-style rules (→ shared
`constitution.md`) and one-off history (→ the ticket's `decisions.md`). Keep it lean.

On first use, create the file with this structure:

```markdown
# Memory — operational lessons

> Curated, forward-acting lessons that should survive across runs so the blind
> executor and reviewer don't re-learn them. **Project-wide** — lives at the
> `.spec/` root and is shared across every ticket. NOT a changelog. Prune superseded
> entries. Code-style rules belong in `constitution.md`; one-off history in the
> ticket's `decisions.md`.

<!-- Each entry:
- type: environment | pitfall | tried-rejected | hotspot
  lesson: <one line — the operational fact>
  apply:  <one line — why it matters / what to do about it>
-->

- type: environment
  lesson: <e.g. the test suite needs the package installed (`pip install -e .`) first>
  apply:  <run the documented setup before the gate; a bare `pytest` gives a false red>
```

### 7. NEXT
Report the task outcome (built, reviewed, committed). Then:
- **Interactive default:** continue to the next unchecked task. Pausing for the
  user between tasks is fine and expected.
- If the user asked to **run it through** ("do it all", "build everything"), or
  `tiny-spec-loop` invoked you, keep looping until one of the five terminal states
  below is reached — committing per passed task as you go.

**The task list is the budget.** The loop ends when the tasks end. There is no turn
ceiling, no token cap, and no max-tasks knob to set — adding one would put a second,
weaker stopping rule next to the real one.

There is **no** separate autonomous mode and **no** checkpoint config: one commit
per passed task, always, on the current branch. (If the user wants a feature
branch, create it once up front — that's their call, not a knob here.) Running
through is a caller's instruction, not a mode — every step above is identical either
way, which is why a loop and a hand-driven build can't drift apart.

## Halting

Every build run ends in exactly **one** of five terminal states. Name it out loud in
the closing report:

| State | Cause |
|---|---|
| `done` | every task `[x]` and the final smoke passed |
| `blocked` | the executor reported a `BLOCKER`, or the reviewer found a missing `visual:` command |
| `exhausted` | convergence (step 4) spent its 2 fix attempts and the task is still red |
| `paused` | a task's `pause:` point was reached |
| `fork` | a genuine either/or the plan doesn't pin down |

**Never round up.** Only `done` may report the work as built. A run that ended at
`blocked`, `exhausted`, `paused`, or `fork` has unbuilt work in it, and a closing
report that calls it done is worse than the halt itself — it converts a stop the user
could act on into a false completion they won't check. Say the state, then say what's
left and which command resolves it.

**`blocked` and `exhausted`** log **one** entry with `type: blocker` — an upstream doc
must change; see **Blockers** below. **`fork`** logs `type: halt`:

```
## D-NNN — <short title>
- type: halt
- state: fork
- date: <ISO date>
- affects: REQ-N, T<n>
- note: <the options, your recommendation, and what the user has to decide>
```

Write one entry per halt, not one per cause — a blocker that halts the loop is a single
event and reads as two records if you log it twice.

**`done` and `paused` log nothing.** A green tree with every box ticked already says
`done`. And a `paused` run stopped at a task whose `pause:` line is sitting right there
in `tasks.md` saying why — an entry would restate what the file already tells you, and
the log is for things that aren't otherwise visible. Report it, don't record it.

The task the loop stopped at stays `[ ]`. That is the whole resume mechanism:
re-running `tiny-spec-build` (or `tiny-spec-loop`) picks up at exactly that task with no
conversational context needed.

## Blockers (never hack around)

When the executor reports `BLOCKER`, when the reviewer reports a **missing `visual:`
command** for a `design:` task, or when convergence (step 4) exhausts its attempts:

1. Leave the task `[ ]`.
2. Log it to `.spec/<active>/decisions.md` using the fixed skeleton (`type: blocker`,
   the terminal state in `state:`, the upstream doc to fix named in `note:`, and the
   affected `REQ-N`/`T<n>` in `affects:`). Create the file if absent:

   ```
   ## D-NNN — <short title>
   - type: blocker
   - state: blocked
   - date: <ISO date>
   - affects: REQ-N, T<n>
   - note: <what stopped you; which upstream doc must change>
   ```

   `state:` is `blocked` for an executor blocker or a missing `visual:`, and
   `exhausted` when convergence ran out. Both route upstream the same way; the
   distinction is what the user reads to know whether the task was impossible or just
   never converged.
3. **Surface and route upstream:** `tiny-spec-plan` (a design gap, a missing `visual:`
   command, or a token the Design system doesn't define) or `tiny-spec-create` (a
   requirement is wrong/impossible), in update mode. Never resolve a missing `visual:`
   command by dropping the task's `design:` field — that turns a gap in the gate into
   a task that quietly claims a check it never got. After the upstream fix and a
   `tiny-spec-tasks` reconcile, re-run `tiny-spec-build` — it resumes from the checkbox state.

A genuine fork the plan doesn't pin down → don't guess: present the options + your
recommendation, get the user's call, record it in `decisions.md`, then continue.

**When running through, a fork is a halt** (`type: halt`, `state: fork`) — record the
options and your recommendation in the `note:` and stop, rather than blocking on an
answer nobody may be present to give. Ask only when the user is in the conversation
with you; a question asked into an empty room stalls the run without ending it, and
the halt is what makes the same fork readable hours later.

## Completion

When every task in `tasks.md` is `[x]`:

1. **Final smoke** — run the constitution's **Verification commands** once more
   against the whole project, exercised the way a user would (after the documented
   setup — install/build, not a test-runner shortcut). There is no separate
   verify skill — this final smoke confirms the requirements actually work end-to-end, not
   just that tasks are ticked.
2. **Report** — the terminal state by name (`done` here, since every task is `[x]`
   and the smoke passed), what was built, the commits made (with the branch), and any
   open `decisions.md` items (blockers, tasks unchecked by a reconcile). If the final
   smoke reveals a gap, it's a bug to fix now (new/edited task) or a blocker to
   route upstream — **not** a pass, and not `done`.
3. **Close the ticket (reference-only).** If a ticket is bound, this is where the
   **closing** keyword belongs — on the final / PR commit, not the per-task ones:
   GitHub `Closes #123`, ADO `Fixes AB#123`. Jira/Monday have no closing keyword,
   so move the ticket's status manually (active auto-transitions are an opt-in layer
   — see [INTEGRATIONS.md](INTEGRATIONS.md)). The suite makes **no API calls**.
