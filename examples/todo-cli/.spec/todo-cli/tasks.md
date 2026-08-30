---
status: current
updated: 2026-06-29
---

<!-- progress: all tasks done -->
# Tasks — todo CLI

> Executed top to bottom, one at a time. A checked `[x]` task is implemented AND
> reviewed. `type:` and `req:` are optional; `files:` is a hint, not an ownership
> contract.

## Tasks

- [x] T1 — Scaffold `todo.py`: store load/save and `main()` dispatch skeleton
  - acceptance: `python3 todo.py` (no/unknown command) prints a short usage error to stderr and exits non-zero; `load_store` returns `{"next_id": 1, "tasks": []}` when `todos.json` is absent and `save_store` writes human-readable (`indent=2`) JSON; running a valid no-op path does not crash.
  - type: feat
  - req: REQ-9
  - files: todo.py

- [x] T2 — Implement `add <text>`
  - acceptance: `python3 todo.py add "buy milk"` prints `1`, a second `add` prints `2`; ids come from a persisted `next_id` counter that only increases; `add ""` (empty/whitespace) prints a stderr error, exits non-zero, and adds nothing.
  - type: feat
  - req: REQ-1, REQ-2, REQ-3
  - files: todo.py

- [x] T3 — Implement `list`
  - acceptance: with two open tasks, `list` prints `1. [ ] buy milk` then `2. [ ] write tests` in id order; with no tasks it prints nothing and exits 0; done tasks render with `[x]`.
  - type: feat
  - req: REQ-4, REQ-5
  - files: todo.py

- [x] T4 — Implement `done <id>` and `remove <id>`
  - acceptance: `done 1` then `list` shows `1. [x] buy milk`; `remove 2` then `list` omits id 2; `done 99` and `remove 99` (unknown id) each print a stderr error and exit non-zero; ids of remaining tasks are unchanged and not reused.
  - type: feat
  - req: REQ-6, REQ-7, REQ-8, REQ-2
  - files: todo.py

- [x] T5 — End-to-end verification of the ticket example session and persistence
  - acceptance: a script run in a clean temp cwd reproduces the ticket's example session exactly (ids, checkboxes, ordering) across separate `python3 todo.py` invocations, confirms `todos.json` persists state between processes, and confirms `add ""`, `done 99`, `remove 99`, and a non-integer id each exit non-zero with stderr output.
  - type: test
  - req: REQ-9
  - files: todo.py, .spec/todo-cli/
