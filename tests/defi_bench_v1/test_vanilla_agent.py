import json
from pathlib import Path

from src.defi_bench_v1.agent_loop import run_agent_on_task
from src.defi_bench_v1.dataset import load_dataset
from src.defi_bench_v1.evaluator import evaluate_actions
from src.defi_bench_v1.llm_agents import (
    VanillaLLMAgent,
    build_vanilla_prompt,
    parse_tool_call,
)
from src.defi_bench_v1.runner import build_agents, load_dotenv, run_experiment
from src.defi_bench_v1.types import ToolCall


DATASET_ROOT = Path("data/defi_bench_v1")


class FakeChatClient:
    def __init__(self, outputs):
        self.outputs = list(outputs)
        self.calls = []
        self.model = "fake-qwen"

    def chat(self, system: str, user: str):
        self.calls.append({"system": system, "user": user})
        text = self.outputs.pop(0)
        return type("FakeResponse", (), {"text": text})()


def aave_l1_task():
    return next(
        item for item in load_dataset(DATASET_ROOT).tasks
        if item.task_id == "aave_v3_l1_001"
    )


def test_parse_tool_call_accepts_plain_json():
    call = parse_tool_call('{"tool":"final","args":{"answer":"done"}}')

    assert call == ToolCall("final", {"answer": "done"})


def test_parse_tool_call_accepts_markdown_json_block():
    call = parse_tool_call(
        '```json\n{"tool":"get_wallet_balance","args":{"token":"WETH"}}\n```'
    )

    assert call == ToolCall("get_wallet_balance", {"token": "WETH"})


def test_parse_tool_call_returns_invalid_call_for_bad_output():
    call = parse_tool_call("I cannot decide.")

    assert call.tool == "invalid_tool_call"
    assert call.args["raw"] == "I cannot decide."


def test_vanilla_prompt_contains_public_context_only():
    task = aave_l1_task()
    prompt = build_vanilla_prompt(
        task=task,
        context=type(
            "Context",
            (),
            {
                "task_id": task.task_id,
                "protocol": task.protocol,
                "user_request": task.public["user_request"],
                "available_tools": task.public["available_tools"],
                "policy": task.policy,
                "initial_observation": task.public["initial_observation"],
                "history": [],
            },
        )(),
    )

    assert task.public["user_request"] in prompt
    assert "aave_pool" in prompt
    assert "reference_actions" not in prompt
    assert "success_conditions" not in prompt
    assert "gold" not in prompt.lower()


def test_vanilla_agent_runs_through_common_loop_with_fake_client():
    task = aave_l1_task()
    fake_client = FakeChatClient(
        [
            json.dumps({
                "tool": "approve",
                "args": {"token": "WETH", "spender": "aave_pool", "amount": "1"},
            }),
            json.dumps({
                "tool": "supply",
                "args": {"asset": "WETH", "amount": "1"},
            }),
            json.dumps({"tool": "final", "args": {"answer": "done"}}),
        ]
    )
    agent = VanillaLLMAgent(client=fake_client)

    result = run_agent_on_task(agent, task, run_index=1)

    assert result.agent == "vanilla"
    assert result.safe_task_success is True
    assert len(fake_client.calls) == 3
    assert result.trajectory[0]["observation"]["tx_status"] == "success"


def test_load_dotenv_sets_jd_api_key(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("JD_API_KEY=abc123\n", encoding="utf-8")
    monkeypatch.delenv("JD_API_KEY", raising=False)

    load_dotenv(env_file)

    assert __import__("os").environ["JD_API_KEY"] == "abc123"


def test_runner_builds_vanilla_agent(monkeypatch):
    monkeypatch.setenv("JD_API_KEY", "fake-key")

    agents = build_agents(["vanilla"])

    assert len(agents) == 1
    assert agents[0].name == "vanilla"


def test_vanilla_agent_reads_experiment_env(monkeypatch):
    monkeypatch.setenv("JD_API_KEY", "fake-key")
    monkeypatch.setenv("DEFI_VANILLA_TIMEOUT_S", "17")
    monkeypatch.setenv("DEFI_VANILLA_MAX_TOKENS", "256")
    monkeypatch.setenv("DEFI_VANILLA_TEMPERATURE", "0.3")

    agent = VanillaLLMAgent()

    assert agent.client.timeout_s == 17
    assert agent.client.max_tokens == 256
    assert agent.client.temperature == 0.3


def test_vanilla_agent_converts_client_error_to_tool_call():
    class FailingClient:
        model = "failing"

        def chat(self, system, user):
            raise TimeoutError("read timed out")

    task = aave_l1_task()
    agent = VanillaLLMAgent(client=FailingClient())
    agent.bind_task(task)

    call = agent.next_call(
        type(
            "Context",
            (),
            {
                "task_id": task.task_id,
                "protocol": task.protocol,
                "user_request": task.public["user_request"],
                "available_tools": task.public["available_tools"],
                "policy": task.policy,
                "initial_observation": task.public["initial_observation"],
                "history": [],
            },
        )()
    )

    assert call.tool == "llm_error"
    assert "read timed out" in call.args["error"]


def test_run_experiment_can_filter_task_ids(tmp_path):
    task_id = "aave_v3_l1_001"

    summary = run_experiment(
        dataset_root=DATASET_ROOT,
        output_root=tmp_path / "runs_defi",
        agents=[FakeReferenceAgent()],
        repeats=1,
        task_ids=[task_id],
    )

    assert summary["agents"]["fake_reference"]["task_count"] == 1


def test_run_experiment_passes_max_steps(tmp_path):
    task_id = "aave_v3_l1_001"

    summary = run_experiment(
        dataset_root=DATASET_ROOT,
        output_root=tmp_path / "runs_defi",
        agents=[FakeReferenceAgent()],
        repeats=1,
        task_ids=[task_id],
        max_steps=1,
    )

    assert summary["agents"]["fake_reference"]["safe_task_success_rate"] == 0.0


class FakeReferenceAgent:
    name = "fake_reference"

    def bind_task(self, task):
        self.calls = [
            ToolCall(item["tool"], item.get("args", {}))
            for item in task.gold["reference_actions"]
        ]

    def next_call(self, context):
        if len(context.history) >= len(self.calls):
            return ToolCall("final", {"answer": "done"})
        return self.calls[len(context.history)]


def test_evaluator_allows_extra_read_tools_before_required_writes():
    task = aave_l1_task()

    result = evaluate_actions(
        task,
        [
            {"tool": "get_wallet_balance", "args": {"token": "WETH"}},
            {"tool": "get_allowance", "args": {"token": "WETH", "spender": "aave_pool"}},
            {"tool": "approve", "args": {"token": "WETH", "spender": "aave_pool", "amount": "1"}},
            {"tool": "supply", "args": {"asset": "WETH", "amount": "1"}},
        ],
        agent_name="vanilla",
        run_index=1,
    )

    assert result.safe_task_success is True
