# Memory — operational lessons

> Curated, forward-acting lessons that should survive across runs so the blind
> executor and reviewer don't re-learn them. **Project-wide** — lives at the
> `.spec/` root and is shared across every ticket. NOT a changelog. Prune superseded
> entries. Code-style rules belong in `constitution.md`; one-off history in the
> ticket's `decisions.md`.

<!-- Each entry:
- type: environment | pitfall | tried-rejected | hotspot
  lesson: <one line — the operational fact>
  apply:  <one line — why it matters / what to do about it>
-->

- type: environment
  lesson: <e.g. the test suite needs the package installed (`pip install -e .`) first>
  apply:  <run the documented setup before the gate; a bare `pytest` gives a false red>
