from __future__ import annotations

from typing import Protocol

from .dataset import TaskBundle
from .evaluator import TaskResult, evaluate_actions
from .tool_runtime import ProtocolSandbox
from .types import AgentContext, ToolCall, ToolObservation, TrajectoryStep


class StepwiseAgent(Protocol):
    name: str

    def bind_task(self, task: TaskBundle) -> None:
        ...

    def next_call(self, context: AgentContext) -> ToolCall:
        ...


def make_context(task: TaskBundle, history: list[ToolObservation]) -> AgentContext:
    return AgentContext(
        task_id=task.task_id,
        protocol=task.protocol,
        user_request=task.public["user_request"],
        available_tools=task.public["available_tools"],
        policy=task.policy,
        initial_observation=task.public["initial_observation"],
        history=history,
    )


def run_agent_on_task(
    agent: StepwiseAgent,
    task: TaskBundle,
    *,
    run_index: int,
    max_steps: int = 20,
) -> TaskResult:
    agent.bind_task(task)
    sandbox = ProtocolSandbox(task)
    history: list[ToolObservation] = []
    trajectory: list[TrajectoryStep] = []

    for step_number in range(1, max_steps + 1):
        call = agent.next_call(make_context(task, history))
        observation = sandbox.execute(call)

        if call.tool == "final":
            break

        history.append(observation)
        trajectory.append(TrajectoryStep(step_number, call, observation))

        if observation.status == "revert":
            break

    actions = [step.call.to_json() for step in trajectory]
    return evaluate_actions(
        task,
        actions,
        agent_name=agent.name,
        run_index=run_index,
        trajectory=[step.to_json() for step in trajectory],
    )
