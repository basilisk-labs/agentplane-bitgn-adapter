# Smoke Results

## 2026-05-14 sandbox t01

Command:

```bash
MODEL_ID=gpt-5.4-mini ./scripts/bitgn_smoke.sh \
  --benchmark-id bitgn/sandbox \
  --runtime sandbox \
  --max-steps 4 \
  t01
```

Result:

- Benchmark: `bitgn/sandbox`
- Runtime: `sandbox`
- Model: `gpt-5.4-mini`
- Task: `t01`
- Score: `1.00`
- Trial id: `vm2-LwukLhRBxoWzA1g6UdkZrxrgPKE`

Observed proof shape:

- bootstrap `tree /`
- bootstrap `read AGENTS.MD`
- final answer: `Not Ready`
- refs: `AGENTS.MD`

Interpretation:

This proves the adapter can connect to the live BitGN harness, start a
playground trial, execute runtime calls, invoke Codex through ChatGPT OAuth,
submit the final answer, and receive a live score. It does not prove PAC1,
ECOM1, or leaderboard readiness.

## 2026-05-14 PAC1 DEV t01

Command:

```bash
./scripts/bitgn_smoke.sh \
  --benchmark-id bitgn/pac1-dev \
  --runtime pcm \
  --model gpt-5.4-mini \
  --max-steps 8 \
  t01
```

Result:

- Benchmark: `bitgn/pac1-dev`
- Runtime: `pcm`
- Model: `gpt-5.4-mini`
- Task: `t01`
- Score: `1.00`
- Trial id: `vm2-Lwuoau7vrBgfG2XpcHXvLMkfKma`
- Proof: `.agentplane-bitgn/bitgn_pac1-dev/pcm/t01/vm2-Lwuoau7vrBgfG2XpcHXvLMkfKma/proof.json`

Observed proof shape:

- bootstrap `tree /`
- bootstrap `read AGENTS.md`
- bootstrap `context`
- `tree 02_distill`
- `delete_many`
- verification tree
- final answer

Interpretation:

This proves the adapter can use the BitGN Platform API key, run a PAC1 DEV
trial, avoid unsupported shell execution in PCM, use a generic batch helper that
maps to official runtime deletes, and complete a policy-sensitive file task.

## 2026-05-14 ECOM1 DEV t01

Command:

```bash
./scripts/bitgn_smoke.sh \
  --benchmark-id bitgn/ecom1-dev \
  --runtime ecom \
  --model gpt-5.4-mini \
  --max-steps 10 \
  t01
```

Result:

- Benchmark: `bitgn/ecom1-dev`
- Runtime: `ecom`
- Model: `gpt-5.4-mini`
- Task: `t01`
- Score: `1.00`
- Trial id: `vm2-LwuokU5vFt5ABGaunXRKzq5idqi`
- Proof: `.agentplane-bitgn/bitgn_ecom1-dev/ecom/t01/vm2-LwuokU5vFt5ABGaunXRKzq5idqi/proof.json`

Observed proof shape:

- bootstrap `tree /`
- bootstrap `read /AGENTS.MD`
- bootstrap `/bin/date`
- bootstrap `/bin/id`
- inspect docs
- use `/bin/sql`
- final answer

Interpretation:

This proves the adapter can exercise the most relevant ECOM runtime surface:
policy bootstrap, runtime identity, SQL execution, final answer, and live score.
