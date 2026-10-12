#!/usr/bin/env python3
"""Materialize the generic template and optional Go caller locally, never push."""
import argparse
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--code-owner", required=True, help="user or organization/team, without @")
    parser.add_argument("--workflow-ref", "--workflow-sha", dest="workflow_ref", required=True)
    parser.add_argument("--hook-ref", "--hook-sha", dest="hook_ref", required=True)
    parser.add_argument("--go-version", help="optional Go pilot instead of the generic caller")
    parser.add_argument("--go-module", default="example.com/github-go-pilot", help="Go module path for a rendered Go pilot")
    args = parser.parse_args()
    immutable_ref = r"(?:[0-9a-f]{40}|v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)?)"
    if not all(re.fullmatch(immutable_ref, ref) for ref in (args.workflow_ref, args.hook_ref)):
        parser.error("refs must be full commit SHAs or exact immutable release versions")
    if not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)?", args.code_owner):
        parser.error("supply a GitHub user or organization/team")
    if args.go_version and not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", args.go_version):
        parser.error("Go version must be explicit")
    if args.go_version and (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)+", args.go_module) or any(part in (".", "..") for part in args.go_module.split("/"))):
        parser.error("supply a valid Go module path")
    destination = Path(args.destination)
    if destination.exists():
        parser.error("destination must not exist; bootstrap must never overwrite files")
    root = Path(__file__).resolve().parents[1]
    source = root / "templates" / "generic"
    replacement = {"CODE_OWNER": args.code_owner, "WORKFLOW_SHA": args.workflow_ref,
                   "HOOK_SHA": args.hook_ref, "GO_VERSION": args.go_version or ""}
    destination.mkdir(parents=True)
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        if args.go_version and str(relative) == ".github/workflows/ci.yml.in":
            path = root / "examples" / "go-pilot" / "ci.yml.in"
        target = destination / (str(relative)[:-3] if str(relative).endswith(".in") else relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        content = path.read_text()
        for key, value in replacement.items():
            content = content.replace("{{" + key + "}}", value)
        if "{{" in content:
            raise ValueError("unresolved template placeholder")
        target.write_text(content)
    if args.go_version:
        pilot = root / "examples" / "go-pilot"
        for path in pilot.rglob("*"):
            relative = path.relative_to(pilot)
            if not path.is_file() or path.name.endswith(".in") or any(part in (".git", "__pycache__", ".terraform") for part in relative.parts):
                continue
            if str(relative) in (".github/workflows/ci.yml", ".pre-commit-config.yaml", ".github/CODEOWNERS"):
                continue
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            content = path.read_text()
            if str(relative) == "go.mod":
                content = "module " + args.go_module + "\n\ngo " + ".".join(args.go_version.split(".")[:2]) + ".0\n"
            target.write_text(content)
            target.chmod(path.stat().st_mode & 0o777)
        (destination / ".github/CODEOWNERS").write_text("* @" + args.code_owner + "\n")
    print("Local starter materialized. Source commit provenance and live checks remain pending.")


if __name__ == "__main__":
    main()
