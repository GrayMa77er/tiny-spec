# Security policy

## Supported versions

tiny-spec is a small, single-maintainer project. Only the **latest release** gets
fixes — there are no maintenance branches. Upgrade with `uvx tiny-spec install`.

## What the threat surface actually is

Worth being precise, because it is unusual for a Python package:

- **The installer** (`tiny_spec/`) is standard-library only, has no runtime
  dependencies, and does two things: copy markdown files into `~/.claude/skills/` and
  `~/.claude/agents/`, and remove what it copied. A bug here could overwrite files in
  your Claude config directory.
- **The skills and agents are prompts.** They ship no executable code. Their risk is
  that they instruct a coding agent to run commands in your repository — notably the
  `tiny-spec-build-reviewer`, which runs the verification commands *you* wrote into
  your own `constitution.md`, and executes your `visual:` command if you defined one.
  tiny-spec never supplies those commands; it runs what your project declares.
- **Prompt injection is a real consideration.** The skills read files from your project
  — `PRD.md`, `BREAKDOWN.md`, ticket text, and design exports under `design/`. Content
  in those files is treated as input to an agent that can write code and run commands.
  Treat untrusted design exports and ticket descriptions with the same care you would
  give any input to an agent with shell access.

A report that the suite can be steered into running something harmful **through
content it reads** is in scope and worth filing.

## Reporting a vulnerability

Use GitHub's private reporting: **Security → Report a vulnerability** on
[the repository](https://github.com/GrayMa77er/tiny-spec/security/advisories/new).
That keeps the report private until there's a fix.

Please don't open a public issue for a security problem.

Include what you did, what happened, and what you expected. A reproduction — a repo
state and the prompt or command that triggers it — is far more useful than a
description, since almost everything here is prompt behavior rather than code.

**Expectations, honestly set:** this is one person's side project. I aim to acknowledge
within a week. There is no bounty, and no guaranteed fix timeline. If something is
serious and I have gone quiet, open a public issue asking me to check my advisories.
