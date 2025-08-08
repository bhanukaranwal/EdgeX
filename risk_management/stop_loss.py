"""
stop_loss.py
Implements fixed, trailing, and dynamic stop loss algorithms.
"""

from typing import Optional

class StopLossManager:
    def __init__(
        self,
        mode: str = 'fixed',
        fixed_pct: float = 2.5,
        trail_pct: float = 2.0,
        logger=None
    ):
        self.mode = mode
        self.fixed_pct = fixed_pct
        self.trail_pct = trail_pct
        self.logger = logger

    def stop_loss_price(
        self,
        entry_price: float,
        current_price: Optional[float] = None,
        highest_price: Optional[float] = None,
        indicator: Optional[float] = None
    ) -> float:
        if self.mode == 'fixed':
            stop = entry_price * (1 - self.fixed_pct / 100)
        elif self.mode == 'trailing':
            if highest_price is None:
                raise ValueError("Trailing mode requires highest_price")
            stop = highest_price * (1 - self.trail_pct / 100)
        elif self.mode == 'dynamic':
            if indicator is None:
                raise ValueError("Dynamic mode requires indicator value")
            stop = indicator
        else:
            raise ValueError(f"Unknown stop loss mode: {self.mode}")

        if self.logger:
            self.logger.debug(f"[StopLossManager] Computed stop: {stop}")
        return round(stop, 2)
