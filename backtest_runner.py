"""
backtest_runner.py
Flexible strategy backtesting engine with daily or intraday data support.
"""

import pandas as pd
from typing import Any, Dict
from edgeX.analytics.backtest_analyzer import BacktestAnalyzer

class BacktestRunner:
    def __init__(
        self,
        strategy_class,
        historical_data: pd.DataFrame,
        initial_capital: float = 1_000_000.0,
        risk_manager=None,
        logger=None
    ):
        self.strategy_class = strategy_class
        self.data = historical_data
        self.capital = initial_capital
        self.risk_manager = risk_manager
        self.logger = logger
        self.trades = []
        self.equity_curve = [initial_capital]

    def run(self, params: Dict[str, Any]) -> Dict[str, Any]:
        strategy = self.strategy_class(
            "BacktestStrategy",
            params,
            broker=None,
            data_fetcher=None,
            risk_manager=self.risk_manager,
            logger=self.logger
        )
        strategy.initialize()

        for idx in range(50, len(self.data)):
            df_slice = self.data.iloc[:idx]
            signals = strategy.generate_signals(df_slice)
            if self.risk_manager:
                signals = self.risk_manager.check_signals(signals)

            for sig in signals:
                entry_price = sig["price"]
                exit_price = df_slice.iloc[-1]['close']  # naive next-bar exit
                pnl = (exit_price - entry_price) * sig["size"] if "BUY" in sig["action"] else (entry_price - exit_price) * sig["size"]
                self.capital += pnl
                self.trades.append({"date": df_slice.index[-1], "pnl": pnl, "returns": pnl/self.capital})
                self.equity_curve.append(self.capital)

        analyzer = BacktestAnalyzer(self.logger)
        summary = analyzer.summarize(pd.DataFrame(self.trades))
        summary["equity_curve"] = self.equity_curve
        return summary
