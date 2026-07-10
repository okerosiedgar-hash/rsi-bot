from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import ccxt


@dataclass
class ExchangeConfig:
    name: str
    api_key: str | None = None
    api_secret: str | None = None
    sandbox: bool = True


class ExchangeClient:
    def __init__(self, config: ExchangeConfig):
        self.config = config
        self.client = getattr(ccxt, config.name.lower())({
            "apiKey": config.api_key,
            "secret": config.api_secret,
            "options": {"defaultType": "spot"},
        })
        if self.config.sandbox:
            self.client.set_sandbox_mode(True)

    def fetch_ohlcv(self, symbol: str, timeframe: str = "15m", limit: int = 100) -> list[list[Any]]:
        return self.client.fetch_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
