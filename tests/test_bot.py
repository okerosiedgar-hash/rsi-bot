from datetime import datetime, timedelta

from rsi_bot.bot import RSITradingBot


def test_should_process_returns_true_after_cooldown_elapsed():
    bot = RSITradingBot(symbol="BTC/USDT")
    last_signal_time = datetime(2024, 1, 1, 12, 0, 0)
    now = last_signal_time + timedelta(minutes=10)

    assert bot.should_process(last_signal_time, now, cooldown_seconds=600)


def test_should_process_returns_false_before_cooldown_elapsed():
    bot = RSITradingBot(symbol="BTC/USDT")
    last_signal_time = datetime(2024, 1, 1, 12, 0, 0)
    now = last_signal_time + timedelta(minutes=5)

    assert not bot.should_process(last_signal_time, now, cooldown_seconds=600)
