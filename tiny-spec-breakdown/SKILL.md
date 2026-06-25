---
name: tiny-spec-breakdown
description: Optional Phase-0 on-ramp — read a PRD plus wireframes/notes, interview briefly, and decompose the work into a flat list of Features → user Stories (each with draft acceptance criteria and a slug) plus a shared Decisions block, written to BREAKDOWN.md at the project root. Does not scaffold .spec/ or touch the constitution — tiny-spec-create reads BREAKDOWN.md in seeded mode and does that. The suite works without it.
---

# tiny-spec-breakdown

Turns a body of source material — a PRD, wireframes, loose notes — into the set of
**user stories** to spec, *before* any one of them is picked up. It is the moment
**before** `tiny-spec-create`: that skill takes **one story → one spec**; this one
decides what the stories *are*.

This is an **optional** front door. The suite works fine without it — start at
`tiny-spec-create` for a single known piece of work. Reach for `breakdown` only when
you have a multi-story PRD to carve.

**It writes exactly one file: `BREAKDOWN.md` at the project root.** It does **not**
scaffold `.spec/`, does **not** create or edit `constitution.md`, and does **not**
run `tiny-spec-create` or loop over stories. It produces the worksheet and stops —
you create the work items in your tracker from it, then run the normal flow per
story. Keeping the carve out of `.spec/` is deliberate: `.spec/` is per-spec build
state; the breakdown is pre-spec planning the tracker owns.

## Inputs

Take one or more file paths from the user (a PRD is the usual anchor; wireframes,
design notes, an API sketch are common companions). **Read them all.** If two
sources disagree, ask which wins and note it — don't silently pick.

## Interview — short, five groups

Keep it lean (earned ceremony). Ask only what you can't infer from the inputs; skip
a group the material already answers.

1. **Inputs & boundary.** Which files are in scope, and what's the boundary of *this*
   breakdown — the whole product, one epic, or an MVP slice? *(Hint: anchors against
   boiling the ocean; you can re-run later for the next slice.)*
2. **Platform & hierarchy.** Where will these live — `ado | jira | github | monday`,
   or **ad-hoc** (no tracker)? Which levels does the team actually use? *(Hint: ADO
   default is Epic › Feature › Story › Task, but many teams skip Feature — don't
   invent levels they won't track. Ad-hoc → kebab slugs, no parent ids, no `Refs:`
   footer downstream.)*
3. **Structure & granularity.** How should features be grouped — by user journey, by
   screen/surface, by domain/module, or by persona? And how big is a story? *(Hint:
   wireframes push toward screen-based, a PRD usually reads journey-based — pick one
   lens. A story = one buildable spec = one tight plan→build loop; if it can't be
   built and verified in one pass, split it as a vertical slice, not a layer.)*
4. **Tech & cross-cutting** (→ the Decisions block). Stack / framework, where code
   lives, and any cross-cutting non-functionals (auth, i18n, a11y, perf)? *(Hint:
   stack + code-location seed the constitution later; cross-cutting concerns become
   constitution invariants or shared requirements — **not** their own feature.)*
5. **Confirm the carve.** Play back the proposed Features and the stories under each
   before writing. Adjust on feedback.

## Write `BREAKDOWN.md`

Copy this skill's `templates/BREAKDOWN.template.md` to `BREAKDOWN.md` at the
**project root** (the user's cwd) and fill it in:

- the **`## Decisions`** block — stack, code location, platform, structure lens,
  scope, cross-cutting concerns;
- one **`## Feature:`** heading per feature (a grouping only — it never becomes a
  folder), with the tracker-parent id left blank for the user to fill after creating
  it;
- under each feature, the **stories** — each a single user-observable capability,
  with a proposed **slug** and its **draft acceptance criteria** (`AC:` lines).

**Slugs** mirror `tiny-spec-create`: derive from the platform key when bound —
ADO `AB#77`→`ado-77`, GitHub `#42`→`gh-42`, Monday item→`monday-<id>`, Jira
`PROJ-123` verbatim; **ad-hoc** → a short kebab-case slug (`email-login`). The
tracker id is unknown until the user creates the item, so leave the parent-id
placeholder and use a provisional slug where needed.

**Acceptance criteria are draft `REQ-N`.** Write each as one **user-observable,
testable** outcome with no implementation detail — and keep it **atomic**: if a line
hides two capabilities behind an "and", split it. `tiny-spec-create` promotes these
into `REQ-N`, so atomic ACs here save a re-split later.

## When done

Print the carve — the features and the stories under each — and a **suggested first
spec** (which story to pick up first). Then **stop**. Tell the user the next steps,
which you do **not** perform:

1. Create the Features and Stories in their tracker from `BREAKDOWN.md`, capturing
   the ids.
2. Run `tiny-spec-create` per story — with `BREAKDOWN.md` present it reads each
   story's entry instead of re-interviewing (seeded mode), and on first run seeds the
   constitution from the Decisions block.

Do **not** scaffold `.spec/`, write a constitution, or invoke `tiny-spec-create`
yourself — `breakdown` ends here.
