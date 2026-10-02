"""Central configuration for the Web Tours UI test framework.

Every value can be overridden with an environment variable so the same
code runs locally, in CI, or against another Web Tours host.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable ("1", "true", "yes", "on")."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    """Read an integer environment variable with a fallback."""
    value = os.getenv(name)
    return int(value) if value and value.strip().isdigit() else default


@dataclass
class Settings:
    """Run settings (CLI options in conftest.py may override them)."""

    base_url: str = os.getenv(
        "BASE_URL", "http://192.168.1.183:1080/webtours/"
    )
    browser: str = os.getenv("BROWSER", "chromium")
    headless: bool = _env_bool("HEADLESS", True)
    slow_mo: int = _env_int("SLOW_MO", 0)

    # Timeouts in milliseconds.
    default_timeout: int = _env_int("DEFAULT_TIMEOUT", 10_000)
    navigation_timeout: int = _env_int("NAVIGATION_TIMEOUT", 30_000)

    viewport: dict = field(
        default_factory=lambda: {"width": 1366, "height": 768}
    )

    reports_dir: Path = PROJECT_ROOT / "reports"
    screenshots_dir: Path = PROJECT_ROOT / "reports" / "screenshots"
    test_data_dir: Path = PROJECT_ROOT / "test_data"


settings = Settings()
