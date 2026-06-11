from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .agent_loop import run_agent_on_task
from .agents import ReferenceAgent
from .dataset import load_dataset
from .evaluator import TaskResult
from .metrics import aggregate_agent_metrics


def json_dump(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def jsonl_dump(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def run_experiment(
    *,
    dataset_root: Path | str,
    output_root: Path | str,
    agents: list[ReferenceAgent],
    repeats: int = 3,
) -> dict:
    dataset = load_dataset(dataset_root)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(output_root) / timestamp
    run_dir.mkdir(parents=True, exist_ok=False)

    all_results: list[TaskResult] = []
    for agent in agents:
        for run_index in range(1, repeats + 1):
            for task in dataset.tasks:
                all_results.append(run_agent_on_task(agent, task, run_index=run_index))

    result_rows = [result.to_json() for result in all_results]
    metrics = {
        "dataset": dataset.manifest["dataset"],
        "dataset_version": dataset.manifest["version"],
        "repeats": repeats,
        "agents": {},
    }
    for agent in agents:
        agent_results = [result for result in all_results if result.agent == agent.name]
        metrics["agents"][agent.name] = aggregate_agent_metrics(agent_results, repeats)

    json_dump(
        run_dir / "config.json",
        {
            "dataset_root": str(dataset.root),
            "dataset_version": dataset.manifest["version"],
            "agents": [agent.name for agent in agents],
            "repeats": repeats,
        },
    )
    jsonl_dump(run_dir / "results.jsonl", result_rows)
    json_dump(run_dir / "metrics.json", metrics)
    return metrics


def build_agents(agent_names: list[str]) -> list[ReferenceAgent]:
    agents: list[ReferenceAgent] = []
    for name in agent_names:
        if name == "reference":
            agents.append(ReferenceAgent())
        else:
            raise ValueError(f"Unsupported DeFi Bench v1 agent: {name}")
    return agents


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the isolated DeFi Bench v1 experiment.")
    parser.add_argument("--dataset-root", default="data/defi_bench_v1")
    parser.add_argument("--output-root", default="runs_defi")
    parser.add_argument("--agents", default="reference")
    parser.add_argument("--repeats", type=int, default=3)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")

    agent_names = [name.strip() for name in args.agents.split(",") if name.strip()]
    metrics = run_experiment(
        dataset_root=Path(args.dataset_root),
        output_root=Path(args.output_root),
        agents=build_agents(agent_names),
        repeats=args.repeats,
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
