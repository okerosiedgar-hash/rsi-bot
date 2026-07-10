# RSI Bot

RSI Bot is a multi-exchange spot trading bot built in Python that executes a Buy the Dip, Sell the Rip strategy using RSI(14) on 15-minute candles.

## Features
- Strategy: buy when RSI(14) enters oversold territory and sell when it reaches overbought levels
- Risk management: Chandelier Exit using an ATR-based trailing stop
- Exchanges: Binance, Bybit, and KuCoin via ccxt
- Multi-exchange support with per-plan configuration
- Cooldown logic and persistent JSON trade history
- A lightweight backtester for historical candle data

## Installation

```bash
pip install ccxt pandas ta python-dotenv
```

## Usage

Run the bot once with a config file:

```bash
python -m rsi_bot.cli --config config.json --once
```

Run it in a loop with a polling interval:

```bash
python -m rsi_bot.cli --config config.json --interval 60
```

Set the following environment variables before running by copying the sample file:

```bash
cp env/.env.example env/.env
```

Then edit [env/.env](env/.env) with your credentials.

Optional Telegram alerts can be enabled by setting:

```bash
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

When configured, the bot will send a Telegram message for each non-hold signal.

## Testing

```bash
pytest -q
```

## Backtesting

A sample OHLCV dataset is included at [data/sample_candles.csv](data/sample_candles.csv). Run a backtest with:

```bash
python -m rsi_bot.cli --backtest data/sample_candles.csv
```