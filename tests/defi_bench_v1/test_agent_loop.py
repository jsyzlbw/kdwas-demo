from pathlib import Path

from src.defi_bench_v1.agent_adapters import ScriptedAgent
from src.defi_bench_v1.agent_loop import run_agent_on_task
from src.defi_bench_v1.agents import ReferenceAgent
from src.defi_bench_v1.dataset import load_dataset
from src.defi_bench_v1.types import AgentContext, ToolCall, ToolObservation


DATASET_ROOT = Path("data/defi_bench_v1")


def test_reference_agent_emits_one_tool_call_per_turn_then_final():
    task = next(
        item for item in load_dataset(DATASET_ROOT).tasks
        if item.task_id == "aave_v3_l1_001"
    )
    agent = ReferenceAgent()
    agent.bind_task(task)
    context = AgentContext(
        task_id=task.task_id,
        protocol=task.protocol,
        user_request=task.public["user_request"],
        available_tools=task.public["available_tools"],
        policy=task.policy,
        initial_observation=task.public["initial_observation"],
    )

    first = agent.next_call(context)
    second = agent.next_call(
        AgentContext(
            task_id=context.task_id,
            protocol=context.protocol,
            user_request=context.user_request,
            available_tools=context.available_tools,
            policy=context.policy,
            initial_observation=context.initial_observation,
            history=[
                ToolObservation(first.tool, "success", {"tx_status": "success"}, None),
            ],
        )
    )
    final = agent.next_call(
        AgentContext(
            task_id=context.task_id,
            protocol=context.protocol,
            user_request=context.user_request,
            available_tools=context.available_tools,
            policy=context.policy,
            initial_observation=context.initial_observation,
            history=[
                ToolObservation(first.tool, "success", {"tx_status": "success"}, None),
                ToolObservation(second.tool, "success", {"tx_status": "success"}, None),
            ],
        )
    )

    assert first.tool == "approve"
    assert second.tool == "supply"
    assert final.tool == "final"


def test_agent_loop_records_calls_and_observations():
    task = next(
        item for item in load_dataset(DATASET_ROOT).tasks
        if item.task_id == "aave_v3_l1_001"
    )
    agent = ReferenceAgent()

    result = run_agent_on_task(agent, task, run_index=1)

    assert result.safe_task_success is True
    assert result.action_count == 2
    assert result.trajectory[0]["tool"] == "approve"
    assert result.trajectory[0]["status"] == "success"
    assert "observation" in result.trajectory[0]


def test_scripted_agent_can_run_through_common_loop():
    task = next(
        item for item in load_dataset(DATASET_ROOT).tasks
        if item.task_id == "aave_v3_l1_001"
    )
    agent = ScriptedAgent(
        name="scripted",
        calls=[
            ToolCall("approve", {"token": "WETH", "spender": "aave_pool", "amount": "1"}),
            ToolCall("supply", {"asset": "WETH", "amount": "1"}),
        ],
    )

    result = run_agent_on_task(agent, task, run_index=1)

    assert result.agent == "scripted"
    assert result.safe_task_success is True
