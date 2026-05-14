# BitGN Test Strategy

## Objective

Use BitGN as an external behavioral benchmark for AgentPlane as a control-plane
profile around Codex, not as a standalone model.

The adapter should maximize benchmark-valid success by improving generic agent
execution mechanics:

- load runtime policy before the first model step;
- expose only tools valid for the active runtime;
- keep observations compact and grounded;
- prefer deterministic generic helpers over shell access;
- always submit an answer, even on adapter step exhaustion;
- record enough proof to classify failures.

## Runtime ladder

1. `bitgn/sandbox`
   - Purpose: prove live harness, playground trial, Codex OAuth, runtime calls,
     answer submission, and score retrieval.
   - No BitGN API key required.

2. `bitgn/pac1-dev`
   - Purpose: prove Platform API key, PCM runtime, policy-sensitive file
     operations, outcome/ref quality, and multi-step state tracking.
   - Key risks: unsupported shell assumptions, too many one-file mutations,
     missed refs, and no final answer.

3. `bitgn/ecom1-dev`
   - Purpose: prove the leaderboard-relevant domain: ecommerce policy, SQL,
     payments, fraud controls, warehouse/customer evidence, and auditability.
   - Key risks: SQL misuse, numeric aggregation errors, policy injection, and
     unsafe payment/customer actions.

## Generic improvements already in the adapter

- Runtime bootstrap:
  - sandbox: `tree /`, `read AGENTS.MD`
  - PCM: `tree /`, `read AGENTS.md`, `context`
  - ECOM: `tree /`, `read /AGENTS.MD`, `/bin/date`, `/bin/id`
- Runtime-specific tool contracts:
  - PCM cannot use `exec`.
  - ECOM can use `exec`, especially `/bin/sql`.
- `delete_many` pseudo-tool:
  - maps to multiple official runtime `delete` calls;
  - keeps the helper generic and visible in proof;
  - avoids benchmark-invalid shell access in PCM.
- Fallback final answer:
  - prevents `no answer provided` when the step limit is hit.
- Live progress:
  - prints bootstrap and per-step tool choices with flush.

## Current PAC1 failure notes

The first PAC1 smoke proved API/runtime access but failed:

- score: `0.00`;
- reason: `no answer provided`;
- root causes:
  - generic prompt exposed `exec` to PCM;
  - PCM `tree` ignored `path` and always used default root;
  - no final fallback answer on max step exhaustion.

Those failure modes are now addressed in the adapter. A fresh PAC1 run is still
required before claiming broad PAC1 readiness.

## Current smoke status

- `bitgn/sandbox t01`: pass, score `1.00`.
- `bitgn/pac1-dev t01`: pass, score `1.00`.
- `bitgn/ecom1-dev t01`: pass, score `1.00`.

These are first-task smoke checks only. They prove the harness path and the
first happy-path task for each runtime, not benchmark readiness.

Current coverage rule:

- Treat `t01` as the only proven passing task in PAC1 and ECOM1.
- Treat every non-`t01` PAC1/ECOM1 task as failing or unsupported until a live
  score proves otherwise.
- Do not extrapolate from `t01` to task families; BitGN tasks are heterogeneous
  and benchmark metadata exposes only ids, not task semantics.

## Claim threshold

Valid claim after sandbox only:

- The adapter can run a live BitGN playground trial and receive a score.

Valid claim after PAC1 DEV single-task success:

- The adapter can execute policy-sensitive PCM file tasks through official
  runtime calls.

Valid claim after ECOM1 DEV single-task success:

- The adapter can exercise the most relevant leaderboard domain surface.

Invalid claim until broader evidence exists:

- AgentPlane is leaderboard-ready.
- AgentPlane improves score over raw Codex.
- AgentPlane is a model.
- PAC1 or ECOM1 is passing beyond `t01`.
