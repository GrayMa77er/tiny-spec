---
description: Re-score tiny-spec against the SDD evaluation rubric, record it, and report the delta vs the last run.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent
---

# /eval-suite — self-evaluate tiny-spec and track the score over time

You are scoring **this repo's tiny-spec suite** against the rubric in
`docs/sdd-evaluation-rubric.md`, recording the result, and reflecting on how recent
changes moved the score. This is a **maintainer dev tool** — it is *not* part of the
installed suite (not in `tiny_spec/manifest.json`) and must never be added to it.

The goal is a **stable, comparable** time series: a score only moves when there is a
concrete, evidenced reason in the suite's source — not from re-judging the same facts
differently. Anchor hard to the previous scorecard.

## Inputs (read these first)

1. **The rubric** — `docs/sdd-evaluation-rubric.md`: §2 (the 16 criteria + the 0–3
   anchored scale), §3 (the weighting formula). These define the scale and weights; do
   not invent your own.
2. **The previous scorecard** — the **last line** of `docs/eval/scores.jsonl`
   (`tail -n 1`). This is your anchor: its per-criterion scores and evidence.
3. **The suite source** — score against what the code/contract actually says today:
   - `CONTRACTS.md` (formats, the build loop, blockers, staleness)
   - `AGENTS.md` and `CLAUDE.md` (philosophy, anti-goals)
   - `README.md` (positioning, verification claims)
   - each `tiny-spec-*/SKILL.md` and `agents/tiny-spec-build-*.md`
   - `tiny_spec/manifest.json` (what actually ships)
   For a thorough pass you may dispatch an `Explore` agent to diff behaviour, but read
   `CONTRACTS.md` and the two agent files directly — they back most scores.

## The 0–3 scale (from the rubric, do not redefine)

- **0** absent · **1** ad hoc (no structural support) · **2** present & consistent
  (defined mechanism, default) · **3** enforced/measured (a gate/check/metric makes it
  non-optional).

## Procedure

1. **Establish HEAD context.** Run `git rev-parse --short HEAD` and `date +%Y-%m-%d`.
   Optionally `git log --oneline <prev_sha>..HEAD` (prev_sha from the last scorecard) to
   see what changed since the last run — this is what you're reflecting on.
2. **Score all 16 criteria.** For each, start from the previous score. Keep it unless the
   suite source now justifies a change; if you change it, cite the specific file/section
   that moved it. Write a one-line evidence string per criterion (current, not copied
   blindly). Be conservative: no evidence a mechanism exists → score it low.
3. **Compute** per the rubric §3:
   - `dim_avg` = mean of the 4 criteria in each dimension (A,B,C,D).
   - `weighted_dim` = `dim_avg / 3 × weight` with weights A=25, B=30, C=25, D=20.
   - `total` = sum of the four weighted dims (0–100). Round displayed numbers to 2 dp.
4. **Append** one JSON line to `docs/eval/scores.jsonl` with this exact shape (one line,
   no pretty-printing):
   ```
   {"date":"<YYYY-MM-DD>","git_sha":"<short>","scored_by":"/eval-suite","scores":{"A1":..,"A2":..,...,"D4":..},"evidence":{"A1":"..",...},"dims":{"A":..,"B":..,"C":..,"D":..},"weighted":{"A":..,"B":..,"C":..,"D":..},"total":..,"note":"<one line: what changed since last run and why>"}
   ```
   Append only — never edit or delete prior lines (the history is the point).
5. **Report to the user** in chat:
   - **Total: `<new>` (`<+/−delta>` vs `<prev_sha>` @ `<prev_total>`).**
   - A **changed-criteria table**: `criterion | old → new | why` — only the rows that
     moved. If nothing moved, say so explicitly.
   - **Dimension deltas** (A/B/C/D old → new).
   - **Reflection (2–4 sentences):** did the changes since the last run help, hurt, or not
     touch the score, and what is the highest-leverage next change? Tie it to a dimension
     (Dim A — empirical measurement — is the standing weak spot; flag if a change finally
     addresses it).

## Guardrails

- **Stability over novelty.** Identical source since the last run → identical scores. Drift
  with no source change is a bug in your judgment, not a real movement.
- **Self-score, labelled as such.** You are scoring from inside the repo; keep
  `"scored_by"` honest. Do not silently re-score the competitor frameworks — they live in
  the rubric doc and are a separate, heavier (web-research) job.
- **Respect the philosophy.** If a change *raised* a score by adding ceremony the suite's
  own anti-goals reject (waves, orchestrator, validators, config, mandatory phases), call
  that out in the reflection — a higher number bought with banned machinery is a regression
  in the suite's terms, not a win.
- **No new artifacts** beyond appending to `docs/eval/scores.jsonl`. Do not create
  per-run files or a parallel history; the JSONL is the single source of truth.
