# KDWAS 实验数据调研报告

## 1. 研究概述

本研究提出一种知识驱动的钱包智能体系统（Knowledge-Driven Wallet Agent System, KDWAS），核心思想是将动态金融知识图谱（DFKG）作为 Wallet Agent 的认知与记忆基础设施。系统包含四个核心模块：

- **DFKG**（动态金融知识图谱）—— 长期语义记忆
- **Neuro-Symbolic Reasoning Engine**（神经符号推理引擎）—— 结合 LLM 与结构化图谱推理
- **Mission-Centric Coordination Layer**（任务中心协同层）—— 多智能体共享世界模型
- **Runtime Provenance Framework**（运行时溯源框架）—— 可解释与可审计

实验设计涵盖五个方面：金融推理评估、长期记忆评估、多智能体协同评估、可解释性与审计评估、系统级性能评估。

本报告梳理了各项实验所需数据、已采集数据及其来源，以及当前数据缺口。

---

## 2. 实验数据需求总览

| 实验 | 核心评估目标 | 需要的数据类型 |
|------|-------------|---------------|
| 8.1 金融推理评估 | 知识图谱能否提升长期金融推理能力 | 协议关系数据、钱包行为数据、安全事件数据、多步骤任务场景 |
| 8.2 长期记忆评估 | Agent 能否保持长期偏好一致性与上下文持续性 | 长周期钱包行为序列（≥12个月）、用户偏好演化数据 |
| 8.3 多智能体协同评估 | Shared World Model 能否提升集体智能 | 多钱包协同场景数据、DAO 治理数据、流动性迁移数据 |
| 8.4 可解释性与审计评估 | 推理链是否可追溯、可审计 | 安全事件 ground truth、专家评审数据 |
| 8.5 系统级评估 | 大规模智能体生态下的系统性能 | 大规模地址池、全量链上数据 |

---

## 3. 已采集数据集

目前已构建 7 个数据集，覆盖协议层、钱包行为层和安全事件层三个维度。所有原始数据存储在 `data/` 目录下。

### 3.1 数据流水线

```
DefiLlama API                    Dune Analytics (Spellbook)
     │                                    │
     ├─ GET /protocols                    ├─ dex.trades → wallet_swap_ts.csv
     │  ├─ protocol_list.csv              ├─ lending.borrow/repay → wallet_lending_ts.csv
     │  └─ defi_tvl.csv                   └─ 用户画像聚合 → wallet_profiles.csv
     │                                                        └─ 精选 → selected_addresses.csv
手动整理
     │
     └─ Rekt News → security_events.csv
```

---

### 3.2 协议层数据

#### (a) 协议 TVL 排名 (`protocol_list.csv`)

- **来源**: DefiLlama API `GET /protocols`，免费，无需 API Key
- **采集方式**: 按 TVL 降序取 Top 20
- **记录数**: 20 条
- **用途**: 构建 DFKG 中 Protocol 节点的基本属性；协议类别直接为第 5.1 节协议依赖推理提供分类信息

**样例数据**（Top 10）:

| 协议 | 代币 | 类别 | 主链 | TVL (USD) |
|------|------|------|------|-----------|
| Binance CEX | BNB | CEX | Multi-Chain | $154.4B |
| OKX | — | CEX | Multi-Chain | $24.7B |
| Lido | LDO | Liquid Staking | Multi-Chain | $18.9B |
| Bitfinex | — | CEX | Multi-Chain | $18.8B |
| SSV Network | SSV | Staking Pool | Ethereum | $15.7B |
| Bybit | — | CEX | Multi-Chain | $15.3B |
| Aave V3 | AAVE | Lending | Multi-Chain | $14.1B |
| Robinhood | — | CEX | Multi-Chain | $13.7B |
| WBTC | — | Bridge | Bitcoin | $8.8B |
| Binance staked ETH | — | Liquid Staking | Multi-Chain | $7.9B |

#### (b) DeFi 协议 TVL 精选 (`defi_tvl.csv`)

- **来源**: 同上，排除 CEX 和跨链桥后的 Top 25 DeFi 协议
- **记录数**: 25 条
- **用途**: 直接填充 DFKG 中的 DeFi Protocol 节点；跨链/跨类别关系用于构建协议依赖边

**样例数据**:

| 协议 | 代币 | 类别 | TVL (USD) |
|------|------|------|-----------|
| Lido | LDO | Liquid Staking | $18.9B |
| Aave V3 | AAVE | Lending | $14.1B |
| Morpho Blue | MORPHO | Lending | $7.4B |
| EigenCloud | EIGEN | Restaking | $6.9B |
| Sky Lending | SKY | CDP | $5.7B |
| Spark | — | CDP | $5.1B |
| Uniswap | UNI | DEX | $2.4B |
| Curve Finance | CRV | DEX | $1.6B |
| PancakeSwap | CAKE | DEX | $1.5B |
| Pendle | PENDLE | Yield | $1.8B |

---

### 3.3 安全事件层数据

#### (c) DeFi 安全事件 (`security_events.csv`)

- **来源**: [Rekt News](https://rekt.news/) 排行榜及公开事后分析报告，手动整理
- **采集方式**: 从 Rekt News leaderboard 选取 Top 20 重大事件，逐条核对攻击手法和受影响协议
- **记录数**: 20 条，覆盖 2021-2025 年
- **用途**: 对实验 8.1（风险对冲）和第 5.2 节（因果金融推理）至关重要——作为风险传播路径验证和攻击特征识别的 ground truth

**完整数据**:

| 事件 | 日期 | 损失 (M) | 类别 | 链 | 攻击手法 | 受影响协议 |
|------|------|----------|------|-----|----------|-----------|
| Ronin Bridge Exploit | 2022-03-29 | $624 | Bridge | Ethereum/Sidechain | Validator Compromise | Ronin Bridge (Axie Infinity) |
| BNB Bridge Exploit | 2022-10-07 | $568 | Bridge | BNB Chain | Signature Forgery | BNB Token Hub |
| FTX Collapse | 2022-11-11 | $8,500 | CEX | Multi-chain | Fraud | FTX |
| Euler Finance Hack | 2023-03-13 | $197 | Lending | Ethereum | Flash Loan Attack | Euler Finance |
| Curve Vyper Exploit | 2023-07-30 | $73 | DEX | Ethereum | Reentrancy | Curve Finance (Vyper) |
| KyberSwap Elastic Hack | 2023-11-22 | $54.7 | DEX | Multi-chain | Price Manipulation | KyberSwap |
| Mango Markets Exploit | 2022-10-11 | $114 | DEX | Solana | Oracle Manipulation | Mango Markets |
| Radiant Capital Hack | 2024-10-16 | $50 | Lending | Arbitrum | Oracle Manipulation | Radiant Capital |
| Cream Finance Hack | 2021-10-27 | $130 | Lending | Ethereum | Flash Loan Attack | Cream Finance |
| BadgerDAO Hack | 2021-12-02 | $120 | Yield | Ethereum | Frontend Injection | BadgerDAO |
| PancakeBunny Exploit | 2021-05-20 | $45 | Yield | BNB Chain | Flash Loan Attack | PancakeBunny |
| Wintermute Hack | 2022-09-20 | $160 | Market Maker | Ethereum | Private Key Leak | Wintermute |
| Nomad Bridge Hack | 2022-08-02 | $190 | Bridge | Multi-chain | Smart Contract Bug | Nomad Bridge |
| Wormhole Bridge Hack | 2022-02-03 | $326 | Bridge | Ethereum/Solana | Smart Contract Bug | Wormhole Bridge |
| Beanstalk Farms Exploit | 2022-04-17 | $182 | Yield | Ethereum | Governance Attack | Beanstalk |
| Harmony Bridge Hack | 2022-06-24 | $100 | Bridge | Harmony | Private Key Leak | Horizon Bridge |
| Poloniex Hack | 2023-11-10 | $126 | CEX | Ethereum | Private Key Leak | Poloniex |
| Orbit Chain Hack | 2024-01-01 | $81 | Bridge | Multi-chain | Private Key Leak | Orbit Chain |
| UwU Lend Exploit | 2024-06-10 | $19.5 | Lending | Ethereum | Oracle Manipulation | UwU Lend |
| Bybit Hack | 2025-02-21 | $1,500 | CEX | Ethereum | UI Spoofing / Social Engineering | Bybit |

**攻击手法分布**:

| 攻击手法 | 数量 |
|----------|------|
| 私钥泄露 | 4 |
| 闪电贷攻击 | 3 |
| 预言机操纵 | 3 |
| 智能合约漏洞 | 2 |
| 验证者妥协 | 1 |
| 签名伪造 | 1 |
| 前端注入 | 1 |
| 治理攻击 | 1 |
| 价格操纵 | 1 |
| UI 欺骗/社会工程 | 1 |
| 欺诈 | 1 |
| 重入攻击 | 1 |

---

### 3.4 钱包行为层数据

#### (d) 钱包画像 (`wallet_profiles.csv`)

- **来源**: Dune Analytics — `dex.trades` 和 `lending.borrow` spell 表（Dune Query 7536798）
- **采集方式**: SQL 查询 2025-05 至 2026-05 共 12 个月的链上数据，筛选 `swap_count >= 100,000` 的高活跃钱包，聚合 DEX 交易和借贷行为
- **记录数**: 50 个钱包地址
- **用途**: 构建 DFKG 中 Wallet Identity 节点的行为基线；用于实验 8.1 和 8.2 的用户偏好建模

**Archetype 分类方法**:

| Archetype | 判定标准 | 行为解读 |
|-----------|----------|----------|
| **MEV_HFT** | active_days ≥ 300, swap_count ≥ 1M, avg_trade_size < $5,000 | 高频低额交易，极可能为 MEV 机器人或算法交易者 |
| **Institutional_Whale** | total_volume ≥ $5B, avg_trade_size ≥ $10,000 | 超大单笔交易，极可能为机构/做市商/高净值个人 |
| **Cross_Protocol_Power_User** | dex_projects ≥ 10, lend_projects ≥ 1 | 跨协议多样化操作，资深 DeFi 用户 |
| **Protocol_Loyalist** | dex_projects ≤ 3, active_days ≥ 200 | 集中于少数协议但高度活跃，适合治理分析 |

**各 Archetype 样例**:

| 地址 | 交易总数 | 总额 (USD) | DEX 数 | 活跃天数 | 均单额 | 借贷交易 | 借贷额 | 借贷协议 | 类别 |
|------|---------|-----------|--------|---------|--------|---------|--------|---------|------|
| `0x66a9...` | 7,256,538 | $13.3B | 2 | 366 | $1,844 | 0 | $0 | 0 | MEV_HFT |
| `0x74de...` | 1,010,821 | $506M | 15 | 366 | $502 | 0 | $0 | 0 | MEV_HFT |
| `0x51c7...` | 4,331,209 | $52.9B | 6 | 366 | $12,209 | 0 | $0 | 0 | Institutional_Whale |
| `0xae2f...` | 446,538 | $30.0B | 3 | 366 | $68,010 | 0 | $0 | 0 | Institutional_Whale |
| `0x1f2f...` | 3,245,966 | $64.4B | 16 | 366 | $19,861 | 20,604 | -$212K | 2 | Institutional_Whale |
| `0x0bb7...` | 543,040 | $506M | 16 | 119 | $932 | 112 | -$890K | 1 | Cross_Protocol_Power_User |
| `0x3611...` | 474,678 | $1.7B | 17 | 357 | $3,619 | 863 | $281K | 1 | Cross_Protocol_Power_User |
| `0x80a6...` | 629,193 | $278M | 1 | 366 | $442 | 0 | $0 | 0 | Protocol_Loyalist |

#### (e) 精选地址 (`selected_addresses.csv`)

- **来源**: `wallet_profiles.csv` 子集，人工精选
- **记录数**: 14 个（每类 archetype 约 4 个，最大化同类内多样性）
- **用途**: 作为后续时序数据采集的目标地址，也是实验评估的主要测试对象

#### (f) 钱包交易时间序列 (`wallet_swap_ts.csv`)

- **来源**: Dune Analytics — `dex.trades` spell 表（Query 7536842, Execution `01KRZRNJBCCQQVXQ7E627PM953`）
- **采集方式**: 对 10 个精选地址，按 `(address, block_date, project, blockchain)` 四维度聚合每日 DEX 交易
- **记录数**: 100 行（可通过分页扩展至全量）
- **字段**: address, block_date, project, blockchain, daily_swaps, daily_volume_usd, tokens_bought, tokens_sold, avg_trade_size
- **覆盖协议**（22 个）: Uniswap, Curve, PancakeSwap, SushiSwap, Aerodrome, 1inch, Maverick, Fluid, KyberSwap, FraxSwap, Velodrome, Camelot, DODO, Bancor, ShibaSwap, Quickswap, AlienBase, BaseSwap, HorizonDEX, DefiSwap, Verse DEX, Solidly
- **覆盖链**（5 条）: Ethereum, Arbitrum, Base, Optimism, Polygon
- **用途**: 实验 8.1 金融行为推理、实验 8.2 长期时序记忆的核心数据集

**样例数据**（`0x0bb7a4fdea32910038dec59c20ccae3a6e66b09f`, 2026-04-13 当天部分协议）:

| 协议 | 链 | 日交易数 | 日交易额 | 均单额 |
|------|-----|---------|---------|--------|
| uniswap | ethereum | 822 | $1,248,200 | $1,524 |
| curve | ethereum | 87 | $279,851 | $3,217 |
| aerodrome | base | 114 | $35,117 | $308 |
| uniswap | base | 194 | $19,589 | $101 |
| 1inch-LOP | base | 141 | $25,386 | $180 |
| pancakeswap | base | 61 | $26,627 | $437 |
| sushiswap | ethereum | 51 | $5,311 | $104 |
| pancakeswap | ethereum | 52 | $7,530 | $145 |

该地址在 4 天内（2026-04-10 至 2026-04-13）覆盖了 Ethereum、Arbitrum、Base、Optimism、Polygon 共 5 条链上的 22 个 DEX 协议，展现了典型 Cross_Protocol_Power_User 的跨链多协议行为特征。

#### (g) 钱包借贷时间序列 (`wallet_lending_ts.csv`)

- **来源**: Dune Analytics — `lending.borrow` + `lending.repay` spell 表（Query 7536849, Execution `01KRZRPWBFC5ZJ5PVYWR8BEFJQ`）
- **采集方式**: 对 10 个精选地址，按 `(address, block_date, project, blockchain, transaction_type, symbol)` 聚合每日借贷活动
- **记录数**: 100 行
- **字段**: address, block_date, project, blockchain, transaction_type, loan_type, symbol, daily_count, daily_volume_usd
- **覆盖协议**: Aave (Ethereum)
- **覆盖代币**（14 种）: USDT, USDC, DAI, GHO, crvUSD, wstETH, cbETH, osETH, LINK, tBTC, cbBTC, USDe, USDS, EURC
- **用途**: 实验 8.1 协议理解准确率评估（波动性资产 vs 稳定币的风险区分）、第 5.3 节杠杆约束测试

**样例数据**（`0x1f2f10d1c40777ae1da742455c65828ff36df387`, 2025-12-22）:

| 类型 | 代币 | 利率模式 | 笔数 | 交易额 |
|------|------|---------|------|--------|
| borrow | USDT | variable | 3 | +$5,012,359 |
| repay | USDT | — | 3 | -$5,012,359 |
| borrow | USDC | variable | 7 | +$2,447,028 |
| repay | USDC | — | 7 | -$2,447,028 |
| borrow | wstETH | variable | 2 | +$186,923 |
| repay | wstETH | — | 2 | -$186,923 |
| borrow | LINK | variable | 1 | +$62,386 |
| repay | LINK | — | 1 | -$62,386 |

可以看出这是一个 Institutional_Whale 地址，单日借贷规模达数百万美元，且同一代币的 borrow/repay 配对出现，呈现高频循环借贷特征——可能是杠杆策略或闪电贷操作。这种模式为实验 8.1 中"协议理解准确率"评估提供了真实的行为基础。

---

## 4. 数据集与 KDWAS 模块/实验的对应关系

| 数据集 | 记录数 | DFKG（第4节） | 神经符号推理（第5节） | 协同（第6节） | 溯源（第7节） | 服务实验 |
|--------|--------|--------------|---------------------|-------------|------------|---------|
| protocol_list.csv | 20 | Protocol 节点 | 协议依赖推理 | 共享世界模型 | 协议状态审计 | 8.1 |
| defi_tvl.csv | 25 | Protocol 节点 + TVL 边 | 资金流推理 | 流动性状态共享 | TVL 变化追踪 | 8.1 |
| security_events.csv | 20 | Market Event 节点 | 因果风险推理 (5.2) | 风险事件广播 | 风险溯源 | 8.1, 8.4 |
| wallet_profiles.csv | 50 | Wallet Identity 节点 | 用户偏好约束 (5.3) | Agent 身份共享 | 偏好一致性审计 | 8.1, 8.2 |
| selected_addresses.csv | 14 | 目标钱包节点 | 测试对象 | — | — | 全部 |
| wallet_swap_ts.csv | 100+ | Transaction Flow 边 | 金融行为推理 | 语义状态交换 | 行为溯源 | 8.1, 8.2 |
| wallet_lending_ts.csv | 100+ | Protocol Dependency 边 | 约束感知规划 (5.3) | 风险协同 | 约束验证 | 8.1, 8.3 |

---

## 5. 数据来源汇总

| 来源 | 类型 | 获取方式 | 费用 | 速率限制 |
|------|------|---------|------|---------|
| [Dune Analytics](https://dune.com) | 链上 SQL 查询平台 | Dune MCP / Web API | 免费层 5 credits/月 | 3 次/秒 (API) |
| [DefiLlama](https://defillama.com) | DeFi 聚合数据 | REST API (免费, 无需 Key) | 免费 | ~100 次/分钟 |
| [Rekt News](https://rekt.news/) | 安全事件分析 | 网页手动整理 | 免费 | — |

**Dune Spellbook 关键表**:

| 表名 | 用途 | 关键分区列 |
|------|------|----------|
| `dex.trades` | 所有 DEX 交易记录 | `block_time` |
| `lending.borrow` | 借贷协议借款记录 | `block_time` |
| `lending.repay` | 借贷协议还款记录 | `block_time` |
| `lending.supply` | 借贷协议存款记录 | `block_time` |
| `lending.liquidation` | 清算事件 | `block_time` |

---

## 6. 当前数据缺口与后续计划

### 已具备的数据
- 协议 TVL 现状和分类
- 20 起重大安全事件的攻击手法/损失/协议
- 50 个钱包的 12 个月聚合行为画像（4 种 archetype）
- 10 个钱包的 DEX 交易时间序列
- 10 个钱包的 Aave 借贷时间序列

### 缺口

| 缺口 | 重要性 | 预获取来源 | 说明 |
|------|--------|----------|------|
| **治理参与数据** | 高 | Boardroom API / Snapshot API / Dune governance 表 | 实验 8.1 Governance Voting 和 8.3 Multi-Agent Governance 的核心数据 |
| **跨链桥交易数据** | 高 | Dune bridge 相关 spell 表 / Across / Stargate | 实验 8.1 Cross-Protocol Planning 和 8.3 Liquidity Migration 场景 |
| **历史 TVL 时间序列** | 中 | DefiLlama `/protocol/{slug}` 历史端点 | 当前仅有快照数据，实验 8.2 需要 TVL 变化趋势 |
| **清算事件数据** | 中 | Dune `lending.liquidation` 表 | 风险传播建模和实验 8.1 Risk Hedging 的补充数据 |
| **钱包样本扩展** | 中 | Dune 扩大查询范围至 500+ 地址 | 实验 8.5 大规模评估需要更大的测试集 |
| **多链借贷数据** | 中 | 扩展 Dune 查询至 Aave V3 Arbitrum/Optimism/Base | 当前仅覆盖 Aave Ethereum |
| **DAO Treasury 数据** | 中 | DeepDAO API / Dune DAO 相关表 | 实验 8.3 Treasury Coordination 场景 |
| **专家评审数据** | 低（后期） | 人工邀请 | 实验 8.4 需要 DeFi 专家和安全审计者参与 |

### 优先级建议

**下一步优先采集**:
1. 治理参与数据（Snapshot 投票记录、DAO 提案）—— 对实验 8.1 和 8.3 关键
2. 跨链桥交易数据 —— 对实验 8.1 Cross-Protocol Planning 关键
3. 清算事件数据 —— 充实风险传播 ground truth

**中期补充**:
4. 多链借贷数据扩展
5. 历史 TVL 时间序列

**后期**:
6. 专家评审（实验 8.4 人工评估环节）

---

## 7. 小结

目前已从 **3 个数据源**（Dune Analytics, DefiLlama, Rekt News）采集了 **7 个数据集**，覆盖：

- **协议层**: 25 个 DeFi 协议的 TVL 和分类
- **事件层**: 20 起安全事件的结构化攻击记录
- **行为层**: 50 个钱包的 12 个月聚合行为画像（含 4 类 archetype），其中 10 个钱包的细粒度日频 DEX 交易和借贷时间序列

这些数据可直接支撑实验 8.1（金融推理）和 8.2（长期记忆）的初步评估。实验 8.3（多智能体协同）和 8.4（可解释性审计）所需的治理数据、跨链桥数据、清算数据仍需补充采集。
