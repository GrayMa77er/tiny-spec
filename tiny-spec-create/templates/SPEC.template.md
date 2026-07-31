---
status: current
updated: <ISO date>
# Ticket binding (reference-only). Omit this whole block if there is no ticket.
ticket:
  provider: jira | github | ado | monday
  id: <PROJ-123 | #42 | AB#77 | item id>
  url: <link to the ticket>
  status: <optional manual mirror of the platform status, e.g. In Progress>
---

# <Project / feature name>

<!-- optional: omit if N/A -->
## Context

<Why now — the background, the problem, what prompted this. No solution detail.>

## Intent

<One paragraph: what this is and why it exists. The "what" and "why", never the "how".>

## Requirements

<Each REQ is one user-observable, testable capability. No implementation detail.
If a line hides two capabilities behind an "and", split it.>

- REQ-1 — <capability>
- REQ-2 — <capability>
- REQ-3 — <capability>

<!-- optional: omit if this ticket has no visual surface -->
## Design

<One `D<n>` entry per screen or surface this ticket touches. `layout`, `elements`, and
`states` may reference **only** token names defined in the constitution's Design
system — a raw value here (`24px`, `#3B82F6`) is a violation, because it is how
per-screen drift starts. Keep the source and export lines even when a design is
view-only: they are the provenance, and the sha256 is the staleness signal.

The `elements:` selectors are a **contract the code must match verbatim** — the
reviewer measures exactly these. Prefer a stable test id over a CSS class; classes get
renamed by refactors and mangled by CSS-in-JS, and a selector that silently stops
matching is the exact failure this prevents.>

- D1 — <screen / surface name>
  - source: <Figma URL#node-id, or the tool of record; "view-only" if you can't export from it>
  - export: design/<file>.png            # the committed artifact the reviewer can actually read
  - sha256: <hash of that export>        # changes when the design changes → this SPEC goes stale
  - layout: <the arrangement and the order — e.g. "single centered column, max 420px;
    title → field → error → submit". This is what the reviewer checks geometry against.>
  - elements:
    - <name>  `<selector>`  → <the tokens this element must satisfy>
    - <name>  `<selector>`  → <…>
  - states: <which of empty / loading / error / success this surface must render, and what each shows>

<!-- optional: omit if N/A -->
## Non-goals

<What this explicitly does NOT cover — scope boundaries that prevent creep.>

<!-- optional: omit if N/A -->
## Success criteria

<How we'll know the whole spec succeeded, beyond the per-requirement acceptance —
e.g. a metric, an end-to-end scenario, a stakeholder sign-off.>

<!-- optional: omit if N/A -->
## Open questions

<Unresolved questions that may change requirements. Resolve before/while planning.>

<!-- optional: omit if N/A -->
## Links

<Ticket, related specs, design docs, prior art.>
