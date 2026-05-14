# Leaderboard Plan

## Current assessment

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

1. PAC1 DEV single task.
2. PAC1 DEV all 43 tasks.
3. ECOM1 DEV single task.
4. ECOM1 DEV selected failure-class batch.
5. ECOM1 full public run.

## Expected weak links

- Codex CLI JSON adherence in a repeated loop.
- Runtime observation volume and context compaction.
- Exact `OUTCOME_*` selection.
- Structured write validation.
- Numeric aggregation/date scoping.
- Prompt injection hidden inside trusted-looking documents.
