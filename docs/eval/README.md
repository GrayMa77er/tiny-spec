# tiny-spec evaluation

Three complementary evaluations of the tiny-spec suite, plus a shared score history.
All are **maintainer-only dev tools** — none of this is in `tiny_spec/manifest.json`,
so nothing here ships to users.

| Eval | Question it answers | How | Drives |
|------|---------------------|-----|--------|
| **Static review** — `/eval-suite` | Does the *design* have the right mechanisms? | Reads `CONTRACTS.md`, agents, SKILL.md; scores 0–3 against the rubric. | Dimensions **B, C, D** |
| **Empirical harness** — `harness/run.sh` | Does the *execution* stage produce working code, and does its own gate tell the truth? | Runs `create → plan → tasks → build` on benchmark tasks and grades the output with held-out tests. | Dimension **A** (auto-derived) |
| **Planning harness** — `harness/run-planning.sh` | Does the *planning* stage produce a sound, faithful hand-off? | Runs `tiny-spec-prd → tiny-spec-breakdown` on loose ideas; grades the PRD/BREAKDOWN with structural checks + an LLM judge. | `planning-results.jsonl` (standalone) |

The rubric, criteria, weights, and worked rationale live in
[`../sdd-evaluation-rubric.md`](../sdd-evaluation-rubric.md).

## Files

```
docs/eval/
  scores.jsonl              append-only scorecard history (the A–D score over time)
  results.jsonl             append-only per-run empirical detail (created on first run)
  planning-results.jsonl    append-only planning-eval detail (created on first run)
  benchmark/<task>/         execution-stage tasks
    TICKET.md               the prompt handed to tiny-spec (NO hidden tests)
    grade/test.py           held-out grader — the suite never sees this
  planning/<case>/          planning-stage cases
    IDEA.md                 a loose product idea handed to the planning stage
  harness/
    run.sh                  execution: sandbox -> headless build -> held-out grade -> score
    score.py                metrics + Dimension A thresholds + merge into scores.jsonl
    run-planning.sh         planning: sandbox -> headless prd+breakdown -> grade -> score
    grade_planning.py       structural checks + LLM judge -> one result object per case
    score_planning.py       aggregate -> planning-results.jsonl (does NOT touch scores.jsonl)
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

## Running the planning eval

```sh
docs/eval/harness/run-planning.sh                 # all planning cases
docs/eval/harness/run-planning.sh snip            # a subset
JUDGE_MODEL=claude-sonnet-4-6 docs/eval/harness/run-planning.sh   # pick the judge model
KEEP_SANDBOX=1 docs/eval/harness/run-planning.sh snip            # keep sandbox to inspect
```

Each case runs in a throwaway sandbox seeded with `IDEA.md` and the vendored skills.
`claude -p` drives `tiny-spec-prd → tiny-spec-breakdown` (it must **not** scaffold
`.spec/` or run any later skill), then `grade_planning.py` scores the produced
`PRD.md` + `BREAKDOWN.md`.

### What gets measured

- **structural conformance** (deterministic) — PRD has its required sections filled;
  BREAKDOWN has a Decisions block, ≥1 Feature, Stories with a slug and ≥1 AC; the
  planning skills left no `.spec/` behind.
- **hand-off integrity** (LLM judge) — **coverage** (every PRD capability lands in ≥1
  story, nothing dropped) and **no fabrication** (every story traces to a capability,
  nothing invented). These are the high-value signals; a case PASSes only if structural
  conformance holds *and* the judge confirms both.
- **quality** (LLM judge, reported not gated) — atomicity / user-observable phrasing,
  cross-cutting concerns placed in Decisions rather than as their own Feature, and
  whether the PRD faithfully reflects the idea.

Results append to `planning-results.jsonl`. This scorecard is **standalone** — it does
not feed the A–D `scores.jsonl`, because planning quality and execution correctness are
separate claims.

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
- **Planning eval uses an LLM judge:** coverage/fabrication/atomicity are judged by a
  model, so verdicts are not bit-reproducible the way held-out tests are. The
  deterministic structural layer *is* reproducible; the judge adds the semantic signal
  the structure can't see. Add planning cases by dropping a new `planning/<case>/IDEA.md`.
