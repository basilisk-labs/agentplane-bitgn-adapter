from __future__ import annotations

import json
from typing import Any

from google.protobuf.json_format import MessageToDict

from .models import AgentCommand


def _json_message(value: Any) -> str:
    try:
        return json.dumps(MessageToDict(value), indent=2, sort_keys=True)
    except Exception:
        return str(value)


class RuntimeSession:
    def dispatch(self, command: AgentCommand) -> tuple[str, bool]:
        raise NotImplementedError


def preferred_path(command: AgentCommand) -> str:
    path = command.path or command.root or "/"
    return normalize_workspace_path(path)


def normalize_workspace_path(path: str) -> str:
    if not path:
        return path
    if path.startswith("/Users/") or path.startswith("/tmp/") or path.startswith("/private/"):
        for marker in (
            "/00_inbox/",
            "/01_capture/",
            "/02_distill/",
            "/03_publish/",
            "/90_memory/",
            "/99_process/",
        ):
            index = path.find(marker)
            if index >= 0:
                return path[index:]
        return "/"
    return path


def batch_result(items: list[dict[str, str]]) -> str:
    return json.dumps({"items": items}, indent=2, sort_keys=True)


class SandboxSession(RuntimeSession):
    def __init__(self, harness_url: str) -> None:
        from bitgn.vm.mini_connect import MiniRuntimeClientSync

        self.vm = MiniRuntimeClientSync(harness_url)

    def dispatch(self, command: AgentCommand) -> tuple[str, bool]:
        from bitgn.vm.mini_pb2 import (
            AnswerRequest,
            DeleteRequest,
            ListRequest,
            OutlineRequest,
            ReadRequest,
            SearchRequest,
            WriteRequest,
        )

        if command.tool in {"tree", "outline"}:
            result = self.vm.outline(OutlineRequest(path=preferred_path(command)))
            return _json_message(result), False
        if command.tool == "search":
            return _json_message(
                self.vm.search(
                    SearchRequest(
                        path=command.path or command.root or "/",
                        pattern=command.pattern,
                        count=command.limit,
                    )
                )
            ), False
        if command.tool == "list":
            return _json_message(
                self.vm.list(ListRequest(path=normalize_workspace_path(command.path or "/")))
            ), False
        if command.tool == "read":
            return _json_message(
                self.vm.read(ReadRequest(path=normalize_workspace_path(command.path)))
            ), False
        if command.tool == "write":
            return _json_message(
                self.vm.write(
                    WriteRequest(
                        path=normalize_workspace_path(command.path),
                        content=command.content,
                    )
                )
            ), False
        if command.tool == "delete":
            return _json_message(
                self.vm.delete(DeleteRequest(path=normalize_workspace_path(command.path)))
            ), False
        if command.tool == "delete_many":
            items = []
            for path in command.paths:
                normalized = normalize_workspace_path(path)
                self.vm.delete(DeleteRequest(path=normalized))
                items.append({"path": normalized, "status": "deleted"})
            return batch_result(items), False
        if command.tool == "answer":
            return _json_message(
                self.vm.answer(AnswerRequest(answer=command.message, refs=command.refs))
            ), True
        raise ValueError(f"Tool {command.tool} is not supported by sandbox runtime.")


class PcmSession(RuntimeSession):
    def __init__(self, harness_url: str) -> None:
        from bitgn.vm.pcm_connect import PcmRuntimeClientSync

        self.vm = PcmRuntimeClientSync(harness_url)

    def dispatch(self, command: AgentCommand) -> tuple[str, bool]:
        from bitgn.vm.pcm_pb2 import (
            AnswerRequest,
            ContextRequest,
            DeleteRequest,
            FindRequest,
            ListRequest,
            MkDirRequest,
            MoveRequest,
            Outcome,
            ReadRequest,
            SearchRequest,
            TreeRequest,
            WriteRequest,
        )

        outcomes = {
            "OUTCOME_OK": Outcome.OUTCOME_OK,
            "OUTCOME_DENIED_SECURITY": Outcome.OUTCOME_DENIED_SECURITY,
            "OUTCOME_NONE_CLARIFICATION": Outcome.OUTCOME_NONE_CLARIFICATION,
            "OUTCOME_NONE_UNSUPPORTED": Outcome.OUTCOME_NONE_UNSUPPORTED,
            "OUTCOME_ERR_INTERNAL": Outcome.OUTCOME_ERR_INTERNAL,
        }
        if command.tool == "context":
            return _json_message(self.vm.context(ContextRequest())), False
        if command.tool == "tree":
            result = self.vm.tree(TreeRequest(root=preferred_path(command), level=command.level))
            return _json_message(result), False
        if command.tool == "find":
            return _json_message(
                self.vm.find(
                    FindRequest(
                        root=preferred_path(command),
                        name=command.name,
                        limit=command.limit,
                    )
                )
            ), False
        if command.tool == "search":
            return _json_message(
                self.vm.search(
                    SearchRequest(
                        root=preferred_path(command),
                        pattern=command.pattern,
                        limit=command.limit,
                    )
                )
            ), False
        if command.tool == "list":
            return _json_message(
                self.vm.list(ListRequest(name=normalize_workspace_path(command.path)))
            ), False
        if command.tool == "read":
            return _json_message(
                self.vm.read(
                    ReadRequest(
                        path=normalize_workspace_path(command.path),
                        start_line=command.start_line,
                        end_line=command.end_line,
                    )
                )
            ), False
        if command.tool == "write":
            result = self.vm.write(
                WriteRequest(path=normalize_workspace_path(command.path), content=command.content)
            )
            return _json_message(result), False
        if command.tool == "delete":
            return _json_message(
                self.vm.delete(DeleteRequest(path=normalize_workspace_path(command.path)))
            ), False
        if command.tool == "delete_many":
            items = []
            for path in command.paths:
                normalized = normalize_workspace_path(path)
                self.vm.delete(DeleteRequest(path=normalized))
                items.append({"path": normalized, "status": "deleted"})
            return batch_result(items), False
        if command.tool == "mkdir":
            return _json_message(
                self.vm.mk_dir(MkDirRequest(path=normalize_workspace_path(command.path)))
            ), False
        if command.tool == "move":
            return _json_message(
                self.vm.move(
                    MoveRequest(
                        from_name=normalize_workspace_path(command.from_name),
                        to_name=normalize_workspace_path(command.to_name),
                    )
                )
            ), False
        if command.tool == "answer":
            return _json_message(
                self.vm.answer(
                    AnswerRequest(
                        message=command.message,
                        outcome=outcomes[command.outcome],
                        refs=command.refs,
                    )
                )
            ), True
        raise ValueError(f"Tool {command.tool} is not supported by PCM runtime.")


class EcomSession(RuntimeSession):
    def __init__(self, harness_url: str) -> None:
        from bitgn.vm.ecom.ecom_connect import EcomRuntimeClientSync

        self.vm = EcomRuntimeClientSync(harness_url)

    def dispatch(self, command: AgentCommand) -> tuple[str, bool]:
        from bitgn.vm.ecom.ecom_pb2 import (
            AnswerRequest,
            ContextRequest,
            DeleteRequest,
            ExecRequest,
            FindRequest,
            ListRequest,
            NodeKind,
            Outcome,
            ReadRequest,
            SearchRequest,
            StatRequest,
            TreeRequest,
            WriteRequest,
        )

        outcomes = {
            "OUTCOME_OK": Outcome.OUTCOME_OK,
            "OUTCOME_DENIED_SECURITY": Outcome.OUTCOME_DENIED_SECURITY,
            "OUTCOME_NONE_CLARIFICATION": Outcome.OUTCOME_NONE_CLARIFICATION,
            "OUTCOME_NONE_UNSUPPORTED": Outcome.OUTCOME_NONE_UNSUPPORTED,
            "OUTCOME_ERR_INTERNAL": Outcome.OUTCOME_ERR_INTERNAL,
        }
        if command.tool == "context":
            return _json_message(self.vm.context(ContextRequest())), False
        if command.tool == "tree":
            result = self.vm.tree(TreeRequest(root=preferred_path(command), level=command.level))
            return _json_message(result), False
        if command.tool == "find":
            return _json_message(
                self.vm.find(
                    FindRequest(
                        root=preferred_path(command),
                        name=command.name,
                        kind=NodeKind.NODE_KIND_UNSPECIFIED,
                        limit=command.limit,
                    )
                )
            ), False
        if command.tool == "search":
            return _json_message(
                self.vm.search(
                    SearchRequest(
                        root=preferred_path(command),
                        pattern=command.pattern,
                        limit=command.limit,
                    )
                )
            ), False
        if command.tool == "list":
            return _json_message(
                self.vm.list(ListRequest(path=normalize_workspace_path(command.path)))
            ), False
        if command.tool == "read":
            return _json_message(
                self.vm.read(
                    ReadRequest(
                        path=normalize_workspace_path(command.path),
                        start_line=command.start_line,
                        end_line=command.end_line,
                    )
                )
            ), False
        if command.tool == "write":
            result = self.vm.write(
                WriteRequest(path=normalize_workspace_path(command.path), content=command.content)
            )
            return _json_message(result), False
        if command.tool == "delete":
            return _json_message(
                self.vm.delete(DeleteRequest(path=normalize_workspace_path(command.path)))
            ), False
        if command.tool == "delete_many":
            items = []
            for path in command.paths:
                normalized = normalize_workspace_path(path)
                self.vm.delete(DeleteRequest(path=normalized))
                items.append({"path": normalized, "status": "deleted"})
            return batch_result(items), False
        if command.tool == "stat":
            return _json_message(
                self.vm.stat(StatRequest(path=normalize_workspace_path(command.path)))
            ), False
        if command.tool == "exec":
            return _json_message(
                self.vm.exec(
                    ExecRequest(path=command.path, args=command.args, stdin=command.stdin)
                )
            ), False
        if command.tool == "answer":
            return _json_message(
                self.vm.answer(
                    AnswerRequest(
                        message=command.message,
                        outcome=outcomes[command.outcome],
                        refs=command.refs,
                    )
                )
            ), True
        raise ValueError(f"Tool {command.tool} is not supported by ECOM runtime.")


def create_runtime_session(runtime: str, harness_url: str) -> RuntimeSession:
    if runtime == "sandbox":
        return SandboxSession(harness_url)
    if runtime == "pcm":
        return PcmSession(harness_url)
    if runtime == "ecom":
        return EcomSession(harness_url)
    raise ValueError(f"Unsupported runtime: {runtime}")
