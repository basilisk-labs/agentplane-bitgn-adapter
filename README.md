# AgentPlane BitGN Adapter

[![CI](https://github.com/basilisk-labs/agentplane-bitgn-adapter/actions/workflows/ci.yml/badge.svg)](https://github.com/basilisk-labs/agentplane-bitgn-adapter/actions/workflows/ci.yml)

Adapter scaffold for running AgentPlane-backed Codex execution against BitGN
benchmarks.

AgentPlane is not submitted as a model. It is used as a control-plane profile
around an executor:

- benchmark runtime: BitGN PCM or ECOM
- executor: Codex CLI
- control layer: policy, step loop, proof bundle, score-detail capture

## Status

Experimental, but the first real BitGN smoke has passed: `bitgn/sandbox t01`
scored `1.00` with `gpt-5.4-mini` through Codex CLI ChatGPT OAuth.

Start with sandbox, then `bitgn/pac1-dev`, then a single ECOM task before
claiming anything about leaderboard quality.

## Why this exists

BitGN evaluates observable agent behavior: runtime tool calls, files, task
state, side effects, outcome codes, compliance, and security posture. That is
the same surface where AgentPlane can add value: bounded policy, traceability,
explicit outcomes, and failure evidence.

The near-term goal is not "AgentPlane beats everyone". The useful public claim
is narrower:

> AgentPlane can wrap a strong executor, preserve BitGN benchmark validity, and
> produce auditable evidence for why trials passed or failed.

## Install

```bash
make sync
```

Install BitGN SDK dependencies from the same Buf registry used by the upstream
samples:

```bash
make sync-bitgn
```

The SDK currently tracks Python 3.14 in the sample agents, so the Make targets
create a Python 3.14 uv environment.

## Authentication

Codex can use ChatGPT subscription auth:

```bash
codex login
codex login status
```

That path is useful for local smoke runs because the adapter invokes `codex
exec`. For reproducible public runs, API-key auth is still cleaner because it is
easier to document and recreate in CI or another machine.

BitGN official runs still need:

```bash
export BITGN_API_KEY="..."
```

## PAC1 smoke

```bash
cp .env.example .env.local
$EDITOR .env.local
make oauth
make sandbox
```

`scripts/bitgn_smoke.sh` loads `.env` and then `.env.local`; keep secrets in
one of those ignored files, not in committed config.

Sandbox is the first end-to-end check because it does not require a BitGN
Platform key. PAC1 is the next check:

```bash
make pac1
```

## ECOM smoke

Set:

```bash
BENCHMARK_ID=bitgn/ecom1-dev
BITGN_RUNTIME=ecom
```

Then run a single task:

```bash
make ecom
```

## Proof bundle

Each trial writes:

```text
.agentplane-bitgn/<benchmark-id>/<runtime>/<task-id>/<trial-id>/
  AGENTS.md
  proof.json
```

The proof bundle captures:

- benchmark id and runtime
- model id
- task id and trial id
- each JSON tool command requested by Codex
- runtime observations, truncated for readability
- final status

## Documentation

- [Runbook](docs/runbook.md)
- [Test strategy](docs/test-strategy.md)
- [Leaderboard plan](docs/leaderboard.md)
- [Evidence report template](docs/evidence-template.md)
- [Cost notes](docs/cost.md)
- [OAuth notes](docs/oauth.md)
- [Smoke results](docs/test-results.md)

## Leaderboard realism

PAC1 live already has multiple 104/104 runs. A naive scaffold is unlikely to
stand out there. The best AgentPlane path is:

1. Use PAC1 DEV to harden outcome selection, grounding refs, structured writes,
   and injection refusal.
2. Mine `score_detail` into regression cases.
3. Move to ECOM1, where policy books, payment state, SQL, fraud controls, and
   audit trails are closer to AgentPlane's control-plane strengths.
4. Publish a proof-backed run rather than only a score screenshot.

## Integrity rules

Do not:

- fetch benchmark solutions from the internet;
- inspect hidden graders or oracle solutions;
- alter BitGN scoring, task sets, or runtime contracts;
- inject task-specific hints into the adapter policy;
- claim leaderboard readiness without a reproducible run id and proof bundle.
