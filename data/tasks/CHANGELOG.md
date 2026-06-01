# Task Set Changelog

冻结日期与变更记录。任务一经评估禁止修改。

## v1.0.0 - 2026-05-25

最终冻结任务集（由 v0.4 blind fair set 合并而来）：

- **Runtime**：`blind.jsonl`，60 条
- **Private gold**：`gold.jsonl`，60 条（仅评测使用，不暴露给 Agent）
- 四类任务：`portfolio`(12) / `cross_protocol`(16) / `risk_hedging`(16) / `governance`(16)
- 难度：`L1`(12) / `L2`(32) / `L3`(16)
- 公开字段：`scenario`、`market_notes`、`action_descriptions`；动作盲化为 `option_A`…
- Gold 由模拟器 utility 生成（`candidate_scores`、`optimal_utility`、`utility_tolerance`）

## 历史版本（已归档删除）

- v0.1.0：32 条显式动作名任务（portfolio/governance/cross_protocol/risk_hedging 各 8）
- v0.2：60 条 hard set（显式动作 + KG 路径标注）
- v0.3：60 条 hard + 4 条 kg_probe（盲化动作 + action_semantics）
- v0.4：60 条 blind fair set（本版合并为 v1.0.0）
