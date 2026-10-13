#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v python3 >/dev/null || { echo 'Python 3.10+ is required.' >&2; exit 1; }
command -v go >/dev/null || { echo 'Install the Go toolchain specified in go.mod first.' >&2; exit 1; }
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else "Python 3.10+ is required.")'
git rev-parse --git-dir >/dev/null
test "$(git rev-parse --show-toplevel)" = "$PWD" || { echo 'Run setup in the generated repository clone, not the module example subdirectory.' >&2; exit 1; }
test ! -L .venv || { echo 'Refusing a symlinked .venv.' >&2; exit 1; }
# The environment and hook entry point remain inside this clone, not global PATH.
python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check 'pre-commit==4.3.0'
.venv/bin/python -m pre_commit validate-config
.venv/bin/python -m pre_commit install --install-hooks
.venv/bin/python -m pre_commit run secret-scan-setup --hook-stage manual
echo 'Developer hooks installed. Gitleaks is verified in your user cache; no standalone install is needed.'
