from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


ToolStatus = Literal["success", "revert"]


@dataclass(frozen=True)
class ToolCall:
    tool: str
    args: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolObservation:
    tool: str
    status: ToolStatus
    observation: dict[str, Any]
    error: str | None = None

    def to_json(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentContext:
    task_id: str
    protocol: str
    user_request: str
    available_tools: list[str]
    policy: str
    initial_observation: dict[str, Any]
    history: list[ToolObservation] = field(default_factory=list)

    def to_json(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "protocol": self.protocol,
            "user_request": self.user_request,
            "available_tools": self.available_tools,
            "policy": self.policy,
            "initial_observation": self.initial_observation,
            "history": [item.to_json() for item in self.history],
        }


@dataclass(frozen=True)
class TrajectoryStep:
    step: int
    call: ToolCall
    observation: ToolObservation

    def to_json(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "tool": self.call.tool,
            "args": self.call.args,
            "status": self.observation.status,
            "observation": self.observation.observation,
            "error": self.observation.error,
        }
