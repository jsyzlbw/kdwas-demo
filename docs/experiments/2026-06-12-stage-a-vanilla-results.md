# 2026-06-12 Stage A Vanilla Agent Results

## Setup

- Agent: `vanilla`
- Model provider: JD SaaS OpenAI-compatible API
- Model: `qwen3.6-plus`
- Dataset: `defi_bench_v1`
- Dataset version: `1.0.0`
- Scope: one L1 task per protocol
- Repeats: `1`
- Max steps: `6`
- Runtime: deterministic local DeFi sandbox

Environment overrides used for the successful Stage A runs:

```bash
DEFI_VANILLA_TIMEOUT_S=35
DEFI_VANILLA_MAX_TOKENS=512
```

## Task Set

| Protocol | Task ID |
|---|---|
| Uniswap V3 | `uniswap_v3_l1_001` |
| Aave V3 | `aave_v3_l1_001` |
| Maker / Sky | `maker_sky_l1_001` |
| Lido | `lido_l1_001` |
| Pendle | `pendle_l1_001` |
| GMX | `gmx_l1_001` |

## Results

| Protocol | Task ID | Safe Success | Action Count | Failure Reasons | Run Directory |
|---|---|---:|---:|---|---|
| Uniswap V3 | `uniswap_v3_l1_001` | 1 | 3 | - | `runs_defi/stage_a/20260612T063454Z` |
| Aave V3 | `aave_v3_l1_001` | 1 | 4 | - | `runs_defi/stage_a/20260612T063629Z` |
| Maker / Sky | `maker_sky_l1_001` | 1 | 2 | - | `runs_defi/stage_a/20260612T063754Z` |
| Lido | `lido_l1_001` | 1 | 2 | - | `runs_defi/stage_a/20260612T063813Z` |
| Pendle | `pendle_l1_001` | 1 | 5 | - | `runs_defi/stage_a/20260612T063853Z` |
| GMX | `gmx_l1_001` | 1 | 4 | - | `runs_defi/stage_a/20260612T063944Z` |

Aggregate:

```text
tasks = 6
safe_task_success = 6 / 6
stage_a_success_rate = 1.0
```

## Notes

An initial batch run over all six tasks was interrupted because JD API responses were slow and the default `max_steps=20` made the smoke test too long. The runtime was updated to support:

```bash
--max-steps
DEFI_VANILLA_TIMEOUT_S
DEFI_VANILLA_MAX_TOKENS
```

The successful Stage A run was then executed one protocol at a time with `max_steps=6`.

One evaluator issue was also fixed before the final Stage A run: write-task scoring now allows extra read-only tool calls before the required write actions. This matches the benchmark design because read tools are the Agent's way to inspect state.

## Conclusion

Stage A passed. The vanilla JD Qwen agent is connected to the Python tool-use runtime and can complete one L1 task for each of the six protocols.

Recommended next step: Stage B, using one L1, one L2, and one L3 task per protocol.
