"""LLM client and prompt templates for auto-upgrade."""

from auto_upgrade.llm.client import SUPPORTED_MODELS, get_llm, get_structured_llm

__all__ = ["SUPPORTED_MODELS", "get_llm", "get_structured_llm"]
