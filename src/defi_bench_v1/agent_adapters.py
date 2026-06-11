from __future__ import annotations

from .dataset import TaskBundle
from .types import AgentContext, ToolCall


class ScriptedAgent:
    def __init__(self, name: str, calls: list[ToolCall]):
        self.name = name
        self.calls = calls

    def bind_task(self, task: TaskBundle) -> None:
        return None

    def next_call(self, context: AgentContext) -> ToolCall:
        if len(context.history) >= len(self.calls):
            return ToolCall("final", {"answer": "done"})
        return self.calls[len(context.history)]
