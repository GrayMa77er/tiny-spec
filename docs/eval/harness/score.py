#!/usr/bin/env python3
"""Aggregate empirical eval results, derive Dimension A from real output, and merge
into the scorecard history.

Input: a JSON file (path as argv[1]) holding a list of per-task result objects:
  {"task": str, "produced": bool, "suite_completed": bool, "blocker": bool,
   "held_out_pass": bool, "notes": str}

What it does:
  1. Computes empirical metrics (held-out pass rate, suite/truth agreement,
     false-PASS rate, completion/blocker rates).
  2. Derives A1-A4 (0-3) from those metrics via fixed thresholds (documented below).
  3. Reads the latest line of docs/eval/scores.jsonl, keeps its static B/C/D scores,
     swaps in the empirical A scores, recomputes the weighted total.
  4. Appends the full per-run detail to docs/eval/results.jsonl and the merged
     scorecard to docs/eval/scores.jsonl.
  5. Prints a human report (totals, deltas, metrics).

Dimension A is the only empirically-derived dimension; B/C/D remain the static
design review from /eval-suite. Run `python3 score.py --help` is not implemented;
the contract is: score.py <results.json> [--sha <short>] [--date <YYYY-MM-DD>].
"""
import json, os, sys

WEIGHTS = {"A": 25, "B": 30, "C": 25, "D": 20}
HERE = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.dirname(HERE)
SCORES = os.path.join(EVAL_DIR, "scores.jsonl")
RESULTS = os.path.join(EVAL_DIR, "results.jsonl")


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path):
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def dim_avg(scores, dim):
    vals = [scores[f"{dim}{i}"] for i in range(1, 5)]
    return sum(vals) / 4.0


def compute_total(scores):
    dims, weighted = {}, {}
    for d in "ABCD":
        a = dim_avg(scores, d)
        dims[d] = round(a, 2)
        weighted[d] = round(a / 3 * WEIGHTS[d], 2)
    total = round(sum(weighted.values()), 2)
    return dims, weighted, total


def metrics(results):
    n = len(results)
    produced = [r for r in results if r.get("produced")]
    completed = [r for r in results if r.get("suite_completed")]
    passed = [r for r in results if r.get("held_out_pass")]
    # suite verdict = PASS iff it considered the work complete (all tasks ticked,
    # no open blocker). truth = held-out grader.
    false_pass = [r for r in results if r.get("suite_completed") and not r.get("held_out_pass")]
    false_fail = [r for r in results if not r.get("suite_completed") and r.get("held_out_pass")]
    agree = [r for r in results if bool(r.get("suite_completed")) == bool(r.get("held_out_pass"))]
    blockers = [r for r in results if r.get("blocker")]
    rate = lambda xs: round(len(xs) / n, 3) if n else 0.0
    return {
        "n": n,
        "completion_rate": rate(completed),
        "held_out_pass_rate": rate(passed),
        "suite_truth_agreement": rate(agree),
        "false_pass_rate": rate(false_pass),
        "false_fail_rate": rate(false_fail),
        "blocker_rate": rate(blockers),
        "produced_count": len(produced),
    }


def derive_A(m, prior_run_count):
    """Map empirical metrics -> A1-A4 (0-3). Bands are intentionally simple and
    documented so a score move is explainable.

    A1 measurability   : a pass-rate metric was produced this run -> 3.
    A3 reproducible harness: the harness ran and graded -> 3.
    A2 gate effectiveness (does the suite's PASS verdict match reality?):
         no completed tasks            -> 0  (gate never exercised on a 'done' claim)
         0 false-PASS & agreement>=.90 -> 3
         <=20% false-PASS & agree>=.70 -> 2
         otherwise                     -> 1
    A4 regression visibility: >=2 empirical runs on record -> 3, else 2.
    """
    a1 = 3 if m["n"] else 0
    a3 = 3 if m["n"] else 0
    if m["completion_rate"] == 0:
        a2 = 0
    elif m["false_pass_rate"] == 0 and m["suite_truth_agreement"] >= 0.90:
        a2 = 3
    elif m["false_pass_rate"] <= 0.20 and m["suite_truth_agreement"] >= 0.70:
        a2 = 2
    else:
        a2 = 1
    a4 = 3 if prior_run_count + 1 >= 2 else 2
    return {"A1": a1, "A2": a2, "A3": a3, "A4": a4}


def main():
    if len(sys.argv) < 2:
        print("usage: score.py <results.json> [--sha <short>] [--date <YYYY-MM-DD>]")
        sys.exit(2)
    results_path = sys.argv[1]
    sha = date = None
    args = sys.argv[2:]
    for i, a in enumerate(args):
        if a == "--sha" and i + 1 < len(args):
            sha = args[i + 1]
        if a == "--date" and i + 1 < len(args):
            date = args[i + 1]
    sha = sha or "unknown"
    date = date or "unknown"

    results = json.load(open(results_path))

    # Invalid-run guard: if EVERY task's headless `claude` errored, this is an infra
    # failure (CLI/auth/harness), not a measurement of the suite. Refuse to score so a
    # crashed run can't pollute the history. (claude_rc may be absent in older results.)
    rcs = [r.get("claude_rc") for r in results if "claude_rc" in r]
    if rcs and all(rc != 0 for rc in rcs):
        print("INVALID RUN: every task's `claude` exited non-zero (infra failure, not a "
              "suite result). Nothing appended to scores.jsonl. Check the task logs.")
        sys.exit(3)

    m = metrics(results)

    prior = read_jsonl(SCORES)
    prior_empirical = [r for r in read_jsonl(RESULTS)]
    if not prior:
        print("FATAL: no baseline in scores.jsonl; run /eval-suite first.")
        sys.exit(1)
    last = prior[-1]
    prev_total = last.get("total")
    prev_sha = last.get("git_sha")

    A = derive_A(m, len(prior_empirical))
    merged_scores = dict(last["scores"])
    merged_scores.update(A)
    evidence = dict(last.get("evidence", {}))
    evidence["A1"] = f"measured: held-out pass rate {m['held_out_pass_rate']:.0%} over {m['n']} tasks"
    evidence["A2"] = (f"gate vs truth: agreement {m['suite_truth_agreement']:.0%}, "
                      f"false-PASS {m['false_pass_rate']:.0%}")
    evidence["A3"] = f"reproducible harness ran {m['n']} tasks via docs/eval/harness/run.sh"
    evidence["A4"] = f"{len(prior_empirical)+1} empirical run(s) on record in results.jsonl"

    dims, weighted, total = compute_total(merged_scores)
    note = (f"empirical run: pass {m['held_out_pass_rate']:.0%}, "
            f"agreement {m['suite_truth_agreement']:.0%}, "
            f"false-PASS {m['false_pass_rate']:.0%}, blockers {m['blocker_rate']:.0%}")

    scorecard = {
        "date": date, "git_sha": sha, "scored_by": "eval-output",
        "scores": merged_scores, "evidence": evidence,
        "dims": dims, "weighted": weighted, "total": total, "note": note,
    }
    run_detail = {
        "date": date, "git_sha": sha, "metrics": m,
        "tasks": results, "derived_A": A,
    }

    with open(RESULTS, "a") as f:
        f.write(json.dumps(run_detail) + "\n")
    with open(SCORES, "a") as f:
        f.write(json.dumps(scorecard) + "\n")

    delta = (round(total - prev_total, 2) if isinstance(prev_total, (int, float)) else None)
    print("=" * 60)
    print(f"EMPIRICAL EVAL  ({date} @ {sha})")
    print("=" * 60)
    print(f"tasks                 : {m['n']}")
    print(f"held-out pass rate    : {m['held_out_pass_rate']:.0%}  ({sum(1 for r in results if r.get('held_out_pass'))}/{m['n']})")
    print(f"suite completion rate : {m['completion_rate']:.0%}")
    print(f"suite/truth agreement : {m['suite_truth_agreement']:.0%}")
    print(f"FALSE-PASS rate       : {m['false_pass_rate']:.0%}   <- suite said done but grader failed")
    print(f"false-fail rate       : {m['false_fail_rate']:.0%}")
    print(f"blocker rate          : {m['blocker_rate']:.0%}")
    print("-" * 60)
    print(f"derived Dimension A   : A1={A['A1']} A2={A['A2']} A3={A['A3']} A4={A['A4']}  (avg {dims['A']})")
    print(f"total                 : {total} / 100"
          + (f"   ({'+' if delta and delta>=0 else ''}{delta} vs {prev_sha} @ {prev_total})" if delta is not None else ""))
    print("=" * 60)
    print("per-task:")
    for r in results:
        verdict = "PASS" if r.get("held_out_pass") else "FAIL"
        sv = "done" if r.get("suite_completed") else ("BLOCKED" if r.get("blocker") else "incomplete")
        flag = "  <-- FALSE-PASS" if (r.get("suite_completed") and not r.get("held_out_pass")) else ""
        print(f"  {r['task']:<10} grader={verdict:<4} suite={sv}{flag}")


if __name__ == "__main__":
    main()
