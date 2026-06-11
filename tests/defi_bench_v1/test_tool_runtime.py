from pathlib import Path

from src.defi_bench_v1.dataset import load_dataset
from src.defi_bench_v1.tool_runtime import ProtocolSandbox
from src.defi_bench_v1.types import AgentContext, ToolCall, ToolObservation


DATASET_ROOT = Path("data/defi_bench_v1")


def test_tool_use_types_round_trip_to_json():
    call = ToolCall(tool="get_wallet_balance", args={"token": "USDC"})
    observation = ToolObservation(
        tool="get_wallet_balance",
        status="success",
        observation={"balance": "10000"},
        error=None,
    )
    context = AgentContext(
        task_id="aave_v3_l1_001",
        protocol="aave_v3",
        user_request="Supply exactly 1 WETH to Aave V3.",
        available_tools=["get_wallet_balance"],
        policy="Never use unsupported assets.",
        initial_observation={"wallet_alias": "wallet_aave_v3_001"},
        history=[observation],
    )

    assert call.to_json() == {
        "tool": "get_wallet_balance",
        "args": {"token": "USDC"},
    }
    assert observation.to_json()["status"] == "success"
    assert context.to_json()["task_id"] == "aave_v3_l1_001"


def test_sandbox_executes_read_tool_from_wallet_state():
    task = load_dataset(DATASET_ROOT).tasks[0]
    sandbox = ProtocolSandbox(task)

    result = sandbox.execute(ToolCall("get_wallet_balance", {"token": "WETH"}))

    assert result.status == "success"
    assert result.observation["balance"] == "2"


def test_sandbox_executes_approve_and_updates_allowance():
    task = load_dataset(DATASET_ROOT).tasks[0]
    sandbox = ProtocolSandbox(task)

    result = sandbox.execute(
        ToolCall("approve", {"token": "WETH", "spender": "aave_pool", "amount": "1"})
    )

    assert result.status == "success"
    assert result.observation["tx_status"] == "success"
    assert sandbox.wallet_state["allowances"]["WETH"]["aave_pool"] == "1"


def test_sandbox_reverts_unknown_tool():
    task = load_dataset(DATASET_ROOT).tasks[0]
    sandbox = ProtocolSandbox(task)

    result = sandbox.execute(ToolCall("not_a_tool", {}))

    assert result.status == "revert"
    assert result.error == "unknown_tool:not_a_tool"
