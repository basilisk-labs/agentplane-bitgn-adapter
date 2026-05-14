from agentplane_bitgn_adapter.agent import bootstrap_commands


def test_sandbox_bootstrap_loads_agents_md() -> None:
    commands = bootstrap_commands("sandbox")
    assert [command.tool for command in commands] == ["tree", "read"]
    assert commands[1].path == "AGENTS.MD"


def test_ecom_bootstrap_loads_policy_and_runtime_identity() -> None:
    commands = bootstrap_commands("ecom")
    assert commands[0].root == "/"
    assert [command.path for command in commands[1:]] == ["/AGENTS.MD", "/bin/date", "/bin/id"]
