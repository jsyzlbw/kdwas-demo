# 2026-06-12 Stage B Vanilla Agent Results

## Setup

- Agent: `vanilla`
- Model provider: JD SaaS OpenAI-compatible API
- Model: `qwen3.6-plus`
- Dataset: `defi_bench_v1`
- Dataset version: `1.0.0`
- Scope: one L1, one L2, and one L3 task per protocol
- Tasks: `18`
- Repeats: `1`
- Max steps: `8`
- Runtime: deterministic local DeFi sandbox

Environment overrides:

```bash
DEFI_VANILLA_TIMEOUT_S=35
DEFI_VANILLA_MAX_TOKENS=512
```

Raw summaries:

```text
runs_defi/stage_b_summary.jsonl
runs_defi/stage_b_retry_summary.jsonl
```

## Why Retry Was Needed

The first Stage B run completed many tasks but several harder tasks exited with JD API `ReadTimeout`. This is an infrastructure/model-call failure mode, not a dataset validation failure.

The runtime was then improved so LLM client exceptions are converted into a tool call:

```text
ToolCall("llm_error", {"error_type": "...", "error": "..."})
```

This lets the evaluator record a failed trajectory instead of crashing the whole run. The timeout tasks were then retried and recorded as normal failed task runs.

## Aggregate Result

```text
tasks = 18
safe_success = 11 / 18
stage_b_success_rate = 0.611
```

By difficulty:

| Difficulty | Success | Total | Rate |
|---|---:|---:|---:|
| L1 | 6 | 6 | 1.000 |
| L2 | 5 | 6 | 0.833 |
| L3 | 0 | 6 | 0.000 |

By protocol:

| Protocol | Success | Total | Rate |
|---|---:|---:|---:|
| Uniswap V3 | 1 | 3 | 0.333 |
| Aave V3 | 2 | 3 | 0.667 |
| Maker / Sky | 2 | 3 | 0.667 |
| Lido | 2 | 3 | 0.667 |
| Pendle | 2 | 3 | 0.667 |
| GMX | 2 | 3 | 0.667 |

## Task-Level Result

| Protocol | Difficulty | Task ID | Safe Success | Action Count | Failure Reasons |
|---|---|---|---:|---:|---|
| Uniswap V3 | L1 | `uniswap_v3_l1_001` | 1 | 3 | - |
| Uniswap V3 | L2 | `uniswap_v3_l2_001` | 0 | 2 | `unknown_tools:llm_error`, `revert_detected`, `reference_actions_mismatch` |
| Uniswap V3 | L3 | `uniswap_v3_l3_001` | 0 | 5 | `unknown_tools:llm_error`, `revert_detected`, `reference_actions_mismatch` |
| Aave V3 | L1 | `aave_v3_l1_001` | 1 | 4 | - |
| Aave V3 | L2 | `aave_v3_l2_001` | 1 | 3 | - |
| Aave V3 | L3 | `aave_v3_l3_001` | 0 | 2 | `unknown_tools:llm_error`, `revert_detected`, `reference_actions_mismatch` |
| Maker / Sky | L1 | `maker_sky_l1_001` | 1 | 2 | - |
| Maker / Sky | L2 | `maker_sky_l2_001` | 1 | 3 | - |
| Maker / Sky | L3 | `maker_sky_l3_001` | 0 | 2 | `unknown_tools:llm_error`, `revert_detected`, `reference_actions_mismatch` |
| Lido | L1 | `lido_l1_001` | 1 | 2 | - |
| Lido | L2 | `lido_l2_001` | 1 | 3 | - |
| Lido | L3 | `lido_l3_001` | 0 | 2 | `unknown_tools:llm_error`, `revert_detected`, `reference_actions_mismatch` |
| Pendle | L1 | `pendle_l1_001` | 1 | 4 | - |
| Pendle | L2 | `pendle_l2_001` | 1 | 3 | - |
| Pendle | L3 | `pendle_l3_001` | 0 | 7 | `unknown_tools:llm_error`, `revert_detected`, `reference_actions_mismatch` |
| GMX | L1 | `gmx_l1_001` | 1 | 4 | - |
| GMX | L2 | `gmx_l2_001` | 1 | 3 | - |
| GMX | L3 | `gmx_l3_001` | 0 | 1 | `unknown_tools:llm_error`, `revert_detected`, `reference_actions_mismatch` |

## Interpretation

Stage B shows a clear difficulty gradient:

```text
L1: 6/6
L2: 5/6
L3: 0/6
```

This is useful for the experiment design. It means the benchmark is not trivially easy for the vanilla agent. The simple tasks are solvable, most medium tasks are solvable, and risk-heavy L3 tasks currently fail under the vanilla setup.

The dominant observed failure mode in failed tasks is:

```text
llm_error caused by JD API read timeout
```

This should be treated separately from pure reasoning failure. For formal baseline runs, we should decide whether to:

1. keep `DEFI_VANILLA_TIMEOUT_S=35` and count timeout as a real operational failure;
2. increase timeout for L3 tasks;
3. reduce prompt size or max tokens;
4. add one retry at the agent-call level.

## Conclusion

Stage B completed. The vanilla agent is usable as a baseline, and the benchmark shows meaningful separation by difficulty.

Recommended next step before Stage C:

```text
Run a small L3-only retry with a longer timeout, e.g. DEFI_VANILLA_TIMEOUT_S=90, to distinguish API latency from model reasoning failure.
```

Do not tune protocol-specific prompts for vanilla. If timeout handling is changed, record it as an experiment configuration change.
