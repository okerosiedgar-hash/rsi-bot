from rsi_bot.bot import RSITradingBot


def test_bot_accepts_multiple_symbols_and_exchanges():
    bot = RSITradingBot(
        symbols=["BTC/USDT", "ETH/USDT"],
        exchange_configs=[
            {"name": "binance", "sandbox": True},
            {"name": "bybit", "sandbox": True},
        ],
    )

    assert bot.symbols == ["BTC/USDT", "ETH/USDT"]
    assert len(bot.exchange_clients) == 2
    assert bot.exchange_clients[0].config.name == "binance"
    assert bot.exchange_clients[1].config.name == "bybit"
