from __future__ import annotations

from pathlib import Path

from .codex_executor import CodexExecutor
from .models import AdapterConfig, AgentCommand
from .playbooks import (
    final_answer_blocker,
    knowledge_capture_state,
    route_for_instruction,
    state_as_dict,
)
from .prompt import GENERIC_POLICY, render_step_prompt
from .proof import ProofRecorder
from .runtime import create_runtime_session


def safe_component(value: str) -> str:
    return "".join(char if char.isalnum() or char in "-_." else "_" for char in value)


def bootstrap_commands(runtime: str) -> list[AgentCommand]:
    if runtime == "sandbox":
        return [
            AgentCommand(tool="tree", path="/", reason="Initial sandbox outline."),
            AgentCommand(tool="read", path="AGENTS.MD", reason="Load sandbox policy."),
        ]
    if runtime == "pcm":
        return [
            AgentCommand(tool="tree", root="/", level=2, reason="Initial PCM tree."),
            AgentCommand(tool="read", path="AGENTS.md", reason="Load PCM policy."),
            AgentCommand(tool="context", reason="Load PCM runtime context."),
        ]
    if runtime == "ecom":
        return [
            AgentCommand(tool="tree", root="/", level=2, reason="Initial ECOM tree."),
            AgentCommand(tool="read", path="/AGENTS.MD", reason="Load ECOM policy."),
            AgentCommand(tool="exec", path="/bin/date", reason="Capture runtime date."),
            AgentCommand(tool="exec", path="/bin/id", reason="Capture runtime identity."),
        ]
    return []


def run_agent(
    *,
    config: AdapterConfig,
    harness_url: str,
    instruction: str,
    task_id: str,
    trial_id: str,
) -> None:
    artifact_dir = (
        Path(config.artifact_dir)
        / safe_component(config.benchmark_id)
        / config.runtime
        / safe_component(task_id)
        / safe_component(trial_id)
    )
    proof = ProofRecorder(artifact_dir=artifact_dir)
    route = route_for_instruction(instruction, config.runtime)
    proof.start(
        {
            "adapter": "agentplane-bitgn-adapter",
            "runtime": config.runtime,
            "model": config.model,
            "task_id": task_id,
            "trial_id": trial_id,
            "instruction_preview": instruction[:1000],
            "blueprint": route.blueprint,
            "playbook": route.playbook,
            "required_states": list(route.required_states),
            "route_match_reasons": list(route.match_reasons),
        }
    )
    (artifact_dir / "AGENTS.md").write_text(GENERIC_POLICY + "\n", encoding="utf-8")

    runtime = create_runtime_session(config.runtime, harness_url)
    executor = CodexExecutor(config.model)
    transcript: list[dict[str, str]] = [{"role": "instruction", "content": instruction}]
    commands: list[AgentCommand] = []

    for index, command in enumerate(bootstrap_commands(config.runtime), start=1):
        try:
            observation, _ = runtime.dispatch(command)
        except Exception as exc:
            observation = f"ERROR: {type(exc).__name__}: {exc}"
        proof.record("bootstrap_command", step=index, command=command.model_dump())
        proof.record("bootstrap_observation", step=index, observation=observation[:4000])
        print(f"bootstrap {index}: {command.tool} {command.path or command.root}", flush=True)
        transcript.append({"role": "bootstrap_command", "content": command.model_dump_json()})
        transcript.append({"role": "observation", "content": observation})

    for step in range(1, config.max_steps + 1):
        prompt = render_step_prompt(
            benchmark_instruction=instruction,
            transcript=transcript,
            runtime=config.runtime,
            step=step,
        )
        command = executor.run_step(prompt)
        print(f"step {step}: {command.tool} {command.path or command.root}", flush=True)
        proof.record("command", step=step, command=command.model_dump())
        blocker = final_answer_blocker(
            instruction=instruction,
            commands=commands,
            command=command,
        )
        if blocker:
            transcript.append({"role": "assistant_command", "content": command.model_dump_json()})
            transcript.append({"role": "observation", "content": blocker})
            proof.record("observation", step=step, done=False, observation=blocker[:4000])
            proof.record(
                "execution_state",
                step=step,
                state=state_as_dict(knowledge_capture_state(commands)),
            )
            continue
        try:
            observation, done = runtime.dispatch(command)
        except Exception as exc:
            observation = f"ERROR: {type(exc).__name__}: {exc}"
            done = False
        commands.append(command)
        proof.record(
            "execution_state",
            step=step,
            state=state_as_dict(knowledge_capture_state(commands)),
        )
        transcript.append({"role": "assistant_command", "content": command.model_dump_json()})
        transcript.append({"role": "observation", "content": observation})
        proof.record("observation", step=step, done=done, observation=observation[:4000])
        if done:
            proof.finish(status="answered", steps=step)
            return

    fallback = AgentCommand(
        tool="answer",
        message="Reached the adapter step limit before a confident completion.",
        outcome="OUTCOME_NONE_UNSUPPORTED",
        refs=[],
        reason=(
            "The adapter reached max_steps without a verified completion; report unsupported "
            "instead of crashing or claiming success."
        ),
    )
    proof.record("command", step=config.max_steps + 1, command=fallback.model_dump())
    try:
        observation, _ = runtime.dispatch(fallback)
    except Exception as exc:
        observation = f"ERROR: {type(exc).__name__}: {exc}"
    proof.record(
        "observation",
        step=config.max_steps + 1,
        done=True,
        observation=observation[:4000],
    )
    proof.finish(status="max_steps_exhausted", steps=config.max_steps)
