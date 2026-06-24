# A lean spec-driven flow

A small, opinionated pipeline that takes a change from intent to verified code,
anchored by a strong, persistent **constitution** and a per-task loop with an
independent reviewer.

**The whole flow:**

```
spec-create  →  spec-plan  →  spec-tasks  →  spec-build
  intent          design        task list      per-task loop
  (SPEC.md)     (PLAN.md +     (tasks.md)     plan → implement → review → commit
                conventions.md                       (one task at a time)
                = constitution)
```

The **constitution** (`conventions.md`) is the spine — produced by `spec-create`,
hardened by `spec-plan`, and injected whole into every task's executor and
reviewer. `spec-build` walks the task list top to bottom and runs each task
through a tight loop:

1. **plan** the slice against the constitution (inline, brief);
2. **implement** it with a fresh `spec-build-executor` subagent;
3. **review** it with an *independent* `spec-build-reviewer` subagent that runs
   the real gate end-to-end and grades against the constitution + acceptance;
4. on PASS, **commit** (code + a bookkeeping tick); on FAIL, loop back to the
   executor with findings (bounded to 2 attempts, then it's a blocker).

A lean **`memory.md`** carries operational lessons run-to-run so the blind
executor/reviewer don't re-learn them.

## Design north star — earned ceremony

Deliberately small. **No** wave/parallel model, **no** `owns:` /
scope-disjointness contracts, **no** checkpoint-granularity config, **no**
`config.yml`, **no** autonomous-mode budgets, **no** orchestrator, **no** separate
verify skill (review is per-task; a final smoke closes it out), and **no** Python
validators. One task, one tree, one commit per passed task. The independent
reviewer running the gate is the safeguard that replaces deterministic scope
machinery.

## What it guarantees

- a clear upstream chain (intent → design → tasks);
- a **strong constitution** as the persistent anchor;
- **memory** across runs;
- the **blocker round-trip** (never hack past a gap — route upstream);
- **unit-green ≠ working**: the reviewer exercises acceptance end-to-end, and a
  final smoke confirms the whole spec.

## Layout

Each skill is **self-contained** — it carries the templates it needs in its own
`templates/` folder and references them by relative path. There are **no
absolute paths and no shared parent directory** required at runtime, so a skill
folder works wherever it's dropped.

```
.
  README.md                 this file
  CONTRACTS.md              maintainer reference — the formats + the build loop
  spec-create/
    SKILL.md                intent → SPEC.md (+ scaffold + constitution seed)
    templates/              SPEC.template.md, conventions.template.md
  spec-plan/
    SKILL.md                SPEC → PLAN.md + hardened conventions.md
    templates/              PLAN.template.md
  spec-tasks/
    SKILL.md                PLAN → tasks.md (flat ordered checklist)
    templates/              tasks.template.md
  spec-build/
    SKILL.md                the per-task plan→implement→review loop
    templates/              memory.template.md
  agents/
    spec-build-executor.md  implements one task
    spec-build-reviewer.md  independently reviews one task (runs the gate)
```

`.spec/` is created in the **user's project root**, never inside a skill.
`CONTRACTS.md` is a reference for maintainers — the skills do not read it at
runtime; each is self-sufficient.

## Install / discovery

Claude Code discovers skills from `~/.claude/skills/` and agents from
`~/.claude/agents/`. Copy them there — no absolute paths to edit, the suite works
from any checkout location:

```sh
# run from the suite's root (the folder containing this README)
SUITE="$(pwd)"
mkdir -p "$HOME/.claude/skills" "$HOME/.claude/agents"
for s in spec-create spec-plan spec-tasks spec-build; do
  cp -R "$SUITE/$s" "$HOME/.claude/skills/$s"     # brings each skill's templates/ along
done
cp "$SUITE"/agents/*.md "$HOME/.claude/agents/"
```

> Copying (not symlinking) makes each install self-contained and independent of
> where the source lives. If a skill name collides with one already in
> `~/.claude/skills/`, rename these (e.g. a short prefix) first, or install only
> one set at a time. New skills/agents are discovered at startup — restart the
> session after installing.
