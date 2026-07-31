# Constitution

> This is the strongest, most persistent document in the project. It is
> **project-wide** — it lives at the `.spec/` root and anchors *every* ticket, not
> any one of them. Every task is implemented and reviewed against it. Keep it true;
> keep it lean. Project-specific richness belongs here — not scattered across tasks.

## Style
<Formatting, naming, language idioms. The defaults a reader should assume.>

<!-- conditional: the one section that may be omitted entirely. Include it only if
     this project has a visual surface; a CLI, library, or headless service should
     not carry a dead design heading. -->
## Design system
<The project-wide UI contract, written as **named tokens** — never raw values. Every
screen description and every line of UI code references these names, so a redesign
edits one table instead of every file. Name them DTCG-style (`color.surface.raised`,
`space.4`) so a token pipeline costs nothing to adopt later.
- color:     <semantic roles → value, e.g. `color.surface.base` #FFFFFF, `color.text.muted` #6B7280>
- space:     <one scale, e.g. `space.1`=4px … `space.8`=32px. A value off the scale is a violation.>
- type:      <named steps → size/weight/line-height, e.g. `type.heading.lg` 24px/600/1.25>
- radius:    <named steps, same rule>
- elevation: <named steps, same rule>
- states:    <what every interactive surface must define — default, hover, focus,
  disabled, loading, empty, error>
>

## Engineering standards
<Error handling, logging, testing approach, dependency policy, what "tested" means here.>

## Guiding invariants
<The non-negotiables. "Never X." "Always Y." The rules a reviewer can fail a task on.>

## Glossary
<Domain term — one-line definition. Keep the team speaking one language.>

## Layout
<Where things live. Directory map. Where new code of each kind goes.>

## Definition of Done
<The bar a task must clear to be checked off: e.g. code + tests + docs updated,
gate green, no TODOs left, matches the invariants above.>

## Verification commands
<The exact gate. The reviewer runs these. Example:
- install: `...`
- lint:    `...`
- test:    `...`
- build:   `...`
- run:     `...`
- visual:  `...`   # optional; only if there is a Design system above. The command
  that boots the UI so the reviewer can read back computed styles and geometry
  (e.g. a Playwright script that navigates to a route and prints
  getComputedStyle/getBoundingClientRect for the selectors it is given). Required
  before any task may carry a `design:` reference — a task that names one with no
  `visual:` command here is a blocker, not a silent pass.
>
