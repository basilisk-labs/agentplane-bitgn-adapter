.PHONY: sync sync-bitgn lint typecheck test check help oauth sandbox pac1 ecom

help:
	@echo "Targets: sync sync-bitgn check oauth sandbox pac1 ecom"

sync:
	uv sync --extra dev --python 3.14

sync-bitgn:
	uv sync --extra dev --extra bitgn --python 3.14

lint:
	uv run --extra dev ruff check .

typecheck:
	uv run --extra dev pyright

test:
	uv run --extra dev pytest

check: lint typecheck test

oauth:
	./scripts/check_oauth.sh

sandbox:
	./scripts/bitgn_smoke.sh --benchmark-id bitgn/sandbox --runtime sandbox t01

pac1:
	./scripts/bitgn_smoke.sh --benchmark-id bitgn/pac1-dev --runtime pcm t01

ecom:
	./scripts/bitgn_smoke.sh --benchmark-id bitgn/ecom1-dev --runtime ecom t01
