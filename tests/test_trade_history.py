from pathlib import Path

from rsi_bot.trade_history import append_trade, load_trade_history


def test_trade_history_round_trip(tmp_path: Path):
    history_path = tmp_path / "history.json"

    append_trade(history_path, {"symbol": "BTC/USDT", "side": "buy", "price": 100.0})
    append_trade(history_path, {"symbol": "BTC/USDT", "side": "sell", "price": 110.0})

    trades = load_trade_history(history_path)
    assert len(trades) == 2
    assert trades[0]["side"] == "buy"
    assert trades[1]["price"] == 110.0
