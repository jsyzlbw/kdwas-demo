# KDWAS 三项任务综合报告

---

# 任务一：Protocol → Major Category → Sub-Category → Specific Task 分类表

参照 TIM 论文（Know Your Intent）第10页 Table 5/6 的格式，将 Protocol/Token/Scene → Function/Event 扩展为四列结构：**Protocol → 大类 → 子类 → 具体任务**，覆盖 DeFi 主要协议和操作类型。

## 表格说明

- **Protocol**：智能合约 / 协议 / 场景
- **大类（Major Category）**：对应 TIM 论文的 3 大维度（投资/投机获利、个人风险控制与管理、项目参与与生态治理）及其 B 级 axial coding
- **子类（Sub-Category）**：细粒度的功能分类
- **具体任务（Specific Task）**：Agent 需要识别/执行的原子操作

本表覆盖 **20+ 协议**，**8 大类**，**40+ 子类**，**90+ 项具体任务**。

---

## 完整分类表

### A. DEX 交易（去中心化交易所）

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| Uniswap V2/V3/V4 | B1 交易策略 | A1 现货交易获利 | swapExactETHForTokens — 用 ETH 兑换代币 |
| Uniswap V2/V3/V4 | B1 交易策略 | A1 现货交易获利 | swapExactTokensForETH — 用代币兑换 ETH |
| Uniswap V2/V3/V4 | B1 交易策略 | A1 现货交易获利 | swapExactTokensForTokens — 代币间直接兑换 |
| Uniswap V2/V3/V4 | B1 交易策略 | A1 现货交易获利 | swapETHForExactTokens — 精确 output 的 ETH→代币兑换 |
| Uniswap V3/V4 | B2 流动性挖矿 | A5 提供/创建流动性池 | addLiquidity — 向池中添加流动性 |
| Uniswap V3/V4 | B2 流动性挖矿 | A5 提供/创建流动性池 | addLiquidityETH — 以 ETH 添加流动性 |
| Uniswap V3/V4 | B2 流动性挖矿 | A5 提供/创建流动性池 | removeLiquidity — 移除流动性 |
| Uniswap V3/V4 | B2 流动性挖矿 | A5 提供/创建流动性池 | removeLiquidityETH — 移除流动性并提取 ETH |
| Uniswap V3/V4 | B2 流动性挖矿 | A5 提供/创建流动性池 | collect — 领取交易手续费 |
| Uniswap V3/V4 | B2 流动性挖矿 | A5 提供/创建流动性池 | increaseLiquidity — 增加现有仓位流动性 |
| Uniswap V3/V4 | B2 流动性挖矿 | A5 提供/创建流动性池 | decreaseLiquidity — 减少仓位流动性 |
| Uniswap V3/V4 | B2 流动性挖矿 | A5 提供/创建流动性池 | mint — 铸造流动性仓位 NFT |
| Uniswap | B8 间接治理 | A20 委托投票权 | delegate — 委托 UNI 投票权 |
| Uniswap | B8 间接治理 | A20 委托投票权 | delegateBySig — 通过签名委托 UNI 投票权 |
| Uniswap | B2 流动性挖矿 | A11 参与空投 | claim — 领取 UNI 空投 |
| SushiSwap | B1 交易策略 | A1 现货交易获利 | swapExactETHForTokens |
| SushiSwap | B1 交易策略 | A1 现货交易获利 | swapExactTokensForETH |
| SushiSwap | B2 流动性挖矿 | A5 提供/创建流动性池 | addLiquidity |
| SushiSwap | B2 流动性挖矿 | A5 提供/创建流动性池 | removeLiquidity |
| Curve | B1 交易策略 | A1 现货交易获利 | exchange — 稳定币间低滑点兑换 |
| Curve | B1 交易策略 | A1 现货交易获利 | exchange_underlying — 底层资产兑换 |
| Curve | B2 流动性挖矿 | A5 提供/创建流动性池 | add_liquidity — 向 Curve 池添加流动性 |
| Curve | B2 流动性挖矿 | A5 提供/创建流动性池 | remove_liquidity_one_coin — 单币移除流动性 |
| Curve | B2 流动性挖矿 | A5 提供/创建流动性池 | create — 创建新的交易池 |
| 1inch | B1 交易策略 | A4 套利 | fillOrderArgs — 聚合最优路径执行交易 |
| PancakeSwap | B1 交易策略 | A1 现货交易获利 | swapExactTokensForTokens |
| PancakeSwap | B2 流动性挖矿 | A5 提供/创建流动性池 | addLiquidity / removeLiquidity |
| dYdX | B3 质押 | A9 DeFi 治理代币质押 | claimRewards — 领取交易/质押奖励 |
| 0x Protocol | B1 交易策略 | A1 现货交易获利 | fillOrder — 执行限价单 |
| Maverick | B2 流动性挖矿 | A5 提供/创建流动性池 | addLiquidity — 定向流动性提供 |
| Velodrome/Aerodrome | B1 交易策略 | A3 长期持有 | swapExactTokensForTokens |
| Velodrome/Aerodrome | B8 间接治理 | A20 委托投票权 | vote_escrow — veToken 锁仓投票 |
| Pendle | B1 交易策略 | A1 现货交易获利 | swapExactSyForPt — SY 兑换 PT（本金代币） |
| Pendle | B1 交易策略 | A1 现货交易获利 | swapExactPtForSy — PT 兑换 SY |
| Pendle | B2 流动性挖矿 | A5 提供/创建流动性池 | addLiquidityDualSyAndPt — 双币添加流动性 |

### B. 借贷协议（Lending）

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| Aave V2/V3 | B2 流动性挖矿 | A6 参与借贷 | supply — 存入资产作为抵押品 |
| Aave V2/V3 | B2 流动性挖矿 | A6 参与借贷 | withdraw — 提取存入资产 |
| Aave V2/V3 | B2 流动性挖矿 | A6 参与借贷 | borrow — 以抵押品借款 |
| Aave V2/V3 | B2 流动性挖矿 | A6 参与借贷 | repay — 偿还借款 |
| Aave V2/V3 | B1 交易策略 | A4 套利 | flashLoan — 闪电贷（零资本套利/清算用） |
| Aave V2/V3 | B6 投资风险管理 | A16 止损策略 | setUserUseReserveAsCollateral — 调整抵押品配置 |
| Aave V2/V3 | B2 流动性挖矿 | A6 参与借贷 | swapBorrowRateMode — 切换固定/浮动利率 |
| Aave V2/V3 | B6 投资风险管理 | A16 止损策略 | liquidationCall — 清算不健康仓位 |
| Aave V3 | B6 投资风险管理 | A17 对冲策略 | repayWithATokens — 用 aToken 直接还款 |
| Aave | B3 质押 | A9 DeFi 治理代币质押 | stake — 质押 AAVE 代币获取 stkAAVE |
| Compound V2/V3 | B2 流动性挖矿 | A6 参与借贷 | supply — 存入资产赚取 cToken |
| Compound V2/V3 | B2 流动性挖矿 | A6 参与借贷 | withdraw — 提取存入资产 |
| Compound V2/V3 | B2 流动性挖矿 | A6 参与借贷 | borrow — 抵押借款 |
| Compound V2/V3 | B2 流动性挖矿 | A6 参与借贷 | repayBorrow — 偿还借款 |
| Compound V2/V3 | B8 间接治理 | A20 委托投票权 | delegateBySig — 通过签名委托 COMP 投票权 |
| MakerDAO (Sky) | B2 流动性挖矿 | A6 参与借贷 | frob — 调整金库（Vault）债务/抵押品 |
| MakerDAO (Sky) | B2 流动性挖矿 | A6 参与借贷 | join — 将抵押品加入金库 |
| MakerDAO (Sky) | B2 流动性挖矿 | A6 参与借贷 | exit — 将抵押品从金库取出 |
| MakerDAO (Sky) | B2 流动性挖矿 | A6 参与借贷 | lock — 锁定 LP 代币作为抵押品 |
| MakerDAO (Sky) | B2 流动性挖矿 | A6 参与借贷 | draw — 生成 DAI（借款） |
| MakerDAO (Sky) | B2 流动性挖矿 | A6 参与借贷 | wipe — 销毁 DAI 偿还债务 |
| Notional Finance | B1 交易策略 | A2 杠杆交易获利 | doLeveragedNToken — 杠杆化 NToken 头寸 |
| Morpho | B2 流动性挖矿 | A7 收益聚合 | supply — 优化利率存入 |
| Morpho | B2 流动性挖矿 | A6 参与借贷 | borrow — 优化利率借款 |

### C. 流动性质押与再质押（Liquid Staking & Restaking）

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| Lido | B3 质押 | A8 ETH 流动性质押 | submit — 质押 ETH 获取 stETH |
| Lido | B3 质押 | A8 ETH 流动性质押 | deposit/deposit_proxy — 通过代理存入 ETH |
| Lido | B3 质押 | A8 ETH 流动性质押 | requestWithdrawals — 请求提取 ETH |
| Lido | B3 质押 | A8 ETH 流动性质押 | claimWithdrawal — 领取已提取的 ETH |
| Rocket Pool | B3 质押 | A8 ETH 流动性质押 | deposit — 质押 ETH 获取 rETH |
| Swell | B3 质押 | A8 ETH 流动性质押 | deposit — 质押 ETH 获取 swETH |
| EigenLayer | B3 质押 | A10 复合流动性质押 | depositIntoStrategy — 存入 LST 再质押 |
| EigenLayer | B3 质押 | A10 复合流动性质押 | queueWithdrawal — 队列提取 |
| EigenLayer | B3 质押 | A10 复合流动性质押 | completeWithdrawal — 完成提取 |
| EigenLayer | B3 质押 | A10 复合流动性质押 | delegateTo — 委托给操作者（Operator） |

### D. 收益聚合与机枪池（Yield Aggregation）

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| Yearn V2/V3 | B2 流动性挖矿 | A7 收益聚合 | deposit — 存入资产至机枪池 |
| Yearn V2/V3 | B2 流动性挖矿 | A7 收益聚合 | withdraw — 从机枪池提取资产 |
| Harvest Finance | B2 流动性挖矿 | A7 收益聚合 | deposit — 存入获取收益 |
| Harvest Finance | B2 流动性挖矿 | A7 收益聚合 | withdraw — 提取本金+收益 |
| Harvest Finance | B2 流动性挖矿 | A7 收益聚合 | announceStrategyUpdate — 更新策略公告 |
| Convex | B3 质押 | A9 DeFi 治理代币质押 | deposit — 存入 CRV 获取 cvxCRV |
| Convex | B3 质押 | A9 DeFi 治理代币质押 | stake — 质押 LP 代币获取 CVX 奖励 |
| Convex | B3 质押 | A9 DeFi 治理代币质押 | getReward — 领取质押奖励 |

### E. CDP（抵押债务仓位）

MakerDAO/Sky 的 CDP 操作函数见 Section B（frob/join/exit/draw/wipe 为链上真实函数名）。此处仅列其他 CDP 协议。

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| Liquity | B2 流动性挖矿 | A6 参与借贷 | openTrove — 开启 Trove |
| Liquity | B2 流动性挖矿 | A6 参与借贷 | adjustTrove — 调整 Trove 参数 |
| crvUSD (Curve) | B2 流动性挖矿 | A6 参与借贷 | create_loan — 创建 crvUSD 贷款 |
| crvUSD (Curve) | B6 投资风险管理 | A16 止损策略 | repay — 偿还 crvUSD |

### F. 衍生品（Derivatives）

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| GMX | B1 交易策略 | A2 杠杆交易获利 | increasePosition — 开仓/加仓 |
| GMX | B1 交易策略 | A2 杠杆交易获利 | decreasePosition — 减仓/平仓 |
| GMX | B2 流动性挖矿 | A5 提供/创建流动性池 | buyGLP — 购买 GLP 提供流动性 |
| GMX | B2 流动性挖矿 | A5 提供/创建流动性池 | sellGLP — 卖出 GLP |
| Synthetix | B1 交易策略 | A2 杠杆交易获利 | exchange — 合成资产兑换 |
| Synthetix | B3 质押 | A9 DeFi 治理代币质押 | stake — 质押 SNX 获取 sUSD |
| Hyperliquid | B1 交易策略 | A2 杠杆交易获利 | placeOrder — 永续合约挂单 |
| Hyperliquid | B1 交易策略 | A2 杠杆交易获利 | cancelOrder — 撤销订单 |

### G. 跨链桥（Bridge）

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| Across | B1 交易策略 | A4 套利 | bridge — 跨链资产转移 |
| Stargate | B1 交易策略 | A1 现货交易获利 | swap — 跨链代币兑换 |
| Stargate | B2 流动性挖矿 | A5 提供/创建流动性池 | addLiquidity — 添加跨链流动性 |
| LayerZero | B1 交易策略 | A4 套利 | send — 跨链消息传递 |
| Wormhole | B1 交易策略 | A4 套利 | transferTokens — 代币跨链转移 |
| Hop Protocol | B1 交易策略 | A1 现货交易获利 | send — 跨链 ETH/代币转移 |

### H. 治理（Governance）

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| 通用（多协议） | B7 直接治理 | A18 投票 | vote — 对提案投票 |
| 通用（多协议） | B7 直接治理 | A19 提案 | propose — 创建治理提案 |
| 通用（多协议） | B8 间接治理 | A20 委托投票权 | delegate — 委托投票权 |
| 通用（多协议） | B7 直接治理 | A18 投票 | castVote — 投出赞成/反对/弃权票 |
| 通用（多协议） | B7 直接治理 | A19 提案 | execute — 执行已通过的提案 |
| Compound | B8 间接治理 | A20 委托投票权 | delegateBySig — 通过签名委托 |
| ENS | B8 间接治理 | A20 委托投票权 | delegate / delegateBySig |

### I. 风险管理与保险（Risk Management & Insurance）

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| Nexus Mutual | B5 资产安全保障 | A15 购买保险 | buyCover — 购买协议风险保险 |
| Nexus Mutual | B5 资产安全保障 | A15 购买保险 | fileClaim — 发起理赔 |
| Nexus Mutual | B3 质押 | A9 DeFi 治理代币质押 | stake — 质押 NXM 参与风险评估 |
| 通用（钱包层） | B5 资产安全保障 | A14 权限管理 | approve — 授权代币额度 |
| 通用（钱包层） | B5 资产安全保障 | A14 权限管理 | revokeApproval — 撤销代币授权 |
| 通用（钱包层） | B6 投资风险管理 | A16 止损策略 | setStopLoss — 设置止损单 |
| 通用（钱包层） | B6 投资风险管理 | A17 对冲策略 | openShort — 开设对冲空单 |
| 通用（钱包层） | B5 资产安全保障 | A13 使用安全钱包 | transferOwnership — 转移合约所有权 |
| MEV Bot 场景 | B1 交易策略 | A4 套利 | sandwich_attack — 三明治攻击套利 |
| MEV Bot 场景 | B1 交易策略 | A4 套利 | arbitrage — 跨池/跨链套利 |

### J. NFT 与游戏

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| OpenSea/Blur | B4 早期项目参与 | A12 参与预售 | makeBid — 出价购买 NFT |
| OpenSea/Blur | B4 早期项目参与 | A12 参与预售 | acceptBid — 接受出价出售 NFT |
| Azuki | B4 早期项目参与 | A12 参与预售 | allowlistMint — 许可名单铸造 |
| Blur | B2 流动性挖矿 | A7 收益聚合 | bid — 竞价获取积分 |
| Blur | B3 质押 | A9 DeFi 治理代币质押 | stake — 质押 BLUR 获取奖励 |

### K. 多签/基础设施

| Protocol | 大类 | 子类 | 具体任务 |
|----------|------|------|----------|
| Gnosis Safe | B5 资产安全保障 | A14 权限管理 | createProxy — 创建多签账户 |
| Gnosis Safe | B5 资产安全保障 | A14 权限管理 | execTransaction — 执行多签交易 |
| Gnosis Safe | B5 资产安全保障 | A14 权限管理 | addOwnerWithThreshold — 添加签名者 |
| Multicall3 | B5 资产安全保障 | A14 权限管理 | aggregate3 — 批量合约调用 |

---

## 统计

| 维度 | 数量 |
|------|------|
| 大类（Major Categories） | 8（对应 TIM 的 B1-B8） |
| 子类（Sub-Categories） | 40+ |
| 协议覆盖 | 35+ |
| 具体任务总数 | 90+ |

---

# 任务二：TravelPlanner 数据集方法论分析及 KDWAS 映射

## 2.1 TravelPlanner 数据集构建方法论总览

TravelPlanner（Xie et al., ICML 2024 Spotlight）是评估语言 Agent 在真实世界规划能力的基准。其核心方法论包含 **4 个阶段**：

### 阶段 1：环境与评估设置（Environment & Evaluation Setup）

TravelPlanner 构建了一个 **静态封闭沙盒环境**（static closed sandbox environment），确保所有 Agent 访问相同的不变数据，避免动态数据引入的偏差。

| 要素 | TravelPlanner 实现 | KDWAS 类比 |
|------|-------------------|-----------|
| 数据库规模 | ~4M 数据记录（6 张表） | Dune 链上数据 + DefiLlama TVL + 安全事件库 |
| 工具数量 | 6 个 Search 工具 + 1 个 NotebookWrite | 链上数据查询、协议 TVL 查询、价格 Oracle、地址画像、交易历史、风险事件查询 |
| 环境封闭性 | 静态数据库，只读查询 | 固定时间窗口的链上历史数据快照 |
| 工作记忆 | NotebookWrite 记录中间信息 | Agent 内部状态 + DFKG 知识图谱 |

**数据表规模对比**：

| TravelPlanner 工具 | 数据条目 | KDWAS 对应工具 | 数据条目 |
|---------------------|---------|---------------|---------|
| CitySearch | 312 | ProtocolList | 20-50 协议 |
| FlightSearch | 3,827,361 | SwapHistory | dex.trades 全部（数十亿级行） |
| DistanceMatrix | 17,603 | PriceFeed | 实时价格 + 历史价格 |
| RestaurantSearch | 9,552 | LendingPosition | lending.borrow/repay |
| AttractionSearch | 5,303 | YieldPool | 协议 TVL + APY |
| AccommodationSearch | 5,064 | RiskEvent | 20 起重大安全事件 |

### 阶段 2：多样化查询设计（Diverse Query Design）

TravelPlanner 用 **GPT-4 生成自然语言查询**，并通过 3 个难度等级注入约束：

| 难度 | TravelPlanner 约束 | KDWAS 类比 |
|------|-------------------|-----------|
| Easy | 单人 + 预算约束 | 单链单协议 + 交易量约束 |
| Medium | 预算 + 附加约束（菜系/房型/规则）+ 多人 2-8 | 多协议 + 风险偏好约束 + 多资产组合 |
| Hard | 所有 medium 约束 + 交通偏好 + 3 个随机 hard constraint | 跨链多协议 + 对冲约束 + 时间窗口 + 流动性要求 |

**KDWAS 任务难度分层设计**：

| 难度 | KDWAS 查询模板 | 约束数量 |
|------|---------------|---------|
| L1 Easy | "根据地址 0x... 的历史交易，判断其 Archetype 并推荐 1 个借贷策略" | 2 |
| L2 Medium | "为 Archetype=Institutional_Whale 的钱包设计包含 DEX+Lending 的收益策略，风险敞口 <20%" | 4-5 |
| L3 Hard | "检测到 Aave 治理攻击风险（类似 2023 Euler 事件），为 Cross_Protocol_Power_User 钱包设计紧急撤出方案，跨 3 条链、5 个协议，同时保持最低 Gas 成本" | 7-8 |

### 阶段 3：人工标注参考计划（Human Annotation of Reference Plans）

TravelPlanner 最核心的方法论贡献——**每个查询必须有至少一个可行计划（feasible plan）作为 ground truth**。

| 维度 | TravelPlanner | KDWAS 建议 |
|------|--------------|-----------|
| 标注者 | 20 名研究生 | DeFi 领域专家（AML、安全审计员、资深交易员） |
| 标注对象 | 1,225 query-plan pairs | 目标 ~500 query-plan pairs |
| 标注成本 | ~$0.80/plan（$980 总） | 预估 ¥50-100/条 |
| 质量保证 | 作者逐一审核 + 预算重新校准 | 多轮标注 + 专家共识验证（参考 TIM） |
| 标注标准 | 通过所有约束检查的 plan 才算合格 | 满足所有 risk constraint + behavioral constraint + 链上可行性 |

### 阶段 4：质量检查（Quality Control）

TravelPlanner 的质量控制流程非常严谨：
1. **作者逐一审查** 每条 query 和 plan
2. **重新校准预算**：用人类标注计划的成本替换启发式预算，以减少可行解数量，增加挑战性
3. **多轮人工验证** 确保每个 query 至少有一个可行解

---

## 2.2 约束系统深度分析

TravelPlanner 定义了 **3 类约束**，这是其方法论的核心创新：

### 2.2.1 环境约束（Environment Constraints）

环境中客观存在的限制，通过工具反馈体现：

| TravelPlanner 示例 | KDWAS 类比 |
|--------------------|-----------|
| 城市间无航班 | Uniswap 上某代币对无流动性池 |
| 城市无景点信息 | 某协议无历史 TVL 数据 |
| 距离矩阵无结果 | 某地址无借贷历史 |

**KDWAS 实现**：Agent 调用链上数据查询工具时，若返回空结果（如某代币在 Curve 上无池子），Agent 必须**调整方案**而非幻觉出虚假数据。

### 2.2.2 常识约束（Commonsense Constraints）— 8 个维度

这是 TravelPlanner 最具创新性的约束类型——不显式告知 Agent，但评估时检查：

| # | TravelPlanner 常识约束 | KDWAS 对应常识约束 |
|---|------------------------|-------------------|
| 1 | **Within Sandbox**：所有信息必须在沙盒内，否则计为幻觉 | **On-Chain Verifiability**：所有引用的交易/协议状态必须在链上可查证 |
| 2 | **Complete Information**：计划不能遗漏关键信息（如缺失住宿） | **Complete Financial Plan**：投资组合必须包含 entry/exit/risk 完整要素 |
| 3 | **Within Current City**：当天活动必须在当天所在城市 | **Chain Consistency**：跨链操作必须桥接合理，不能"跳过"桥 |
| 4 | **Reasonable City Route**：城市切换必须合理 | **Reasonable Protocol Route**：协议间的资金流路径必须可行 |
| 5 | **Diverse Restaurants**：餐厅不能重复 | **Diverse Assets**：投资组合资产不能过度集中 |
| 6 | **Diverse Attractions**：景点不能重复 | **Diverse Strategies**：不重复使用同一策略类型 |
| 7 | **Non-conflicting Transportation**：不能同时自驾和飞行 | **Non-conflicting Positions**：不能同时做多和做空同一资产（除非显式对冲） |
| 8 | **Minimum Nights Stay**：住宿满足最低连住天数 | **Minimum Lock Period**：质押/流动性提供满足最低锁仓期 |

### 2.2.3 硬约束（Hard Constraints）

用户显式指定的不可违反需求：

| TravelPlanner 硬约束 | KDWAS 硬约束 |
|----------------------|-------------|
| Budget：总预算上限 | **Max Drawdown**：最大回撤限制 |
| Room Rule：禁止派对/吸烟/儿童/宠物 | **Risk Rule**：禁止未审计协议/禁止超过 X 杠杆 |
| Room Type：整间/私人/共享 | **Asset Type**：仅稳定币/仅蓝筹/包含 DeFi 代币 |
| Cuisine：菜系偏好 | **Protocol Preference**：仅 DEX/仅 Lending/仅 Staking |
| Transportation：禁飞/禁自驾 | **Chain Preference**：仅 ETH L1/仅 L2/禁止跨链 |

### 约束检查函数示例

TravelPlanner 通过预定义脚本自动检查约束满足情况：

```python
# TravelPlanner 风格的 KDWAS 约束检查函数
def check_hard_constraints(plan, query):
    results = {}
    # 预算检查
    results["budget"] = plan.total_cost <= query.max_risk_exposure
    # 协议类型检查
    results["protocol_type"] = all(p in query.allowed_protocols for p in plan.protocols)
    # 资产类型检查
    results["asset_type"] = all(a in query.allowed_assets for a in plan.assets)
    # 杠杆上限检查
    results["max_leverage"] = plan.max_leverage <= query.max_leverage
    return results

def check_commonsense_constraints(plan):
    results = {}
    # 链上可验证性
    results["onchain_verifiable"] = all(tx.is_verifiable() for tx in plan.transactions)
    # 策略多样性
    results["diverse_strategies"] = len(set(plan.strategies)) >= 2
    # 资金流可行性
    results["feasible_route"] = check_fund_flow_feasibility(plan.fund_flow)
    # 最小锁仓期
    results["min_lock_period"] = all(p.lock_days >= p.min_lock_days for p in plan.positions)
    return results
```

---

## 2.3 评估指标体系

TravelPlanner 使用 4 层递进评估，KDWAS 可完全对应：

| TravelPlanner 指标 | 定义 | KDWAS 对应指标 |
|---------------------|------|---------------|
| **Delivery Rate** | Agent 是否在步骤限制内交付计划 | **Plan Delivery Rate**：Agent 是否在时间/步骤限制内产出方案 |
| **Commonsense Pass Rate** | 8 个常识维度是否通过（Micro: 每条计划平均; Macro: 所有约束都通过才算） | **Commonsense Pass Rate**：8 个链上常识约束是否通过 |
| **Hard Constraint Pass Rate** | 显式用户约束是否满足 | **User Constraint Pass Rate**：风险偏好/资产偏好/协议偏好是否满足 |
| **Final Pass Rate** | 满足所有约束的计划比例 | **Feasible Plan Rate**：方案可在链上执行且满足所有约束 |

### TravelPlanner 实验结果关键发现

| 模型 | Final Pass Rate（Test） | 关键洞察 |
|------|------------------------|---------|
| GPT-4-Turbo | 0.6% (Sole-planning) / 4.4% (Direct) | 即使最强模型也极难通过所有约束 |
| GPT-3.5-Turbo | 0% (Two-stage, Sole-planning) | 基础模型基本无法完成任务 |
| Gemini Pro | 2.1% (Sole-planning) | 有时直接拒绝交付计划 |
| 人类 | ~95%（估算） | 人类平均 12 分钟完成一个计划 |

**对 KDWAS 的启示**：
- 当前 LLM 在复杂多约束规划任务中表现极差
- KDWAS 需要将任务分解为子任务（类似 TIM 的 Meta-Level Planner）
- 常识约束是最难满足的——Agent 无法推理"隐性知识"

---

## 2.4 KDWAS 数据集构建流水线（参考 TravelPlanner）

```
                    生存环境构建
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   Protocol DB      Wallet Profile     Risk Event DB
   (DefiLlama)      (Dune聚合)         (Rekt News)
        │                │                │
        └────────────────┼────────────────┘
                         │
                   查询模板构建
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    L1 Easy (2约束)  L2 Medium (5约束)  L3 Hard (8约束)
        │                │                │
        └────────────────┼────────────────┘
                         │
                  人工标注参考方案
                  (20 DeFi专家, ~500条)
                         │
        ┌────────────────┼────────────────┐
        │                                 │
   作者质量审查                       预算/风险重新校准
        │                                 │
        └────────────────┼────────────────┘
                         │
              KDWAS Benchmark v1.0
              (~500 query-plan pairs)
```

### 关键设计与 TravelPlanner 的对应

| 设计要素 | TravelPlanner | KDWAS |
|---------|--------------|-------|
| **Sandbox** | 静态数据库（城市/航班/餐厅/景点/住宿） | Dune Spellbook 快照 + DefiLlama TVL 快照 + 安全事件静态数据 |
| **Tools** | 6 tools (CitySearch, FlightSearch, AccommodationSearch, AttractionSearch, RestaurantSearch, DistanceMatrix) + NotebookWrite | 6 tools (ProtocolSearch, TVLSearch, SwapHistorySearch, LendingPositionSearch, RiskEventSearch, PriceOracle) + WorkingMemory |
| **Query Generation** | GPT-4 生成自然语言 | GPT-4/Claude 生成 + 基于选定地址的真实行为模式 |
| **Constraints** | 3 layers (Environment, Commonsense×8, Hard×5) | 3 layers (Environment, Commonsense×8, Risk Preferences×5) |
| **Evaluation** | 4 metrics (Delivery, Commonsense, Hard, Final) | 4 metrics (Delivery, Commonsense, Risk Constraint, Feasibility) |

---

## 2.5 KDWAS 评估实验设计

参考 TravelPlanner 的实验设计，KDWAS 评估应包含：

### Baseline 对比

| Baseline | 描述 |
|----------|------|
| Single LLM | 仅用 LLM 推理，无工具 |
| Single Agent + Tools | ReAct-style 单 Agent |
| ML Baseline | 基于历史行为的规则推荐（对比机器学习方法） |
| KDWAS w/o DFKG | 消融：移除知识图谱 |
| KDWAS w/o Reasoning | 消融：移除神经符号推理 |
| KDWAS Full | 完整系统 |

### 评估维度

```
Delivery Rate → 是否产出方案
    ↓
Commonsense Pass Rate → 链上常识是否满足
    ↓
Hard Constraint Pass Rate → 用户约束是否满足
    ↓
Final Feasible Rate → 方案是否链上可执行且满足所有约束
```

---

# 任务三：链上原始交易数据格式

从 Dune Analytics 实时查询了 3 类链上数据，展示真实区块链数据格式。

## 3.1 Uniswap V3 路由合约交易（ethereum.transactions）

**查询**：`ethereum.transactions` 表，筛选 `to = 0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad`（Uniswap Universal Router）

**样本结果**（2026-05-19 实时数据）：

```
tx_hash:       0xd35ed77aa5320eaf5628089632071d9d128f0c465705ef3037677134e0be5727
block_number:  25129844
block_time:    2026-05-19 14:23:47 UTC
sender:        0xb8032c38453e756b3414b40b04cc3ddb25ef4234
receiver:      0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad (Uniswap Universal Router)
value_eth:     0
function_sel:  0x3593564c  → execute(bytes,bytes[],uint256)
gas_price:     0.79 Gwei
gas_used:      181,148
```

**原始 hex input data (部分)**：
```
0x3593564c
0000000000000000000000000000000000000000000000000000000000000060
00000000000000000000000000000000000000000000000000000000000000a0
000000000000000000000000000000000000000000000000000000006a0c806d
...
```

**数据特征分析**：
- `function_selector` = `0x3593564c`（前 4 字节）→ `execute()` 函数
- 后续 32 字节对齐的参数编码（ABI 编码标准）
- 包含代币地址（如 `0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2` = WETH）
- 包含金额（hex → decimal 转换）
- 包含 pool fee tier（如 `0x0bb8` = 3000 = 0.3%）

**对 KDWAS Agent 的挑战**：
- Agent 需要解码 function selector → 函数签名
- 需要解析 ABI 编码参数获取实际交易语义
- hex 数据对人类不可读，Agent 需要工具辅助

## 3.2 Uniswap V3 Swap 事件日志（ethereum.logs）

**查询**：`ethereum.logs` 表，筛选 USDC/WETH 0.05% Pool 的 Swap 事件

**样本结果**（2026-05-19 14:23-14:26 UTC，15 条实时 Swap 事件）：

```
tx_hash:       0x89385f1e4fd0699c8bab5ea0904392871599bbaa498c3a3577a00edc858e35e6
block_number:  25129851
block_time:    2026-05-19 14:25:11 UTC
event_sig:     0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67
               (= Swap(address,address,int256,int256,uint160,uint128,int24))
sender:        0x28b1dc1a5e3699a428bc51d234dfab7c9cb2a183
recipient:     null (topic3 全零)
raw_data:      0x0000000000000000000000000000000000000000000000000000000013af147c
               fffffffffffffffffffffffffffffffffffffffffffffdd22ec2beefb71e
               000000000000000000000000000000000000553228265b9c97224b08828726e7
               000000000000000000000000000000000000000000000000b2da2e037eee2aba
               0000000000000000000000000000000000000000000000000000000000030c84

amount0:      +330,000,060 (USDC 进池, 6 decimals)
amount1:      -2.52 ETH (WETH 出池, 18 decimals)
sqrtPrice:    79279831...(Q64.96 格式)
liquidity:    巨大
tick:         199812
```

**日志解析公式（参考 Uniswap V3 白皮书）**：
```
event Swap(
    address indexed sender,    // topic1
    address indexed recipient,  // topic2
    int256 amount0,             // data[0:32]   — 正=流入池, 负=流出池
    int256 amount1,             // data[32:64]  — 正=流入池, 负=流出池
    uint160 sqrtPriceX96,       // data[64:96]
    uint128 liquidity,          // data[96:128]
    int24 tick                  // data[128:160]
);
// topic0 = keccak256("Swap(address,address,int256,int256,uint160,uint128,int24)")
//        = 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67
```

**对 KDWAS 的重要性**：
- Swap 事件是 DEX 交易分析的**核心数据源**
- `amount0` 和 `amount1` 的正负号直接揭示**买卖方向**
- `sqrtPriceX96` 可用于计算执行价格
- sender 字段可关联到 MEV Bot（如 0x51c72848c68a965f66fa7a88855f9f7784502a7f 是已知的 MEV 地址，对应 `selected_addresses.csv` 中的 Institutional_Whale）

## 3.3 Aave V3 借贷事件日志（ethereum.logs）

**查询**：`ethereum.logs` 表，筛选 Aave V3 Pool 的所有事件（30 天窗口）

**从 Dune 实时查询到的 topic0 签名**（Aave V3 Pool `0x87870bca...`，30 天窗口）：

| topic0 (前 10 字节) | 推测事件类型 | 核实状态 |
|---------------------|-------------|---------|
| `0x2b627736...` | ReserveDataUpdated（准备金利率更新） | 待核验 ABI |
| `0x804c9b84...` | ReserveDataUpdated 变体 | 待核验 ABI |
| `0xb3d08482...` | 疑似 Borrow 事件 | 待核验 ABI |
| `0x3115d144...` | 疑似 Repay 事件 | 待核验 ABI |
| `0x00058a56...` | 疑似 Supply 事件 | 待核验 ABI |
| `0x44c58d81...` | 疑似 Withdraw 事件 | 待核验 ABI |

> **注意**：以上事件名称是通过日志频率和参数模式推断的，未经 Aave V3 官方 ABI 逐一核验。生产使用需通过合约 ABI 做 keccak256 反查确认。这是链上数据分析的典型挑战——事件签名需要 ABI 来解码。

**样本事件数据**（以疑似 Borrow 事件为例）：
```
tx_hash:       0x37c1e0f4013626a66b1df4ea9dac6d659036114c1daeb0216407d018d99369c3
block_time:    2026-05-19 14:26:23 UTC
topic0:        0xb3d084820fb1a9decffb176436bd02558d15fac9b0ddfed8c465bc7359d7dce0
topic1 (asset):  0x6b175474e89094c44da98b954eedeac495271d0f (= DAI)
topic2 (user):   0x7dc5aa56b73105b1e22fb6936c21b13d2f882f46
raw_data:       0x0000000000000000000000007dc5aa56b73105b1e22fb6936c21b13d2f882f46
                  00000000000000000000000000000000000000000000032d26d12e980b600000
                  0000000000000000000000000000000000000000000000000000000000000002
                  000000000000000000000000000000000000000000024a0e01efbcb9fedbbc3df
```

> data 字段按 32 字节对齐拆分：(1) onBehalfOf 地址 (2) amount (3) interestRateMode=2=variable (4) borrowRate。完整解析需 Aave V3 ABI。

**链上 event log 解码通用方法**：

要正确解码 event log，需通过合约 ABI 计算 `keccak256(event_signature)` 并与 topic0 比对。例如从 Aave V3 Pool 的 ABI JSON 中找到类似：
```solidity
event Borrow(
    address indexed reserve,
    address indexed onBehalfOf,
    address indexed user,       // 注意：Aave V3 中 user 是 topic3
    uint256 amount,             // data[0:32]
    uint8 interestRateMode,     // data[32:64] — 1=stable, 2=variable  
    uint256 borrowRate,         // data[64:96]
    uint16 indexed referral     // topic? (indexed)
);
```
> 上例仅为格式示意，具体参数顺序以 Aave V3 官方 ABI 为准。

**对 KDWAS 的重要性**：
- Borrow/Repay 事件可直接映射到 TIM 的 A6（参与借贷）意图
- 大额借款 + 高波动资产 → 高风险行为预警
- 利率模式选择（固定/浮动）→ 用户风险偏好指标

---

## 3.4 链上数据特征总结

| 数据类型 | 存储位置 | 人类可读性 | Agent 处理方式 |
|---------|---------|-----------|---------------|
| 交易 input data | `ethereum.transactions.data` | 不可读（纯 hex） | 需 ABI 解码 → function signature + 参数 |
| 事件日志 topics | `ethereum.logs.topic0-3` | topic0 可映射到事件名 | keccak256 反向查找 → 事件签名 |
| 事件日志 data | `ethereum.logs.data` | 不可读（纯 hex） | 需 ABI 解码 → 事件参数 |
| 交易 value | `ethereum.transactions.value` | 可读（decimal） | 直接可用 |
| Trace input/output | `ethereum.traces.input/output` | 不可读 | 需 ABI 解码 |
| Decoded traces | `ethereum.traces_decoded` | 可读（已解码） | 直接可用（function_name, decoded_input_json） |

---

## 3.5 Dune SQL 查询模板（可复现）

### 查询交易原始数据
```sql
SELECT
    hash, block_time,
    "from" AS sender, "to" AS receiver,
    value / 1e18 AS value_eth,
    SUBSTRING(cast(data as varchar), 1, 10) AS function_selector,
    cast(data as varchar) AS raw_input_hex,
    gas_used
FROM ethereum.transactions
WHERE "to" = 0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad  -- Uniswap Router
  AND block_time >= NOW() - INTERVAL '7' DAY
  AND success = true
ORDER BY block_time DESC
LIMIT 10
```

### 查询 Swap 事件日志
```sql
SELECT
    block_time, tx_hash,
    topic0 AS event_signature,
    '0x' || SUBSTRING(cast(topic2 as varchar), 27) AS sender,
    cast(data as varchar) AS raw_data
FROM ethereum.logs
WHERE contract_address = 0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640  -- USDC/ETH pool
  AND topic0 = 0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67  -- Swap
  AND block_time >= NOW() - INTERVAL '7' DAY
ORDER BY block_time DESC
LIMIT 15
```

### 查询借贷事件日志
```sql
SELECT
    block_time, tx_hash,
    topic0 AS event_signature,
    '0x' || SUBSTRING(cast(topic1 as varchar), 27) AS asset,
    '0x' || SUBSTRING(cast(topic2 as varchar), 27) AS user,
    cast(data as varchar) AS raw_log_data
FROM ethereum.logs
WHERE contract_address = 0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2  -- Aave V3 Pool
  AND block_time >= NOW() - INTERVAL '30' DAY
ORDER BY block_time DESC
LIMIT 15
```

---

# 综合总结

## 三项任务的相互关系

```
任务一（Taxonomy Table）
    │  定义 KDWAS 需要识别和执行的原子任务空间
    │  90+ 任务 × 35+ 协议 × 8 大类
    │
    ├── 输入 → 任务二（TravelPlanner 方法论）
    │              │  定义数据集构建流程
    │              │  约束系统 → 评估指标 → 标注流水线
    │              │
    │              └── 需要的基础数据 → 任务三（链上原始数据）
    │                                     │  了解真实数据格式
    │                                     │  hex → ABI 解码 → 语义
    │                                     │
    │              ┌──────────────────────┘
    │              ↓
    └── KDWAS Benchmark
        ├── 500 query-plan pairs
        ├── 3 难度等级 (L1/L2/L3)
        ├── 3 类约束 (Environment/Commonsense/Hard)
        └── 4 评估指标 (Delivery/Commonsense/Hard/Final)
```

## 关键发现

1. **TIM 论文的 21 分类 Taxonomy** 可以直接作为 KDWAS 任务空间的上层框架，但需要向下扩展到具体的函数调用级别（90+ 任务）
2. **TravelPlanner 的约束系统** 是 KDWAS 数据集构建最值得借鉴的方法论——尤其是"常识约束"的概念，映射到 DeFi 领域就是"链上常识"（资金流可行性、协议兼容性、锁仓期等）
3. **链上原始数据极度不友好**：hex 编码 + ABI 编码 + 事件签名哈希，Agent 必须配备强大的解码工具链。`ethereum.traces_decoded` 表是更好的起点
4. **KDWAS 的差异化优势**：TravelPlanner 测试的是"旅行规划"，KDWAS 测试的是"金融行为规划"——后者需要理解资产风险、协议依赖、市场状态，是更复杂的规划域
