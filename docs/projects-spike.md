# Spike: tiny-spec inside a Claude Code Project

Phase 0 of the Projects integration. Nothing in the skills changes until this is
filled in: the answers decide whether `tiny-spec-run` can start Project threads itself,
or whether threads stay a documented manual recipe.

**Setup.** A scratch GitHub repo with a 3-feature `BREAKDOWN.md` (two independent, one
`needs:` the first) and a `.spec/constitution.md` whose Verification command really runs.
Create a Project on it. Add the `tiny-spec` plugin
(`/plugin marketplace add GrayMa77er/tiny-spec`) to the Project's plugins.

Fill in each answer with what you saw, not what the docs say.

## 1. Can a skill start a thread?

Ask the coordinator: *"list the tools you have for creating or messaging threads, with
their exact names and parameters."* Then run `/tiny-spec:tiny-spec-run build the backlog`
and watch what it does at Step 4.

- Tool name(s) and parameters:
- Can the coordinator be *told* "start a thread on branch X with brief Y"? Yes/no:
- Does a thread start on a branch you name, or always on a fresh one?
- Signal a skill could use to detect it's running as a coordinator:

## 2. Human gates in the coordinator chat

- Does `AskUserQuestion` render in the coordinator chat?
- Do plan mode / `EnterPlanMode` / `ExitPlanMode` exist there?

## 3. Plugin inside threads

- Are `tiny-spec:*` skills and the two agents visible inside a thread?
- Can a thread dispatch `tiny-spec:tiny-spec-build-executor` as a subagent?
- Does a thread have `gh`, push rights, and permission to open a PR?

## 4. Branch hand-off

The coordinator commits SPEC/PLAN on `<slug>` and pushes. Does a thread started
afterwards see that branch and those files?

## 5. Limits and cost

- How many threads ran concurrently before queuing?
- Usage per thread for one small feature (from the Project's usage view):

## 6. Watching it from your laptop

With `uvx tiny-spec view` open on a local clone and *watch PRs* ticked: did each
thread's branch and PR show up, with the right state?

## Verdict

- [ ] Auto-detect + thread lanes (Phase 2 as planned)
- [ ] Manual recipe only: document "one thread per feature, paste this brief"
