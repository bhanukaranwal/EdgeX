"""
base_strategy.py
Abstract base class for trading strategies.
Defines interfaces and lifecycle hooks for robust, extensible strategy development.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseStrategy(ABC):
    def __init__(
        self,
        name: str,
        params: Dict[str, Any],
        broker: Any,
        data_fetcher: Any,
        risk_manager: Optional[Any] = None,
        logger: Optional[Any] = None,
    ):
        self.name = name
        self.params = params
        self.broker = broker
        self.data_fetcher = data_fetcher
        self.risk_manager = risk_manager
        self.logger = logger

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def generate_signals(self, market_data: Any) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def execute_trades(self, signals: List[Dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def manage_positions(self) -> None:
        pass

    def report(self) -> Dict[str, Any]:
        return {
            "strategy": self.name,
            "params": self.params
        }
