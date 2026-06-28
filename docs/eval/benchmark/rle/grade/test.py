"""Held-out grader for the `rle` task. Never shown to the suite under eval.

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
    for fn in ("encode", "decode"):
        if not hasattr(m, fn):
            fail(f"solution has no {fn}")
    enc = {"":"", "aaab":"3a1b", "abc":"1a1b1c", "a":"1a",
           "aaaaaaaaaab":"10a1b", "zzzzz":"5z"}
    for s, exp in enc.items():
        try:
            got = m.encode(s)
        except Exception as e:
            fail(f"encode({s!r}) raised {e}")
        if got != exp:
            fail(f"encode({s!r}) = {got!r}, expected {exp!r}")
    for s in ["", "a", "aaab", "abcabc", "aaaaaaaaaab", "mississippi",
              "zzzzzzzzzzzzzzzzzzzz"]:
        try:
            rt = m.decode(m.encode(s))
        except Exception as e:
            fail(f"roundtrip({s!r}) raised {e}")
        if rt != s:
            fail(f"decode(encode({s!r})) = {rt!r}, expected {s!r}")
    print("PASS"); sys.exit(0)

if __name__ == "__main__":
    main()
