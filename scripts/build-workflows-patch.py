#!/usr/bin/env python3
"""Build a reviewable sibling-repository patch; never writes to that repository."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkout", required=True)
    args = parser.parse_args()
    checkout = Path(args.checkout)
    root = Path(__file__).resolve().parents[1]
    integration = root / "integrations" / "github-workflows"
    additions = integration / "additions"
    blocks = []
    for source in sorted(additions.rglob("*")):
        if not source.is_file() or "__pycache__" in source.parts:
            continue
        relative = source.relative_to(additions).as_posix()
        target = checkout / relative
        if target.exists():
            raise ValueError("Addition conflicts with an existing sibling file: " + relative)
        executable = bool(source.stat().st_mode & 0o111)
        blocks.append(f"diff --git a/{relative} b/{relative}\nnew file mode {'100755' if executable else '100644'}\n")
        blocks.extend(difflib.unified_diff([], source.read_text().splitlines(keepends=True),
                                         fromfile="/dev/null", tofile="b/" + relative))
    for source in sorted((integration / "updates").rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(integration / "updates").as_posix()
        target = checkout / relative
        if not target.is_file():
            raise ValueError("Update requires an existing baseline file: " + relative)
        blocks.append(f"diff --git a/{relative} b/{relative}\n")
        blocks.extend(difflib.unified_diff(target.read_text().splitlines(keepends=True),
                                         source.read_text().splitlines(keepends=True),
                                         fromfile="a/" + relative, tofile="b/" + relative))
    original = (checkout / "TERRAFORM.md").read_text()
    updated = original + (integration / "TERRAFORM-addendum.md").read_text()
    blocks.append("diff --git a/TERRAFORM.md b/TERRAFORM.md\n")
    blocks.extend(difflib.unified_diff(original.splitlines(keepends=True), updated.splitlines(keepends=True),
                                     fromfile="a/TERRAFORM.md", tofile="b/TERRAFORM.md"))
    (integration / "local-additions.patch").write_text("".join(blocks))
    baseline = {}
    for relative in ("TERRAFORM.md", ".github/workflows/terraform-plan.yml", ".github/workflows/terraform-deploy.yml"):
        baseline[relative] = hashlib.sha256((checkout / relative).read_bytes()).hexdigest()
    (integration / "baseline-sha256.json").write_text(json.dumps(baseline, indent=2) + "\n")
    print("Patch generated locally. Sibling checkout was read only.")


if __name__ == "__main__":
    main()
