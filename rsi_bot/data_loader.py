from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_ohlcv_file(path: str | Path) -> pd.DataFrame:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".csv":
        frame = pd.read_csv(file_path)
    elif suffix == ".json":
        with file_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, list):
            frame = pd.DataFrame(payload)
        elif isinstance(payload, dict) and "data" in payload:
            frame = pd.DataFrame(payload["data"])
        else:
            raise ValueError("Unsupported JSON OHLCV payload")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    expected_columns = {"close", "high", "low"}
    if not expected_columns.issubset(frame.columns):
        raise ValueError("OHLCV file must include close, high, and low columns")

    if "open" not in frame.columns:
        frame["open"] = frame["close"]
    if "volume" not in frame.columns:
        frame["volume"] = 0.0
    if "timestamp" not in frame.columns:
        frame["timestamp"] = range(len(frame))

    return frame
