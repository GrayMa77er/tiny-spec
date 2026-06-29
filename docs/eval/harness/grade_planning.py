#!/usr/bin/env python3
"""Grade one planning-stage run: the PRD.md + BREAKDOWN.md produced by
tiny-spec-prd → tiny-spec-breakdown for a single idea.

Two layers, mirroring the suite's own measured-vs-judgment split:

  STRUCTURAL (deterministic)  — do the artifacts conform to the contract?
      PRD.md has its required sections filled; BREAKDOWN.md has a Decisions block,
      ≥1 Feature, and Stories that each carry a slug and ≥1 AC; no .spec/ was
      scaffolded by the planning skills.

  JUDGE (LLM, via the `claude` CLI)  — the things structure can't see:
      coverage     every PRD capability lands in ≥1 BREAKDOWN story (nothing dropped)
      fabrication  every BREAKDOWN story traces to a PRD capability (nothing invented)
      atomicity    capabilities/ACs are atomic, user-observable, no impl detail
      faithfulness the PRD honestly reflects the IDEA

Usage (standalone — grade an existing pair):
    grade_planning.py <case_name> <artifact_dir> <case_dir>
  where <artifact_dir> holds PRD.md + BREAKDOWN.md (and must NOT hold .spec/),
  and <case_dir> holds IDEA.md. Prints one result JSON object to stdout.

Env:
    JUDGE_MODEL    optional --model for the judge claude call
    NO_JUDGE=1     skip the LLM judge (structural only) — for offline debugging
"""
import json, os, re, subprocess, sys

REQUIRED_PRD_SECTIONS = ["Problem / context", "Goal & non-goals", "Core capabilities"]


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
    prd_raw, bd_raw = _read(os.path.join(artifact_dir, "PRD.md")), _read(os.path.join(artifact_dir, "BREAKDOWN.md"))
    prd, bd = _strip_comments(prd_raw), _strip_comments(bd_raw)
    findings = []

    prd_produced = bool(prd_raw.strip())
    bd_produced = bool(bd_raw.strip())
    no_spec_dir = not os.path.isdir(os.path.join(artifact_dir, ".spec"))
    if not no_spec_dir:
        findings.append("planning skills scaffolded a .spec/ dir (they must not)")

    # PRD required sections present + filled
    prd_sections_ok = True
    for h in REQUIRED_PRD_SECTIONS:
        if not _has_content(_section(prd, h)):
            prd_sections_ok = False
            findings.append(f"PRD missing/empty required section: {h}")
    capabilities = _bullets(_section(prd, "Core capabilities"))
    if len(capabilities) < 2:
        prd_sections_ok = False
        findings.append(f"PRD Core capabilities has <2 bullets ({len(capabilities)})")

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

    ok = prd_produced and bd_produced and no_spec_dir and prd_sections_ok and bd_ok
    return {
        "structural_ok": ok,
        "prd_produced": prd_produced,
        "breakdown_produced": bd_produced,
        "no_spec_dir": no_spec_dir,
        "prd_sections_ok": prd_sections_ok,
        "breakdown_shape_ok": bd_ok,
        "n_capabilities": len(capabilities),
        "n_stories": len(stories),
        "findings": findings,
    }, prd_raw, bd_raw


JUDGE_PROMPT = """You are grading the hand-off quality of a two-step planning stage. \
An IDEA was expanded into a PRD (PRD.md), whose "Core capabilities" were then carved \
into a BREAKDOWN (Features → Stories with acceptance criteria). Judge ONLY what is \
present; do not rewrite anything.

Return ONLY a JSON object (no prose, no code fences) with exactly these keys:
{
  "prd_faithful_to_idea": true|false,
  "coverage_ok": true|false,            // every PRD core capability appears in >=1 BREAKDOWN story
  "dropped_capabilities": [string],     // PRD capabilities with no corresponding story (empty if none)
  "no_fabrication": true|false,         // every BREAKDOWN story traces to a PRD capability
  "invented_stories": [string],         // story titles with no basis in the PRD (empty if none)
  "atomicity_ok": true|false,           // capabilities & ACs are atomic, user-observable, no implementation detail
  "atomicity_violations": [string],     // offending lines (empty if none)
  "cross_cutting_placement_ok": true|false, // cross-cutting concerns are in Decisions/invariants, not their own Feature
  "verdict": "PASS"|"FAIL",             // PASS only if coverage_ok AND no_fabrication AND atomicity_ok
  "notes": string                       // 1-3 sentences, the single most important observation
}

=== IDEA ===
{idea}

=== PRD.md ===
{prd}

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


def judge(idea, prd, breakdown):
    if os.environ.get("NO_JUDGE") == "1":
        return {"judge_ran": False, "notes": "judge skipped (NO_JUDGE=1)"}
    prompt = (JUDGE_PROMPT
              .replace("{idea}", idea.strip())
              .replace("{prd}", prd.strip())
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
    struct, prd_raw, bd_raw = structural(artifact_dir)
    idea = _read(os.path.join(case_dir, "IDEA.md"))
    j = judge(idea, prd_raw, bd_raw) if struct["prd_produced"] and struct["breakdown_produced"] else \
        {"judge_ran": False, "notes": "skipped judge (artifacts missing)"}

    # case PASS = structural conformance AND the judge's hand-off integrity core.
    judge_core = bool(j.get("coverage_ok")) and bool(j.get("no_fabrication"))
    case_pass = bool(struct["structural_ok"]) and j.get("judge_ran", False) and judge_core

    result = {
        "case": case,
        "pass": case_pass,
        **{k: struct[k] for k in struct},
        "judge_ran": j.get("judge_ran", False),
        "prd_faithful_to_idea": j.get("prd_faithful_to_idea"),
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
