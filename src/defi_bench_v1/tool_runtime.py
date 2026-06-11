from __future__ import annotations

from copy import deepcopy
from typing import Any

from .dataset import TaskBundle
from .types import ToolCall, ToolObservation


class ProtocolSandbox:
    def __init__(self, task: TaskBundle):
        self.task = task
        self.tool_specs = {tool["name"]: tool for tool in task.tools["tools"]}
        self.wallet_state = deepcopy(task.scenario["wallet_state"])
        self.executed_calls: list[ToolCall] = []

    def execute(self, call: ToolCall) -> ToolObservation:
        if call.tool == "final":
            return ToolObservation(call.tool, "success", {"final": True}, None)

        if call.tool not in self.tool_specs:
            return ToolObservation(call.tool, "revert", {}, f"unknown_tool:{call.tool}")

        missing = self._missing_required_args(call)
        if missing:
            return ToolObservation(
                call.tool,
                "revert",
                {},
                f"missing_required_args:{','.join(missing)}",
            )

        spec = self.tool_specs[call.tool]
        self.executed_calls.append(call)
        if spec["type"] == "read":
            return ToolObservation(call.tool, "success", self._execute_read(call), None)
        return self._execute_write(call)

    def protocol_actions(self) -> list[dict[str, Any]]:
        return [call.to_json() for call in self.executed_calls if call.tool != "final"]

    def _missing_required_args(self, call: ToolCall) -> list[str]:
        spec = self.tool_specs[call.tool]
        required = spec.get("parameters", {}).get("required", [])
        return [name for name in required if name not in call.args]

    def _execute_read(self, call: ToolCall) -> dict[str, Any]:
        if call.tool == "get_wallet_balance":
            token = call.args["token"]
            return {"balance": self.wallet_state.get("balances", {}).get(token, "0")}
        if call.tool == "get_allowance":
            token = call.args["token"]
            spender = call.args["spender"]
            allowance = self.wallet_state.get("allowances", {}).get(token, {}).get(spender, "0")
            return {"allowance": allowance}
        if call.tool in {"get_user_position", "get_position", "get_lp_position", "get_vault_state"}:
            return {"positions": self.wallet_state.get("positions", [])}
        if call.tool == "get_steth_balance":
            return {"balance": self.wallet_state.get("balances", {}).get("stETH", "0")}
        return {"simulated": True, "tool": call.tool, "args": call.args}

    def _execute_write(self, call: ToolCall) -> ToolObservation:
        if call.tool == "approve":
            token = call.args["token"]
            spender = call.args["spender"]
            amount = call.args["amount"]
            self.wallet_state.setdefault("allowances", {}).setdefault(token, {})[spender] = amount
            return ToolObservation(
                call.tool,
                "success",
                {"tx_status": "success", "allowance": amount},
                None,
            )

        return ToolObservation(
            call.tool,
            "success",
            {"tx_status": "success", "applied": call.tool},
            None,
        )
