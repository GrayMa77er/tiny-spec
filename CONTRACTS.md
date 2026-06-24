# CONTRACTS — the source of truth

This is a deliberately small spec-driven flow. A change moves
**intent → design → tasks → build**, where *build* is a per-task loop of
**plan → implement → review**, anchored by a strong, persistent **constitution**
(`conventions.md`).

This file is a **maintainer reference** for every file format and rule — the
skills do not read it at runtime (each `SKILL.md` is self-sufficient). If you
change a format here, also change the matching skeleton in the **owning skill's**
`templates/` folder and every skill that reads or writes it.

> **Design north star — earned ceremony.** This flow is deliberately small: no
> waves, no `owns:` contracts, no checkpoint matrix, no autonomous budgets, no
> orchestrator. Do **not** add a skill, artifact, agent, or knob unless it clearly
> pays for itself. When in doubt, leave it out.

---

## §1 — The skills

| Skill | Reads | Writes | Job |
|-------|-------|--------|-----|
| `spec-create` | user intent | `SPEC.md` (+ scaffolds `.spec/`, `conventions.md` seed) | Capture **what** and **why** as `REQ-N` requirements. |
| `spec-plan` | `SPEC.md` | `PLAN.md`, refines `conventions.md` | Decide **how**. Produce the design and harden the **constitution**. |
| `spec-tasks` | `PLAN.md` | `tasks.md` | Slice the plan into a **flat, ordered checklist** of small tasks. |
| `spec-build` | `tasks.md`, `conventions.md`, `memory.md` | code, ticks `tasks.md`, appends `memory.md` / `decisions.md` | Run the **per-task loop** — plan, implement (executor), review (independent reviewer), commit. |

There is **no orchestrator and no separate verify skill** — review happens
per-task inside `spec-build`. To make a change, re-run the owning upstream skill
in update mode, then re-run `spec-build`; it resumes from the checkbox state.

## §2 — Two agents (both restricted: `Read, Write, Edit, Bash, Grep, Glob` — no `Agent`)

- **`spec-build-executor`** — implements **one task**. Blind to the workflow, free
  to read the whole codebase. Returns a structured report. Never spawns agents,
  never hacks past a blocker.
- **`spec-build-reviewer`** — independently reviews **one finished task** against
  the constitution + the task's acceptance, **running the real gate** end-to-end.
  Blind to how the code was written. Returns `PASS`/`FAIL` + findings. Read-only
  on the source (it may run commands, not edit code).

The split is the point: the thing that writes the code does not grade it.

---

## §3 — The artifacts (all under `.spec/` in the **project root**)

`.spec/` lives in the user's project (their cwd), **never** inside a skill's
directory. Each skill is self-contained and portable: it carries its own templates
in its `templates/` folder and references them by relative path — there are no
absolute paths anywhere in the suite.

```
.spec/
  SPEC.md          intent + REQ-N requirements
  PLAN.md          the technical design
  conventions.md   THE CONSTITUTION — persistent rules, the spine of every task
  tasks.md         flat ordered task checklist (the execution state)
  memory.md        operational lessons carried run-to-run (optional until first lesson)
  decisions.md     log of decisions + blockers (optional until first entry)
```

### §3.1 `SPEC.md`
Frontmatter `status: current | stale`, `updated: <ISO date>`. Body: a one-paragraph
intent, then a `## Requirements` list of `REQ-N` lines — each a single
user-observable capability, testable, no implementation detail.

### §3.2 `conventions.md` — the constitution
The **strongest, most persistent** artifact. Seeded by `spec-create`, hardened by
`spec-plan`, and injected **whole** into every executor and reviewer. Seven fixed
sections (keep all, even if short):

1. **Style** — formatting, naming, language idioms.
2. **Engineering standards** — error handling, logging, testing approach, deps policy.
3. **Guiding invariants** — the non-negotiables ("never X", "always Y").
4. **Glossary** — domain terms with one-line definitions.
5. **Layout** — where things live (directory map).
6. **Definition of Done** — the bar a task must clear to be `[x]`.
7. **Verification commands** — the exact commands that constitute the gate
   (install, lint, test, build, run). This is what the reviewer executes.

### §3.3 `PLAN.md`
Frontmatter `status`, `updated`. Body: `## Approach` (the design narrative,
decisions, trade-offs), `## Requirement coverage` (each `REQ-N` → where it's
addressed). Phases are optional headings for readability only — they do **not**
parallelize or gate anything.

### §3.4 `tasks.md` — the execution state
Frontmatter `status`, `updated`. Body is a single `## Tasks` checklist, executed
**top to bottom, sequentially**. Each task:

```
- [ ] T1 — <imperative description of one small slice>
  - acceptance: <one user-observable outcome that proves this task is done>
  - files: <comma-separated hint of files it will touch> (guidance, not a contract)
```

Ids are `T1, T2, …` in execution order. `files:` is a hint for the executor and a
focus for the reviewer — **not** an enforced ownership boundary (execution is
sequential, so there are no parallel write conflicts to police). A checked `[x]` task is done
**and reviewed**; checkboxes are the source of execution state.

### §3.5 `memory.md` — kept, lean
Curated operational lessons that should survive across runs so the blind executor
and reviewer don't re-learn them. Each entry: `type` (one of
`environment | pitfall | tried-rejected | hotspot`), a one-line lesson, and a
one-line **why/how-to-apply**. Append only what is **forward-acting and
operational** — a toolchain quirk, a flaky/precondition-laden gate, an abandoned
approach, a fragile area. Code-style rules go to `conventions.md`; one-off history
goes to `decisions.md`. Prune any entry a new one supersedes. Injected whole into
every executor and reviewer prompt.

### §3.6 `decisions.md`
Append-only log. Each entry: `D-NNN` id, `type` (`decision | blocker | change`),
`date`, affected `REQ-N`/`T-N` ids, and the note. Used for the blocker round-trip
(§5) and the change/update path (§6).

---

## §4 — The build loop (the heart of the flow)

`spec-build` processes `tasks.md` top to bottom. For the **first unchecked** task:

1. **PLAN** *(inline, brief).* Restate the task as a 2–4 step micro-plan against
   the constitution: which invariants apply, which files, which Definition-of-Done
   items and Verification commands it must satisfy. This is the executor's brief.
2. **IMPLEMENT.** Dispatch one **`spec-build-executor`** with a fresh,
   self-contained prompt (§7): the task + acceptance, the `files:` hint, the
   **whole** `conventions.md`, and the **whole** `memory.md`. It writes the code
   and returns its report. A `BLOCKER` → go to §5 (do not continue this task).
3. **REVIEW.** Dispatch one **`spec-build-reviewer`** — blind to step 2 — with the
   task + acceptance, the **whole** `conventions.md`, the changed files, and the
   Verification commands. It **runs the gate end-to-end** and checks the
   Definition of Done. Returns `PASS` or `FAIL` + findings.
4. **CONVERGE.** On `FAIL`, re-dispatch the executor with the reviewer's findings.
   Bound this to **2 fix attempts**. Still failing → treat as a blocker (§5).
5. **COMMIT + TICK.** On `PASS`: commit the **code** (`T<n>: <desc>`), then tick
   `[x]` in `tasks.md` and commit the **bookkeeping** separately (`spec: tick T<n>`).
   Never tick a task the reviewer did not pass. Never commit a red gate.
6. **DISTILL.** If anything in steps 2–4 surfaced a forward-acting operational
   lesson, add a curated `memory.md` entry (§3.5).
7. **NEXT.** Interactive default: do one task, report, and continue to the next
   (pausing for the user is fine). If the user said "do it all / run it through,"
   keep looping until done or a blocker stops you. There is **no** separate
   autonomous mode and **no** checkpoint matrix — one commit per passed task, always.

When every task is `[x]`: run the Verification commands once more as a final
whole-spec smoke, report what was built + the commits + any open `decisions.md`
items. That final smoke is the only verification step — there is no separate
verify skill.

**Why no `owns:`/wave/scope validator:** tasks run one at a time in one tree,
so there are no parallel writes to attribute or police. The reviewer reading the
actual diff is the scope check.

---

## §5 — Blockers (never hack around)

If the executor cannot proceed correctly — a design gap, an impossible
requirement, a contradiction with the constitution, a missing dependency — it
**stops and reports a `BLOCKER`**, leaving the tree clean. `spec-build` then:

1. Leaves the task `[ ]`.
2. Logs it to `decisions.md` (`type: blocker`, naming the upstream doc to fix).
3. Surfaces it to the user and routes upstream: `spec-plan` (design gap) or
   `spec-create` (a requirement itself is wrong/impossible), in update mode.

After the upstream fix, re-run `spec-build`; it resumes from the checkbox state.
A genuine fork the plan doesn't pin down → don't guess: surface it with the
options + your recommendation, record the resolution in `decisions.md`.

## §6 — Changes & staleness

To change something already built, edit the **owning** upstream artifact in update
mode, which flips downstream `status: stale` and logs a `decisions.md` entry:

| Change | Edit | Effect |
|--------|------|--------|
| add/alter a requirement | `SPEC.md` | `PLAN.md`, `tasks.md` → stale |
| change the design / constitution | `PLAN.md` / `conventions.md` | `tasks.md` → stale |
| rework specific tasks | `tasks.md` | uncheck affected `[x]`, log it |

**Completed-work guardrail:** if a change touches a task already `[x]`, **uncheck
it** and log it (`type: change`) for human review — never assume built work
survived the change. Reconcile stale artifacts (re-run the owning skill in update
mode) before re-running `spec-build`.

## §7 — The executor/reviewer context contract

Each agent prompt is **fresh, minimal, and self-contained** — it carries
everything needed and nothing else:

- the task id, description, and **acceptance**
- the `files:` hint (executor) / the actual changed files (reviewer)
- the **whole** `conventions.md` (the constitution)
- the **whole** `memory.md` if it exists
- (reviewer only) the **Verification commands** to run

Do **not** pass the plan, other tasks, or prior agents' chatter. The constitution
+ memory + the one task is the entire world the agent needs.
