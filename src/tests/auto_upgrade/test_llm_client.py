"""Unit tests for auto_upgrade.llm.client."""

from __future__ import annotations

import importlib

import pytest

from auto_upgrade.llm.client import SUPPORTED_MODELS, validate_model


class TestValidateModel:
    def test_accepts_all_supported_models(self):
        for model_id in SUPPORTED_MODELS:
            assert validate_model(model_id) == model_id

    def test_rejects_unknown_model(self):
        with pytest.raises(ValueError, match="Unsupported model"):
            validate_model("gpt-4")

    def test_error_message_lists_valid_options(self):
        with pytest.raises(ValueError) as excinfo:
            validate_model("claude-2")
        msg = str(excinfo.value)
        for model_id in SUPPORTED_MODELS:
            assert model_id in msg


class TestSupportedModels:
    def test_default_model_is_opus_4_6(self):
        assert "claude-opus-4-6" in SUPPORTED_MODELS

    def test_sonnet_and_haiku_are_available(self):
        assert "claude-sonnet-4-6" in SUPPORTED_MODELS
        assert "claude-haiku-4-5" in SUPPORTED_MODELS

    def test_every_entry_has_a_description(self):
        for model_id, desc in SUPPORTED_MODELS.items():
            assert isinstance(desc, str) and desc, f"empty description for {model_id}"


class TestGetLlm:
    def test_get_llm_requires_api_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

        import auto_upgrade.config as config_module
        importlib.reload(config_module)
        import auto_upgrade.llm.client as client_module
        importlib.reload(client_module)

        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            client_module.get_llm()

    def test_get_llm_rejects_unknown_model(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        import auto_upgrade.config as config_module
        importlib.reload(config_module)
        import auto_upgrade.llm.client as client_module
        importlib.reload(client_module)

        with pytest.raises(ValueError, match="Unsupported model"):
            client_module.get_llm(model="not-a-real-model")

    def test_get_llm_passes_args_to_chat_anthropic(self, monkeypatch):
        """Patch the lazy ChatAnthropic import and assert wiring."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")

        import auto_upgrade.config as config_module
        importlib.reload(config_module)
        import auto_upgrade.llm.client as client_module
        importlib.reload(client_module)

        captured: dict = {}

        class _FakeChatAnthropic:
            def __init__(self, **kwargs):
                captured.update(kwargs)

            def with_structured_output(self, schema):  # pragma: no cover
                return self

        fake_module = type(
            "fake_langchain_anthropic", (), {"ChatAnthropic": _FakeChatAnthropic}
        )
        monkeypatch.setitem(__import__("sys").modules, "langchain_anthropic", fake_module)

        llm = client_module.get_llm(model="claude-sonnet-4-6", temperature=0.2, max_tokens=4096)

        assert isinstance(llm, _FakeChatAnthropic)
        assert captured["model"] == "claude-sonnet-4-6"
        assert captured["temperature"] == 0.2
        assert captured["max_tokens"] == 4096
        assert captured["api_key"] == "sk-test"
