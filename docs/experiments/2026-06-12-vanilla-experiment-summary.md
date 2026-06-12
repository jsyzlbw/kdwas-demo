# 2026-06-12 Vanilla Agent 实验总结

## 1. 做的实验内容

今天的目标是用 **裸 Agent** 跑一次 DeFi Bench v1 实验，作为之后方法比较中的 vanilla baseline。

这里的 vanilla agent 定义为：

```text
LLM + 当前任务 user_request + protocol policy + tools schema + tool observations
```

它不使用：

- RAG
- 额外知识库
- 手写 planner
- self-reflection
- protocol-specific solver
- hidden gold annotation
- hidden scenario
- candidate utility

### 1.1 接入 JD Qwen API

使用京东 OpenAI-compatible API：

```text
base_url = https://agentrs.jd.com/api/saas/openai-u/v1
model = qwen3.6-plus
env key = JD_API_KEY
```

新增 vanilla agent 代码：

```text
src/defi_bench_v1/llm_agents.py
```

主要包含：

- `VanillaLLMAgent`
- `build_vanilla_prompt`
- `parse_tool_call`

`VanillaLLMAgent` 接入已有 Python tool-use runtime：

```text
AgentContext
  -> VanillaLLMAgent.next_call()
  -> ToolCall
  -> ProtocolSandbox.execute()
  -> ToolObservation
  -> next AgentContext
  -> Evaluator
```

### 1.2 Runner 支持 vanilla 实验

修改了：

```text
src/defi_bench_v1/runner.py
```

新增能力：

- 自动读取根目录 `.env`
- 支持 `--agents vanilla`
- 支持 `--task-ids` 跑任务子集
- 支持 `--max-steps` 控制每个任务最多工具调用步数

### 1.3 Evaluator 修正

实验中发现一个重要评测问题：

```text
vanilla agent 会先调用 read tools 查询余额、allowance 等状态。
旧 evaluator 会把这些额外 read actions 也拿去和 reference_actions 精确匹配，导致合理探索被误判失败。
```

因此修正为：

```text
如果任务包含写动作，则评分时只比较 write action sequence；
read tools 仍保留在 trajectory 中，用于失败分析；
read-only / no-write 任务仍比较完整 action sequence。
```

这符合 benchmark 设计：read tools 是 Agent 的“眼睛”，不能因为合理查询而扣成失败。

### 1.4 Stage A：接口 smoke test

Stage A 目标是确认：

```text
JD Qwen API
VanillaLLMAgent
Python tool-use runtime
ProtocolSandbox
Evaluator
```

整条链能跑通。

实验设置：

```text
每个协议选 1 条 L1 任务
总任务数 = 6
repeats = 1
max_steps = 6
```

环境参数：

```bash
DEFI_VANILLA_TIMEOUT_S=35
DEFI_VANILLA_MAX_TOKENS=512
```

Stage A 任务：

| Protocol | Task ID |
|---|---|
| Uniswap V3 | `uniswap_v3_l1_001` |
| Aave V3 | `aave_v3_l1_001` |
| Maker / Sky | `maker_sky_l1_001` |
| Lido | `lido_l1_001` |
| Pendle | `pendle_l1_001` |
| GMX | `gmx_l1_001` |

### 1.5 Stage B：分层小实验

Stage B 目标是检查：

- L1 / L2 / L3 难度分层是否有效。
- 不同协议是否有系统性失败。
- vanilla agent 的主要失败类型是什么。

实验设置：

```text
每个协议选 L1、L2、L3 各 1 条
总任务数 = 18
repeats = 1
max_steps = 8
```

环境参数：

```bash
DEFI_VANILLA_TIMEOUT_S=35
DEFI_VANILLA_MAX_TOKENS=512
```

Stage B 任务：

| Protocol | L1 | L2 | L3 |
|---|---|---|---|
| Uniswap V3 | `uniswap_v3_l1_001` | `uniswap_v3_l2_001` | `uniswap_v3_l3_001` |
| Aave V3 | `aave_v3_l1_001` | `aave_v3_l2_001` | `aave_v3_l3_001` |
| Maker / Sky | `maker_sky_l1_001` | `maker_sky_l2_001` | `maker_sky_l3_001` |
| Lido | `lido_l1_001` | `lido_l2_001` | `lido_l3_001` |
| Pendle | `pendle_l1_001` | `pendle_l2_001` | `pendle_l3_001` |
| GMX | `gmx_l1_001` | `gmx_l2_001` | `gmx_l3_001` |

Stage B 首轮中，一些任务因为 JD API read timeout 导致进程非零退出。随后修正 vanilla agent：

```text
LLM client exception -> ToolCall("llm_error", ...)
```

这样 API 超时会被记录成 failed trajectory，而不是让整个 runner 崩掉。

## 2. 实验结果

### 2.1 Stage A 结果

Stage A 结果：

```text
总任务数 = 6
safe success = 6 / 6
success rate = 1.000
```

任务级结果：

| Protocol | Task ID | Safe Success | Action Count |
|---|---|---:|---:|
| Uniswap V3 | `uniswap_v3_l1_001` | 1 | 3 |
| Aave V3 | `aave_v3_l1_001` | 1 | 4 |
| Maker / Sky | `maker_sky_l1_001` | 1 | 2 |
| Lido | `lido_l1_001` | 1 | 2 |
| Pendle | `pendle_l1_001` | 1 | 5 |
| GMX | `gmx_l1_001` | 1 | 4 |

Stage A 结论：

```text
vanilla agent 已成功接入 JD Qwen API 和 DeFi Bench v1 Python tool-use runtime。
6 个协议的 L1 smoke tasks 全部通过。
```

详细记录：

```text
docs/experiments/2026-06-12-stage-a-vanilla-results.md
```

### 2.2 Stage B 总体结果

Stage B 结果：

```text
总任务数 = 18
safe success = 11 / 18
success rate = 0.611
```

### 2.3 Stage B 按难度结果

| Difficulty | Success | Total | Success Rate |
|---|---:|---:|---:|
| L1 | 6 | 6 | 1.000 |
| L2 | 5 | 6 | 0.833 |
| L3 | 0 | 6 | 0.000 |

观察：

```text
L1 全部成功；
L2 大部分成功；
L3 全部失败。
```

这说明当前任务难度分层是有效的。vanilla agent 可以完成简单任务，也能完成多数中等任务，但在风险约束更强、推理链更长的 L3 任务上表现明显下降。

### 2.4 Stage B 按协议结果

| Protocol | Success | Total | Success Rate |
|---|---:|---:|---:|
| Uniswap V3 | 1 | 3 | 0.333 |
| Aave V3 | 2 | 3 | 0.667 |
| Maker / Sky | 2 | 3 | 0.667 |
| Lido | 2 | 3 | 0.667 |
| Pendle | 2 | 3 | 0.667 |
| GMX | 2 | 3 | 0.667 |

Uniswap V3 的结果较低，主要是因为 L2 和 L3 在本次运行中都触发了 `llm_error`。

### 2.5 Stage B 任务级结果

| Protocol | Difficulty | Task ID | Safe Success | Action Count | Failure Reasons |
|---|---|---|---:|---:|---|
| Uniswap V3 | L1 | `uniswap_v3_l1_001` | 1 | 3 | - |
| Uniswap V3 | L2 | `uniswap_v3_l2_001` | 0 | 3 | `reference_actions_mismatch` |
| Uniswap V3 | L3 | `uniswap_v3_l3_001` | 0 | 7 | `reference_actions_mismatch` |
| Aave V3 | L1 | `aave_v3_l1_001` | 1 | 4 | - |
| Aave V3 | L2 | `aave_v3_l2_001` | 1 | 3 | - |
| Aave V3 | L3 | `aave_v3_l3_001` | 0 | 1 | `reference_actions_mismatch` |
| Maker / Sky | L1 | `maker_sky_l1_001` | 1 | 2 | - |
| Maker / Sky | L2 | `maker_sky_l2_001` | 1 | 3 | - |
| Maker / Sky | L3 | `maker_sky_l3_001` | 0 | 1 | `reference_actions_mismatch` |
| Lido | L1 | `lido_l1_001` | 1 | 2 | - |
| Lido | L2 | `lido_l2_001` | 1 | 3 | - |
| Lido | L3 | `lido_l3_001` | 0 | 2 | `reference_actions_mismatch` |
| Pendle | L1 | `pendle_l1_001` | 1 | 4 | - |
| Pendle | L2 | `pendle_l2_001` | 1 | 3 | - |
| Pendle | L3 | `pendle_l3_001` | 0 | 6 | `reference_actions_mismatch` |
| GMX | L1 | `gmx_l1_001` | 1 | 4 | - |
| GMX | L2 | `gmx_l2_001` | 1 | 3 | - |
| GMX | L3 | `gmx_l3_001` | 0 | 6 | `reference_actions_mismatch` |

详细记录：

```text
docs/experiments/2026-06-12-stage-b-vanilla-results.md
docs/experiments/2026-06-12-stage-b-long-timeout-retry-results.md
```

### 2.6 主要失败模式

Stage B 首轮的主要失败模式看起来是：

```text
JD API read timeout -> llm_error -> trajectory failure
```

根据修改意见，随后对所有出现 `llm_error` 的任务做了 long-timeout retry：

```bash
DEFI_VANILLA_TIMEOUT_S=120
DEFI_VANILLA_MAX_TOKENS=512
--max-steps 8
```

重跑结果：

```text
retried tasks = 7
safe success = 0 / 7
llm_error after retry = 0 / 7
```

这说明：

```text
首轮 llm_error 主要是 timeout 设置过短造成的；
大幅延长 timeout 后，API 能返回动作；
但 vanilla agent 仍然没有完成这些 L2/L3 任务。
```

因此，更新后的失败解释是：

```text
Stage B 最终失败主要不是 API 不稳定，而是 vanilla agent 的动作序列没有满足任务要求。
```

## 3. 当前结论

今天的 vanilla baseline 实验已经完成前两阶段：

```text
Stage A: passed, 6 / 6
Stage B: completed, 11 / 18
```

目前可以得出：

1. JD Qwen `qwen3.6-plus` 已成功接入 DeFi Bench v1。
2. Vanilla agent 可以通过 Python tool-use runtime 正常执行工具调用。
3. L1 任务对 vanilla agent 来说基本可解。
4. L2 任务大部分可解。
5. L3 任务在当前配置下全部失败。
6. 大幅延长 timeout 后，原先的 llm_error 消失，但失败任务仍然失败，因此 L3 更可能是 vanilla agent 的能力边界，而不是单纯 API 不稳定。

## 4. 验证结果

代码测试：

```text
python3 -m pytest tests/defi_bench_v1 -q
23 passed
```

数据集校验：

```text
python3 data/defi_bench_v1/scripts/validate_dataset.py
OK: DeFi Bench v1 dataset is valid
tasks=72 scenarios=72 deterministic=59 optimization=13
```

## 5. 建议下一步

可以进入正式 Stage C，但正式 baseline 应使用 long-timeout 配置：

```bash
DEFI_VANILLA_TIMEOUT_S=120
DEFI_VANILLA_MAX_TOKENS=512
--max-steps 8
```

Stage C 设置：

```text
72 tasks
repeats = 3
vanilla agent
```

后续报告中应将两类失败区分开：

```text
llm_error / API timeout = operational failure
reference_actions_mismatch = model/action failure
```
