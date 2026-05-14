# Codex OAuth Notes

OpenAI's current Codex CLI supports signing in with a ChatGPT account via
`codex login`. Local `codex exec` can then use that stored auth instead of an
explicit `OPENAI_API_KEY`.

Use it for local BitGN smoke runs when the agent process runs on the same
machine as the logged-in Codex CLI.

Prefer API-key auth for:

- CI;
- remote benchmark machines;
- reproducing a public leaderboard run;
- publishing exact run instructions for another person.

Verification commands:

```bash
codex --version
codex login status
codex exec --skip-git-repo-check 'Return {"tool":"answer","message":"ok"} as JSON.'
```
