from __future__ import annotations

import subprocess

from .json_extract import extract_json_object
from .models import AgentCommand


class CodexExecutor:
    def __init__(self, model: str) -> None:
        self.model = model

    def run_step(self, prompt: str) -> AgentCommand:
        args = [
            "codex",
            "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "--skip-git-repo-check",
            "-m",
            self.model,
            prompt,
        ]
        result = subprocess.run(args, check=False, text=True, capture_output=True)
        output = "\n".join(part for part in [result.stdout, result.stderr] if part)
        if result.returncode != 0 and not output.strip():
            raise RuntimeError(f"codex exec failed with exit code {result.returncode}")
        return AgentCommand.model_validate(extract_json_object(output))
