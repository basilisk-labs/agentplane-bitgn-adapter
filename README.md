# AgentPlane BitGN Adapter

Adapter scaffold for running AgentPlane-backed Codex execution against BitGN
benchmarks.

AgentPlane is not submitted as a model. It is used as a control-plane profile
around an executor:

- benchmark runtime: BitGN PCM or ECOM
- executor: Codex CLI
- control layer: policy, step loop, proof bundle, score-detail capture

## Status

Experimental. Start with `bitgn/pac1-dev` or a single ECOM task before claiming
anything about leaderboard quality.

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
uv venv
uv pip install -e ".[dev]"
```

Install BitGN SDK dependencies the same way as the upstream samples:

```bash
git clone https://github.com/bitgn/sample-agents /tmp/bitgn-sample-agents
cd /tmp/bitgn-sample-agents/pac1-py
make sync
```

If the generated BitGN Python packages are not visible in this environment,
run this adapter from the same virtualenv used by the sample agent.

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
./scripts/check_oauth.sh
./scripts/bitgn_smoke.sh t01
```

Default settings:

```bash
BENCHMARK_ID=bitgn/pac1-dev
BITGN_RUNTIME=pcm
MODEL_ID=gpt-5.4
```

## ECOM smoke

Set:

```bash
BENCHMARK_ID=bitgn/ecom1-dev
BITGN_RUNTIME=ecom
```

Then run a single task:

```bash
./scripts/bitgn_smoke.sh t01
```

## Proof bundle

Each trial writes:

```text
.agentplane-bitgn/<task-id>/
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
