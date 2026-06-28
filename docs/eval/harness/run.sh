#!/usr/bin/env bash
# Empirical eval harness for tiny-spec — runs the suite on real tasks and grades
# the actual output with held-out tests.
#
# For each benchmark task it: spins up a hermetic sandbox, vendors the repo's
# tiny-spec skills+agents into the sandbox's local .claude/, hands the sandbox a
# TICKET.md, drives the full tiny-spec flow headlessly with `claude -p`, then runs
# the held-out grader and introspects the suite's own verdict. Results are scored by
# harness/score.py, which derives Dimension A and appends to docs/eval/scores.jsonl.
#
# Usage:
#   docs/eval/harness/run.sh                 # all benchmark tasks
#   docs/eval/harness/run.sh roman duration  # a subset
# Env:
#   CLAUDE_MODEL   optional --model passed to claude
#   TASK_TIMEOUT   seconds per task (default 900; needs coreutils `timeout`)
#   KEEP_SANDBOX=1 keep sandboxes for debugging (default: removed)
set -uo pipefail

REPO="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
EVAL_DIR="$REPO/docs/eval"
BM="$EVAL_DIR/benchmark"
HARNESS="$EVAL_DIR/harness"
SHA="$(git -C "$REPO" rev-parse --short HEAD)"
DATE="$(date +%Y-%m-%d)"
TASK_TIMEOUT="${TASK_TIMEOUT:-900}"

# task list
if [ "$#" -gt 0 ]; then
  TASKS=("$@")
else
  TASKS=(); for d in "$BM"/*/; do TASKS+=("$(basename "$d")"); done
fi

command -v claude >/dev/null || { echo "FATAL: claude CLI not on PATH"; exit 1; }
TIMEOUT_BIN=""; command -v timeout >/dev/null && TIMEOUT_BIN="timeout ${TASK_TIMEOUT}"
gtimeout_check() { command -v gtimeout >/dev/null && TIMEOUT_BIN="gtimeout ${TASK_TIMEOUT}"; }
[ -z "$TIMEOUT_BIN" ] && gtimeout_check

RESULTS_JSONL="$(mktemp)"
LOGDIR="$(mktemp -d)"
echo ">> tiny-spec empirical eval  ($DATE @ $SHA)"
echo ">> tasks: ${TASKS[*]}"
echo ">> logs:  $LOGDIR"

DRIVER='You are in a fresh project directory. Read TICKET.md, then implement it END TO END using the tiny-spec workflow, fully autonomously — do NOT ask me anything, make reasonable decisions and proceed. Steps: (1) use the tiny-spec-create skill for ad-hoc work (no external ticket) to capture the requirement from TICKET.md; (2) tiny-spec-plan; (3) tiny-spec-tasks; (4) tiny-spec-build, running every task straight through (run-it-through mode) until all tasks are checked or a blocker stops you. Deliver the code at the exact path the ticket specifies. Do not stop for confirmation at any point.'

for task in "${TASKS[@]}"; do
  TDIR="$BM/$task"
  [ -d "$TDIR" ] || { echo "  ?? unknown task: $task (skipping)"; continue; }
  SB="$(mktemp -d)"
  echo "-- $task : sandbox $SB"

  # hermetic sandbox: fresh git repo + vendored skills/agents
  git -C "$SB" init -q
  git -C "$SB" config user.email eval@local; git -C "$SB" config user.name eval
  git -C "$SB" commit -q --allow-empty -m "init" || true
  mkdir -p "$SB/.claude/skills" "$SB/.claude/agents"
  for s in tiny-spec-breakdown tiny-spec-create tiny-spec-plan tiny-spec-tasks tiny-spec-build; do
    [ -d "$REPO/$s" ] && cp -R "$REPO/$s" "$SB/.claude/skills/$s"
  done
  cp "$REPO/agents/"*.md "$SB/.claude/agents/" 2>/dev/null || true
  cp "$TDIR/TICKET.md" "$SB/TICKET.md"

  # drive tiny-spec headlessly
  MODEL_ARG=(); [ -n "${CLAUDE_MODEL:-}" ] && MODEL_ARG=(--model "$CLAUDE_MODEL")
  # ${arr[@]+"${arr[@]}"} expands safely when empty under `set -u` on bash 3.2 (macOS)
  ( cd "$SB" && $TIMEOUT_BIN claude -p "$DRIVER" \
      --dangerously-skip-permissions ${MODEL_ARG[@]+"${MODEL_ARG[@]}"} ) \
      >"$LOGDIR/$task.log" 2>&1
  RUN_RC=$?
  [ $RUN_RC -ne 0 ] && echo "   (claude exited rc=$RUN_RC; see $LOGDIR/$task.log)"

  # held-out grade
  if [ -f "$SB/solution.py" ]; then
    GRADE_OUT="$(SOLUTION_PATH="$SB/solution.py" python3 "$TDIR/grade/test.py" 2>&1)"
    GRADE_RC=$?
  else
    GRADE_OUT="no solution.py produced"; GRADE_RC=1
  fi
  echo "   grader: $GRADE_OUT"

  # introspect the suite's own verdict + emit one result object
  python3 - "$task" "$SB" "$GRADE_RC" "$RUN_RC" "$GRADE_OUT" >>"$RESULTS_JSONL" <<'PY'
import json, os, sys, glob, re
task, sb, grade_rc, run_rc, grade_out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
produced = os.path.exists(os.path.join(sb, "solution.py"))
tasks_files = glob.glob(os.path.join(sb, ".spec", "*", "tasks.md"))
dec_files = glob.glob(os.path.join(sb, ".spec", "*", "decisions.md"))
suite_completed = False
if tasks_files:
    txt = open(tasks_files[0]).read()
    unchecked = re.search(r'(?m)^\s*-\s*\[ \]', txt)
    checked = re.search(r'(?m)^\s*-\s*\[x\]', txt, re.I)
    suite_completed = bool(checked) and not bool(unchecked)
blocker = any("type: blocker" in open(f).read() for f in dec_files)
if blocker:
    suite_completed = False
print(json.dumps({
    "task": task,
    "produced": produced,
    "suite_completed": suite_completed,
    "blocker": blocker,
    "held_out_pass": grade_rc == 0,
    "notes": grade_out if grade_rc != 0 else "ok",
    "claude_rc": run_rc,
}))
PY

  if [ "${KEEP_SANDBOX:-0}" = "1" ]; then echo "   kept: $SB"; else rm -rf "$SB"; fi
done

# assemble JSON list and score
RESULTS_JSON="$(mktemp)"
python3 -c "import json,sys; print(json.dumps([json.loads(l) for l in open(sys.argv[1]) if l.strip()]))" "$RESULTS_JSONL" >"$RESULTS_JSON"
echo
python3 "$HARNESS/score.py" "$RESULTS_JSON" --sha "$SHA" --date "$DATE"
echo
echo ">> appended to docs/eval/results.jsonl and docs/eval/scores.jsonl"
