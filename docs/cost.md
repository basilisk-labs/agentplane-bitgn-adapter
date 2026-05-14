# Cost Notes

The adapter primarily uses `codex exec`, so local ChatGPT OAuth can cover
development smoke runs when `codex login status` reports a ChatGPT login.

Cost or usage limits are still model/account dependent. Treat these as planning
rules, not guarantees:

1. Start with `make sandbox`.
2. Run one PAC1 DEV task.
3. Run one ECOM1 DEV task.
4. Only then run a wider batch.

Recommended smoke models:

- `gpt-5.4-mini` for adapter validation.
- `gpt-5.4` or stronger only after the runtime loop is stable.

For public reproducibility, API-key based Codex auth is cleaner than local
OAuth because another machine can recreate it.
