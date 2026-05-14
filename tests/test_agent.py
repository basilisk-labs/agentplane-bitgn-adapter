from agentplane_bitgn_adapter.agent import bootstrap_commands, safe_component
from agentplane_bitgn_adapter.models import AgentCommand
from agentplane_bitgn_adapter.runtime import normalize_workspace_path, preferred_path


def test_sandbox_bootstrap_loads_agents_md() -> None:
    commands = bootstrap_commands("sandbox")
    assert [command.tool for command in commands] == ["tree", "read"]
    assert commands[1].path == "AGENTS.MD"


def test_ecom_bootstrap_loads_policy_and_runtime_identity() -> None:
    commands = bootstrap_commands("ecom")
    assert commands[0].root == "/"
    assert [command.path for command in commands[1:]] == ["/AGENTS.MD", "/bin/date", "/bin/id"]


def test_safe_component_keeps_artifact_paths_flat() -> None:
    assert safe_component("bitgn/pac1-dev") == "bitgn_pac1-dev"


def test_preferred_path_rejects_host_paths() -> None:
    command = AgentCommand(tool="tree", path="/Users/example/project")
    assert preferred_path(command) == "/"


def test_normalize_workspace_path_preserves_known_runtime_suffix() -> None:
    assert (
        normalize_workspace_path(
            "/Users/example/project/02_distill/cards/2026-03-23__walmart.md"
        )
        == "/02_distill/cards/2026-03-23__walmart.md"
    )
