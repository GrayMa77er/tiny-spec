---
name: tiny-spec-run
description: The one router — read each artifact's status flag to work out where work stands, then invoke the skill that moves it forward. Two stop points, chosen once at the start: by default it walks tiny-spec-adopt/create → design → plan and STOPS before tiny-spec-build; asked to build ("spec it out and build it") or handed a feature list, it drives each feature branch → spec → plan → build → merge until the list ends or something halts it. With a PRD and no BREAKDOWN.md it runs tiny-spec-scope first. Build-through is supervised by default — each feature's open questions are asked and its plan is approved in plan mode before it builds — and unattended only when asked. Independent features — grouped by their BREAKDOWN.md needs: field, or named by the user — build concurrently, one git worktree per lane, merging batch by batch. Use for "run the spec flow", "pick the chain back up", "build the backlog", "work through the breakdown". NOT for a single stage — for that invoke tiny-spec-create, tiny-spec-plan, or tiny-spec-design directly.
---

# tiny-spec-run

A **router**, not a stage. It owns no artifact, duplicates no instructions, writes
nothing, and holds no state file. It answers one question — *where does this work
stand?* — and invokes the one skill that moves it forward. Then it re-asks.

**Everything it decides comes from files on disk and from git.** There is no run-state
file, no pointer, no lock. That is the property that makes it safe: a run abandoned
halfway through an interview and resumed tomorrow lands on exactly the right rung, and
a feature list resumes correctly overnight. Do not "optimize" this into stored state.

## Step 0 — fix the stop point, once

**This is the most important decision in the skill, and it is made exactly once.**
Read the user's opening request and pick one:

| The user asked for | Stop point |
|---|---|
| the flow, the spec, "pick the chain back up", "get it ready" | **stop-before-build** (default) |
| the flow **and** the build — "spec it out and build it", "build the backlog", "work through the breakdown" — or handed a feature list | **build-through** |

**Anything short of an explicit ask to build is stop-before-build.** Build is the
user's review gate — stopping before it is why this skill's default exists.

> **The stop point is fixed for the whole run and is never revised.** Not by a stage's
> closing report, not by a rung, not by an ambiguous follow-up, not by "do it all"
> arriving later. A stop-before-build run that reaches a ready task list **stops** and
> tells the user to run `tiny-spec-build` — it does not promote itself. If the user
> wants the build after seeing the plan, that is a new invocation, and that second look
> is exactly the value of the default.

If the user named a **single stage** ("update the spec", "redo the tasks", "anchor the
designs"), hand off to that skill and stop. `run` is for walking the chain, not for
wrapping one stage.

Step 0 is a **once-per-run** check on the opening request. Do not re-run it when you
return to Step 2 after a stage, or between features.

### Supervised or unattended — build-through only, also fixed once

A build-through run is **supervised** by default: for each feature, `tiny-spec-create`
asks you whatever the PRD and the breakdown leave open, and `tiny-spec-plan` drafts the
plan in plan mode and **waits for your approval** before writing it. Only an approved
plan reaches the build. The run is **unattended** only when the opening request says so
— "walk away", "unattended", "overnight", "don't ask me anything" — and then the stages
take their approvals from `BREAKDOWN.md` and stop only on genuine blockers.

Like the stop point, this is read once from the opening request and never revised. A
declined plan does not flip the run to unattended, and "just build it" mid-run does not
waive the remaining approvals — that is a new invocation.

### Also at Step 0, if the stop point is build-through

1. **Check the preconditions.** All three, before touching anything:
   - it is a git repo (`git rev-parse --is-inside-work-tree`);
   - the working tree is **clean** (`git status --porcelain` prints nothing) — a dirty
     tree would get swept into the first feature's commits;
   - an integration branch exists — `main`, or `master` if there is no `main`.

   Any of them failing → say which and stop. Do not offer to stash, commit, or create
   the branch for the user.

2. **Resolve the feature list** (below) and play it back in order — slug and title — with
   the state you derived for each, **grouped into the batches you will run**. This is the
   user's chance to reorder, drop, narrow, or correct a dependency before anything is cut.

3. **Take the pause policy.** Ask for, or accept, standing technical stop points for
   this run — *"halt before anything that touches auth"*, *"stop before any schema
   migration"*. Carry the wording verbatim into every feature's `tiny-spec-plan` stage,
   where it becomes a real `pause:` line on the matching task. Pause points are
   **technical**, not per-feature: the thing worth looking at is a migration or an auth
   boundary, not a feature heading.

4. **Fix the lane count.** Default **3**; take a number from the user if they gave one.
   This is a concurrency limit on the machine, not a budget — the feature list is still the
   budget, and a batch wider than the lane count simply runs in successive fills. **One
   lane must stay available**: any phrasing asking for one feature at a time ("one at a
   time", "no parallelism", "serially") sets it to 1, which collapses Step 4 to the
   sequential behavior — no worktrees, no batching.

   Then check one more precondition, once you know the slugs in the first batch: **no
   target worktree path already exists.** Name the collisions and stop; do not reuse or
   remove a directory you found.

## Step 1 — resolve the scope

### Stop-before-build: the active ticket dir

Read `git rev-parse --abbrev-ref HEAD`, then resolve `.spec/<slug>/`:

0. **No ticket dirs exist at all** — nothing to resolve. Skip straight to the ladder
   (L0–L2); do **not** ask the user to choose among nothing.
1. **Branch match** — the `.spec/<slug>/` whose `<slug>` appears as a token in the
   branch name (case-insensitive, bounded by the start/end or a `/`, `-`, `_`).
2. **Sole dir** — if none matches, use the only ticket dir, if exactly one exists.
3. **Ask** — else ask the user which.

**Two cases pre-empt that order — ask instead of applying it:**

- **More than one dir matches** the branch (e.g. `feature/PROJ-123-gh-42` matching both
  `PROJ-123/` and `gh-42/`). There is no defined tie-break; inventing one here would
  silently disagree with every other skill.
- **Ticket dirs exist, the branch is `main`/`master`, and no dir matches by name.** Ask
  **before** falling through to rule 2 — rule 2 would otherwise silently swallow this.
  The usual cause is a forgotten `git switch`, and guessing either way is wrong. Offer
  three options: resume the existing ticket (naming it), start new work (→ L2), or
  switch to the right branch first and re-run.

**Degraded case, not an ask case: detached HEAD, or not a git repo.** Branch match is
simply unavailable — fall through to rules 2 and 3 as written, and mention that
`tiny-spec-build` will need a repo later to commit.

Never create a ticket dir yourself — that is `tiny-spec-create`'s job.

### Build-through: the feature list

**No `BREAKDOWN.md` yet, but a PRD?** If the user named a PRD or doc at invocation, or a
`PRD.md` sits at the project root, and no list was pasted, carve it first: `git switch
<integration>`, then invoke **`tiny-spec-scope`** with the brief *carve `<path>` into
`BREAKDOWN.md`, then commit `BREAKDOWN.md` alone on the current branch.* The commit is
what lets every lane see the list: a worktree cut from the integration branch only
contains what's committed there. Scope's own playback is where the user approves the
carve. Then continue below with the file it wrote. A PRD that isn't committed already
failed the clean-tree check, which is correct, because a lane couldn't read it either.

**Default: `BREAKDOWN.md` at the project root**, in file order. Each `## Feature:`
heading is one item; take its **`slug:`** — that names both the branch and the
`.spec/<slug>/` dir. One feature is one branch and one merge.

**A pre-2.0 `BREAKDOWN.md`** (with `- Story:` lines nested under the features) is a
stop: say the format changed and point the user at `tiny-spec-scope` to regenerate it,
or at flattening each story into its own `## Feature:` by hand. Don't guess which level
was meant to be the unit.

**A list pasted at invocation wins** over `BREAKDOWN.md` when the user gives one. Treat
each line as a feature title and derive a kebab-case slug from it. Such a feature has **no
acceptance criteria**, so `tiny-spec-create` will run its full interview when it reaches
that feature — which is correct, not a failure: a one-line feature name is not enough to
build from, and that interview *is* the human input the run stops for. Say so at Step 0
so the user knows a pasted list will interview them even in an unattended run.

If there is no pasted list, no `BREAKDOWN.md`, and no PRD, stop and say so. Never invent
the list.

**Where each feature stands — derive, don't record.** For each slug, in order, ask git —
first match wins:

1. **`git show <integration>:.spec/<slug>/PLAN.md`** succeeds, its `## Tasks` has at
   least one task, and every task is `[x]` → **built and merged.** Skip it.
2. Otherwise, if the branch exists (`git rev-parse --verify <slug>`), read
   **`git show <slug>:.spec/<slug>/PLAN.md`**, counting only `## Tasks`:
   - succeeds, every task `[x]` → **built, not merged** → resume at the **merge**.
   - succeeds, at least one `[ ]` → **in progress** → resume at the **build**.
   - fails, or `## Tasks` is empty → **planning incomplete** → resume at the **ladder**.
3. Otherwise → **not started.** Run the full cycle.

Ask **git**, not the working tree. A feature that isn't merged yet has no `.spec/<slug>/`
on the integration branch at all, so "does the directory exist" can't tell "not started"
apart from "built on a branch you haven't merged" — reading each ref explicitly can.
Sourcing step 1 from the integration branch is also what survives a deleted branch: once
a feature is merged, its ticked task list is part of `main` whether or not the branch that
built it still exists. **This survives parallelism unchanged** — a worktree is just a
branch, so a feature built in a worktree but not yet merged lands on rule 2 exactly as one
built in place.

**Group the remaining features into batches.** Level 0 is every unbuilt feature whose
`needs:` are empty or already built-and-merged; level 1 is every feature whose `needs:` are
all in level 0; and so on. Batches run **in order**; the features inside one batch run
**concurrently**, capped at the lane count.

- **A parallel set the user named at invocation overrides the graph** for this run —
  "build these three at once", or a pasted list they called independent. Explicit beats
  derived, the same way a pasted feature list already wins over `BREAKDOWN.md`. Say that you
  are overriding, and name what the graph would have done.
- **A cycle in `needs:` is a stop.** Print the cycle and stop. Never break it by picking
  an order — `tiny-spec-scope` says two features that need each other are really one, and
  choosing for the user hides a carve that needs fixing.
- **A `needs:` naming a slug that isn't in the list is a stop**, not a shrug. It is either
  a typo or a feature someone dropped, and both want a human.
- **A batch of one is the sequential behavior** — Step 4 collapses to exactly what it did
  before lanes existed. This is the common case for a single ticket and must not change.

## Step 2 — the ladder

**First matching rung wins. Run exactly one stage, then return to Step 1** and
re-evaluate against the new state on disk.

| # | Condition | Action |
|---|---|---|
| LP | no ticket dir resolves, no `BREAKDOWN.md`, and a PRD exists (a `PRD.md` at the root, or a doc the user named) | `tiny-spec-scope` — carve it, and commit `BREAKDOWN.md` |
| L0 | no `.spec/` at all | **does this repo already contain source?** yes → `tiny-spec-adopt`; no → `tiny-spec-create` (fresh) |
| L1 | `.spec/` exists, `.spec/constitution.md` missing | repo has source → `tiny-spec-adopt`; else `tiny-spec-create` — **reseed only** |
| L2 | no ticket dir resolves, or `<active>/SPEC.md` missing | `tiny-spec-create` — **fresh** |
| L3 | `SPEC.md` is `status: stale` | **stop and ask** |
| L4 | `SPEC.md` has a `## Design` section and an export's `sha256` no longer matches | `tiny-spec-design` — **re-anchor** |
| L5 | `<active>/PLAN.md` missing, stale, **or its `## Tasks` is empty** | `tiny-spec-plan` |
| L6 | all current, **at least one task**, at least one `[ ]` | **stop** (stop-before-build) or **build** (build-through) |
| L7 | all current, **at least one task**, every task `[x]` | **stop** — the work is built (build-through: merge) |
| — | **no rung matched** | **stop** — report the exact state you found and ask; never improvise a stage |

**Upstream beats downstream — that is what the table order encodes.** Always fix the
earliest artifact in the chain that needs attention, stale *or* missing. Deriving a task
list from a design you already know is wrong wastes the run, and the reconcile then has
to uncheck completed work all over again.

**L0/L1 carry the greenfield/brownfield fork.** "Does this repo already contain source?"
means: real code beyond config and docs. If yes, the constitution must be *derived from
that code* (`tiny-spec-adopt`) rather than interviewed out of the user — an interviewed
constitution on an existing codebase is how you get a gate that names commands the
project doesn't have. Starting from an idea with no code yet, `tiny-spec-scope` is the
user's to run first; it is not in the ladder (see below).

**L1 is a reseed, not a fresh start**, and it **outranks L2**. The constitution is
project-wide, so it can go missing while a perfectly good `SPEC.md` sits next to it.
Invoke the chosen skill in **reseed/refresh mode** — say so explicitly, and add: *do not
re-interview from scratch, do not create a ticket dir, and do not touch `SPEC.md`.* If the
constitution still doesn't exist afterwards, stop and tell the user; do not loop. The next
pass lands on L2 and creates the spec properly — a *different rung*, so the same-skill
bound below does not fire.

**L3 is a stop, not a stage.** Nothing in the suite ever *sets* `SPEC.md` to stale — it is
the root of the chain — so a stale SPEC means someone hand-edited it. Surface it and offer
`tiny-spec-create` in update mode rather than assuming intent. A go-ahead **in the same
turn** is enough to invoke it and carry on down the ladder; the stop exists to get a human
decision, not to force a second command. (Update mode *clears* the flag on its way out, so
this rung resolves rather than repeating.)

**L4 is the one thing `run` checks that isn't a `status:` flag**, and it is deliberately
*not* a validator: for each `D<n>` in the active `SPEC.md`, run `shasum -a 256 <export>`
and compare with the `sha256:` the entry declares. You are checking whether an anchor
still points at what it says it points at, not inferring whether two documents agree. A
design that moved under a finished spec is otherwise completely invisible — no status
flips, and the build reviews against a screen that no longer exists.

- **Mismatch** → `tiny-spec-design` in re-anchor mode.
- **Missing file** → **stop and tell the user**, naming the entry and the path. Don't
  route it: a deleted export can mean a rename, a move, or a withdrawn design, and each
  wants a different answer. Never quietly drop the entry.
- No `## Design` section, or every hash matches → the rung doesn't fire; fall through.

**Any `status:` that isn't exactly `current`** — `stale`, missing, unreadable, or an
unrecognized value like `draft` — counts as **stale**, on `SPEC.md` and `PLAN.md`
alike. Say so out loud. `PLAN.md` → reconcile (update mode preserves existing ids, the
non-destructive way to be wrong); `SPEC.md` → L3, stop and ask.

**A `## Tasks` with no tasks at all is not "built"** — L6 and L7 both require at least one
task, so an empty checklist matches neither and L5 catches it. Empty a second time → stop
and tell the user; the plan has nothing derivable in it.

`run` trusts the `status:` flags. It does **not** second-guess hand edits, diff
timestamps, or validate the chain — there is no validator in this suite by design. (L4 is
not an exception: a hash is a value the spec itself declares about a file it names, so
checking it is reading state, not judging consistency. Not a precedent for adding
cross-document checks.) So it inherits each stage's propagation: if `tiny-spec-create`
update mode doesn't flip `PLAN.md`, `run` walks right past it. That trust is the price of
having no validator; when a run's result looks wrong, suspect the stage's propagation
before the ladder.

**LP is the PRD on-ramp, and it outranks L0.** Someone who arrives with a PRD wants it
carved into features before any one of them is specced. Otherwise L0/L2 would start a
blank interview and leave the PRD unread. It fires only when there's no ticket dir and no
`BREAKDOWN.md`, so it can't re-fire: once scope has written the file, the next pass falls
through to L0, and `tiny-spec-create` then seeds from it (asking which feature, unless the
user already said). Without a PRD, `tiny-spec-scope` is still the user's call to run from
a bare idea. There is no document for a router to route from.

## Step 3 — how to invoke a stage

Before each invocation, print `tiny-spec-run — <skill>` and one line on why the ladder
picked it. Re-print it every time: `tiny-spec-create`'s interview genuinely ends the
turn, and the orchestration frame has to be in *recent* context to survive that.

Hand the stage its scope explicitly, so a stage reading "run the flow" can't start
something new:

- **When a ticket dir is resolved** (L1–L7): *the active ticket dir is `.spec/<slug>/`;
  operate on it in `<fresh | update | reseed | re-anchor>` mode; do not create a new
  spec dir.*
- **At L0 and L2 there may be no ticket dir yet** — creating one is the point of the
  rung. Say instead: *this is new work; there is no active ticket dir. Create one.* Do
  **not** send the "do not create a new spec dir" line here, and add: *do not fall back
  to an existing ticket dir — the user confirmed this is new work.*
  (`tiny-spec-create` honors that phrase by skipping its sole-dir fallback.)

**Briefs — pass them through verbatim.** In a build-through run you hand stages briefs:

- a **create-stage brief**: *this is a feature run; seed from the `BREAKDOWN.md` feature
  with slug `<slug>`; its `AC:` lines are already approved — don't re-confirm them.* Then
  add one clause by supervision. **Supervised:** *read the PRD named in the Decisions
  `Source:` for this feature and ask me, in one round, anything whose answer would change
  a `REQ-N`.* **Unattended:** *do not stop to ask; stop only on a genuine blocker.* Omit
  the seeding clause for a pasted-list feature. There is nothing to seed from, and the
  full interview is correct in either mode.
- a **plan-stage brief**: the pause policy from Step 0, **word for word**, so the
  technical stop points land as `pause:` lines. **Supervised**, add: *get my approval
  before writing anything — use plan mode.*

Send each brief only to the stage it addresses. Do not summarize one, act on it
yourself, or let it change which rung fires — the ladder is still yours, and a brief is
cargo, not an instruction to you.

**A stage's closing "point the user at X" is not a terminus.** Each stage ends by naming
the next skill. Inside a run that sentence is a *report*, not a stop — when a stage
finishes, return to Step 1 and keep going. This applies **only** to a stage you invoked.
It never applies to L6/L7, which are the ladder's own stops, and **it is never a reason
to enter `tiny-spec-build` in a stop-before-build run.**

## Step 4 — build-through only: build and merge

Reached only when Step 0 fixed the stop point at build-through and the ladder is at L6
(or L7 with an unmerged branch). Work **one batch at a time**, in batch order. For every
feature in the current batch that isn't already built and merged:

1. **Lane.** Give each feature its own **git worktree**, so lanes cannot collide on the
   filesystem: `git worktree add ../<repo>-<slug> -b <slug> <integration>`, or
   `git worktree add ../<repo>-<slug> <slug>` when the branch already exists. Cut **fresh
   from the integration branch** so the feature sees every feature merged before it — that is
   what makes an ordered backlog build correctly, and it is why batches merge before the
   next one starts.

   With a single lane you may stay in the main checkout and `git switch` as before; a
   worktree is only required when a batch has more than one feature.

2. **Ladder.** Walk Steps 1–3 for each feature, in its own worktree, until it reaches L6.
   A feature that stops anywhere else does **not** enter the build — its lane is halted;
   see the halt rule below. In a supervised run this is where the user's input happens,
   one feature at a time: each feature's questions, then its plan approval. A batch
   therefore collects every answer and approval up front, then builds without
   interruption. **A plan the user declined leaves no `PLAN.md`**, so the feature stops at
   L5 and its lane halts `paused`. Re-running picks it up at the plan, and the plan asks
   again. **Never walk the ladder twice to push past its own stop:**
   each of those is a human decision it deliberately declined to make, and running it
   again declines again.

3. **Build.** Invoke **`tiny-spec-build`** **once for the whole batch**, briefed to run
   through, and hand it every live lane as a `(worktree path, slug)` pair. It owns the
   per-task loop, runs the lanes concurrently, and writes each feature's halt record.
   Do not invoke it a second time for a lane that halted: it resumes from the checkbox
   state, so it lands on the very task that just halted and halts there again.

4. **Merge — only the lanes that returned `done`, one at a time, in batch order.**
   For each, in the main checkout:
   - `git switch <integration>`
   - `git merge --no-ff <slug>` — the merge commit keeps each feature legible in history.
   - **Conflict** → `git merge --abort`, halt that feature `conflict`, and carry on with
     the rest of the batch. Report every conflicted feature at the end.
   - **Run the constitution's Verification commands on the merged result**, exercised the
     way a user would. Red → halt `blocked`. **This check is load-bearing under
     parallelism and is never skipped:** every lane gated against a tree that did not
     contain its siblings, so the merged result is the first time they meet.
   - **Never push.** Merging locally keeps a bad run one `git reset` away; sending it to
     a remote is the user's call, and this suite makes no network calls.

5. **Next batch.** If **every** lane in this batch merged cleanly, return to Step 1 for
   the next batch. Do not re-run Step 0. **If any lane halted, stop the run here** — a
   later batch may well depend on the feature that failed, and working out which features
   are still safe is exactly the machinery this suite refuses to grow. Report and let the
   user decide.

6. **Leave the worktrees.** Do **not** run `git worktree remove`. Cleanup is the user's,
   for the same reason branch deletion is — a halted lane's worktree holds the tree they
   need to look at. List every path you created in the closing report, with the
   `git worktree remove` commands, and let them run it.

**A halt stops the lane it happened in, and ends the run at the end of that batch.**
Within a batch the other lanes run to completion: the features were declared independent,
so stopping the ones that are working buys nothing and throws away finished work. Across
batches the old rule stands unchanged — later features usually assume earlier ones landed,
so never skip ahead past a failure.

`tiny-spec-build` records its own halts (`blocked`, `exhausted`, `fork`) in the feature's
`decisions.md`. **You record nothing** — the merge-stage halts are already legible
without a log: a `conflict` leaves the feature's branch unmerged and git itself reports
the conflicted paths, and a red gate after a merge is reported by the gate. A log entry
restating what git already shows is a second source of truth with extra steps.

**On a red gate after a merge, leave the merge in place.** Report it, name the feature,
and tell the user that `git reset --hard HEAD~1` on the integration branch undoes it.
Do not undo it yourself: fixing forward and rolling back are both reasonable, the choice
is theirs, and discarding a real merge is not a call a router gets to make.

## When done

**Stop-before-build.** Report, in order: the active ticket dir, which stages ran, and
the resulting state — requirements captured, whether every `REQ-N` is covered, and the
task count. Then hand off explicitly: **run `tiny-spec-build` when you're ready to
build** (it starts at the first unchecked task, reviewing as it goes). If you stopped at
L3 or on a bound, say exactly what stopped you and what the user needs to decide.

**Build-through.** Name, in this order:

1. **The terminal state** — exactly one of `done`, `blocked`, `exhausted`, `paused`,
   `fork`, `conflict`. Use the word. With more than one lane, report **each feature's own
   state**, and give the run's state as the **worst** of them: four green lanes and one
   `blocked` is a `blocked` run, never a `done` one with a footnote.
2. **Features built and merged**, in batch order, with their merge commits.
3. **The feature or features it stopped on**, the task within each, and why in one line.
4. **Features never started** — say how many are left, by name.
5. **Worktrees left on disk**, with the `git worktree remove` command for each. You do
   not run them.
6. **The one command that resolves it** — `tiny-spec-create`/`tiny-spec-plan` in update
   mode for `blocked`/`exhausted`, this skill again for `paused` (including a declined
   plan, which it re-drafts and asks about again), the decision the user
   owes you for a `fork`, or the conflicted paths for a `conflict`.

**Only `done` — every feature merged — may report the work as built.** A run that halted
has unbuilt features in it, and a report that rounds `blocked`, `exhausted`, `paused`,
`fork`, or `conflict` up to done converts a stop the user could act on into a false
completion they won't check. Say the state, then say what's left.

**Unanchored designs — say it once, don't act on it.** If a `design/` directory exists
at the project root with files in it, and the active `SPEC.md` has **no `## Design`
section**, note that in the report: name the count and tell the user `tiny-spec-design`
would anchor them, or that they can ignore it if this ticket has no visual surface.
This is deliberately **a notice, not a rung** — a rung would re-fire forever on any
ticket that legitimately has no visual surface.

## Hard rules

- **The Step 0 stop point is fixed for the run.** A stop-before-build run **never**
  invokes `tiny-spec-build`, no matter what a stage reports, which rung fires, or what
  a follow-up message seems to imply. "Do it all" arriving mid-run does not override it
  — that is a new invocation.
- **Never write, edit, or flip anything.** No `status:`, no checkbox, no `decisions.md`
  entry, no code, no `BREAKDOWN.md` edit. Delegate or stop. A router that regenerates
  documents is a second source of truth.
- **Never push, force, rebase, reset, delete a branch, or remove a worktree.** The only
  git commands this skill issues are `switch`, `switch -c`, `merge --no-ff`,
  `merge --abort`, `worktree add`, `worktree list`, and read-only queries. Everything
  outward-facing or destructive stays the user's — `worktree remove` included, which is
  why Step 4 hands those commands over instead of running them.
- **Never merge a feature whose build didn't return `done`.**
- **Never build an unapproved plan in a supervised run.** The approval is the plan
  existing: `tiny-spec-plan` writes `PLAN.md` only once the user approves it. Never write
  it for them, and never build from a draft.
- **Never invoke `tiny-spec-run`.** Re-entering means re-reading these steps, not
  calling yourself. Self-invocation compounds context and does not terminate.
- **Never resolve a halt yourself.** A blocker means an upstream document is wrong,
  which is the user's call. Routing to `plan`/`create` in update mode automatically
  would let the run rewrite the requirement its own task just failed to satisfy — the
  agent grading its own homework, one level up.
- **Bounded: at most four stage invocations per ticket, and never the same skill twice
  in a row *for the same rung*.** Then report where things stand and stop, even if the
  ladder still points somewhere. The rung qualifier is what makes the bound usable:
  `create` at L1 (reseed) followed by `create` at L2 (write the spec) is a legitimate
  sequence. But landing on the *same* rung twice means the stage didn't do what you
  asked, and running it again will not fix that — stop and tell the user. The count
  lives in this turn's context, not on disk; a resumed run starts it over, which is the
  intended trade for having no state file.
- **There is no budget to set.** The feature list is the budget: the run ends when the
  features end. No turn ceiling, no token cap, no max-features knob.
