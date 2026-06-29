#!/usr/bin/env bash
# Planning-stage eval harness for tiny-spec — runs the planning on-ramps on loose
# ideas and grades the produced PRD.md + BREAKDOWN.md.
#
# For each planning case it: spins up a hermetic sandbox, vendors the repo's
# tiny-spec skills+agents into the sandbox's local .claude/, hands the sandbox an
# IDEA.md, drives tiny-spec-prd → tiny-spec-breakdown headlessly with `claude -p`,
# then grades the artifacts with grade_planning.py (deterministic structural checks
# + an LLM judge for coverage / no-fabrication / atomicity). Results are aggregated
# by score_planning.py into docs/eval/planning-results.jsonl.
#
# Usage:
#   docs/eval/harness/run-planning.sh                # all planning cases
#   docs/eval/harness/run-planning.sh snip           # a subset
# Env:
#   CLAUDE_MODEL   optional --model for the generation run
#   JUDGE_MODEL    optional --model for the judge (defaults to CLI default)
#   TASK_TIMEOUT   seconds per case (default 600; needs coreutils `timeout`)
#   KEEP_SANDBOX=1 keep sandboxes for debugging (default: removed)
set -uo pipefail

REPO="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
EVAL_DIR="$REPO/docs/eval"
PLAN_DIR="$EVAL_DIR/planning"
HARNESS="$EVAL_DIR/harness"
SHA="$(git -C "$REPO" rev-parse --short HEAD)"
DATE="$(date +%Y-%m-%d)"
TASK_TIMEOUT="${TASK_TIMEOUT:-600}"

if [ "$#" -gt 0 ]; then
  CASES=("$@")
else
  CASES=(); for d in "$PLAN_DIR"/*/; do CASES+=("$(basename "$d")"); done
fi

command -v claude >/dev/null || { echo "FATAL: claude CLI not on PATH"; exit 1; }
TIMEOUT_BIN=""; command -v timeout >/dev/null && TIMEOUT_BIN="timeout ${TASK_TIMEOUT}"
command -v gtimeout >/dev/null && TIMEOUT_BIN="gtimeout ${TASK_TIMEOUT}"

RESULTS_JSONL="$(mktemp)"
LOGDIR="$(mktemp -d)"
echo ">> tiny-spec planning eval  ($DATE @ $SHA)"
echo ">> cases: ${CASES[*]}"
echo ">> logs:  $LOGDIR"

DRIVER='You are in a fresh project directory. Read IDEA.md, then run the planning stage END TO END, fully autonomously — do NOT ask me anything, make reasonable decisions and proceed. Steps: (1) use the tiny-spec-prd skill to turn the idea in IDEA.md into a PRD.md at the project root; (2) use the tiny-spec-breakdown skill to carve that PRD.md into a BREAKDOWN.md at the project root. Treat the work as ad-hoc (no external tracker). Do NOT scaffold .spec/, do NOT run tiny-spec-create or any later skill, and do not stop for confirmation at any point.'

for case in "${CASES[@]}"; do
  CDIR="$PLAN_DIR/$case"
  [ -d "$CDIR" ] || { echo "  ?? unknown case: $case (skipping)"; continue; }
  SB="$(mktemp -d)"
  echo "-- $case : sandbox $SB"

  git -C "$SB" init -q
  git -C "$SB" config user.email eval@local; git -C "$SB" config user.name eval
  git -C "$SB" commit -q --allow-empty -m "init" || true
  mkdir -p "$SB/.claude/skills" "$SB/.claude/agents"
  for s in tiny-spec-prd tiny-spec-breakdown tiny-spec-create tiny-spec-plan tiny-spec-tasks tiny-spec-build; do
    [ -d "$REPO/$s" ] && cp -R "$REPO/$s" "$SB/.claude/skills/$s"
  done
  cp "$REPO/agents/"*.md "$SB/.claude/agents/" 2>/dev/null || true
  cp "$CDIR/IDEA.md" "$SB/IDEA.md"

  MODEL_ARG=(); [ -n "${CLAUDE_MODEL:-}" ] && MODEL_ARG=(--model "$CLAUDE_MODEL")
  ( cd "$SB" && $TIMEOUT_BIN claude -p "$DRIVER" \
      --dangerously-skip-permissions ${MODEL_ARG[@]+"${MODEL_ARG[@]}"} ) \
      >"$LOGDIR/$case.log" 2>&1
  RUN_RC=$?
  [ $RUN_RC -ne 0 ] && echo "   (claude exited rc=$RUN_RC; see $LOGDIR/$case.log)"

  # grade: structural + LLM judge -> one result object
  GRADE="$(python3 "$HARNESS/grade_planning.py" "$case" "$SB" "$CDIR" 2>>"$LOGDIR/$case.log")"
  if [ -n "$GRADE" ]; then
    echo "$GRADE" >>"$RESULTS_JSONL"
    echo "   $(printf '%s' "$GRADE" | python3 -c 'import json,sys; r=json.load(sys.stdin); print(("PASS" if r["pass"] else "FAIL"), "- struct", r["structural_ok"], "cov", r.get("coverage_ok"), "nofab", r.get("no_fabrication"))')"
  else
    echo "   (grader produced no output; see $LOGDIR/$case.log)"
  fi

  if [ "${KEEP_SANDBOX:-0}" = "1" ]; then echo "   kept: $SB"; else rm -rf "$SB"; fi
done

RESULTS_JSON="$(mktemp)"
python3 -c "import json,sys; print(json.dumps([json.loads(l) for l in open(sys.argv[1]) if l.strip()]))" "$RESULTS_JSONL" >"$RESULTS_JSON"
echo
python3 "$HARNESS/score_planning.py" "$RESULTS_JSON" --sha "$SHA" --date "$DATE"
