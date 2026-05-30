"""Minimal multi-provider chat clients.

Ported from SoundnessBench `rigorbench/llm/client.py` (OpenAI / Anthropic
/ Gemini / Vertex / vLLM, unified `chat()` interface), plus a
`RandomBaseline` so the full load -> score -> metrics pipeline is runnable
offline with no API key (chance-level reference for the gold set).
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Any

import yaml


class LLMClient:
    """Unified chat interface used by the calibration runner."""

    model: str
    max_tokens: int
    temperature: float

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        raise NotImplementedError


class RandomBaseline(LLMClient):
    """Pseudo-client predicting uniformly random rigor buckets (offline)."""

    model = "random_baseline"
    max_tokens = 0
    temperature = 0.0

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        bucket = self._rng.choice(["low", "high"])
        confidence = self._rng.randint(1, 5)
        return json.dumps(
            {"rigor_bucket": bucket, "confidence": confidence, "justification": "random baseline"}
        )


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # eval/judge/client.py -> repo root is three parents up.
    repo_root = Path(__file__).resolve().parent.parent.parent
    load_dotenv(repo_root / ".env")


def _load_config(config_path: str | Path | None = None) -> dict[str, Any]:
    _load_dotenv()
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    path = Path(config_path)
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class OpenAIChatClient(LLMClient):
    """OpenAI API or OpenAI-compatible endpoint, including vLLM."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY") or "dummy"
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.temperature = temperature

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Install openai: pip install openai") from None

        client_kwargs: dict[str, Any] = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        client = OpenAI(**client_kwargs)

        create_kwargs: dict[str, Any] = {"model": self.model, "messages": messages}
        token_value = kwargs.get("max_tokens", self.max_tokens)
        if self.base_url and "openai.com" in self.base_url:
            create_kwargs["max_completion_tokens"] = token_value
        else:
            create_kwargs["max_tokens"] = token_value
            create_kwargs["temperature"] = kwargs.get("temperature", self.temperature)
        response = client.chat.completions.create(**create_kwargs)
        if not response.choices:
            return ""
        return (response.choices[0].message.content or "").strip()


class AnthropicChatClient(LLMClient):
    """Anthropic Messages API client."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY") or ""
        self.max_tokens = max_tokens
        self.temperature = temperature

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("Install anthropic: pip install anthropic") from None

        system = ""
        anthropic_messages: list[dict[str, str]] = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                system = content
            else:
                anthropic_messages.append({"role": role, "content": content})

        client = Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
            temperature=kwargs.get("temperature", self.temperature),
            system=system or None,
            messages=anthropic_messages,
        )
        if response.content:
            return (response.content[0].text or "").strip()
        return ""


class GeminiChatClient(LLMClient):
    """Google AI Studio Gemini chat client."""

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        max_tokens: int = 2048,
        temperature: float = 0.2,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY") or ""
        self.max_tokens = max_tokens
        self.temperature = temperature

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("Install google-generativeai: pip install google-generativeai") from None

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        prompt = "\n\n".join(f"[{m.get('role', 'user')}]\n{m.get('content', '')}" for m in messages)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
            ),
        )
        return (response.text or "").strip() if response and response.text else ""


def get_llm_client(
    provider: str | None = None,
    config_path: str | Path | None = None,
    model: str | None = None,
) -> LLMClient:
    """Create the configured chat client for calibration."""
    cfg = _load_config(config_path)
    provider = (provider or cfg.get("provider") or os.environ.get("LLM_PROVIDER") or "openai").lower()
    max_tokens = int(cfg.get("max_tokens", 2048))
    temperature = float(cfg.get("temperature", 0.2))

    if provider in ("random", "random_baseline"):
        return RandomBaseline(seed=int(cfg.get("seed", 42)))

    if provider == "openai":
        openai_cfg = cfg.get("openai") or {}
        return OpenAIChatClient(
            model=model or openai_cfg.get("model", "gpt-4o-mini"),
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=openai_cfg.get("base_url"),
            max_tokens=max_tokens,
            temperature=temperature,
        )

    if provider == "vllm":
        vllm_cfg = cfg.get("vllm") or {}
        return OpenAIChatClient(
            model=model or vllm_cfg.get("model", "Qwen/Qwen2.5-7B-Instruct"),
            api_key=os.environ.get("VLLM_API_KEY", "dummy"),
            base_url=vllm_cfg.get("base_url", "http://localhost:8000/v1"),
            max_tokens=max_tokens,
            temperature=temperature,
        )

    if provider == "anthropic":
        anthropic_cfg = cfg.get("anthropic") or {}
        return AnthropicChatClient(
            model=model or anthropic_cfg.get("model", "claude-3-5-sonnet-20241022"),
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            max_tokens=max_tokens,
            temperature=temperature,
        )

    if provider == "gemini":
        google_cfg = cfg.get("google") or {}
        return GeminiChatClient(
            model=model or google_cfg.get("model", "gemini-2.5-pro"),
            api_key=os.environ.get("GOOGLE_API_KEY"),
            max_tokens=max_tokens,
            temperature=temperature,
        )

    raise ValueError("Unknown LLM provider. Use one of: openai, anthropic, gemini, vllm, random")
