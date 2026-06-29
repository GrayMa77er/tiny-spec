---
name: tiny-spec-prd
description: Optional planning on-ramp — turn a rough product idea into a short PRD through a brief interview, written to PRD.md at the project root. The one skill that works from a blank page. Does not scaffold .spec/, touch the constitution, or carve stories — tiny-spec-breakdown reads PRD.md and decomposes it into Features → Stories. The suite works without it.
---

# tiny-spec-prd

Turns a **rough idea** — a sentence, a few notes, a sketch — into a short **PRD**:
the *what* and *why* of the product, before any stories exist. It is the moment
**before** `tiny-spec-breakdown`: that skill carves a PRD into stories; this one
**writes** the PRD.

This is an **optional** planning on-ramp, and the only skill that starts from a
blank page. The suite works fine without it — if you already have a PRD (or any
source material), skip straight to `tiny-spec-breakdown`; if you have a single known
piece of work, skip both and start at `tiny-spec-create`. Reach for `prd` only when
you have an idea but nothing written down yet.

**It writes exactly one file: `PRD.md` at the project root.** It does **not**
scaffold `.spec/`, does **not** create or edit `constitution.md`, and does **not**
run `tiny-spec-breakdown` or carve stories. It produces the PRD and stops. Keeping it
at the project root (not in `.spec/`) is deliberate: `.spec/` is per-spec build
state; the PRD is pre-spec planning, regenerable, the same tier as `BREAKDOWN.md`.

> **Earned ceremony — keep it thin.** A PRD is the easiest place in this suite to
> fake rigor with a wall of polished prose. Don't. The PRD exists to *feed
> breakdown* — a tight statement of problem, goal, and capabilities — not to be an
> artifact of record. Write the shortest PRD that lets `tiny-spec-breakdown` carve
> good stories. Leave optional sections out when the idea doesn't need them.

## Inputs

Anything the user has, or nothing at all. A one-line idea is enough; loose notes,
competitor links, or a rough sketch are welcome companions. **Read any files they
point at.** Where the idea is silent, the interview fills the gaps — don't invent
scope the user hasn't asked for.

## Interview — short, four groups

Keep it lean (earned ceremony). Ask only what you can't infer from the input; skip a
group the idea already answers.

1. **Problem & who has it.** What problem is this solving, and for whom? *(Hint: a
   PRD that names the user and the pain writes itself; one that opens with a feature
   list doesn't. Get the "why" before the "what".)*
2. **Goal & boundary.** What does success look like, and what is explicitly **out of
   scope** for now — the whole product, one epic, or an MVP slice? *(Hint: non-goals
   are as load-bearing as goals; they stop breakdown from boiling the ocean. You can
   re-run later for the next slice.)*
3. **Core capabilities.** What are the handful of things a user must be able to *do*?
   And any cross-cutting non-functionals (auth, i18n, a11y, perf)? *(Hint: these
   bullets are the seam — `tiny-spec-breakdown` groups them into Features → Stories,
   so phrase each as a user-observable capability, not a component. Cross-cutting
   concerns become constitution invariants or shared requirements downstream, **not**
   their own capability. Aim for the **minimum set that makes a coherent product** — if
   that needs a capability the idea didn't literally name, add it but **call it out in
   the playback** so the user can cut it; don't pad with speculative scope.)*
4. **Constraints & signal.** Any stack/platform constraints already decided, and how
   you'll know it's working? *(Hint: stack/platform hints flow into the breakdown
   Decisions block later; a success signal keeps the PRD honest. Keep both to a line
   each — don't design the system here.)*

Then **play back** the problem, goal, non-goals, and the capability list before
writing. Adjust on feedback.

## Write `PRD.md`

Copy this skill's `templates/PRD.template.md` to `PRD.md` at the **project root**
(the user's cwd) and fill it in:

- **Problem / context** and **Goal & non-goals** — required; the spine of the PRD;
- **Core capabilities** — required; a bullet list of user-observable capabilities,
  each atomic (no "and" hiding two), which `tiny-spec-breakdown` carves into stories;
- the optional sections (`Users / personas`, `Constraints & cross-cutting`,
  `Success signals`, `Open questions`) where they add value — omit any that don't.

Keep capabilities **user-observable and testable** with no implementation detail
("a signed-in user can reset their password by email", not "add an auth service").
Keep each atomic — if a bullet hides two capabilities behind an "and", split it, so
breakdown's stories and the eventual `REQ-N` come out clean.

## When done

Print the PRD summary — the problem, the goal, and the capability list — and the
**suggested next step**. Then **stop**. Tell the user the next steps, which you do
**not** perform:

1. Run `tiny-spec-breakdown` to carve `PRD.md` into Features → Stories
   (`BREAKDOWN.md`) — it reads this PRD as its anchor.
2. Then run the normal flow per story (`tiny-spec-create` → `plan` → `tasks` →
   `build`).

Do **not** carve stories, scaffold `.spec/`, write a constitution, or invoke
`tiny-spec-breakdown` yourself — `prd` ends here.
