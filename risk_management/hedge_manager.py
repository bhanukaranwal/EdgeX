"""
hedge_manager.py
Manages portfolio-level hedges and Greeks-based risk reduction.
"""

class HedgeManager:
    def __init__(self, logger=None):
        self.logger = logger

    def hedge_by_futures(self, net_delta, lot_size, underlying_symbol):
        threshold = lot_size * 0.9
        if abs(net_delta) > threshold:
            qty = int(abs(net_delta) / lot_size)
            action = 'SELL' if net_delta > 0 else 'BUY'
            hedge = {
                "action": action,
                "qty": qty * lot_size,
                "underlying": underlying_symbol
            }
            if self.logger:
                self.logger.info(f"Executing hedge: {hedge}")
            return hedge
        return {}
