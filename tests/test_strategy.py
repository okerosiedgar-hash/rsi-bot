import pandas as pd

from rsi_bot.strategy import analyze_candles, build_signal, build_trade_plan


def test_build_signal_marks_oversold_and_overbought():
    candles = pd.DataFrame(
        {
            "close": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
            "high": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
            "low": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
        }
    )

    signal = build_signal(candles)
    assert signal == "buy"


def test_trade_plan_includes_chandelier_stop_and_trend_context():
    candles = pd.DataFrame(
        {
            "close": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
            "high": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
            "low": [100, 95, 90, 85, 80, 75, 70, 65, 60, 55],
        }
    )

    plan = build_trade_plan(candles)
    assert plan["signal"] == "buy"
    assert plan["trend"] in {"uptrend", "downtrend", "range"}
    assert plan["stop_loss"] is not None
    assert plan["use_chandelier_stop"] is True


def test_analyze_candles_returns_expected_columns():
    candles = pd.DataFrame(
        {
            "close": [100, 101, 102, 103, 102, 101, 100, 99, 98, 97],
            "high": [105, 106, 107, 108, 107, 106, 105, 104, 103, 102],
            "low": [95, 96, 97, 98, 97, 96, 95, 94, 93, 92],
        }
    )

    result = analyze_candles(candles)
    assert {"rsi", "atr", "chandelier_exit"}.issubset(result.columns)
    assert len(result) == len(candles)
