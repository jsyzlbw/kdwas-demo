# DeFi Bench v1 Utility Formulas

This document defines deterministic local utility formulas for optimization tasks.
Utilities are not manually assigned. They are computed by
`scripts/compute_candidate_utilities.py` from candidate metrics.

All formulas are normalized to make candidates comparable within a task. Utility
values should only be compared among candidates of the same task.

## General Rules

- Invalid candidates have `valid = false` and `utility = null`.
- `best_valid_utility` is the maximum utility among valid candidates.
- `best_candidate_id` is the candidate id with `best_valid_utility`.
- The utility provenance must record:
  - `source = deterministic_local_simulator`
  - `formula`
  - `version`
  - `block_number`

## Formula IDs

### `uniswap_fee_tier_v1`

Used when choosing among Uniswap V3 fee tiers.

```text
utility = normalized_received_value - gas_cost_usd / 100 - slippage_loss_usd / 100
```

Hard invalidation:

- slippage > 0.005
- price_impact > 0.01

### `uniswap_lp_range_v1`

Used when choosing LP range width for a conservative user.

```text
utility = fee_potential_score - out_of_range_risk_score
```

For conservative users, wider ranges receive lower risk penalty.

### `uniswap_largest_safe_swap_v1`

Used when choosing the largest safe swap size.

```text
utility = size_score + received_value_score - slippage_penalty - price_impact_penalty
```

Hard invalidation:

- slippage > 0.005
- price_impact > 0.01

### `aave_max_borrow_v1`

Used when borrowing the maximum safe USDC.

```text
utility = borrowed_value_score + health_factor_margin_score - gas_cost_usd / 100
```

Hard invalidation:

- post_action_health_factor < 1.5

### `aave_max_withdraw_v1`

Used when withdrawing maximum collateral safely.

```text
utility = withdrawn_value_score + health_factor_margin_score - gas_cost_usd / 100
```

Hard invalidation:

- post_action_health_factor < 1.8

### `maker_max_draw_v1`

Used when drawing maximum stablecoin safely.

```text
utility = minted_value_score + collateral_ratio_margin_score - gas_cost_usd / 100
```

Hard invalidation:

- post_action_collateral_ratio < 1.8

### `maker_max_withdraw_v1`

Used when withdrawing maximum collateral safely.

```text
utility = withdrawn_value_score + collateral_ratio_margin_score - gas_cost_usd / 100
```

Hard invalidation:

- post_action_collateral_ratio < 2.0

### `lido_liquidity_buffer_v1`

Used when choosing a staking amount while preserving liquidity.

```text
utility = staking_yield_score - liquidity_buffer_penalty - gas_cost_usd / 100
```

Hard invalidation:

- remaining_eth < 0.5

### `pendle_best_apy_v1`

Used when choosing a PT market.

```text
utility = fixed_yield_score - liquidity_penalty - maturity_penalty
```

Hard invalidation:

- market_liquidity < 500000
- maturity exceeds policy horizon

### `pendle_max_pt_v1`

Used when buying maximum PT under price impact constraints.

```text
utility = pt_amount_score + fixed_yield_score - slippage_loss - liquidity_penalty
```

Hard invalidation:

- price_impact > 0.01

### `pendle_sell_or_hold_v1`

Used when deciding whether to sell PT early.

```text
utility = received_value_score - early_exit_penalty - slippage_loss
```

Hard invalidation:

- slippage > 0.01

### `gmx_safe_long_size_v1`

Used when choosing safe long position size.

```text
utility = exposure_score - liquidation_risk_cost - fee_cost
```

Hard invalidation:

- leverage > 3
- liquidation_price > 1600

### `gmx_hedge_size_v1`

Used when choosing short hedge size.

```text
utility = hedge_effectiveness_score - fee_cost - liquidation_risk_cost
```

Hard invalidation:

- hedge_ratio < 0.4
- hedge_ratio > 0.7
