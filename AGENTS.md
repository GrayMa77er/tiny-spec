# AGENTS.md — working on this skill suite

Guidance for any agent (Claude Code or otherwise) editing this folder.

## What this is

A lean spec-driven flow: `tiny-spec-create` → `tiny-spec-plan` → `tiny-spec-tasks` →
`tiny-spec-build`, anchored by a strong **constitution** (`constitution.md`) and a
per-task loop of **plan → implement → review → commit** with an *independent*
reviewer. See [README.md](README.md) for the shape and [CONTRACTS.md](CONTRACTS.md)
for the formats and rules of record.

## North star — earned ceremony

This suite is deliberately small. Do **not** grow it back into waves, `owns:`
contracts, a checkpoint matrix, autonomous budgets, an orchestrator, or
validators. Before adding a skill, agent, artifact, format field, or knob, the bar
is: *does it clearly pay for itself, or is it ceremony?* When in doubt, leave it
out. A change that makes this bigger needs a strong reason; a change that makes it
smaller usually doesn't.

Two structural choices are **intended**, not drift — don't "simplify" them away:
the **per-ticket namespacing** under `.spec/<ticket-id>/` with a shared
`constitution.md`/`memory.md` spine (the suite works one ticket at a time against an
external platform), and the **richer SPEC/PLAN templates** whose extra sections are
all marked optional (`<!-- optional -->`) so they add shape without forcing
ceremony. Keep new template sections optional unless a section truly must always be
filled.

## ⚠️ After making changes — validate (don't skip)

Editing a `SKILL.md` or agent file is editing a **prompt**, not code — bugs are
silent (no compiler, no test will catch a misleading instruction). So:

1. **Keep the contract consistent — by hand.** There are *no* Python validators by
   design. A format or rule change must land in **all three**: `CONTRACTS.md`
   (rules of record), the matching skeleton in the **owning skill's** `templates/`
   folder, and **every** skill or agent that reads/writes that artifact. Grep for
   the artifact name and the token you changed; reconcile every hit. The artifacts
   split **project-wide vs per-ticket** (see `CONTRACTS.md` §3): `constitution.md`
   and `memory.md` are **shared** at the `.spec/` root; `SPEC.md`, `PLAN.md`,
   `tasks.md`, `decisions.md` live under `.spec/<ticket-id>/`, resolved via the
   `.spec/ACTIVE` pointer. `decisions.md` has no template on purpose — it's an
   append-only log with a fixed inline skeleton (`CONTRACTS.md` §3.6). Each template
   has exactly one owning skill that copies it: `tiny-spec-create` (SPEC + constitution),
   `tiny-spec-plan` (PLAN), `tiny-spec-tasks` (tasks), `tiny-spec-build` (memory). **Commits are
   Conventional Commits** (`CONTRACTS.md` §4.1) — the format lives in `tiny-spec-build`
   and `CONTRACTS.md`; reconcile both if you change it.
2. **Dry-run in a throwaway sandbox** (`/tmp/...`, `git init`). A **new** skill or
   agent can't be invoked the session it's added (both load at startup). Validate
   one of three ways: follow the `SKILL.md` **verbatim** yourself; dispatch a
   built-in stand-in (`Explore` for read-only, `general-purpose` for writing) with
   the same prompt; or — once installed — dispatch the real agents
   (`tiny-spec-build-executor`, `tiny-spec-build-reviewer`) directly. Confirm the
   instructions, followed exactly, produce contract-conforming output.
3. **Runtime-verify — never static-only.** The core belief here: **unit-green ≠
   working.** A passing test suite is necessary, not sufficient. The whole reason
   `tiny-spec-build-reviewer` runs the real gate end-to-end and exercises the
   acceptance is to catch this — so when you change the build loop, prove it on a
   real task, don't infer it from the prose reading correctly.
4. **Trip the safeguards on purpose** when you touch the build/executor/reviewer
   machinery. These must stay caught:
   - a task that **passes a narrow self-check but fails the gate / acceptance** →
     the reviewer must return `FAIL`, and `tiny-spec-build` must loop back (not tick);
   - an executor that hits a real **blocker** → it must STOP and report
     `blocked` (never hack past), and `tiny-spec-build` must leave the task `[ ]` and
     route upstream;
   - **convergence bound:** a task that stays red past 2 fix attempts must become
     a blocker, not an infinite grind;
   - **memory round-trip:** an operational lesson surfaced during a build must
     land as a curated `memory.md` entry and be injected into the *next*
     executor/reviewer prompt — not re-learned;
   - **completed-work guardrail:** an upstream change that touches a `[x]` task
     must **uncheck** it and log it for review.
5. **Clean up.** Remove the sandbox. Never commit a `.spec/` from a test run or
   any build artifacts into this folder.

## Portability — no absolute paths

This suite must run for **anyone on any machine**. So:

- **No hardcoded absolute paths** (no `/Users/...`, no machine-specific dirs).
  Each skill is **self-contained**: it carries its templates in its own
  `templates/` folder and references them by **relative** path ("this skill's
  `templates/<name>`"). A skill folder works wherever it's installed.
- **No shared parent required at runtime.** `CONTRACTS.md` is a maintainer
  reference only — the skills do not read it when they run; each `SKILL.md` is
  self-sufficient. Keep it that way: if you add a rule a skill needs, inline it in
  the skill, don't make the skill depend on reading `CONTRACTS.md`.
- **The two agents are referenced by name** (`tiny-spec-build-executor`,
  `tiny-spec-build-reviewer`), not by path — they must be installed in
  `~/.claude/agents/` for `tiny-spec-build` to dispatch them.
- **Project root vs skill** — `.spec/` and the user's code live in the user's cwd
  (the project root); it is **never** created inside a skill's directory.

## Install / discovery

Skills install to `~/.claude/skills/` and agents to `~/.claude/agents/` (**copied**,
so each install is self-contained — see [README.md](README.md) for the commands).
If a skill name collides with one already installed, rename these or install only
one set at a time. New skills/agents load at startup — restart the session after
installing.

## Commits

One commit per logical change, in **Conventional Commits** format
(`<type>(<scope>): <description>`), ending with the trailer:

```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```

This is the same format the suite itself now emits (`CONTRACTS.md` §4.1) — use it
for work *on* the suite too (e.g. `feat(commits): adopt conventional commits`,
`docs: add INTEGRATIONS.md`). Only commit work once it's validated per the checklist
above.
