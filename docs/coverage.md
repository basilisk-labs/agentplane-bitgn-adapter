# Coverage Matrix

## Summary

Current proven coverage is smoke plus the first targeted PAC1 slice.

| Benchmark | Tasks | Proven pass | Current effective status |
| --- | ---: | --- | --- |
| `bitgn/sandbox` | 7 | `t01` | smoke path proven only |
| `bitgn/pac1-dev` | 43 | `t01`-`t06` | `t07`-`t43` unproven |
| `bitgn/ecom1-dev` | 24 | `t01` | `t02`-`t24` treated as failing/unsupported |

The adapter has not demonstrated benchmark-level competence. It has
demonstrated that the live harness path works for the first task of each runtime.

## Why this matters

`t01` is a smoke task. It can validate:

- authentication;
- benchmark start/end flow;
- runtime client wiring;
- policy bootstrap;
- final answer submission;
- score retrieval.

It cannot validate:

- task-family generalization;
- prompt-injection resistance across hidden variations;
- date/numeric correctness;
- multi-file and multi-step recovery;
- ECOM payment/fraud/warehouse policy handling;
- leaderboard viability.

## Current task inventory

BitGN benchmark metadata currently exposes ids for these DEV benchmarks:

- PAC1 DEV: `t01` through `t43`.
- ECOM1 DEV: `t01` through `t24`.

Task instructions are trial-time data, so this repo should not claim semantic
coverage for non-`t01` tasks without running them and recording score detail.

## Reporting rule

When summarizing the adapter, use this wording:

> The adapter passes `t01` smoke checks for sandbox, PAC1 DEV, and ECOM1 DEV.
> It also passes the targeted PAC1 DEV `t02`-`t06` slice. All remaining
> PAC1/ECOM1 tasks are unproven or currently failing and should be treated as
> failing until live scores prove otherwise.

Do not use:

- "PAC1 passes";
- "ECOM1 passes";
- "leaderboard-ready";
- "AgentPlane improves BitGN score";
- "the benchmark is solved".

## Next validation step

Run broader PAC1 and ECOM slices before improving claims:

```bash
./scripts/bitgn_smoke.sh --benchmark-id bitgn/pac1-dev --runtime pcm --model gpt-5.4-mini --max-steps 32 t07 t08 t09 t10
./scripts/bitgn_smoke.sh --benchmark-id bitgn/ecom1-dev --runtime ecom --model gpt-5.4-mini --max-steps 12 t02 t03 t04 t05 t06
```

The expected near-term result is not a high score. The useful output is a
failure taxonomy that can drive generic adapter improvements without
task-specific cheating.
