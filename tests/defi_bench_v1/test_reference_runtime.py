import json
import subprocess
import sys
from pathlib import Path

from src.defi_bench_v1.agents import ReferenceAgent
from src.defi_bench_v1.dataset import load_dataset
from src.defi_bench_v1.runner import run_experiment


DATASET_ROOT = Path("data/defi_bench_v1")


def test_dataset_loader_keeps_evaluator_fields_out_of_agent_view():
    dataset = load_dataset(DATASET_ROOT)

    assert len(dataset.tasks) == 72
    first = dataset.tasks[0]

    assert first.public["task_id"] == first.task_id
    assert "reference_actions" not in first.public
    assert "success_conditions" not in first.public
    assert "hard_constraints" not in first.public
    assert first.gold["task_id"] == first.task_id
    assert first.scenario["task_id"] == first.task_id


def test_reference_agent_safely_completes_all_frozen_tasks():
    dataset = load_dataset(DATASET_ROOT)
    agent = ReferenceAgent()

    results = [agent.run_task(task) for task in dataset.tasks]

    assert len(results) == 72
    assert all(result.safe_task_success for result in results)
    assert all(result.revert_count == 0 for result in results)
    assert all(result.unsafe_action_count == 0 for result in results)

    optimization_results = [result for result in results if result.economic_regret is not None]
    assert len(optimization_results) == 13
    assert all(result.economic_regret == 0 for result in optimization_results)


def test_experiment_runner_writes_isolated_outputs_and_pass3(tmp_path):
    run_dir = tmp_path / "runs_defi"

    summary = run_experiment(
        dataset_root=DATASET_ROOT,
        output_root=run_dir,
        agents=[ReferenceAgent()],
        repeats=3,
    )

    assert summary["agents"]["reference"]["task_count"] == 72
    assert summary["agents"]["reference"]["runs"] == 216
    assert summary["agents"]["reference"]["safe_task_success_rate"] == 1.0
    assert summary["agents"]["reference"]["pass^1"] == 1.0
    assert summary["agents"]["reference"]["pass^3"] == 1.0

    created_runs = list(run_dir.iterdir())
    assert len(created_runs) == 1
    assert (created_runs[0] / "config.json").exists()
    assert (created_runs[0] / "results.jsonl").exists()
    assert (created_runs[0] / "metrics.json").exists()

    result_rows = [
        json.loads(line)
        for line in (created_runs[0] / "results.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert "observation" in result_rows[0]["trajectory"][0]


def test_runner_cli_uses_defi_output_root(tmp_path):
    run_dir = tmp_path / "runs_defi_cli"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.defi_bench_v1.runner",
            "--dataset-root",
            str(DATASET_ROOT),
            "--output-root",
            str(run_dir),
            "--agents",
            "reference",
            "--repeats",
            "1",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    summary = json.loads(completed.stdout)
    assert summary["agents"]["reference"]["runs"] == 72
    assert summary["agents"]["reference"]["pass^1"] == 1.0
    assert len(list(run_dir.iterdir())) == 1
