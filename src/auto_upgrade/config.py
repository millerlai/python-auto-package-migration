"""Runtime configuration for auto-upgrade.

All values are resolved from environment variables first; CLI flags in
``cli.py`` override these by writing directly onto ``settings`` before the
graph is built.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


DEFAULT_MODEL = "claude-opus-4-6"
DEFAULT_MAX_TEST_ITERS = 3
DEFAULT_CHECKPOINT_DB = Path.home() / ".auto-upgrade" / "checkpoints.sqlite"


@dataclass
class Settings:
    """Process-wide settings. Populated from env vars on import."""

    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    github_token: Optional[str] = field(
        default_factory=lambda: os.getenv("GITHUB_TOKEN")
    )
    model: str = field(
        default_factory=lambda: os.getenv("AUTO_UPGRADE_MODEL", DEFAULT_MODEL)
    )
    checkpoint_db: Path = field(
        default_factory=lambda: Path(
            os.getenv("AUTO_UPGRADE_CHECKPOINT_DB", str(DEFAULT_CHECKPOINT_DB))
        )
    )
    log_level: str = field(
        default_factory=lambda: os.getenv("AUTO_UPGRADE_LOG_LEVEL", "INFO")
    )
    max_test_iters: int = field(
        default_factory=lambda: int(
            os.getenv("AUTO_UPGRADE_MAX_TEST_ITERS", str(DEFAULT_MAX_TEST_ITERS))
        )
    )

    def require_api_key(self) -> str:
        """Raise a clear error if no Anthropic API key is configured."""
        if not self.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Export it or pass it via "
                "the environment before running auto-upgrade."
            )
        return self.anthropic_api_key


settings = Settings()
"""Singleton settings instance. Import and mutate attributes from CLI."""
