# KDWAS Dataset Documentation

Datasets for the Knowledge-Driven Wallet Agent System (KDWAS) paper. This document describes each dataset, its source, schema, collection methodology, and relationship to the proposed experiments.

---

## Directory Structure

```
data/
├── README.md
├── raw/
│   ├── protocol_list.csv        # Top 20 protocols by TVL (DefiLlama)
│   ├── defi_tvl.csv             # Top 25 DeFi protocols with TVL (DefiLlama)
│   └── security_events.csv      # 20 major DeFi security events (manual)
└── processed/
    ├── wallet_profiles.csv      # 50 classified wallet addresses (Dune)
    ├── selected_addresses.csv   # 14 representative wallets per archetype
    ├── wallet_swap_ts.csv       # DEX swap time-series for selected wallets (Dune)
    └── wallet_lending_ts.csv    # Lending borrow/repay time-series (Dune)
```

---

## 1. Protocol List (`raw/protocol_list.csv`)

**Source**: [DefiLlama API](https://defillama.com/docs/api) — `GET /protocols`

**Description**: Top 20 protocols by total value locked (TVL), including both DeFi protocols and centralized exchanges (CEX). Provides the overall landscape of capital concentration in crypto.

**Collection method**: `curl https://api.llama.fi/protocols` and select top 20 by TVL.

**Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Protocol display name |
| `symbol` | string | Native token ticker |
| `category` | string | Protocol category (CEX, Liquid Staking, Lending, DEX, Bridge, CDP, etc.) |
| `chain` | string | Primary blockchain |
| `tvl` | float | Total value locked in USD |
| `slug` | string | DefiLlama identifier |

**Record count**: 20

**KDWAS relevance**: Used for constructing the Dynamic Financial Knowledge Graph's Protocol nodes. The protocol categories directly inform the Financial Semantic Reasoning engine's protocol dependency modeling (Section 5.1).

---

## 2. DeFi Protocol TVL (`raw/defi_tvl.csv`)

**Source**: [DefiLlama API](https://defillama.com/docs/api) — `GET /protocols`

**Description**: Top 25 DeFi protocols (excluding CEXes and bridges) ranked by TVL. Covers Liquid Staking, Lending, DEX, CDP, Yield, Derivatives, and Restaking categories across multiple chains.

**Schema**: Same as `protocol_list.csv`.

**Record count**: 25

**KDWAS relevance**: Directly populates the DeFi Protocol nodes in DFKG. The cross-chain and cross-category relationships inform protocol dependency edge construction. Used in Experiment 8.1 (Financial Reasoning Evaluation) to test whether the agent correctly understands protocol relationships.

---

## 3. Security Events (`raw/security_events.csv`)

**Source**: Manual compilation from [Rekt News](https://rekt.news/) leaderboard and public post-mortem reports.

**Description**: 20 major DeFi security incidents spanning 2021–2025, covering bridges, lending protocols, DEXes, CEXes, yield aggregators, and market makers. Includes the Bybit hack (Feb 2025, $1.5B), Ronin Bridge exploit (Mar 2022, $624M), and FTX collapse (Nov 2022, $8.5B).

**Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Incident name |
| `date` | date | Date of incident (YYYY-MM-DD) |
| `amount_m` | float | Loss amount in millions USD |
| `category` | string | Protocol category affected |
| `chain` | string | Blockchain(s) affected |
| `technique` | string | Attack technique (Flash Loan, Oracle Manipulation, Private Key Leak, etc.) |
| `protocol_affected` | string | Primary protocol impacted |
| `reference` | string | Rekt News article URL |

**Record count**: 20

**KDWAS relevance**: This dataset is critical for Experiment 8.1 (Risk Hedging) and Section 5.2 (Causal Financial Reasoning). The events serve as ground truth for:
- Risk propagation path validation in DFKG
- Testing whether the Neuro-Symbolic engine correctly identifies cascading risk patterns
- Training the Constraint-Aware Planning module to recognize attack signatures

**Attack technique distribution**:

| Technique | Count |
|-----------|-------|
| Private Key Leak | 4 |
| Flash Loan Attack | 3 |
| Oracle Manipulation | 3 |
| Smart Contract Bug | 2 |
| Validator Compromise | 1 |
| Signature Forgery | 1 |
| Frontend Injection | 1 |
| Governance Attack | 1 |
| Price Manipulation | 1 |
| UI Spoofing / Social Engineering | 1 |
| Fraud | 1 |
| Reentrancy | 1 |

---

## 4. Wallet Profiles (`processed/wallet_profiles.csv`)

**Source**: [Dune Analytics](https://dune.com) — `dex.trades` and `lending.borrow` spell tables. Query ID: 7536798.

**Description**: 50 active DeFi wallet addresses with 12-month aggregated behavioral profiles. Each address is classified into one of 4 archetypes based on on-chain activity patterns.

**Collection method**: SQL query against Dune's spellbook tables over the period 2025-05-01 to 2026-05-01, filtering for wallets with swap_count >= 100,000 to focus on high-activity users.

**Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | Wallet address (0x...) |
| `swap_count` | int | Total DEX swap transactions |
| `total_volume` | float | Total USD volume across all DEX trades |
| `dex_projects` | int | Number of distinct DEX protocols used |
| `active_days` | int | Number of days with at least 1 swap |
| `avg_trade_size` | float | Average trade size in USD |
| `total_lend_txs` | int | Total lending transactions (borrow + repay) |
| `total_lend_volume` | float | Net lending volume in USD |
| `lend_projects` | int | Number of distinct lending protocols used |
| `lend_active_days` | int | Number of days with lending activity |
| `profile` | string | Archetype label |

**Record count**: 50

### Archetype Classification Methodology

Addresses are classified into 4 archetypes using heuristic thresholds derived from on-chain behavior:

| Archetype | Criteria | Behavioral Interpretation |
|-----------|----------|--------------------------|
| **MEV_HFT** | active_days >= 300, swap_count >= 1,000,000, avg_trade_size < $5,000 | High-frequency, low-value trading. Likely MEV bots or algorithmic traders executing thousands of small trades daily. |
| **Institutional_Whale** | total_volume >= $5B, avg_trade_size >= $10,000 | Very large single trades. Likely institutional desks, market makers, or high-net-worth individuals executing block trades. |
| **Cross_Protocol_Power_User** | dex_projects >= 10, lend_projects >= 1 | Diversified across many protocols. Sophisticated DeFi users who interact with the entire ecosystem including both DEX and lending. |
| **Protocol_Loyalist** | dex_projects <= 3, active_days >= 200 | Highly active but concentrated on few protocols. Users deeply embedded in specific protocol ecosystems, relevant for governance analysis. |

**Archetype distribution**:

| Profile | Count |
|---------|-------|
| Cross_Protocol_Power_User | ~20 |
| Institutional_Whale | ~12 |
| MEV_HFT | ~10 |
| Protocol_Loyalist | ~8 |

**KDWAS relevance**: These wallet profiles are the primary data source for the user modeling component of DFKG. The archetypes serve as Wallet Identity nodes and provide the behavioral baselines for:
- Experiment 8.1: Testing whether KDWAS maintains archetype-appropriate risk preferences
- Experiment 8.2: Long-term memory evaluation — does the agent remember a user's archetype-consistent preferences over long time horizons?
- Section 5.3: Constraint-Aware Planning — each archetype implies different risk constraints

---

## 5. Selected Addresses (`processed/selected_addresses.csv`)

**Source**: Subset of `wallet_profiles.csv`, manually selected for best representativeness.

**Description**: 14 wallet addresses selected as the most representative examples of each archetype for detailed time-series analysis.

**Schema**: Same as `wallet_profiles.csv`.

**Record count**: 14

**Selection**: ~4 per archetype, chosen to maximize behavioral diversity within each archetype (different chains, protocols, volume ranges).

**KDWAS relevance**: These addresses are the targets for the time-series datasets below and serve as the primary test subjects for the experimental evaluation.

---

## 6. Wallet Swap Time-Series (`processed/wallet_swap_ts.csv`)

**Source**: [Dune Analytics](https://dune.com) — `dex.trades` spell table. Query ID: 7536842, Execution ID: `01KRZRNJBCCQQVXQ7E627PM953`.

**Description**: Daily DEX swap activity for 10 selected wallet addresses, broken down by blockchain and DEX protocol. Each row represents one wallet's activity on one protocol on one blockchain on one day.

**Collection method**:
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

**Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | Wallet address |
| `block_date` | date | Date of trading activity |
| `project` | string | DEX protocol name |
| `blockchain` | string | Blockchain network |
| `daily_swaps` | int | Number of swap transactions |
| `daily_volume_usd` | float | Total USD volume |
| `tokens_bought` | int | Distinct tokens bought |
| `tokens_sold` | int | Distinct tokens sold |
| `avg_trade_size` | float | Average trade size in USD |

**Record count**: 100

**Covered protocols**: Uniswap, Curve, PancakeSwap, SushiSwap, Aerodrome, 1inch, Maverick, Fluid, KyberSwap, FraxSwap, Velodrome, Camelot, DODO, Bancor, ShibaSwap, Quickswap, AlienBase, BaseSwap, HorizonDEX, DefiSwap, Verse DEX, Solidly

**Covered chains**: Ethereum, Arbitrum, Base, Optimism, Polygon

**KDWAS relevance**: Primary dataset for:
- Experiment 8.1 (Financial Reasoning): Can KDWAS infer the wallet's archetype and predict behavior?
- Experiment 8.2 (Long-Term Memory): Can the agent maintain context across multi-day trading sequences?
- DFKG construction: Transaction Flow edges between Wallet and Protocol nodes

---

## 7. Wallet Lending Time-Series (`processed/wallet_lending_ts.csv`)

**Source**: [Dune Analytics](https://dune.com) — `lending.borrow` spell table. Query ID: 7536849, Execution ID: `01KRZRPWBFC5ZJ5PVYWR8BEFJQ`.

**Description**: Daily lending borrow and repay activity for 10 selected wallet addresses on Aave (Ethereum). Each row represents one token's borrow or repay activity on one day.

**Collection method**:
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

**Schema**:

| Field | Type | Description |
|-------|------|-------------|
| `address` | string | Wallet address |
| `block_date` | date | Date of activity |
| `project` | string | Lending protocol name |
| `blockchain` | string | Blockchain network |
| `transaction_type` | string | `borrow` or `repay` |
| `loan_type` | string | `variable` for borrow, empty for repay |
| `symbol` | string | Token symbol borrowed/repaid |
| `daily_count` | int | Number of transactions |
| `daily_volume_usd` | float | USD volume (positive for borrow, negative for repay) |

**Record count**: 100

**Covered tokens**: USDT, USDC, DAI, GHO, crvUSD, wstETH, cbETH, osETH, LINK, tBTC, cbBTC, USDe, USDS, EURC

**KDWAS relevance**: This data enables the lending-specific portion of:
- Experiment 8.1: Protocol Understanding Accuracy — does the agent understand the risk implications of borrowing volatile tokens (e.g., tBTC, LINK) vs. stablecoins?
- Section 5.3 (Constraint-Aware Planning): Testing whether the agent correctly applies leverage constraints based on historical borrow/repay patterns
- Risk propagation modeling in DFKG: Borrow/repay patterns reveal which assets users use as collateral and how liquidation cascades could propagate

---

## Data Pipeline Summary

```
DefiLlama API                    Dune Analytics (Spellbook)
     │                                    │
     ├─ GET /protocols                    ├─ dex.trades (query 7536842)
     │  └─ protocol_list.csv              │  └─ wallet_swap_ts.csv
     │  └─ defi_tvl.csv                   │
     │                                    ├─ lending.borrow + lending.repay (query 7536849)
     │                                    │  └─ wallet_lending_ts.csv
     │                                    │
     │                                    └─ User profile aggregation (query 7536798)
     │                                       └─ wallet_profiles.csv
     │                                          └─ (manual selection)
     │                                             └─ selected_addresses.csv
     │
Manual Compilation
     │
     └─ Rekt News leaderboard
        └─ security_events.csv
```

---

## Reproducibility

### Prerequisites
- Dune Analytics account with API key (for Dune queries)
- DefiLlama API is free and rate-limited at ~100 req/min (no key needed)
- Python 3.x with `csv` standard library

### Re-running the Dune queries

**Swap time-series** (Dune Query 7536842):
1. Update the address list in the WHERE clause with target wallets
2. Adjust the time window as needed
3. Execute via Dune MCP: `executeQueryById(7536842)`
4. Retrieve results: `getExecutionResults(<execution_id>)`

**Lending time-series** (Dune Query 7536849):
1. Same as above, update addresses and time window
2. Execute: `executeQueryById(7536849)`

**Wallet profiles** (Dune Query 7536798):
1. Adjust `swap_count >= N` threshold to control sample size
2. Update the 12-month window if needed

### Re-running the DefiLlama data
```bash
curl -s "https://api.llama.fi/protocols" | jq '.[] | select(.tvl > 1e9)'
```

### Re-running the classification
The Python classification script is at `/tmp/save_data.py`. It uses the thresholds described in Section 4 above. Adjust thresholds based on the population distribution.

---

## Dataset Relationships to KDWAS Modules

| Dataset | DFKG (Section 4) | Neuro-Symbolic Reasoning (Section 5) | Coordination (Section 6) | Provenance (Section 7) | Experiments (Section 8) |
|---------|-------------------|--------------------------------------|--------------------------|------------------------|--------------------------|
| protocol_list.csv | Protocol nodes | Protocol dependency reasoning | Shared world model | Protocol state audit | 8.1 Protocol Understanding |
| defi_tvl.csv | Protocol nodes + TVL edges | Capital flow reasoning | Liquidity state sharing | TVL change tracing | 8.1 Portfolio Management |
| security_events.csv | Market Event nodes | Causal risk reasoning (5.2) | Risk event broadcasting | Risk traceability | 8.1 Risk Hedging |
| wallet_profiles.csv | Wallet Identity nodes | User preference constraints (5.3) | Agent identity sharing | Preference consistency audit | 8.2 Memory Retention |
| selected_addresses.csv | Target wallet nodes | Test subject selection | — | — | All experiments |
| wallet_swap_ts.csv | Transaction Flow edges | Financial behavior reasoning | Semantic state exchange | Action provenance | 8.1, 8.2 |
| wallet_lending_ts.csv | Protocol Dependency edges | Constraint-aware planning (5.3) | Risk coordination | Constraint verification | 8.1, 8.3 |

---

## Known Limitations

1. **Dune row limits**: Both time-series datasets are capped at 100 rows. Full-scale experiments require paginating through all results or exporting via Dune's CSV export.
2. **Single lending protocol**: The lending time-series covers only Aave on Ethereum. Multi-protocol lending data requires expanding the query.
3. **No governance data**: Governance participation (DAO voting, proposal creation) is not yet included. This would require querying governance-specific tables.
4. **Archetype classification is heuristic**: The thresholds are manually chosen. A more rigorous approach would use clustering (k-means on normalized behavioral features).
5. **Security events are manually curated**: Not from a real-time feed. For production use, integrate with real-time monitoring APIs.
6. **TVL data is point-in-time**: DefiLlama data reflects TVL at query time. Historical TVL time-series would require the DefiLlama historical API endpoints.

---

## Next Steps for Dataset Expansion

- [ ] Pull governance participation data from Boardroom/Snapshot APIs
- [ ] Add cross-chain bridge transaction data
- [ ] Pull historical TVL time-series from DefiLlama `/protocol/{slug}` endpoints
- [ ] Expand wallet sample to 500+ addresses with clustering-based archetype discovery
- [ ] Add liquidation event data from `lending.liquidation` spell table
- [ ] Add yield/strategy data for yield-bearing positions
