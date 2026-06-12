from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

import requests


@dataclass(frozen=True)
class LLMResponse:
    text: str
    latency_s: float
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class JdSaaSClient:
    """OpenAI-compatible chat client for JD SaaS."""

    def __init__(
        self,
        base_url: str = "https://agentrs.jd.com/api/saas/openai-u/v1",
        model: str = "qwen3.6-plus",
        api_key: str | None = None,
        temperature: float = 0.0,
        top_p: float = 1.0,
        max_tokens: int = 1024,
        timeout_s: int = 120,
        max_attempts: int = 2,
        retry_backoff_s: float = 2.0,
        json_response: bool = True,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key or os.getenv("JD_API_KEY")
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.timeout_s = timeout_s
        self.max_attempts = max(1, int(max_attempts))
        self.retry_backoff_s = max(0.0, float(retry_backoff_s))
        self.json_response = json_response
        if not self.api_key:
            raise ValueError(
                "JD_API_KEY is missing. Create a .env file in the project root "
                "or set the environment variable before running."
            )

    def chat(self, system: str, user: str) -> LLMResponse:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json;charset=UTF-8",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
        }
        if self.json_response:
            payload["response_format"] = {"type": "json_object"}

        t0 = time.time()
        last_error: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=self.timeout_s)
                response.encoding = "utf-8"
                if response.status_code in {429, 500, 502, 503, 504} and attempt < self.max_attempts:
                    time.sleep(self.retry_backoff_s * attempt)
                    continue
                response.raise_for_status()
                break
            except (
                requests.exceptions.ChunkedEncodingError,
                requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.SSLError,
                requests.exceptions.Timeout,
            ) as exc:
                last_error = exc
                if attempt >= self.max_attempts:
                    raise
                time.sleep(self.retry_backoff_s * attempt)
            except requests.exceptions.HTTPError as exc:
                last_error = exc
                retryable = (
                    exc.response is not None
                    and exc.response.status_code in {429, 500, 502, 503, 504}
                )
                if not retryable or attempt >= self.max_attempts:
                    raise
                time.sleep(self.retry_backoff_s * attempt)
        else:
            if last_error:
                raise last_error
            raise RuntimeError("JD SaaS request failed without an exception")

        latency_s = time.time() - t0
        data = response.json()
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        text = message.get("content")
        if isinstance(text, list):
            text = "".join(
                str(part.get("text", part)) if isinstance(part, dict) else str(part)
                for part in text
            )
        elif text is None:
            text = message.get("reasoning") or message.get("reasoning_content") or ""
        usage = data.get("usage") or {}
        return LLMResponse(
            text=text,
            latency_s=latency_s,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
        )
