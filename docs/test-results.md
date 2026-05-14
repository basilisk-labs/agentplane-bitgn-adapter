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
