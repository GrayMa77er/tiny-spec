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

## Pull requests

1. Branch off `main`.
2. Make the change and dry-run it (see [AGENTS.md](AGENTS.md) for how).
3. Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for
   commit messages.
4. Open a PR describing what changed, which skills or agents you touched, and how
   you verified it.
