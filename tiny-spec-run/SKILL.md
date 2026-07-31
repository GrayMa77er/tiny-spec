---
name: tiny-spec-run
description: Run the spec flow end to end — read each artifact's status flag to work out where the active ticket stands, then invoke tiny-spec-create → tiny-spec-plan → tiny-spec-tasks in order, taking anything marked stale before anything missing. STOPS before tiny-spec-build; it never builds, never commits, and never writes an artifact itself. Use for "run the whole spec flow", "spec this out end to end", or "pick the chain back up after a change". NOT for a single stage — for that, invoke tiny-spec-create, tiny-spec-plan, or tiny-spec-tasks directly.
---

# tiny-spec-run

A **router**, not a stage. It owns no artifact, duplicates no instructions, and
writes nothing. It answers one question — *where does this ticket stand?* — and
invokes the one skill that moves it forward. Then it re-asks.

It exists because `plan` and `tasks` are rarely reviewed on their own; the real
review happens at build time. So `run` collapses the walk from intent to a ready
task list into one command — and **stops there**, because `tiny-spec-build` is where
you actually look at the work.

**Everything it decides comes from files on disk.** There is no run-state file, no
pointer, no lock. That is the property that makes it safe: a run abandoned halfway
through an interview and resumed tomorrow lands on exactly the right rung. Do not
"optimize" this into stored state.

`tiny-spec-prd` and `tiny-spec-breakdown` are **not** in the ladder. They are pre-spec
planning on-ramps that write `PRD.md` / `BREAKDOWN.md` at the project root, carry no
`status:` frontmatter, and are the user's call to run — there is nothing for a router
to resolve. `tiny-spec-create` picks `BREAKDOWN.md` up on its own when it exists.

## Step 0 — is this really a whole-flow run?

If the user named a **single stage** ("update the spec", "redo the tasks"), hand off
to that skill and stop. `run` is for walking the chain, not for wrapping one stage.

If they asked for the flow **and** the build ("spec this out and build it"), run the
chain as normal and stop at the end anyway — then tell them `tiny-spec-build` is the
next command. The stop is not negotiable; see the hard rules.

Step 0 is a **once-per-run** check on the user's opening request. Do not re-run it
when you return to Step 1 after a stage.

## Step 1 — resolve the active ticket dir

Read `git rev-parse --abbrev-ref HEAD`, then resolve `.spec/<slug>/` the same way
every other skill does (`CONTRACTS.md` §1 — the order **and** the exceptions):

0. **No ticket dirs exist at all** — nothing to resolve. Skip straight to the ladder
   (L0/L1); do **not** ask the user to choose among nothing.
1. **Branch match** — the `.spec/<slug>/` whose `<slug>` appears as a token in the
   branch name (case-insensitive, bounded by the start/end or a `/`, `-`, `_`).
2. **Sole dir** — if none matches, use the only ticket dir, if exactly one exists.
3. **Ask** — else ask the user which.

**Two cases pre-empt that order — ask instead of applying it:**

- **More than one dir matches** the branch (e.g. `feature/PROJ-123-gh-42` matching
  both `PROJ-123/` and `gh-42/`). There is no defined tie-break; inventing one here
  would silently disagree with every other skill.
- **Ticket dirs exist, the branch is `main`/`master`, and no dir matches by name.**
  Ask **before** falling through to rule 2 — rule 2 would otherwise silently swallow
  this. The usual cause is a forgotten `git switch`, and guessing either way is
  wrong. Offer three options: resume the existing ticket (naming it), start new work
  (→ L1), or switch to the right branch first and re-run.

**Degraded case, not an ask case: detached HEAD, or not a git repo.** Branch match is
simply unavailable — fall through to rules 2 and 3 as written, and mention that
`tiny-spec-build` will need a repo later to commit.

In the ladder below, **L1's "no ticket dir resolves" means the rules above ran and
produced nothing** — not merely that the branch didn't match by name.

Never create a ticket dir yourself — that is `tiny-spec-create`'s job.

## Step 2 — the ladder

**First matching rung wins. Run exactly one stage, then return to Step 1** and
re-evaluate against the new state on disk.

| # | Condition | Action |
|---|-----------|--------|
| L0 | no `.spec/` at all | `tiny-spec-create` — **fresh** |
| L2 | `.spec/` exists, `.spec/constitution.md` missing | `tiny-spec-create` — **reseed only**, see below |
| L1 | no ticket dir resolves for this branch | `tiny-spec-create` — **fresh** (after the `main` check above) |
| L3 | `<active>/SPEC.md` missing | `tiny-spec-create` — **fresh** |
| L4 | `SPEC.md` is `status: stale` | **stop and ask** — see below |
| L4b | `SPEC.md` has a `## Design` section and an export's `sha256` no longer matches | `tiny-spec-create` — **update mode**, see below |
| L5 | `<active>/PLAN.md` missing | `tiny-spec-plan` — **fresh** |
| L6 | `PLAN.md` is `status: stale` | `tiny-spec-plan` — **update mode** |
| L7 | `<active>/tasks.md` missing | `tiny-spec-tasks` — **fresh** |
| L8 | `tasks.md` is `status: stale`, **or its checklist is empty** | `tiny-spec-tasks` — **update mode** |
| L9 | all current, **at least one task**, at least one `[ ]` | **stop** — tell the user to run `tiny-spec-build` |
| L10 | all current, **at least one task**, every task `[x]` | **stop** — the work is built |
| — | **no rung matched** | **stop** — report the exact state you found and ask; never improvise a stage |

**Upstream beats downstream — that is what the table order encodes.** Always fix the
earliest artifact in the chain that needs attention, whether it's stale *or* missing.
Concretely: `PLAN.md` stale + `tasks.md` missing → fix the plan first (L6 before L7).
Deriving a task list from a design you already know is wrong wastes the run, and then
the tasks reconcile has to uncheck completed work all over again.

(So "stale before new" in the description means *reconcile as you walk the chain*, not
that a stale artifact outranks a missing one further upstream — `PLAN.md` missing
still comes before `tasks.md` stale.)

**L2 is a reseed, not a fresh start.** The constitution is project-wide, so it can go
missing while a perfectly good `SPEC.md` sits next to it. Invoke `tiny-spec-create`
in **reseed mode** — it has a section by that name; say so explicitly and add:
*the shared `.spec/constitution.md` is missing — reseed it from whatever already
exists, preferring a `BREAKDOWN.md` `## Decisions` block if there is one, then
`PRD.md`, then the active `SPEC.md`, then the codebase; do not re-interview, do not
create a ticket dir, and do not touch `SPEC.md`.* Reseed is a third mode alongside
`fresh` and `update`. If the constitution still doesn't exist afterwards, stop and
tell the user; do not loop.

**L2 outranks both L1 and L3** — that's why it sits above them in the table. A
constitution gets reseeded even when the ticket dir or `SPEC.md` is also missing;
that's why the brief says "if there is one". `tiny-spec-create` orders its own modes
the same way, so the two agree. The next pass then lands on L1 or L3 and creates the
spec properly — and because that's a *different rung*, the same-skill bound below
does not fire.

**L4 is a stop, not a stage.** Nothing in the suite ever *sets* `SPEC.md` to stale —
it is the root of the chain. A stale SPEC means someone hand-edited it, so surface it
and offer `tiny-spec-create` in update mode rather than assuming intent. If the user
says go ahead **in the same turn**, invoke it and carry on down the ladder — the stop
is there to get a human decision, not to force a second command. (Update mode *clears*
the flag on its way out, so this rung resolves rather than repeating.)

**L4b is the one thing `run` checks that isn't a `status:` flag** — and it is
deliberately *not* a validator. For each `D<n>` in the active `SPEC.md`, run
`shasum -a 256 <export>` and compare with the `sha256:` the entry declares. You are
checking whether an anchor still points at what it says it points at, not inferring
whether two documents agree. A design that moved under a finished spec is otherwise
completely invisible — no status flips, and the build reviews against a screen that
no longer exists.

- **Mismatch** → `tiny-spec-create` in update mode, briefed as: *the design export
  for `D<n>` changed under the spec; re-read it, update the entry and its hash, and
  propagate staleness as the update-mode steps require.*
- **Missing file** → **stop and tell the user**, naming the entry and the path.
  Don't route it: a deleted export can mean a rename, a move, or a design that was
  withdrawn, and each wants a different answer. Never quietly drop the entry.
- No `## Design` section, or every hash matches → the rung doesn't fire; fall through.

**Any `status:` that isn't exactly `current`** — `stale`, missing, unreadable, or an
unrecognized value like `draft` — counts as **stale**, on `SPEC.md`, `PLAN.md`, and
`tasks.md` alike. Say so out loud. For `PLAN.md`/`tasks.md` that means reconciling
(both update modes preserve existing ids, so it's the non-destructive way to be
wrong); for `SPEC.md` it means L4 — stop and ask.

**A `tasks.md` with no tasks at all is not "built"** — that's why L9 and L10 both
require at least one task, and why an empty checklist matches neither. It means the
`tiny-spec-tasks` run produced nothing, so treat it as L8: re-run `tiny-spec-tasks` in
update mode. If it comes back empty a second time, stop and tell the user — the plan
has nothing derivable in it.

`run` trusts the `status:` flags. It does **not** second-guess hand edits, diff
timestamps, or validate the chain — there is no validator in this suite by design.
(L4b is not an exception: a hash is a value the spec itself declares about a file it
names, so checking it is reading state, not judging consistency. Do not use it as a
precedent for adding cross-document checks.) That means it inherits each stage's
propagation: if `tiny-spec-plan` update mode doesn't flip `tasks.md` to stale, `run`
will walk right past it. That trust is the price of having no validator; when a run's
result looks wrong, suspect the stage's propagation before the ladder.

## Step 3 — how to invoke a stage

Before each invocation, print `tiny-spec-run — stage N/3: <skill>` and one line on
why the ladder picked it. **N is the skill's fixed position in the chain**, not a
counter: `create` is always 1, `plan` always 2, `tasks` always 3. So a run that only
reconciles a stale plan prints `stage 2/3`. Re-print it every time:
`tiny-spec-create`'s interview genuinely ends the turn, and the orchestration frame
has to be in *recent* context to survive that.

Hand the stage its scope explicitly, so a stage reading "run the flow" can't start
something new:

- **When a ticket dir is resolved** (L2–L10): *the active ticket dir is
  `.spec/<slug>/`; operate on it in `<fresh | update | reseed>` mode; do not create a
  new spec dir.*
- **At L0 and L1 there is no ticket dir yet** — creating one is the whole point of the
  rung. Say instead: *this is new work; there is no active ticket dir. Create one.*
  Do **not** send the "do not create a new spec dir" line here, and at L1 add: *do not
  fall back to an existing ticket dir — the user confirmed this is new work.*
  (`tiny-spec-create` honors that phrase by skipping its sole-dir fallback.)

**A stage's closing "point the user at X" is not a terminus.** Each stage ends by
naming the next skill ("point the user at `tiny-spec-plan`"). Inside a run that
sentence is a *report*, not a stop — when a stage finishes, return to Step 1 and keep
going. This applies **only** to a stage you invoked. It never applies to L9/L10, which
are the ladder's own stops, and it is never a reason to enter `tiny-spec-build`.

### Hard rules

- **Never invoke `tiny-spec-build`.** Build is the user's review gate — stopping
  before it is the entire point of this skill. "Do it all" does not override this.
- **Never invoke `tiny-spec-run`.** Re-entering means re-reading the ladder above,
  not calling yourself. Self-invocation compounds context and does not terminate.
- **Never write, edit, or flip a `status:` on any artifact.** Delegate or stop.
  A router that regenerates documents is a second source of truth.
- **Bounded: at most four stage invocations per run, and never the same skill twice
  in a row *for the same rung*.** Then report where things stand and stop, even if
  the ladder still points somewhere. The rung qualifier is what makes the bound
  usable: `create` at L2 (reseed) followed by `create` at L3 (write the spec) is a
  legitimate sequence and is exactly why the ceiling is four rather than three. But
  landing on the *same* rung twice means the stage didn't do what you asked, and
  running it again will not fix that — stop and tell the user. The count lives in
  this turn's context, not on disk; a resumed run starts it over, which is the
  intended trade for having no state file.

## When done

Report, in order: the active ticket dir, which stages ran, and the resulting state —
requirements captured, whether every `REQ-N` is covered, and the task count.

**Unanchored designs — say it once, don't act on it.** If a `design/` directory exists
at the project root with files in it, and the active `SPEC.md` has **no `## Design`
section**, note that in the report: name the count and tell the user
`tiny-spec-create` in update mode would anchor them, or that they can ignore it if
this ticket has no visual surface. This is the common case for a spec written before
the designs arrived, and the ladder cannot see it — L4b only re-hashes `D<n>` entries
that already exist, so a spec with none walks clean to L9.

Deliberately **a notice, not a rung.** A rung here would re-fire forever on any ticket
that legitimately has no visual surface, because update mode would correctly decline to
invent a `## Design` section and the condition would still hold on the next pass.
Telling the user once and letting them decide is the version that terminates.

Then hand off explicitly: **run `tiny-spec-build` when you're ready to build** (it
starts at the first unchecked task). If you stopped at L4 or on a bound, say exactly
what stopped you and what the user needs to decide.
