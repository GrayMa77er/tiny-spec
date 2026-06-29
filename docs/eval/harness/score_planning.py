#!/usr/bin/env python3
"""Aggregate planning-stage eval results and append a run to planning-results.jsonl.

Input: a JSON file (argv[1]) holding a list of per-case result objects emitted by
grade_planning.py. Computes pass rates across the structural and judge dimensions,
prints a human report, and appends the run detail.

This is a STANDALONE scorecard for the planning stage (tiny-spec-prd →
tiny-spec-breakdown). It deliberately does NOT touch docs/eval/scores.jsonl — that
file scores the execution loop's correctness claim (Dimensions A–D); planning quality
is a separate concern and keeping them apart stops one from masking the other.

Contract: score_planning.py <results.json> [--sha <short>] [--date <YYYY-MM-DD>].
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL_DIR = os.path.dirname(HERE)
RESULTS = os.path.join(EVAL_DIR, "planning-results.jsonl")


def main():
    if len(sys.argv) < 2:
        print("usage: score_planning.py <results.json> [--sha <short>] [--date <YYYY-MM-DD>]")
        sys.exit(2)
    sha = date = None
    args = sys.argv[2:]
    for i, a in enumerate(args):
        if a == "--sha" and i + 1 < len(args):
            sha = args[i + 1]
        if a == "--date" and i + 1 < len(args):
            date = args[i + 1]
    sha, date = sha or "unknown", date or "unknown"

    results = json.load(open(sys.argv[1]))
    n = len(results)

    # Invalid-run guard: if the judge never ran on any case, this is an infra failure
    # (claude/auth/harness), not a measurement. Refuse to record it.
    if n and not any(r.get("judge_ran") for r in results):
        print("INVALID RUN: the judge never ran on any case (infra failure, not a "
              "planning result). Nothing appended. Check JUDGE call / claude CLI.")
        sys.exit(3)

    rate = lambda key: round(sum(1 for r in results if r.get(key)) / n, 3) if n else 0.0
    metrics = {
        "n": n,
        "pass_rate": rate("pass"),
        "structural_pass_rate": rate("structural_ok"),
        "coverage_rate": rate("coverage_ok"),
        "no_fabrication_rate": rate("no_fabrication"),
        "atomicity_rate": rate("atomicity_ok"),
        "cross_cutting_ok_rate": rate("cross_cutting_placement_ok"),
        "prd_faithful_rate": rate("prd_faithful_to_idea"),
    }

    with open(RESULTS, "a") as f:
        f.write(json.dumps({"date": date, "git_sha": sha, "metrics": metrics, "cases": results}) + "\n")

    print("=" * 60)
    print(f"PLANNING-STAGE EVAL  ({date} @ {sha})")
    print("=" * 60)
    print(f"cases                 : {n}")
    print(f"overall pass rate     : {metrics['pass_rate']:.0%}  ({sum(1 for r in results if r.get('pass'))}/{n})")
    print(f"structural conformance: {metrics['structural_pass_rate']:.0%}")
    print(f"coverage (no dropped) : {metrics['coverage_rate']:.0%}")
    print(f"no fabrication        : {metrics['no_fabrication_rate']:.0%}")
    print(f"atomicity             : {metrics['atomicity_rate']:.0%}")
    print(f"cross-cutting placed  : {metrics['cross_cutting_ok_rate']:.0%}")
    print(f"PRD faithful to idea  : {metrics['prd_faithful_rate']:.0%}")
    print("-" * 60)
    print("per-case:")
    for r in results:
        v = "PASS" if r.get("pass") else "FAIL"
        bits = []
        if not r.get("structural_ok"):
            bits.append("structural")
        if r.get("dropped_capabilities"):
            bits.append(f"dropped={len(r['dropped_capabilities'])}")
        if r.get("invented_stories"):
            bits.append(f"invented={len(r['invented_stories'])}")
        if r.get("atomicity_ok") is False:
            bits.append("atomicity")
        flag = ("  <- " + ", ".join(bits)) if bits else ""
        print(f"  {r['case']:<12} {v}{flag}")
    print("=" * 60)
    print(">> appended to docs/eval/planning-results.jsonl")


if __name__ == "__main__":
    main()
