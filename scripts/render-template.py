#!/usr/bin/env python3
"""Materialize the generic template and optional Go caller locally, never push."""
import argparse
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--code-owner", required=True, help="user or organization/team, without @")
    parser.add_argument("--workflow-sha", required=True)
    parser.add_argument("--hook-sha", required=True)
    parser.add_argument("--go-version", help="optional Go pilot instead of the generic caller")
    args = parser.parse_args()
    if not all(re.fullmatch(r"[0-9a-f]{40}", sha) for sha in (args.workflow_sha, args.hook_sha)):
        parser.error("pins must be full commit SHAs")
    if not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)?", args.code_owner):
        parser.error("supply a GitHub user or organization/team")
    if args.go_version and not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", args.go_version):
        parser.error("Go version must be explicit")
    destination = Path(args.destination)
    if destination.exists():
        parser.error("destination must not exist; bootstrap must never overwrite files")
    root = Path(__file__).resolve().parents[1]
    source = root / "templates" / "generic"
    replacement = {"CODE_OWNER": args.code_owner, "WORKFLOW_SHA": args.workflow_sha,
                   "HOOK_SHA": args.hook_sha, "GO_VERSION": args.go_version or ""}
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
    print("Local starter materialized. Source commit provenance and live checks remain pending.")


if __name__ == "__main__":
    main()
