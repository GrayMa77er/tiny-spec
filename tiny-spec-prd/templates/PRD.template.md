# PRD — <product / feature name>

<!-- A pre-spec planning doc. It lives at the PROJECT ROOT (not under .spec/) and is
     NOT a tracked .spec/ artifact. tiny-spec-breakdown reads it as its anchor and
     carves the Core capabilities below into Features → Stories (BREAKDOWN.md), which
     tiny-spec-create then turns into per-story specs. Regenerable — edit freely.
     Keep it thin: the shortest PRD that lets breakdown carve good stories. -->

## Problem / context

<!-- Required. The problem and who has it — the "why" before any "what". One short
     paragraph. Name the user and the pain; don't open with a feature list. -->

## Goal & non-goals

<!-- Required. What success looks like, and what is explicitly OUT of scope for now.
     Non-goals are load-bearing — they set the boundary breakdown won't cross. -->

- Goal: <the outcome this delivers>
- Non-goal: <explicitly out of scope — re-run later for the next slice>

## Users / personas

<!-- optional. Who uses this, and what they're trying to do. Skip for a single
     obvious user. -->

## Core capabilities

<!-- Required. The handful of things a user must be able to DO. This is the seam:
     tiny-spec-breakdown groups these into Features → Stories, and each becomes a
     story's draft AC → REQ-N. Phrase each as a single user-observable, testable
     capability with no implementation detail. Keep each atomic — no "and" hiding
     two capabilities. -->

- <a user-observable capability — e.g. "a signed-in user can reset their password by email">
- <another — atomic, testable, no implementation detail>
- <…>

## Constraints & cross-cutting

<!-- optional. Stack/platform already decided, and cross-cutting non-functionals
     (auth, i18n, a11y, perf). These flow into the breakdown Decisions block and
     become constitution invariants or shared requirements downstream — NOT their
     own capability above. One line each. -->

- Stack / platform: <if already decided>
- Cross-cutting: <auth, i18n, a11y, perf — spanning capabilities>

## Success signals

<!-- optional. How you'll know it's working — a metric, a behaviour, an acceptance
     bar. Keeps the PRD honest. -->

## Open questions

<!-- optional. What's still undecided. Surfacing it here beats guessing downstream. -->
