---
status: current
updated: 2026-06-29
---

# Plan — todo CLI

## Approach

One file, `todo.py`, standard library only. Structure it as a thin set of pure-ish
functions over an in-memory store dict, plus a `main()` that loads the store,
dispatches on `argv[1]`, mutates, and saves.

Store shape (`todos.json`):

```json
{ "next_id": 3, "tasks": [ {"id": 1, "text": "buy milk", "done": true} ] }
```

`next_id` is a monotonic counter persisted in the store — this is how ids are never
reused after removal (removing a task does not roll back the counter). It starts at 1.

Functions:
- `load_store(path) -> dict` — return parsed JSON, or `{"next_id": 1, "tasks": []}`
  if the file is missing. (Tolerate absent file; do not create on read.)
- `save_store(path, store)` — write pretty-printed JSON (`indent=2`) so the file is
  human-readable.
- `cmd_add(store, text)` — strip/validate text; on empty raise a usage error; else
  append `{"id": next_id, "text": text, "done": False}`, bump `next_id`, print the
  new id.
- `cmd_list(store)` — iterate tasks sorted by id, print `<id>. [ ] <text>` or
  `<id>. [x] <text>`. No tasks → print nothing.
- `cmd_done(store, id)` — find by id; mark `done=True`; unknown id → error.
- `cmd_remove(store, id)` — find by id; drop it; unknown id → error.
- `main(argv)` — parse command + args, validate usage (missing/extra args, non-int
  ids), call the right handler, save only on a successful mutation, return an exit
  code. A small `die(msg)` helper prints to stderr and exits non-zero.

Errors (empty add text, unknown id, bad/missing args, unknown command) all go
through `die()`: short message to stderr, non-zero exit. Successful reads/writes go
to stdout. Save the store after add/done/remove; `list` never writes.

The store path is `todos.json` in the current working directory. Resolve it at call
time (not import time) so tests can run in a temp cwd.

## Requirement coverage

- REQ-1 — `cmd_add` prints the new id; `main` dispatches `add`.
- REQ-2 — persisted `next_id` counter, only ever incremented; `remove` never decrements it.
- REQ-3 — `cmd_add` rejects empty/whitespace-only text via `die()` before mutating.
- REQ-4 — `cmd_list` renders sorted tasks with `[ ]`/`[x]` checkbox format.
- REQ-5 — `cmd_list` prints nothing for an empty task list; `main` returns 0.
- REQ-6 — `cmd_done` sets `done=True` for the matching id.
- REQ-7 — `cmd_remove` deletes the matching task.
- REQ-8 — `cmd_done`/`cmd_remove` call `die()` when no task matches the id.
- REQ-9 — `load_store`/`save_store` persist to `todos.json`; missing file tolerated, created on first write with `indent=2`.

## Test strategy

A script-driven end-to-end check in a clean temp cwd that runs the ticket's exact
example session and asserts stdout + exit codes line by line, then asserts that a
fresh process sees the persisted state (`todos.json` survives). Negative cases:
`add ""`, `done 99`, `remove 99`, and a non-integer id each exit non-zero with
stderr output.
