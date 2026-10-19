#!/usr/bin/env python3
"""Materialize the generic template and optional Go caller locally, never push."""
import argparse
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--code-owner", help="user or organization/team, without @")
    parser.add_argument("--workflow-ref", "--workflow-sha", dest="workflow_ref")
    parser.add_argument("--hook-ref", "--hook-sha", dest="hook_ref")
    parser.add_argument("--go-version", help="optional Go pilot instead of the generic caller")
    parser.add_argument("--go-module", default="example.com/github-go-pilot", help="Go module path for a rendered Go pilot")
    parser.add_argument("--terraform-version", help="opt in to AWS Terraform callers; explicit patch version")
    parser.add_argument("--terraform-workflow-ref", help="exact immutable release version or full SHA for shared workflows")
    parser.add_argument("--terraform-directory", default="terraform")
    parser.add_argument("--workflows-only", action="store_true", help="render additive Terraform workflow files for an existing repo into a new staging directory")
    args = parser.parse_args()
    immutable_ref = r"(?:[0-9a-f]{40}|v(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)?)"
    if args.terraform_version:
        if (not args.workflows_only and not args.go_version) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", args.terraform_version):
            parser.error("Terraform starter requires --go-version and an explicit Terraform patch version")
        if not re.fullmatch(immutable_ref, args.terraform_workflow_ref or ""):
            parser.error("Terraform workflows require an exact immutable release version or full SHA")
        if not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*", args.terraform_directory):
            parser.error("Terraform directory must be a relative directory without traversal")
    elif args.workflows_only or args.terraform_workflow_ref:
        parser.error("--workflows-only and --terraform-workflow-ref require --terraform-version")
    if not args.workflows_only and not all(re.fullmatch(immutable_ref, ref or "") for ref in (args.workflow_ref, args.hook_ref)):
        parser.error("refs must be full commit SHAs or exact immutable release versions")
    if not args.workflows_only and not re.fullmatch(r"[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)?", args.code_owner or ""):
        parser.error("supply a GitHub user or organization/team")
    if args.go_version and not re.fullmatch(r"[0-9]+\.[0-9]+(?:\.[0-9]+)?", args.go_version):
        parser.error("Go version must be explicit")
    if args.go_version and (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)+", args.go_module) or any(part in (".", "..") for part in args.go_module.split("/"))):
        parser.error("supply a valid Go module path")
    destination = Path(args.destination)
    if destination.exists():
        parser.error("destination must not exist; bootstrap must never overwrite files")
    root = Path(__file__).resolve().parents[1]
    if args.workflows_only:
        destination.mkdir(parents=True)
        render_terraform(root, destination, args)
        print("Local Terraform workflow overlay materialized; review before adding to an existing repository.")
        return
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
            if not path.is_file() or path.name.endswith(".in") or any(part in (".git", ".venv", "__pycache__", ".terraform", "terraform") for part in relative.parts):
                continue
            if str(relative) in (".github/workflows/ci.yml", ".pre-commit-config.yaml", ".github/CODEOWNERS"):
                continue
            if str(relative) in ("main.go", "main_test.go"):
                command = args.go_module.split("/")[-1]
                relative = Path("cmd") / command / relative
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            content = path.read_text()
            if str(relative) == "README.md":
                start = content.index("## Create the repository")
                end = content.index("## Run the Go starter")
                content = content[:start] + "Repository provisioning is complete before this starter is added. See BOOTSTRAP.md for source bootstrap instructions.\n\n" + content[end:]
                content = content.replace("go run .", "go run ./cmd/" + args.go_module.split("/")[-1])
            if str(relative) == "go.mod":
                content = "module " + args.go_module + "\n\ngo " + ".".join(args.go_version.split(".")[:2]) + ".0\n"
            target.write_text(content)
            target.chmod(path.stat().st_mode & 0o777)
        (destination / ".go-main.mk").write_text(
            "# Generated starter command; review and commit.\nGO_MAIN := ./cmd/" + args.go_module.split("/")[-1] + "\n")
        (destination / ".github/CODEOWNERS").write_text("* @" + args.code_owner + "\n")
        with (destination / ".pre-commit-config.yaml").open("a") as hooks:
            hooks.write("  - repo: local\n    hooks:\n      - id: go-validation\n        name: Go formatting, vet and race tests\n        entry: bash scripts/validate.sh\n        language: system\n        pass_filenames: false\n        always_run: true\n")
    if args.terraform_version:
        render_terraform(root, destination, args)
        with (destination / ".gitignore").open("a") as ignore:
            ignore.write("\n# Terraform runtime and state\n**/.terraform/\n*.tfstate\n*.tfstate.*\n*.tfplan\ncrash.log\n*.tfvars\n*.tfvars.json\n")
    print("Local starter materialized. Source commit provenance and live checks remain pending.")


def render_terraform(root, destination, args):
    replacements = {"TERRAFORM_VERSION": args.terraform_version,
                    "TERRAFORM_WORKFLOW_REF": args.terraform_workflow_ref,
                    "TERRAFORM_DIRECTORY": args.terraform_directory}
    source = root / "templates/go-terraform"
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target = destination / str(relative).removesuffix(".in")
        target.parent.mkdir(parents=True, exist_ok=True)
        content = path.read_text()
        for key, value in replacements.items():
            content = content.replace("{{" + key + "}}", value)
        if re.search(r"(?<!\$)\{\{", content):
            raise ValueError("unresolved Terraform template placeholder")
        target.write_text(content)


if __name__ == "__main__":
    main()
