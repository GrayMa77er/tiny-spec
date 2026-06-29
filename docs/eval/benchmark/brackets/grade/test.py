"""Held-out grader for the `brackets` task. Never shown to the suite under eval.

Usage: SOLUTION_PATH=/path/to/solution.py python3 test.py
"""
import importlib.util, os, sys

def load(path):
    spec = importlib.util.spec_from_file_location("solution", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def fail(msg):
    print("FAIL:", msg); sys.exit(1)

def main():
    path = os.environ.get("SOLUTION_PATH", "solution.py")
    if not os.path.exists(path):
        fail(f"no solution at {path}")
    try:
        m = load(path)
    except Exception as e:
        fail(f"cannot import solution: {e}")
    if not hasattr(m, "is_balanced"):
        fail("solution has no is_balanced")
    truthy = ["", "()", "()[]{}", "([{}])", "a(b)c[d]{e}", "{[()]}", "(())()"]
    falsy = ["(", ")", "([)]", "{[}", "(]", "))((", "(()", "([]", "abc)"]
    for s in truthy:
        try:
            got = m.is_balanced(s)
        except Exception as e:
            fail(f"is_balanced({s!r}) raised {e}")
        if got is not True:
            fail(f"is_balanced({s!r}) = {got!r}, expected True")
    for s in falsy:
        try:
            got = m.is_balanced(s)
        except Exception as e:
            fail(f"is_balanced({s!r}) raised {e}")
        if got is not False:
            fail(f"is_balanced({s!r}) = {got!r}, expected False")
    print("PASS"); sys.exit(0)

if __name__ == "__main__":
    main()
