---
name: tiny-spec-scope
description: The greenfield on-ramp — turn a rough idea, or an existing PRD, into BREAKDOWN.md at the project root - a flat list of well-defined Features, each with draft acceptance criteria, a slug, and an optional needs: naming the features it must follow, plus a shared Decisions block. The one skill that works from a blank page. Does not scaffold .spec/ or touch the constitution — tiny-spec-create reads BREAKDOWN.md in seeded mode and does that. For an existing codebase use tiny-spec-adopt (plus this skill, if you also have a PRD to carve). The suite works without either.
---

# tiny-spec-scope

The **greenfield front door**. Takes what you have — a one-line idea, loose notes, a
PRD someone else wrote, wireframes — and turns it into the set of **features** to
spec, *before* any one of them is picked up.

It is the moment **before** `tiny-spec-create`: that skill takes **one feature → one
spec**; this one decides what the features *are*. You create the work items in your
tracker from the result, then run the normal flow per feature.

**A feature is the unit of work.** One feature = one spec = one branch = one plan→build
loop. There is no Story level beneath it — a feature is written well-defined enough to
build directly, and its acceptance criteria are what the spec's requirements come from.

**Starting from an existing codebase instead?** Use `tiny-spec-adopt` — it derives the
constitution from the code that's already there. The two are the suite's two front
doors, and you generally want exactly one of them. The exception is a **PRD for new
work on an existing codebase**: the PRD still needs carving into features, so run this
too (`tiny-spec-run` does both on its own: adopt for the constitution, scope for the
features).

This skill does **not** scaffold `.spec/`, create or edit `constitution.md`, or invoke
`tiny-spec-create`. It writes `BREAKDOWN.md` and stops. Keeping it at the project root
(not in `.spec/`) is deliberate: `.spec/` is per-spec build state; the breakdown is
pre-spec planning the tracker owns, and it is freely regenerable.

> **Earned ceremony — keep it thin.** This is the easiest place in the suite to fake
> rigor with a wall of polished prose. Don't. The breakdown exists to feed
> `tiny-spec-create` good features — not to be an artifact of record. Write the shortest
> one that does that, and leave optional sections out.

## Inputs

Anything the user has, or nothing at all. A one-line idea is enough.

- **A `PRD.md` or any doc the user points at** — read it and use it as the anchor, and
  record its path as `Source:` in the Decisions block. Its capability list is what you
  carve into features. A PRD you were handed means most of
  the interview below is already answered: confirm, don't re-ask.
- **Wireframes.** Glob a `design/` directory at the project root; also accept paths the
  user gives. **Visual inputs count as inputs** — `Read` renders images, so *look at*
  every PNG, JPG, and SVG, open every HTML mockup, read every Excalidraw. A wireframe
  is usually the only place the screen inventory, the states, and the real information
  hierarchy are written down, and none of that is recoverable from prose.

**Don't describe screens here.** A wireframe at this stage tells you what the product
*is* and which features touch a surface. It is far too early to pin down layout or
spacing, and the token system that would be written against does not exist yet. Route
each wireframe to the feature it belongs to via a `design:` pointer and move on —
`tiny-spec-design` anchors screens properly, once there is a constitution to anchor
them to.

**If two sources disagree, ask which wins and note it — don't silently pick.** This
bites hardest between prose and a wireframe, because the contradiction is quiet: the
text says one thing, the picture shows another, and whichever you read last wins by
accident. Name both readings explicitly when you ask, and record the answer inline on
the feature it affects.

## Interview — short, five groups

Keep it lean (earned ceremony). Ask only what you can't infer from the input; **skip
any group the material already answers.** A well-written PRD may collapse this to
group 4 and the playback.

1. **Problem & who has it.** What problem is this solving, and for whom? *(Hint: get
   the "why" before the "what". A breakdown that names the user and the pain carves
   itself; one that opens with a feature list doesn't.)*
2. **Goal & boundary.** What does success look like, and what is explicitly **out of
   scope** — the whole product, one epic, or an MVP slice? *(Hint: non-goals are as
   load-bearing as goals; they're what stops the carve boiling the ocean. You can
   re-run later for the next slice.)*
3. **Core capabilities.** What are the handful of things a user must be able to *do*?
   *(Hint: these are the seam — each becomes a Feature below, and each feature's
   `AC:` lines become that spec's `REQ-N`. Phrase each as a user-observable capability,
   not a component. Aim for the **minimum set that makes a coherent product** — if that
   needs a capability the idea didn't literally name, add it but **call it out in the
   playback** so the user can cut it; don't pad with speculative scope.)*
4. **Platform.** Where will these live — `ado | jira | github | monday`, or **ad-hoc**
   (no tracker)? *(Hint: each feature becomes **one** tracker item — whatever level the
   team builds against. Don't invent a hierarchy under it. Ad-hoc → kebab slugs, no
   tracker ids, no `Refs:` footer downstream.)*
5. **Tech & cross-cutting** (→ the Decisions block). Stack / framework, where code will
   live, and any cross-cutting non-functionals (auth, i18n, a11y, perf)? *(Hint: stack
   + code-location seed the constitution later; cross-cutting concerns become
   constitution invariants or shared requirements — **not** their own feature. One line
   each; don't design the system here.)*

**How big is a feature?** One buildable spec = one tight plan→build loop — typically a
handful of commits. If it can't be built and verified in one pass, split it into two
features as **vertical slices**, not layers. If it's a single tiny change, fold it into
the feature it serves.

**Well-defined means:** one user-observable capability, a short title that says what a
user can now do, atomic `AC:` lines that pin down its happy path and the negatives that
bound it, and nothing left that `tiny-spec-create` would have to invent.

Then **play back** the problem, the goal and non-goals, and the proposed Features with
their acceptance criteria, before writing. Adjust on feedback.

## Write `BREAKDOWN.md`

Write `BREAKDOWN.md` at the **project root** (the user's cwd) with the structure below:

```markdown
# Breakdown — <product / epic name>

<!-- A pre-spec worksheet. It lives at the PROJECT ROOT (not under .spec/) and is
     NOT a tracked .spec/ artifact. tiny-spec-create reads it in seeded mode: each
     Feature below becomes one .spec/<slug>/SPEC.md (its AC lines → REQ-N), and on the
     first create the Decisions block seeds the shared constitution.md.
     Regenerable — edit freely; the tracker (ADO/Jira/…) stays the source of truth. -->

## Problem

<!-- Required. The problem and who has it — the "why" before any "what". One short
     paragraph. Name the user and the pain; don't open with a feature list. -->

## Goal & non-goals

<!-- Required. What success looks like, and what is explicitly OUT of scope for now.
     Non-goals are load-bearing — they set the boundary this carve won't cross. -->

- Goal: <the outcome this delivers>
- Non-goal: <explicitly out of scope — re-run later for the next slice>

## Decisions

<!-- Project-wide framing. tiny-spec-create folds these into constitution.md on a
     feature's first run: Stack + Code-lives → Style and Layout; verification hints →
     Verification commands; Cross-cutting → Guiding invariants. Keep each to a line. -->

- Stack: <language / framework / runtime>
- Code lives: <where the code is — repo path, dirs of note>
- Platform: <ado | jira | github | monday | ad-hoc>   <!-- ad-hoc → kebab slugs, no tracker ids, no Refs footer -->
- Scope: <whole product | epic | MVP slice — the boundary of this breakdown>
- Cross-cutting: <non-functionals spanning features — auth, i18n, a11y, perf. These become constitution invariants or shared REQ, NOT their own feature.>
- Source: <path to the PRD or doc this carve came from — omit if it came from an interview>   <!-- tiny-spec-create reads it per feature for context and gaps -->

## Feature: <one user-observable capability>     slug: <ado-__ | kebab>     (tracker: <fill after creating, e.g. AB#120>)

- AC: <a single user-observable, testable outcome — becomes REQ-1 in this feature's SPEC.md>
- AC: <another — keep each atomic; no "and" hiding two capabilities>
- needs: <slug, slug>   <!-- optional; features this one must be built after. Omit when independent. -->
- design: <path(s) to the wireframe(s) covering this feature — omit if it has no visual surface>

## Feature: <one user-observable capability>     slug: <ado-__ | kebab>     (tracker: <…>)

- AC: <…>

<!-- optional: omit if N/A -->
## Success signals

<!-- How you'll know it's working — a metric, a behaviour, an acceptance bar. -->

<!-- optional: omit if N/A -->
## Open questions

<!-- What's still undecided. Surfacing it here beats guessing downstream. -->

## Suggested first spec

<feature title> (slug: <…>) — run tiny-spec-create on this first.
```

Required: **Problem**, **Goal & non-goals**, the **`## Decisions`** block, and at least
one **`## Feature:`** with a `slug:` and at least one `AC:`. `Success signals` and
`Open questions` are optional — omit them when they don't apply.

Each **`## Feature:`** is one work item: it becomes exactly one `.spec/<slug>/` and one
branch. Leave its tracker id blank for the user to fill after creating the item.

**`design:` is a pointer, not a description.** Route each wireframe you read to the
feature it belongs to, so `tiny-spec-design` knows which files to open for that spec
instead of re-deriving the mapping from filenames. A wireframe covering several features
is listed on each of them.

**`needs:` is what lets features build in parallel — so keep it honest and keep it rare.**
It names the features this one must be built *after*. `tiny-spec-run` uses it to group the
backlog into batches: features with no unmet `needs:` build concurrently, each in its own
git worktree, and the next batch starts once they merge. Three rules:

- **Name a feature only for a real code dependency** — this feature reads or edits files
  that one writes, or builds on a schema, API, or type it introduces. A shared theme or
  "it feels like it comes second" is **not** a dependency.
- **When unsure, omit it.** The two errors are not symmetric. A `needs:` you didn't need
  costs parallelism on every future run of this backlog, silently and forever. A `needs:`
  you missed costs one merge conflict, which `tiny-spec-run` already detects and halts on.
- **Never point across a cycle.** If two features each need the other, they are one
  feature — merge them, or split the shared part out into a third that both need.

Most backlogs need the field on a minority of features; a `needs:` on nearly every
feature means the carve is really a sequence, and you should say so rather than encode
it here.

**Slugs** mirror `tiny-spec-create`: derive from the platform key when bound — ADO
`AB#77`→`ado-77`, GitHub `#42`→`gh-42`, Monday item→`monday-<id>`, Jira `PROJ-123`
verbatim; **ad-hoc** → a short kebab-case slug (`email-login`). The tracker id is
unknown until the user creates the item, so leave the tracker placeholder and use a
provisional slug where needed.

**Acceptance criteria are draft `REQ-N`.** Write each as one **user-observable,
testable** outcome with no implementation detail — and keep it **atomic**: if a line
hides two capabilities behind an "and", split it. `tiny-spec-create` promotes these into
`REQ-N`, so atomic ACs here save a re-split later. They are also the approval:
`tiny-spec-create` will not re-confirm them feature by feature in a build-through run, so
write them as though nobody will read them again before code exists.

## When done

**If the caller asked you to commit** (`tiny-spec-run` does when it carves a PRD),
commit `BREAKDOWN.md` alone — `git add BREAKDOWN.md` and
`git commit -m "docs(scope): carve <name> into features" -- BREAKDOWN.md` — and nothing
else in the tree.

Print the carve — the features, each with its slug and `needs:` — and a **suggested
first spec**. Then **stop**. Tell the user the next steps, which you do **not** perform:

1. Create the Features in their tracker from `BREAKDOWN.md`, capturing the ids.
2. Run `tiny-spec-create` per feature — with `BREAKDOWN.md` present it reads each
   feature's entry instead of re-interviewing (seeded mode), and on first run seeds the
   constitution from the Decisions block. Or run `tiny-spec-run` and ask it to build the
   backlog, which walks the whole list.

Do **not** scaffold `.spec/`, write a constitution, or invoke `tiny-spec-create`
yourself — `scope` ends here.
