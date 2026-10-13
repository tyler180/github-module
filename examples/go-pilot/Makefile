.PHONY: setup hooks run test check
setup:
	bash scripts/setup.sh
hooks:
	.venv/bin/python -m pre_commit run --all-files
run:
	go run .
test:
	go test -race ./...
check:
	bash scripts/validate.sh
