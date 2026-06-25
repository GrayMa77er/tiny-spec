# Breakdown — <product / epic name>

<!-- A pre-spec worksheet. It lives at the PROJECT ROOT (not under .spec/) and is
     NOT a tracked .spec/ artifact. tiny-spec-create reads it in seeded mode: each
     Story below becomes one .spec/<slug>/SPEC.md (its AC lines → REQ-N), and on a
     story's first create the Decisions block seeds the shared constitution.md.
     Regenerable — edit freely; the tracker (ADO/Jira/…) stays the source of truth. -->

## Decisions

<!-- Project-wide framing. tiny-spec-create folds these into constitution.md on a
     story's first run: Stack + Code-lives → Style and Layout; verification hints →
     Verification commands; Cross-cutting → Guiding invariants. Keep each to a line. -->

- Stack: <language / framework / runtime>
- Code lives: <where the code is — repo path, dirs of note>
- Platform: <ado | jira | github | monday | ad-hoc>   <!-- ad-hoc → kebab slugs, no parent ids, no Refs footer -->
- Structure lens: <by journey | by screen | by domain | by persona — how features are grouped below>
- Scope: <whole product | epic | MVP slice — the boundary of this breakdown>
- Cross-cutting: <non-functionals spanning stories — auth, i18n, a11y, perf. These become constitution invariants or shared REQ, NOT their own feature.>

## Feature: <feature name>           (tracker parent: <fill after creating, e.g. AB#120>)

- Story: <one user-observable capability>     slug: <ado-__ | kebab>
  - AC: <a single user-observable, testable outcome — becomes REQ-1 in this story's SPEC.md>
  - AC: <another — keep each atomic; no "and" hiding two capabilities>
- Story: <one user-observable capability>     slug: <ado-__ | kebab>
  - AC: <…>

## Feature: <feature name>           (tracker parent: <…>)

- Story: <one user-observable capability>     slug: <ado-__ | kebab>
  - AC: <…>

## Suggested first spec

<story title> (slug: <…>) — run tiny-spec-create on this first.
