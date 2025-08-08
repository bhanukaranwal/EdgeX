"""
backtest_analyzer.py
Computes detailed summary from simulated trading history.
"""

import pandas as pd
from edgeX.analytics.performance_metrics import PerformanceMetrics

class BacktestAnalyzer:
    def __init__(self, logger=None):
        self.logger = logger

    def summarize(self, trades_df):
        total_pnl = trades_df['pnl'].sum()
        returns = trades_df['returns'].values
        dd = PerformanceMetrics.max_drawdown(trades_df['pnl'].cumsum())
        sharpe = PerformanceMetrics.sharpe_ratio(returns)
        sortino = PerformanceMetrics.sortino_ratio(returns)
        expectancy = PerformanceMetrics.expectancy(trades_df['pnl'].values)
        win_rate = (trades_df['pnl'] > 0).mean()
        n_trades = len(trades_df)

        summary = {
            "total_pnl": round(total_pnl, 4),
            "sharpe": round(sharpe, 4),
            "sortino": round(sortino, 4),
            "max_drawdown": round(dd, 4),
            "expectancy": round(expectancy, 4),
            "win_rate": round(win_rate, 4),
            "trade_count": n_trades
        }
        if self.logger:
            self.logger.info(f"Backtest summary: {summary}")
        return summary
