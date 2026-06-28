# tiny-spec evaluation

Two complementary evaluations of the tiny-spec suite, plus a shared score history.
Both are **maintainer-only dev tools** — none of this is in `tiny_spec/manifest.json`,
so nothing here ships to users.

| Eval | Question it answers | How | Drives |
|------|---------------------|-----|--------|
| **Static review** — `/eval-suite` | Does the *design* have the right mechanisms? | Reads `CONTRACTS.md`, agents, SKILL.md; scores 0–3 against the rubric. | Dimensions **B, C, D** |
| **Empirical harness** — `harness/run.sh` | Does the suite *actually produce working code*, and does its own gate tell the truth? | Runs the real flow on benchmark tasks and grades the output with held-out tests. | Dimension **A** (auto-derived) |

The rubric, criteria, weights, and worked rationale live in
[`../sdd-evaluation-rubric.md`](../sdd-evaluation-rubric.md).

## Files

```
docs/eval/
  scores.jsonl              append-only scorecard history (the score over time)
  results.jsonl             append-only per-run empirical detail (created on first run)
  benchmark/<task>/
    TICKET.md               the prompt handed to tiny-spec (NO hidden tests)
    grade/test.py           held-out grader — the suite never sees this
  harness/
    run.sh                  orchestrator: sandbox -> headless claude -> grade -> score
    score.py                metrics + Dimension A thresholds + merge into scores.jsonl
```

## Running the empirical eval

Prereqs: `claude` CLI, `python3`, `git`. The harness vendors the repo's skills+agents
into each sandbox's local `.claude/`, so you do **not** need tiny-spec globally installed.

```sh
docs/eval/harness/run.sh                  # all tasks
docs/eval/harness/run.sh roman duration   # a subset
CLAUDE_MODEL=claude-sonnet-4-6 docs/eval/harness/run.sh roman   # pick a model
KEEP_SANDBOX=1 docs/eval/harness/run.sh roman                   # keep sandbox to inspect
```

Each task runs in a throwaway sandbox: a fresh git repo seeded only with `TICKET.md`
and the vendored skills. `claude -p` drives `create → plan → tasks → build`
autonomously; then the held-out grader runs against the produced `solution.py`.

### What gets measured

- **held-out pass rate** — the real correctness signal (truth = the grader).
- **suite/truth agreement** & **FALSE-PASS rate** — does tiny-spec's *own* verdict (all
  tasks ticked, no open blocker) match reality? A FALSE-PASS (suite says done, grader
  fails) is the worst outcome; it directly tests the suite's core claim that "an
  independent reviewer running the real gate is the safeguard."
- completion rate, blocker rate.

### How Dimension A is derived (thresholds in `score.py`)

- **A1 measurability** → 3 once a pass-rate is produced.
- **A3 reproducible harness** → 3 once the harness has run.
- **A2 gate effectiveness** → 3 if 0 false-PASS & agreement ≥ 90%; 2 if ≤ 20% false-PASS
  & agreement ≥ 70%; 1 otherwise; 0 if nothing completed.
- **A4 regression visibility** → 3 once ≥ 2 empirical runs are on record, else 2.

B/C/D are carried over from the latest `/eval-suite` static scorecard; the empirical run
swaps in the A scores and recomputes the weighted total, appending a new line tagged
`"scored_by": "eval-output"`.

## Caveats

- **Cost/time:** each task runs the full multi-agent flow headlessly — minutes and real
  tokens per task. Start with a subset.
- **Autonomy:** `--dangerously-skip-permissions` is used so the sandbox run is
  non-interactive. It runs in a throwaway dir, never your repo.
- **Small benchmark:** 5 self-contained Python tasks. It measures the suite's loop on
  small, well-specified work — not large-codebase performance. To approximate the
  literature (Spec Kit Agents on SWE-bench Lite), add harder tasks under `benchmark/`;
  the grader contract (`grade/test.py` reading `$SOLUTION_PATH`) is all a new task needs.
- **Judgment vs measurement:** Dimension A here is *measured*; B/C/D remain design
  judgment from `/eval-suite`.
