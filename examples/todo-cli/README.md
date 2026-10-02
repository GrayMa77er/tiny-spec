# Example: todo CLI

A **real run** of the tiny-spec suite on one small ticket — not a hand-written ideal.
Everything in this folder (the `.spec/` artifacts and the code) was produced by
actually driving `tiny-spec-create → plan → tasks → build` autonomously on
[`TICKET.md`](TICKET.md), then committed verbatim. Browse it to see exactly what the
workflow generates before you run it on your own work.

> Produced on 2026-06-29 with tiny-spec **v0.2.1**, and kept as-run rather than
> retouched to match the current artifact formats — a doctored example would defeat
> the point. Later versions add a `## Design` section to `SPEC.md` (unused here: this
> is a CLI with no design surface) and richer status flags. The shape is the same.
> One format move was applied after the fact: in 2.0 the checklist stopped being its
> own `tasks.md` and became `PLAN.md`'s `## Tasks` section, so the original `tasks.md`
> was moved there verbatim — same tasks, same ticks, no content edited.

## What's here

```
TICKET.md                     the input — a small "todo CLI" ask
.spec/
  constitution.md             the shared spine: style, standards, invariants,
                              definition of done, and the verification gate
  todo-cli/
    SPEC.md                   intent + REQ-1..REQ-9 (what "done" means)
    PLAN.md                   the design, how each requirement is covered, and
                              the ordered ## Tasks checklist, all ticked [x]
todo.py                       the produced CLI (stdlib only, 117 lines)
test_todo.py                  the produced end-to-end test (129 lines)
```

Read them in flow order: `TICKET.md` → `SPEC.md` → `PLAN.md` → `todo.py`. The `constitution.md` is the persistent context injected into every task.

## It passes its own gate

The committed code clears the gate defined in its own
[`constitution.md`](.spec/constitution.md) — the same check `tiny-spec-build-reviewer`
runs. From this directory:

```sh
python3 -m pytest test_todo.py        # 8 passed
```

And the ticket's example session reproduces exactly:

```sh
python3 todo.py add "buy milk"        # -> 1
python3 todo.py add "write tests"     # -> 2
python3 todo.py list                  # two open lines
python3 todo.py done 1
python3 todo.py list                  # 1 now shows [x]
```

> Running these creates a `todos.json` in your working directory — delete it
> afterward, and don't commit it.

## How it was generated

Driven headlessly the same way the eval harness drives its benchmark tasks: a
hermetic sandbox with the suite vendored into a local `.claude/`, seeded with
`TICKET.md`, and run via `claude -p` with instructions to complete the flow
autonomously. See [`docs/eval/harness/run.sh`](../../docs/eval/harness/run.sh) for the
exact recipe — the `DRIVER` prompt near the top is what was handed to the model.

This run finished in 55 turns at roughly $3.49 with no blockers; all five tasks
passed review on the first or second attempt.

To produce your own equivalent, point that harness recipe at this `TICKET.md`, or
just run the flow interactively in a scratch directory. Output won't be
byte-identical — the model is nondeterministic — but it will be an equivalent,
gate-passing run.
