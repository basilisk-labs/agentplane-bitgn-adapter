from agentplane_bitgn_adapter.prompt import render_step_prompt


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
