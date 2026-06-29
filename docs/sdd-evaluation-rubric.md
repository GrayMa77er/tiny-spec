# A Research-Grounded Rubric for Evaluating Spec-Driven Development Frameworks

> Status: reference doc, not part of the runtime suite. It does not change any skill,
> agent, template, or contract — it is documentation you can apply to *any* SDD
> framework, with `tiny-spec` scored as the first worked example.
>
> **Tracking the score over time:** run `/eval-suite` (a maintainer-only command at
> `.claude/commands/eval-suite.md`, not part of the installed suite) after a change. It
> re-scores tiny-spec against §2/§3, appends a line to `docs/eval/scores.jsonl`, and
> reports the delta vs the previous run. The JSONL is the machine-readable history; this
> doc holds the criteria, weights, and the latest worked rationale (§5).

## 1. Purpose & provenance

Spec-driven development (SDD) frameworks for AI coding agents have multiplied
(GitHub Spec Kit, Kiro, BMAD, OpenSpec, tiny-spec, …), but **no peer-reviewed paper
benchmarks them against each other**. The literature gives us three usable threads
instead, and this rubric stitches them into one comparable scorecard:

- **A rigor taxonomy** — where a framework sits on the spec-first → spec-anchored →
  spec-as-source spectrum (Piskala 2026).
- **Empirical agent evaluation** — measuring task completion on real issues, e.g. Spec
  Kit Agents on SWE-bench Lite, and cross-framework benchmarking via a unified spec
  representation (Taghavi & Bhavani 2026; Agent Spec 2025).
- **Methodology scoring** — explicit, weighted multi-criteria decision making (MCDM)
  over software-quality attributes (ISO 25010 quality models).

Every criterion below cites one of these sources, so the rubric is traceable rather
than arbitrary. Weights are explicit and meant to be re-tuned for your context.

### References

| # | Work | arXiv / source | Used for |
|---|------|----------------|----------|
| 1 | Piskala — *Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants* (2026) | [2602.00180](https://arxiv.org/abs/2602.00180) | Rigor taxonomy (Dim B) |
| 2 | Taghavi & Bhavani — *Spec Kit Agents: Context-Grounded Agentic Workflows* (2026) | [2604.05278](https://arxiv.org/abs/2604.05278) | Empirical eval method, SWE-bench (Dim A) |
| 3 | *Open Agent Specification (Agent Spec)* (2025) | [2510.04173](https://arxiv.org/abs/2510.04173) | Cross-framework benchmarking (Dim A) |
| 4 | Rosa et al. — *Understanding Specification-Driven Code Generation with LLMs* (SANER 2026 Registered Report) | [2601.03878](https://arxiv.org/abs/2601.03878) | Spec/test refinement → correctness (Dim B) |
| 5 | *A Review of Software Quality Models for the Evaluation of Software Products* | [1412.2977](https://arxiv.org/abs/1412.2977) | ISO 25010 quality attributes (Dim C) |
| 6 | *Evaluation of Software Product Quality Metrics* | [2009.01557](https://arxiv.org/abs/2009.01557) | Metric-based quality (Dim C) |
| 7 | *A customizable approach to assess software quality through Multi-Criteria Decision Making* | [2301.12202](https://arxiv.org/abs/2301.12202) | MCDM weighting & scoring method |
| 8 | METR — *Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity* | [2507.09089](https://arxiv.org/abs/2507.09089) | "Ceremony must pay off" caution (Dim D) |
| 9 | Practitioner head-to-heads (no peer review) | [spec-compare](https://github.com/cameronsjo/spec-compare), [15-framework comparison](https://medium.com/@wasowski.jarek/comparing-15-spec-driven-development-frameworks-artifacts-and-decision-paths-sdd-c052df529274) | Existing informal comparisons |

## 2. The four scored dimensions

Each criterion is scored on one anchored scale:

| Score | Meaning |
|------:|---------|
| **0** | Absent — the framework does not address this at all. |
| **1** | Ad hoc — depends on the operator remembering; no structural support. |
| **2** | Present & consistent — a defined mechanism exists and is followed by default. |
| **3** | Enforced / measured — a gate, automated check, or recorded metric makes it non-optional. |

Default dimension weights (sum = 100) reflect that for AI-assisted SDD, *methodology
rigor* and *real verification* matter most; **re-tune them for your context**.

| Dim | Weight | Criteria (each 0–3) | Grounded in |
|-----|-------:|---------------------|-------------|
| **A. Empirical task performance** | 25 | A1 task-completion measurability · A2 correctness/defect gate · A3 reproducible eval harness · A4 regression visibility | 2, 3 |
| **B. Spec rigor & methodology fit** | 30 | B1 placement on the rigor taxonomy · B2 requirement→design→task→code traceability · B3 staleness/change propagation · B4 blocker handling vs hacking around | 1, 4 |
| **C. Quality attributes (ISO 25010)** | 25 | C1 maintainability of artifacts · C2 reliability of the gate (real run vs inferred) · C3 traceability/auditability · C4 portability/self-containment | 5, 6 |
| **D. Developer experience / ceremony** | 20 | D1 earned-ceremony / overhead · D2 config burden · D3 cognitive load per task · D4 onboarding to existing codebases | 7, 8 |

### Criterion definitions

**A — Empirical task performance** (does the framework produce *measured* outcomes?)
- **A1 task-completion measurability** — can you express "what fraction of tasks the framework completes correctly" as a number (e.g. SWE-bench-Lite pass rate)?
- **A2 correctness/defect gate** — is there a hard pass/fail gate per unit of work that exercises real behavior, not just "tests exist"?
- **A3 reproducible eval harness** — is there a runnable, repeatable benchmark/harness that others can re-run to compare configurations?
- **A4 regression visibility** — does it surface whether a later change broke earlier work, with evidence?

**B — Spec rigor & methodology fit** (how strongly do specs actually drive the build?)
- **B1 rigor-taxonomy placement** — spec-first (specs lead) / spec-anchored (specs guide alongside code) / spec-as-source (code generated/verified from specs). Higher rigor consistently applied scores higher.
- **B2 traceability** — an unbroken chain requirement → design → task → code, auditable end to end.
- **B3 staleness/change propagation** — when an upstream artifact changes, are downstream artifacts (and already-done work) marked or invalidated rather than silently drifting?
- **B4 blocker handling** — when the spec/design is wrong, does the framework stop and route upstream, or does the agent hack around the gap?

**C — Quality attributes (ISO 25010)**
- **C1 maintainability** — are the artifacts small, lean, and easy to keep in sync, or a sprawl that rots?
- **C2 reliability of the gate** — does verification *run the real thing* end to end, or infer "done" from green unit tests / polished docs?
- **C3 traceability/auditability** — is there a durable record (decision log, requirement map, linked commits) you can audit later?
- **C4 portability/self-containment** — does it run anywhere without absolute paths, hidden global state, or external credentials?

**D — Developer experience / ceremony** (does the process pay for itself? — cf. METR's finding that AI tooling can *slow* experienced devs while feeling faster)
- **D1 earned ceremony** — is structure added only where it pays, or imposed as mandatory phases/sections?
- **D2 config burden** — how much must you configure/learn before first use?
- **D3 cognitive load per task** — how much context must a human (or agent) hold to make progress on one unit of work?
- **D4 onboarding to existing codebases** — does it assume greenfield, or fit a ticket inside a system that already exists?

## 3. Scoring method (MCDM, ref 7)

For each framework:

1. Score every criterion 0–3.
2. Per dimension, take the **mean** of its criteria → `dim_avg` (0–3).
3. Normalize and weight:

```
weighted_total = Σ_dimensions ( dim_avg / 3 × dimension_weight )
```

`dim_avg / 3` rescales each dimension to 0–1; multiplying by the weight (summing to
100) yields a 0–100 total. Weights are **explicit and adjustable** — that is the whole
point of MCDM: make the value judgement visible and tunable, not baked in. A team that
cares only about shipping benchmarks bumps Dim A's weight; a team optimizing for audit
trails bumps Dim C.

## 4. Comparison matrix

All five columns are filled. tiny-spec is the worked self-assessment of this repo (§5);
the other four were researched from each project's primary docs (§6). **Calibration
caveat:** tiny-spec was scored by the assistant working *inside* its own repo, while the
others were scored by external research agents instructed to be conservative — read the
tiny-spec lead with that home-field bias in mind, and re-score for your context.

| Criterion | Weight grp | tiny-spec | Spec Kit | Kiro | BMAD | OpenSpec |
|-----------|:----------:|:---------:|:--------:|:----:|:----:|:--------:|
| A1 task-completion measurability | A (25) | 1 | 0 | 0 | 0 | 0 |
| A2 correctness/defect gate | A | 3 | 1 | 1 | 1 | 0 |
| A3 reproducible eval harness | A | 0 | 0 | 0 | 0 | 0 |
| A4 regression visibility | A | 1 | 0 | 0 | 1 | 0 |
| B1 rigor-taxonomy placement | B (30) | 2 | 3 | 2 | 2 | 3 |
| B2 requirement→…→code traceability | B | 2 | 2 | 2 | 2 | 2 |
| B3 staleness/change propagation | B | 3 | 1 | 1 | 1 | 2 |
| B4 blocker handling vs hacking | B | 3 | 2 | 2 | 2 | 1 |
| C1 maintainability of artifacts | C (25) | 3 | 2 | 2 | 1 | 2 |
| C2 reliability of the gate | C | 3 | 1 | 1 | 1 | 1 |
| C3 traceability/auditability | C | 2 | 2 | 2 | 2 | 2 |
| C4 portability/self-containment | C | 3 | 3 | 1 | 2 | 3 |
| D1 earned ceremony / overhead | D (20) | 3 | 2 | 1 | 1 | 2 |
| D2 config burden | D | 3 | 3 | 2 | 1 | 3 |
| D3 cognitive load per task | D | 3 | 2 | 2 | 2 | 2 |
| D4 onboarding to existing codebases | D | 2 | 2 | 2 | 2 | 3 |
| **A avg → /25** | | 1.25 → 10.4 | 0.25 → 2.1 | 0.25 → 2.1 | 0.50 → 4.2 | 0.00 → 0.0 |
| **B avg → /30** | | 2.50 → 25.0 | 2.00 → 20.0 | 1.75 → 17.5 | 1.75 → 17.5 | 2.00 → 20.0 |
| **C avg → /25** | | 2.75 → 22.9 | 1.75 → 14.6 | 1.50 → 12.5 | 1.50 → 12.5 | 2.00 → 16.7 |
| **D avg → /20** | | 2.75 → 18.3 | 2.25 → 15.0 | 1.75 → 11.7 | 1.50 → 10.0 | 2.50 → 16.7 |
| **Weighted total (/100)** | | **≈77** | **≈52** | **≈44** | **≈44** | **≈53** |

## 5. Worked self-assessment: tiny-spec

Scores below cite real facts in this repo (`README.md`, `CONTRACTS.md`). The profile
is deliberately honest: tiny-spec is **strong on rigor, quality, and DX, and weak on
empirical measurement** — by design, it bets on one independent reviewer over volumes
of machinery and has never been benchmarked.

### Dimension A — Empirical task performance · avg 1.25 → 10.4 / 25

| # | Score | Evidence |
|---|:-----:|----------|
| A1 | 1 | Per-task `PASS`/`FAIL` exists (`CONTRACTS.md` §4) but there is **no aggregate completion metric** — no number for "% of tasks shipped correctly." |
| A2 | 3 | Strong gate: an **independent reviewer runs the real gate end-to-end** before any commit (`CONTRACTS.md` §2, §4; README "Why it's small"). |
| A3 | 0 | No benchmark or reproducible eval harness ships with the suite. |
| A4 | 1 | A final whole-spec smoke runs once all tasks pass (`CONTRACTS.md` §4), and staleness unchecks affected work, but there is **no tracked regression suite/metric** across runs. |

> This is the gap to close — see "Raising the A score" below.

### Dimension B — Spec rigor & methodology fit · avg 2.5 → 25.0 / 30 (strongest)

| # | Score | Evidence |
|---|:-----:|----------|
| B1 | 2 | Sits firmly at **spec-anchored**: specs drive the build and code is reviewed against them, but code is *not* regenerated from the spec (no spec-as-source). Consistently applied across the flow. |
| B2 | 2 | Explicit chain — `REQ-N` (SPEC) → `## Requirement coverage` (PLAN, every REQ mapped) → `req: REQ-N` (tasks) → commit (`CONTRACTS.md` §3.1, §3.3, §3.4). Scored 2 not 3 because the task-level `req:` link is **optional**, so traceability-to-code isn't fully enforced. |
| B3 | 3 | Enforced staleness: changing an upstream artifact flips downstream to `status: stale`, and a change touching an already-`[x]` task **unchecks it** for human review (`CONTRACTS.md` §6). |
| B4 | 3 | Enforced "never hack around": the executor **stops and logs a `BLOCKER`**, routing upstream to plan/create in update mode (`CONTRACTS.md` §5; README). |

### Dimension C — Quality attributes (ISO 25010) · avg 2.75 → 22.9 / 25

| # | Score | Evidence |
|---|:-----:|----------|
| C1 | 3 | Minimal, lean artifact set with optional sections marked as such; explicit anti-bloat stance ("documents are context, and context isn't free", README). |
| C2 | 3 | The gate **runs install→lint→test→build→run for real** and exercises acceptance black-box; "a green unit test suite is not the same as working software" (README; `CONTRACTS.md` §3.2 §4). |
| C3 | 2 | Durable trail via `decisions.md`, requirement coverage map, and `Refs:` commit footers — but `decisions.md` and `req:` are **lazy/optional**, so auditability is present rather than guaranteed (`CONTRACTS.md` §3.6, §4.1). |
| C4 | 3 | Fully portable: "no absolute paths anywhere", self-contained skills carrying their own templates, reference-only ticket binding with no credentials (`CONTRACTS.md` §3, §8; README "Project layout"). |

### Dimension D — Developer experience / ceremony · avg 2.75 → 18.3 / 20

| # | Score | Evidence |
|---|:-----:|----------|
| D1 | 3 | "Earned ceremony" is the stated north star; explicit anti-goals — no waves, `owns:` contracts, checkpoint matrix, autonomous budgets, orchestrator, or validators (`CONTRACTS.md` north-star note; AGENTS.md). |
| D2 | 3 | **Zero config** — "no orchestrator, no config file, no build step" (README). |
| D3 | 3 | Fresh, minimal, self-contained context per task — constitution + memory + the one task, nothing else (`CONTRACTS.md` §7). |
| D4 | 2 | Designed for "a ticket inside a system, not a greenfield repo" (README), and the executor may read the whole codebase — but there is **no dedicated existing-codebase mapping/adopt step**, so onboarding leans on the agent's own exploration. |

### Weighted total

```
A: 1.25/3 × 25 = 10.4
B: 2.50/3 × 30 = 25.0
C: 2.75/3 × 25 = 22.9
D: 2.75/3 × 20 = 18.3
                 ------
total          ≈ 76.7 / 100  → ~77
```

### Raising tiny-spec's A score (without violating "stay small")

The honest weak spot is **measurement**, not capability. This gap now has a tool:
**`docs/eval/`** holds an empirical harness (`harness/run.sh`) that runs the real flow on
benchmark tasks and grades the actual output with held-out tests, auto-deriving Dimension
A — see [`docs/eval/README.md`](eval/README.md). The research method it follows already
exists: Spec Kit Agents (ref 2) ran its workflow over **SWE-bench Lite** and reported a
task-completion pass rate (56.5% baseline → 58.2% with context-grounding). tiny-spec
measures itself the same way **without adding runtime machinery**:

- Run the `tiny-spec-create → plan → tasks → build` loop over a small SWE-bench-Lite
  subset and record the per-task reviewer pass rate — turning A1/A3 from 0–1 into a
  real number. This is an *evaluation* of the suite, not a new skill in it, so it stays
  consistent with the "don't grow it back" rule.
- Use Agent Spec (ref 3) as the representation if you want an apples-to-apples run
  against Spec Kit / Kiro on the same tasks.

That single experiment would move tiny-spec from "rigorous by argument" to "rigorous by
argument *and* measurement" — the one thing the literature says SDD frameworks broadly
still lack.

## 6. Other frameworks (researched from primary docs)

Each was scored by an external research agent against the §2 criteria using the project's
own documentation, instructed to score conservatively and to mark unverifiable mechanisms
low. Confidence and caveats are recorded per framework.

### GitHub Spec Kit — ≈52 / 100 (confidence: medium-high)

Open-source toolkit; flow **Constitution → Specify → (Clarify) → Plan → Tasks → (Analyze)
→ Implement**, one Markdown artifact per phase, 30+ supported agents, bootstrapped by
`specify init`. Sources: [repo](https://github.com/github/spec-kit),
[docs](https://github.github.com/spec-kit/),
[blog](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/),
[issue #1323](https://github.com/github/spec-kit/issues/1323).

- **Strengths:** strongest **B1** (3 — explicit spec-as-source-of-truth, consistently
  applied), painless setup (**D2** 3), portable/offline (**C4** 3). `/analyze` is a real
  six-pass consistency check.
- **Weaknesses:** **no last-mile gate** — `/analyze` is an LLM read-only review, not a run
  of the system (issue #1323 is an open request for exactly this), so **C2/A2** = 1. No
  benchmark, no done-work invalidation (**A** ≈ 0, **B3** 1).
- **vs tiny-spec:** comparable on rigor/portability; the gap is entirely **verification
  reliability** — Spec Kit *reviews* the spec; tiny-spec *runs the real gate per task*.

### OpenSpec — ≈53 / 100 (confidence: high on the A/C2 gaps)

Lightweight, tool-agnostic; npm CLI + `openspec/` dir holding a `specs/` baseline and
`changes/<name>/` proposals (delta specs as ADDED/MODIFIED/REMOVED, GIVEN/WHEN/THEN
scenarios). Loop: `/opsx:explore → propose → apply → archive`. Sources:
[repo](https://github.com/Fission-AI/OpenSpec),
[cli.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md),
[existing-projects.md](https://github.com/Fission-AI/OpenSpec/blob/main/docs/existing-projects.md).

- **Strengths:** highest non-tiny-spec total. **B1** 3 (spec-first by design), best
  brownfield onboarding (**D4** 3 — `/opsx:onboard` derives a delta spec from real code),
  near-zero config (**D2** 3), and a genuine baseline-update mechanism via `archive`
  merging deltas (**B3** 2).
- **Weaknesses:** `openspec validate` is **structural only** — it checks spec shape, never
  runtime behavior — so **A** = straight 0 and **C2** = 1. Blocker routing is operator-
  dependent (**B4** 1).
- **vs tiny-spec:** the closest competitor on rigor/DX; same fundamental gap — structure
  validation ≠ running the software.

### AWS Kiro — ≈44 / 100 (confidence: medium)

Proprietary VS Code-based agentic IDE. Spec pipeline **Prompt → Requirements (EARS) →
Design → Tasks → Code** under `.kiro/specs/`, plus steering files and event-triggered
hooks; recent "deep spec analysis" adds an LLM+SMT upstream check. Sources:
[docs](https://kiro.dev/docs/), [specs](https://kiro.dev/docs/specs/),
[hooks](https://kiro.dev/docs/hooks/),
[deep-spec-analysis](https://kiro.dev/blog/deep-spec-analysis/).

- **Strengths:** EARS-notation requirements with tasks linked back to them (**B2** 2),
  strong existing-codebase support, requirements-analysis catches conflicts upstream
  (**B4** 2). Polished onboarding.
- **Weaknesses:** **proprietary IDE + AWS account** drags **C4** to 1 (workflow locked to
  the tool); hooks *can* run tests but are optional/operator-defined (**A2/C2** 1); fixed
  three-phase ceremony on every spec regardless of size (**D1** 1).
- **vs tiny-spec:** Kiro has a richer requirements notation, but loses on portability,
  earned-ceremony, and the real per-task gate.

### BMAD-METHOD — ≈44 / 100 (confidence: medium)

Heavy, role-agent framework (v6). Four phases (Analysis → Planning → Solutioning →
Implementation); persona agents (PM, Architect, Dev, etc.) plus an optional Test Architect
module with a "Release Gate"; hyper-detailed per-story files; real brownfield support.
Sources: [repo](https://github.com/bmad-code-org/BMAD-METHOD),
[brownfield guide](https://github.com/bmad-code-org/BMAD-METHOD/blob/main/docs/working-in-the-brownfield.md).

- **Strengths:** most detailed story files → low per-task ambiguity (**D3** 2), real
  brownfield tooling (**D4** 2), `dev-auto` halts with `status: blocked` rather than
  hacking around (**B4** 2). The optional TEA module is the only competitor with explicit
  traceability/regression *concepts*.
- **Weaknesses:** **most ceremony** — 4 phases, 12+ personas, 34+ workflows, many
  generated docs → lowest **C1** (1) and **D1/D2** (1) of the set. The default QA "runs
  tests" but there's no enforced blocking gate (**C2** 1).
- **vs tiny-spec:** opposite philosophy — BMAD adds machinery and personas where tiny-spec
  keeps one independent reviewer. BMAD's TEA *could* close the A-gap if enabled, but it's a
  separate, heavier module.

## 7. Results, ranking & takeaways

| Rank | Framework | Total | One-line profile |
|-----:|-----------|:-----:|------------------|
| 1 | **tiny-spec** | ≈77 | Wins on the real per-task gate + enforced change/blocker discipline; self-scored. |
| 2 | OpenSpec | ≈53 | Leanest spec-first flow with the best brownfield onboarding; structural validation only. |
| 3 | GitHub Spec Kit | ≈52 | Strongest spec-as-source positioning + ecosystem; no last-mile run gate. |
| 4 | BMAD-METHOD | ≈44 | Most thorough/heaviest; ceremony cost; optional TEA gate. |
| 4 | AWS Kiro | ≈44 | Polished IDE + EARS requirements; proprietary lock-in; optional gates. |

**Cross-cutting findings:**

1. **Dimension A is everyone's gap.** Every framework scores ≈0 on empirical task
   performance — no benchmarks, no shipped eval harness, no regression metric. This
   exactly matches the literature's verdict (no peer-reviewed multi-framework benchmark
   exists) and is the clearest opportunity for *any* of these projects.
2. **The real differentiator is C2 / A2 — does verification run the real thing?** This is
   where tiny-spec separates from the field: it is the only one whose default loop has an
   **independent reviewer execute the gate end-to-end per task**. Spec Kit, Kiro, OpenSpec
   verify the *spec* (LLM review / structural validate); BMAD runs tests but doesn't block.
   "Polished planning artifacts look like rigor; running the tests *is* rigor" is the whole
   thesis, and the scores bear it out.
3. **Rigor (B1) is a solved problem.** Everyone is at least spec-anchored; Spec Kit and
   OpenSpec push to spec-as-source. Choosing on B1 alone won't separate them.
4. **Ceremony trades against thoroughness (Dimension D).** tiny-spec and OpenSpec win on
   low overhead; BMAD and Kiro impose more fixed structure. Per the METR caution (ref 8),
   more ceremony is only worth it if it demonstrably pays off — which loops back to the
   unmeasured Dimension A.

**How to use this:** the scores encode *this repo's* weighting (verification-heavy). If you
weight differently — e.g. you value BMAD's exhaustive planning or Kiro's IDE integration —
bump the relevant dimension weights in §3 and recompute; the matrix makes that a one-line
change. And treat the tiny-spec column as self-assessment to pressure-test, not gospel.
