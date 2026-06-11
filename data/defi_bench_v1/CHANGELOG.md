# DeFi Bench v1 Changelog

## v1.0.0 - 2026-06-08

- Created isolated dataset directory under `data/defi_bench_v1/`.
- Added 6 protocol sandboxes.
- Added 72 task blueprints split into Agent-visible tasks and evaluator-only gold annotations.
- Added task-specific `scenarios.jsonl` files for hidden initial wallet positions.
- Each protocol contains 4 L1, 4 L2, and 4 L3 tasks.
- Added deterministic local utility computation for 13 optimization tasks.
- Added task overview generation for human review.
- Dataset remains isolated from the existing pilot experiment under `data/tasks/`.
- Frozen as DeFi Bench v1.0.0.

Freeze rule:

- Do not modify generated `tasks.jsonl`, `gold.jsonl`, or `scenarios.jsonl` by hand.
- Change `scripts/generate_dataset.py` or `scripts/compute_candidate_utilities.py`, regenerate, and rerun validation.
- Any future task/content changes must create a new version entry.
