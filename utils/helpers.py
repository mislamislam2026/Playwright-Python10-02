"""Small reusable helpers (unique data, dates, file names)."""
from __future__ import annotations

import re
import uuid
from datetime import date, datetime, timedelta


def unique_username(prefix: str = "qa") -> str:
    """A short username that will not collide between runs."""
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def future_date(days_ahead: int = 7) -> str:
    """A date in Web Tours' MM/DD/YYYY format."""
    return (date.today() + timedelta(days=days_ahead)).strftime("%m/%d/%Y")


def safe_file_name(name: str) -> str:
    """Turn a pytest node id into a file-system friendly name."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("_")
    return f"{cleaned}_{stamp}"
