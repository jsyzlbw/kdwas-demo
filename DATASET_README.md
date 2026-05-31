# KDWAS Dataset Specification

Knowledge-Driven Wallet Agent System — Dataset Design for Experimental Evaluation

---

## 目录

1. [概述](#1-概述)
2. [Mission 测试集 (8.1 Financial Reasoning)](#2-mission-测试集-81-financial-reasoning)
3. [时间线数据集 (8.2 Long-Term Memory)](#3-时间线数据集-82-long-term-memory)
4. [多 Agent 剧本 (8.3 Multi-Agent Coordination)](#4-多-agent-剧本-83-multi-agent-coordination)
5. [对抗样本 & 专家评估框架 (8.4 Explainability & Auditing)](#5-对抗样本--专家评估框架-84-explainability--auditing)
6. [性能基准 (8.5 System-Level)](#6-性能基准-85-system-level)
7. [附录：数据收集与标注流程](#7-附录数据收集与标注流程)

---

## 1. 概述

### 1.1 研究目标

KDWAS (Knowledge-Driven Wallet Agent System) 旨在构建一种知识驱动的钱包智能体系统，使自治金融智能体能够在开放动态环境中实现长期记忆、语义推理、任务中心自治以及可解释协同。

本数据集用于支撑 KDWAS 论文第 8 节的五个实验维度。

### 1.2 总体数据资产一览

| # | 数据集 | 用途 | 规模 | 标注要求 | 工作量 |
|---|--------|------|------|---------|--------|
| D1 | Mission 测试集 | 8.1 Financial Reasoning | 30 场景 | 3 位 DeFi 专家标注最优动作路径 | 高 |
| D2 | 时间线数据集 | 8.2 Long-Term Memory | 5 条 × 15-20 步 | 专家评估全时间线一致性 | 高 |
| D3 | 多 Agent 剧本 | 8.3 Multi-Agent Coordination | 8 场景 | 定义多 Agent 协同路径基线 | 中 |
| D4 | 对抗样本 | 8.4 Explainability | 30 case | 专家编写问题 case | 中 |
| D5 | 专家评估框架 | 8.4 Auditing | 问卷 + 评分体系 | 设计评分标准 | 低 |
| D6 | 性能日志 | 8.5 System-Level | 运行时采集 | 无需标注 | 低 |

### 1.3 分类体系 (Financial Mission Taxonomy)

所有数据集共用以下分类体系，覆盖 Wallet Agent 的自治金融任务空间。

```
Core Category 1: Portfolio & Asset Management
├── 1.1 Asset Allocation
│   ├── 1.1.1 Single-Asset Rebalancing
│   ├── 1.1.2 Multi-Asset Portfolio Optimization
│   └── 1.1.3 Yield Optimization
├── 1.2 Liquidity Management
│   ├── 1.2.1 Cross-Chain Liquidity Migration
│   ├── 1.2.2 LP Position Management
│   └── 1.2.3 Emergency Liquidity Withdrawal
└── 1.3 Long-Term Holding Strategy
    ├── 1.3.1 HODL with Monitoring
    ├── 1.3.2 Staking/Locking Strategy
    └── 1.3.3 Vesting Schedule Management

Core Category 2: Risk Management
├── 2.1 Risk Monitoring
│   ├── 2.1.1 Protocol Security Monitoring
│   ├── 2.1.2 Market Volatility Alert
│   └── 2.1.3 Position Health Monitoring
├── 2.2 Risk Mitigation
│   ├── 2.2.1 Automated Hedging
│   ├── 2.2.2 Stop-Loss Execution
│   └── 2.2.3 Collateral Top-Up / Deleveraging
└── 2.3 Insurance & Protection
    ├── 2.3.1 DeFi Insurance Purchase
    ├── 2.3.2 Permission Revocation
    └── 2.3.3 Multi-Sig Migration

Core Category 3: Governance & Ecosystem Participation
├── 3.1 Direct Governance
│   ├── 3.1.1 Proposal Voting
│   ├── 3.1.2 Proposal Creation & Submission
│   └── 3.1.3 Governance Delegation
├── 3.2 Ecosystem Intelligence
│   ├── 3.2.1 Protocol Dependency Analysis
│   ├── 3.2.2 Governance Signal Aggregation
│   └── 3.2.3 Reputation & Trust Scoring
└── 3.3 Treasury Operations
    ├── 3.3.1 DAO Treasury Rebalancing
    ├── 3.3.2 Grant Distribution Automation
    └── 3.3.3 Revenue Distribution & Buyback

Core Category 4: Multi-Agent Coordination
├── 4.1 Cooperative Finance
│   ├── 4.1.1 Joint Liquidity Provision
│   ├── 4.1.2 Coordinated Hedging
│   └── 4.1.3 Shared Treasury Management
├── 4.2 Agent-to-Agent Operations
│   ├── 4.2.1 Machine-to-Machine Payment
│   ├── 4.2.2 Cross-Agent Delegation
│   └── 4.2.3 Agent Service Marketplace
└── 4.3 Collective Intelligence
    ├── 4.3.1 Shared Risk Signal Propagation
    ├── 4.3.2 Distributed Market Analysis
    └── 4.3.3 Collective Governance Coordination
```

---

## 2. Mission 测试集 (8.1 Financial Reasoning)

### 2.1 用途

评估 KDWAS 的 **Neuro-Symbolic Financial Reasoning Engine** 在单 Agent 多步骤金融任务中的表现。对比 Vanilla LLM Agent、RAG-Based Agent 和 KDWAS 在推理质量上的差异。

### 2.2 数据规模与分布

| 难度级别 | Portfolio Mgmt | Governance | Cross-Protocol | Risk Hedging | Treasury | 合计 |
|---------|---------------|------------|---------------|-------------|---------|------|
| Simple | 2 | 1 | 1 | 2 | 1 | 7 |
| Medium | 3 | 2 | 2 | 2 | 1 | 10 |
| Complex | 3 | 2 | 2 | 3 | 3 | 13 |
| **合计** | **8** | **5** | **5** | **7** | **5** | **30** |

### 2.3 每条数据字段定义

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mission_id` | string | 是 | 唯一标识，格式 `FR-NNN` |
| `category` | string | 是 | 分类体系中对应类别 |
| `difficulty` | enum | 是 | `simple` / `medium` / `complex` |
| `initial_wallet_state` | object | 是 | Agent 的初始链上钱包状态 |
| `mission_prompt` | string | 是 | 自然语言描述的任务指令 |
| `environment_context` | object | 是 | 当前市场和协议状态快照 |
| `ground_truth` | object | 是 | 专家标注的参考答案 |
| `evaluation` | object | 是 | 评估标准定义 |

### 2.4 数据来源

| 信息项 | 来源 |
|--------|------|
| 钱包地址 | 随机生成 |
| 余额/头寸 | 基于真实 Aave/Compound 仓位按比例缩放 |
| 市场价格 | CoinGecko / Chainlink Oracle 历史快照 |
| 协议参数 | Aave / Compound / Uniswap 官方文档 |
| 最优动作 | 3 位 DeFi 专家独立标注 → 多轮共识 |
| 幻觉案例 | 专家预标注 + TIM 论文已知 LLM 失败的 case 整理 |

---

## 3. 时间线数据集 (8.2 Long-Term Memory)

### 3.1 用途

评估 KDWAS 的 **Dynamic Financial Knowledge Graph** 能否在长时间序列交互中维持上下文持续性。

### 3.2 数据规模

| 时间线 | 涉及场景 | 步数 | 偏好变更 | 特别测试点 |
|--------|---------|------|---------|-----------|
| TL-01: 保守投资者的月度之旅 | Portfolio Mgmt + Risk Monitoring | 18 | 2 | 重复市场波动测试 |
| TL-02: 稳健 DAO 参与者 | Governance + Treasury | 20 | 3 | 治理历史 Recall |
| TL-03: 跨链流动性提供者 | Cross-Protocol + Liquidity | 16 | 2 | 协议迁移后记忆保留 |
| TL-04: 激进收益猎人 → 风险规避 | All categories | 20 | 4 | 偏好漂移后的行为修正 |
| TL-05: 多任务 Treasury Agent | Coordination + Governance | 15 | 1 | 长周期 Mission 一致性 |

### 3.3 时间线设计原则

1. **记忆驻留测试**：每条第 2-3 个步骤插入一个偏好/事件的 recall probe
2. **重复场景测试**：同一市场条件出现两次，观察 Agent 第二次的响应是否更优
3. **偏好漂移测试**：用户偏好逐渐变化，观察 Agent 是否能准确追踪
4. **长程 mission 对齐**：终点处综合评估整条时间线上的行为
5. **干扰注入**：在时间线中点加入不相关信息，测试 Agent 能否区分重要记忆和噪声

---

## 4. 多 Agent 剧本 (8.3 Multi-Agent Coordination)

### 4.1 用途

评估 KDWAS 的 **Mission-Centric Coordination Layer**。对比 Isolated Agents、Communication-Only Agents 和 Shared-KG Agents。

### 4.2 数据规模

| 场景 ID | 类型 | Agent 数量 | 难度 |
|---------|------|-----------|------|
| MA-01 | DAO Treasury Coordination | 3 | medium |
| MA-02 | Cooperative Hedging | 2 | simple |
| MA-03 | Emergency Liquidity Migration | 3 | complex |
| MA-04 | Multi-Agent Governance | 4 | complex |
| MA-05 | Joint Liquidity Provision | 2 | simple |
| MA-06 | Distributed Risk Monitoring | 3 | medium |
| MA-07 | Cross-Chain Coordinated Arbitrage | 3 | complex |
| MA-08 | Multi-Treasury Rebalancing | 4 | complex |

### 4.3 评估基线

| 指标 | 单位 | Isolated Agents | Communication-Only | Shared KG |
|------|------|----------------|-------------------|-----------|
| Coordination Efficiency | steps | 15 | 10 | 8 |
| Consensus Latency | minutes | N/A | 180 | 60 |
| Communication Overhead | messages | 0 | 25 | 12 |

---

## 5. 对抗样本 & 专家评估框架 (8.4 Explainability & Auditing)

### 5.1 对抗样本

| 类型 | 数量 | 说明 |
|------|------|------|
| Hallucinated Actions (HA) | 10 | Agent 执行了不存在或错误的链上操作 |
| Risky Decisions (RD) | 10 | 高风险操作被触发而未被风险模块拦截 |
| Protocol Misunderstanding (PM) | 5 | Agent 对协议机制理解错误 |
| Mission Violations (MV) | 5 | 执行了明显与长期 mission 冲突的操作 |

### 5.2 专家评估问卷

评估维度：A. Reasoning Transparency (1-5) B. Auditability (1-5) C. Human Trust Score (1-5) D. Causal Trace Completeness (1-5) E. Risk Explainability (1-5)

Cohen's kappa 阈值 = 0.7。

---

## 6. 性能基准 (8.5 System-Level)

| 负载级别 | Agent 数量 | 并发任务 |
|---------|-----------|---------|
| 低 | 10 | 20 |
| 中 | 50 | 100 |
| 高 | 100 | 200 |
| 极端 | 500 | 1000 |

---

## 7. 文件目录结构

```
dataset/
├── DATASET_README.md
├── mission_taxonomy.json
├── mission_config.json
├── missions/
│   ├── FR-001.json ~ FR-030.json
│   ├── baselines/
│   └── annotations/
├── timelines/
│   ├── TL-01.json ~ TL-05.json
│   └── evaluation_scores/
├── multi_agent/
│   ├── MA-01.json ~ MA-08.json
│   └── baselines/
├── adversarial/
│   ├── HA-01.json ~ HA-10.json
│   ├── RD-01.json ~ RD-10.json
│   ├── PM-01.json ~ PM-05.json
│   └── MV-01.json ~ MV-05.json
├── evaluation_framework/
│   ├── questionnaire_template.md
│   ├── scoring_guidelines.md
│   └── results/
└── performance/
    ├── load_test_L10.json
    ├── load_test_L50.json
    ├── load_test_L100.json
    └── load_test_L500.json
```

*Last updated: 2026-05-31*
