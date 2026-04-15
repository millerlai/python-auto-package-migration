"""Smoke test: ``auto-upgrade --help`` works and flags are wired up.

The full CLI behavior is tested in Step 11; here we only verify Step 1's
"the CLI is importable, --help runs, and flag validation fires" contract.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from auto_upgrade.cli import app


runner = CliRunner()


def test_help_runs_cleanly():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Help should mention the key flags the user relies on.
    for flag in [
        "--package", "--version", "--cve", "--model", "--test-command",
        "--test-cwd", "--checkpointer", "--non-interactive", "--no-pr",
    ]:
        assert flag in result.output, f"--help missing flag: {flag}"


def test_help_lists_supported_models():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for model_id in ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5"]:
        assert model_id in result.output


def test_rejects_conflicting_modes(tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    result = runner.invoke(
        app,
        [str(proj), "--package", "requests", "--version", "2.32.0",
         "--cve", "CVE-2024-00001"],
    )
    assert result.exit_code != 0
    assert "--cve cannot be combined" in result.output


def test_requires_package_or_cve(tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    result = runner.invoke(app, [str(proj)])
    assert result.exit_code != 0
    assert "Provide either --cve" in result.output


def test_rejects_unsupported_model(tmp_path: Path):
    proj = tmp_path / "proj"
    proj.mkdir()
    result = runner.invoke(
        app,
        [str(proj), "--package", "requests", "--version", "2.32.0",
         "--model", "gpt-4"],
    )
    assert result.exit_code != 0
    assert "Unsupported model" in result.output


def test_accepts_valid_plan(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    proj = tmp_path / "proj"
    proj.mkdir()
    result = runner.invoke(
        app,
        [str(proj), "--package", "requests", "--version", "2.32.0"],
    )
    assert result.exit_code == 0, result.output
    assert "requests==2.32.0" in result.output
    assert "model=claude-opus-4-6" in result.output


def test_accepts_cve_mode(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    proj = tmp_path / "proj"
    proj.mkdir()
    result = runner.invoke(
        app,
        [str(proj), "--cve", "CVE-2024-35195"],
    )
    assert result.exit_code == 0, result.output
    assert "CVE CVE-2024-35195" in result.output


def test_accepts_custom_test_command_and_cwd(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    proj = tmp_path / "mono" / "services" / "api"
    proj.mkdir(parents=True)
    test_cwd = tmp_path / "mono"
    result = runner.invoke(
        app,
        [str(proj), "--package", "requests", "--version", "2.32.0",
         "--test-command", "tox -e api-py311",
         "--test-cwd", str(test_cwd)],
    )
    assert result.exit_code == 0, result.output
    assert "tox -e api-py311" in result.output


def test_rejects_invalid_checkpointer(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    proj = tmp_path / "proj"
    proj.mkdir()
    result = runner.invoke(
        app,
        [str(proj), "--package", "requests", "--version", "2.32.0",
         "--checkpointer", "redis"],
    )
    assert result.exit_code != 0
    assert "--checkpointer" in result.output
