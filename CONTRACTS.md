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
| `tiny-spec-prd` *(optional)* | a rough idea (+ optional notes/sketches, read as images) | `PRD.md` (project root — **not** a `.spec/` artifact) | Planning on-ramp: interview an idea into a short PRD. Feeds `tiny-spec-breakdown`. |
| `tiny-spec-breakdown` *(optional)* | PRD (`PRD.md` if present), wireframes (read as images), notes | `BREAKDOWN.md` (project root — **not** a `.spec/` artifact) | Planning on-ramp: decompose inputs into Features → Stories with draft ACs + `design:` refs. Feeds `tiny-spec-create`. |
| `tiny-spec-create` | user intent (+ optional `BREAKDOWN.md`, `design/` exports) | `<ticket>/SPEC.md` (+ scaffolds `.spec/` and the shared `constitution.md` seed) | Bind a ticket, capture **what** and **why** as `REQ-N` requirements. |
| `tiny-spec-plan` | `<ticket>/SPEC.md` | `<ticket>/PLAN.md`, refines shared `constitution.md` | Decide **how**. Produce the design and harden the **constitution**. |
| `tiny-spec-tasks` | `<ticket>/PLAN.md` | `<ticket>/tasks.md` | Slice the plan into a **flat, ordered checklist** of small tasks. |
| `tiny-spec-build` | `<ticket>/tasks.md`, shared `constitution.md`, shared `memory.md` | code, ticks `<ticket>/tasks.md`, appends shared `memory.md` / `<ticket>/decisions.md` | Run the **per-task loop** — plan, implement (executor), review (independent reviewer), commit. |

`<ticket>` is the **active ticket directory** under `.spec/` — see §3. Every skill
resolves it the **same way**, from the current git branch:

1. **Branch match** — the `.spec/<slug>/` whose `<slug>` appears as a token in the
   current git branch name (case-insensitive, bounded by the start/end or a `/`,
   `-`, or `_` separator). One branch per ticket, so `feature/PROJ-123-dark-mode`,
   `PROJ-123`, and `snir/gh-42-fix` resolve to `PROJ-123`, `PROJ-123`, `gh-42`.
2. **Sole dir** — if no dir matches, use the only ticket dir, if exactly one exists.
3. **Ask** — else ask the user which.

Three exceptions to that order, all to stop it resolving *confidently and wrongly*:

- **More than one dir matches** the branch (e.g. `feature/PROJ-123-gh-42` matching
  both `PROJ-123/` and `gh-42/`) — **ask**. There is no defined tie-break, and
  inventing one in any single skill makes it disagree with the others.
- **On `main`/`master` with ticket dirs present and no name match** — **ask** before
  falling through to *sole dir*. The usual cause is a forgotten `git switch`, and the
  fallback would otherwise silently adopt whatever ticket happens to exist.
- **When the caller says this is new work** (`tiny-spec-create` only) — skip *sole
  dir* entirely. It exists to find the ticket you're already on, not to adopt an old
  one for a new spec.

**Degraded, not an ask case:** detached HEAD or not a git repo. Branch match is simply
unavailable — fall through to rules 2 and 3 as written.

Every skill implements the same order **and the same exceptions**. A skill that
resolved differently from the one that invoked it would operate on a different ticket
than the caller intended, which no artifact would record.

The branch is the single source of truth for which ticket is active: parallel work
on separate branches each resolves to its own ticket, with no shared pointer file to
fall out of sync.

There is **no orchestrator and no separate verify skill** — review happens
per-task inside `tiny-spec-build`. To make a change, re-run the owning upstream skill
in update mode, then re-run `tiny-spec-build`; it resumes from the checkbox state.

## §2 — Two agents (both restricted: `Read, Write, Edit, Bash, Grep, Glob` — no `Agent`)

- **`tiny-spec-build-executor`** — implements **one task**. Blind to the workflow, free
  to read the whole codebase. Returns a structured report. Never spawns agents,
  never hacks past a blocker.
- **`tiny-spec-build-reviewer`** — independently reviews **one finished task** against
  the constitution + the task's acceptance, **running the real gate** end-to-end.
  Blind to how the code was written. Returns `PASS`/`FAIL` + findings. Read-only
  on the source (it may run commands, not edit code). On a task carrying `design:` it
  also runs the visual gate (§4.2) — its `Read` tool renders images and its `Bash`
  runs the browser, so this needs no extra tools.

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
  constitution.md    THE CONSTITUTION — project-wide, the spine of every task (shared)
  memory.md          operational lessons carried run-to-run, project-wide (shared; optional until first lesson)
  <ticket-id>/       one dir per ticket — e.g. PROJ-123/, gh-42/, ado-77/, monday-88/
    SPEC.md          intent + REQ-N requirements (+ ticket binding)
    PLAN.md          the technical design
    tasks.md         flat ordered task checklist (the execution state)
    decisions.md     log of decisions + blockers (optional until first entry)
```

> `PRD.md` (from `tiny-spec-prd`) and `BREAKDOWN.md` (from `tiny-spec-breakdown`) are
> **not** shown above on purpose — both are optional pre-spec planning files at the
> **project root**, not `.spec/` artifacts. See §3.0. Neither is `design/` — the
> committed wireframe exports are project files no skill writes, referenced by
> `SPEC.md` `D<n>` entries. See §3.1.1.

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

### §3.0 Pre-spec planning files — `PRD.md`, `BREAKDOWN.md` (project root, **not** `.spec/` artifacts)
Both are optional, regenerable, and live at the **project root** — pre-spec planning
the tracker owns, never read by the build loop and not subject to the staleness rules
(§6). They have no `status` frontmatter. They stack: `PRD.md` → `BREAKDOWN.md` → the
per-story flow.

**`PRD.md`** — written by the **optional** `tiny-spec-prd` skill from a rough idea via
a short interview. The shortest PRD that lets `tiny-spec-breakdown` carve good stories:

- **Problem / context** and **Goal & non-goals** (required) — the *why* and the
  boundary; optional `Users / personas`, `Constraints & cross-cutting`,
  `Success signals`, `Open questions`;
- a required **Core capabilities** list — each a single user-observable, testable
  capability (no implementation detail, atomic), which `tiny-spec-breakdown` carves
  into Features → Stories.

The skeleton is owned by `tiny-spec-prd` (`templates/PRD.template.md`).

**`BREAKDOWN.md`** — written by the **optional** `tiny-spec-breakdown` skill from a PRD
(`PRD.md` if present) + wireframes/notes. Read by `tiny-spec-create` in seeded mode.
Shape:

- a `## Decisions` block — Stack, Code lives, Platform, Structure lens, Scope,
  Cross-cutting — which seeds `constitution.md` (§3.2) on a story's first `create`;
- one `## Feature: <name>` heading per feature (a grouping only — features never
  become `.spec/` dirs), each with a tracker-parent id to fill in after creation;
- under each, `- Story: <title>   slug: <ado-77 | kebab>` entries with `- AC:` lines
  and an optional `- design:` line naming the wireframes that cover that story,
  each a single user-observable, testable capability (draft `REQ-N`).

`tiny-spec-create` maps a chosen story's `AC:` lines → `REQ-N` and the Decisions block
→ the constitution. The skeleton is owned by `tiny-spec-breakdown`
(`templates/BREAKDOWN.template.md`).

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
`## Design` *(optional)*, `## Non-goals` *(optional)*, `## Success criteria`
*(optional)*, `## Open questions` *(optional)*, `## Links` *(optional)*. The binding is
**reference-only** — its sole runtime effect is supplying the commit/PR link footer
(§4). No API calls; status is moved manually. Deeper layers are documented in
[INTEGRATIONS.md](INTEGRATIONS.md).

#### §3.1.1 `## Design` — the `D<n>` screen entries *(optional)*
Present only for tickets with a visual surface. One entry per screen or surface:

```
- D1 — <screen name>
  - source: <Figma URL#node-id, or the tool of record>
  - export: design/<file>.png     # the committed artifact an agent can actually read
  - sha256: <hash of that export> # the staleness signal
  - layout: <arrangement, max width, and the ORDER elements appear in>
  - elements:
    - <name>  `<selector>`  → <the tokens this element must satisfy>
  - states: <which of empty / loading / error / success this surface renders>
```

The **constitution's Design system is the vocabulary; a `D<n>` is one screen's
sentence in it.** That is the two-level split — a global spec plus a per-screen
composition whose parts only specialize the global — and it is what keeps screens
coherent instead of each drifting its own way.

Three rules make it load-bearing rather than decorative:

- **Token names only.** `layout`, `elements`, and `states` may reference only tokens
  the constitution's **Design system** defines. A raw `24px` or `#3B82F6` in a `D`
  entry is a violation — it is how per-screen drift starts, and it is cheaply
  greppable.
- **Selectors are a contract, not a hint** — the one place a `.spec/` artifact names
  something the code must match verbatim (contrast `files:` in §3.4, which is
  guidance). The reviewer measures exactly these selectors; a selector matching
  nothing is a `FAIL`, never a skip, because a silently-unmatched selector turns the
  visual gate into theater. Prefer a stable test id over a CSS class: classes are
  renamed by refactors and mangled by CSS-in-JS. An executor that cannot use a given
  selector raises a **blocker** rather than substituting its own.
- **The anchor must fail loudly.** `sha256` is recomputed by `tiny-spec-create` update
  mode; a mismatch means the design moved under the spec, and a missing `export` file
  stops the run. A link that 404s silently is worse than no link, because it
  manufactures false confidence.

A `REQ-N` that a design bears on names its screen inline (`REQ-3 — … (D1)`), which is
what makes `frame → REQ → task → files` greppable in both directions.

**`design/` is a convention, not an artifact.** Exported wireframes/mockups live in a
`design/` directory at the **project root**, committed alongside the code — like
`PRD.md` and `BREAKDOWN.md` (§3.0), it is outside `.spec/` and **no skill writes it**.
tiny-spec reads what is there and records provenance in `SPEC.md`; it never fetches
from Figma, requires an API token, or depends on a design SaaS. A view-only design
tool is fully supported: export, commit, and the `source:` line keeps the trail back.

### §3.2 `constitution.md` — the constitution (project-wide, shared)
The **strongest, most persistent** artifact — and **project-wide**: it lives at the
`.spec/` root and anchors every ticket. Seeded by `tiny-spec-create`, hardened by
`tiny-spec-plan`, and injected **whole** into every executor and reviewer. Seven fixed
sections (keep all, even if short) plus one conditional:

1. **Style** — formatting, naming, language idioms.
2. **Design system** *(conditional — the only omittable section)* — the project-wide
   UI contract as **named tokens** (`color.*`, `space.*`, `type.*`, `radius.*`,
   `elevation.*`) plus the states every interactive surface must define. Present only
   when the project has a visual surface; omitted entirely for a CLI, library, or
   headless service rather than left empty. Seeded by `tiny-spec-create` from the
   designs (propose a coherent scale, don't measure per screen), hardened by
   `tiny-spec-plan` into values a reviewer can fail a task on.
3. **Engineering standards** — error handling, logging, testing approach, deps policy.
4. **Guiding invariants** — the non-negotiables ("never X", "always Y").
5. **Glossary** — domain terms with one-line definitions.
6. **Layout** — where things live (directory map).
7. **Definition of Done** — the bar a task must clear to be `[x]`.
8. **Verification commands** — the exact commands that constitute the gate
   (install, lint, test, build, run). This is what the reviewer executes. Adds an
   optional **`visual:`** command where there is a Design system: what boots the UI so
   the reviewer can read back `getComputedStyle`/`getBoundingClientRect`. It is a
   precondition for the visual gate (§4.2) — a `design:` task with no `visual:`
   command is a blocker, never a silent pass.

**Why tokens rather than a screenshot or a description.** A token name is the most
durable anchor available: semantic, diffable, and stable across a visual redesign. An
image records what a screen looked like once, cannot be asserted against, and rots
undetectably. Naming tokens DTCG-style also means a Style Dictionary / Tokens Studio
pipeline can be adopted later at no cost — but none is required, and the suite has no
dependency on Figma, a token tool, or any design SaaS.

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
  - design: D1            # optional; the SPEC.md D<n> this task builds — arms the visual gate (§4.2)
  - files: <comma-separated hint of files it will touch> (guidance, not a contract)
```

Ids are `T1, T2, …` in execution order. `type:` (one of the Conventional Commit
types in §4) selects the commit type at COMMIT time and defaults to `feat` if
omitted. `req:` links the task to the `REQ-N` it satisfies. `files:` is a hint for
the executor and a focus for the reviewer — **not** an enforced ownership boundary
(execution is sequential, so there are no parallel write conflicts to police). A
checked `[x]` task is done **and reviewed**; checkboxes are the source of execution
state.

`design:` is the **only field that changes how a task is graded** — it is the explicit
opt-in to the visual gate (§4.2). Set it on tasks that build the visible surface, not
on the API call behind it; the gate is per-task precisely so the blast radius is a
deliberate choice rather than a project-wide mode. Every `D<n>` in `SPEC.md` should be
claimed by at least one task, and a task may only carry `design:` if the constitution
has a `visual:` command.

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

`tiny-spec-build` processes `tasks.md` top to bottom. For the **first unchecked** task:

1. **PLAN** *(inline, brief).* Restate the task as a 2–4 step micro-plan against
   the constitution: which invariants apply, which files, which Definition-of-Done
   items and Verification commands it must satisfy. This is the executor's brief.
2. **IMPLEMENT.** Dispatch one **`tiny-spec-build-executor`** with a fresh,
   self-contained prompt (§7): the task + acceptance, the `files:` hint, the
   **whole** `constitution.md`, and the **whole** `memory.md`. It writes the code
   and returns its report. A `BLOCKER` → go to §5 (do not continue this task).
3. **REVIEW.** Dispatch one **`tiny-spec-build-reviewer`** — blind to step 2 — with the
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

### §4.2 The visual gate (only on tasks carrying `design:`)

A task without `design:` is graded exactly as it always was — steps 1–3 of the
reviewer, unchanged. With it, the reviewer adds a fourth step:

1. **Precondition.** No `visual:` command in the constitution → **blocker**, routed to
   `tiny-spec-plan`. Never a silent skip and never resolved by dropping the `design:`
   field: a checked box would then claim a verification that never ran.
2. **Measure every named selector, don't diff.** Run `visual:` against each row of the
   `D<n>`'s `elements:`, read back `getComputedStyle()` / `getBoundingClientRect()`,
   and compare to the tokens that row names. **A selector matching nothing is a
   `FAIL`, never a skip** — otherwise the gate measures less and less as the markup
   drifts, while still reporting green. **Pixel-diffing a screenshot is explicitly not
   the mechanism** — font antialiasing makes image comparison flaky enough that the
   check gets muted, which is how visual gates die. Numeric assertions are stable
   under exactly that noise.
3. **Check `layout:`** — arrangement, max width, and the order the entry names, from
   the bounding rectangles. Every token can be right on an element in the wrong place.
4. **Exercise every state** the `D<n>` names (empty, loading, error, success). Drive
   the UI into each; a source-text match is not evidence and false-passes routinely.
   A surface that renders only its happy path is a fail — generated UI passing a
   functional check while missing its states is the single most common failure mode.
5. **Read the export image** as a cross-check for what numbers can't catch (a missing
   element, wrong hierarchy).

**Verdict split — deliberate, and the one place "when torn, fail" does not apply.**
Measurable violations (an unmatched selector, off-scale value, undefined token,
hardcoded value where a token exists, contradicted order, a named state that doesn't
render) **fail**. Subjective impressions are recorded as `flag:` findings and do
**not** fail the task: convergence is bounded at 2 attempts (§4), so failing on taste
blocks a task on something no executor can fix.

## §5 — Blockers (never hack around)

If the executor cannot proceed correctly — a design gap, an impossible
requirement, a contradiction with the constitution, a missing dependency — it
**stops and reports a `BLOCKER`**, leaving the tree clean. `tiny-spec-build` then:

1. Leaves the task `[ ]`.
2. Logs it to `decisions.md` (`type: blocker`, naming the upstream doc to fix).
3. Surfaces it to the user and routes upstream: `tiny-spec-plan` (design gap) or
   `tiny-spec-create` (a requirement itself is wrong/impossible), in update mode.

After the upstream fix, re-run `tiny-spec-build`; it resumes from the checkbox state.
A genuine fork the plan doesn't pin down → don't guess: surface it with the
options + your recommendation, record the resolution in `decisions.md`.

## §6 — Changes & staleness

To change something already built, edit the **owning** upstream artifact in update
mode, which flips downstream `status: stale` and logs a `decisions.md` entry:

| Change | Edit | Effect |
|--------|------|--------|
| add/alter a requirement | `SPEC.md` | `PLAN.md`, `tasks.md` → stale |
| a design export changed (`sha256` mismatch) | `SPEC.md` — re-read the export, update the `D<n>` entry + hash | `PLAN.md`, `tasks.md` → stale (it is a requirement change) |
| change the design / constitution | `PLAN.md` / `constitution.md` | `tasks.md` → stale |
| change **Design system** token values | `constitution.md` | **every** ticket's `tasks.md` with `[x]` visual work → stale (it is project-wide) |
| rework specific tasks | `tasks.md` | uncheck affected `[x]`, log it |

**Completed-work guardrail:** if a change touches a task already `[x]`, **uncheck
it** and log it (`type: change`) for human review — never assume built work
survived the change. Reconcile stale artifacts (re-run the owning skill in update
mode) before re-running `tiny-spec-build`.

## §7 — The executor/reviewer context contract

Each agent prompt is **fresh, minimal, and self-contained** — it carries
everything needed and nothing else:

- the task id, description, and **acceptance**
- the `files:` hint (executor) / the actual changed files (reviewer)
- the **whole** `constitution.md` (the constitution)
- the **whole** `memory.md` if it exists
- (reviewer only) the **Verification commands** to run
- **only if the task carries `design:`** — that `D<n>` entry verbatim from `SPEC.md`
  and its `export:` path, to both agents

Do **not** pass the plan, other tasks, or prior agents' chatter. The constitution
+ memory + the one task is the entire world the agent needs. The `D<n>` entry is the
one conditional addition, and it stays within that rule: it is part of *this* task's
definition of done, not context about the wider spec — the agents get one screen, not
the `## Design` section.

## §8 — Task-platform binding

The suite is used **one ticket at a time** against an external platform (Jira,
GitHub Issues, Azure DevOps, Monday). The binding is **reference-only**: a `ticket`
block in `SPEC.md` frontmatter (§3.1) records the id/url/provider, the per-ticket
namespacing (§3) keeps each ticket's artifacts separate, and the `Refs:` commit
footer (§4.1) lets the platform auto-link the work. **One branch per ticket** is the
team convention: name the branch after the ticket slug (e.g. `PROJ-123` or
`feature/PROJ-123-dark-mode`) so the active-ticket resolution (§1) picks it up from
the branch — letting several tickets be in flight on separate branches at once, each
resolving to its own artifacts. There are **no API calls, no
credentials, and no config** — status is moved manually. Deeper, opt-in integration
layers (active MCP/CLI sync, PR automation, full API) are documented in
[INTEGRATIONS.md](INTEGRATIONS.md) — none are part of the core suite.
