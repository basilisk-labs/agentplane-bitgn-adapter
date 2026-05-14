from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import PurePosixPath

from .models import AgentCommand
from .runtime import normalize_workspace_path


@dataclass
class KnowledgeCaptureState:
    source_paths: set[str] = field(default_factory=set)
    retired_sources: set[str] = field(default_factory=set)
    capture_paths: set[str] = field(default_factory=set)
    card_paths: set[str] = field(default_factory=set)
    thread_paths: set[str] = field(default_factory=set)
    thread_card_links: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class PlaybookRoute:
    blueprint: str
    playbook: str
    required_states: tuple[str, ...]
    match_reasons: tuple[str, ...]


GENERIC_ROUTE = PlaybookRoute(
    blueprint="runner.execution",
    playbook="verify_then_answer",
    required_states=("answer_outcome_selected",),
    match_reasons=(),
)

KNOWLEDGE_CAPTURE_ROUTE = PlaybookRoute(
    blueprint="context.assimilation",
    playbook="knowledge_capture_pipeline",
    required_states=(
        "source_read",
        "capture_artifact_exists",
        "distill_card_exists",
        "distill_card_canonical_name",
        "retrieval_index_updated",
        "thread_links_card",
        "source_retired",
    ),
    match_reasons=("knowledge filesystem signals",),
)


def route_for_instruction(instruction: str, runtime: str) -> PlaybookRoute:
    if runtime == "pcm" and is_knowledge_capture_candidate(instruction, []):
        return KNOWLEDGE_CAPTURE_ROUTE
    return GENERIC_ROUTE


def state_as_dict(state: KnowledgeCaptureState) -> dict[str, list[str]]:
    return {key: sorted(value) for key, value in asdict(state).items()}


def is_knowledge_capture_candidate(instruction: str, commands: list[AgentCommand]) -> bool:
    del commands
    text = instruction.lower()
    signal_count = sum(
        1
        for signal in ("00_inbox", "01_capture", "02_distill", "capture", "distill", "thread")
        if signal in text
    )
    return signal_count >= 2


def knowledge_capture_state(commands: list[AgentCommand]) -> KnowledgeCaptureState:
    state = KnowledgeCaptureState()
    for command in commands:
        path = normalize_workspace_path(command.path)
        if path.startswith("/00_inbox/") or path.startswith("00_inbox/"):
            state.source_paths.add(path.lstrip("/"))
            if command.tool == "delete":
                state.retired_sources.add(path.lstrip("/"))
        if command.tool == "delete_many":
            for item in command.paths:
                normalized = normalize_workspace_path(item).lstrip("/")
                if normalized.startswith("00_inbox/"):
                    state.source_paths.add(normalized)
                    state.retired_sources.add(normalized)
        if command.tool == "move":
            source = normalize_workspace_path(command.from_name).lstrip("/")
            target = normalize_workspace_path(command.to_name).lstrip("/")
            if source.startswith("00_inbox/"):
                state.source_paths.add(source)
                state.retired_sources.add(source)
            if target.startswith("00_inbox/"):
                state.source_paths.add(target)
        if command.tool == "write":
            normalized = path.lstrip("/")
            if normalized.startswith("01_capture/"):
                state.capture_paths.add(normalized)
            if normalized.startswith("02_distill/cards/"):
                state.card_paths.add(normalized)
            if normalized.startswith("02_distill/threads/"):
                state.thread_paths.add(normalized)
                for card_path in state.card_paths:
                    card_name = PurePosixPath(card_path).name
                    if card_path in command.content or card_name in command.content:
                        state.thread_card_links.add(card_path)
    return state


def missing_knowledge_capture_state(
    instruction: str,
    commands: list[AgentCommand],
) -> list[str]:
    if not is_knowledge_capture_candidate(instruction, commands):
        return []
    state = knowledge_capture_state(commands)
    missing: list[str] = []
    if state.source_paths and not state.source_paths.issubset(state.retired_sources):
        remaining = sorted(state.source_paths - state.retired_sources)
        missing.append(f"source_retired: delete or move processed inbox source(s): {remaining}")
    if "capture" in instruction.lower() and not state.capture_paths:
        missing.append("capture_artifact_exists: write the capture artifact under 01_capture/")
    if "distill" in instruction.lower() and not state.card_paths:
        missing.append("distill_card_exists: write the distill card under 02_distill/cards/")
    for source_path in sorted(state.source_paths):
        source_name = PurePosixPath(source_path).name
        if state.card_paths and not any(
            PurePosixPath(card_path).name == source_name for card_path in state.card_paths
        ):
            missing.append(
                "distill_card_canonical_name: write the distill card with the same basename "
                f"as source {source_name!r} unless policy explicitly requires a different id"
            )
    if (state.capture_paths or state.card_paths) and not state.thread_paths:
        missing.append(
            "retrieval_index_updated: update the relevant file under 02_distill/threads/ "
            "with a link or reference to the distill card"
        )
    if state.card_paths and state.thread_paths and not state.thread_card_links:
        missing.append(
            "thread_links_card: thread update must reference the distill card path or basename"
        )
    return missing


def final_answer_blocker(
    *,
    instruction: str,
    commands: list[AgentCommand],
    command: AgentCommand,
) -> str | None:
    if command.tool != "answer":
        return None
    missing = missing_knowledge_capture_state(instruction, commands)
    is_capture = is_knowledge_capture_candidate(instruction, commands)
    if not is_capture:
        return None
    if not missing and command.outcome == "OUTCOME_OK":
        return None
    if not missing:
        missing = [
            "outcome_ok_required: this playbook reached its required observable state; "
            "answer with OUTCOME_OK unless a policy/security blocker was observed"
        ]
    return json.dumps(
        {
            "final_verifier": "blocked",
            "playbook": "knowledge_capture_pipeline",
            "blocked_outcome": command.outcome,
            "missing": missing,
            "observed_state": state_as_dict(knowledge_capture_state(commands)),
            "next_action": (
                "Do not finish with this outcome yet. Perform the missing runtime actions "
                "when listed, verify the resulting paths with read/tree/search, then answer "
                "with the outcome required by the verified state."
            ),
        },
        indent=2,
        sort_keys=True,
    )
