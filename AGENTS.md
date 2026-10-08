# AGENTS.md — working on this skill suite

Guidance for any agent (Claude Code or otherwise) editing this folder.

## What this is

A lean spec-driven flow with **two front doors**, one spine, and one router:

```
GREENFIELD                      BROWNFIELD
tiny-spec-scope                 tiny-spec-adopt
idea → features                 code → constitution
BREAKDOWN.md                    constitution.md
        \                        /
         v                      v
  tiny-spec-create → tiny-spec-plan → tiny-spec-build
  SPEC.md            PLAN.md (+ Tasks)    per-task loop
                     + constitution

         tiny-spec-run     the one router, drives the above
         tiny-spec-design  optional add-on, UI projects only
```

Anchored by a strong **constitution** (`.spec/constitution.md`) and a per-task loop of
**plan → implement → review → commit** with an *independent* reviewer. See
[README.md](README.md) for the user-facing shape.

**Each `SKILL.md` is the sole contract for what it writes.** There is no separate
rules-of-record document — that was `CONTRACTS.md`, and it was deleted in 1.0 because
nothing read it at runtime and keeping it in sync by hand was pure drift surface. If you
need to know a format, read the skill that owns it.

## North star — earned ceremony

This suite is deliberately small. Do **not** grow it back into waves, `owns:` contracts,
a checkpoint matrix, autonomous budgets, or validators. `tiny-spec-run` is the one
router, and it earns that only by owning nothing — no artifact, no state file. Before
adding a skill, agent, artifact, format field, or knob, the bar is: *does it clearly pay
for itself, or is it ceremony?* When in doubt, leave it out. A change that makes this
bigger needs a strong reason; a change that makes it smaller usually doesn't.

**Parallelism is allowed across features, and forbidden within one.** This line is load-
bearing, so hold it in both directions. *Across* features: independent work builds
concurrently, one git worktree per lane, grouped by the `needs:` field in `BREAKDOWN.md`
and merged batch by batch. That earns its keep — the features are separate branches
touching separate files, and worktrees make the isolation real rather than promised.
*Within* a feature: tasks stay strictly sequential, top to bottom. They share files and
each one assumes its predecessors landed, so parallelizing them would require `owns:`
file contracts — the exact ceremony 1.0 deleted. Waves, a checkpoint matrix, and
validators all remain out at **both** levels.

**The router's stop point is decided once and never revised.** This is the single most
important invariant in the suite, and the one most likely to be "helpfully" relaxed.
`tiny-spec-run` fixes stop-before-build or build-through at Step 0 from the user's
opening request. No stage report, no rung, no later "do it all" may promote a
stop-before-build run into a build-through run. Build is the user's review gate; a
router that talks itself into building is the failure this design exists to prevent.

The same holds for **supervised vs unattended**, also fixed at Step 0. A build-through
run is supervised unless the opening request asks to walk away: each feature's open
questions get asked, and its plan is approved in plan mode before it builds. The approval
is not a flag. It is `PLAN.md` existing, because `tiny-spec-plan` writes nothing until the
user approves, so a resumed run can never build a plan nobody said yes to. Don't add an
`approved:` field; the file's existence already says it.

**There is no budget and no state file.** The feature list *is* the budget — the run ends
when the features end. A turn ceiling, a token cap, or a max-features knob would each put
a weaker stopping rule beside the real one. And loop progress is *derived*:
`git show <integration>:.spec/<slug>/PLAN.md` answers "is this feature built and merged"
without anything being written down. A progress file would be faster to read and wrong
the first time someone merges by hand.

**The git surface is deliberately tiny.** `tiny-spec-run` is the only skill that runs
git beyond committing, and it is capped at `switch`, `switch -c`, `merge --no-ff`,
`merge --abort`, `worktree add`, `worktree list`, and reads. Pushing, rebasing,
resetting, deleting branches, removing worktrees, and opening PRs are all out — not
because they're hard, but because they are outward-facing or destructive, and those stay
the user's.

> **Amendment (parallel features).** `worktree add`/`worktree list` were added to that cap
> when features gained the ability to build concurrently — a worktree is what keeps two
> lanes from colliding on the filesystem, and there is no way to get that isolation
> without it. **`worktree remove` was deliberately left out**, on exactly the same
> grounds as branch deletion: a halted lane's worktree holds the tree the user needs to
> look at. `tiny-spec-run` reports the paths and the removal commands; the user runs
> them. Do not "finish the feature" by adding cleanup.

Three structural choices are **intended**, not drift — don't "simplify" them away:

- **Per-spec namespacing** under `.spec/<slug>/` with a shared
  `constitution.md`/`memory.md` spine.
- **The task checklist is a `## Tasks` section of `PLAN.md`, not its own file.**
  Design and checklist always went stale together, so they share one `status:` flag.
  `tiny-spec-build` may change only the checkboxes and `updated:` in `PLAN.md` — never
  the design prose. Don't split it back out (it was `tasks.md` before 2.0).
- **Richer SPEC/PLAN templates** whose extra sections are all marked optional
  (`<!-- optional -->`) so they add shape without forcing ceremony. Keep new template
  sections optional unless a section truly must always be filled.

## Artifact ownership

Each artifact has exactly **one** owning skill that copies its skeleton, with one
documented exception:

| Artifact | Owner |
|---|---|
| `BREAKDOWN.md` (project root) | `tiny-spec-scope` |
| `.spec/constitution.md` | **two owners** — `tiny-spec-adopt` (derive, brownfield) and `tiny-spec-create` (seed, greenfield) |
| `.spec/constitution.md` § `Design system`, § `visual:` | `tiny-spec-design` |
| `.spec/<slug>/SPEC.md` | `tiny-spec-create` |
| `.spec/<slug>/SPEC.md` § `Design` (`D<n>`) | `tiny-spec-design` |
| `.spec/<slug>/PLAN.md` (incl. `## Tasks`; build ticks checkboxes only) | `tiny-spec-plan` |
| `.spec/memory.md` | `tiny-spec-build` |
| `.spec/<slug>/decisions.md` | no template — append-only, fixed inline skeleton |

**The constitution's two owners are a real cost, so treat them as one unit:** a change
to the constitution skeleton must land in **both** `tiny-spec-adopt/SKILL.md` and
`tiny-spec-create/SKILL.md`. They are duplicated on purpose — the portability rule below
forbids a shared file — so grep for the section heading and reconcile every hit.

The same goes for `tiny-spec-design` writing into two files it doesn't own. It owns
*named sections*; it must never touch a `REQ-N`, the rest of the constitution, or a
`status:` flag outside its own propagation rules.

## ⚠️ After making changes — validate (don't skip)

Editing a `SKILL.md` or agent file is editing a **prompt**, not code — bugs are silent
(no compiler, no test will catch a misleading instruction). So:

1. **Keep the contract consistent — by hand.** There are *no* Python validators by
   design. A format change must land in the owning skill's inline skeleton **and every
   skill or agent that reads or writes that artifact**. Grep for the artifact name and
   the token you changed; reconcile every hit. Mind the two-owner cases above.
2. **Dry-run in a throwaway sandbox** (`/tmp/...`, `git init`). A **new** skill or agent
   can't be invoked the session it's added (both load at startup). Validate one of three
   ways: follow the `SKILL.md` **verbatim** yourself; dispatch a built-in stand-in
   (`Explore` for read-only, `general-purpose` for writing) with the same prompt; or —
   once installed — dispatch the real agents directly. Confirm the instructions,
   followed exactly, produce contract-conforming output.
3. **Runtime-verify — never static-only.** The core belief here: **unit-green ≠
   working.** A passing test suite is necessary, not sufficient. The whole reason
   `tiny-spec-build-reviewer` exercises every task's acceptance end-to-end is to catch
   this — so when you change the build loop, prove it on a real task, don't infer it from
   the prose reading correctly.
4. **Trip the safeguards on purpose** when you touch the build/executor/reviewer or
   router machinery. These must stay caught:
   - a task that **passes a narrow self-check but fails the gate / acceptance** → the
     reviewer must return `FAIL`, and `tiny-spec-build` must loop back (not tick);
   - **gate scope escalates, never narrows:** a reviewer handed a `scoped` gate that
     cannot establish the acceptance (needs a build artifact, stale install state) must
     run the **full** gate and say so in `GATE:` — never pass on the thinner evidence.
     And a task whose `CHANGES` touch dependency or build config must be dispatched
     `full` by `tiny-spec-build` in the first place. The acceptance is exercised
     end-to-end at **both** scopes; that part is never what gets scoped away;
   - an executor that hits a real **blocker** → it must STOP and report `blocked` (never
     hack past), and `tiny-spec-build` must leave the task `[ ]` and route upstream;
   - **convergence bound:** a task that stays red past 2 fix attempts must become a
     blocker, not an infinite grind;
   - **memory round-trip:** an operational lesson surfaced during a build must land as a
     curated `memory.md` entry and be injected into the *next* executor/reviewer prompt;
   - **completed-work guardrail:** an upstream change that touches a `[x]` task must
     **uncheck** it and log it for review;
   - **pause honored, and honored *early*:** a task carrying `pause:` must halt the build
     **before** it runs — task still `[ ]`, no executor dispatched, `PLAN.md` untouched
     — and a conversational waiver must not be written back into the file;
   - **terminal state never rounded up:** a run that ends `blocked`, `exhausted`,
     `paused`, `fork`, or `conflict` must say so by name. Only `done` may report the work
     as built, and in a feature run that means **every** feature merged — a run that stopped
     at feature 2 of 7 must not read like a finished backlog;
   - **no merge without `done`:** a feature whose build halted must leave its branch
     unmerged. In a **sequential** run that halt stops the run. In a **parallel batch**
     it stops only its own lane — the sibling lanes were declared independent and run to
     completion — and the run then stops at the **end of that batch**, never starting the
     next one. A halted lane must never be rounded up into a sibling's `done`;
   - **lanes stay isolated:** every executor and reviewer is given a working directory
     and must never read, write, or run a gate outside it. A `memory.md` write from
     inside a lane is a bug — in multi-lane mode the file is written once, after the
     batch merges, or every parallel batch ends in a merge conflict on it;
   - **the stop point holds:** a stop-before-build run must not enter `tiny-spec-build`,
     however a stage's closing line or a follow-up message is phrased;
   - **approval holds:** in a supervised run, a feature whose plan the user declined has
     no `PLAN.md` and halts `paused`; it must never reach the build;
   - **git stays narrow:** `tiny-spec-run` may only `switch`, `switch -c`,
     `merge --no-ff`, `merge --abort`, and read. It must refuse to start a build-through
     run on a dirty tree, and must **never** push, force, rebase, reset, or delete a
     branch. A red gate after a merge is reported with the undo command, never undone
     automatically;
   - **`tiny-spec-adopt` stays read-only:** it must never modify source, create a spec
     dir, or touch git — and it must never invent a verification command it didn't run.
5. **Clean up.** Remove the sandbox. Never commit a `.spec/` from a test run or any build
   artifacts into this folder.

## Portability — no absolute paths

This suite must run for **anyone on any machine**. So:

- **No hardcoded absolute paths** (no `/Users/...`, no machine-specific dirs). Each skill
  is **self-contained**: every skeleton it writes is **inline in its own `SKILL.md`**, so
  it reads no companion file at all. A skill is one file, and it works wherever it's
  installed. Don't reintroduce a `templates/` folder — an out-of-project read costs the
  user a permission prompt on every run. This is why the constitution skeleton is
  duplicated across two skills; that duplication is the cheaper half of the trade.
- **No shared parent required at runtime.** Each `SKILL.md` is self-sufficient. If you
  add a rule a skill needs, inline it in the skill.
- **The two agents are referenced by name** (`tiny-spec-build-executor`,
  `tiny-spec-build-reviewer`), not by path — they must be installed in `~/.claude/agents/`
  for `tiny-spec-build` to dispatch them.
- **Project root vs skill** — `.spec/` and the user's code live in the user's cwd (the
  project root); it is **never** created inside a skill's directory.

## Install / discovery

Skills install to `~/.claude/skills/` and agents to `~/.claude/agents/` (**copied**, so
each install is self-contained). The install set is declared in
[tiny_spec/manifest.json](tiny_spec/manifest.json) — adding, renaming, or removing a
skill means editing the manifest and the matching path in `pyproject.toml`, nothing else.
New skills/agents load at startup — restart the session after installing.

**Removed skills are not uninstalled by a re-install.** `tiny-spec install` copies the
manifest's entries; it does not delete skills that left the manifest. After a release
that removes a skill, users must `tiny-spec uninstall` first or delete the stale
directories by hand — say so in the changelog.

## Commits

One commit per logical change, in **Conventional Commits** format
(`<type>(<scope>): <description>`), ending with the trailer:

```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

This is the same format the suite itself emits — use it for work *on* the suite too.
Only commit work once it's validated per the checklist above.
