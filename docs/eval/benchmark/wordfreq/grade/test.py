"""Held-out grader for the `wordfreq` task. Never shown to the suite under eval.

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

def norm(result):
    # accept list of tuples or list of lists
    return [tuple(x) for x in result]

def main():
    path = os.environ.get("SOLUTION_PATH", "solution.py")
    if not os.path.exists(path):
        fail(f"no solution at {path}")
    try:
        m = load(path)
    except Exception as e:
        fail(f"cannot import solution: {e}")
    if not hasattr(m, "top_words"):
        fail("solution has no top_words")
    txt = "the quick brown fox the lazy dog the fox"
    cases = [
        (txt, 2, [("the",3),("fox",2)]),
        (txt, 3, [("the",3),("fox",2),("brown",1)]),
        ("Hello, hello! World.", 1, [("hello",2)]),
        ("A a B b b", 2, [("b",3),("a",2)]),
        ("", 5, []),
        ("one two two three three three", 10,
            [("three",3),("two",2),("one",1)]),
        ("c c b b a a", 2, [("a",2),("b",2)]),  # all tie at 2 -> alphabetical
    ]
    for text, n, exp in cases:
        try:
            got = norm(m.top_words(text, n))
        except Exception as e:
            fail(f"top_words({text!r}, {n}) raised {e}")
        if got != exp:
            fail(f"top_words({text!r}, {n}) = {got!r}, expected {exp!r}")
    print("PASS"); sys.exit(0)

if __name__ == "__main__":
    main()
