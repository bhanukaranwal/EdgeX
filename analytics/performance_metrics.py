"""
performance_metrics.py
Comprehensive performance metrics library for strategy evaluation.
"""

import numpy as np
from typing import List

class PerformanceMetrics:
    @staticmethod
    def sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        excess = np.array(returns) - risk_free_rate
        if len(excess) < 2 or np.std(excess) == 0:
            return np.nan
        return (np.mean(excess) / np.std(excess)) * np.sqrt(252)

    @staticmethod
    def sortino_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        excess = np.array(returns) - risk_free_rate
        downside = excess[excess < 0]
        if len(downside) == 0:
            return np.nan
        return (np.mean(excess) / np.std(downside)) * np.sqrt(252)

    @staticmethod
    def max_drawdown(equity_curve: List[float]) -> float:
        high = np.maximum.accumulate(equity_curve)
        drawdowns = (high - equity_curve) / high
        return float(np.max(drawdowns))

    @staticmethod
    def expectancy(trades: List[float]) -> float:
        if not trades:
            return 0.0
        wins = [t for t in trades if t > 0]
        losses = [t for t in trades if t < 0]
        win_rate = len(wins) / len(trades)
        avg_win = np.mean(wins) if wins else 0
        avg_loss = abs(np.mean(losses)) if losses else 0
        return (avg_win * win_rate) - (avg_loss * (1 - win_rate))
