---
name: tiny-spec-loop
description: Work a list of stories end to end, one after another — for each story cut a branch from main, plan it, build it, merge it back locally, then move to the next. Reads BREAKDOWN.md by default, or a list pasted at invocation. Halts the WHOLE run on a blocker, a spent convergence budget, a task's pause: point, a genuine fork, a merge conflict, or a red gate after a merge — and names which. Use for "build the backlog", "work through the breakdown", "build these features one after another". NOT for a single story — for that use tiny-spec-run then tiny-spec-build.
---

# tiny-spec-loop

A **router**, not a stage. It owns no artifact, writes nothing, and holds no state
file. It walks a list of stories and, for each one, drives the existing flow to a
finished, merged branch — then moves to the next.

Per story the cycle is always the same four moves:

```
cut a branch from main  →  tiny-spec-run  →  tiny-spec-build  →  merge back to main
```

**Everything it decides comes from files on disk and from git.** Which stories are
built, which are merged, which haven't started — all derived, never recorded. That is
what makes a run abandoned overnight resume correctly tomorrow, and it is why this
skill needs no run log, pointer, or lock. Do not "optimize" this into stored state.

**It supplies one thing the flow was missing: a stopping rule.** The task list is the
goal, the independent reviewer running the real gate is the verification, `memory.md`
plus a commit per passed task is the memory. This skill adds when to stop, and nothing
else — no budget, no turn ceiling, no config.

## Step 0 — the run brief

The one interactive moment. Everything after it runs without asking unless a stage
genuinely needs an answer.

1. **Check the preconditions.** All three, before touching anything:
   - it is a git repo (`git rev-parse --is-inside-work-tree`);
   - the working tree is **clean** (`git status --porcelain` prints nothing) — a dirty
     tree would get swept into the first story's commits;
   - an integration branch exists — `main`, or `master` if there is no `main`.

   Any of them failing → say which and stop. Do not offer to stash, commit, or create
   the branch for the user.

2. **Resolve the story list** (Step 1) and play it back in order — slug and title —
   with the state you derived for each (Step 2). This is the user's chance to
   reorder, drop, or narrow before anything is cut.

3. **Take the pause policy.** Ask for, or accept, standing technical stop points for
   this run — *"halt before anything that touches auth"*, *"stop before any schema
   migration"*. Carry the wording verbatim into every story's `tiny-spec-tasks` stage
   (Step 3), where it becomes a real `pause:` line on the matching task. Pause points
   are **technical**, not per-story: there is no way to mark a whole story for review,
   because the thing worth looking at is a migration or an auth boundary, not a
   feature heading.

Step 0 is a **once-per-run** check. Do not re-run it between stories.

## Step 1 — the story list

**Default: `BREAKDOWN.md` at the project root**, in file order. Each `- Story:` under
each `## Feature:` heading is one item; take its **`slug:`** — that names both the
branch and the `.spec/<slug>/` dir. A `## Feature:` heading is a grouping, not an item:
it carries no slug, so a Feature with three stories is three branches and three merges.

**A list pasted at invocation wins** over `BREAKDOWN.md` when the user gives one. Treat
each line as a story title and derive a kebab-case slug from it. Such a story has **no
acceptance criteria**, so `tiny-spec-create` will run its full interview when it reaches
that story — which is correct, not a failure: a one-line feature name is not enough to
build from, and that interview *is* the human input the run stops for. Say so in Step 0
so the user knows a pasted list is a supervised run, not a walk-away one.

If neither exists, stop and say so. Never invent the list.

## Step 2 — where each story stands (derive, don't record)

For each story slug, in order, ask git — **in this order**, first match wins:

1. **`git show <integration>:.spec/<slug>/tasks.md`** succeeds and every task is `[x]`
   → **built and merged.** Skip it.
2. Otherwise, if the branch exists (`git rev-parse --verify <slug>`), read
   **`git show <slug>:.spec/<slug>/tasks.md`**:
   - succeeds, every task `[x]` → **built, not merged** → resume at the **merge** (4).
   - succeeds, at least one `[ ]` → **in progress** → resume at the **build** (3).
   - fails (no task list yet) → **planning incomplete** → resume at the **plan** (2).
3. Otherwise → **not started.** Run the full cycle.

Ask **git**, not the working tree. A story that isn't merged yet has no `.spec/<slug>/`
on the integration branch at all, so "does the directory exist" can't tell "not started"
apart from "built on a branch you haven't merged" — reading each ref explicitly can.
Sourcing step 1 from the integration branch is also what survives a deleted branch: once
a story is merged, its ticked task list is part of `main` whether or not the branch that
built it still exists.

## Step 3 — the per-story cycle

For the first story that isn't already built and merged:

1. **Branch.** `git switch <slug>` if it already exists; otherwise
   `git switch -c <slug> <integration>` — cut **fresh from the integration branch** so
   this story sees every story merged before it. That is what makes an ordered list
   build correctly: story 3 gets stories 1 and 2 already in its tree.

2. **Plan.** Invoke **`tiny-spec-run`**, once. It resolves `.spec/<slug>/` from the
   branch name automatically, so you don't name the ticket dir. Hand it two things:
   - a **create-stage brief**: *this is a loop run; seed from the `BREAKDOWN.md` story
     with slug `<slug>` and do not stop to confirm the requirements — its `AC:` lines
     are already approved.* Omit the seeding clause for a pasted-list story; there is
     nothing to seed from and the interview is correct.
   - a **tasks-stage brief**: the pause policy from Step 0, verbatim, so the technical
     stop points land as `pause:` lines.

   If `tiny-spec-run` stops anywhere other than **L9** (tasks ready) or **L10** (already
   built), that is a halt — report and stop the whole run. **Never invoke it twice to
   push past its own stop:** each of those is a human decision it deliberately declined
   to make, and running it again declines again.

3. **Build.** Invoke **`tiny-spec-build`**, once, briefed to run it through. It owns
   the per-task loop and writes its own halt record. Anything other than `done` halts
   the whole run — **do not merge a story that didn't finish**, and do not invoke build
   a second time: it resumes from the checkbox state, so it lands on the very task that
   just halted and halts there again.

4. **Merge — only on `done`.** In order:
   - `git switch <integration>`
   - `git merge --no-ff <slug>` — the merge commit keeps each story legible in history.
   - **Conflict** → `git merge --abort`, then halt `conflict` (below).
   - **Run the constitution's Verification commands on the merged result**, exercised
     the way a user would. A story that was green alone can still break against work
     merged before it, and that is exactly what this catches. Red → halt `blocked`.
   - **Never push.** Merging locally keeps a bad run one `git reset` away; sending it
     to a remote is the user's call, and this suite makes no network calls.

5. **Next story.** Return to Step 2. Do not re-run Step 0.

## Step 4 — report

Name, in this order:

1. **The terminal state** — exactly one of `done`, `blocked`, `exhausted`, `paused`,
   `fork`, `conflict`. Use the word.
2. **Stories built and merged**, in order, with their merge commits.
3. **The story it stopped on**, the task within it, and why in one line.
4. **Stories never started** — say how many are left, by name. A run that stopped at
   story 2 of 7 must not read like a finished backlog.
5. **The one command that resolves it** — `tiny-spec-create`/`tiny-spec-plan` in update
   mode for `blocked`/`exhausted`, `tiny-spec-loop` again for `paused`, the decision
   the user owes you for a `fork`, or the conflicted paths for a `conflict`.

**Only `done` — every story merged — may report the work as built.** A run that halted
has unbuilt stories in it, and a report that rounds `blocked`, `exhausted`, `paused`,
`fork`, or `conflict` up to done converts a stop the user could act on into a false
completion they won't check. Say the state, then say what's left.

### Halting

A halt stops **the whole run**, not just the current story. Later stories in a list you
wrote top to bottom usually assume the earlier ones landed, so skipping ahead past a
failure produces a second, more confusing failure downstream.

`tiny-spec-build` records its own halts (`blocked`, `exhausted`, `fork`) in the story's
`decisions.md`. **You record nothing** — the merge-stage halts are already legible
without a log: a `conflict` leaves the story's branch unmerged and git itself reports
the conflicted paths, and a red gate after a merge is reported by the gate. A log entry
restating what git already shows is a second source of truth with extra steps.

**On a red gate after a merge, leave the merge in place.** Report it, name the story,
and tell the user that `git reset --hard HEAD~1` on the integration branch undoes it.
Do not undo it yourself: fixing forward and rolling back are both reasonable, the
choice is theirs, and discarding a real merge is not a call a router gets to make.

### Hard rules

- **Never write, edit, or flip anything.** No `status:`, no checkbox, no
  `decisions.md` entry, no code, no `BREAKDOWN.md` edit. Delegate or stop.
- **Never push, force, rebase, reset, or delete a branch.** The only git commands this
  skill issues are `switch`, `switch -c`, `merge --no-ff`, `merge --abort`, and
  read-only queries. Everything outward-facing or destructive is the user's.
- **Never merge a story whose build didn't return `done`.**
- **At most one `tiny-spec-run` and one `tiny-spec-build` per story.**
- **Never invoke `tiny-spec-loop`.** Re-entering means re-reading these steps, not
  calling yourself. Self-invocation compounds context and does not terminate.
- **Never invoke `tiny-spec-create`, `tiny-spec-plan`, or `tiny-spec-tasks` directly.**
  That ladder is `tiny-spec-run`'s; walking it here would duplicate it, and two ladders
  drift. Briefs are passed *through* run, not around it.
- **Never resolve a halt yourself.** A blocker means an upstream document is wrong,
  which is the user's call. Routing to `plan`/`create` in update mode automatically
  would let the loop rewrite the requirement its own task just failed to satisfy — the
  agent grading its own homework, one level up.
- **There is no budget to set.** The story list is the budget: the run ends when the
  stories end. No turn ceiling, no token cap, no max-stories knob.
