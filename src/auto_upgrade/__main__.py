"""Allow ``python -m auto_upgrade`` to invoke the Typer CLI."""

from auto_upgrade.cli import app


if __name__ == "__main__":
    app()
