"""
risk_policies.py
Comprehensive strategy risk scanner and filter.
"""

class BasicRiskManager:
    def __init__(self, risk_config, position_limits=None, logger=None):
        self.risk_config = risk_config
        self.position_limits = position_limits or {"max_per_trade": 10, "max_total": 50}
        self.logger = logger

    def check_signals(self, signals, current_exposure=0):
        filtered = []
        for sig in signals:
            size = sig.get("size", 0)
            if size > self.position_limits["max_per_trade"]:
                if self.logger:
                    self.logger.warning(f"Signal {sig} exceeds max per trade. Skipped.")
                continue
            if size + current_exposure > self.position_limits["max_total"]:
                if self.logger:
                    self.logger.error(f"Signal {sig}: total position exceeds max. Skipped.")
                continue
            filtered.append(sig)
        return filtered
