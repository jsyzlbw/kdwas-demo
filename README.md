# DeFi Bench v1 Standalone Bundle

This repository contains the files for the independent DeFi Bench v1 experiment extracted from the KDWAS repository.

## Contents

```text
data/defi_bench_v1/                         Frozen dataset, schemas, policies, scripts
src/defi_bench_v1/                          Independent runtime, tool-use loop, evaluator
tests/defi_bench_v1/                        Focused tests for DeFi Bench v1
docs/superpowers/plans/2026-06-10-...md     Implementation plan for Python tool-use runtime
defi_agent_benchmark_sandbox_design.md      Experiment design document
```

## Validation Commands

Run from this repository root:

```bash
python3 -m pytest tests/defi_bench_v1 -q

python3 data/defi_bench_v1/scripts/generate_dataset.py \
  && python3 data/defi_bench_v1/scripts/compute_candidate_utilities.py \
  && python3 data/defi_bench_v1/scripts/validate_dataset.py \
  && python3 data/defi_bench_v1/scripts/generate_task_overview.py
```

## Notes

- This bundle intentionally excludes local experiment outputs such as `runs_defi/`.
- This bundle does not include the old KDWAS task set under `data/tasks/`.
- The runtime is a deterministic local sandbox, not a mainnet fork.
