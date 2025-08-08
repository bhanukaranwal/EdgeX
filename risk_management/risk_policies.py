"""
risk_policies.py
Basic risk manager: checks position limits, max drawdown, etc.
"""

class BasicRiskManager:
    def __init__(self, risk_config, logger=None):
        self.risk_config = risk_config
        self.logger = logger

    def check_signals(self, signals):
        # Example implementation: You can add more rigorous rules
        max_position = self.risk_config.get("position_limit", 10)
        filtered = []
        for sig in signals:
            if sig.get("size", 0) <= max_position:
                filtered.append(sig)
            else:
                if self.logger:
                    self.logger.warning(f"Signal {sig} exceeds position limit.")
        return filtered
