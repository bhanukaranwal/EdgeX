"""
position_sizing.py
Advanced position sizing utilities — volatility‑adjusted, fixed, or equity‑percentage based.
Provides robust size calculation to ensure consistent risk management across all strategies.
"""

from typing import Optional

class PositionSizer:
    def __init__(
        self,
        capital: float,
        risk_per_trade: float = 0.02,
        min_lot_size: int = 25,
        max_lots: int = 10,
        logger=None
    ):
        self.capital = capital
        self.risk_per_trade = risk_per_trade
        self.min_lot_size = min_lot_size
        self.max_lots = max_lots
        self.logger = logger

    def size_by_atr(self, atr_value: float, price: float) -> int:
        risk_amount = self.capital * self.risk_per_trade
        per_lot_risk = atr_value * self.min_lot_size
        lot_count = max(1, int(risk_amount / per_lot_risk))
        lot_count = min(lot_count, self.max_lots)
        qty = lot_count * self.min_lot_size
        if self.logger:
            self.logger.debug(f"[PositionSizer] ATR={atr_value}, Price={price}, Qty={qty}")
        return qty

    def fixed_size(self, desired_lots: int) -> int:
        lots = min(max(desired_lots, 1), self.max_lots)
        qty = lots * self.min_lot_size
        return qty

    def pct_of_equity(self, percent: float, price: float) -> int:
        dollar_value = self.capital * percent
        lots = max(1, int(dollar_value / (price * self.min_lot_size)))
        lots = min(lots, self.max_lots)
        return lots * self.min_lot_size
