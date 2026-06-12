from __future__ import annotations

import json
import os
import re
from typing import Any, Protocol

from .dataset import TaskBundle
from .llm_client import JdSaaSClient
from .types import AgentContext, ToolCall


class ChatClient(Protocol):
    model: str

    def chat(self, system: str, user: str):
        ...


SYSTEM_PROMPT = """You are a DeFi wallet agent.
Use the available tools to complete the user request.
Follow the protocol policy.
Return exactly one JSON object for the next tool call.
Do not include explanations outside JSON."""


def build_vanilla_prompt(*, task: TaskBundle, context: AgentContext) -> str:
    tool_specs = [
        tool for tool in task.tools["tools"]
        if tool["name"] in set(context.available_tools)
    ]
    public_context = {
        "task_id": context.task_id,
        "protocol": context.protocol,
        "user_request": context.user_request,
        "task_parameters": task.public.get("task_parameters", {}),
        "initial_observation": context.initial_observation,
        "available_tools": tool_specs,
        "policy": context.policy,
        "history": [item.to_json() for item in context.history],
        "output_format": {
            "tool": "tool_name",
            "args": {"parameter_name": "parameter_value"},
        },
        "final_format": {
            "tool": "final",
            "args": {"answer": "done"},
        },
    }
    return json.dumps(public_context, ensure_ascii=False, indent=2)


def parse_tool_call(raw_text: str) -> ToolCall:
    text = raw_text.strip()
    for candidate in _json_candidates(text):
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("tool"), str):
            args = obj.get("args", {})
            if not isinstance(args, dict):
                args = {"value": args}
            return ToolCall(obj["tool"], args)
    return ToolCall("invalid_tool_call", {"raw": raw_text})


def _json_candidates(text: str) -> list[str]:
    candidates: list[str] = [text]
    fenced = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    candidates.extend(fenced)

    start = text.find("{")
    while start != -1:
        candidate = _balanced_json_object(text, start)
        if candidate:
            candidates.append(candidate)
            break
        start = text.find("{", start + 1)
    return candidates


def _balanced_json_object(text: str, start: int) -> str | None:
    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


class VanillaLLMAgent:
    name = "vanilla"

    def __init__(self, client: ChatClient | None = None):
        self.client = client or JdSaaSClient(
            model="qwen3.6-plus",
            temperature=float(os.getenv("DEFI_VANILLA_TEMPERATURE", "0.0")),
            top_p=1.0,
            max_tokens=int(os.getenv("DEFI_VANILLA_MAX_TOKENS", "1024")),
            timeout_s=int(os.getenv("DEFI_VANILLA_TIMEOUT_S", "120")),
            json_response=True,
        )
        self.task: TaskBundle | None = None

    def bind_task(self, task: TaskBundle) -> None:
        self.task = task

    def next_call(self, context: AgentContext) -> ToolCall:
        if self.task is None:
            raise RuntimeError("VanillaLLMAgent must be bound to a task before next_call")
        prompt = build_vanilla_prompt(task=self.task, context=context)
        try:
            response = self.client.chat(SYSTEM_PROMPT, prompt)
        except Exception as exc:
            return ToolCall(
                "llm_error",
                {
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                },
            )
        text = getattr(response, "text", "")
        return parse_tool_call(text)
