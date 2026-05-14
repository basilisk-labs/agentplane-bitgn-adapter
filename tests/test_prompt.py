from agentplane_bitgn_adapter.prompt import (
    allowed_tool_contract,
    render_step_prompt,
    runtime_hints,
)


def test_prompt_contains_runtime_instruction_and_json_contract() -> None:
    prompt = render_step_prompt(
        benchmark_instruction="Find the invoice.",
        transcript=[{"role": "observation", "content": "AGENTS.md says stay safe."}],
        runtime="pcm",
        step=2,
    )
    assert "Runtime: pcm" in prompt
    assert "Find the invoice." in prompt
    assert "Respond with exactly one JSON object" in prompt
    assert "OUTCOME_DENIED_SECURITY" in prompt


def test_pcm_tool_contract_excludes_exec() -> None:
    contract = allowed_tool_contract("pcm")
    assert "Do not use exec" in contract["tool"]
    assert "delete_many" in contract["tool"]


def test_ecom_tool_contract_allows_exec() -> None:
    contract = allowed_tool_contract("ecom")
    assert "exec" in contract["tool"]
    assert "stdin" in contract


def test_pcm_hints_include_capture_pipeline_completion() -> None:
    hints = runtime_hints("pcm")
    assert "write the distilled card" in hints
    assert "update the relevant 02_distill/threads" in hints
