from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import pandas as pd
from dotenv import load_dotenv

from .config import load_config
from .exchange import ExchangeClient, ExchangeConfig
from .strategy import build_trade_plan
from .telegram import TelegramNotifier
from .trade_history import append_trade, load_trade_history

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "env", ".env"))
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "env", ".env.example"), override=False)


class RSITradingBot:
    def __init__(
        self,
        symbol: str | None = None,
        symbols: list[str] | None = None,
        config: dict[str, Any] | None = None,
        exchange_configs: list[dict[str, Any]] | None = None,
    ) -> None:
        self.config = {
            "exchange_name": os.getenv("EXCHANGE_NAME", "binance"),
            "api_key": os.getenv("API_KEY"),
            "api_secret": os.getenv("API_SECRET"),
            "sandbox": True,
            "timeframe": "15m",
            "limit": 100,
            "cooldown_seconds": 600,
            "history_path": os.getenv("TRADE_HISTORY_PATH", "trade_history.json"),
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
            "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        }
        file_config = load_config(os.getenv("RSI_BOT_CONFIG"))
        self.config.update(file_config)
        self.config.update(config or {})

        self.symbol = symbol or "BTC/USDT"
        self.symbols = symbols or self.config.get("symbols") or [self.symbol]

        raw_exchange_configs = exchange_configs or self.config.get("exchange_configs") or [
            {
                "name": self.config["exchange_name"],
                "api_key": self.config["api_key"],
                "api_secret": self.config["api_secret"],
                "sandbox": self.config["sandbox"],
            }
        ]
        self.exchange_clients = [
            ExchangeClient(
                ExchangeConfig(
                    name=exchange_config.get("name", self.config["exchange_name"]),
                    api_key=exchange_config.get("api_key", self.config["api_key"]),
                    api_secret=exchange_config.get("api_secret", self.config["api_secret"]),
                    sandbox=exchange_config.get("sandbox", self.config["sandbox"]),
                )
            )
            for exchange_config in raw_exchange_configs
        ]
        self.notifier = TelegramNotifier(
            bot_token=self.config.get("telegram_bot_token"),
            chat_id=self.config.get("telegram_chat_id"),
        )
        self.open_positions: dict[tuple[str, str], dict[str, Any]] = {}
        self.last_signal_time: datetime | None = None

    def should_process(self, last_signal_time: datetime | None, now: datetime | None = None, cooldown_seconds: int | None = None) -> bool:
        if last_signal_time is None:
            return True
        if now is None:
            now = datetime.now(timezone.utc)
        cooldown = cooldown_seconds if cooldown_seconds is not None else self.config["cooldown_seconds"]
        return (now - last_signal_time).total_seconds() >= cooldown

    def _send_trade_alert(self, exchange_name: str, symbol: str, event: str, plan: dict[str, Any], close_price: float, stop_loss: float | None = None) -> None:
        if not self.notifier.is_configured():
            return

        reason = f"{event.upper()}"
        details = [f"{exchange_name} {symbol}", reason, f"trend={plan['trend']}", f"RSI={plan['rsi']:.1f}"]
        if stop_loss is not None:
            details.append(f"stop={stop_loss}")
        details.append(f"price={close_price}")
        self.notifier.send_message(" | ".join(details))

    def _handle_signal(self, exchange_name: str, symbol: str, plan: dict[str, Any], close_price: float) -> None:
        position_key = (exchange_name, symbol)
        position = self.open_positions.get(position_key)
        signal = plan["signal"]

        if position is None:
            if signal == "buy":
                self.open_positions[position_key] = {
                    "entry_price": close_price,
                    "stop_loss": float(plan["stop_loss"]),
                    "use_chandelier_stop": bool(plan["use_chandelier_stop"]),
                }
                self._send_trade_alert(exchange_name, symbol, "entry", plan, close_price, float(plan["stop_loss"]))
            return

        trailing_stop = float(position["stop_loss"])
        if position.get("use_chandelier_stop"):
            trailing_stop = max(trailing_stop, float(plan["stop_loss"]))
            position["stop_loss"] = trailing_stop

        if close_price <= trailing_stop:
            self._send_trade_alert(exchange_name, symbol, "stop_loss", plan, close_price, trailing_stop)
            self.open_positions.pop(position_key, None)
            return

        if signal == "sell":
            self._send_trade_alert(exchange_name, symbol, "exit", plan, close_price, trailing_stop)
            self.open_positions.pop(position_key, None)

    def run_once(self) -> dict[str, Any]:
        if not self.should_process(self.last_signal_time):
            return {"symbol": self.symbol, "signal": "hold", "skipped": True}

        trades = []
        for exchange_client in self.exchange_clients:
            for symbol in self.symbols:
                candles = exchange_client.fetch_ohlcv(symbol, timeframe=self.config["timeframe"], limit=self.config["limit"])
                frame = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
                plan = build_trade_plan(frame)
                signal = plan["signal"]

                history = load_trade_history(self.config["history_path"])
                trade = {
                    "exchange": exchange_client.config.name,
                    "symbol": symbol,
                    "signal": signal,
                    "trend": plan["trend"],
                    "stop_loss": plan["stop_loss"],
                    "use_chandelier_stop": plan["use_chandelier_stop"],
                    "history_length": len(history),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                append_trade(self.config["history_path"], trade)
                self._handle_signal(exchange_client.config.name, symbol, plan, float(frame["close"].iloc[-1]))
                trades.append(trade)

        self.last_signal_time = datetime.now(timezone.utc)
        return {"trades": trades}
