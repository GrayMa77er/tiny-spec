"""Derive where a tiny-spec backlog stands — from git and the artifacts, nothing else.

The suite has no state file by design, so neither does this: every call re-reads
git and the `.spec/` artifacts and returns one JSON-able dict. Both viewers consume it —
``tiny-spec view`` (the local HTML page) and the plugin's mod (which runs this file
directly with ``python3 tiny_spec/state.py``), so it must stay stdlib-only, importable
on Python 3.9, and free of package-relative imports.

The per-feature ladder below is a port of tiny-spec-run's "Where each feature stands —
derive, don't record" (tiny-spec-run/SKILL.md, Step 1). If you change one, change both.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Terminal-state vocabulary shared with the skills, plus the in-flight states a viewer
# needs that the router never has to name.
#   merged      built and merged into the integration branch
#   built       every task ticked, branch not merged yet
#   review      a PR is open for it (PR landing) — awaiting the user's merge
#   building    PLAN.md has tasks, some still [ ]
#   paused      the next [ ] task carries pause:
#   blocked / exhausted / fork   a halt recorded in decisions.md
#   planning    branch exists, PLAN.md missing or has no tasks
#   not-started nothing on any ref
STATES = (
    "merged", "built", "review", "building", "paused",
    "blocked", "exhausted", "fork", "planning", "not-started",
)

_FEATURE_RE = re.compile(r"^##\s+Feature:\s*(?P<title>.+?)\s+slug:\s*(?P<slug>[^\s(]+)")
_TASK_RE = re.compile(r"^- \[(?P<mark>[ xX])\]\s+(?P<id>T\d+)\s*[—–-]+\s*(?P<title>.*)$")
_FIELD_RE = re.compile(r"^\s+-\s+(?P<key>[a-z]+):\s*(?P<value>.*)$")
_REQ_RE = re.compile(r"^-\s+(?P<id>REQ-\d+)\s*[—–:-]+\s*(?P<text>.*)$")
_DECISION_RE = re.compile(r"^##\s+(?P<id>D-\d+)\s*[—–-]+\s*(?P<title>.*)$")
_COMMENT_RE = re.compile(r"<!--.*?-->")
_SEP = "\x1f"


def _git(root: Path, *args: str, timeout: int = 15) -> tuple[bool, str]:
    try:
        out = subprocess.run(
            ["git", *args], cwd=root, capture_output=True, text=True, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    return out.returncode == 0, out.stdout


def _show(root: Path, ref: str, path: str) -> str | None:
    ok, text = _git(root, "show", f"{ref}:{path}")
    return text if ok else None


def _ref_exists(root: Path, ref: str) -> bool:
    return _git(root, "rev-parse", "--verify", "--quiet", ref)[0]


def _strip(value: str) -> str:
    return _COMMENT_RE.sub("", value).strip()


# ---------------------------------------------------------------- artifact parsers


def parse_breakdown(text: str) -> tuple[list[dict], list[str]]:
    """``## Feature:`` blocks → features, plus any format problems found."""
    features: list[dict] = []
    problems: list[str] = []
    current: dict | None = None
    for line in text.splitlines():
        match = _FEATURE_RE.match(line)
        if match:
            current = {
                "title": match["title"].strip(),
                "slug": match["slug"].strip(),
                "acs": [],
                "needs": [],
                "design": [],
            }
            features.append(current)
            continue
        if line.startswith("## "):
            current = None
            continue
        if current is None:
            continue
        stripped = line.strip()
        if stripped.startswith("- Story:"):
            problems.append(
                "BREAKDOWN.md is the pre-2.0 format (- Story: lines); "
                "regenerate it with tiny-spec-scope"
            )
        elif stripped.startswith("- AC:"):
            current["acs"].append(_strip(stripped[5:]))
        elif stripped.startswith("- needs:"):
            current["needs"] = [s for s in re.split(r"[,\s]+", _strip(stripped[8:])) if s]
        elif stripped.startswith("- design:"):
            current["design"] = [s for s in re.split(r"[,\s]+", _strip(stripped[9:])) if s]
    return features, sorted(set(problems))


def _frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields = {}
    for line in text[3:end].splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def _section(text: str, heading: str) -> list[str]:
    """Lines under ``## <heading>`` up to the next ``## `` heading."""
    lines = text.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].strip().lower().startswith(heading.lower())
            continue
        if inside:
            out.append(line)
    return out


def parse_plan(text: str) -> dict:
    """PLAN.md → status plus the ``## Tasks`` checklist."""
    tasks: list[dict] = []
    current: dict | None = None
    for line in _section(text, "Tasks"):
        match = _TASK_RE.match(line)
        if match:
            current = {
                "id": match["id"],
                "title": match["title"].strip(),
                "done": match["mark"] != " ",
                "acceptance": "",
                "type": "",
                "req": [],
                "design": "",
                "pause": "",
            }
            tasks.append(current)
            continue
        field = _FIELD_RE.match(line)
        if field and current is not None:
            key, value = field["key"], field["value"].split("  #", 1)[0].strip()
            if key == "req":
                current["req"] = re.findall(r"REQ-\d+", value)
            elif key in current and key != "done":
                current[key] = value
    return {"status": _frontmatter(text).get("status", ""), "tasks": tasks}


def parse_spec(text: str) -> dict:
    reqs = []
    for line in _section(text, "Requirements"):
        match = _REQ_RE.match(line.strip())
        if match:
            reqs.append({"id": match["id"], "text": match["text"].strip()})
    title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), "")
    fm = _frontmatter(text)
    return {"title": title, "status": fm.get("status", ""), "ticket": fm.get("ticket", ""), "reqs": reqs}


def parse_decisions(text: str) -> list[dict]:
    entries: list[dict] = []
    current: dict | None = None
    for line in text.splitlines():
        match = _DECISION_RE.match(line)
        if match:
            current = {"id": match["id"], "title": match["title"].strip()}
            entries.append(current)
            continue
        if current is not None and line.startswith("- ") and ":" in line:
            key, _, value = line[2:].partition(":")
            current[key.strip()] = value.strip()
    return entries


def parse_constitution(text: str) -> dict:
    headings = [l[3:].strip() for l in text.splitlines() if l.startswith("## ")]
    verification = [
        l.strip()[2:].strip()
        for l in _section(text, "Verification")
        if l.strip().startswith("- ")
    ]
    return {"headings": headings, "verification": verification}


# ---------------------------------------------------------------- graph


def batches(features: list[dict], done: set[str]) -> tuple[dict[str, int], list[str]]:
    """Router batching: level 0 = unbuilt features whose needs are empty or merged."""
    slugs = {f["slug"] for f in features}
    problems = []
    for f in features:
        for need in f["needs"]:
            if need not in slugs:
                problems.append(f"{f['slug']} needs '{need}', which is not in the list")
    level: dict[str, int] = {}
    remaining = [f for f in features if f["slug"] not in done]
    satisfied = set(done)
    n = 0
    while remaining:
        ready = [f for f in remaining if all(x in satisfied or x not in slugs for x in f["needs"])]
        if not ready:
            cycle = ", ".join(f["slug"] for f in remaining)
            problems.append(f"needs: cycle among {cycle}")
            break
        for f in ready:
            level[f["slug"]] = n
        satisfied |= {f["slug"] for f in ready}
        remaining = [f for f in remaining if f["slug"] not in satisfied]
        n += 1
    return level, problems


def depth(features: list[dict]) -> dict[str, int]:
    """Structural depth of every feature in the needs: graph (for drawing it)."""
    by_slug = {f["slug"]: f for f in features}
    memo: dict[str, int] = {}

    def visit(slug: str, stack: tuple) -> int:
        if slug in memo:
            return memo[slug]
        if slug in stack or slug not in by_slug:
            return 0
        needs = by_slug[slug]["needs"]
        d = 0 if not needs else 1 + max(visit(n, stack + (slug,)) for n in needs)
        memo[slug] = d
        return d

    return {f["slug"]: visit(f["slug"], ()) for f in features}


# ---------------------------------------------------------------- git facts


def _worktrees(root: Path) -> list[dict]:
    ok, text = _git(root, "worktree", "list", "--porcelain")
    if not ok:
        return []
    out, cur = [], {}
    for line in text.splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
            cur = {}
        elif line.startswith("worktree "):
            cur["path"] = line[9:]
        elif line.startswith("branch "):
            cur["branch"] = line[7:].replace("refs/heads/", "", 1)
        elif line.startswith("HEAD "):
            cur["head"] = line[5:][:7]
    return out


def _commits(root: Path, rev_range: str) -> list[dict]:
    ok, text = _git(root, "log", f"--format=%h{_SEP}%s{_SEP}%cI", rev_range)
    if not ok:
        return []
    out = []
    for line in text.splitlines():
        parts = line.split(_SEP)
        if len(parts) == 3:
            out.append({"sha": parts[0], "subject": parts[1], "time": parts[2]})
    return out


def _merge_commit(root: Path, integration: str, slug: str) -> dict | None:
    ok, text = _git(
        root, "log", "--merges", "--fixed-strings", f"--grep={slug}",
        f"--format=%H{_SEP}%s{_SEP}%cI", integration,
    )
    if not ok:
        return None
    for line in text.splitlines():
        sha, subject, when = (line.split(_SEP) + ["", ""])[:3]
        if subject.endswith(f"'{slug}'") or subject.endswith(f"/{slug}") or subject.endswith(f" {slug}"):
            return {"sha": sha, "subject": subject, "time": when}
    return None


def _remote_prs(root: Path) -> dict:
    result = {"enabled": True, "ok": False, "error": "", "prs": {}}
    ok, err = _git(root, "fetch", "--quiet", "--prune", "origin", timeout=30)
    if not ok:
        result["error"] = f"git fetch failed: {err.strip() or 'no origin?'}"
        return result
    try:
        out = subprocess.run(
            ["gh", "pr", "list", "--state", "all", "--limit", "200", "--json",
             "number,headRefName,state,isDraft,url,title,mergedAt,body"],
            cwd=root, capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        result["error"] = f"gh unavailable: {exc}"
        return result
    if out.returncode != 0:
        result["error"] = out.stderr.strip() or "gh pr list failed"
        return result
    try:
        listed = json.loads(out.stdout or "[]")
    except ValueError as exc:
        result["error"] = f"gh pr list returned unreadable JSON: {exc}"
        return result
    prs: dict[str, dict] = {}
    for pr in listed:
        # gh lists newest first; keep the newest PR per branch.
        head = pr.get("headRefName", "")
        if head and head not in prs:
            body = pr.pop("body", "") or ""
            pr["has_lessons"] = "## Lessons" in body
            prs[head] = pr
    result.update(ok=True, prs=prs)
    return result


# ---------------------------------------------------------------- derive


def derive(root: Path, remote: bool = False) -> dict:
    root = root.resolve()
    state: dict = {
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(root),
        "problems": [],
        "features": [],
        "batches": [],
        "worktrees": [],
        "cleanup": [],
        "remote": {"enabled": False, "ok": False, "error": "", "prs": {}},
    }
    if not _git(root, "rev-parse", "--is-inside-work-tree")[0]:
        state["problems"].append("not a git repository")
        return state

    integration = "main" if _ref_exists(root, "main") else ("master" if _ref_exists(root, "master") else "")
    state["integration"] = integration
    state["branch"] = _git(root, "rev-parse", "--abbrev-ref", "HEAD")[1].strip()
    state["dirty"] = bool(_git(root, "status", "--porcelain")[1].strip())
    if not integration:
        state["problems"].append("no main or master branch")

    if remote:
        state["remote"] = _remote_prs(root)
    prs = state["remote"]["prs"]

    constitution = root / ".spec" / "constitution.md"
    state["constitution"] = (
        {"exists": True, **parse_constitution(constitution.read_text())}
        if constitution.is_file() else {"exists": False, "headings": [], "verification": []}
    )
    memory = root / ".spec" / "memory.md"
    state["memory_entries"] = (
        sum(1 for l in memory.read_text().splitlines() if l.startswith("- type:"))
        if memory.is_file() else 0
    )

    # Feature list: BREAKDOWN.md (working tree, else integration), else the ticket dirs.
    breakdown = root / "BREAKDOWN.md"
    text = breakdown.read_text() if breakdown.is_file() else (
        _show(root, integration, "BREAKDOWN.md") if integration else None
    )
    if text is not None:
        features, problems = parse_breakdown(text)
        state["source"] = "BREAKDOWN.md"
        state["problems"] += problems
    else:
        spec_dir = root / ".spec"
        features = [
            {"title": d.name, "slug": d.name, "acs": [], "needs": [], "design": []}
            for d in sorted(spec_dir.iterdir()) if (d / "SPEC.md").is_file()
        ] if spec_dir.is_dir() else []
        state["source"] = ".spec/ ticket dirs"

    worktrees = _worktrees(root)
    state["worktrees"] = worktrees
    by_branch = {w.get("branch"): w for w in worktrees if w.get("branch")}

    merged: set[str] = set()
    for f in features:
        slug = f["slug"]
        plan_path = f".spec/{slug}/PLAN.md"
        f.update(state="not-started", ref="", tasks=[], reqs=[], halts=[], commits=[],
                 merge=None, pr=prs.get(slug), worktree=by_branch.get(slug, {}).get("path"))

        # Router ladder, rule 1: integration has the feature, every task ticked.
        main_plan = _show(root, integration, plan_path) if integration else None
        if main_plan is not None:
            plan = parse_plan(main_plan)
            if plan["tasks"] and all(t["done"] for t in plan["tasks"]):
                f.update(state="merged", ref=integration, tasks=plan["tasks"])
                f["merge"] = _merge_commit(root, integration, slug)
                if f["merge"]:
                    f["commits"] = _commits(root, f"{f['merge']['sha']}^1..{f['merge']['sha']}^2")
                merged.add(slug)
        if f["state"] != "merged":
            # Rule 2: the feature branch — local first, then origin (cloud threads).
            ref = slug if _ref_exists(root, slug) else (
                f"origin/{slug}" if _ref_exists(root, f"origin/{slug}") else ""
            )
            if ref:
                f["ref"] = ref
                f["commits"] = _commits(root, f"{integration}..{ref}") if integration else []
                text = _show(root, ref, plan_path)
                plan = parse_plan(text) if text else {"tasks": []}
                f["tasks"] = plan["tasks"]
                if not plan["tasks"]:
                    f["state"] = "planning"
                elif all(t["done"] for t in plan["tasks"]):
                    f["state"] = "built"
                else:
                    f["state"] = "building"
                    nxt = next(t for t in plan["tasks"] if not t["done"])
                    if nxt["pause"]:
                        f["state"] = "paused"
                # A halt recorded by tiny-spec-build wins over "building".
                if f["state"] in ("building", "paused"):
                    dec = _show(root, ref, f".spec/{slug}/decisions.md")
                    halts = [
                        d for d in parse_decisions(dec or "")
                        if d.get("type") in ("blocker", "halt")
                    ]
                    f["halts"] = halts
                    # Only a halt naming the task the loop is stuck on is live; one
                    # resolved upstream, after which the build moved on, is history.
                    last = halts[-1] if halts else {}
                    affects = re.findall(r"T\d+", last.get("affects", ""))
                    if last.get("state") in ("blocked", "exhausted", "fork") and (
                        not affects or nxt["id"] in affects
                    ):
                        f["state"] = last["state"]
            pr = f["pr"]
            if pr and pr.get("state") == "OPEN" and f["state"] in ("built", "building", "planning"):
                f["state"] = "review" if not pr.get("isDraft") else f["state"]

        spec_text = _show(root, f["ref"], f".spec/{slug}/SPEC.md") if f["ref"] else None
        if spec_text is None and (root / ".spec" / slug / "SPEC.md").is_file():
            spec_text = (root / ".spec" / slug / "SPEC.md").read_text()
        if spec_text:
            spec = parse_spec(spec_text)
            f["reqs"] = spec["reqs"]
            f["ticket"] = spec["ticket"]
        covered = {r for t in f["tasks"] for r in t["req"]}
        f["uncovered"] = [r["id"] for r in f["reqs"] if r["id"] not in covered] if f["tasks"] else []
        f["done_count"] = sum(1 for t in f["tasks"] if t["done"])
        f["total"] = len(f["tasks"])
        f["current_task"] = next((t for t in f["tasks"] if not t["done"]), None)
        times = [c["time"] for c in f["commits"]]
        f["started"] = min(times) if times else None
        f["last_activity"] = max(times) if times else None

    level, problems = batches(features, merged)
    state["problems"] += problems
    dep = depth(features)
    for f in features:
        f["batch"] = level.get(f["slug"])
        f["depth"] = dep.get(f["slug"], 0)
    n_batches = max(level.values()) + 1 if level else 0
    state["batches"] = [[f["slug"] for f in features if f["batch"] == i] for i in range(n_batches)]
    state["features"] = features

    # Worktrees whose feature is merged: print the removal command; never run it.
    state["cleanup"] = [
        {"slug": f["slug"], "path": f["worktree"], "command": f"git worktree remove {f['worktree']}"}
        for f in features if f["state"] == "merged" and f["worktree"]
    ]
    counts: dict[str, int] = {}
    for f in features:
        counts[f["state"]] = counts.get(f["state"], 0) + 1
    state["counts"] = counts
    return state


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print where a tiny-spec backlog stands, as JSON.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root (default: cwd)")
    parser.add_argument("--remote", action="store_true", help="git fetch + gh pr list (cloud/PR runs)")
    parser.add_argument("--pretty", action="store_true", help="indent the JSON")
    args = parser.parse_args(argv)
    json.dump(derive(args.root, remote=args.remote), sys.stdout, indent=2 if args.pretty else None)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
