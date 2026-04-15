"""Claude LLM client for auto-upgrade.

Only Anthropic Claude 4.x models are supported. The default model is
``claude-opus-4-6`` (highest reasoning quality), which is what the 7-phase
upgrade workflow is tuned for. Users can switch via ``--model`` on the CLI.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Optional

from auto_upgrade.config import DEFAULT_MODEL, settings


SUPPORTED_MODELS: dict[str, str] = {
    "claude-opus-4-6": "Highest reasoning. Default. Recommended for Phase 3/6.",
    "claude-sonnet-4-6": "Balanced cost/quality. Good for medium projects.",
    "claude-haiku-4-5": "Fastest/cheapest. Not recommended for breaking-change analysis.",
}
"""Whitelist of Claude models this agent accepts.

Keyed by model id. CLI will reject any model id not in this mapping and print
the supported options.
"""


def validate_model(model: str) -> str:
    """Return ``model`` if supported, otherwise raise ``ValueError``.

    The error message lists every valid option so the CLI can surface it
    directly to the user.
    """
    if model not in SUPPORTED_MODELS:
        valid = ", ".join(sorted(SUPPORTED_MODELS))
        raise ValueError(
            f"Unsupported model: {model!r}. Valid options are: {valid}"
        )
    return model


@lru_cache(maxsize=8)
def _build_llm(
    model: str,
    temperature: float,
    max_tokens: int,
    api_key: Optional[str],
) -> Any:
    """Cached factory so repeat calls with the same args return the same client.

    Imported lazily so that ``auto_upgrade`` remains importable (and the test
    suite for non-LLM modules remains runnable) even if ``langchain-anthropic``
    is not installed in the current environment.
    """
    from langchain_anthropic import ChatAnthropic  # lazy import

    return ChatAnthropic(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=api_key,
        timeout=120,
    )


def get_llm(
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 8192,
) -> Any:
    """Return a ``ChatAnthropic`` instance bound to the selected Claude model.

    Parameters
    ----------
    model:
        Optional override. If ``None``, uses ``settings.model`` (which itself
        defaults to ``claude-opus-4-6``).
    temperature:
        Sampling temperature. Defaults to 0 for deterministic reasoning.
    max_tokens:
        Maximum output tokens per call.
    """
    chosen = validate_model(model or settings.model or DEFAULT_MODEL)
    api_key = settings.require_api_key()
    return _build_llm(chosen, temperature, max_tokens, api_key)


def get_structured_llm(
    schema: Any,
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 8192,
) -> Any:
    """Return an LLM that is constrained to emit ``schema`` (a Pydantic model)."""
    return get_llm(
        model=model, temperature=temperature, max_tokens=max_tokens
    ).with_structured_output(schema)
