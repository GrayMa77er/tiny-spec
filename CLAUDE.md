# CLAUDE.md — working on this skill suite

This folder has its own working guidance in **[AGENTS.md](AGENTS.md)** — read it
before editing anything here. It is the single source of truth for how to work on
this suite; this file just points at it so the harness loads the pointer.

**The one rule that matters most:** this suite exists to be *small* — earned
ceremony. Don't grow it back into waves, `owns:` contracts, a checkpoint matrix,
autonomous budgets, an orchestrator, or validators. Before adding any skill,
agent, artifact, format field, or knob, ask whether it clearly pays for itself;
when in doubt, leave it out.

Everything else — portability (no absolute paths; self-contained skills), contract
consistency across `CONTRACTS.md` and each skill's own `templates/`, dry-run
validation of prompt changes, runtime-verify over static checks, the safeguards to
trip, install, and commits — is in [AGENTS.md](AGENTS.md).
