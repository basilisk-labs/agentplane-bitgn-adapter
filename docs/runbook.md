# Runbook

## 1. Verify local tools

```bash
uv --version
codex --version
codex login status
```

## 2. Install adapter

```bash
make sync
make check
```

## 3. Install BitGN SDK

```bash
make sync-bitgn
```

The BitGN generated Python SDK is published through Buf's Python registry.
This repo keeps the same pins as `bitgn/sample-agents`.

## 4. First end-to-end smoke

```bash
make sandbox
```

This uses `bitgn/sandbox` and `StartPlaygroundRequest`, so no BitGN Platform key
is required.

## 5. PAC1 DEV smoke

```bash
export BITGN_API_KEY="..."
make pac1
```

## 6. ECOM1 DEV smoke

```bash
export BITGN_API_KEY="..."
make ecom
```

## 7. Inspect artifacts

Check:

- `.agentplane-bitgn/<task-id>/AGENTS.md`
- `.agentplane-bitgn/<task-id>/proof.json`
- terminal score and `score_detail`

## 8. Full run gate

Do not run PROD or publish a leaderboard claim until:

- sandbox smoke completed;
- PAC1 DEV single task completed;
- ECOM1 DEV single task completed;
- proof bundle exists;
- score_detail failures have been classified;
- adapter commit is public and pinned.
