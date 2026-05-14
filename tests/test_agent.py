from agentplane_bitgn_adapter.agent import bootstrap_commands, safe_component


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
