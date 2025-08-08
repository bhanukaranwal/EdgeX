"""
supertrend_adx.py
Advanced implementation of Supertrend + ADX strategy for options.
"""

import pandas as pd
from typing import Any, Dict, List, Optional
from edgeX.strategies.base_strategy import BaseStrategy
from edgeX.strategies.strategy_utils import calc_supertrend, calc_adx

class SupertrendADXStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.underlying_symbol = self.params.get("underlying_symbol", "NSE:NIFTY 50")
        self.adx_threshold = self.params.get("adx_threshold", 25)
        self.lot_size = self.params.get("lot_size", 50)
        if self.logger:
            self.logger.info(f"[{self.name}] Initialized for {self.underlying_symbol} ADX>{self.adx_threshold} lot:{self.lot_size}")

    def generate_signals(self, market_data: pd.DataFrame) -> List[Dict[str, Any]]:
        if market_data is None or market_data.empty:
            if self.logger:
                self.logger.warning(f"[{self.name}] Market data empty.")
            return []
        try:
            df = calc_supertrend(market_data.copy())
            df = calc_adx(df)
            last = df.iloc[-1]
            signals = []
            reason = ""
            if "in_uptrend" in last and last['ADX'] > self.adx_threshold:
                if last['in_uptrend']:
                    option_action = "BUY_CALL"
                    reason = "Supertrend up, ADX strong"
                else:
                    option_action = "BUY_PUT"
                    reason = "Supertrend down, ADX strong"
                price = last['close']
                strike = int(round(price / 50.0) * 50)
                symbol = f"NIFTY{strike}CE" if option_action == "BUY_CALL" else f"NIFTY{strike}PE"
                signals.append({
                    "symbol": symbol,
                    "action": option_action,
                    "size": self.lot_size,
                    "price": price,
                    "reason": reason
                })
            if self.logger:
                self.logger.info(f"[{self.name}] Signals generated: {signals}")
            return signals
        except Exception as e:
            if self.logger:
                self.logger.error(f"[{self.name}] Signal generation failed: {e}", exc_info=True)
            return []

    def execute_trades(self, signals: List[Dict[str, Any]]) -> None:
        if not self.broker or signals is None:
            if self.logger:
                self.logger.error(f"[{self.name}] Broker or signals missing, cannot execute.")
            return
        for sig in signals:
            try:
                self.logger.info(f"[{self.name}] Executing trade: {sig}")
                self.broker.place_order(
                    exchange='NSE',
                    tradingsymbol=sig["symbol"],
                    txn_type='BUY',
                    quantity=sig["size"],
                    order_type='MARKET',
                    product='MIS'
                )
            except Exception as e:
                if self.logger:
                    self.logger.error(f"[{self.name}] Order execution failed: {e}", exc_info=True)

    def manage_positions(self) -> None:
        if self.logger:
            self.logger.debug(f"[{self.name}] Position management not yet implemented.")
