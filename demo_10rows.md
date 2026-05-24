# KDWAS Demo — 小规模原型

---

## 表 A：Task Taxonomy（Protocol → 大类 → 子类 → 具体任务）— 10 条

参照 TIM 论文 Table 5/6 四列格式，每行是一个可被 Agent 执行的原子任务。

| # | Protocol | 大类 (Major Category) | 子类 (Sub-Category) | 具体任务 (Specific Task) | 对应 TIM Intent |
|---|----------|----------------------|---------------------|------------------------|-----------------|
| 1 | Uniswap V3 | B1 交易策略 | A1 现货交易获利 | `swapExactETHForTokens` — 用户用 ETH 兑换 USDC，路由通过 Uniswap V3 Router | A1 |
| 2 | Uniswap V3 | B2 流动性挖矿 | A5 提供流动性池 | `addLiquidity` — 用户向 USDC/ETH 0.05% 池添加双边流动性，获取 LP NFT 和手续费分成 | A5 |
| 3 | Aave V3 | B2 流动性挖矿 | A6 参与借贷 | `borrow` — 用户以 stETH 为抵押品，在 Aave Ethereum 上借出 USDC（浮动利率） | A6 |
| 4 | Aave V3 | B2 流动性挖矿 | A6 参与借贷 | `repay` — 用户偿还之前借出的 USDC + 利息，释放部分抵押品 | A6 |
| 5 | Aave V3 | B6 投资风险管理 | A16 止损策略 | `liquidationCall` — 第三方清算者触发清算，用户健康因子 <1 的仓位被部分清算 | A16 |
| 6 | Lido | B3 质押 | A8 ETH 流动性质押 | `submit` — 用户质押 ETH 获取 stETH，用于后续 DeFi 操作 | A8 |
| 7 | Curve | B1 交易策略 | A1 现货交易获利 | `exchange` — 用户在 Curve 3pool (DAI/USDC/USDT) 上执行低滑点稳定币兑换 | A1 |
| 8 | MakerDAO | B2 流动性挖矿 | A6 参与借贷 | `frob` — 用户调整金库 (Vault) 的抵押品/债务比例，生成更多 DAI | A6 |
| 9 | Compound | B8 间接治理 | A20 委托投票权 | `delegateBySig` — 用户通过签名消息将 COMP 投票权委托给另一地址 | A20 |
| 10 | EigenLayer | B3 质押 | A10 复合流动性质押 | `depositIntoStrategy` — 用户将 stETH 存入 EigenLayer 策略合约，参与再质押 | A10 |

---

## 表 B：TravelPlanner 风格的 Query-Plan Pair — 5 条

参考 TravelPlanner 的 query-plan 构建方法论，每条包含：
- **自然语言 Query**（含显式 + 隐式约束）
- **约束清单**（Hard / Commonsense / Environment）
- **参考 Plan**（ground truth，由专家标注的可行方案）
- **难度等级**

---

### Query #1 [难度: L1 Easy]

**Query**:
> 钱包 `0x3611b82c7b13e72b26eb0e9be0613bee7a45ac7c` (Cross_Protocol_Power_User) 目前持有 10 ETH 和 50,000 USDC。请为其设计一个在 Uniswap V3 上提供流动性的方案：要求全部资金在 Ethereum 主网上操作，选择 USDC/ETH 池，资金效率最大化（使用集中流动性）。

**约束清单**:

| 约束类型 | 约束项 | 内容 |
|---------|-------|------|
| Hard | Budget | 10 ETH + 50,000 USDC (全部) |
| Hard | Protocol | 仅 Uniswap V3 |
| Hard | Chain | 仅 Ethereum |
| Hard | 资产类型 | USDC/ETH pair |
| Commonsense | 非冲突仓位 | 提供的双边流动性价值应相等 |
| Commonsense | 完整方案 | 必须含 pool fee tier 选择、价格区间设定 |
| Commonsense | 链上可验证 | Pool 地址必须真实存在于 Uniswap V3 Factory |
| Environment | — | 若所选 fee tier 无流动性则需切换 |

**参考 Plan**:
```
1. 选择 Uniswap V3 USDC/ETH 0.05% pool (0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640)
2. 当前价格: ~$3,200/ETH → 10 ETH = $32,000
3. 双边流动性: 10 ETH 配对 32,000 USDC (共 $64,000)
4. 剩余 18,000 USDC 可保留或投入更低 fee tier pool
5. 价格区间: [2930, 3560] (当前价的 ±10%)
6. 调用 addLiquidity(amount0Desired=32000000000, amount1Desired=10000000000000000000, tickLower=-887220, tickUpper=887220, ...)
7. Gas 预估: ~200,000 gas × 15 Gwei = 0.003 ETH
```

---

### Query #2 [难度: L2 Medium]

**Query**:
> 钱包 `0x50d3865a63d52c0a54e4679949647ea752107390` (Cross_Protocol_Power_User, 交易量 $7B+, 16 个 DEX, 2 个借贷协议) 希望将其 500 ETH 的部分仓位从纯持有转换为收益策略。要求：至少覆盖 2 个协议（一个质押 + 一个借贷），年化目标 >4%，最大回撤控制在 15% 以内，不接受未审计协议。

**约束清单**:

| 约束类型 | 约束项 | 内容 |
|---------|-------|------|
| Hard | Budget | ≤500 ETH |
| Hard | 收益要求 | 年化 >4% |
| Hard | 协议数量 | ≥2 |
| Hard | 风控规则 | 禁止未审计协议，禁止新项目（TVL < $100M） |
| Hard | 最大回撤 | 15% |
| Commonsense | 合理协议路线 | 质押品 → 借贷协议的路径必须可行（stETH 可作 Aave 抵押品） |
| Commonsense | 资产多样性 | 不把全部 ETH 换成一个收益源 |
| Commonsense | 锁仓期 | 质押协议若有锁仓期需在方案中说明 |
| Environment | — | 若 Lido queue 拥堵（提款排队>1天）需标记风险 |

**参考 Plan**:
```
1. 300 ETH → Lido staking (stETH)
   - 调用: Lido.submit{value: 300 ETH}
   - 预期年化: ~3.5% (Lido APR)
   - 锁仓期: 无（stETH 可即刻流通）

2. stETH → Aave V3 存入作抵押品
   - 调用: Aave.supply(stETH, 300)
   - 健康因子目标: >2.0 (保守)
   - 年化: ~0.05% (stETH supply APR)

3. 200 ETH 保留在钱包，视市场条件决定后续操作
   - 若 ETH 价格下跌 >15%，stETH 自动贬值 → 需关注健康因子

4. 总年化估算: 300 ETH × 3.5% / 500 ETH = ~2.1% (仅 staking)
   达不到 4% 目标 → 需引入 Yield 协议或 Curve LP
   备选: 100 ETH → Curve stETH/ETH pool LP → Convex 质押
   增加后预期年化: ~5%

5. 最大回撤风险: stETH/ETH depeg 风险 (<0.5% 历史), Aave 清算风险 (健康因子>2 安全)
```

---

### Query #3 [难度: L2 Medium]

**Query**:
> 钱包 `0xae2fc483527b8ef99eb5d9b44875f005ba1fae13` (Institutional_Whale, 交易量 $29.9B, avg_trade_size $68,010) 检测到其 Aave 上的 USDC 借款利率在最近 3 小时内从 2.5% 飙升至 12.3%。请为该地址生成一个在 24 小时内执行的债务重组方案：最小化利息成本，同时不被清算（健康因子从 1.35 提升到 >1.8）。

**约束清单**:

| 约束类型 | 约束项 | 内容 |
|---------|-------|------|
| Hard | 时间窗口 | 24 小时 |
| Hard | 健康因子目标 | >1.8 |
| Hard | 成本优化 | 最小化交易 Gas + 滑点 |
| Hard | 协议偏好 | 可使用 Aave + 1 个 DEX |
| Commonsense | 非冲突操作 | 不可在还款的同时借出更多 |
| Commonsense | 合理 Gas 策略 | 不选 Gas Price >50 Gwei 的时段 |
| Commonsense | 价格影响 | 大额交易用聚合器避免滑点 |
| Environment | 利率变化 | 若 USDC 利率继续上升则方案需说明 Plan B |

**参考 Plan**:
```
当前状态 (假设):
- 抵押品: 1,000 stETH ($3,200,000)
- 债务: 2,000,000 USDC
- 健康因子: 1.35
- USDC 借款利率: 12.3% (variable)

方案:
1. 从钱包转 500,000 USDC 到 Aave
2. repay(USDC, 500000000000) → 债务降至 1,500,000 USDC
3. 健康因子重算: 3,200,000 × 0.75 / 1,500,000 = 1.6 (仍未达标)

4. 继续 repay 500,000 USDC → 债务降至 1,000,000 USDC
   健康因子: 3,200,000 × 0.75 / 1,000,000 = 2.4 ✓

5. 或者: 用 1inch 将 100 ETH 换为 USDC → 约 320,000 USDC
   → repay(USDC, 320000000000)
   健康因子: 3,200,000 × 0.75 / 1,000,000 = 2.4 ✓

6. Gas 预估: approve + repay × 2-3 txs ≈ 0.005 ETH
   建议在 Ethereum gas <30 Gwei 时执行

Plan B (若 USDC 利率持续上升):
   考虑用 Compound 的 USDC 借款替代 (若 Compound 利率更低)
   步骤: Compound.borrow(USDC) → 偿还 Aave 债务 → 完成再融资
```

---

### Query #4 [难度: L3 Hard]

**Query**:
> 2025 年 2 月 21 日 14:00 UTC，Bybit 冷钱包被盗 15 亿美元 ETH（攻击手法：Safe 多签 UI 欺骗）。你是钱包 `0x63242a4ea82847b20e506b63b0e2e2eff0cc6cb0` (Institutional_Whale) 的风险管理 Agent。请生成一份紧急响应方案：从 3 条链（Ethereum、Arbitrum、Base）上的 5 个协议中撤出流动性，转移到安全的冷钱包 `0x5141b82f5ffda4c6fe1e372978f1c5427640a190`。要求：24 小时内完成，Gas 成本 <5 ETH，不触发大额交易预警（单笔 <10M USD）。

**约束清单**:

| 约束类型 | 约束项 | 内容 |
|---------|-------|------|
| Hard | 时间窗口 | 24 小时 |
| Hard | 源链 | Ethereum + Arbitrum + Base |
| Hard | 目标地址 | 0x5141... |
| Hard | Gas 上限 | <5 ETH 总 Gas |
| Hard | 单笔上限 | 单笔 <$10M |
| Hard | 协议数 | 最少 3 个不同协议 |
| Commonsense | 跨链合理性 | 不能跳过桥直接跨链 |
| Commonsense | 滑点控制 | 用 1inch 聚合器执行大额 swap |
| Commonsense | 应急速度 | 优先提取易受攻击的协议 |
| Environment | 桥接拥堵 | 若跨链桥拥堵，需排队时间预估 |

**参考 Plan**:
```
风险评估优先级:
  高优: Safe 多签相关仓位 (任何通过 Gnosis Safe 管理的资产)
  中优: 可升级代理合约的协议 (Aave, Compound 安全)
  低优: 不可变合约的协议 (Uniswap V3 pool)

Step 1: Ethereum (预计 Gas: 1.5 ETH)
  - Aave V3: withdraw(USDC, full) → 约 $8M
    分 2 笔: $5M + $3M (避单笔上限)
  - Uniswap V3: decreaseLiquidity + collect → 约 $12M
    分 3 笔: $4M + $4M + $4M
  - Lido: requestWithdrawals(100 stETH) → 需排队 (标记)

Step 2: Arbitrum (预计 Gas: 0.3 ETH)
  - GMX: decreasePosition → 约 $3M
  - 通过 Across Bridge 将资金桥接到 Ethereum → $3M

Step 3: Base (预计 Gas: 0.2 ETH)
  - Aerodrome: removeLiquidity → 约 $2M
  - 通过 Across Bridge → Ethereum → $2M

Step 4: 汇总到冷钱包
  - Ethereum 上收集所有资金
  - 分 5 笔 transfer 到 0x5141... ($8M + $12M + $3M + $2M = $25M)
    每笔 ≤$5M，间隔 10 分钟

总 Gas: ~1.5 + 0.3 + 0.2 + 1.0 (汇总) = 3.0 ETH ✓
时间: ~6 小时 (不含 Lido 提款排队)
```

---

### Query #5 [难度: L1 Easy]

**Query**:
> 钱包 `0x0bb7a4fdea32910038dec59c20ccae3a6e66b09f` (Cross_Protocol_Power_User, 16 DEX, 1 借贷协议) 当前在 Compound 上存有 50,000 USDC (cUSDC)。请推荐：继续在 Compound 赚取 2.3% 年化，还是迁移到 Aave V3 ETH 赚取 4.1% 年化？需包含完整操作步骤。

**约束清单**:

| 约束类型 | 约束项 | 内容 |
|---------|-------|------|
| Hard | 资产 | 50,000 USDC |
| Hard | 协议选项 | Compound / Aave V3 |
| Hard | 决策标准 | 年化收益率比较 |
| Commonsense | Gas 成本 | 迁移成本必须 < 收益增量 |
| Commonsense | 协议风险 | 比较两协议的安全审计历史 |
| Environment | — | 若 Aave 利率在迁移过程中下降，需说明 |

**参考 Plan**:
```
当前状态:
  Compound: cUSDC (50,000 USDC), APR 2.3%
  年化收益: 50,000 × 2.3% = $1,150

迁移后:
  Aave V3: USDC deposit, APR 4.1%
  年化收益: 50,000 × 4.1% = $2,050
  增量: $900/年

迁移步骤:
1. Compound.withdraw(cUSDC, 50000000000) → 50,000 USDC 回到钱包
   Gas: ~150,000

2. USDC.approve(AavePool, 50000000000)
   Gas: ~46,000

3. Aave.supply(USDC, 50000000000)
   Gas: ~250,000

总 Gas: ~446,000 × 15 Gwei = 0.0067 ETH ≈ $21

盈亏分析: $900 - $21 = $879 净收益 → 推荐迁移

协议风险对比:
  - Compound: 已审计，无安全事故，TVL $2.5B
  - Aave V3: 已审计 (Sigma Prime, Trail of Bits)，无安全事故，TVL $12B
  → 两者风险相当

Plan B: 若 Aave USDC 利率降至 <2.5%，保留 Compound 方案
```

---

## 格式说明

### 与 TravelPlanner 的对应关系

| TravelPlanner | KDWAS |
|---------------|-------|
| `CitySearch`, `FlightSearch`, ... (6 tools) | Dune 链上查询、DefiLlama TVL、价格 Oracle、地址画像、协议审计、Gas 预测 (6 tools) |
| Budget / Room Type / Cuisine (Hard constraints) | 预算上限 / 资产类型 / 协议偏好 / 链偏好 / 最大回撤 |
| Within Sandbox / Complete Info / ... (Commonsense) | 链上可验证 / 完整财务计划 / 资金流可行 / 非冲突仓位 / 锁仓期 |
| Unavailable Transportation (Environment) | 无流动性 / 跨链桥拥堵 / 利率波动 |
| 1,225 query-plan pairs | 目标 500+ pairs（先做 5 条 demo） |
| 4 evaluation metrics | 4 评估指标 (Delivery/Commonsense/Hard/Final) |
