from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TaskBundle:
    task_id: str
    protocol: str
    public: dict[str, Any]
    gold: dict[str, Any]
    scenario: dict[str, Any]
    tools: dict[str, Any]
    policy: str


@dataclass(frozen=True)
class Dataset:
    root: Path
    manifest: dict[str, Any]
    tasks: list[TaskBundle]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_dataset(root: Path | str) -> Dataset:
    dataset_root = Path(root)
    manifest = load_json(dataset_root / "manifest.json")
    tasks: list[TaskBundle] = []

    for protocol in manifest["protocols"]:
        env_dir = dataset_root / "envs" / protocol
        public_rows = load_jsonl(env_dir / "tasks.jsonl")
        gold_by_id = {row["task_id"]: row for row in load_jsonl(env_dir / "gold.jsonl")}
        scenario_by_id = {row["task_id"]: row for row in load_jsonl(env_dir / "scenarios.jsonl")}
        tools = load_json(env_dir / "tools.json")
        policy = (env_dir / "policy.md").read_text(encoding="utf-8")

        for public in public_rows:
            task_id = public["task_id"]
            tasks.append(
                TaskBundle(
                    task_id=task_id,
                    protocol=protocol,
                    public=public,
                    gold=gold_by_id[task_id],
                    scenario=scenario_by_id[task_id],
                    tools=tools,
                    policy=policy,
                )
            )

    return Dataset(root=dataset_root, manifest=manifest, tasks=tasks)
