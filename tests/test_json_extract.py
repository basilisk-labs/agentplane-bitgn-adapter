from agentplane_bitgn_adapter.json_extract import extract_json_object


def test_extracts_last_json_object_from_noisy_output() -> None:
    data = extract_json_object('noise {"tool":"read"} more {"tool":"answer","message":"ok"}')
    assert data == {"tool": "answer", "message": "ok"}


def test_raises_when_no_json_object_exists() -> None:
    try:
        extract_json_object("no json here")
    except ValueError as exc:
        assert "No JSON object" in str(exc)
    else:
        raise AssertionError("expected ValueError")
