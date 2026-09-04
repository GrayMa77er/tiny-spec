#!/usr/bin/env python3
"""Grade one planning-stage run: the BREAKDOWN.md produced by tiny-spec-scope
for a single idea.

Two layers, mirroring the suite's own measured-vs-judgment split:

  STRUCTURAL (deterministic)  — does the artifact conform to the contract?
      BREAKDOWN.md has its required sections filled (Problem, Goal & non-goals),
      a Decisions block, ≥1 Feature, and Stories that each carry a slug and ≥1 AC;
      no .spec/ was scaffolded by the planning skill.

  JUDGE (LLM, via the `claude` CLI)  — the things structure can't see:
      coverage     every capability the IDEA implies lands in ≥1 story (nothing dropped)
      fabrication  every story traces back to the IDEA (nothing invented)
      atomicity    ACs are atomic, user-observable, no impl detail
      faithfulness the breakdown honestly reflects the IDEA

Usage (standalone — grade an existing artifact):
    grade_planning.py <case_name> <artifact_dir> <case_dir>
  where <artifact_dir> holds BREAKDOWN.md (and must NOT hold .spec/),
  and <case_dir> holds IDEA.md. Prints one result JSON object to stdout.

Env:
    JUDGE_MODEL    optional --model for the judge claude call
    NO_JUDGE=1     skip the LLM judge (structural only) — for offline debugging
"""
import json, os, re, subprocess, sys

REQUIRED_BREAKDOWN_SECTIONS = ["Problem", "Goal & non-goals"]


def _read(path):
    return open(path, encoding="utf-8").read() if os.path.exists(path) else ""


def _strip_comments(text):
    """Drop HTML comment blocks so template scaffolding doesn't count as content."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _section(body, heading):
    """Return the lines under `## <heading>` up to the next `## ` heading."""
    lines = body.splitlines()
    out, capturing = [], False
    for ln in lines:
        if ln.strip().startswith("## "):
            capturing = ln.strip()[3:].strip().lower() == heading.strip().lower()
            continue
        if capturing:
            out.append(ln)
    return "\n".join(out)


def _has_content(section_text):
    """A section counts as filled if it has a non-blank line that isn't a bare
    <placeholder> token."""
    for ln in section_text.splitlines():
        s = ln.strip().lstrip("-").strip()
        if not s:
            continue
        if s.startswith("<") and s.endswith(">"):  # untouched <placeholder>
            continue
        return True
    return False


def _bullets(section_text):
    out = []
    for ln in section_text.splitlines():
        s = ln.strip()
        if s.startswith("- "):
            val = s[2:].strip()
            if val and not (val.startswith("<") and val.endswith(">")):
                out.append(val)
    return out


def structural(artifact_dir):
    bd_raw = _read(os.path.join(artifact_dir, "BREAKDOWN.md"))
    bd = _strip_comments(bd_raw)
    findings = []

    bd_produced = bool(bd_raw.strip())
    no_spec_dir = not os.path.isdir(os.path.join(artifact_dir, ".spec"))
    if not no_spec_dir:
        findings.append("planning skill scaffolded a .spec/ dir (it must not)")

    # BREAKDOWN required framing sections present + filled
    bd_sections_ok = True
    for h in REQUIRED_BREAKDOWN_SECTIONS:
        if not _has_content(_section(bd, h)):
            bd_sections_ok = False
            findings.append(f"BREAKDOWN missing/empty required section: {h}")

    # BREAKDOWN shape
    bd_ok = True
    if "## Decisions" not in bd:
        bd_ok = False; findings.append("BREAKDOWN missing ## Decisions block")
    if not re.search(r"(?m)^##\s+Feature:", bd):
        bd_ok = False; findings.append("BREAKDOWN has no ## Feature: heading")
    stories = re.findall(r"(?m)^-\s*Story:\s*(.+)$", bd)
    if not stories:
        bd_ok = False; findings.append("BREAKDOWN has no - Story: entries")
    stories_missing_slug = [s for s in stories if "slug:" not in s]
    if stories_missing_slug:
        bd_ok = False
        findings.append(f"{len(stories_missing_slug)} story line(s) missing a slug:")
    if not re.search(r"(?m)^\s*-\s*AC:", bd):
        bd_ok = False; findings.append("BREAKDOWN has no - AC: lines")

    ok = bd_produced and no_spec_dir and bd_sections_ok and bd_ok
    return {
        "structural_ok": ok,
        "breakdown_produced": bd_produced,
        "no_spec_dir": no_spec_dir,
        "breakdown_sections_ok": bd_sections_ok,
        "breakdown_shape_ok": bd_ok,
        "n_stories": len(stories),
        "findings": findings,
    }, bd_raw


JUDGE_PROMPT = """You are grading the hand-off quality of a planning stage. An IDEA \
was expanded directly into a BREAKDOWN (Problem, Goal & non-goals, a Decisions block, \
then Features → Stories with acceptance criteria). Judge ONLY what is present; do not \
rewrite anything.

Return ONLY a JSON object (no prose, no code fences) with exactly these keys:
{
  "breakdown_faithful_to_idea": true|false,
  "coverage_ok": true|false,            // every capability the IDEA calls for appears in >=1 story
  "dropped_capabilities": [string],     // IDEA capabilities with no corresponding story (empty if none)
  "no_fabrication": true|false,         // every story traces back to the IDEA
  "invented_stories": [string],         // story titles with no basis in the IDEA (empty if none)
  "atomicity_ok": true|false,           // ACs are atomic, user-observable, no implementation detail
  "atomicity_violations": [string],     // offending lines (empty if none)
  "cross_cutting_placement_ok": true|false, // cross-cutting concerns are in Decisions/invariants, not their own Feature
  "verdict": "PASS"|"FAIL",             // PASS only if coverage_ok AND no_fabrication AND atomicity_ok
  "notes": string                       // 1-3 sentences, the single most important observation
}

Note: a breakdown may legitimately add a capability the IDEA did not literally name, \
if it is required to make the product coherent — count that as fabrication ONLY if it \
expands scope beyond what the IDEA asks for.

=== IDEA ===
{idea}

=== BREAKDOWN.md ===
{breakdown}
"""


def _extract_json(text):
    start, depth = text.find("{"), 0
    if start < 0:
        return None
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def judge(idea, breakdown):
    if os.environ.get("NO_JUDGE") == "1":
        return {"judge_ran": False, "notes": "judge skipped (NO_JUDGE=1)"}
    prompt = (JUDGE_PROMPT
              .replace("{idea}", idea.strip())
              .replace("{breakdown}", breakdown.strip()))
    cmd = ["claude", "-p", prompt, "--dangerously-skip-permissions"]
    model = os.environ.get("JUDGE_MODEL")
    if model:
        cmd += ["--model", model]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except Exception as e:  # noqa: BLE001 — infra failure, report don't crash
        return {"judge_ran": False, "notes": f"judge call failed: {e}"}
    parsed = _extract_json(out.stdout)
    if parsed is None:
        return {"judge_ran": False, "notes": "judge returned unparseable output",
                "raw": out.stdout[:500]}
    parsed["judge_ran"] = True
    return parsed


def main():
    if len(sys.argv) < 4:
        print("usage: grade_planning.py <case_name> <artifact_dir> <case_dir>", file=sys.stderr)
        sys.exit(2)
    case, artifact_dir, case_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    struct, bd_raw = structural(artifact_dir)
    idea = _read(os.path.join(case_dir, "IDEA.md"))
    j = judge(idea, bd_raw) if struct["breakdown_produced"] else \
        {"judge_ran": False, "notes": "skipped judge (artifact missing)"}

    # case PASS = structural conformance AND the judge's hand-off integrity core.
    judge_core = bool(j.get("coverage_ok")) and bool(j.get("no_fabrication"))
    case_pass = bool(struct["structural_ok"]) and j.get("judge_ran", False) and judge_core

    result = {
        "case": case,
        "pass": case_pass,
        **{k: struct[k] for k in struct},
        "judge_ran": j.get("judge_ran", False),
        "breakdown_faithful_to_idea": j.get("breakdown_faithful_to_idea"),
        "coverage_ok": j.get("coverage_ok"),
        "dropped_capabilities": j.get("dropped_capabilities", []),
        "no_fabrication": j.get("no_fabrication"),
        "invented_stories": j.get("invented_stories", []),
        "atomicity_ok": j.get("atomicity_ok"),
        "atomicity_violations": j.get("atomicity_violations", []),
        "cross_cutting_placement_ok": j.get("cross_cutting_placement_ok"),
        "judge_verdict": j.get("verdict"),
        "notes": j.get("notes", ""),
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
