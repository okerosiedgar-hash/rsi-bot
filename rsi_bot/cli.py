from __future__ import annotations

import argparse
import os
import time
from typing import Any

from .backtest import Backtester
from .bot import RSITradingBot
from .data_loader import load_ohlcv_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the RSI trading bot")
    parser.add_argument("--config", default=os.getenv("RSI_BOT_CONFIG", "config.json"), help="Path to the JSON config file")
    parser.add_argument("--once", action="store_true", help="Run a single cycle and exit")
    parser.add_argument("--interval", type=int, default=0, help="Seconds between each cycle when not using --once")
    parser.add_argument("--backtest", metavar="PATH", help="Run a backtest using a CSV or JSON OHLCV file")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    os.environ["RSI_BOT_CONFIG"] = args.config

    if args.backtest:
        candles = load_ohlcv_file(args.backtest)
        result = Backtester().run(candles)
        print({
            "final_equity": result.final_equity,
            "win_rate": result.win_rate,
            "trade_count": len(result.trades),
        })
        return 0

    bot = RSITradingBot(config={"history_path": "trade_history.json"})

    if args.once:
        result = bot.run_once()
        print(result)
        return 0

    while True:
        result = bot.run_once()
        print(result)
        if args.interval <= 0:
            break
        time.sleep(args.interval)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
