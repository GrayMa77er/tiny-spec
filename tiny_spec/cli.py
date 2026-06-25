"""tiny-spec installer CLI.

Two commands, stdlib only:

    tiny-spec install      copy skills + agents into ~/.claude
    tiny-spec uninstall    remove the ones tiny-spec installed

Re-running ``install`` overwrites in place, so it doubles as an update. Pass
``--dir`` to target a Claude config dir other than ``~/.claude`` (handy for
testing into a throwaway directory).

What gets installed is declared in ``manifest.json`` — the single source of
truth for the install set. Adding or renaming a skill/agent means editing the
manifest (and the matching path in ``pyproject.toml``), nothing else here.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from importlib.resources import as_file, files
from pathlib import Path


def _manifest() -> dict:
    """The declared install set: ``{"skills": [...], "agents": [...]}``."""
    return json.loads(files("tiny_spec").joinpath("manifest.json").read_text())


def _default_dir() -> Path:
    return Path.home() / ".claude"


def install(claude_dir: Path) -> int:
    """Copy the manifest's skills and agents into ``claude_dir``. Overwrites in place."""
    manifest = _manifest()
    skills_dst = claude_dir / "skills"
    agents_dst = claude_dir / "agents"
    skills_dst.mkdir(parents=True, exist_ok=True)
    agents_dst.mkdir(parents=True, exist_ok=True)

    with as_file(files("tiny_spec").joinpath("_bundle")) as bundle:
        for skill in manifest["skills"]:
            src = bundle / skill
            if not src.is_dir():
                raise SystemExit(f"manifest lists skill '{skill}' but it is not bundled")
            dst = skills_dst / skill
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  skill   {dst}")
        for agent in manifest["agents"]:
            src = bundle / "agents" / agent
            if not src.is_file():
                raise SystemExit(f"manifest lists agent '{agent}' but it is not bundled")
            dst = agents_dst / agent
            shutil.copy2(src, dst)
            print(f"  agent   {dst}")

    print(f"\nInstalled tiny-spec into {claude_dir}. Restart Claude Code to load it.")
    return 0


def uninstall(claude_dir: Path) -> int:
    """Remove only the manifest's skills and agents. Leaves the rest alone."""
    manifest = _manifest()
    removed = 0
    for skill in manifest["skills"]:
        dst = claude_dir / "skills" / skill
        if dst.exists():
            shutil.rmtree(dst)
            print(f"  removed {dst}")
            removed += 1
    for agent in manifest["agents"]:
        dst = claude_dir / "agents" / agent
        if dst.exists():
            dst.unlink()
            print(f"  removed {dst}")
            removed += 1

    if removed:
        print(f"\nRemoved {removed} item(s) from {claude_dir}.")
    else:
        print(f"Nothing to remove in {claude_dir}.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tiny-spec",
        description="Install the tiny-spec skill suite into your Claude Code config.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    for name, help_text in (
        ("install", "copy skills and agents into ~/.claude (re-run to update)"),
        ("uninstall", "remove the skills and agents tiny-spec installed"),
    ):
        p = sub.add_parser(name, help=help_text)
        p.add_argument(
            "--dir",
            type=Path,
            default=_default_dir(),
            metavar="PATH",
            help="Claude config directory (default: ~/.claude)",
        )

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    claude_dir: Path = args.dir.expanduser()
    if args.command == "install":
        return install(claude_dir)
    if args.command == "uninstall":
        return uninstall(claude_dir)
    return 1  # pragma: no cover — argparse guarantees a known command


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
