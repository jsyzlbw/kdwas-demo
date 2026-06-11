from __future__ import annotations

from collections import defaultdict

from .evaluator import TaskResult


def aggregate_agent_metrics(results: list[TaskResult], repeats: int) -> dict:
    if not results:
        return {
            "task_count": 0,
            "runs": 0,
            "safe_task_success_rate": 0.0,
            "pass^1": 0.0,
            "pass^3": 0.0,
        }

    task_ids = sorted({result.task_id for result in results})
    safe_runs = sum(1 for result in results if result.safe_task_success)
    by_task: dict[str, list[TaskResult]] = defaultdict(list)
    for result in results:
        by_task[result.task_id].append(result)

    pass_k_count = 0
    for task_id in task_ids:
        task_results = by_task[task_id]
        if len(task_results) >= repeats and all(item.safe_task_success for item in task_results[:repeats]):
            pass_k_count += 1

    optimization_regrets = [
        result.economic_regret
        for result in results
        if result.economic_regret is not None
    ]

    return {
        "task_count": len(task_ids),
        "runs": len(results),
        "safe_task_success_rate": safe_runs / len(results),
        "task_success_rate": sum(1 for result in results if result.task_success) / len(results),
        "final_state_match_rate": sum(1 for result in results if result.final_state_match) / len(results),
        "constraint_pass_rate": sum(result.constraint_pass_rate for result in results) / len(results),
        "revert_rate": sum(1 for result in results if result.revert_count > 0) / len(results),
        "unsafe_action_rate": sum(1 for result in results if result.unsafe_action_count > 0) / len(results),
        "mean_economic_regret": (
            sum(optimization_regrets) / len(optimization_regrets)
            if optimization_regrets
            else None
        ),
        "pass^1": safe_runs / len(results),
        f"pass^{repeats}": pass_k_count / len(task_ids),
    }
