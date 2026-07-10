from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_trade_history(path: str | Path | None = None) -> list[dict[str, Any]]:
    history_path = Path(path or "trade_history.json")
    if not history_path.exists():
        return []

    with history_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if isinstance(data, list):
        return data
    return []


def append_trade(path: str | Path | None, trade: dict[str, Any]) -> list[dict[str, Any]]:
    history_path = Path(path or "trade_history.json")
    history = load_trade_history(history_path)
    history.append(trade)
    with history_path.open("w", encoding="utf-8") as handle:
        json.dump(history, handle, indent=2)
    return history
