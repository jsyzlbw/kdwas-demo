#!/usr/bin/env python3
"""Validate the isolated DeFi Bench v1 dataset."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PROTOCOLS = ["uniswap_v3", "aave_v3", "maker_sky", "lido", "pendle", "gmx"]
DIFFICULTIES = ["L1", "L2", "L3"]
HIDDEN_FIELD_NAMES = {
    "reference_actions",
    "success_conditions",
    "hard_constraints",
    "forbidden_conditions",
    "economic_regret_config",
    "best_valid_utility",
}
BEST_CANDIDATE_ARG_ALIASES = {
    "fee_tiers": "fee_tier",
    "amount_in": "amount_in",
    "borrow_amounts": "amount",
    "withdraw_amounts": "amount",
    "draw_amounts": "amount",
    "stake_amounts": "amount_eth",
    "markets": "market",
    "size_usd": "size_usd",
}
REQUIRED_POSITION_HINTS = {
    "uniswap_v3": ["existing", "remove the lp", "remove an existing"],
    "aave_v3": ["existing aave debt", "supplied liquidity", "withdrawing", "withdraw", "repay"],
    "maker_sky": ["vault debt", "withdraw", "repay", "liquidation"],
    "lido": ["existing lido withdrawal request"],
    "pendle": ["sell", "existing pendle lp", "remove"],
    "gmx": ["existing", "increase collateral", "decrease", "close the existing", "reduce"],
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise AssertionError(f"{path}:{line_no} is not valid JSON: {exc}") from exc
    return rows


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def schema_validator(name: str) -> Draft202012Validator:
    schema = load_json(ROOT / "schemas" / name)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_with_schema(validator: Draft202012Validator, instance: dict, label: str) -> None:
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        details = "; ".join(f"{'/'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors[:3])
        raise AssertionError(f"{label}: schema validation failed: {details}")


def reference_actions_contain_candidate(reference_actions: list[dict], candidate_id: str) -> bool:
    key, raw_value = candidate_id.split(":", 1)
    arg_name = BEST_CANDIDATE_ARG_ALIASES.get(key)
    if arg_name is None:
        return True
    for action in reference_actions:
        for arg_key, arg_value in action.get("args", {}).items():
            if arg_key == arg_name and str(arg_value) == raw_value:
                return True
    return False


def validate_protocol(protocol: str) -> tuple[list[dict], list[dict], list[dict]]:
    env_dir = ROOT / "envs" / protocol
    require(env_dir.exists(), f"missing env directory: {env_dir}")
    for name in ["state.json", "metadata.json", "tools.json", "policy.md", "tasks.jsonl", "gold.jsonl", "scenarios.jsonl"]:
        require((env_dir / name).exists(), f"missing {protocol}/{name}")

    state = load_json(env_dir / "state.json")
    metadata = load_json(env_dir / "metadata.json")
    tools = load_json(env_dir / "tools.json")
    policy = (env_dir / "policy.md").read_text(encoding="utf-8")
    tasks = load_jsonl(env_dir / "tasks.jsonl")
    gold = load_jsonl(env_dir / "gold.jsonl")
    scenarios = load_jsonl(env_dir / "scenarios.jsonl")

    validators = {
        "state": schema_validator("state.schema.json"),
        "metadata": schema_validator("metadata.schema.json"),
        "tools": schema_validator("tools.schema.json"),
        "task": schema_validator("task.schema.json"),
        "gold": schema_validator("gold.schema.json"),
        "scenario": schema_validator("scenario.schema.json"),
    }
    validate_with_schema(validators["state"], state, f"{protocol}/state.json")
    validate_with_schema(validators["metadata"], metadata, f"{protocol}/metadata.json")
    validate_with_schema(validators["tools"], tools, f"{protocol}/tools.json")
    for row in tasks:
        validate_with_schema(validators["task"], row, f"{protocol}/{row.get('task_id', '<unknown>')}/task")
    for row in gold:
        validate_with_schema(validators["gold"], row, f"{protocol}/{row.get('task_id', '<unknown>')}/gold")
    for row in scenarios:
        validate_with_schema(validators["scenario"], row, f"{protocol}/{row.get('task_id', '<unknown>')}/scenario")

    require(state["protocol"] == protocol, f"{protocol}: state protocol mismatch")
    require(metadata["protocol"] == protocol, f"{protocol}: metadata protocol mismatch")
    require(tools["protocol"] == protocol, f"{protocol}: tools protocol mismatch")

    task_ids = [row["task_id"] for row in tasks]
    gold_ids = [row["task_id"] for row in gold]
    scenario_ids = [row["task_id"] for row in scenarios]
    require(len(task_ids) == 12, f"{protocol}: expected 12 tasks, got {len(task_ids)}")
    require(len(gold_ids) == 12, f"{protocol}: expected 12 gold rows, got {len(gold_ids)}")
    require(len(scenario_ids) == 12, f"{protocol}: expected 12 scenarios, got {len(scenario_ids)}")
    require(len(set(task_ids)) == 12, f"{protocol}: duplicate task ids")
    require(set(task_ids) == set(gold_ids), f"{protocol}: task/gold ids differ")
    require(set(task_ids) == set(scenario_ids), f"{protocol}: task/scenario ids differ")

    difficulty_counts = Counter(row["difficulty"] for row in tasks)
    for difficulty in DIFFICULTIES:
        require(difficulty_counts[difficulty] == 4, f"{protocol}: expected 4 {difficulty}, got {difficulty_counts[difficulty]}")

    available_tool_names = {tool["name"] for tool in tools["tools"]}
    for tool in tools["tools"]:
        require(tool["parameters"].get("properties") is not None, f"{protocol}/{tool['name']}: missing parameter properties")
        require(tool["returns"].get("properties") is not None, f"{protocol}/{tool['name']}: missing return properties")

    require("Hard thresholds:" in policy, f"{protocol}: policy missing hard thresholds")

    scenario_by_id = {row["task_id"]: row for row in scenarios}
    for row in tasks:
        require(row["protocol"] == protocol, f"{row['task_id']}: protocol mismatch")
        require(row["difficulty"] in DIFFICULTIES, f"{row['task_id']}: invalid difficulty")
        require(row["task_type"] in {"deterministic", "optimization"}, f"{row['task_id']}: invalid task_type")
        require("task_parameters" in row and isinstance(row["task_parameters"], dict), f"{row['task_id']}: missing task_parameters")
        require(row["initial_observation"].get("scenario_id") == f"{row['task_id']}_scenario", f"{row['task_id']}: bad scenario_id in initial_observation")
        require(not (HIDDEN_FIELD_NAMES & set(row.keys())), f"{row['task_id']}: hidden field leaked into task")
        require(set(row["available_tools"]).issubset(available_tool_names), f"{row['task_id']}: unknown available tool")
        scenario = scenario_by_id[row["task_id"]]
        require(scenario["scenario_id"] == f"{row['task_id']}_scenario", f"{row['task_id']}: scenario_id mismatch")
        require(scenario["wallet_state"]["wallet_alias"] == row["initial_observation"]["wallet_alias"], f"{row['task_id']}: wallet alias mismatch")
        request = row["user_request"].lower()
        if any(hint in request for hint in REQUIRED_POSITION_HINTS[protocol]):
            require(len(scenario["wallet_state"]["positions"]) > 0, f"{row['task_id']}: request implies existing position but scenario has none")

    task_type_by_id = {row["task_id"]: row["task_type"] for row in tasks}
    task_by_id = {row["task_id"]: row for row in tasks}
    for row in gold:
        require("success_conditions" in row and isinstance(row["success_conditions"], dict), f"{row['task_id']}: missing success_conditions")
        require("hard_constraints" in row and isinstance(row["hard_constraints"], list), f"{row['task_id']}: missing hard_constraints")
        require("forbidden_conditions" in row and isinstance(row["forbidden_conditions"], list), f"{row['task_id']}: missing forbidden_conditions")
        applicable = row["economic_regret_applicable"]
        require(applicable == (task_type_by_id[row["task_id"]] == "optimization"), f"{row['task_id']}: economic_regret_applicable mismatch")
        visible = task_by_id[row["task_id"]]
        if applicable:
            config = row["economic_regret_config"]
            require(isinstance(config, dict), f"{row['task_id']}: optimization task missing regret config")
            require("candidate_space" in config, f"{row['task_id']}: missing candidate_space")
            require("best_valid_utility" in config, f"{row['task_id']}: missing best_valid_utility")
            require("candidate_evaluations" in config, f"{row['task_id']}: missing candidate_evaluations")
            require("best_candidate_id" in config, f"{row['task_id']}: missing best_candidate_id")
            require("utility_formula" in config, f"{row['task_id']}: missing utility_formula")
            require("utility_provenance" in config, f"{row['task_id']}: missing utility_provenance")
            provenance = config["utility_provenance"]
            require(provenance.get("source") == "deterministic_local_simulator", f"{row['task_id']}: utility source is not deterministic_local_simulator")
            require(provenance.get("formula") == config["utility_formula"], f"{row['task_id']}: utility formula provenance mismatch")
            require(provenance.get("source") not in {"manual", "placeholder"}, f"{row['task_id']}: placeholder utility source is forbidden")
            valid_candidates = [item for item in config["candidate_evaluations"] if item["valid"]]
            require(valid_candidates, f"{row['task_id']}: no valid candidates")
            require(any(item["candidate_id"] == config["best_candidate_id"] for item in valid_candidates), f"{row['task_id']}: best candidate not valid")
            best = max(valid_candidates, key=lambda item: item["utility"])
            require(best["candidate_id"] == config["best_candidate_id"], f"{row['task_id']}: best_candidate_id is not max utility")
            require(best["utility"] == config["best_valid_utility"], f"{row['task_id']}: best_valid_utility is not max utility")
            require(reference_actions_contain_candidate(row["reference_actions"], config["best_candidate_id"]), f"{row['task_id']}: reference_actions do not contain best candidate")
            for item in config["candidate_evaluations"]:
                require("metrics" in item and isinstance(item["metrics"], dict), f"{row['task_id']}/{item['candidate_id']}: missing metrics")
                if item["valid"]:
                    require(item["utility"] is not None, f"{row['task_id']}/{item['candidate_id']}: valid candidate missing utility")
                else:
                    require(item["utility"] is None, f"{row['task_id']}/{item['candidate_id']}: invalid candidate should have null utility")
            require(visible["task_parameters"].get("candidate_space") == config["candidate_space"], f"{row['task_id']}: visible candidate_space mismatch")
        else:
            require(row["economic_regret_config"] is None, f"{row['task_id']}: deterministic task should not have regret config")
            require("required_action_parameters" in visible["task_parameters"], f"{row['task_id']}: deterministic task missing visible required_action_parameters")

    return tasks, gold, scenarios


def main() -> None:
    manifest = load_json(ROOT / "manifest.json")
    require(manifest["dataset"] == "defi_bench_v1", "manifest dataset mismatch")
    require(manifest["protocols"] == PROTOCOLS, "manifest protocol order mismatch")

    all_tasks = []
    all_gold = []
    all_scenarios = []
    for protocol in PROTOCOLS:
        tasks, gold, scenarios = validate_protocol(protocol)
        all_tasks.extend(tasks)
        all_gold.extend(gold)
        all_scenarios.extend(scenarios)

    require(len(all_tasks) == 72, f"expected 72 tasks, got {len(all_tasks)}")
    require(len(all_gold) == 72, f"expected 72 gold rows, got {len(all_gold)}")
    require(len(all_scenarios) == 72, f"expected 72 scenarios, got {len(all_scenarios)}")
    require(manifest["total_tasks"] == 72, "manifest total_tasks mismatch")
    require(manifest["total_scenarios"] == 72, "manifest total_scenarios mismatch")

    difficulty_counts = Counter(row["difficulty"] for row in all_tasks)
    require(dict(difficulty_counts) == {"L1": 24, "L2": 24, "L3": 24}, f"bad difficulty counts: {dict(difficulty_counts)}")

    optimization_count = sum(1 for row in all_tasks if row["task_type"] == "optimization")
    deterministic_count = sum(1 for row in all_tasks if row["task_type"] == "deterministic")
    print("OK: DeFi Bench v1 dataset is valid")
    print(f"tasks={len(all_tasks)} scenarios={len(all_scenarios)} deterministic={deterministic_count} optimization={optimization_count}")
    print(f"difficulty_counts={dict(difficulty_counts)}")


if __name__ == "__main__":
    main()
