#!/usr/bin/env python3
"""A small command-line todo manager that persists tasks to todos.json."""

import json
import os
import sys

STORE_FILENAME = "todos.json"


def store_path():
    """Resolve the store path in the current working directory at call time."""
    return os.path.join(os.getcwd(), STORE_FILENAME)


def load_store():
    """Load the store, returning an empty store when the file is absent."""
    try:
        with open(store_path(), "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {"next_id": 1, "tasks": []}


def save_store(store):
    """Write the store as human-readable JSON, creating the file on first write."""
    with open(store_path(), "w", encoding="utf-8") as fh:
        json.dump(store, fh, indent=2)
        fh.write("\n")


def die(msg):
    """Print a short message to stderr and exit non-zero."""
    print(msg, file=sys.stderr)
    sys.exit(1)


def cmd_add(args):
    """Add a new task with the given text, printing its assigned id."""
    if len(args) != 1:
        die("usage: todo.py add <text>")
    text = args[0]
    if not text.strip():
        die("add: text must not be empty")
    store = load_store()
    task_id = store["next_id"]
    store["tasks"].append({"id": task_id, "text": text, "done": False})
    store["next_id"] = task_id + 1
    save_store(store)
    print(task_id)


def cmd_list(args):
    """Print tasks ordered by id ascending; nothing when there are none."""
    if args:
        die("usage: todo.py list")
    store = load_store()
    for task in sorted(store["tasks"], key=lambda t: t["id"]):
        mark = "x" if task["done"] else " "
        print(f"{task['id']}. [{mark}] {task['text']}")


def cmd_done(args):
    """Mark the task with the given id as done (idempotent)."""
    if len(args) != 1:
        die("usage: todo.py done <id>")
    try:
        task_id = int(args[0])
    except ValueError:
        die("done: id must be an integer")
    store = load_store()
    for task in store["tasks"]:
        if task["id"] == task_id:
            task["done"] = True
            save_store(store)
            return
    die(f"done: no task with id {task_id}")


def cmd_remove(args):
    """Remove the task with the given id; ids of remaining tasks are unchanged."""
    if len(args) != 1:
        die("usage: todo.py remove <id>")
    try:
        task_id = int(args[0])
    except ValueError:
        die("remove: id must be an integer")
    store = load_store()
    for index, task in enumerate(store["tasks"]):
        if task["id"] == task_id:
            del store["tasks"][index]
            save_store(store)
            return
    die(f"remove: no task with id {task_id}")


COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "done": cmd_done,
    "remove": cmd_remove,
}


def main(argv):
    """Dispatch on the command name to its handler."""
    if len(argv) < 1:
        die("usage: todo.py <add|list|done|remove> [args]")
    command = argv[0]
    handler = COMMANDS.get(command)
    if handler is None:
        die("usage: todo.py <add|list|done|remove> [args]")
    handler(argv[1:])


if __name__ == "__main__":
    main(sys.argv[1:])
