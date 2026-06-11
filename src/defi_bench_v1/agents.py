from __future__ import annotations

from typing import Any

from .dataset import TaskBundle
from .evaluator import TaskResult, evaluate_actions
from .types import AgentContext, ToolCall


class ReferenceAgent:
    name = "reference"

    def __init__(self) -> None:
        self._actions_by_task: dict[str, list[ToolCall]] = {}

    def bind_task(self, task: TaskBundle) -> None:
        self._actions_by_task[task.task_id] = [
            ToolCall(item["tool"], item.get("args", {}))
            for item in task.gold["reference_actions"]
        ]

    def plan(self, task: TaskBundle) -> list[dict[str, Any]]:
        return task.gold["reference_actions"]

    def next_call(self, context: AgentContext) -> ToolCall:
        actions = self._actions_by_task[context.task_id]
        if len(context.history) >= len(actions):
            return ToolCall("final", {"answer": "done"})
        return actions[len(context.history)]

    def run_task(self, task: TaskBundle, run_index: int = 1) -> TaskResult:
        return evaluate_actions(
            task,
            self.plan(task),
            agent_name=self.name,
            run_index=run_index,
        )
