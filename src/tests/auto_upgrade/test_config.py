"""Unit tests for auto_upgrade.config."""

from __future__ import annotations

import importlib

import pytest


def test_default_settings_reads_env(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    monkeypatch.setenv("AUTO_UPGRADE_MODEL", "claude-sonnet-4-6")
    monkeypatch.setenv("AUTO_UPGRADE_MAX_TEST_ITERS", "5")

    import auto_upgrade.config as config_module
    importlib.reload(config_module)

    assert config_module.settings.anthropic_api_key == "sk-test"
    assert config_module.settings.model == "claude-sonnet-4-6"
    assert config_module.settings.max_test_iters == 5


def test_require_api_key_raises_when_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    import auto_upgrade.config as config_module
    importlib.reload(config_module)

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        config_module.settings.require_api_key()


def test_require_api_key_returns_value_when_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-xyz")

    import auto_upgrade.config as config_module
    importlib.reload(config_module)

    assert config_module.settings.require_api_key() == "sk-xyz"
