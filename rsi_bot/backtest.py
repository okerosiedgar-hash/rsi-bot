from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from .strategy import analyze_candles, build_signal, build_trade_plan


@dataclass
class BacktestResult:
    trades: list[dict[str, Any]]
    equity_curve: list[float]
    final_equity: float
    win_rate: float

    @property
    def trade_count(self) -> int:
        return len(self.trades)


class Backtester:
    def __init__(self, initial_balance: float = 1000.0) -> None:
        self.initial_balance = initial_balance

    def run(self, candles: pd.DataFrame) -> BacktestResult:
        features = analyze_candles(candles)
        trades: list[dict[str, Any]] = []
        balance = self.initial_balance
        position: dict[str, Any] | None = None

        for index in range(1, len(features)):
            plan = build_trade_plan(features.iloc[: index + 1])
            signal = plan["signal"]
            close_price = float(features.iloc[index]["close"])

            if signal == "buy" and position is None:
                position = {
                    "entry_price": close_price,
                    "entry_index": index,
                    "stop_loss": float(plan["stop_loss"]),
                    "use_chandelier_stop": bool(plan["use_chandelier_stop"]),
                }
            elif position is not None:
                if position["use_chandelier_stop"] and position["stop_loss"] is not None:
                    trailing_stop = max(position["stop_loss"], float(plan["stop_loss"]))
                    if close_price <= trailing_stop:
                        pnl = (close_price - position["entry_price"]) / position["entry_price"]
                        balance *= 1 + pnl
                        trades.append({
                            "entry_index": position["entry_index"],
                            "exit_index": index,
                            "entry_price": position["entry_price"],
                            "exit_price": close_price,
                            "pnl": pnl,
                            "stop_loss": trailing_stop,
                            "use_chandelier_stop": position["use_chandelier_stop"],
                            "exit_reason": "stop_loss",
                        })
                        position = None
                    else:
                        position["stop_loss"] = trailing_stop
                elif position["stop_loss"] is not None and close_price <= position["stop_loss"]:
                    pnl = (close_price - position["entry_price"]) / position["entry_price"]
                    balance *= 1 + pnl
                    trades.append({
                        "entry_index": position["entry_index"],
                        "exit_index": index,
                        "entry_price": position["entry_price"],
                        "exit_price": close_price,
                        "pnl": pnl,
                        "stop_loss": position["stop_loss"],
                        "use_chandelier_stop": position["use_chandelier_stop"],
                        "exit_reason": "stop_loss",
                    })
                    position = None
                elif signal == "sell":
                    pnl = (close_price - position["entry_price"]) / position["entry_price"]
                    balance *= 1 + pnl
                    trades.append({
                        "entry_index": position["entry_index"],
                        "exit_index": index,
                        "entry_price": position["entry_price"],
                        "exit_price": close_price,
                        "pnl": pnl,
                        "stop_loss": position["stop_loss"],
                        "use_chandelier_stop": position["use_chandelier_stop"],
                        "exit_reason": "signal",
                    })
                    position = None

        final_equity = balance
        if trades:
            wins = sum(1 for trade in trades if trade["pnl"] > 0)
            win_rate = wins / len(trades)
        else:
            win_rate = 0.0

        return BacktestResult(
            trades=trades,
            equity_curve=[self.initial_balance * (1 + sum(trade["pnl"] for trade in trades[:i])) for i in range(1, len(trades) + 1)],
            final_equity=final_equity,
            win_rate=win_rate,
        )
