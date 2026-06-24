# Conventions — the constitution

> This is the strongest, most persistent document in the project. Every task is
> implemented and reviewed against it. Keep it true; keep it lean. Project-specific
> richness belongs here — not scattered across tasks.

## Style
<Formatting, naming, language idioms. The defaults a reader should assume.>

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
>
