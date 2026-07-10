import os
from pathlib import Path

from rsi_bot.bot import RSITradingBot


def test_bot_reads_symbols_and_exchanges_from_config(tmp_path: Path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '{"symbols": ["BTC/USDT"], "exchange_configs": [{"name": "binance", "sandbox": true}]}',
        encoding="utf-8",
    )

    os.environ["RSI_BOT_CONFIG"] = str(config_path)
    bot = RSITradingBot(config={"history_path": str(tmp_path / "history.json")})

    assert bot.symbols == ["BTC/USDT"]
    assert len(bot.exchange_clients) == 1
    assert bot.exchange_clients[0].config.name == "binance"
