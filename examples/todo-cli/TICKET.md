# Ticket: todo CLI

A small command-line todo manager that persists tasks to a local file, so a user
can capture and track tasks from the terminal across separate invocations.

## Deliverable

- A single-file CLI `todo.py` at the project root, runnable with `python3 todo.py <command>`.
- Python standard library only — no third-party dependencies.
- Tasks persist to a `todos.json` file in the current working directory, created on
  first write.

## Commands

- `add <text>` — add a new task with the given text. Prints the new task's id.
- `list` — print all tasks, one per line, as `<id>. [ ] <text>` for open tasks and
  `<id>. [x] <text>` for done tasks, in id order. Prints nothing (exit 0) when there
  are no tasks.
- `done <id>` — mark the task with that id as done.
- `remove <id>` — delete the task with that id.

## Behaviour

- Task ids are positive integers, assigned in increasing order; ids are not reused
  after removal.
- `done` / `remove` with an unknown id print a short error to stderr and exit
  non-zero.
- `add` with empty text prints a short error to stderr and exits non-zero.
- The store file is human-readable JSON and survives between invocations.

## Examples

```
$ python3 todo.py add "buy milk"
1
$ python3 todo.py add "write tests"
2
$ python3 todo.py list
1. [ ] buy milk
2. [ ] write tests
$ python3 todo.py done 1
$ python3 todo.py list
1. [x] buy milk
2. [ ] write tests
$ python3 todo.py remove 2
$ python3 todo.py list
1. [x] buy milk
```

Acceptance: the example session reproduces exactly (ids, checkbox states, ordering),
tasks persist across separate process invocations via `todos.json`, and unknown-id /
empty-text operations exit non-zero with a stderr message.
