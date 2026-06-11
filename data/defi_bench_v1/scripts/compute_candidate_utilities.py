#!/usr/bin/env python3
"""Compute deterministic local utilities for DeFi Bench v1 optimization tasks.

The generator intentionally does not assign utility values. This script reads
candidate spaces from gold annotations, evaluates each candidate with a
deterministic local simulator, and writes candidate_evaluations back to gold.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROTOCOLS = ["uniswap_v3", "aave_v3", "maker_sky", "lido", "pendle", "gmx"]
PROVENANCE_SOURCE = "deterministic_local_simulator"
PROVENANCE_VERSION = "utility-sim-v1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def only_candidate(candidate_space: dict) -> tuple[str, list]:
    if len(candidate_space) != 1:
        raise ValueError(f"expected one candidate dimension, got {candidate_space}")
    key = next(iter(candidate_space))
    return key, candidate_space[key]


def round4(value: float) -> float:
    return round(value, 4)


def candidate_id(key: str, value: object) -> str:
    return f"{key}:{value}"


def evaluate_uniswap_fee_tier(value: int) -> dict:
    metrics_by_fee = {
        500: {"amount_out_weth": 0.3021, "slippage": 0.0030, "price_impact": 0.0040, "gas_cost_usd": 3.20},
        3000: {"amount_out_weth": 0.3004, "slippage": 0.0045, "price_impact": 0.0060, "gas_cost_usd": 3.05},
        10000: {"amount_out_weth": 0.2940, "slippage": 0.0110, "price_impact": 0.0140, "gas_cost_usd": 2.90},
    }
    metrics = metrics_by_fee[value]
    valid = metrics["slippage"] <= 0.005 and metrics["price_impact"] <= 0.01
    utility = metrics["amount_out_weth"] * 3000 - metrics["gas_cost_usd"] / 100 - metrics["slippage"] * 10 if valid else None
    return result(metrics, valid, utility)


def evaluate_uniswap_lp_range(value: str) -> dict:
    table = {
        "narrow": {"fee_potential_score": 0.95, "out_of_range_risk_score": 0.38},
        "balanced": {"fee_potential_score": 0.82, "out_of_range_risk_score": 0.20},
        "wide": {"fee_potential_score": 0.72, "out_of_range_risk_score": 0.06},
    }
    metrics = table[value]
    utility = metrics["fee_potential_score"] - metrics["out_of_range_risk_score"]
    return result(metrics, True, utility)


def evaluate_uniswap_largest_swap(value: int) -> dict:
    metrics = {
        "amount_in": value,
        "amount_out_weth": value * 0.000301,
        "slippage": 0.0015 + value / 1_000_000,
        "price_impact": 0.0020 + value / 500_000,
        "gas_cost_usd": 3.4,
    }
    valid = metrics["slippage"] <= 0.005 and metrics["price_impact"] <= 0.01
    utility = value / 2500 + metrics["amount_out_weth"] - metrics["slippage"] * 40 - metrics["price_impact"] * 30 if valid else None
    return result(metrics, valid, utility)


def evaluate_aave_borrow(value: int) -> dict:
    health_factor = 2.70 - value / 1900
    metrics = {"borrowed_usdc": value, "post_action_health_factor": round4(health_factor), "gas_cost_usd": 4.5}
    valid = health_factor >= 1.5
    utility = value / 2500 + (health_factor - 1.5) * 0.15 - metrics["gas_cost_usd"] / 100 if valid else None
    return result(metrics, valid, utility)


def evaluate_aave_withdraw(value: float) -> dict:
    health_factor = 2.2 - value * 0.85
    metrics = {"withdrawn_weth": value, "post_action_health_factor": round4(health_factor), "gas_cost_usd": 4.1}
    valid = health_factor >= 1.8
    utility = value / 0.5 + (health_factor - 1.8) * 0.12 - metrics["gas_cost_usd"] / 100 if valid else None
    return result(metrics, valid, utility)


def evaluate_maker_draw(value: int) -> dict:
    collateral_ratio = 2.75 - value / 2000
    metrics = {"drawn_dai": value, "post_action_collateral_ratio": round4(collateral_ratio), "gas_cost_usd": 5.2}
    valid = collateral_ratio >= 1.8
    utility = value / 2200 + (collateral_ratio - 1.8) * 0.10 - metrics["gas_cost_usd"] / 100 if valid else None
    return result(metrics, valid, utility)


def evaluate_maker_withdraw(value: float) -> dict:
    collateral_ratio = 2.5 - value * 0.58
    metrics = {"withdrawn_eth": value, "post_action_collateral_ratio": round4(collateral_ratio), "gas_cost_usd": 5.0}
    valid = collateral_ratio >= 2.0
    utility = value / 1.0 + (collateral_ratio - 2.0) * 0.10 - metrics["gas_cost_usd"] / 100 if valid else None
    return result(metrics, valid, utility)


def evaluate_lido_stake(value: float) -> dict:
    starting_eth = 2.0
    remaining_eth = starting_eth - value
    metrics = {"stake_amount_eth": value, "remaining_eth": round4(remaining_eth), "expected_annual_yield_eth": round4(value * 0.031), "gas_cost_usd": 2.2}
    valid = remaining_eth >= 0.5
    liquidity_penalty = max(0.0, 0.8 - remaining_eth) * 0.4
    utility = metrics["expected_annual_yield_eth"] * 10 - liquidity_penalty - metrics["gas_cost_usd"] / 100 if valid else None
    return result(metrics, valid, utility)


def evaluate_pendle_market(value: str) -> dict:
    table = {
        "sUSDe Jun 2026": {"implied_apy": 0.091, "market_liquidity": 920000, "maturity_months": 1},
        "sUSDe Sep 2026": {"implied_apy": 0.108, "market_liquidity": 760000, "maturity_months": 4},
        "sUSDe Dec 2026": {"implied_apy": 0.126, "market_liquidity": 420000, "maturity_months": 7},
    }
    metrics = table[value]
    valid = metrics["market_liquidity"] >= 500000 and metrics["maturity_months"] <= 6
    liquidity_penalty = 500000 / metrics["market_liquidity"] * 0.02
    maturity_penalty = metrics["maturity_months"] * 0.005
    utility = metrics["implied_apy"] - liquidity_penalty - maturity_penalty if valid else None
    return result(metrics, valid, utility)


def evaluate_pendle_amount(value: int) -> dict:
    metrics = {
        "amount_in_usdc": value,
        "pt_received": round4(value * 1.045),
        "price_impact": round4(0.002 + value / 550000),
        "slippage": round4(0.001 + value / 1_000_000),
    }
    valid = metrics["price_impact"] <= 0.01
    utility = value / 2500 + metrics["pt_received"] / 10000 - metrics["slippage"] * 30 if valid else None
    return result(metrics, valid, utility)


def evaluate_pendle_sell_action(value: str) -> dict:
    table = {
        "hold": {"received_usdc": 0, "slippage": 0.0, "early_exit_penalty": 0.02},
        "sell_500": {"received_usdc": 515, "slippage": 0.004, "early_exit_penalty": 0.05},
        "sell_1000": {"received_usdc": 1028, "slippage": 0.008, "early_exit_penalty": 0.08},
    }
    metrics = table[value]
    valid = metrics["slippage"] <= 0.01
    utility = metrics["received_usdc"] / 1000 - metrics["early_exit_penalty"] - metrics["slippage"] * 10 if valid else None
    return result(metrics, valid, utility)


def evaluate_gmx_long_size(value: int) -> dict:
    leverage = value / 1000
    liquidation_price = 1300 + value * 0.1
    metrics = {"size_usd": value, "leverage": round4(leverage), "liquidation_price": round4(liquidation_price), "fee_cost_usd": round4(value * 0.0007)}
    valid = leverage <= 3 and liquidation_price <= 1600
    utility = value / 3000 - (liquidation_price - 1200) / 2000 - metrics["fee_cost_usd"] / 100 if valid else None
    return result(metrics, valid, utility)


def evaluate_gmx_hedge_ratio(value: float) -> dict:
    metrics = {"hedge_ratio": value, "fee_cost_usd": round4(value * 12), "liquidation_risk_score": round4(0.12 + value * 0.08)}
    valid = 0.4 <= value <= 0.7
    hedge_effectiveness = 1 - abs(value - 0.5)
    utility = hedge_effectiveness - metrics["fee_cost_usd"] / 100 - metrics["liquidation_risk_score"] if valid else None
    return result(metrics, valid, utility)


def result(metrics: dict, valid: bool, utility: float | None) -> dict:
    return {
        "metrics": metrics,
        "valid": valid,
        "utility": None if utility is None else round4(utility),
        "invalid_reason": None if valid else "violates_hard_constraints",
    }


EVALUATORS = {
    "uniswap_fee_tier_v1": evaluate_uniswap_fee_tier,
    "uniswap_lp_range_v1": evaluate_uniswap_lp_range,
    "uniswap_largest_safe_swap_v1": evaluate_uniswap_largest_swap,
    "aave_max_borrow_v1": evaluate_aave_borrow,
    "aave_max_withdraw_v1": evaluate_aave_withdraw,
    "maker_max_draw_v1": evaluate_maker_draw,
    "maker_max_withdraw_v1": evaluate_maker_withdraw,
    "lido_liquidity_buffer_v1": evaluate_lido_stake,
    "pendle_best_apy_v1": evaluate_pendle_market,
    "pendle_max_pt_v1": evaluate_pendle_amount,
    "pendle_sell_or_hold_v1": evaluate_pendle_sell_action,
    "gmx_safe_long_size_v1": evaluate_gmx_long_size,
    "gmx_hedge_size_v1": evaluate_gmx_hedge_ratio,
}


def compute_config(config: dict, block_number: int) -> dict:
    formula = config["utility_formula"]
    evaluator = EVALUATORS[formula]
    key, values = only_candidate(config["candidate_space"])
    evaluations = []
    for value in values:
        item = evaluator(value)
        evaluations.append({
            "candidate_id": candidate_id(key, value),
            "candidate": {key: value},
            **item,
        })

    valid = [item for item in evaluations if item["valid"]]
    if not valid:
        raise ValueError(f"no valid candidates for {formula}")
    best = max(valid, key=lambda item: item["utility"])
    return {
        **config,
        "candidate_evaluations": evaluations,
        "best_candidate_id": best["candidate_id"],
        "best_valid_utility": best["utility"],
        "utility_provenance": {
            "source": PROVENANCE_SOURCE,
            "formula": formula,
            "version": PROVENANCE_VERSION,
            "block_number": block_number,
        },
    }


def main() -> None:
    for protocol in PROTOCOLS:
        env_dir = ROOT / "envs" / protocol
        state = load_json(env_dir / "state.json")
        gold_rows = load_jsonl(env_dir / "gold.jsonl")
        updated = []
        for row in gold_rows:
            config = row["economic_regret_config"]
            if row["economic_regret_applicable"]:
                row = {
                    **row,
                    "economic_regret_config": compute_config(config, state["block_number"]),
                }
            updated.append(row)
        write_jsonl(env_dir / "gold.jsonl", updated)

    print("OK: computed deterministic candidate utilities")


if __name__ == "__main__":
    main()
