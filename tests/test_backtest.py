from pathlib import Path

import pandas as pd

from rsi_bot.backtest import Backtester
from rsi_bot.data_loader import load_ohlcv_file


def test_backtester_returns_trade_summary():
    candles = pd.DataFrame(
        {
            "close": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
            "high": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
            "low": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
        }
    )

    result = Backtester(initial_balance=1000.0).run(candles)
    assert result.final_equity >= 0
    assert isinstance(result.win_rate, float)
    assert len(result.trades) >= 0


def test_sample_dataset_produces_active_trades():
    sample_path = Path(__file__).resolve().parents[1] / "data" / "sample_candles.csv"
    candles = load_ohlcv_file(sample_path)

    result = Backtester(initial_balance=1000.0).run(candles)
    assert result.trade_count > 0
