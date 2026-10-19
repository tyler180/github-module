-include .go-main.mk
GO_MAIN ?= .

.PHONY: setup hooks run build test check
setup:
	bash scripts/setup.sh
hooks:
	.venv/bin/python -m pre_commit run --all-files
run:
	go run $(GO_MAIN)
build:
	go build ./...
test:
	go test -race ./...
check:
	bash scripts/validate.sh
