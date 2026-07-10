from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def load_config(path: str | None = None) -> dict[str, Any]:
    config_path = Path(path or os.getenv("RSI_BOT_CONFIG", "config.json"))
    if not config_path.exists():
        return {}

    with config_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
