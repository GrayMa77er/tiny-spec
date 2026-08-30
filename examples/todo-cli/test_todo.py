#!/usr/bin/env python3
"""End-to-end tests for todo.py.

Each test runs todo.py as a separate subprocess in a fresh temporary working
directory, exercising persistence across process invocations and asserting on
stdout, stderr and exit codes. Standard library only.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

TODO_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todo.py")


def run(cwd, *args):
    """Invoke todo.py as a separate process in cwd, capturing its output."""
    return subprocess.run(
        [sys.executable, TODO_PY, *args],
        cwd=cwd,
        capture_output=True,
        text=True,
    )


class TodoEndToEndTest(unittest.TestCase):
    def test_example_session_and_persistence(self):
        """Reproduce the ticket example session across separate invocations."""
        with tempfile.TemporaryDirectory() as cwd:
            r = run(cwd, "add", "buy milk")
            self.assertEqual(r.returncode, 0, msg=f"add buy milk: stderr={r.stderr!r}")
            self.assertEqual(r.stdout, "1\n", msg="add buy milk stdout")

            r = run(cwd, "add", "write tests")
            self.assertEqual(r.returncode, 0, msg=f"add write tests: stderr={r.stderr!r}")
            self.assertEqual(r.stdout, "2\n", msg="add write tests stdout")

            r = run(cwd, "list")
            self.assertEqual(r.returncode, 0, msg=f"list: stderr={r.stderr!r}")
            self.assertEqual(
                r.stdout,
                "1. [ ] buy milk\n2. [ ] write tests\n",
                msg="list after two adds",
            )

            r = run(cwd, "done", "1")
            self.assertEqual(r.returncode, 0, msg=f"done 1: stderr={r.stderr!r}")

            r = run(cwd, "list")
            self.assertEqual(r.returncode, 0, msg=f"list: stderr={r.stderr!r}")
            self.assertEqual(
                r.stdout,
                "1. [x] buy milk\n2. [ ] write tests\n",
                msg="list after done 1",
            )

            r = run(cwd, "remove", "2")
            self.assertEqual(r.returncode, 0, msg=f"remove 2: stderr={r.stderr!r}")

            r = run(cwd, "list")
            self.assertEqual(r.returncode, 0, msg=f"list: stderr={r.stderr!r}")
            self.assertEqual(r.stdout, "1. [x] buy milk\n", msg="list after remove 2")

            # Persistence: todos.json exists, is valid JSON, and a brand-new
            # subprocess still sees the persisted state.
            store_file = os.path.join(cwd, "todos.json")
            self.assertTrue(
                os.path.exists(store_file), msg="todos.json should exist after writes"
            )
            with open(store_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)  # raises on invalid JSON -> test failure
            self.assertIn("tasks", data, msg="todos.json should contain tasks")

            r = run(cwd, "list")
            self.assertEqual(r.returncode, 0, msg=f"final list: stderr={r.stderr!r}")
            self.assertEqual(
                r.stdout,
                "1. [x] buy milk\n",
                msg="state should survive across processes",
            )

    def test_ids_not_reused(self):
        """A removed id is not reused by a subsequent add."""
        with tempfile.TemporaryDirectory() as cwd:
            self.assertEqual(run(cwd, "add", "one").stdout, "1\n")
            self.assertEqual(run(cwd, "add", "two").stdout, "2\n")

            r = run(cwd, "remove", "1")
            self.assertEqual(r.returncode, 0, msg=f"remove 1: stderr={r.stderr!r}")

            r = run(cwd, "add", "three")
            self.assertEqual(r.returncode, 0, msg=f"add three: stderr={r.stderr!r}")
            self.assertEqual(r.stdout, "3\n", msg="new id should be 3, not reused")

    def _assert_fails(self, label, *args):
        """Run todo.py and assert non-zero exit with non-empty stderr."""
        with tempfile.TemporaryDirectory() as cwd:
            r = run(cwd, *args)
            self.assertNotEqual(
                r.returncode, 0, msg=f"{label}: expected non-zero exit"
            )
            self.assertNotEqual(
                r.stderr.strip(), "", msg=f"{label}: expected stderr output"
            )

    def test_add_empty_text(self):
        self._assert_fails("add empty", "add", "")

    def test_add_whitespace_text(self):
        self._assert_fails("add whitespace", "add", "   ")

    def test_done_unknown_id(self):
        self._assert_fails("done 99", "done", "99")

    def test_remove_unknown_id(self):
        self._assert_fails("remove 99", "remove", "99")

    def test_done_non_integer_id(self):
        self._assert_fails("done abc", "done", "abc")

    def test_no_command(self):
        self._assert_fails("no command")


if __name__ == "__main__":
    unittest.main()
