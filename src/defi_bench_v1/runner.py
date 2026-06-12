from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from .agent_loop import run_agent_on_task
from .agents import ReferenceAgent
from .dataset import load_dataset
from .evaluator import TaskResult
from .llm_agents import VanillaLLMAgent
from .metrics import aggregate_agent_metrics


ROOT = Path(__file__).resolve().parents[2]


def json_dump(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def jsonl_dump(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def run_experiment(
    *,
    dataset_root: Path | str,
    output_root: Path | str,
    agents: list,
    repeats: int = 3,
    task_ids: list[str] | None = None,
    max_steps: int = 20,
) -> dict:
    dataset = load_dataset(dataset_root)
    tasks = dataset.tasks
    if task_ids is not None:
        requested = set(task_ids)
        tasks = [task for task in tasks if task.task_id in requested]
        found = {task.task_id for task in tasks}
        missing = sorted(requested - found)
        if missing:
            raise ValueError(f"Unknown DeFi Bench v1 task ids: {', '.join(missing)}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path(output_root) / timestamp
    run_dir.mkdir(parents=True, exist_ok=False)

    all_results: list[TaskResult] = []
    for agent in agents:
        for run_index in range(1, repeats + 1):
            for task in tasks:
                all_results.append(
                    run_agent_on_task(
                        agent,
                        task,
                        run_index=run_index,
                        max_steps=max_steps,
                    )
                )

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
            "task_ids": task_ids,
            "max_steps": max_steps,
        },
    )
    jsonl_dump(run_dir / "results.jsonl", result_rows)
    json_dump(run_dir / "metrics.json", metrics)
    return metrics


def build_agents(agent_names: list[str]) -> list[ReferenceAgent]:
    agents: list = []
    for name in agent_names:
        if name == "reference":
            agents.append(ReferenceAgent())
        elif name == "vanilla":
            agents.append(VanillaLLMAgent())
        else:
            raise ValueError(f"Unsupported DeFi Bench v1 agent: {name}")
    return agents


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the isolated DeFi Bench v1 experiment.")
    parser.add_argument("--dataset-root", default="data/defi_bench_v1")
    parser.add_argument("--output-root", default="runs_defi")
    parser.add_argument("--agents", default="reference")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--max-steps", type=int, default=20)
    parser.add_argument(
        "--task-ids",
        default="",
        help="Optional comma-separated task ids for smoke or subset runs.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    load_dotenv(ROOT / ".env")
    args = parse_args(argv)
    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")
    if args.max_steps < 1:
        raise SystemExit("--max-steps must be >= 1")

    agent_names = [name.strip() for name in args.agents.split(",") if name.strip()]
    task_ids = [item.strip() for item in args.task_ids.split(",") if item.strip()] or None
    metrics = run_experiment(
        dataset_root=Path(args.dataset_root),
        output_root=Path(args.output_root),
        agents=build_agents(agent_names),
        repeats=args.repeats,
        task_ids=task_ids,
        max_steps=args.max_steps,
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
