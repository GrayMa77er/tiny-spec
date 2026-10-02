---
name: tiny-spec-design
description: Optional add-on for projects with a visual surface — turn wireframes and mockups into a project-wide token system in the constitution plus one D<n> screen entry per surface in the active SPEC.md, and record the visual: gate command. Re-run to re-anchor after a design export changes. Skip entirely for a CLI, library, or headless service.
---

# tiny-spec-design

Wireframes and mockups are worth nothing to a build agent as loose files — they get
read once and forgotten. This skill turns them into two durable things: a
**project-wide token system** in the constitution, and a **per-screen `D<n>` entry**
in the active `SPEC.md`. Together those arm the **visual gate**: a task carrying
`design: D<n>` is rendered, measured against the tokens, and can *fail* on a numeric
deviation.

**Skip this skill entirely** for a CLI, library, or headless service. A dead design
heading in the constitution is worse than none — it gets injected into every executor
and reviewer prompt for the life of the project.

## What this skill owns

Every other skill in the suite owns whole files. This one owns **named sections inside
two files other skills own** — the one deliberate exception, because the design system
is project-wide while the screens are per-ticket, and splitting them across two owners
is what made this material sprawl in the first place:

| Artifact | Section | Owner |
|---|---|---|
| `.spec/constitution.md` | `## Design system` | **this skill** |
| `.spec/constitution.md` | `visual:` line under Verification commands | **this skill** |
| `.spec/<active>/SPEC.md` | `## Design` (the `D<n>` entries) | **this skill** |
| everything else in both files | — | `tiny-spec-create` / `tiny-spec-plan` |

Write **only** those sections. Never touch a `REQ-N`, the rest of the constitution, or
any `status:` flag except as the update rules below require.

## Resolve the active ticket dir

Artifacts live under `.spec/`: the **shared** constitution at the root
(`.spec/constitution.md`), the per-ticket `SPEC.md` under `.spec/<slug>/`. Resolve the
active ticket dir from the current git branch: the `.spec/<slug>/` whose slug matches
the branch name (one branch per ticket). If none matches, use the sole ticket dir if
there's exactly one; else ask which.

**Two cases pre-empt that order — ask instead of applying it:** more than one dir
matches the branch (there is no defined tie-break, and inventing one here would
silently disagree with every other skill), or ticket dirs exist while you are on
`main`/`master` with no name match (the usual cause is a forgotten `git switch`, and
the sole-dir fallback would otherwise swallow it). Detached HEAD or no git repo is a
**degraded** case, not an ask case — branch match is simply unavailable, so fall
through to sole-dir and ask as written.

Requires `.spec/constitution.md` and `.spec/<active>/SPEC.md` to exist. If either is
missing, stop and point the user at `tiny-spec-create` — this skill adds sections to
documents, it does not create them.

## Pick your mode

| If | Mode |
|---|---|
| the constitution has no `## Design system` | **seed** — build the token system, then anchor screens |
| the token system exists, this ticket has no `## Design` yet | **anchor** — reuse the tokens, write this ticket's `D<n>` entries |
| `D<n>` entries exist and an export's `sha256` no longer matches | **re-anchor** — the design moved under the spec |

## Find and read the designs

**Actually read every file.** Look for a `design/` directory at the project root (also
accept paths the user hands you). `Read` renders images, so look at the PNG/JPG/SVG,
open the HTML mockup, read the Excalidraw. A design you did not open cannot be
described, and a guessed description is worse than none because it reads as
authoritative.

## Seed mode — propose the token system, don't measure it

Read *all* the designs together and infer **one coherent scale** across them: semantic
color roles, a single spacing step, a type scale, radii, elevation. Do **not** measure
each screen and record its pixels — image-derived per-screen values are unreliable and
produce no shared vocabulary. Snapping ragged wireframe values onto a clean scale is
the point, not a loss of fidelity.

Present the proposed system for approval and note anything you had to round. Then write
the constitution's **Design system** section, placed after `## Style`:

```markdown
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
```

**Every token needs a concrete value.** "A consistent spacing scale" fails nothing;
`space.1`=4px … `space.8`=32px fails a `padding: 19px`. A token with no value is worse
than no token, because it looks like a contract and isn't one.

Then add the scale as a **guiding invariant** in the constitution, since that is the
line a reviewer actually fails on: *"no raw color or spacing values in UI code —
reference a token."*

## The `visual:` command — ask for it, then confirm it runs

Record under the constitution's **Verification commands**:

```
- visual:  <the command that boots the UI so the reviewer can read back computed
  styles and geometry — e.g. a Playwright script that navigates to a route and prints
  getComputedStyle/getBoundingClientRect for the selectors it is given. Scratch files,
  gitignored.>
```

Ask that it **also screenshot each state it drives** and print `SCREENSHOT <state>
<path>` — one `page.screenshot({ path })` call next to the measuring it already does,
not a second script. That line is what lets the reviewer look at the render beside the
export, which is the only way to catch an element that measures perfectly and renders
invisibly. If the user says no, that's fine: the gate still works on numbers alone and
the reviewer reports the judge as not run.

**Confirm the command actually runs from a clean checkout.** It is the gate for every
task carrying `design:`; an aspirational command means the visual gate silently never
fires. A task that names a `D<n>` with no working `visual:` command here is a blocker,
not a silent pass — so either fix the command or drop the `design:` references.

## Anchor mode — write one `D<n>` per screen

Write one entry per screen **this ticket touches** into the active `SPEC.md`'s
`## Design` section, placed after `## Requirements`. If the token system already exists,
**reuse it** — describe this ticket's screens in the existing tokens and flag any screen
that genuinely needs a new token rather than inventing one silently.

```markdown
## Design

<`layout`, `elements`, and `states` may reference **only** token names defined in the
constitution's Design system — a raw value here (`24px`, `#3B82F6`) is a violation,
because it is how per-screen drift starts. Keep the source and export lines even when a
design is view-only: they are the provenance, and the sha256 is the staleness signal.>

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
```

Three things make or break the entry:

- **`sha256` is the staleness signal, so compute it** — `shasum -a 256 <file>`. Never
  invent it. A hash that was guessed makes the anchor permanently useless.
- **`elements:` selectors are a contract the code must match verbatim.** The reviewer
  measures exactly the selectors you name; without them it has to guess which node is
  "the error line", and a wrong guess measures the wrong element and passes. Prefer a
  **stable test id** (`[data-testid="signup-email"]`) over a CSS class — classes get
  renamed by refactors and mangled by CSS-in-JS, and a selector that silently stops
  matching is the exact failure this prevents.

  List the elements the design actually constrains — the ones whose spacing, type, or
  color you'd notice being wrong. A wrapper `<div>` nobody can see does not need a row.
  Five to ten rows describes most screens; past fifteen, the screen is probably two
  `D<n>` entries.
- **`layout:` carries the arrangement**, which no per-element row can express: the
  structure (single column, 3-col grid, sidebar + main), the max width, and the **order**
  elements appear in. This is what the reviewer compares geometry against.

**Link the requirements.** A `REQ-N` that a design bears on names its screen —
`REQ-3 — the signup form validates email inline (D1)`. That is what makes
`frame → REQ → task → files` greppable in both directions. This is the one edit this
skill makes outside its own sections; keep it to appending the `(D<n>)` reference.

**Sanity-check the selectors against the codebase.** A selector that assumes markup this
project can't produce — a class a component library owns and mangles, an id that
collides — becomes a build-time blocker. Prefer stable test ids and say where they get
added.

If the intent and a design **disagree**, do not silently pick one. Say what each says,
ask which wins, and record the answer in the `D` entry or `## Open questions`.

## Re-anchor mode — a design moved under the spec

Run `shasum -a 256 <export>` for every `D<n>` and compare with the recorded `sha256`.
A design that moved under a finished spec is otherwise completely invisible — no status
flips, and the build reviews against a screen that no longer exists.

- **Mismatch** → re-read that export, update the entry's `layout`/`elements`/`states`
  and its hash, then propagate staleness (below).
- **Missing export file** → a broken anchor. **Say so loudly and stop** rather than
  leaving an entry that points at nothing. A deleted export can mean a rename, a move,
  or a design that was withdrawn, and each wants a different answer. Never quietly drop
  the entry.
- **Every hash matches** → nothing to do; say so.

**Propagating staleness** after any change to a `D<n>` or to the token system:

1. Set `.spec/<active>/PLAN.md` to `status: stale` (if it exists).
2. Append a `decisions.md` entry to `.spec/<active>/decisions.md`, creating the file if
   absent:

   ```
   ## D-NNN — <short title>
   - type: change
   - date: <ISO date>
   - affects: D<n>, REQ-N
   - note: <what changed + why>
   ```

3. **Completed-work guardrail.** If a changed `D<n>` is built by a task already `[x]`
   in `PLAN.md`'s `## Tasks` (follow its `design:` field), **uncheck it** and name the
   unchecked ids in the same `decisions.md` entry. `tiny-spec-build` resumes from the checkbox state,
   so a task left `[x]` is a task it will never revisit — never assume built work
   survived a design change.

A token-system change touches **every ticket**, not just the active one — apply steps
1–3 to every ticket dir whose `SPEC.md` has a `## Design` section.

## When done

Report the tokens you defined (or reused), the `D<n>` entries written, and anything you
rounded or had to ask about. Say plainly whether the `visual:` command was confirmed to
run — if it wasn't, say that no task may carry a `design:` reference yet.

Then point the user at `tiny-spec-plan`, which hardens the token values and checks that
every token a `D<n>` names actually resolves.
