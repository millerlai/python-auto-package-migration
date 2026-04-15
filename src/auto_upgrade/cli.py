"""Typer CLI entry point for auto-upgrade.

This module is deliberately thin during Step 1: the real graph driver loop
and HITL interactive layer are built in Step 11. For now we only wire up the
flags so ``auto-upgrade --help`` is runnable and ``cli.app`` is importable by
tests.

Uses Typer's ``@app.callback(invoke_without_command=True)`` pattern so the
CLI is a single-command tool (no ``auto-upgrade run`` subcommand required).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from auto_upgrade import __version__
from auto_upgrade.config import settings
from auto_upgrade.llm.client import SUPPORTED_MODELS, validate_model


app = typer.Typer(
    name="auto-upgrade",
    help="LangGraph-based Python package upgrade agent powered by Claude 4.6.",
    add_completion=False,
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"auto-upgrade {__version__}")
        raise typer.Exit()


def _model_callback(value: Optional[str]) -> Optional[str]:
    """Eagerly validate --model so the user sees the supported list up-front."""
    if value is None:
        return None
    try:
        return validate_model(value)
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    project_path: Optional[Path] = typer.Argument(
        None,
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Path to the Python project to upgrade.",
    ),
    package: Optional[str] = typer.Option(
        None, "--package", "-p",
        help="Package name to upgrade (mutually exclusive with --cve).",
    ),
    version: Optional[str] = typer.Option(
        None, "--version", "-V",
        help="Target version for --package (e.g. 2.32.0).",
    ),
    cve: Optional[str] = typer.Option(
        None, "--cve",
        help="CVE id to fix, e.g. CVE-2024-35195.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        callback=_model_callback,
        help=(
            "Claude model id. Supported: "
            + ", ".join(sorted(SUPPORTED_MODELS))
            + ". Default: claude-opus-4-6."
        ),
    ),
    test_command: Optional[str] = typer.Option(
        None,
        "--test-command",
        help='Custom test command, e.g. "tox -e py311" or "make test-ci".',
    ),
    test_cwd: Optional[Path] = typer.Option(
        None,
        "--test-cwd",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help=(
            "Working directory for --test-command (default: PROJECT_PATH). "
            "Monorepo example: --test-command 'tox -e api-py311' "
            "--test-cwd ~/monorepo when PROJECT_PATH is ~/monorepo/services/api."
        ),
    ),
    checkpointer: str = typer.Option(
        "memory",
        "--checkpointer",
        help="Checkpointer backend: 'memory' (default) or 'sqlite'.",
    ),
    checkpoint_db: Optional[Path] = typer.Option(
        None,
        "--checkpoint-db",
        help="SqliteSaver file path (default: ~/.auto-upgrade/checkpoints.sqlite).",
    ),
    non_interactive: bool = typer.Option(
        False, "--non-interactive",
        help="Skip optional HITL confirmations (CI/CD mode).",
    ),
    no_pr: bool = typer.Option(
        False, "--no-pr",
        help="Do not create a Pull Request (local-only mode).",
    ),
    snapshot_dir: Optional[Path] = typer.Option(
        None, "--snapshot-dir",
        help="Where to store env snapshots for rollback.",
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level",
        help="Log level: DEBUG, INFO, WARNING, ERROR.",
    ),
    show_version: Optional[bool] = typer.Option(
        None,
        "--app-version",
        callback=_version_callback,
        is_eager=True,
        help="Show the auto-upgrade version and exit.",
    ),
) -> None:
    """Run the upgrade workflow against ``PROJECT_PATH``.

    Either ``--package NAME --version VER`` or ``--cve CVE-ID`` must be given.
    """
    if ctx.invoked_subcommand is not None:
        return

    if project_path is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=2)

    # Validate mutually exclusive modes.
    if cve and (package or version):
        raise typer.BadParameter(
            "--cve cannot be combined with --package/--version."
        )
    if not cve and not (package and version):
        raise typer.BadParameter(
            "Provide either --cve CVE-ID, or both --package NAME and --version VER."
        )
    if checkpointer not in {"memory", "sqlite"}:
        raise typer.BadParameter("--checkpointer must be 'memory' or 'sqlite'.")

    # Push CLI overrides into the singleton settings so downstream modules
    # (llm.client, graph nodes, ...) see them without plumbing kwargs through.
    if model is not None:
        settings.model = model
    if checkpoint_db is not None:
        settings.checkpoint_db = checkpoint_db
    settings.log_level = log_level

    typer.echo(
        f"[auto-upgrade] project={project_path} "
        f"target={'CVE ' + cve if cve else f'{package}=={version}'} "
        f"model={settings.model} checkpointer={checkpointer} "
        f"non_interactive={non_interactive} no_pr={no_pr}"
    )
    if test_command:
        typer.echo(
            f"[auto-upgrade] test_command={test_command!r} "
            f"test_cwd={test_cwd or project_path}"
        )
    typer.echo(
        "[auto-upgrade] Graph driver is not wired up yet (Step 11). "
        "This CLI currently validates arguments and reports the parsed plan."
    )


if __name__ == "__main__":
    app()
