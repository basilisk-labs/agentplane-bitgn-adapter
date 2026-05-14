from __future__ import annotations

import subprocess
from typing import Any

from pydantic import ValidationError

from .json_extract import extract_json_object
from .models import AgentCommand


def normalize_command_object(data: dict[str, Any]) -> dict[str, Any]:
    for key in ("command", "function", "action"):
        value = data.get(key)
        if isinstance(value, dict):
            data = value
            break
    if "tool" not in data and ("message" in data or "outcome" in data):
        data = {
            **data,
            "tool": "answer",
            "reason": data.get("reason", "Executor returned a final-answer shaped object."),
            "message": str(data.get("message") or data.get("answer") or data.get("outcome") or ""),
        }
    return data


def validation_error_summary(error: ValidationError) -> str:
    parts: list[str] = []
    for item in error.errors()[:5]:
        loc = ".".join(str(part) for part in item.get("loc", [])) or "<root>"
        parts.append(f"{loc}: {item.get('msg', 'invalid')}")
    return "; ".join(parts)


class CodexExecutor:
    def __init__(self, model: str) -> None:
        self.model = model

    def _run_codex(self, prompt: str) -> str:
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
        return output

    def _parse_command(self, output: str) -> AgentCommand:
        data = normalize_command_object(extract_json_object(output))
        return AgentCommand.model_validate(data)

    def run_step(self, prompt: str) -> AgentCommand:
        output = self._run_codex(prompt)
        try:
            return self._parse_command(output)
        except (ValueError, ValidationError) as first_error:
            if isinstance(first_error, ValidationError):
                detail = validation_error_summary(first_error)
            else:
                detail = str(first_error)
            repair_prompt = (
                f"{prompt}\n\n"
                "Your previous response could not be parsed as a valid tool call.\n"
                f"Schema error: {detail}\n"
                "Return exactly one valid JSON object using only the listed schema fields. "
                "Do not explain the correction."
            )
            repair_output = self._run_codex(repair_prompt)
            try:
                return self._parse_command(repair_output)
            except (ValueError, ValidationError):
                return AgentCommand(
                    tool="answer",
                    outcome="OUTCOME_ERR_INTERNAL",
                    message="Executor returned an invalid command schema.",
                    reason=(
                        "Command validation failed after one repair attempt; returning "
                        "a benchmark-visible failure instead of crashing."
                    ),
                )
