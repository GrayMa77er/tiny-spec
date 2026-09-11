# Changelog

All notable changes to tiny-spec are recorded here. Format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Every release upgrades the same way: re-run `uvx tiny-spec install` and restart
Claude Code.

## [1.0.1] — 2026-09-11

Documentation only. No skill, agent, or artifact format changed — upgrading is optional.

### Changed

- **README prose trimmed.** The argument sections had outgrown their weight. The
  comparison footnote, the "why it's small" bullets, the design-judge and
  `visual:`-command explanations, and the story-run notes were tightened to what each
  actually claims.
- **Eval results cite the version, not the commit.** The benchmark section pinned its
  numbers to three commit SHAs, which say nothing to a reader and go stale every release.

### Fixed

- `tiny_spec.__version__` had been left at `0.5.0` since the 1.0 release; it now tracks
  `pyproject.toml`.

## [1.0.0] — 2026-09-07

A refocus, not a feature release. Same core loop — one task, one commit, an independent
reviewer running the real gate — reorganised around **two front doors, three core
stages, and one router**. Four skills became two, one skill was extracted, and one
genuinely new skill was added.

### ⚠️ Breaking — read before upgrading

Four skills were removed. `tiny-spec install` copies what the manifest declares; it does
**not** delete skills that left it. So the removed ones will linger in
`~/.claude/skills/` and Claude Code will keep offering them.

```sh
tiny-spec uninstall        # removes the old set
uvx tiny-spec install      # installs the 1.0 set
```

Then **restart Claude Code** — skills load at startup.

| Removed | Replaced by |
|---|---|
| `tiny-spec-prd` | `tiny-spec-scope` — one on-ramp instead of two |
| `tiny-spec-breakdown` | `tiny-spec-scope` |
| `tiny-spec-tasks` | `tiny-spec-plan` — now writes `PLAN.md` **and** `tasks.md` in one pass |
| `tiny-spec-loop` | `tiny-spec-run` — one router with two stop points |

**`PRD.md` is no longer an artifact.** It was a pure intermediate — breakdown read it,
then create read breakdown. Its problem/goal/non-goal material now lives in
`BREAKDOWN.md`'s header. An existing `PRD.md` is still readable *input* to
`tiny-spec-scope`; it just isn't written any more.

**`CONTRACTS.md` was deleted.** No skill read it at runtime, and keeping it in sync by
hand was pure drift surface. Every format now lives inline in the skill that owns it.
Artifact ownership is mapped in [AGENTS.md](AGENTS.md).

Artifacts on disk are **unchanged** — `SPEC.md`, `PLAN.md`, `tasks.md`,
`constitution.md`, `memory.md`, `decisions.md` all keep their formats. An in-flight
`.spec/` keeps working; only the commands change.

### Added

- **`tiny-spec-adopt` — the brownfield front door.** The suite's stated thesis has
  always been that real work is a ticket inside a system that already exists, but every
  skill behaved as though you were starting from a blank page: the constitution was
  *interviewed* out of you, including the verification commands.

  `tiny-spec-adopt` reads the repo instead. It derives the gate from CI workflows, task
  runners, and tool config (CI wins — whatever runs on every PR *is* the real gate),
  the layout from the actual tree, style and standards from linter config and observed
  idiom, and invariants from `CONTRIBUTING.md`/ADRs where someone already wrote them
  down. Every section is marked **declared** or **inferred** so you know what to
  distrust.

  Then it **runs the commands it derived** and reports which went green. A derived gate
  that has never been run is the most dangerous thing the suite can produce — it turns
  every future review into theatre.

  Read-only against your code: it never modifies source, creates a spec dir, or touches
  git. Re-run it in **refresh mode** after the codebase drifts; it diffs rather than
  overwrites, and marks completed tasks stale, since they were reviewed against the
  previous constitution.

- **`tiny-spec-scope` — the greenfield front door.** Takes a rough idea *or* a PRD you
  already have and produces `BREAKDOWN.md` in one interview instead of two.

- **`tiny-spec-design` — the visual system, extracted.** Tokens, `D<n>` screen entries,
  export hashing, and the `visual:` gate command used to be threaded through
  `tiny-spec-create`, `tiny-spec-run`, and the constitution. They now live in one
  optional skill you run only when a project has a visual surface. Non-UI projects no
  longer read past ~35% of `tiny-spec-create`.

  The reviewer's visual gate is unchanged — only *authoring* moved.

### Changed

- **`tiny-spec-plan` now writes `PLAN.md` and `tasks.md` in one pass.** They stay two
  files (build rewrites `tasks.md` constantly; mixing that into design prose is worse)
  but they are now **one staleness unit** — reconciled together, never left disagreeing.
  One fewer command, one fewer status flag to reason about.

- **`tiny-spec-run` is the only router, with a stop point fixed at Step 0.** By default
  it walks the chain and stops before the build, exactly as before. Ask it to build
  ("build the backlog", "spec it out and build it") or hand it a story list, and it runs
  the per-story branch → plan → build → merge cycle that was `tiny-spec-loop`.

  **The stop point is decided once from your opening request and never revised** — not
  by a stage's closing line, not by a rung, not by a later "do it all". Build is your
  review gate, so a run you started as "get it ready" will not promote itself into
  building. The old absolute "`run` never invokes `build`" was a stronger guarantee;
  this is the rule that replaces it, and it is the invariant to watch in this release.

  Everything else carries over unchanged: the six terminal states and the never-round-up
  rule, no merge without `done`, no run-state file (progress is derived from git), no
  budget, and the same five git commands — `switch`, `switch -c`, `merge --no-ff`,
  `merge --abort`, and reads. It still never pushes, rebases, resets, or deletes a
  branch.

- **The router's ladder went from 12 rungs to 8**, because merging skills removed rungs
  rather than relocating them. Its first rung now carries the greenfield/brownfield
  fork: does this repo already contain source?

### Removed

- `tiny-spec-prd`, `tiny-spec-breakdown`, `tiny-spec-tasks`, `tiny-spec-loop` — see the
  breaking notice above.
- `CONTRACTS.md` — folded into the skills.

## [0.5.0] — 2026-08-30

### Added

- **`tiny-spec-loop` — work a whole list of stories, one after another.** Point it at
  your `BREAKDOWN.md` (or paste a list) and for each story it cuts a branch from `main`,
  runs the planning chain, builds every task, merges the finished branch back locally,
  and moves to the next one.

  Each branch is cut **fresh from the integration branch**, so story 3 sees stories 1
  and 2 already merged — which is what makes an ordered list build correctly, and why a
  story that doesn't finish stops the run instead of being skipped.

  **Every run ends in one of six terminal states, named out loud:** `done`, `blocked`,
  `exhausted`, `paused`, `fork`, `conflict`. **Only `done` means the work is built** —
  and in a story loop that means *every* story merged. A run that stopped at story 2 of
  7 reporting "all done" is the failure mode this exists to prevent, so the report
  always names what merged and how many stories are still untouched.

  Like `tiny-spec-run` it owns nothing: no artifact, no state file, no run log.
  Progress is **derived** — a story whose ticked `tasks.md` is on `main` is merged, a
  `.spec/<slug>/` with an unchecked task is in progress, no directory means not started
  — so a run you abandon overnight resumes correctly the next day.

  **What it will not do to your repo:** it runs exactly `switch`, `switch -c`,
  `merge --no-ff`, `merge --abort`, and reads. It refuses to start on a dirty tree, and
  it never pushes, rebases, resets, deletes a branch, or opens a PR. A red gate after a
  merge is reported with the undo command rather than undone. It also never resolves a
  blocker for you — a loop allowed to rewrite the requirement its own task just failed
  would be grading its own homework.

- **`pause:` — a task field that stops the build before that task runs.** Put
  `pause: <why>` on a task and the build halts *before* dispatching it, leaving it
  unchecked, so you review the approach while redirecting it is still cheap.
  `tiny-spec-tasks` proposes one for genuinely irreversible work — migrations,
  destructive file operations, a new dependency, an auth boundary, a public API
  contract. Pause points are **technical**, not per-story: you can also hand a run a
  standing policy ("halt before anything that touches auth") and it gets applied as each
  story's tasks are sliced. Waive one for a single run by saying so; overrides are never
  written back to `tasks.md`.

- **`type: halt` and `state:` in `decisions.md`,** so a halt survives a walk-away.
  `blocked`/`exhausted` stay `type: blocker`; a `fork` logs `type: halt`. `done`,
  `paused`, and `conflict` log nothing — a green tree, a `pause:` line on the first
  unchecked task, and an unmerged branch each already say why the loop stopped, and a
  log that restates what another file shows is a second source of truth with extra
  steps.

### Changed

- **`tiny-spec-create` no longer re-confirms requirements during a loop run.** In
  seeded mode the story's `AC:` lines are the approval — you reviewed them when you
  wrote or accepted `BREAKDOWN.md` — so asking again once per story is asking the same
  question twice. Everything that is a genuine question still stops the run:
  contradictory ACs, an AC that won't become a testable requirement, a missing ticket
  id, a design export that isn't on disk. Invoked directly, it confirms exactly as
  before.
- **`tiny-spec-run` forwards stage-addressed caller briefs verbatim** and acts on none
  of them. The ladder is unchanged.

### Upgrading

Re-run `uvx tiny-spec install` and **restart Claude Code** — `tiny-spec-loop` is a new
skill, and skills only load at startup, so it stays invisible until you do.

Nothing else changes. Existing `tasks.md` files are valid as they are: `pause:` is
optional, and a task list without one builds exactly as it did in v0.4.0. Invoked
directly, every skill behaves as before — the loop-run waiver in `tiny-spec-create`
applies only when `tiny-spec-loop` is driving.

### Notes

No budget, no turn ceiling, no checkpoint config, and no state file. **The story list
is the budget** — the run ends when the stories end.

## [0.4.0] — 2026-08-03

### Added

- **The visual gate now looks at what it measured.** Since v0.3.0 a task tagged
  `design: D1` has been graded by measuring every selector the `D<n>` names against
  your design tokens. Numbers catch the wrong padding and the renamed test id — they
  cannot catch an element that is present in the DOM, carries every correct token, and
  is invisible on screen: `opacity: 0`, zero height, occluded by a sibling, clipped out
  of view, or the same color as its background.

  The reviewer now reads a screenshot of each state it just measured beside your
  committed export and grades four things: **presence** (is each element actually
  visible), **legibility** (clipped, truncated, overlapping, unreadable contrast),
  **correspondence** (same regions, same reading order), and **hierarchy**. The first
  three fail the task; hierarchy is always a flag.

  **Numbers keep precedence wherever they already applied.** Padding that is on your
  `space.*` scale but "looks cramped" is a `flag:`, never a failure — which stops the
  two halves of the gate returning opposite verdicts on the same element and burning
  the bounded fix loop on something no executor can resolve. It is still not a pixel
  diff: your export is usually a wireframe, so this judges structure and legibility,
  not visual identity.

### Changed

- `tiny-spec-plan` now checks your constitution for a screenshot-emitting `visual:`
  command and adds the call the next time it hardens the constitution.
- The README now says *how* a design reaches the flow. It documented `design/`, the
  `D<n>` entries, and the token system, but never named which skill reads them — so
  there was no way to learn that there is no design flag to pass. `tiny-spec-create`
  reads every file in `design/`, whether invoked directly or reached via
  `tiny-spec-run`.

### Upgrading

Your `visual:` command should now screenshot each state it drives and print
`SCREENSHOT <state> <path>` — one `page.screenshot({ path })` call next to the
measuring it already does (see the `visual.mjs` example in the README). Printing
`opacity` and `visibility` alongside the other computed styles is worth doing too: it
turns the cheapest kind of invisible element into a numeric failure.

**Nothing breaks if you skip it.** A command that prints no `SCREENSHOT` line still
gates on numbers exactly as in v0.3.0; the reviewer reports `judge: not run` and flags
it rather than failing or blocking the task. No new skills, agents, or dependencies —
tiny-spec still ships no browser code, and the `visual:` command stays yours.

## [0.3.0] — 2026-07-31

### Added

- **`tiny-spec-run`** — an optional router that walks `create → plan → tasks` in one
  command, reconciling anything stale before anything missing. It owns no artifact and
  writes nothing; it resolves where your ticket stands from the files on disk and
  delegates. It **stops before `tiny-spec-build`**, which stays your review gate.
- **`tiny-spec-prd`** — an optional planning on-ramp that interviews a rough idea into
  a `PRD.md`. The one skill that works from a blank page. Stacks in front of
  `tiny-spec-breakdown`.
- **Designs anchored to specs and enforced at build time.** Drop exported wireframes in
  `design/` and `tiny-spec-create` reads them as images, proposes a project-wide design
  system of named tokens for your approval, and describes each screen as a `D<n>` entry
  in `SPEC.md` — its layout, its elements with a selector each, and the states it must
  render.

  Tag a task `design: D1` and the reviewer renders that surface, measures the named
  selectors with `getComputedStyle`/`getBoundingClientRect`, and **fails the task** on
  an off-scale value, an element that was never built, or a state the design calls for
  and the code doesn't render. Tasks without the tag are graded exactly as before.

  No Figma token, plugin, or design SaaS — a view-only account works, since the
  committed export is what the agents read. Change an export and its recorded hash
  stops matching, marking the spec stale the same way editing a requirement does.
- **Constitution repair.** The constitution is project-wide, so it can go missing while
  your specs survive. Re-running `tiny-spec-create` rebuilds it from whatever is already
  written down and marks completed tasks stale, since they were reviewed against a
  document that wasn't there.

### Changed

- **Skills no longer ship `templates/`.** Every document skeleton is inline in its
  owning `SKILL.md`. Those templates installed outside your project, so reading one
  prompted for permission — up to seven prompts before a run wrote anything. Each skill
  is now a single self-contained file.

  *Breaking for customizations:* if you had edited an installed template, that change is
  not carried over.

### Fixed

- `tiny-spec-create` now clears `SPEC.md`'s own `status:` in update mode. `plan` and
  `tasks` always did; `create` didn't — so a SPEC hand-edited to `stale` could never be
  cleared and the chain jammed at its root.
- Every skill resolves the active ticket the same way, including the edge cases. Two
  situations previously resolved confidently and wrongly: more than one ticket dir
  matching the branch, and being on `main`/`master` with dirs present but no name match
  (usually a forgotten `git switch`, where the sole-dir fallback would silently adopt
  whatever ticket existed). Both now ask.

## [0.2.1] — 2026-06-25

### Added

- **`tiny-spec-breakdown`** — an optional skill that turns a PRD (plus
  wireframes/notes) into a `BREAKDOWN.md`: a flat list of Features → Stories with draft
  acceptance criteria.
- `tiny-spec-create` reads `BREAKDOWN.md` — pulls a story's acceptance criteria into
  `REQ-N` and seeds the constitution, skipping the full interview.

## [0.2.0] — 2026-06-25

Superseded by 0.2.1, which carries the same changes. This version did not publish
successfully to PyPI.

## [0.1.1] — 2026-06-25

Republished 0.1.0 to trigger the PyPI workflow. No functional changes.

## [0.1.0] — 2026-06-25

The first release — a tiny, opinionated take on spec-driven development for Claude
Code. You write the intent; it produces a design, a task list, and then builds the work
one task at a time. Every task is implemented by one agent and graded by an independent
reviewer that runs your real tests before anything is committed.

[0.5.0]: https://github.com/GrayMa77er/tiny-spec/releases/tag/v0.5.0
[0.4.0]: https://github.com/GrayMa77er/tiny-spec/releases/tag/v0.4.0
[0.3.0]: https://github.com/GrayMa77er/tiny-spec/releases/tag/v0.3.0
[0.2.1]: https://github.com/GrayMa77er/tiny-spec/releases/tag/v0.2.1
[0.2.0]: https://github.com/GrayMa77er/tiny-spec/releases/tag/v0.2.0
[0.1.1]: https://github.com/GrayMa77er/tiny-spec/releases/tag/v0.1.1
[0.1.0]: https://github.com/GrayMa77er/tiny-spec/releases/tag/v0.1.0
