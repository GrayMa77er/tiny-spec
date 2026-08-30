---
status: current
updated: 2026-06-29
---

# todo CLI

## Context

A user wants to capture and track tasks from the terminal across separate
invocations, with no setup and no dependencies. Captured ad-hoc from `TICKET.md`
(no external tracker).

## Intent

A small command-line todo manager that persists tasks to a local `todos.json` file
so a user can add, list, complete, and remove tasks across separate `python3 todo.py`
invocations, using only the Python standard library.

## Requirements

- REQ-1 — `add <text>` adds a new task with the given text and prints the new task's id to stdout.
- REQ-2 — Task ids are positive integers assigned in increasing order, and are never reused after removal.
- REQ-3 — `add` with empty text prints a short error to stderr and exits non-zero, adding nothing.
- REQ-4 — `list` prints all tasks in id order, one per line, as `<id>. [ ] <text>` for open tasks and `<id>. [x] <text>` for done tasks.
- REQ-5 — `list` with no tasks prints nothing and exits 0.
- REQ-6 — `done <id>` marks the task with that id as done.
- REQ-7 — `remove <id>` deletes the task with that id.
- REQ-8 — `done` or `remove` with an unknown id prints a short error to stderr and exits non-zero.
- REQ-9 — Tasks persist between separate process invocations via a human-readable `todos.json` in the current working directory, created on first write and tolerated when absent.

## Non-goals

- No editing of task text, priorities, due dates, or sorting beyond id order.
- No third-party dependencies, config files, or network access.
- No concurrency/locking guarantees for simultaneous invocations.

## Success criteria

The ticket's example session reproduces exactly (ids, checkbox states, ordering);
tasks persist across separate invocations via `todos.json`; unknown-id and
empty-text operations exit non-zero with a stderr message.
