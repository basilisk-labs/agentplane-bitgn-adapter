# Task Backlog

This repo uses this file as the adapter-local task list. BitGN task ids remain
external benchmark cases; adapter tasks describe generic harness work and must
not encode `if task_id == ...` behavior.

## Active

### BGN-001 - Generic route and playbook runner

- Status: in progress
- Goal: route benchmark instructions into reusable AgentPlane-style
  blueprint/playbook contracts before the model loop.
- Current scope:
  - `context.assimilation + knowledge_capture_pipeline` for PCM inbox capture
    tasks.
  - `runner.execution + verify_then_answer` fallback for non-capture tasks.
- Done so far:
  - route metadata is recorded in proof;
  - per-step execution state is recorded in proof;
  - capture verifier blocks premature `OUTCOME_OK`;
  - capture verifier blocks false unsupported outcomes for executable capture
    tasks;
  - host-path runtime writes are normalized.
- Next:
  - add ECOM playbooks;
  - add batch score report generation.

### BGN-002 - PAC1 full-run hardening

- Status: pending
- Goal: run all `bitgn/pac1-dev` tasks and group failures by generic failure
  class.
- Acceptance:
  - no task-id-specific conditions;
  - failures grouped by playbook/verifier class;
  - coverage docs updated from live scores.

### BGN-003 - ECOM route and policy playbooks

- Status: pending
- Goal: add reusable ECOM playbooks for SQL lookup, policy-guarded mutation,
  denial, and inventory/order/customer actions.
- Acceptance:
  - policy files are read before sensitive actions;
  - SQL/tool use is structured;
  - denial/unsupported/success outcomes are separated by verifier state.

### BGN-004 - Score matrix reporting

- Status: pending
- Goal: persist machine-readable run summaries and generate Markdown coverage
  tables from proof artifacts.
- Acceptance:
  - report includes benchmark, runtime, model, task id, trial id, score, and
    failure class;
  - docs can be updated without manually reading full transcripts.

## Completed

### BGN-000 - Live smoke harness

- Status: completed
- Result: sandbox `t01`, PAC1 `t01`, and ECOM `t01` live smoke paths pass.
