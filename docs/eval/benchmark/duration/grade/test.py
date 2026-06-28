"""Held-out grader for the `duration` task. Never shown to the suite under eval.

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
    if not hasattr(m, "parse_duration"):
        fail("solution has no parse_duration")
    valid = {"45s":45, "2m":120, "1h":3600, "1h30m":5400, "1h30m15s":5415,
             "90m":5400, "3600s":3600, "2h2m2s":7322}
    for s, exp in valid.items():
        try:
            got = m.parse_duration(s)
        except Exception as e:
            fail(f"parse_duration({s!r}) raised {e}, expected {exp}")
        if got != exp:
            fail(f"parse_duration({s!r}) = {got!r}, expected {exp}")
    invalid = ["", "abc", "1x", "1h2", "h", "-5s", "1.5h", "1 h", "m30"]
    for s in invalid:
        try:
            got = m.parse_duration(s)
            fail(f"parse_duration({s!r}) returned {got!r}, expected ValueError")
        except ValueError:
            pass
        except Exception as e:
            fail(f"parse_duration({s!r}) raised {type(e).__name__}, expected ValueError")
    print("PASS"); sys.exit(0)

if __name__ == "__main__":
    main()
