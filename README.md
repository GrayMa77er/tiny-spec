<p align="center">
  <img src="logo.png" alt="tiny-spec" width="200">
</p>

<h1 align="center">tiny-spec</h1>

<p align="center">A tiny, opinionated take on spec-driven development.</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://docs.claude.com/en/docs/claude-code/overview"><img src="https://img.shields.io/badge/Claude%20Code-skills-d97757.svg" alt="Claude Code"></a>
</p>

tiny-spec is a four-step workflow for Claude Code that turns a ticket into shipped,
reviewed code. You write the intent, it produces a design, a task list, and then
builds the work one task at a time. Every task is implemented by one agent and
graded by an independent reviewer that runs the real tests before anything is
committed.

It is four skills and two agents. No orchestrator, no config file, no build step.

```
spec-create  →  spec-plan  →  spec-tasks  →  spec-build
   intent         design        tasks          per-task loop
  SPEC.md      PLAN.md +       tasks.md       plan → implement → review → commit
              constitution
```

## Quickstart

Claude Code loads skills from `~/.claude/skills/` and agents from `~/.claude/agents/`.
Clone the repo and copy them in:

```sh
git clone https://github.com/GrayMa77er/tiny-spec.git
cd tiny-spec

mkdir -p "$HOME/.claude/skills" "$HOME/.claude/agents"
for s in spec-create spec-plan spec-tasks spec-build; do
  cp -R "$s" "$HOME/.claude/skills/$s"
done
cp agents/*.md "$HOME/.claude/agents/"
```

Restart Claude Code so it picks up the new skills, then run the flow in your project:

```
/spec-create   # capture intent and requirements (binds a ticket, optional)
/spec-plan     # turn the spec into a design and harden the constitution
/spec-tasks    # slice the plan into an ordered checklist
/spec-build    # build each task: implement, review, commit
```

Copying (not symlinking) keeps each install self-contained. If a skill name
collides with one you already have, rename these before copying, or install one
set at a time.

## How it works

The constitution (`constitution.md`) is the spine. `spec-create` seeds it from a
short interview, `spec-plan` hardens it with concrete engineering rules, and
`spec-build` injects it whole into every task. It holds your style, standards,
invariants, definition of done, and verification commands.

`spec-build` walks the task list top to bottom. Each task runs through one loop:

1. Plan the task against the constitution (inline, brief).
2. Implement it with a fresh `spec-build-executor` agent.
3. Review it with an independent `spec-build-reviewer` agent that runs the gate
   end to end and grades against the constitution and the task's acceptance.
4. On pass, commit the code plus a checklist tick. On fail, loop back to the
   executor with the findings. After two failed attempts it becomes a blocker.

A small `memory.md` carries operational lessons between runs, so the executor and
reviewer (which start fresh each time) don't relearn the same pitfalls.

When a task can't pass because of a gap in the design or spec, the executor stops
and logs a blocker instead of hacking around it. You fix the gap upstream in
`spec-plan` or `spec-create`, then resume. Work runs one ticket at a time and
resumes from the checklist state.

## Why it's small

A unit-green test suite is not the same as working software, so the reviewer
exercises acceptance criteria end to end and a final smoke test confirms the whole
spec. That independent review is the safeguard. It replaces the parallel-execution
machinery, ownership contracts, and scope config that larger kits carry. One task,
one commit, an external reviewer. Nothing gets added unless it earns its place.

## Project layout

Each skill is self-contained. It carries its own templates and refers to them by
relative path, with no absolute paths and no shared parent required at runtime, so
a skill folder works wherever you drop it.

```
.
  README.md                 this file
  CONTRACTS.md              maintainer reference: formats and the build loop
  CONTRIBUTING.md           how to work on the suite
  spec-create/
    SKILL.md                intent → SPEC.md (scaffold + constitution seed)
    templates/              SPEC.template.md, constitution.template.md
  spec-plan/
    SKILL.md                SPEC → PLAN.md + hardened constitution.md
    templates/              PLAN.template.md
  spec-tasks/
    SKILL.md                PLAN → tasks.md (flat ordered checklist)
    templates/              tasks.template.md
  spec-build/
    SKILL.md                the per-task plan → implement → review loop
    templates/              memory.template.md
  agents/
    spec-build-executor.md  implements one task
    spec-build-reviewer.md  reviews one task and runs the gate
```

tiny-spec creates a `.spec/` directory in your project root, never inside a skill.
It is namespaced per ticket, with a shared spine at the root:

```
.spec/
  ACTIVE                    the active ticket directory name (resolution pointer)
  constitution.md           project-wide, shared across tickets
  memory.md                 operational lessons, shared across tickets
  <ticket-id>/              one directory per ticket (PROJ-123/, gh-42/, …)
    SPEC.md  PLAN.md  tasks.md  decisions.md
```

`CONTRACTS.md` documents the formats for maintainers. The skills do not read it at
runtime; each is self-sufficient.

## Integrations

tiny-spec binds to a task platform (Jira, GitHub Issues, Azure DevOps, Monday) by
reference only: a `ticket` block in the spec and a `Refs:` footer on each
[Conventional Commit](https://www.conventionalcommits.org/en/v1.0.0/), so the
platform auto-links the work. No API calls or credentials are required.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md), and
read [AGENTS.md](AGENTS.md) before changing any skill or agent.

## License

[MIT](LICENSE)
