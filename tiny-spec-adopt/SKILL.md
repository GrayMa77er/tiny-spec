---
name: tiny-spec-adopt
description: The brownfield on-ramp — onboard an EXISTING codebase by deriving the shared constitution (.spec/constitution.md) from the code that is actually there: the real lint/test/build commands, the real layout, the real conventions. Read-only analysis; it never creates a ticket dir, writes SPEC.md, or touches git. Run once per project before the first tiny-spec-create, and re-run in refresh mode after the codebase drifts. For a project with no code yet, use tiny-spec-scope instead.
---

# tiny-spec-adopt

The **brownfield front door**. Most real work is a ticket inside a system that already
exists — the stack, the layout, the test command, and the conventions are all already
decided, written down in config files and visible in the code. Interviewing a user about
them is asking for a worse copy of something you can read.

This skill reads the codebase and writes `.spec/constitution.md` from what's actually
there, then stops. It does **not** create a ticket dir, write a `SPEC.md`, switch
branches, or modify a single line of source.

**Starting from a blank page instead?** Use `tiny-spec-scope` — it interviews an idea
into stories. The two are the suite's two front doors, and you generally want exactly
one of them.

## The one thing that matters most

The constitution is injected **whole** into every executor and reviewer, for the life of
the project. Its **Verification commands** block is the gate the reviewer literally
executes. So:

> **A derived gate that has never been run is the most dangerous thing this skill can
> produce.** A command that looks plausible and silently fails, or passes vacuously,
> turns every future review into theatre. Run the commands you derive. If one doesn't
> work from a clean checkout, say so rather than writing it down.

## Pick your mode

| If | Mode |
|---|---|
| `.spec/constitution.md` does not exist | **derive** — the normal first run |
| it exists and the user wants it re-derived after the codebase moved | **refresh** — diff, don't overwrite |

In refresh mode, never overwrite silently. Re-derive, show the user a section-by-section
diff against what's there, and apply only what they accept — then propagate staleness
(below), because a constitution change invalidates work that was reviewed against the
old one.

## Step 1 — map the codebase

Derive, don't ask. Work through the four dimensions below. On anything larger than a
small repo this is a genuine fan-out, so you may dispatch **read-only `Explore` agents**,
one per dimension, and synthesize their reports.

> This is the only skill in the suite that dispatches agents for anything but the build
> loop. It earns it: the alternative is either a shallow constitution or a long
> interview about facts already on disk. It stays read-only, runs once per project, and
> writes exactly one file.

**A declared source always beats inference.** If the project says something about itself,
that wins over what you'd guess from reading code.

### 1. Verification commands — the highest-value output

Read them off the real config, in this order of authority:

- **CI is the strongest signal** — `.github/workflows/*.yml`, `.gitlab-ci.yml`,
  `Jenkinsfile`. Whatever CI runs on every PR *is* the project's real gate; nothing a
  contributor says outranks it.
- **Task runners** — `package.json` `scripts`, `Makefile` targets, `justfile`,
  `Taskfile.yml`, `pyproject.toml` (`[tool.poetry.scripts]`, `[project.scripts]`),
  `Cargo.toml`, `build.gradle`, `composer.json`.
- **Tool config that implies a command** — `pytest.ini`/`tox.ini`, `jest.config`,
  `vitest.config`, `.eslintrc`, `ruff.toml`, `.golangci.yml`.

Map them onto `install / lint / test / build / run`. A stage the project genuinely
doesn't have is **omitted**, not invented — a `build:` line on a project with no build
step is a command that will fail for the rest of time.

**Then run them.** Report which passed, which failed, and which you couldn't run
(needs credentials, a service, a device). A command you could not verify goes in marked
as unverified, or not at all.

### 2. Layout

From the actual directory tree and where each kind of file already lives — source,
tests, config, docs, migrations, assets. Say where **new** code of each kind goes, since
that is what the executor needs. Note the convention as it is, not as it should be: if
tests sit beside their source, write that down even if you'd prefer a `tests/` root.

### 3. Style & engineering standards

From formatter and linter config first (`.editorconfig`, `prettier`, `ruff`, `black`,
`eslint`, `rustfmt`, `.clang-format`) — these are declared and enforced, so they win.
Then observed idiom in the largest source directories: naming, error handling, logging,
how dependencies get added, and **what "tested" means here** (framework, unit vs
integration, whether coverage is enforced, whether new code is expected to ship tests).

### 4. Guiding invariants & glossary — look for declared ones first

Read `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`, `docs/adr/*`, and any
architecture notes. Rules a human already wrote down are **declared** invariants and are
worth ten inferred ones — carry them over close to verbatim.

Only then infer from the code, and only for rules a reviewer could actually **fail a
task on**: "all timestamps are UTC ISO-8601", "no network calls in unit tests", "every
endpoint returns the shared error envelope". Concrete, checkable. Never aspirational —
"write clean code" fails nothing and costs context forever.

Build the **glossary** from domain terms that recur in module, model, and table names.

**Skip `## Design system` entirely.** Deriving a token system from existing CSS produces
a catalogue of what the drift already is, not a contract. If this project has a visual
surface, `tiny-spec-design` builds that section properly from the designs.

## Step 2 — write the constitution

Write `.spec/constitution.md` (creating `.spec/` if needed — but **nothing else** in it).
Use this structure, dropping the indentation when you write the file:

```markdown
# Constitution

> This is the strongest, most persistent document in the project. It is
> **project-wide** — it lives at the `.spec/` root and anchors *every* ticket, not
> any one of them. Every task is implemented and reviewed against it. Keep it true;
> keep it lean. Project-specific richness belongs here — not scattered across tasks.

## Style
<Formatting, naming, language idioms. The defaults a reader should assume.>

## Engineering standards
<Error handling, logging, testing approach, dependency policy, what "tested" means here.>

## Guiding invariants
<The non-negotiables. "Never X." "Always Y." The rules a reviewer can fail a task on.>

## Glossary
<Domain term — one-line definition. Keep the team speaking one language.>

## Layout
<Where things live. Directory map. Where new code of each kind goes.>

## Definition of Done
<The bar a task must clear to be checked off: e.g. code + tests + docs updated,
gate green, no TODOs left, matches the invariants above.>

## Verification commands
<The exact gate. The reviewer runs these. Omit any stage this project doesn't have.
- install: `...`
- lint:    `...`
- test:    `...`
- build:   `...`
- run:     `...`
>
```

**Mark provenance on every section.** End each with one line — `<!-- declared: from
.github/workflows/ci.yml -->` or `<!-- inferred: from 40 files under src/api -->`. It
costs a line and tells the next reader, and the next you, exactly which parts to
distrust. `tiny-spec-plan` hardens the inferred ones; it can only do that if it can see
which they are.

**A `## Design system` section is `tiny-spec-design`'s** — leave it absent. A dead
design heading is worse than none: it gets injected into every prompt forever.

**If a `BREAKDOWN.md` exists** at the project root, fold its `## Decisions` block in
where the codebase is silent — but the code wins on every point where they disagree,
and say so when they do. A stale Decisions block describing an older stack is a common
way to poison an otherwise good derivation.

## Step 3 — confirm, then report honestly

Present what you derived, **separating declared from inferred**, and ask only what you
genuinely could not read off disk. Then report:

- the **verification commands** and which ones you actually ran green — call out any
  that failed or that you couldn't run;
- which sections are **inferred and need review**;
- anything the codebase contradicted itself about (two test runners, a CI command that
  doesn't match the Makefile) — name both and let the user pick.

Say plainly that inferred sections need review before the first build.

## Refresh mode — propagating a change

A constitution change invalidates work reviewed against the old one, so after applying
any accepted change:

For **each** ticket dir under `.spec/` whose `tasks.md` has checked tasks, set it
`status: stale` and log a `decisions.md` entry in that ticket, creating the file if
absent:

```
## D-NNN — <short title>
- type: change
- date: <ISO date>
- affects: constitution
- note: <what changed, and that completed tasks were reviewed against the previous version>
```

The constitution is project-wide, so this applies across **every** ticket, not just the
one you happen to be on. Never assume built work survived a constitution change.

## Hard rules

- **Read-only against the codebase.** Never modify, refactor, format, or "fix" a single
  line of source. You are describing this project, not improving it.
- **Never create a ticket dir, write `SPEC.md`, or touch git.** No branches, no commits.
  That is `tiny-spec-create`'s and `tiny-spec-build`'s work.
- **Never invent a verification command.** An omitted stage is correct; a plausible
  command that doesn't work is a gate that silently never fires.
- **Never invoke `tiny-spec-adopt`.** Re-entering means re-reading these steps.

## When done

Report as above, then point the user at **`tiny-spec-create`** to spec their first
ticket — or at `tiny-spec-run`, which picks the ladder up from here.
