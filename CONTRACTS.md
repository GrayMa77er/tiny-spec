# CONTRACTS — the source of truth

This is a deliberately small spec-driven flow. A change moves
**intent → design → tasks → build**, where *build* is a per-task loop of
**plan → implement → review**, anchored by a strong, persistent **constitution**
(`constitution.md`).

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
| `spec-create` | user intent | `<ticket>/SPEC.md` (+ scaffolds `.spec/`, shared `constitution.md` seed, `ACTIVE` pointer) | Bind a ticket, capture **what** and **why** as `REQ-N` requirements. |
| `spec-plan` | `<ticket>/SPEC.md` | `<ticket>/PLAN.md`, refines shared `constitution.md` | Decide **how**. Produce the design and harden the **constitution**. |
| `spec-tasks` | `<ticket>/PLAN.md` | `<ticket>/tasks.md` | Slice the plan into a **flat, ordered checklist** of small tasks. |
| `spec-build` | `<ticket>/tasks.md`, shared `constitution.md`, shared `memory.md` | code, ticks `<ticket>/tasks.md`, appends shared `memory.md` / `<ticket>/decisions.md` | Run the **per-task loop** — plan, implement (executor), review (independent reviewer), commit. |

`<ticket>` is the **active ticket directory** under `.spec/` — see §3. Every skill
resolves it the same way: read `.spec/ACTIVE` (a one-line pointer); if absent and
exactly one ticket dir exists, use it; if several exist and no `ACTIVE`, ask the user.

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

## §3 — The artifacts (under `.spec/` in the **project root**)

`.spec/` lives in the user's project (their cwd), **never** inside a skill's
directory. Each skill is self-contained and portable: it carries its own templates
in its `templates/` folder and references them by relative path — there are no
absolute paths anywhere in the suite.

The suite works **one ticket at a time**, namespaced per ticket. Two artifacts are
**project-wide** (shared across every ticket) and live at the `.spec/` root; the
rest are **per-ticket** and live under `.spec/<ticket-id>/`:

```
.spec/
  ACTIVE             one line: the active ticket dir name (the resolution pointer)
  constitution.md    THE CONSTITUTION — project-wide, the spine of every task (shared)
  memory.md          operational lessons carried run-to-run, project-wide (shared; optional until first lesson)
  <ticket-id>/       one dir per ticket — e.g. PROJ-123/, gh-42/, ado-77/, monday-88/
    SPEC.md          intent + REQ-N requirements (+ ticket binding)
    PLAN.md          the technical design
    tasks.md         flat ordered task checklist (the execution state)
    decisions.md     log of decisions + blockers (optional until first entry)
```

**Why shared vs per-ticket:** the constitution and operational memory are
properties of the *project*, not of any one ticket (a "never X" rule or a toolchain
quirk applies to all work). Keeping them at the root avoids duplication and makes
them truly persistent. `SPEC`/`PLAN`/`tasks`/`decisions` are the work product of one
ticket and stay scoped to it.

**The slug** (the `<ticket-id>` dir name): when bound to a ticket, derive it from
the platform key — verbatim when filesystem-safe (`PROJ-123`), else normalize
(GitHub `#42`→`gh-42`, Monday item→`monday-<id>`, ADO `AB#77`→`ado-77`).
**Ad-hoc work (no ticket) is fully supported:** use a short kebab-case feature slug
(`dark-mode`) instead — the `SPEC.md` `ticket:` block is omitted and the commit
`Refs:` footer is dropped (§4.1); nothing else changes.

### §3.1 `SPEC.md` (per-ticket)
Frontmatter `status: current | stale`, `updated: <ISO date>`, and an optional
**ticket binding** block (omit the whole block if no ticket):

```yaml
ticket:
  provider: jira | github | ado | monday
  id: PROJ-123
  url: https://...
  status: In Progress     # optional manual mirror of the platform status
```

Body sections (required unless marked optional): `## Context` *(optional)*,
`## Intent` (one paragraph, no implementation detail), `## Requirements` (a list of
`REQ-N` lines — each a single user-observable, testable capability),
`## Non-goals` *(optional)*, `## Success criteria` *(optional)*,
`## Open questions` *(optional)*, `## Links` *(optional)*. The binding is
**reference-only** — its sole runtime effect is supplying the commit/PR link footer
(§4). No API calls; status is moved manually. Deeper layers are documented in
[INTEGRATIONS.md](INTEGRATIONS.md).

### §3.2 `constitution.md` — the constitution (project-wide, shared)
The **strongest, most persistent** artifact — and **project-wide**: it lives at the
`.spec/` root and anchors every ticket. Seeded by `spec-create`, hardened by
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

### §3.3 `PLAN.md` (per-ticket)
Frontmatter `status`, `updated`. Body sections (required unless marked optional):
`## Approach` (the design narrative, key decisions, trade-offs — detailed enough to
derive tasks from), `## Architecture` *(optional — components, data flow)*,
`## Requirement coverage` (each `REQ-N` → where it's addressed),
`## Risks & mitigations` *(optional)*, `## Test strategy` *(optional)*,
`## Open questions` *(optional)*. Phases are optional headings inside `## Approach`
for readability only — they do **not** parallelize or gate anything.

### §3.4 `tasks.md` — the execution state (per-ticket)
Frontmatter `status`, `updated`. Body is a single `## Tasks` checklist, executed
**top to bottom, sequentially**. Each task:

```
- [ ] T1 — <imperative description of one small slice>
  - acceptance: <one user-observable outcome that proves this task is done>
  - type: feat            # optional; the Conventional Commit type for this task's commit (defaults to feat)
  - req: REQ-1            # optional; the REQ-N this task delivers (traceability)
  - files: <comma-separated hint of files it will touch> (guidance, not a contract)
```

Ids are `T1, T2, …` in execution order. `type:` (one of the Conventional Commit
types in §4) selects the commit type at COMMIT time and defaults to `feat` if
omitted. `req:` links the task to the `REQ-N` it satisfies. `files:` is a hint for
the executor and a focus for the reviewer — **not** an enforced ownership boundary
(execution is sequential, so there are no parallel write conflicts to police). A
checked `[x]` task is done **and reviewed**; checkboxes are the source of execution
state.

### §3.5 `memory.md` — kept, lean (project-wide, shared)
Curated operational lessons that should survive across runs so the blind executor
and reviewer don't re-learn them. **Project-wide:** lives at the `.spec/` root and is
shared across every ticket (a toolchain quirk isn't ticket-specific). Each entry:
`type` (one of
`environment | pitfall | tried-rejected | hotspot`), a one-line lesson, and a
one-line **why/how-to-apply**. Append only what is **forward-acting and
operational** — a toolchain quirk, a flaky/precondition-laden gate, an abandoned
approach, a fragile area. Code-style rules go to `constitution.md`; one-off history
goes to `decisions.md`. Prune any entry a new one supersedes. Injected whole into
every executor and reviewer prompt.

### §3.6 `decisions.md` (per-ticket)
Append-only log, one per ticket. **No template** (it is created lazily by whichever
skill first logs to it, and skills can't share a template file at runtime) — instead
every entry uses this **fixed skeleton** so all logs look the same:

```
## D-NNN — <short title>
- type: decision | blocker | change
- date: <ISO date>
- affects: REQ-N, T-n     # the requirement / task ids this touches
- note: <what + why; for a blocker, name the upstream doc to fix>
```

Ids are `D-001, D-002, …`. Used for the blocker round-trip (§5) and the
change/update path (§6).

---

## §4 — The build loop (the heart of the flow)

`spec-build` processes `tasks.md` top to bottom. For the **first unchecked** task:

1. **PLAN** *(inline, brief).* Restate the task as a 2–4 step micro-plan against
   the constitution: which invariants apply, which files, which Definition-of-Done
   items and Verification commands it must satisfy. This is the executor's brief.
2. **IMPLEMENT.** Dispatch one **`spec-build-executor`** with a fresh,
   self-contained prompt (§7): the task + acceptance, the `files:` hint, the
   **whole** `constitution.md`, and the **whole** `memory.md`. It writes the code
   and returns its report. A `BLOCKER` → go to §5 (do not continue this task).
3. **REVIEW.** Dispatch one **`spec-build-reviewer`** — blind to step 2 — with the
   task + acceptance, the **whole** `constitution.md`, the changed files, and the
   Verification commands. It **runs the gate end-to-end** and checks the
   Definition of Done. Returns `PASS` or `FAIL` + findings.
4. **CONVERGE.** On `FAIL`, re-dispatch the executor with the reviewer's findings.
   Bound this to **2 fix attempts**. Still failing → treat as a blocker (§5).
5. **COMMIT + TICK.** On `PASS`: commit the **code**, then tick `[x]` in `tasks.md`
   and commit the **bookkeeping** separately. Both messages are
   **Conventional Commits** (see below). Never tick a task the reviewer did not
   pass. Never commit a red gate.
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

### §4.1 Commit format — Conventional Commits

Every commit follows [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<scope>): <description>

[optional body]

Refs: <ticket-ref>
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

- **type** — one of `feat | fix | docs | refactor | test | chore | build | ci | perf | style`.
  The code commit uses the task's `type:` field (§3.4), defaulting to `feat`.
  A breaking change adds `!` after the type/scope (`feat(api)!: …`) and/or a
  `BREAKING CHANGE: <what>` footer.
- **scope** *(optional)* — the component, or the ticket id.
- **Two commits per passed task** (keeps code history clean of planning churn):
  1. **Code commit** — `<type>(<scope>): <task description>` + the `Refs:` footer.
  2. **Bookkeeping commit** — `chore(spec): tick T<n>` + the `Refs:` footer (ticks
     the box, bumps `updated`, adds any `decisions.md` entry).
- **`Refs:` footer (reference-only ticket linking)** — derived from the active
  `SPEC.md` ticket binding (§3.1). The platform auto-links it. **Omit the footer
  entirely if no ticket is bound.** The closing keyword is reserved for the final /
  PR commit, not per-task commits:

  | Provider | Link footer (per task) | Close (final / PR) |
  |----------|------------------------|--------------------|
  | Jira     | `Refs: PROJ-123`       | active-layer smart-commit transition — see [INTEGRATIONS.md](INTEGRATIONS.md) |
  | GitHub   | `Refs: #123`           | `Closes #123` |
  | ADO      | `Refs: AB#123`         | `Fixes AB#123` |
  | Monday   | `Refs: <item-url>`     | — (no smart-commit syntax) |

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
| change the design / constitution | `PLAN.md` / `constitution.md` | `tasks.md` → stale |
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
- the **whole** `constitution.md` (the constitution)
- the **whole** `memory.md` if it exists
- (reviewer only) the **Verification commands** to run

Do **not** pass the plan, other tasks, or prior agents' chatter. The constitution
+ memory + the one task is the entire world the agent needs.

## §8 — Task-platform binding

The suite is used **one ticket at a time** against an external platform (Jira,
GitHub Issues, Azure DevOps, Monday). The binding is **reference-only**: a `ticket`
block in `SPEC.md` frontmatter (§3.1) records the id/url/provider, the per-ticket
namespacing (§3) keeps each ticket's artifacts separate, and the `Refs:` commit
footer (§4.1) lets the platform auto-link the work. There are **no API calls, no
credentials, and no config** — status is moved manually. Deeper, opt-in integration
layers (active MCP/CLI sync, PR automation, full API) are documented in
[INTEGRATIONS.md](INTEGRATIONS.md) — none are part of the core suite.
