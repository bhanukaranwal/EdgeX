"""
drawdown_manager.py
Tracks equity curve and automates trading halt on max drawdown breach.
"""

class DrawdownManager:
    def __init__(self, start_equity, max_drawdown=0.20, pause_threshold=0.15, logger=None):
        self.start_equity = start_equity
        self.max_drawdown = max_drawdown
        self.pause_threshold = pause_threshold
        self.equity_high = start_equity
        self.trading_active = True
        self.logger = logger

    def update_equity(self, current_equity):
        if current_equity > self.equity_high:
            self.equity_high = current_equity
        dd = 1 - (current_equity / self.equity_high)
        if dd >= self.max_drawdown:
            self.trading_active = False
            if self.logger:
                self.logger.critical(f"Max drawdown {dd:.2%} reached. Trading halted.")
            return "halt"
        elif dd >= self.pause_threshold:
            self.trading_active = False
            if self.logger:
                self.logger.warning(f"Pause threshold {dd:.2%} reached. Trading temporarily paused.")
            return "pause"
        else:
            self.trading_active = True
            return "active"
