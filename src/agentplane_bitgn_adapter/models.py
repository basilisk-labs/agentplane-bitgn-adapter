from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

OutcomeName = Literal[
    "OUTCOME_OK",
    "OUTCOME_DENIED_SECURITY",
    "OUTCOME_NONE_CLARIFICATION",
    "OUTCOME_NONE_UNSUPPORTED",
    "OUTCOME_ERR_INTERNAL",
]

ToolName = Literal[
    "context",
    "tree",
    "outline",
    "find",
    "search",
    "list",
    "read",
    "write",
    "delete",
    "mkdir",
    "move",
    "stat",
    "exec",
    "answer",
]


class AgentCommand(BaseModel):
    tool: ToolName
    current_state: str = ""
    reason: str = ""
    path: str = ""
    root: str = "/"
    name: str = ""
    pattern: str = ""
    content: str = ""
    start_line: int = 0
    end_line: int = 0
    level: int = 2
    limit: int = 10
    from_name: str = ""
    to_name: str = ""
    args: list[str] = Field(default_factory=list)
    stdin: str = ""
    message: str = ""
    refs: list[str] = Field(default_factory=list)
    outcome: OutcomeName = "OUTCOME_OK"


class TrialResult(BaseModel):
    task_id: str
    trial_id: str
    score_available: bool = False
    score: float | None = None
    score_detail: list[str] = Field(default_factory=list)


class AdapterConfig(BaseModel):
    host: str = "https://api.bitgn.com"
    benchmark_id: str = "bitgn/pac1-dev"
    bitgn_api_key: str = ""
    runtime: Literal["sandbox", "pcm", "ecom"] = "pcm"
    model: str = "gpt-5.4"
    run_name: str = "AgentPlane BitGN Codex"
    max_steps: int = 30
    artifact_dir: str = ".agentplane-bitgn"
