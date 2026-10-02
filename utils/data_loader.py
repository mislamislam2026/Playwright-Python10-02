"""Load JSON test data from the test_data/ folder."""
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from config.settings import settings


@lru_cache(maxsize=None)
def load_json(file_name: str) -> dict[str, Any]:
    """Return the parsed contents of ``test_data/<file_name>``."""
    path = settings.test_data_dir / file_name
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def get_user(key: str) -> dict[str, str]:
    """Return one user record from users.json, e.g. ``get_user("valid")``."""
    return load_json("users.json")[key]
