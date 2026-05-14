# Leaderboard Plan

## Current assessment

Current live evidence is first-task-only:

- PAC1 DEV: `t01` passed, `t02`-`t43` must be treated as failing/unsupported.
- ECOM1 DEV: `t01` passed, `t02`-`t24` must be treated as failing/unsupported.

This is enough to validate the adapter path. It is not enough for leaderboard
positioning.

PAC1 PROD is already saturated by perfect or near-perfect live scores. AgentPlane
can still use PAC1 for engineering proof, but brand lift from PAC1 requires more
than a mid-table run.

The better recognition path is ECOM1:

- newer benchmark surface;
- closer fit to AgentPlane policy and audit model;
- richer operations domain: customer files, warehouse evidence, payment state,
  policy books, fraud controls, support workflows, and SQL.

## Evidence target

A credible public artifact should include:

- BitGN run link or run id;
- adapter git commit;
- exact model/auth mode;
- proof bundle for passing and failing tasks;
- score-detail failure taxonomy;
- comparison against the upstream Python sample with the same model where
  feasible.

## Minimum run sequence

1. PAC1 DEV `t01` smoke. Done.
2. ECOM1 DEV `t01` smoke. Done.
3. PAC1 DEV small slice: `t02`-`t06`.
4. ECOM1 DEV small slice: `t02`-`t06`.
5. Failure taxonomy from non-`t01` tasks.
6. ECOM1 selected failure-class batch.
7. ECOM1 full public run only after selected batches have non-trivial pass rate.

## Expected weak links

- Codex CLI JSON adherence in a repeated loop.
- Runtime observation volume and context compaction.
- Exact `OUTCOME_*` selection.
- Structured write validation.
- Numeric aggregation/date scoping.
- Prompt injection hidden inside trusted-looking documents.
- Overfitting to the first task while every later task remains failing.
