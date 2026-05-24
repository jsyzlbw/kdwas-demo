# KDWAS 数据集文档

面向知识驱动钱包智能体系统（KDWAS）论文的数据集文档。本文档详细描述每个数据集的来源、结构、采集方法及其与所提出实验的关联。

---

## 目录结构

```
data/
├── README.md
├── README_zh.md
├── raw/
│   ├── protocol_list.csv        # Top 20 协议 TVL 排名（DefiLlama）
│   ├── defi_tvl.csv             # Top 25 DeFi 协议 TVL（DefiLlama）
│   └── security_events.csv      # 20 起重大 DeFi 安全事件（手动整理）
└── processed/
    ├── wallet_profiles.csv      # 50 个已分类钱包地址（Dune）
    ├── selected_addresses.csv   # 14 个代表性钱包（每类 archetype）
    ├── wallet_swap_ts.csv       # DEX 交易时间序列（Dune）
    └── wallet_lending_ts.csv    # 借贷借/还时间序列（Dune）
```

---

## 1. 协议列表 (`raw/protocol_list.csv`)

**来源**: [DefiLlama API](https://defillama.com/docs/api) — `GET /protocols`

**描述**: 按总锁仓量（TVL）排名的 Top 20 协议，包括 DeFi 协议和中心化交易所（CEX），展示加密领域资本集中度的整体格局。

**采集方法**: `curl https://api.llama.fi/protocols`，按 TVL 选取前 20。

**字段说明**:

| 字段 | 类型 | 说明 |
|-------|------|------|
| `name` | string | 协议名称 |
| `symbol` | string | 原生代币代码 |
| `category` | string | 协议类别（CEX, Liquid Staking, Lending, DEX, Bridge, CDP 等） |
| `chain` | string | 主链 |
| `tvl` | float | 总锁仓量（USD） |
| `slug` | string | DefiLlama 标识符 |

**记录数**: 20

**KDWAS 关联**: 用于构建动态金融知识图谱（DFKG）中的 Protocol 节点。协议类别直接为金融语义推理引擎（第 5.1 节）的协议依赖建模提供信息。

---

## 2. DeFi 协议 TVL (`raw/defi_tvl.csv`)

**来源**: [DefiLlama API](https://defillama.com/docs/api) — `GET /protocols`

**描述**: 排除 CEX 和跨链桥后的 Top 25 DeFi 协议 TVL 排名。涵盖 Liquid Staking、Lending、DEX、CDP、Yield、Derivatives、Restaking 等多个类别和多条链。

**字段说明**: 与 `protocol_list.csv` 相同。

**记录数**: 25

**KDWAS 关联**: 直接填充 DFKG 中的 DeFi Protocol 节点。跨链和跨类别的关联关系为协议依赖边的构建提供信息。用于实验 8.1（金融推理评估），测试智能体是否正确理解协议间关系。

---

## 3. 安全事件 (`raw/security_events.csv`)

**来源**: 根据 [Rekt News](https://rekt.news/) 排行榜和公开事后分析报告手动整理。

**描述**: 2021–2025 年间 20 起重大 DeFi 安全事件，涵盖跨链桥、借贷协议、DEX、CEX、收益聚合器和做市商。包括 Bybit 被盗（2025 年 2 月，15 亿美元）、Ronin Bridge 攻击（2022 年 3 月，6.24 亿美元）以及 FTX 崩盘（2022 年 11 月，85 亿美元）。

**字段说明**:

| 字段 | 类型 | 说明 |
|-------|------|------|
| `name` | string | 事件名称 |
| `date` | date | 事件日期（YYYY-MM-DD） |
| `amount_m` | float | 损失金额（百万 USD） |
| `category` | string | 受影响的协议类别 |
| `chain` | string | 受影响的区块链 |
| `technique` | string | 攻击手法（闪电贷、预言机操纵、私钥泄露等） |
| `protocol_affected` | string | 受影响的主要协议 |
| `reference` | string | Rekt News 文章链接 |

**记录数**: 20

**KDWAS 关联**: 该数据集对实验 8.1（风险对冲）和第 5.2 节（因果金融推理）至关重要。事件可作为以下方面的 ground truth：
- DFKG 中风险传播路径的验证
- 测试神经符号推理引擎是否能正确识别级联风险模式
- 训练约束感知规划模块以识别攻击特征

**攻击手法分布**:

| 攻击手法 | 数量 |
|-----------|-------|
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

## 4. 钱包画像 (`processed/wallet_profiles.csv`)

**来源**: [Dune Analytics](https://dune.com) — `dex.trades` 和 `lending.borrow` spell 表。Query ID: 7536798。

**描述**: 50 个活跃 DeFi 钱包地址的 12 个月聚合行为画像。每个地址根据链上活动模式被归类为 4 种 archetype 之一。

**采集方法**: 针对 Dune spellbook 表执行 SQL 查询，时间范围为 2025-05-01 至 2026-05-01，筛选 swap_count >= 100,000 的钱包以聚焦高活跃度用户。

**字段说明**:

| 字段 | 类型 | 说明 |
|-------|------|------|
| `address` | string | 钱包地址（0x...） |
| `swap_count` | int | DEX 交易总次数 |
| `total_volume` | float | DEX 总交易量（USD） |
| `dex_projects` | int | 使用的不同 DEX 协议数 |
| `active_days` | int | 有交易活动的天数 |
| `avg_trade_size` | float | 平均交易金额（USD） |
| `total_lend_txs` | int | 借贷总交易次数（借款+还款） |
| `total_lend_volume` | float | 借贷净交易量（USD） |
| `lend_projects` | int | 使用的不同借贷协议数 |
| `lend_active_days` | int | 有借贷活动的天数 |
| `profile` | string | Archetype 标签 |

**记录数**: 50

### Archetype 分类方法

基于链上行为的启发式阈值，将地址分为 4 种 archetype：

| Archetype | 判定标准 | 行为解读 |
|-----------|----------|----------|
| **MEV_HFT** | active_days >= 300, swap_count >= 1,000,000, avg_trade_size < $5,000 | 高频低额交易。极可能是 MEV 机器人或算法交易者，每日执行数千笔小额交易。 |
| **Institutional_Whale** | total_volume >= $5B, avg_trade_size >= $10,000 | 超大单笔交易。极可能是机构交易台、做市商或高净值个人执行大宗交易。 |
| **Cross_Protocol_Power_User** | dex_projects >= 10, lend_projects >= 1 | 跨协议多样化操作。资深 DeFi 用户，同时与 DEX 和借贷等整个生态交互。 |
| **Protocol_Loyalist** | dex_projects <= 3, active_days >= 200 | 高度活跃但集中于少数协议。深度嵌入特定协议生态的用户，与治理分析高度相关。 |

**Archetype 分布**:

| Profile | 数量 |
|---------|-------|
| Cross_Protocol_Power_User | ~20 |
| Institutional_Whale | ~12 |
| MEV_HFT | ~10 |
| Protocol_Loyalist | ~8 |

**KDWAS 关联**: 这些钱包画像是 DFKG 用户建模组件的主要数据来源。Archetype 作为 Wallet Identity 节点，为以下方面提供行为基线：
- 实验 8.1：测试 KDWAS 是否能维持与 archetype 匹配的风险偏好
- 实验 8.2：长期记忆评估——智能体能否在长时间跨度内记住用户与 archetype 一致的行为偏好？
- 第 5.3 节：约束感知规划——每种 archetype 意味着不同的风险约束

---

## 5. 精选地址 (`processed/selected_addresses.csv`)

**来源**: `wallet_profiles.csv` 的子集，手动选取最具代表性的地址。

**描述**: 14 个被选为每种 archetype 最具代表性的钱包地址，用于详细的时序分析。

**字段说明**: 与 `wallet_profiles.csv` 相同。

**记录数**: 14

**选取策略**: 每种 archetype 约 4 个，在同类中最大化行为多样性（不同链、不同协议、不同交易量区间）。

**KDWAS 关联**: 这些地址是下述时序数据集的目标对象，也是实验评估的主要测试对象。

---

## 6. 钱包交易时间序列 (`processed/wallet_swap_ts.csv`)

**来源**: [Dune Analytics](https://dune.com) — `dex.trades` spell 表。Query ID: 7536842，Execution ID: `01KRZRNJBCCQQVXQ7E627PM953`。

**描述**: 10 个精选钱包地址的每日 DEX 交易活动，按区块链和 DEX 协议细分。每行表示某个钱包在某条链上某个协议的一天活动。

**采集方法**:
```sql
SELECT
    address,
    DATE_TRUNC('day', block_time) AS block_date,
    project,
    blockchain,
    COUNT(*) AS daily_swaps,
    SUM(amount_usd) AS daily_volume_usd,
    COUNT(DISTINCT token_bought_symbol) AS tokens_bought,
    COUNT(DISTINCT token_sold_symbol) AS tokens_sold,
    AVG(amount_usd) AS avg_trade_size
FROM dex.trades
WHERE address IN (<selected_addresses>)
  AND block_time >= NOW() - INTERVAL '12' MONTH
GROUP BY 1, 2, 3, 4
ORDER BY 1, 2 DESC, 5 DESC
LIMIT 100
```

**字段说明**:

| 字段 | 类型 | 说明 |
|-------|------|------|
| `address` | string | 钱包地址 |
| `block_date` | date | 交易日期 |
| `project` | string | DEX 协议名称 |
| `blockchain` | string | 区块链网络 |
| `daily_swaps` | int | 交易笔数 |
| `daily_volume_usd` | float | 总交易量（USD） |
| `tokens_bought` | int | 买入的不同代币数 |
| `tokens_sold` | int | 卖出的不同代币数 |
| `avg_trade_size` | float | 平均交易金额（USD） |

**记录数**: 100

**覆盖协议**: Uniswap、Curve、PancakeSwap、SushiSwap、Aerodrome、1inch、Maverick、Fluid、KyberSwap、FraxSwap、Velodrome、Camelot、DODO、Bancor、ShibaSwap、Quickswap、AlienBase、BaseSwap、HorizonDEX、DefiSwap、Verse DEX、Solidly

**覆盖链**: Ethereum、Arbitrum、Base、Optimism、Polygon

**KDWAS 关联**: 以下方面的主要数据集：
- 实验 8.1（金融推理）：KDWAS 能否推断钱包的 archetype 并预测行为？
- 实验 8.2（长期记忆）：智能体能否跨越多日交易序列保持上下文？
- DFKG 构建：Wallet 节点与 Protocol 节点之间的 Transaction Flow 边

---

## 7. 钱包借贷时间序列 (`processed/wallet_lending_ts.csv`)

**来源**: [Dune Analytics](https://dune.com) — `lending.borrow` 和 `lending.repay` spell 表。Query ID: 7536849，Execution ID: `01KRZRPWBFC5ZJ5PVYWR8BEFJQ`。

**描述**: 10 个精选钱包地址在 Aave（Ethereum）上的每日借贷和还款活动。每行表示某个代币在某天的借款或还款活动。

**采集方法**:
```sql
SELECT
    address,
    DATE_TRUNC('day', block_time) AS block_date,
    project,
    blockchain,
    'borrow' AS transaction_type,
    loan_type,
    symbol,
    COUNT(*) AS daily_count,
    SUM(amount_usd) AS daily_volume_usd
FROM lending.borrow
WHERE address IN (<selected_addresses>)
  AND block_time >= NOW() - INTERVAL '12' MONTH
GROUP BY 1, 2, 3, 4, 5, 6, 7

UNION ALL

SELECT
    address,
    DATE_TRUNC('day', block_time) AS block_date,
    project,
    blockchain,
    'repay' AS transaction_type,
    NULL AS loan_type,
    symbol,
    COUNT(*) AS daily_count,
    SUM(amount_usd) AS daily_volume_usd
FROM lending.repay
WHERE address IN (<selected_addresses>)
  AND block_time >= NOW() - INTERVAL '12' MONTH
GROUP BY 1, 2, 3, 4, 5, 6, 7

ORDER BY 1, 2 DESC, 9 DESC
LIMIT 100
```

**字段说明**:

| 字段 | 类型 | 说明 |
|-------|------|------|
| `address` | string | 钱包地址 |
| `block_date` | date | 活动日期 |
| `project` | string | 借贷协议名称 |
| `blockchain` | string | 区块链网络 |
| `transaction_type` | string | `borrow` 或 `repay` |
| `loan_type` | string | 借款为 `variable`，还款为空 |
| `symbol` | string | 借入/偿还的代币符号 |
| `daily_count` | int | 交易笔数 |
| `daily_volume_usd` | float | 交易量（USD，借款为正，还款为负） |

**记录数**: 100

**覆盖代币**: USDT、USDC、DAI、GHO、crvUSD、wstETH、cbETH、osETH、LINK、tBTC、cbBTC、USDe、USDS、EURC

**KDWAS 关联**: 该数据支持以下借贷相关分析：
- 实验 8.1：协议理解准确率——智能体是否理解借入波动性代币（如 tBTC、LINK）与稳定币的风险差异？
- 第 5.3 节（约束感知规划）：测试智能体是否能根据历史借/还模式正确应用杠杆约束
- DFKG 中的风险传播建模：借/还模式揭示了用户使用哪些资产作为抵押品，以及清算级联如何传播

---

## 数据流水线总览

```
DefiLlama API                    Dune Analytics (Spellbook)
     │                                    │
     ├─ GET /protocols                    ├─ dex.trades (query 7536842)
     │  └─ protocol_list.csv              │  └─ wallet_swap_ts.csv
     │  └─ defi_tvl.csv                   │
     │                                    ├─ lending.borrow + lending.repay (query 7536849)
     │                                    │  └─ wallet_lending_ts.csv
     │                                    │
     │                                    └─ 用户画像聚合 (query 7536798)
     │                                       └─ wallet_profiles.csv
     │                                          └─ (人工精选)
     │                                             └─ selected_addresses.csv
     │
手动整理
     │
     └─ Rekt News 排行榜
        └─ security_events.csv
```

---

## 可复现性

### 前置条件
- Dune Analytics 账号及 API Key（用于 Dune 查询）
- DefiLlama API 免费，速率限制约 100 次/分钟（无需密钥）
- Python 3.x（使用标准库 `csv`）

### 重新执行 Dune 查询

**交易时间序列**（Dune Query 7536842）:
1. 在 WHERE 子句中更新目标钱包地址列表
2. 根据需要调整时间窗口
3. 通过 Dune MCP 执行: `executeQueryById(7536842)`
4. 获取结果: `getExecutionResults(<execution_id>)`

**借贷时间序列**（Dune Query 7536849）:
1. 同上，更新地址和时间窗口
2. 执行: `executeQueryById(7536849)`

**钱包画像**（Dune Query 7536798）:
1. 调整 `swap_count >= N` 阈值以控制样本量
2. 根据需要更新 12 个月时间窗口

### 重新获取 DefiLlama 数据
```bash
curl -s "https://api.llama.fi/protocols" | jq '.[] | select(.tvl > 1e9)'
```

### 重新执行分类
Python 分类脚本位于 `/tmp/save_data.py`。使用上文第 4 节描述的阈值，可根据分布情况调整阈值。

---

## 数据集与 KDWAS 各模块的对应关系

| 数据集 | DFKG（第4节） | 神经符号推理（第5节） | 协同（第6节） | 溯源（第7节） | 实验（第8节） |
|---------|-------------------|--------------------------------------|--------------------------|------------------------|--------------------------|
| protocol_list.csv | Protocol 节点 | 协议依赖推理 | 共享世界模型 | 协议状态审计 | 8.1 协议理解 |
| defi_tvl.csv | Protocol 节点 + TVL 边 | 资金流推理 | 流动性状态共享 | TVL 变化追踪 | 8.1 投资组合管理 |
| security_events.csv | Market Event 节点 | 因果风险推理（5.2） | 风险事件广播 | 风险溯源 | 8.1 风险对冲 |
| wallet_profiles.csv | Wallet Identity 节点 | 用户偏好约束（5.3） | Agent 身份共享 | 偏好一致性审计 | 8.2 记忆保持 |
| selected_addresses.csv | 目标钱包节点 | 测试对象选择 | — | — | 全部实验 |
| wallet_swap_ts.csv | Transaction Flow 边 | 金融行为推理 | 语义状态交换 | 行为溯源 | 8.1, 8.2 |
| wallet_lending_ts.csv | Protocol Dependency 边 | 约束感知规划（5.3） | 风险协同 | 约束验证 | 8.1, 8.3 |

---

## 已知局限性

1. **Dune 行数限制**: 两个时序数据集均以 100 行为上限。全量实验需要通过分页获取全部结果，或通过 Dune 的 CSV 导出功能。
2. **单一借贷协议**: 借贷时序数据仅覆盖 Aave on Ethereum。多协议借贷数据需要扩展查询。
3. **缺少治理数据**: 治理参与（DAO 投票、提案创建）尚未纳入。需要查询治理专用表。
4. **Archetype 分类为启发式方法**: 阈值为人工选定。更严谨的做法是使用聚类算法（如对归一化行为特征进行 k-means）。
5. **安全事件为手动整理**: 非实时数据源。生产环境需接入实时监控 API。
6. **TVL 数据为快照**: DefiLlama 数据反映查询时刻的 TVL。历史 TVL 时间序列需要使用 DefiLlama 的历史数据 API 端点。

---

## 数据集扩展计划

- [ ] 从 Boardroom/Snapshot API 获取治理参与数据
- [ ] 添加跨链桥交易数据
- [ ] 从 DefiLlama `/protocol/{slug}` 端点获取历史 TVL 时间序列
- [ ] 将钱包样本扩展至 500+ 地址，采用基于聚类的 archetype 发现方法
- [ ] 从 `lending.liquidation` spell 表添加清算事件数据
- [ ] 添加生息仓位的收益/策略数据
