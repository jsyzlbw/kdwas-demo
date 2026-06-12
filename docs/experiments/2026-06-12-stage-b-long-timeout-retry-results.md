# 2026-06-12 Stage B Long-Timeout Retry Results

## Purpose

Stage B 初始结果中，7 条任务失败时出现 `llm_error`，日志显示主要是 JD API `ReadTimeout`：

```text
HTTPSConnectionPool(host='agentrs.jd.com', port=443): Read timed out. (read timeout=35)
```

因此不能直接判断这些失败是模型能力问题，还是 API timeout 问题。

本次 retry 的目的：

```text
大幅延长 timeout，重跑所有出现 llm_error 的任务，
区分 API latency 和模型实际任务失败。
```

## Retry Setup

重跑任务：

```text
uniswap_v3_l2_001
uniswap_v3_l3_001
aave_v3_l3_001
maker_sky_l3_001
lido_l3_001
pendle_l3_001
gmx_l3_001
```

配置：

```bash
DEFI_VANILLA_TIMEOUT_S=120
DEFI_VANILLA_MAX_TOKENS=512
--max-steps 8
--repeats 1
```

执行方式：

```text
2 路并发
每个任务独立 output_root
```

结果文件：

```text
runs_defi/stage_b_long_timeout_summary.jsonl
```

## Result Summary

| Task ID | Difficulty | Safe Success | Action Count | Failure Reasons | Elapsed |
|---|---|---:|---:|---|---:|
| `uniswap_v3_l2_001` | L2 | 0 | 3 | `reference_actions_mismatch` | 106.94s |
| `uniswap_v3_l3_001` | L3 | 0 | 7 | `reference_actions_mismatch` | 267.95s |
| `aave_v3_l3_001` | L3 | 0 | 1 | `reference_actions_mismatch` | 111.32s |
| `maker_sky_l3_001` | L3 | 0 | 1 | `reference_actions_mismatch` | 118.54s |
| `lido_l3_001` | L3 | 0 | 2 | `reference_actions_mismatch` | 51.04s |
| `pendle_l3_001` | L3 | 0 | 6 | `reference_actions_mismatch` | 144.12s |
| `gmx_l3_001` | L3 | 0 | 6 | `reference_actions_mismatch` | 274.27s |

Aggregate:

```text
retried tasks = 7
safe success = 0 / 7
llm_error after retry = 0 / 7
```

## Interpretation

The long-timeout retry changes the interpretation of Stage B.

Before retry:

```text
Some failures looked like API read timeout / llm_error.
```

After retry:

```text
All previously timed-out tasks returned model actions.
No task failed due to llm_error.
All 7 still failed because final action sequence did not match the required reference write actions.
```

Therefore:

```text
The Stage B failures are no longer primarily API instability.
With sufficient timeout, the vanilla agent still fails these L2/L3 tasks due to task/action mismatch.
```

This supports a stronger conclusion:

```text
L3 tasks are genuinely difficult for the vanilla agent under the current prompt and tool-use setup.
```

## Failure Examples

| Task ID | Last Observed Tool | Notes |
|---|---|---|
| `uniswap_v3_l2_001` | `swap_exact_in` | Completed a swap, but action sequence did not match required reference actions. |
| `uniswap_v3_l3_001` | `swap_exact_in` | Performed multiple steps but did not produce the correct risk-aware sequence. |
| `aave_v3_l3_001` | `get_user_position` | Only inspected position, did not execute required corrective write actions. |
| `maker_sky_l3_001` | `get_vault_state` | Only inspected vault, did not execute required write actions. |
| `lido_l3_001` | `stake_eth` | Executed a write action, but not the expected safe final sequence. |
| `pendle_l3_001` | `get_implied_apy` | Spent several steps querying market information, did not reach required final write actions. |
| `gmx_l3_001` | `open_long` | Opened a position, but not the required safe/reference position. |

## Updated Stage B Conclusion

After long-timeout retry:

```text
L1: 6 / 6
L2: 5 / 6
L3: 0 / 6
```

The difficulty gradient remains:

```text
L1 easy for vanilla
L2 mostly solvable
L3 not solved by vanilla
```

The earlier `llm_error` interpretation should be revised:

```text
Initial llm_error failures were caused by too-short timeout.
After extending timeout, these became normal model/action failures.
```

For future Stage C:

```text
Use longer timeout for formal runs, at least DEFI_VANILLA_TIMEOUT_S=120.
Keep llm_error as an operational failure category, but do not treat the earlier 35s timeout run as final evidence.
```
