"""
base_strategy.py
Abstract base class for all trading strategies.
Defines standard interfaces for:
    - signal generation
    - trade execution
    - lifecycle management
    - reporting
"""

from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self, name, params, broker, data_fetcher, risk_manager=None, logger=None):
        self.name = name
        self.params = params
        self.broker = broker
        self.data_fetcher = data_fetcher
        self.risk_manager = risk_manager
        self.logger = logger

    @abstractmethod
    def initialize(self):
        """Setup strategy state, validate params, preload data, etc."""
        pass

    @abstractmethod
    def generate_signals(self, market_data):
        """
        Generate trading signals based on market data.
        Args:
            market_data (DataFrame/dict): Latest fetched data
        Returns:
            list: Each item is {symbol, action, size, price, reason}
        """
        pass

    @abstractmethod
    def execute_trades(self, signals):
        """Place/cancel/modify orders as per given signals."""
        pass

    @abstractmethod
    def manage_positions(self):
        """Handle open positions, apply stop loss, exit logic etc."""
        pass

    def report(self):
        """Optional reporting interface."""
        return {"strategy": self.name, "params": self.params}
