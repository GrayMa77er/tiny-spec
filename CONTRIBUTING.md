# Contributing

Thanks for your interest in tiny-spec. Issues and pull requests are welcome.

Before changing any skill or agent, read [AGENTS.md](AGENTS.md). It is the source
of truth for how to work on this suite. A few things worth knowing up front:

- **Keep it small.** This suite exists to stay lean. Before adding a skill, agent,
  template, format field, or knob, the bar is: does it clearly pay for itself? When
  in doubt, leave it out.
- **Skills are prompts, not code.** Editing a `SKILL.md` or agent file changes a
  prompt. There is no compiler or test to catch a misleading instruction, so keep
  the formats consistent by hand and check [CONTRACTS.md](CONTRACTS.md) when you
  touch an artifact's shape.
- **Verify at runtime.** Validate prompt changes by dry-running them in a throwaway
  directory or dispatching the real agents, rather than reasoning about them
  statically.
- **Stay portable.** No absolute paths. Each skill carries its own `templates/` and
  works wherever it is dropped.

## Running the evals

The suite ships with maintainer-only evaluations under [`docs/eval/`](docs/eval/).
**They do not run in CI** — each spins up throwaway sandboxes and drives the real
flow with the `claude` CLI, so they cost tokens and minutes. You have to run them
**by hand** when your change touches the stage they cover. Prereqs: `claude`,
`python3`, `git` (no global install needed — the harnesses vendor the repo's skills
into each sandbox).

- **Execution loop** (`create → plan → tasks → build`) — held-out grade of produced
  code:

  ```sh
  docs/eval/harness/run.sh                 # all benchmark tasks
  docs/eval/harness/run.sh roman duration  # a subset while iterating
  ```

- **Planning stage** (`tiny-spec-prd → tiny-spec-breakdown`) — structural checks +
  an LLM judge on the produced `PRD.md`/`BREAKDOWN.md`:

  ```sh
  docs/eval/harness/run-planning.sh        # all planning cases
  docs/eval/harness/run-planning.sh snip   # a subset while iterating
  ```

- **Static design review** — no tokens, scores the design against the rubric:
  run the `/eval-suite` skill.

Start with a single task/case while iterating (the full run is slow). See
[`docs/eval/README.md`](docs/eval/README.md) for what each measures, the env knobs
(`CLAUDE_MODEL`, `JUDGE_MODEL`, `KEEP_SANDBOX`, …), and how scores are recorded.

## Pull requests

1. Branch off `main`.
2. Make the change and dry-run it (see [AGENTS.md](AGENTS.md) for how).
3. If you touched the build loop or the planning skills, **run the matching eval
   harness manually** (above) and note the result in the PR.
4. Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for
   commit messages.
5. Open a PR describing what changed, which skills or agents you touched, and how
   you verified it.
