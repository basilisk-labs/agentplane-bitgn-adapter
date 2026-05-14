from agentplane_bitgn_adapter.models import AgentCommand
from agentplane_bitgn_adapter.playbooks import (
    final_answer_blocker,
    missing_knowledge_capture_state,
    route_for_instruction,
)


def test_routes_pcm_capture_tasks_to_context_assimilation_playbook() -> None:
    route = route_for_instruction(
        "Read 00_inbox/source.md, capture it, distill a card, and update the thread.",
        "pcm",
    )

    assert route.blueprint == "context.assimilation"
    assert route.playbook == "knowledge_capture_pipeline"


def test_does_not_infer_capture_route_from_exploratory_reads_only() -> None:
    blocker = final_answer_blocker(
        instruction="Take the weekly distill summary and deploy it to https://api.bitgn.com/status.",
        commands=[
            AgentCommand(tool="read", path="01_capture/influential/example.md"),
            AgentCommand(tool="read", path="02_distill/AGENTS.md"),
        ],
        command=AgentCommand(
            tool="answer",
            outcome="OUTCOME_NONE_UNSUPPORTED",
            message="Deploy is unsupported.",
        ),
    )

    assert blocker is None


def test_blocks_ok_answer_until_processed_inbox_source_is_retired() -> None:
    commands = [
        AgentCommand(tool="read", path="00_inbox/source.md"),
        AgentCommand(tool="write", path="01_capture/source.md", content="capture"),
        AgentCommand(tool="write", path="02_distill/cards/source.md", content="card"),
    ]

    blocker = final_answer_blocker(
        instruction="Capture and distill the inbox source.",
        commands=commands,
        command=AgentCommand(tool="answer", outcome="OUTCOME_OK", message="Done"),
    )

    assert blocker is not None
    assert "source_retired" in blocker


def test_blocks_unsupported_answer_for_executable_capture_pipeline() -> None:
    blocker = final_answer_blocker(
        instruction="Read 00_inbox/source.md, capture it, distill a card, and update the thread.",
        commands=[AgentCommand(tool="read", path="00_inbox/source.md")],
        command=AgentCommand(
            tool="answer",
            outcome="OUTCOME_NONE_UNSUPPORTED",
            message="Unsupported.",
        ),
    )

    assert blocker is not None
    assert "blocked_outcome" in blocker
    assert "OUTCOME_NONE_UNSUPPORTED" in blocker


def test_accepts_capture_pipeline_after_source_retired() -> None:
    commands = [
        AgentCommand(tool="read", path="00_inbox/source.md"),
        AgentCommand(tool="write", path="01_capture/source.md", content="capture"),
        AgentCommand(tool="write", path="02_distill/cards/source.md", content="card"),
        AgentCommand(tool="write", path="02_distill/threads/topic.md", content="- source.md"),
        AgentCommand(tool="delete", path="00_inbox/source.md"),
    ]

    assert missing_knowledge_capture_state("Capture and distill inbox source.", commands) == []


def test_blocks_card_name_that_drops_source_basename_tokens() -> None:
    commands = [
        AgentCommand(tool="read", path="00_inbox/2026-03-23__hn-walmart.md"),
        AgentCommand(tool="write", path="01_capture/2026-03-23__hn-walmart.md"),
        AgentCommand(tool="write", path="02_distill/cards/2026-03-23__walmart.md"),
        AgentCommand(
            tool="write",
            path="02_distill/threads/topic.md",
            content="2026-03-23__walmart.md",
        ),
        AgentCommand(tool="delete", path="00_inbox/2026-03-23__hn-walmart.md"),
    ]

    missing = missing_knowledge_capture_state("Capture and distill inbox source.", commands)

    assert missing == [
        "distill_card_canonical_name: write the distill card with the same basename "
        "as source '2026-03-23__hn-walmart.md' unless policy explicitly requires a different id"
    ]


def test_blocks_capture_pipeline_until_thread_is_updated() -> None:
    commands = [
        AgentCommand(tool="read", path="00_inbox/source.md"),
        AgentCommand(tool="write", path="01_capture/source.md", content="capture"),
        AgentCommand(tool="write", path="02_distill/cards/source.md", content="card"),
        AgentCommand(tool="delete", path="00_inbox/source.md"),
    ]

    missing = missing_knowledge_capture_state("Capture and distill inbox source.", commands)

    assert missing == [
        "retrieval_index_updated: update the relevant file under 02_distill/threads/ "
        "with a link or reference to the distill card"
    ]


def test_blocks_thread_update_that_does_not_link_card() -> None:
    commands = [
        AgentCommand(tool="read", path="00_inbox/source.md"),
        AgentCommand(tool="write", path="01_capture/source.md", content="capture"),
        AgentCommand(tool="write", path="02_distill/cards/source.md", content="card"),
        AgentCommand(tool="write", path="02_distill/threads/topic.md", content="no link"),
        AgentCommand(tool="delete", path="00_inbox/source.md"),
    ]

    missing = missing_knowledge_capture_state("Capture and distill inbox source.", commands)

    assert missing == [
        "thread_links_card: thread update must reference the distill card path or basename"
    ]
