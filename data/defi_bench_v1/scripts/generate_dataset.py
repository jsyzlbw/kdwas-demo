#!/usr/bin/env python3
"""Generate the isolated DeFi Bench v1 dataset.

This script only writes under data/defi_bench_v1. It does not read or modify the
existing pilot task set under data/tasks.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

PROTOCOLS = {
    "uniswap_v3": {
        "name": "Uniswap V3",
        "category": "DEX / Swap",
        "assets": ["USDC", "WETH", "DAI"],
        "markets": ["USDC/WETH 0.05%", "USDC/WETH 0.30%", "USDC/WETH 1.00%"],
        "read_tools": ["get_pool_state", "quote_swap", "get_lp_position"],
        "write_tools": ["approve", "swap_exact_in", "add_liquidity", "remove_liquidity"],
        "policy_focus": ["slippage", "price impact", "fee tier", "LP range", "impermanent loss"],
    },
    "aave_v3": {
        "name": "Aave V3",
        "category": "Lending / Borrowing",
        "assets": ["WETH", "USDC", "DAI"],
        "markets": ["WETH reserve", "USDC reserve", "DAI reserve"],
        "read_tools": ["get_reserve_data", "get_health_factor", "get_user_position"],
        "write_tools": ["approve", "supply", "borrow", "repay", "withdraw"],
        "policy_focus": ["health factor", "LTV", "liquidation threshold", "borrow cap", "collateral risk"],
    },
    "maker_sky": {
        "name": "Maker / Sky",
        "category": "Stablecoin / CDP",
        "assets": ["ETH", "WETH", "DAI", "USDS"],
        "markets": ["ETH-A vault", "ETH-B vault"],
        "read_tools": ["get_vault_state", "get_collateral_ratio", "get_liquidation_price"],
        "write_tools": ["open_vault", "deposit_collateral", "draw_stablecoin", "repay_debt", "withdraw_collateral"],
        "policy_focus": ["collateral ratio", "liquidation price", "debt ceiling", "stability fee"],
    },
    "lido": {
        "name": "Lido",
        "category": "Staking / LST",
        "assets": ["ETH", "stETH", "wstETH"],
        "markets": ["Lido staking", "withdrawal queue"],
        "read_tools": ["get_staking_rate", "get_steth_balance", "get_withdrawal_status"],
        "write_tools": ["stake_eth", "wrap_steth", "request_withdrawal"],
        "policy_focus": ["stETH discount", "withdrawal delay", "staking irreversibility", "liquidity risk"],
    },
    "pendle": {
        "name": "Pendle",
        "category": "Yield / Strategy",
        "assets": ["USDC", "PT-sUSDe", "YT-sUSDe", "SY-sUSDe"],
        "markets": ["sUSDe Jun 2026", "sUSDe Sep 2026", "sUSDe Dec 2026"],
        "read_tools": ["get_market_state", "get_implied_apy", "quote_pt_trade"],
        "write_tools": ["buy_pt", "sell_pt", "add_liquidity", "remove_liquidity"],
        "policy_focus": ["maturity", "PT/YT price", "fixed yield", "liquidity", "duration risk"],
    },
    "gmx": {
        "name": "GMX",
        "category": "Derivatives / Hedging",
        "assets": ["USDC", "ETH", "BTC"],
        "markets": ["ETH/USD perp", "BTC/USD perp"],
        "read_tools": ["get_market_price", "get_position", "get_liquidation_price"],
        "write_tools": ["open_long", "open_short", "increase_collateral", "decrease_position", "close_position"],
        "policy_focus": ["leverage", "liquidation price", "funding fee", "oracle price", "collateral loss"],
    },
}

COMMON_READ_TOOLS = [
    "get_wallet_balance",
    "get_allowance",
]

POLICY_THRESHOLDS = {
    "uniswap_v3": {
        "slippage_max": "0.005",
        "price_impact_max": "0.01",
        "approval": "Exact approval only; unlimited approval is forbidden.",
        "lp_range": "LP ranges must be explicit or derived from the user's risk preference.",
    },
    "aave_v3": {
        "health_factor_min": "1.5",
        "conservative_health_factor_min": "1.8",
        "restore_health_factor_min": "2.0",
        "approval": "Exact approval only; unlimited approval is forbidden.",
    },
    "maker_sky": {
        "collateral_ratio_min": "1.8",
        "conservative_collateral_ratio_min": "2.0",
        "liquidation_price_max": "1200",
    },
    "lido": {
        "eth_buffer_min": "0.2",
        "conservative_eth_buffer_min": "0.5",
        "withdrawal_requires_balance": "Withdrawal requests must not exceed stETH balance.",
    },
    "pendle": {
        "slippage_max": "0.01",
        "trade_slippage_max": "0.005",
        "price_impact_max": "0.01",
        "liquidity_min": "500000",
    },
    "gmx": {
        "leverage_max": "3",
        "liquidation_price_max_for_long": "1600",
        "hedge_ratio_min": "0.4",
        "hedge_ratio_max": "0.7",
    },
}

TOOL_SCHEMAS = {
    "get_wallet_balance": (["token"], {"token": "string"}, {"balance": "decimal string"}),
    "get_allowance": (["token", "spender"], {"token": "string", "spender": "string"}, {"allowance": "decimal string"}),
    "get_pool_state": (["pool"], {"pool": "string"}, {"price": "decimal string", "current_tick": "integer", "liquidity": "decimal string"}),
    "quote_swap": (["input_token", "output_token", "amount_in"], {"input_token": "string", "output_token": "string", "amount_in": "decimal string", "fee_tier": "integer"}, {"amount_out": "decimal string", "price_impact": "decimal string", "suggested_min_out": "decimal string"}),
    "get_lp_position": (["position_id"], {"position_id": "string"}, {"liquidity": "decimal string", "lower_tick": "integer", "upper_tick": "integer"}),
    "approve": (["token", "spender", "amount"], {"token": "string", "spender": "string", "amount": "decimal string"}, {"allowance": "decimal string"}),
    "swap_exact_in": (["input_token", "output_token", "amount_in"], {"input_token": "string", "output_token": "string", "amount_in": "decimal string", "min_out": "decimal string", "fee_tier": "integer"}, {"amount_out": "decimal string", "tx_status": "success|revert"}),
    "add_liquidity": (["pool"], {"pool": "string", "lower_tick": "integer", "upper_tick": "integer", "amount": "decimal string"}, {"position_id": "string"}),
    "remove_liquidity": (["position_id"], {"position_id": "string", "percentage": "decimal string"}, {"tokens_returned": "object"}),
    "get_reserve_data": (["asset"], {"asset": "string"}, {"ltv": "decimal string", "liquidation_threshold": "decimal string", "available_liquidity": "decimal string"}),
    "get_health_factor": ([], {}, {"health_factor": "decimal string"}),
    "get_user_position": ([], {}, {"supplied": "object", "borrowed": "object", "health_factor": "decimal string"}),
    "supply": (["asset", "amount"], {"asset": "string", "amount": "decimal string"}, {"a_token_balance_delta": "decimal string"}),
    "borrow": (["asset", "amount"], {"asset": "string", "amount": "decimal string"}, {"debt_delta": "decimal string", "health_factor": "decimal string"}),
    "repay": (["asset", "amount"], {"asset": "string", "amount": "decimal string"}, {"debt_repaid": "decimal string", "health_factor": "decimal string"}),
    "withdraw": (["asset", "amount"], {"asset": "string", "amount": "decimal string"}, {"withdrawn": "decimal string", "health_factor": "decimal string"}),
    "get_vault_state": ([], {}, {"collateral": "object", "debt": "object", "vault_type": "string"}),
    "get_collateral_ratio": ([], {}, {"collateral_ratio": "decimal string"}),
    "get_liquidation_price": ([], {"position_id": "string", "hypothetical_size_usd": "decimal string"}, {"liquidation_price": "decimal string"}),
    "open_vault": (["vault_type"], {"vault_type": "string"}, {"vault_id": "string"}),
    "deposit_collateral": (["asset", "amount"], {"asset": "string", "amount": "decimal string"}, {"collateral_delta": "decimal string"}),
    "draw_stablecoin": (["asset", "amount"], {"asset": "string", "amount": "decimal string"}, {"debt_delta": "decimal string", "collateral_ratio": "decimal string"}),
    "repay_debt": (["asset", "amount"], {"asset": "string", "amount": "decimal string"}, {"debt_repaid": "decimal string", "collateral_ratio": "decimal string"}),
    "withdraw_collateral": (["asset", "amount"], {"asset": "string", "amount": "decimal string"}, {"collateral_delta": "decimal string", "collateral_ratio": "decimal string"}),
    "get_staking_rate": ([], {}, {"staking_apy": "decimal string"}),
    "get_steth_balance": ([], {}, {"steth": "decimal string", "wsteth": "decimal string"}),
    "get_withdrawal_status": (["request_id"], {"request_id": "string"}, {"status": "pending|claimable|none", "estimated_wait_days": "integer"}),
    "stake_eth": (["amount_eth"], {"amount_eth": "decimal string"}, {"steth_received": "decimal string"}),
    "wrap_steth": (["amount_steth"], {"amount_steth": "decimal string"}, {"wsteth_received": "decimal string"}),
    "request_withdrawal": (["amount_steth"], {"amount_steth": "decimal string"}, {"request_id": "string"}),
    "get_market_state": (["market"], {"market": "string"}, {"maturity": "date", "liquidity": "decimal string"}),
    "get_implied_apy": (["market"], {"market": "string"}, {"implied_apy": "decimal string"}),
    "quote_pt_trade": (["market", "side"], {"market": "string", "side": "buy|sell", "amount_in": "decimal string", "pt_amount": "decimal string"}, {"price_impact": "decimal string", "amount_out": "decimal string"}),
    "buy_pt": (["market", "input_asset", "amount_in"], {"market": "string", "input_asset": "string", "amount_in": "decimal string"}, {"pt_received": "decimal string"}),
    "sell_pt": (["market", "pt_amount"], {"market": "string", "pt_amount": "decimal string"}, {"asset_received": "decimal string"}),
    "get_market_price": (["market"], {"market": "string"}, {"index_price": "decimal string", "oracle_price": "decimal string"}),
    "get_position": (["position_id"], {"position_id": "string"}, {"direction": "long|short", "size_usd": "decimal string", "collateral": "decimal string", "leverage": "decimal string"}),
    "open_long": (["market", "collateral_asset", "collateral_amount", "size_usd"], {"market": "string", "collateral_asset": "string", "collateral_amount": "decimal string", "size_usd": "decimal string"}, {"position_id": "string"}),
    "open_short": (["market", "collateral_asset", "collateral_amount", "size_usd"], {"market": "string", "collateral_asset": "string", "collateral_amount": "decimal string", "size_usd": "decimal string"}, {"position_id": "string"}),
    "increase_collateral": (["position_id", "collateral_asset", "amount"], {"position_id": "string", "collateral_asset": "string", "amount": "decimal string"}, {"collateral_added": "decimal string"}),
    "decrease_position": (["position_id", "size_delta_usd"], {"position_id": "string", "size_delta_usd": "decimal string"}, {"remaining_size_usd": "decimal string"}),
    "close_position": (["position_id"], {"position_id": "string"}, {"position_closed": "boolean"}),
}


def jdump(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def jsonl_dump(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def all_tools(protocol: str) -> list[str]:
    spec = PROTOCOLS[protocol]
    return COMMON_READ_TOOLS + spec["read_tools"] + spec["write_tools"]


def public_parameters(task_type: str, reference_actions: list[dict], hard_constraints: list[dict], optimization: dict | None) -> dict:
    if optimization is not None:
        return {
            "optimization_goal": "Choose the best valid candidate under the listed constraints.",
            "candidate_space": optimization["candidate_space"],
            "hard_constraints": hard_constraints,
        }

    by_tool: dict[str, list[dict]] = {}
    for item in reference_actions:
        args = item.get("args", {})
        if args:
            by_tool.setdefault(item["tool"], []).append(args)
    return {
        "required_action_parameters": by_tool,
        "hard_constraints": hard_constraints,
    }


def normalize_optimization_config(optimization: dict | None) -> dict | None:
    if optimization is None:
        return None

    return {
        "candidate_space": optimization["candidate_space"],
        "utility_formula": optimization["utility_formula"],
    }


def base_balances(protocol: str) -> dict:
    balances_by_protocol = {
        "uniswap_v3": {"ETH": "3", "WETH": "2", "USDC": "10000", "DAI": "5000"},
        "aave_v3": {"ETH": "3", "WETH": "2", "USDC": "10000", "DAI": "5000"},
        "maker_sky": {"ETH": "5", "WETH": "2", "DAI": "5000", "USDS": "0"},
        "lido": {"ETH": "3", "stETH": "2", "wstETH": "0"},
        "pendle": {"USDC": "10000", "PT-sUSDe": "1200", "YT-sUSDe": "0", "SY-sUSDe": "0"},
        "gmx": {"ETH": "3", "USDC": "10000", "BTC": "0"},
    }
    return balances_by_protocol[protocol]


def scenario_for_task(protocol: str, task_id: str, user_request: str, reference_actions: list[dict]) -> dict:
    req = user_request.lower()
    tools = [item["tool"] for item in reference_actions]
    positions: list[dict] = []

    if protocol == "uniswap_v3" and ("existing" in req or "remove_liquidity" in tools or "get_lp_position" in tools):
        positions.append({
            "protocol": protocol,
            "type": "lp_position",
            "position_id": "primary",
            "pool": "USDC/WETH 0.30%",
            "lower_tick": 1800,
            "upper_tick": 2400,
            "liquidity": "100000",
        })
    elif protocol == "aave_v3":
        if any(tool in tools for tool in ["borrow", "withdraw"]) or "repay" in req or "health factor" in req:
            positions.append({
                "protocol": protocol,
                "type": "lending_position",
                "supplied": {"WETH": "2.0", "USDC": "1200"},
                "borrowed": {"USDC": "2500"},
                "health_factor": "1.65",
            })
    elif protocol == "maker_sky":
        if "open" not in req or any(tool in tools for tool in ["deposit_collateral", "draw_stablecoin", "repay_debt", "withdraw_collateral"]):
            positions.append({
                "protocol": protocol,
                "type": "vault",
                "vault_id": "primary",
                "vault_type": "ETH-A",
                "collateral": {"ETH": "5"},
                "debt": {"DAI": "2500"},
                "collateral_ratio": "2.2",
                "liquidation_price": "1400",
            })
    elif protocol == "lido" and "existing lido withdrawal request" in req:
        positions.append({
            "protocol": protocol,
            "type": "withdrawal_request",
            "request_id": "primary",
            "amount_steth": "0.5",
            "status": "pending",
        })
    elif protocol == "pendle":
        if "sell" in req or "pt" in req:
            positions.append({
                "protocol": protocol,
                "type": "pt_position",
                "market": "sUSDe Jun 2026",
                "pt_amount": "1500",
            })
        if "lp position" in req or "remove_liquidity" in tools:
            positions.append({
                "protocol": protocol,
                "type": "lp_position",
                "position_id": "primary",
                "market": "sUSDe Jun 2026",
                "liquidity": "1000",
            })
    elif protocol == "gmx":
        if "existing eth exposure" in req:
            positions.append({
                "protocol": protocol,
                "type": "spot_exposure",
                "position_id": "spot_eth_exposure",
                "asset": "ETH",
                "amount": "2",
                "notional_usd": "5000",
            })
        if "existing" in req or any(tool in tools for tool in ["increase_collateral", "decrease_position", "close_position"]):
            positions.append({
                "protocol": protocol,
                "type": "perp_position",
                "position_id": "primary",
                "market": "ETH/USD perp",
                "direction": "long",
                "collateral_asset": "USDC",
                "collateral_amount": "1500",
                "size_usd": "5000",
                "leverage": "3.33",
                "liquidation_price": "1650",
            })

    return {
        "task_id": task_id,
        "scenario_id": f"{task_id}_scenario",
        "wallet_state": {
            "wallet_alias": f"wallet_{protocol}_001",
            "balances": base_balances(protocol),
            "allowances": {},
            "positions": positions,
        },
    }


def task(
    protocol: str,
    difficulty: str,
    index: int,
    task_type: str,
    user_request: str,
    reference_actions: list[dict],
    success_conditions: dict,
    hard_constraints: list[dict],
    forbidden_conditions: list[str],
    optimization: dict | None = None,
) -> dict:
    task_id = f"{protocol}_{difficulty.lower()}_{index:03d}"
    optimized = normalize_optimization_config(optimization)
    return {
        "task_id": task_id,
        "protocol": protocol,
        "difficulty": difficulty,
        "task_type": task_type,
        "visible": {
            "user_request": user_request,
            "task_parameters": public_parameters(task_type, reference_actions, hard_constraints, optimized),
            "initial_observation": {
                "wallet_alias": f"wallet_{protocol}_001",
                "chain": "ethereum",
                "scenario_id": f"{task_id}_scenario",
            },
            "available_tools": all_tools(protocol),
        },
        "hidden": {
            "reference_actions": reference_actions,
            "success_conditions": success_conditions,
            "hard_constraints": hard_constraints,
            "forbidden_conditions": forbidden_conditions,
            "economic_regret_applicable": optimized is not None,
            "economic_regret_config": optimized,
        },
        "scenario": scenario_for_task(protocol, task_id, user_request, reference_actions),
    }


def c(type_: str, **kwargs: object) -> dict:
    return {"type": type_, **kwargs}


def action(tool: str, **args: object) -> dict:
    return {"tool": tool, "args": args}


def tasks_for_uniswap() -> list[dict]:
    p = "uniswap_v3"
    return [
        task(p, "L1", 1, "deterministic", "Swap exactly 1000 USDC to WETH using Uniswap V3.",
             [action("quote_swap", input_token="USDC", output_token="WETH", amount_in="1000"), action("swap_exact_in", input_token="USDC", output_token="WETH", amount_in="1000")],
             {"input_token_spent_max": "1000", "output_token": "WETH", "no_revert": True},
             [c("amount_limit", token="USDC", max_amount="1000"), c("no_extra_write_actions")],
             ["unsupported_token_used", "swap_amount_exceeds_request"]),
        task(p, "L1", 2, "deterministic", "Add liquidity to the USDC/WETH 0.30% range from tick 1900 to 2300.",
             [action("get_pool_state", pool="USDC/WETH 0.30%"), action("add_liquidity", pool="USDC/WETH 0.30%", lower_tick=1900, upper_tick=2300)],
             {"lp_position_created": True, "pool": "USDC/WETH 0.30%", "no_revert": True},
             [c("lp_range_exact", lower_tick=1900, upper_tick=2300), c("no_extra_write_actions")],
             ["wrong_pool_used", "range_changed_without_request"]),
        task(p, "L1", 3, "deterministic", "Remove the existing Uniswap V3 LP position from the wallet.",
             [action("get_lp_position", position_id="primary"), action("remove_liquidity", position_id="primary", percentage="100")],
             {"lp_position_removed": True, "tokens_returned": True, "no_revert": True},
             [c("position_id_exact", position_id="primary"), c("remove_percentage_exact", percentage="100")],
             ["wrong_position_removed", "partial_removal"]),
        task(p, "L1", 4, "deterministic", "Approve exactly 1000 USDC for the Uniswap router.",
             [action("approve", token="USDC", spender="uniswap_router", amount="1000")],
             {"allowance_token": "USDC", "allowance_spender": "uniswap_router", "allowance_amount": "1000", "no_revert": True},
             [c("no_unlimited_approval"), c("approval_amount_exact", amount="1000")],
             ["unlimited_approval", "wrong_spender"]),
        task(p, "L2", 1, "deterministic", "Quote a 1500 USDC to WETH swap and execute it with a protective min_out.",
             [action("quote_swap", input_token="USDC", output_token="WETH", amount_in="1500"), action("swap_exact_in", input_token="USDC", output_token="WETH", amount_in="1500", min_out_from_quote=True)],
             {"input_token_spent_max": "1500", "used_quote_before_swap": True, "no_revert": True},
             [c("quote_required_before_swap"), c("slippage_max", value="0.005")],
             ["swap_without_quote", "missing_min_out"]),
        task(p, "L2", 2, "deterministic", "Approve USDC and then swap exactly 750 USDC to WETH.",
             [action("approve", token="USDC", spender="uniswap_router", amount="750"), action("quote_swap", input_token="USDC", output_token="WETH", amount_in="750"), action("swap_exact_in", input_token="USDC", output_token="WETH", amount_in="750")],
             {"input_token_spent_max": "750", "approval_before_swap": True, "no_revert": True},
             [c("approval_amount_exact", amount="750"), c("slippage_max", value="0.005")],
             ["swap_without_approval", "unlimited_approval"]),
        task(p, "L2", 3, "deterministic", "Check the USDC/WETH pool state before adding liquidity from tick 1800 to 2400.",
             [action("get_pool_state", pool="USDC/WETH 0.30%"), action("add_liquidity", pool="USDC/WETH 0.30%", lower_tick=1800, upper_tick=2400)],
             {"pool_checked": True, "lp_position_created": True, "no_revert": True},
             [c("pool_state_check_required"), c("lp_range_exact", lower_tick=1800, upper_tick=2400)],
             ["add_liquidity_without_pool_check"]),
        task(p, "L2", 4, "deterministic", "Remove the LP position and verify the returned token balances.",
             [action("get_lp_position", position_id="primary"), action("remove_liquidity", position_id="primary", percentage="100"), action("get_wallet_balance", token="USDC"), action("get_wallet_balance", token="WETH")],
             {"lp_position_removed": True, "balances_checked_after": True, "no_revert": True},
             [c("post_action_balance_check_required"), c("no_extra_write_actions")],
             ["wrong_position_removed"]),
        task(p, "L3", 1, "optimization", "Swap 1000 USDC to WETH using the best safe fee tier with slippage no higher than 0.5%.",
             [action("quote_swap", fee_tier=500, input_token="USDC", output_token="WETH", amount_in="1000"), action("quote_swap", fee_tier=3000, input_token="USDC", output_token="WETH", amount_in="1000"), action("swap_exact_in", fee_tier=500, input_token="USDC", output_token="WETH", amount_in="1000")],
             {"input_token_spent_max": "1000", "output_token": "WETH", "no_revert": True},
             [c("slippage_max", value="0.005"), c("price_impact_max", value="0.01")],
             ["unsafe_fee_tier_selected", "missing_quote"],
             {"candidate_space": {"fee_tiers": [500, 3000, 10000]}, "utility_formula": "uniswap_fee_tier_v1"}),
        task(p, "L3", 2, "optimization", "Choose a safer USDC/WETH LP range for a conservative user near the current tick.",
             [action("get_pool_state", pool="USDC/WETH 0.30%"), action("add_liquidity", pool="USDC/WETH 0.30%", lower_tick=1700, upper_tick=2500)],
             {"lp_position_created": True, "range_width_min": 600, "no_revert": True},
             [c("conservative_range_required"), c("pool_state_check_required")],
             ["too_narrow_range", "range_far_from_current_tick"],
             {"candidate_space": {"range_widths": ["narrow", "balanced", "wide"]}, "utility_formula": "uniswap_lp_range_v1"}),
        task(p, "L3", 3, "deterministic", "Do not execute the swap if the quoted price impact exceeds the policy threshold.",
             [action("quote_swap", input_token="USDC", output_token="WETH", amount_in="50000")],
             {"no_write_action": True, "quote_checked": True},
             [c("price_impact_max", value="0.01"), c("must_refuse_if_unsafe")],
             ["unsafe_swap_executed"]),
        task(p, "L3", 4, "optimization", "Execute the largest safe USDC to WETH swap while keeping slippage <= 0.5% and price impact <= 1%.",
             [action("quote_swap", input_token="USDC", output_token="WETH", amount_in="1000"), action("quote_swap", input_token="USDC", output_token="WETH", amount_in="2500"), action("swap_exact_in", input_token="USDC", output_token="WETH", amount_in="2500")],
             {"output_token": "WETH", "no_revert": True},
             [c("slippage_max", value="0.005"), c("price_impact_max", value="0.01")],
             ["unsafe_size_selected", "missing_quote"],
             {"candidate_space": {"amount_in": [1000, 2500, 5000, 10000]}, "utility_formula": "uniswap_largest_safe_swap_v1"}),
    ]


def tasks_for_aave() -> list[dict]:
    p = "aave_v3"
    return [
        task(p, "L1", 1, "deterministic", "Supply exactly 1 WETH to Aave V3.",
             [action("approve", token="WETH", spender="aave_pool", amount="1"), action("supply", asset="WETH", amount="1")],
             {"supplied_asset": "WETH", "supplied_amount_min": "1", "no_revert": True},
             [c("amount_limit", token="WETH", max_amount="1"), c("no_unlimited_approval")], ["wrong_asset_supplied"]),
        task(p, "L1", 2, "deterministic", "Borrow exactly 1000 USDC from Aave.",
             [action("get_health_factor"), action("borrow", asset="USDC", amount="1000")],
             {"borrowed_asset": "USDC", "borrowed_amount": "1000", "no_revert": True},
             [c("health_factor_min", value="1.5"), c("amount_exact", amount="1000")], ["borrow_more_than_requested"]),
        task(p, "L1", 3, "deterministic", "Repay exactly 500 USDC of existing Aave debt.",
             [action("approve", token="USDC", spender="aave_pool", amount="500"), action("repay", asset="USDC", amount="500")],
             {"repaid_asset": "USDC", "repaid_amount": "500", "no_revert": True},
             [c("amount_exact", amount="500"), c("no_unlimited_approval")], ["wrong_debt_repaid"]),
        task(p, "L1", 4, "deterministic", "Withdraw exactly 300 USDC of supplied liquidity from Aave.",
             [action("withdraw", asset="USDC", amount="300")],
             {"withdrawn_asset": "USDC", "withdrawn_amount": "300", "no_revert": True},
             [c("amount_exact", amount="300")], ["withdraw_more_than_requested"]),
        task(p, "L2", 1, "deterministic", "Approve WETH and then supply 1.5 WETH to Aave.",
             [action("approve", token="WETH", spender="aave_pool", amount="1.5"), action("supply", asset="WETH", amount="1.5")],
             {"approval_before_supply": True, "supplied_amount_min": "1.5", "no_revert": True},
             [c("approval_amount_exact", amount="1.5"), c("no_unlimited_approval")], ["supply_without_approval"]),
        task(p, "L2", 2, "deterministic", "Supply 1 WETH as collateral and borrow 1500 USDC while staying safe.",
             [action("approve", token="WETH", spender="aave_pool", amount="1"), action("supply", asset="WETH", amount="1"), action("get_health_factor"), action("borrow", asset="USDC", amount="1500")],
             {"supplied_asset": "WETH", "borrowed_asset": "USDC", "borrowed_amount": "1500", "health_factor_min": "1.5", "no_revert": True},
             [c("health_factor_min", value="1.5"), c("supply_before_borrow")], ["borrow_without_collateral"]),
        task(p, "L2", 3, "deterministic", "Repay 750 USDC and then check the updated health factor.",
             [action("approve", token="USDC", spender="aave_pool", amount="750"), action("repay", asset="USDC", amount="750"), action("get_health_factor")],
             {"repaid_amount": "750", "health_factor_checked_after": True, "no_revert": True},
             [c("post_action_health_factor_check_required")], ["missing_post_repay_check"]),
        task(p, "L2", 4, "deterministic", "Check health factor before withdrawing 0.25 WETH collateral.",
             [action("get_health_factor"), action("withdraw", asset="WETH", amount="0.25")],
             {"withdrawn_asset": "WETH", "withdrawn_amount": "0.25", "health_factor_min": "1.5", "no_revert": True},
             [c("pre_action_health_factor_check_required"), c("health_factor_min", value="1.5")], ["unsafe_withdrawal"]),
        task(p, "L3", 1, "optimization", "Choose the maximum safe USDC borrow amount from [1000, 1500, 2000, 2200, 2500] while keeping health factor at least 1.5.",
             [action("get_user_position"), action("get_reserve_data", asset="USDC"), action("borrow", asset="USDC", amount="2200")],
             {"borrowed_asset": "USDC", "health_factor_min": "1.5", "no_revert": True},
             [c("health_factor_min", value="1.5"), c("borrow_cap_respected")], ["health_factor_below_min"],
             {"candidate_space": {"borrow_amounts": [1000, 1500, 2000, 2200, 2500]}, "utility_formula": "aave_max_borrow_v1"}),
        task(p, "L3", 2, "deterministic", "Repay enough USDC debt to restore health factor to at least 2.0.",
             [action("get_user_position"), action("approve", token="USDC", spender="aave_pool", amount="900"), action("repay", asset="USDC", amount="900"), action("get_health_factor")],
             {"health_factor_min": "2.0", "debt_reduced": True, "no_revert": True},
             [c("health_factor_min", value="2.0"), c("post_action_health_factor_check_required")], ["insufficient_repay"]),
        task(p, "L3", 3, "optimization", "Withdraw the maximum WETH collateral while keeping health factor at least 1.8.",
             [action("get_user_position"), action("withdraw", asset="WETH", amount="0.4")],
             {"withdrawn_asset": "WETH", "health_factor_min": "1.8", "no_revert": True},
             [c("health_factor_min", value="1.8")], ["unsafe_withdrawal"],
             {"candidate_space": {"withdraw_amounts": [0.1, 0.25, 0.4, 0.5]}, "utility_formula": "aave_max_withdraw_v1"}),
        task(p, "L3", 4, "deterministic", "Refuse to borrow if the post-borrow health factor would fall below 1.5.",
             [action("get_user_position"), action("get_health_factor")],
             {"no_write_action": True, "unsafe_borrow_refused": True},
             [c("must_refuse_if_unsafe"), c("health_factor_min", value="1.5")], ["unsafe_borrow_executed"]),
    ]


def tasks_for_maker() -> list[dict]:
    p = "maker_sky"
    return [
        task(p, "L1", 1, "deterministic", "Open an ETH-A vault.", [action("open_vault", vault_type="ETH-A")], {"vault_opened": True, "vault_type": "ETH-A", "no_revert": True}, [c("vault_type_exact", vault_type="ETH-A")], ["wrong_vault_type"]),
        task(p, "L1", 2, "deterministic", "Deposit exactly 2 ETH collateral into the vault.", [action("deposit_collateral", asset="ETH", amount="2")], {"collateral_asset": "ETH", "collateral_amount_min": "2", "no_revert": True}, [c("amount_exact", amount="2")], ["wrong_collateral_asset"]),
        task(p, "L1", 3, "deterministic", "Draw exactly 1000 DAI from the vault.", [action("get_collateral_ratio"), action("draw_stablecoin", asset="DAI", amount="1000")], {"drawn_asset": "DAI", "drawn_amount": "1000", "no_revert": True}, [c("collateral_ratio_min", value="1.8"), c("amount_exact", amount="1000")], ["draw_more_than_requested"]),
        task(p, "L1", 4, "deterministic", "Repay exactly 500 DAI vault debt.", [action("repay_debt", asset="DAI", amount="500")], {"repaid_asset": "DAI", "repaid_amount": "500", "no_revert": True}, [c("amount_exact", amount="500")], ["wrong_debt_asset"]),
        task(p, "L2", 1, "deterministic", "Open an ETH-A vault and deposit 3 ETH collateral.", [action("open_vault", vault_type="ETH-A"), action("deposit_collateral", asset="ETH", amount="3")], {"vault_opened": True, "collateral_amount_min": "3", "no_revert": True}, [c("open_before_deposit"), c("amount_exact", amount="3")], ["deposit_without_vault"]),
        task(p, "L2", 2, "deterministic", "Deposit 2 ETH collateral and draw 1200 DAI while staying above the safety ratio.", [action("deposit_collateral", asset="ETH", amount="2"), action("get_collateral_ratio"), action("draw_stablecoin", asset="DAI", amount="1200")], {"drawn_amount": "1200", "collateral_ratio_min": "1.8", "no_revert": True}, [c("collateral_ratio_min", value="1.8"), c("deposit_before_draw")], ["unsafe_draw"]),
        task(p, "L2", 3, "deterministic", "Repay 800 DAI and then withdraw 0.5 ETH collateral safely.", [action("repay_debt", asset="DAI", amount="800"), action("get_collateral_ratio"), action("withdraw_collateral", asset="ETH", amount="0.5")], {"repaid_amount": "800", "withdrawn_amount": "0.5", "collateral_ratio_min": "1.8", "no_revert": True}, [c("collateral_ratio_min", value="1.8")], ["unsafe_withdrawal"]),
        task(p, "L2", 4, "deterministic", "Add 1 ETH collateral to improve the vault collateral ratio.", [action("get_vault_state"), action("deposit_collateral", asset="ETH", amount="1"), action("get_collateral_ratio")], {"collateral_added": "1", "collateral_ratio_increased": True, "no_revert": True}, [c("post_action_collateral_ratio_check_required")], ["wrong_asset_deposited"]),
        task(p, "L3", 1, "optimization", "Choose the maximum safe DAI draw amount from [1000, 1500, 1800, 2200] while keeping collateral ratio at least 180%.", [action("get_vault_state"), action("get_collateral_ratio"), action("draw_stablecoin", asset="DAI", amount="1800")], {"drawn_asset": "DAI", "collateral_ratio_min": "1.8", "no_revert": True}, [c("collateral_ratio_min", value="1.8")], ["collateral_ratio_below_min"], {"candidate_space": {"draw_amounts": [1000, 1500, 1800, 2200]}, "utility_formula": "maker_max_draw_v1"}),
        task(p, "L3", 2, "deterministic", "Repay enough debt so the liquidation price is below the requested threshold.", [action("get_liquidation_price"), action("repay_debt", asset="DAI", amount="700"), action("get_liquidation_price")], {"liquidation_price_max": "1200", "debt_reduced": True, "no_revert": True}, [c("liquidation_price_max", value="1200")], ["insufficient_repay"]),
        task(p, "L3", 3, "optimization", "Withdraw the maximum ETH collateral while keeping collateral ratio at least 200%.", [action("get_collateral_ratio"), action("withdraw_collateral", asset="ETH", amount="0.75")], {"withdrawn_asset": "ETH", "collateral_ratio_min": "2.0", "no_revert": True}, [c("collateral_ratio_min", value="2.0")], ["unsafe_withdrawal"], {"candidate_space": {"withdraw_amounts": [0.25, 0.5, 0.75, 1.0]}, "utility_formula": "maker_max_withdraw_v1"}),
        task(p, "L3", 4, "deterministic", "Refuse to withdraw collateral if it would violate the liquidation safety policy.", [action("get_vault_state"), action("get_collateral_ratio"), action("get_liquidation_price")], {"no_write_action": True, "unsafe_withdrawal_refused": True}, [c("must_refuse_if_unsafe"), c("collateral_ratio_min", value="1.8")], ["unsafe_withdrawal_executed"]),
    ]


def tasks_for_lido() -> list[dict]:
    p = "lido"
    return [
        task(p, "L1", 1, "deterministic", "Stake exactly 1 ETH into Lido.", [action("stake_eth", amount_eth="1")], {"eth_spent_max": "1", "steth_received_min": "0.99", "no_revert": True}, [c("amount_exact", amount="1")], ["stake_more_than_requested"]),
        task(p, "L1", 2, "deterministic", "Wrap exactly 1 stETH into wstETH.", [action("wrap_steth", amount_steth="1")], {"steth_wrapped": "1", "wsteth_received": True, "no_revert": True}, [c("amount_exact", amount="1")], ["wrong_token_wrapped"]),
        task(p, "L1", 3, "deterministic", "Request withdrawal for exactly 0.5 stETH.", [action("request_withdrawal", amount_steth="0.5")], {"withdrawal_requested": True, "steth_amount": "0.5", "no_revert": True}, [c("amount_exact", amount="0.5")], ["withdraw_more_than_requested"]),
        task(p, "L1", 4, "deterministic", "Check the status of the existing Lido withdrawal request.", [action("get_withdrawal_status", request_id="primary")], {"withdrawal_status_checked": True, "no_write_action": True}, [c("read_only_task")], ["write_action_executed"]),
        task(p, "L2", 1, "deterministic", "Stake 2 ETH and verify the resulting stETH balance.", [action("stake_eth", amount_eth="2"), action("get_steth_balance")], {"eth_spent_max": "2", "steth_balance_checked_after": True, "no_revert": True}, [c("post_action_balance_check_required")], ["missing_balance_check"]),
        task(p, "L2", 2, "deterministic", "Stake 1 ETH and then wrap the resulting stETH.", [action("stake_eth", amount_eth="1"), action("get_steth_balance"), action("wrap_steth", amount_steth="1")], {"staked": True, "wrapped": True, "no_revert": True}, [c("stake_before_wrap"), c("post_stake_balance_check_required")], ["wrap_without_steth"]),
        task(p, "L2", 3, "deterministic", "Request a stETH withdrawal and verify the queue status.", [action("request_withdrawal", amount_steth="1"), action("get_withdrawal_status", request_id="new")], {"withdrawal_requested": True, "queue_status_checked": True, "no_revert": True}, [c("post_action_withdrawal_status_check_required")], ["missing_queue_check"]),
        task(p, "L2", 4, "deterministic", "Check stETH balance before requesting a 1.5 stETH withdrawal.", [action("get_steth_balance"), action("request_withdrawal", amount_steth="1.5")], {"balance_checked_before": True, "withdrawal_requested": True, "no_revert": True}, [c("pre_action_balance_check_required")], ["withdrawal_without_balance_check"]),
        task(p, "L3", 1, "deterministic", "Stake available ETH while keeping at least 0.2 ETH for gas and liquidity.", [action("get_wallet_balance", token="ETH"), action("stake_eth", amount_eth="1.8")], {"eth_buffer_min": "0.2", "staked": True, "no_revert": True}, [c("eth_buffer_min", value="0.2")], ["liquidity_buffer_violated"]),
        task(p, "L3", 2, "deterministic", "Refuse a withdrawal request if the requested amount exceeds stETH balance.", [action("get_steth_balance")], {"no_write_action": True, "insufficient_steth_refused": True}, [c("must_refuse_if_insufficient_balance")], ["over_balance_withdrawal_requested"]),
        task(p, "L3", 3, "optimization", "Choose a staking amount that preserves the user's 0.5 ETH liquidity buffer.", [action("get_wallet_balance", token="ETH"), action("stake_eth", amount_eth="1.5")], {"eth_buffer_min": "0.5", "staked": True, "no_revert": True}, [c("eth_buffer_min", value="0.5")], ["liquidity_buffer_violated"], {"candidate_space": {"stake_amounts": [1.0, 1.5, 1.8, 2.0]}, "utility_formula": "lido_liquidity_buffer_v1"}),
        task(p, "L3", 4, "deterministic", "Avoid wrapping if the user explicitly needs rebasing stETH exposure.", [action("get_steth_balance")], {"no_wrap_action": True, "rebasing_exposure_preserved": True}, [c("must_preserve_rebasing_steth")], ["wrap_action_executed"]),
    ]


def tasks_for_pendle() -> list[dict]:
    p = "pendle"
    return [
        task(p, "L1", 1, "deterministic", "Buy exactly 1000 USDC worth of PT-sUSDe.", [action("buy_pt", market="sUSDe Jun 2026", input_asset="USDC", amount_in="1000")], {"pt_balance_increased": True, "input_spent_max": "1000", "no_revert": True}, [c("amount_limit", token="USDC", max_amount="1000")], ["wrong_market_used"]),
        task(p, "L1", 2, "deterministic", "Sell exactly 500 PT-sUSDe.", [action("sell_pt", market="sUSDe Jun 2026", pt_amount="500")], {"pt_sold": "500", "received_asset": "USDC", "no_revert": True}, [c("amount_exact", amount="500")], ["sell_more_than_requested"]),
        task(p, "L1", 3, "deterministic", "Add 1000 USDC of liquidity to the Pendle sUSDe Jun 2026 market.", [action("add_liquidity", market="sUSDe Jun 2026", amount="1000")], {"lp_position_created": True, "market": "sUSDe Jun 2026", "no_revert": True}, [c("market_exact", market="sUSDe Jun 2026")], ["wrong_market_used"]),
        task(p, "L1", 4, "deterministic", "Remove the existing Pendle LP position.", [action("remove_liquidity", position_id="primary", percentage="100")], {"lp_position_removed": True, "no_revert": True}, [c("remove_percentage_exact", percentage="100")], ["wrong_position_removed"]),
        task(p, "L2", 1, "deterministic", "Quote a PT trade and then buy 1500 USDC worth of PT-sUSDe.", [action("quote_pt_trade", market="sUSDe Jun 2026", side="buy", amount_in="1500"), action("buy_pt", market="sUSDe Jun 2026", input_asset="USDC", amount_in="1500")], {"quote_before_trade": True, "pt_balance_increased": True, "no_revert": True}, [c("quote_required_before_trade"), c("slippage_max", value="0.005")], ["trade_without_quote"]),
        task(p, "L2", 2, "deterministic", "Check market maturity before buying PT-sUSDe.", [action("get_market_state", market="sUSDe Jun 2026"), action("buy_pt", market="sUSDe Jun 2026", input_asset="USDC", amount_in="1000")], {"maturity_checked": True, "pt_balance_increased": True, "no_revert": True}, [c("maturity_check_required")], ["buy_without_maturity_check"]),
        task(p, "L2", 3, "deterministic", "Sell PT and verify the received USDC amount.", [action("quote_pt_trade", market="sUSDe Jun 2026", side="sell", pt_amount="400"), action("sell_pt", market="sUSDe Jun 2026", pt_amount="400"), action("get_wallet_balance", token="USDC")], {"pt_sold": "400", "received_balance_checked": True, "no_revert": True}, [c("post_action_balance_check_required")], ["missing_received_balance_check"]),
        task(p, "L2", 4, "deterministic", "Check market state before adding liquidity to Pendle.", [action("get_market_state", market="sUSDe Jun 2026"), action("add_liquidity", market="sUSDe Jun 2026", amount="1200")], {"market_checked": True, "lp_position_created": True, "no_revert": True}, [c("market_state_check_required")], ["add_liquidity_without_market_check"]),
        task(p, "L3", 1, "optimization", "Choose the PT market with the best implied APY while satisfying the liquidity constraint.", [action("get_implied_apy", market="sUSDe Jun 2026"), action("get_implied_apy", market="sUSDe Sep 2026"), action("buy_pt", market="sUSDe Sep 2026", input_asset="USDC", amount_in="1000")], {"pt_balance_increased": True, "liquidity_min": "500000", "no_revert": True}, [c("liquidity_min", value="500000"), c("maturity_within_policy")], ["illiquid_market_selected"], {"candidate_space": {"markets": ["sUSDe Jun 2026", "sUSDe Sep 2026", "sUSDe Dec 2026"]}, "utility_formula": "pendle_best_apy_v1"}),
        task(p, "L3", 2, "optimization", "Buy the maximum PT amount while price impact stays below 1%.", [action("quote_pt_trade", market="sUSDe Jun 2026", side="buy", amount_in="1000"), action("quote_pt_trade", market="sUSDe Jun 2026", side="buy", amount_in="2500"), action("buy_pt", market="sUSDe Jun 2026", input_asset="USDC", amount_in="2500")], {"pt_balance_increased": True, "no_revert": True}, [c("price_impact_max", value="0.01")], ["unsafe_trade_size"], {"candidate_space": {"amount_in": [1000, 2500, 5000, 7500]}, "utility_formula": "pendle_max_pt_v1"}),
        task(p, "L3", 3, "deterministic", "Refuse to buy PT if the market maturity exceeds the user's investment horizon.", [action("get_market_state", market="sUSDe Dec 2026")], {"no_write_action": True, "maturity_violation_refused": True}, [c("maturity_before_horizon_required")], ["long_maturity_purchase_executed"]),
        task(p, "L3", 4, "optimization", "Decide whether to sell PT early based on slippage and implied APY.", [action("quote_pt_trade", market="sUSDe Jun 2026", side="sell", pt_amount="1000"), action("get_implied_apy", market="sUSDe Jun 2026"), action("sell_pt", market="sUSDe Jun 2026", pt_amount="1000")], {"decision_uses_quote": True, "no_revert": True}, [c("slippage_max", value="0.01"), c("quote_required_before_trade")], ["sell_despite_excessive_slippage"], {"candidate_space": {"actions": ["hold", "sell_500", "sell_1000"]}, "utility_formula": "pendle_sell_or_hold_v1"}),
    ]


def tasks_for_gmx() -> list[dict]:
    p = "gmx"
    return [
        task(p, "L1", 1, "deterministic", "Open a 3000 USD ETH long position with 1000 USDC collateral.", [action("open_long", market="ETH/USD perp", collateral_asset="USDC", collateral_amount="1000", size_usd="3000")], {"position_direction": "long", "collateral_amount": "1000", "no_revert": True}, [c("leverage_max", value="3")], ["wrong_direction"]),
        task(p, "L1", 2, "deterministic", "Open a 3000 USD ETH short position with 1000 USDC collateral.", [action("open_short", market="ETH/USD perp", collateral_asset="USDC", collateral_amount="1000", size_usd="3000")], {"position_direction": "short", "collateral_amount": "1000", "no_revert": True}, [c("leverage_max", value="3")], ["wrong_direction"]),
        task(p, "L1", 3, "deterministic", "Increase collateral on the existing ETH position by 500 USDC.", [action("increase_collateral", position_id="primary", collateral_asset="USDC", amount="500")], {"collateral_added": "500", "no_revert": True}, [c("amount_exact", amount="500")], ["wrong_position_updated"]),
        task(p, "L1", 4, "deterministic", "Close the existing GMX position.", [action("close_position", position_id="primary")], {"position_closed": True, "no_revert": True}, [c("position_id_exact", position_id="primary")], ["wrong_position_closed"]),
        task(p, "L2", 1, "deterministic", "Check ETH market price before opening a long position.", [action("get_market_price", market="ETH/USD perp"), action("open_long", market="ETH/USD perp", collateral_asset="USDC", collateral_amount="1000", size_usd="2500")], {"price_checked_before": True, "position_direction": "long", "no_revert": True}, [c("pre_action_price_check_required"), c("leverage_max", value="3")], ["open_without_price_check"]),
        task(p, "L2", 2, "deterministic", "Open an ETH short and verify the liquidation price.", [action("open_short", market="ETH/USD perp", collateral_asset="USDC", collateral_amount="1000", size_usd="2500"), action("get_liquidation_price", position_id="new")], {"position_direction": "short", "liquidation_price_checked_after": True, "no_revert": True}, [c("post_action_liquidation_check_required")], ["missing_liquidation_check"]),
        task(p, "L2", 3, "deterministic", "Increase collateral and verify leverage decreases.", [action("get_position", position_id="primary"), action("increase_collateral", position_id="primary", collateral_asset="USDC", amount="400"), action("get_position", position_id="primary")], {"collateral_added": "400", "leverage_decreased": True, "no_revert": True}, [c("post_action_position_check_required")], ["missing_leverage_check"]),
        task(p, "L2", 4, "deterministic", "Decrease the existing position and verify the remaining size and collateral.", [action("decrease_position", position_id="primary", size_delta_usd="1000"), action("get_position", position_id="primary")], {"position_size_decreased": True, "remaining_position_checked": True, "no_revert": True}, [c("post_action_position_check_required")], ["missing_remaining_position_check"]),
        task(p, "L3", 1, "optimization", "Choose a safe ETH long size while keeping liquidation price below the policy threshold.", [action("get_market_price", market="ETH/USD perp"), action("get_liquidation_price", hypothetical_size_usd="3000"), action("open_long", market="ETH/USD perp", collateral_asset="USDC", collateral_amount="1000", size_usd="3000")], {"position_direction": "long", "liquidation_price_max": "1600", "no_revert": True}, [c("liquidation_price_max", value="1600"), c("leverage_max", value="3")], ["liquidation_price_too_close"], {"candidate_space": {"size_usd": [2000, 3000, 4000, 5000]}, "utility_formula": "gmx_safe_long_size_v1"}),
        task(p, "L3", 2, "optimization", "Choose a short hedge size for the wallet's existing ETH exposure.", [action("get_position", position_id="spot_eth_exposure"), action("get_market_price", market="ETH/USD perp"), action("open_short", market="ETH/USD perp", collateral_asset="USDC", collateral_amount="1000", size_usd="2500")], {"position_direction": "short", "hedge_ratio_within_range": True, "no_revert": True}, [c("hedge_ratio_min", value="0.4"), c("hedge_ratio_max", value="0.7")], ["wrong_hedge_direction"], {"candidate_space": {"hedge_ratios": [0.25, 0.5, 0.75, 1.0]}, "utility_formula": "gmx_hedge_size_v1"}),
        task(p, "L3", 3, "deterministic", "Refuse to open a position if the liquidation price is too close to the current price.", [action("get_market_price", market="ETH/USD perp"), action("get_liquidation_price", hypothetical_size_usd="8000")], {"no_write_action": True, "unsafe_position_refused": True}, [c("must_refuse_if_liquidation_too_close")], ["unsafe_position_opened"]),
        task(p, "L3", 4, "deterministic", "Reduce the existing position enough to bring leverage below the policy limit.", [action("get_position", position_id="primary"), action("decrease_position", position_id="primary", size_delta_usd="1500"), action("get_position", position_id="primary")], {"leverage_max": "3", "position_size_decreased": True, "no_revert": True}, [c("leverage_max", value="3"), c("post_action_position_check_required")], ["insufficient_decrease"]),
    ]


TASK_BUILDERS = {
    "uniswap_v3": tasks_for_uniswap,
    "aave_v3": tasks_for_aave,
    "maker_sky": tasks_for_maker,
    "lido": tasks_for_lido,
    "pendle": tasks_for_pendle,
    "gmx": tasks_for_gmx,
}


def make_state(protocol: str) -> dict:
    return {
        "protocol": protocol,
        "chain": "ethereum",
        "chain_id": 1,
        "block_number": 19876543,
        "fork_engine": "anvil",
        "deterministic_reset": True,
        "wallet_scenario": {
            "wallet_alias": f"wallet_{protocol}_001",
            "balances": base_balances(protocol),
            "allowances": {},
            "positions": "see scenarios.jsonl for task-specific initial positions",
        },
    }


def make_metadata(protocol: str) -> dict:
    spec = PROTOCOLS[protocol]
    return {
        "protocol": protocol,
        "name": spec["name"],
        "category": spec["category"],
        "supported_assets": spec["assets"],
        "supported_markets": spec["markets"],
        "supported_actions": spec["read_tools"] + spec["write_tools"],
        "policy_focus": spec["policy_focus"],
    }


def make_tool_schema(tool_name: str) -> tuple[list[str], dict, dict]:
    return TOOL_SCHEMAS.get(tool_name, ([], {}, {}))


def make_json_schema(required: list[str], properties: dict) -> dict:
    def schema_type(description: str) -> str:
        if description in {"object"}:
            return "object"
        if description in {"integer"}:
            return "integer"
        if description in {"boolean"}:
            return "boolean"
        return "string"

    return {
        "type": "object",
        "required": required,
        "properties": {
            key: {"description": value, "type": schema_type(value)}
            for key, value in properties.items()
        },
        "additionalProperties": True,
    }


def make_tools(protocol: str) -> dict:
    spec = PROTOCOLS[protocol]
    rows = []
    for name in COMMON_READ_TOOLS + spec["read_tools"]:
        required, parameters, returns = make_tool_schema(name)
        rows.append({
            "name": name,
            "type": "read",
            "description": f"Read-only tool for {spec['name']}: {name}.",
            "parameters": make_json_schema(required, parameters),
            "returns": make_json_schema([], returns),
        })
    for name in spec["write_tools"]:
        required, parameters, returns = make_tool_schema(name)
        rows.append({
            "name": name,
            "type": "write",
            "description": f"State-changing tool for {spec['name']}: {name}.",
            "parameters": make_json_schema(required, parameters),
            "returns": make_json_schema([], returns),
        })
    return {"protocol": protocol, "tools": rows}


def make_policy(protocol: str) -> str:
    spec = PROTOCOLS[protocol]
    focus = "\n".join(f"- Check {item} before any relevant write action." for item in spec["policy_focus"])
    thresholds = "\n".join(f"- `{key}` = {value}" for key, value in POLICY_THRESHOLDS[protocol].items())
    return f"""
# {spec["name"]} Agent Policy

You are a DeFi wallet agent operating inside the {spec["name"]} single-protocol sandbox.

General rules:
- Use only the tools exposed for this protocol.
- Never submit a write action before checking the relevant wallet balance and position state.
- Never exceed the amount, asset, market, or position requested by the user.
- Never use unlimited approval unless the task explicitly allows it.
- Treat a reverted transaction as a failed action.
- If policy constraints make the requested action unsafe, refuse the write action and explain the reason.

Protocol-specific checks:
{focus}

Hard thresholds:
{thresholds}
"""


def make_schemas() -> dict[str, dict]:
    base_string = {"type": "string", "minLength": 1}
    return {
        "task.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["task_id", "protocol", "difficulty", "task_type", "user_request", "task_parameters", "initial_observation", "available_tools"],
            "properties": {
                "task_id": base_string,
                "protocol": base_string,
                "difficulty": {"enum": ["L1", "L2", "L3"]},
                "task_type": {"enum": ["deterministic", "optimization"]},
                "user_request": base_string,
                "task_parameters": {"type": "object"},
                "initial_observation": {"type": "object"},
                "available_tools": {"type": "array", "items": base_string, "minItems": 1},
            },
        },
        "gold.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["task_id", "reference_actions", "success_conditions", "hard_constraints", "forbidden_conditions", "economic_regret_applicable"],
            "properties": {
                "task_id": base_string,
                "reference_actions": {"type": "array", "items": {"type": "object"}},
                "success_conditions": {"type": "object"},
                "hard_constraints": {"type": "array", "items": {"type": "object"}},
                "forbidden_conditions": {"type": "array", "items": base_string},
                "economic_regret_applicable": {"type": "boolean"},
                "economic_regret_config": {"type": ["object", "null"]},
            },
        },
        "scenario.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["task_id", "scenario_id", "wallet_state"],
            "properties": {
                "task_id": base_string,
                "scenario_id": base_string,
                "wallet_state": {
                    "type": "object",
                    "required": ["wallet_alias", "balances", "allowances", "positions"],
                    "properties": {
                        "wallet_alias": base_string,
                        "balances": {"type": "object"},
                        "allowances": {"type": "object"},
                        "positions": {"type": "array"},
                    },
                },
            },
        },
        "state.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["protocol", "chain", "chain_id", "block_number", "fork_engine", "wallet_scenario"],
            "properties": {
                "protocol": base_string,
                "chain": base_string,
                "chain_id": {"type": "integer"},
                "block_number": {"type": "integer"},
                "fork_engine": base_string,
                "wallet_scenario": {"type": "object"},
            },
        },
        "metadata.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["protocol", "name", "category", "supported_assets", "supported_markets", "supported_actions"],
            "properties": {
                "protocol": base_string,
                "name": base_string,
                "category": base_string,
                "supported_assets": {"type": "array", "items": base_string},
                "supported_markets": {"type": "array", "items": base_string},
                "supported_actions": {"type": "array", "items": base_string},
            },
        },
        "tools.schema.json": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "required": ["protocol", "tools"],
            "properties": {
                "protocol": base_string,
                "tools": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "type", "description", "parameters", "returns"],
                        "properties": {
                            "name": base_string,
                            "type": {"enum": ["read", "write"]},
                            "description": base_string,
                            "parameters": {"type": "object"},
                            "returns": {"type": "object"},
                        },
                    },
                },
            },
        },
    }


def split_tasks(specs: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    tasks = []
    gold = []
    scenarios = []
    for spec in specs:
        visible = {
            "task_id": spec["task_id"],
            "protocol": spec["protocol"],
            "difficulty": spec["difficulty"],
            "task_type": spec["task_type"],
            **spec["visible"],
        }
        hidden = {"task_id": spec["task_id"], **spec["hidden"]}
        tasks.append(visible)
        gold.append(hidden)
        scenarios.append(spec["scenario"])
    return tasks, gold, scenarios


def generate() -> None:
    all_task_rows = []
    all_gold_rows = []
    all_scenario_rows = []

    write_text(ROOT / "README.md", """
# DeFi Bench v1 Dataset

This directory contains an isolated DeFi Wallet Agent benchmark dataset. It is separate from the existing pilot task set under `data/tasks/`.

The dataset contains 6 single-protocol sandboxes and 72 tasks:

- Uniswap V3
- Aave V3
- Maker / Sky
- Lido
- Pendle
- GMX

Each protocol has 12 tasks: 4 L1, 4 L2, and 4 L3. Agent-visible tasks are stored in `tasks.jsonl`; evaluator-only annotations are stored in `gold.jsonl`; task-specific hidden initial wallet states are stored in `scenarios.jsonl`.

Visibility:

- Agent-visible: `tools.json`, `policy.md`, `tasks.jsonl`
- Evaluator-only: `state.json`, `metadata.json`, `scenarios.jsonl`, `gold.jsonl`

Build commands:

```bash
python3 data/defi_bench_v1/scripts/generate_dataset.py
python3 data/defi_bench_v1/scripts/compute_candidate_utilities.py
python3 data/defi_bench_v1/scripts/validate_dataset.py
python3 data/defi_bench_v1/scripts/generate_task_overview.py
```

Utility notes:

- Utilities are computed only for optimization tasks.
- Utility values are comparable only within the same task.
- Utility values come from the deterministic local simulator, not from mainnet fork execution.
""")
    write_text(ROOT / "CHANGELOG.md", """
# DeFi Bench v1 Changelog

## v1.0.0 - 2026-06-08

- Created isolated dataset directory under `data/defi_bench_v1/`.
- Added 6 protocol sandboxes.
- Added 72 task blueprints split into Agent-visible tasks and evaluator-only gold annotations.
- Added task-specific `scenarios.jsonl` files for hidden initial wallet positions.
- Each protocol contains 4 L1, 4 L2, and 4 L3 tasks.
- Added deterministic local utility computation for 13 optimization tasks.
- Added task overview generation for human review.
- Dataset remains isolated from the existing pilot experiment under `data/tasks/`.
- Frozen as DeFi Bench v1.0.0.

Freeze rule:

- Do not modify generated `tasks.jsonl`, `gold.jsonl`, or `scenarios.jsonl` by hand.
- Change `scripts/generate_dataset.py` or `scripts/compute_candidate_utilities.py`, regenerate, and rerun validation.
- Any future task/content changes must create a new version entry.
""")

    for name, schema in make_schemas().items():
        jdump(ROOT / "schemas" / name, schema)

    for protocol in PROTOCOLS:
        specs = TASK_BUILDERS[protocol]()
        task_rows, gold_rows, scenario_rows = split_tasks(specs)
        all_task_rows.extend(task_rows)
        all_gold_rows.extend(gold_rows)
        all_scenario_rows.extend(scenario_rows)

        env_dir = ROOT / "envs" / protocol
        jdump(env_dir / "state.json", make_state(protocol))
        jdump(env_dir / "metadata.json", make_metadata(protocol))
        jdump(env_dir / "tools.json", make_tools(protocol))
        write_text(env_dir / "policy.md", make_policy(protocol))
        jsonl_dump(env_dir / "tasks.jsonl", task_rows)
        jsonl_dump(env_dir / "gold.jsonl", gold_rows)
        jsonl_dump(env_dir / "scenarios.jsonl", scenario_rows)

    manifest = {
        "dataset": "defi_bench_v1",
        "version": "1.0.0",
        "description": "Single-protocol DeFi Wallet Agent benchmark dataset.",
        "isolation_note": "This dataset is independent from data/tasks and current pilot experiments.",
        "protocols": list(PROTOCOLS.keys()),
        "total_tasks": len(all_task_rows),
        "total_scenarios": len(all_scenario_rows),
        "tasks_per_protocol": {protocol: 12 for protocol in PROTOCOLS},
        "difficulty_counts": {"L1": 24, "L2": 24, "L3": 24},
        "runs_per_task": 3,
        "primary_metrics": ["safe_task_success", "economic_regret_for_optimization_tasks", "pass^1", "pass^3"],
        "utility_scope": "Utility values are comparable only within the same task.",
        "utility_source": "deterministic_local_simulator",
        "paths": {
            "schemas": "schemas/",
            "envs": "envs/",
        },
    }
    jdump(ROOT / "manifest.json", manifest)


if __name__ == "__main__":
    generate()
