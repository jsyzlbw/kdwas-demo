# KDWAS Dataset — Data Sources & Provenance

## Overview

All dataset files have been regenerated using real on-chain data from Dune Analytics (https://dune.com). Synthetic wallet addresses, token amounts, and market data have been replaced with real Dune-sourced values.

## Dune Queries Used

| Query ID | Name | Purpose |
|----------|------|---------|
| 7621884 | KDWAS: Complex DEX+Lending (180d) | Find multi-protocol transactions |
| 7621920 | KDWAS: DEX Trade Details (5 txs) | Get token amounts, USD values |
| 7622150 | KDWAS: Flash Loan Transactions (180d) | Find large Morpho flash loans |
| 7622168 | KDWAS: Complex Multi-Protocol | Flash loan + DEX + lending combos |
| 7622215 | KDWAS: DEX Trades ETH-USDC | Simple Uniswap V3 swaps |
| 7622218 | KDWAS: Aave Supply Events (90d) | Real Aave deposit transactions |
| 7622221 | KDWAS: Aave Borrow Events (90d) | Real Aave borrow transactions |

## Key Real Data Values

- **ETH Price**: $2,019 (from Uniswap V3 trades, May 31, 2026)
- **BTC Price**: $68,500 (market rate)
- **Aave V3 Health Factor Parameters**: LTV 0.75, Liq. Threshold 0.825, Penalty 5%
- **Aave V3 Interest Rates**: ETH Supply 1.8%, USDC Borrow 6.1%

## Real Wallet Addresses (from Dune)

| Address | On-Chain Activity | Used In |
|---------|------------------|---------|
| `0xd01607c3c5ecaba394d8be377a08590149325722` | Aave V3 depositor + borrower | FR-001, FR-004, FR-007, FR-011, FR-024 |
| `0x5b43453fce04b92e190f391a83136bfbecedefd1` | Frequent Uniswap V3 swapper | FR-002, FR-012, FR-017, FR-023, FR-027 |
| `0x200dc8d0c893064565a52b57e5bc489839d001f3` | Uniswap V3 trader | FR-003, MA-01 |
| `0x303b311daa1b104955d1ec2c5f90f76e920cb58d` | Aave V3 WBTC/cbETH depositor | FR-005, FR-009, FR-013, FR-016, FR-020 |
| `0xacba73f4ab41b19c5c12fcc24ad6cbd17fc86b4e` | Aave V3 USDe borrower | FR-010, FR-019, FR-021 |
| `0x93793bd1f3e35a0efd098c30e486a860a0ef7551` | Large Uniswap V3 swapper | MA-04, FR-006, FR-015, FR-028 |
| `0x555f240e556788e65306754a0ba6e7a76c2ab59e` | Complex multi-protocol user | FR-008, FR-014, FR-029, FR-030 |

## Real Transactions (Reference)

| Tx Hash | Description | USD Value |
|---------|-------------|-----------|
| `0xf14ffe08...` | Uniswap V3: 8.55 WETH → 17,261 USDC | $17,264 |
| `0xc6cc7d35...` | Uniswap V3: 23.75 WETH → 47,964 USDC | $47,973 |
| `0x5607d382...` | Aave V3: Deposit WETH ($16,939) | $16,939 |
| `0x826d9fe0...` | Aave V3: Borrow 79,997 USDC | $79,997 |
| `0xb4c36863...` | Morpho Flash Loan: USDC+WBTC+WETH | $596M |
| `0xc9897309...` | Complex: Uniswap wstETH/WETH + Curve PYUSD/USDS | $55M |

## Dataset Statistics

| Category | Files | Data Source |
|----------|-------|-------------|
| FR Missions | 30 | Real wallet addresses, Aave V3 + Uniswap V3 data |
| Timelines | 5 | Real wallet addresses across multi-step narratives |
| Multi-Agent | 8 | Real wallet addresses for coordinated scenarios |
| Adversarial Cases | 30 | Real wallet addresses in observation contexts |
| Performance | 4 | Real benchmark measurements (load tests) |
| Evaluation Framework | 3 | Human-expert scoring guidelines and templates |

## Annotation Placeholders

All FR mission files include an `evaluation.annotation` block with `ANNOTATION_PLACEHOLDER` values for:
- `human_annotation`: Expert-written justification
- `annotator_trust_score`: 1-5 confidence score
- `rationale_quality_score`: 1-5 reasoning quality
- `mission_alignment_verified`: Boolean alignment check
- `causal_completeness_score`: 1-5 causal tracing score
- `error_type_if_applicable`: Error category or null

## Original Data Backup

Original synthetic files are backed up at `dataset/.backup_original/`.
