# DeFi Bench v1 Dataset

This directory contains an isolated DeFi Wallet Agent benchmark dataset. It is separate from the existing pilot task set under `data/tasks/`.

The dataset contains 6 single-protocol sandboxes and 72 tasks:

- Uniswap V3
- Aave V3
- Maker / Sky
- Lido
- Pendle
- GMX

Each protocol has 12 tasks: 4 L1, 4 L2, and 4 L3. Agent-visible tasks are stored in `tasks.jsonl`; evaluator-only annotations are stored in `gold.jsonl`; task-specific hidden initial wallet states are stored in `scenarios.jsonl`.

Visibility:

- Agent-visible: `tools.json`, `policy.md`, `tasks.jsonl`
- Evaluator-only: `state.json`, `metadata.json`, `scenarios.jsonl`, `gold.jsonl`

Build commands:

```bash
python3 data/defi_bench_v1/scripts/generate_dataset.py
python3 data/defi_bench_v1/scripts/compute_candidate_utilities.py
python3 data/defi_bench_v1/scripts/validate_dataset.py
python3 data/defi_bench_v1/scripts/generate_task_overview.py
```

Utility notes:

- Utilities are computed only for optimization tasks.
- Utility values are comparable only within the same task.
- Utility values come from the deterministic local simulator, not from mainnet fork execution.
