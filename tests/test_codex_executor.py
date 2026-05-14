from types import SimpleNamespace

from agentplane_bitgn_adapter.codex_executor import CodexExecutor, normalize_command_object


def test_normalizes_final_answer_shape_without_tool() -> None:
    data = normalize_command_object(
        {
            "outcome": "OUTCOME_OK",
            "message": "Done",
            "refs": ["AGENTS.md"],
        }
    )
    assert data["tool"] == "answer"
    assert data["message"] == "Done"


def test_unwraps_nested_function_shape() -> None:
    data = normalize_command_object({"function": {"tool": "read", "path": "AGENTS.md"}})
    assert data == {"tool": "read", "path": "AGENTS.md"}


def test_executor_repairs_invalid_schema_once(monkeypatch) -> None:
    calls: list[list[str]] = []
    outputs = iter(
        [
            '{"tool": "read", "refs": "AGENTS.md"}',
            '{"tool": "read", "path": "AGENTS.md"}',
        ]
    )

    def fake_run(args, check, text, capture_output):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout=next(outputs), stderr="")

    monkeypatch.setattr("subprocess.run", fake_run)

    command = CodexExecutor("test-model").run_step("prompt")

    assert command.tool == "read"
    assert command.path == "AGENTS.md"
    assert len(calls) == 2
    assert "Schema error:" in calls[1][-1]
