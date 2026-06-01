# KDWAS Pilot Dataset

Knowledge-Driven Wallet Agent System — 60-task Financial Reasoning Benchmark.

## Overview

This dataset supports the **Financial Reasoning Evaluation (§8.1)** of KDWAS: a 60-task multiple-choice benchmark comparing Vanilla / RAG / KDWAS-lite agents in a synthetic DeFi sandbox.

## Data Structure

```text
data/
├── tasks/
│   ├── blind.jsonl       # 60 tasks (agent-visible)
│   ├── gold.jsonl        # 60 gold evaluations (private, for scoring only)
│   └── CHANGELOG.md      # Freeze history (v1.0.0, 2026-05-25)
└── knowledge/
    ├── protocols.json    # Synthetic protocol definitions (lendingA, lendingB, dexA, bridgeC)
    ├── events.json       # Market events (oracle anomaly, ETH drawdown, exploit rumors)
    └── missions.json     # Mission profiles with constraints and preferences
```

## Task Distribution

| Type | Count | Difficulty |
|------|-------|------------|
| portfolio | 12 | L1 |
| cross_protocol | 16 | L2 |
| risk_hedging | 16 | L2 |
| governance | 16 | L3 |
| **Total** | **60** | L1(12) / L2(32) / L3(16) |

## Task Format (blind.jsonl)

Each task is an option-based scenario:

```json
{
  "task_id": "V4-L1-01",
  "type": "portfolio",
  "difficulty": "L1",
  "mission_id": "mission_balanced_growth",
  "state": {
    "scenario": "Choose a deployment for idle stablecoin capital...",
    "portfolio": {"USDC": 51000, "ETH": 4},
    "available_capital_usd": 12500,
    "market_notes": []
  },
  "active_events": [],
  "available_actions": ["option_A", "option_B", "option_C", "option_D"],
  "action_descriptions": {
    "option_A": "Deposit USDC into lendingA for audited blue-chip lending yield.",
    "option_B": "Deposit USDC into lendingB, a higher-yield lending market with high LTV.",
    "option_C": "Bridge USDC through bridgeC before redeploying for cross-chain incentives.",
    "option_D": "Hold current USDC position and wait for the next oracle and utilization update."
  }
}
```

## Gold Format (gold.jsonl)

Gold file contains utility scores via sandbox simulation, with `candidate_scores` per action/sequence, `recommended_actions`, `forbidden_actions`, and `optimal_utility`.

## Knowledge Base

Synthetic DeFi sandbox with:
- **4 protocols**: lendingA (conservative), lendingB (high-LTV), dexA (major DEX), bridgeC (risky)
- **5 assets**: ETH, WBTC, USDC, DAI, STBLX
- **3 missions**: conservative_yield, balanced_growth, dao_treasury_steward
- **4 events**: oracle anomaly, exploit rumor, ETH drawdown, DAO proposal

## Source

Generated from the [KDWAS research codebase](https://github.com/qCanoe/KDWAS) — refer to `src/sandbox/simulator.py` for utility computation.
