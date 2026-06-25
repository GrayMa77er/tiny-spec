---
status: current
updated: <ISO date>
---

# Tasks — <project / feature name>

> Executed top to bottom, one at a time. A checked `[x]` task is implemented AND
> reviewed. `type:` and `req:` are optional; `files:` is a hint, not an ownership
> contract.

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
  - files: <path, path>

- [ ] T3 — <…>
  - acceptance: <observable outcome>
  - files: <path, path>
