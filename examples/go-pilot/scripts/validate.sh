#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
unformatted=$(gofmt -l .)
if test -n "$unformatted"; then
  printf 'Run gofmt on:\n%s\n' "$unformatted" >&2
  exit 1
fi
go vet ./...
go test -race ./...
test "$(go run . -name 'Go pilot')" = 'Hello, Go pilot!'
