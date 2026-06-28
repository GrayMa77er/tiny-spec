"""Held-out grader for the `roman` task. Never shown to the suite under eval.

Usage: SOLUTION_PATH=/path/to/solution.py python3 test.py
Prints PASS and exits 0 on success; prints FAIL: <reason> and exits 1 otherwise.
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
    if not hasattr(m, "to_roman"):
        fail("solution has no to_roman")
    cases = {1:"I",3:"III",4:"IV",9:"IX",14:"XIV",40:"XL",58:"LVIII",90:"XC",
             400:"CD",444:"CDXLIV",900:"CM",1954:"MCMLIV",1990:"MCMXC",
             1994:"MCMXCIV",2008:"MMVIII",3888:"MMMDCCCLXXXVIII",3999:"MMMCMXCIX"}
    for n, exp in cases.items():
        try:
            got = m.to_roman(n)
        except Exception as e:
            fail(f"to_roman({n}) raised {e}")
        if got != exp:
            fail(f"to_roman({n}) = {got!r}, expected {exp!r}")
    print("PASS"); sys.exit(0)

if __name__ == "__main__":
    main()
