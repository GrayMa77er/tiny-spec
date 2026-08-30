# Constitution

> This is the strongest, most persistent document in the project. It is
> **project-wide** — it lives at the `.spec/` root and anchors *every* ticket, not
> any one of them. Every task is implemented and reviewed against it. Keep it true;
> keep it lean. Project-specific richness belongs here — not scattered across tasks.

## Style
- Python 3, PEP 8. Single file `todo.py` at the project root.
- Standard library only — no third-party imports.
- Clear, small functions; a `main()` entry point dispatching on the command.

## Engineering standards
- Error handling: invalid input (unknown id, empty text, bad usage) writes a short
  message to **stderr** and exits with a **non-zero** status. Success writes to stdout.
- Persistence: read/write a human-readable `todos.json` in the current working
  directory. Tolerate a missing file (treat as empty); create it on first write.
- "Tested" means: the example session from the ticket reproduces exactly, and the
  error/persistence behaviours are exercised by a script-driven check.
- No dependencies beyond CPython's standard library.

## Guiding invariants
- Never reuse a task id after removal — ids only ever increase.
- Always assign ids as positive integers in increasing order.
- `list` output is ordered by id ascending; open tasks render `<id>. [ ] <text>`,
  done tasks `<id>. [x] <text>`.
- `list` with no tasks prints nothing and exits 0.
- The store file stays valid, human-readable JSON across invocations.

## Glossary
- **task** — a record with an integer `id`, a `text` string, and a `done` boolean.
- **store** — the `todos.json` file holding all tasks plus the id counter.

## Layout
- `todo.py` — the entire CLI, at the project root.
- `todos.json` — the runtime store, created in the cwd on first write (not committed).

## Definition of Done
- Code matches the invariants above; gate is green; no TODOs left.
- The ticket's example session reproduces exactly (ids, checkboxes, ordering).
- Tasks persist across separate process invocations.
- Unknown-id and empty-text operations exit non-zero with a stderr message.

## Verification commands
- run:  `python3 todo.py <command> [args]`
- test: run the ticket example session end-to-end in a clean temp dir and assert
  the exact stdout, exit codes, and that `todos.json` persists between invocations:
  `python3 todo.py add "buy milk"` → `1`; `add "write tests"` → `2`;
  `list` → two open lines; `done 1`; `list` shows `[x]` on id 1; `remove 2`;
  `list` shows only `1. [x] buy milk`. Also assert `done 99`, `remove 99`,
  and `add ""` each exit non-zero with stderr output.
