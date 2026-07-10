from pathlib import Path

import pandas as pd

from rsi_bot.data_loader import load_ohlcv_file


def test_load_ohlcv_file_reads_csv_and_json(tmp_path: Path):
    csv_path = tmp_path / "candles.csv"
    pd.DataFrame(
        {
            "timestamp": [1, 2],
            "open": [100, 101],
            "high": [102, 103],
            "low": [99, 100],
            "close": [101, 102],
            "volume": [10, 11],
        }
    ).to_csv(csv_path, index=False)

    csv_frame = load_ohlcv_file(csv_path)
    assert {"close", "high", "low", "open", "volume", "timestamp"}.issubset(csv_frame.columns)

    json_path = tmp_path / "candles.json"
    json_path.write_text(
        '{"data": [{"timestamp": 1, "open": 100, "high": 102, "low": 99, "close": 101, "volume": 10}]}',
        encoding="utf-8",
    )

    json_frame = load_ohlcv_file(json_path)
    assert len(json_frame) == 1
