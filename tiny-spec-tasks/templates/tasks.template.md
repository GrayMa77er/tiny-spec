---
status: current
updated: <ISO date>
---

# Tasks — <project / feature name>

> Executed top to bottom, one at a time. A checked `[x]` task is implemented AND
> reviewed. `type:`, `req:`, and `design:` are optional; `files:` is a hint, not an
> ownership contract. A task with `design:` is also graded against that screen's
> `D<n>` entry and the constitution's Design system.

## Tasks

- [ ] T1 — <one small, independently-checkable slice of work>
  - acceptance: <one user-observable outcome that proves T1 is done>
  - type: feat            # optional; Conventional Commit type for this task's commit (defaults to feat)
  - req: REQ-1            # optional; the REQ-N this task delivers
  - files: <path, path>

- [ ] T2 — <next slice; assume T1's code exists>
  - acceptance: <observable outcome>
  - type: feat
  - req: REQ-2
  - design: D1            # optional; only on tasks that build the visible surface
  - files: <path, path>

- [ ] T3 — <…>
  - acceptance: <observable outcome>
  - files: <path, path>
