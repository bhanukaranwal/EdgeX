# edgeX/strategies/momentum_breakout.py
import pandas as pd
from typing import List, Dict
from edgeX.strategies.base_strategy import BaseStrategy

class MomentumBreakoutStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.underlying_symbol = self.params.get("underlying_symbol", "NSE:NIFTY 50")
        self.short_ma_period = self.params.get("short_ma_period", 10)
        self.long_ma_period = self.params.get("long_ma_period", 30)
        self.lot_size = self.params.get("lot_size", 50)
        if self.logger:
            self.logger.info(f"[{self.name}] Initialized with short MA {self.short_ma_period} and long MA {self.long_ma_period}")

    def generate_signals(self, market_data: pd.DataFrame) -> List[Dict]:
        signals = []
        if market_data is None or market_data.empty or len(market_data) < self.long_ma_period:
            return signals
        try:
            short_ma = market_data['close'].rolling(window=self.short_ma_period).mean()
            long_ma = market_data['close'].rolling(window=self.long_ma_period).mean()
            if short_ma.iloc[-2] < long_ma.iloc[-2] and short_ma.iloc[-1] > long_ma.iloc[-1]:
                # Bullish crossover: buy call
                price = market_data['close'].iloc[-1]
                strike = int(round(price / 50.0) * 50)
                symbol = f"NIFTY{strike}CE"
                signals.append({
                    "symbol": symbol,
                    "action": "BUY_CALL",
                    "size": self.lot_size,
                    "price": price,
                    "reason": "Momentum bullish crossover"
                })
            elif short_ma.iloc[-2] > long_ma.iloc[-2] and short_ma.iloc[-1] < long_ma.iloc[-1]:
                # Bearish crossover: buy put
                price = market_data['close'].iloc[-1]
                strike = int(round(price / 50.0) * 50)
                symbol = f"NIFTY{strike}PE"
                signals.append({
                    "symbol": symbol,
                    "action": "BUY_PUT",
                    "size": self.lot_size,
                    "price": price,
                    "reason": "Momentum bearish crossover"
                })
            if self.logger:
                self.logger.info(f"[{self.name}] Signals generated: {signals}")
            return signals
        except Exception as e:
            if self.logger:
                self.logger.error(f"[{self.name}] Error generating signals: {e}", exc_info=True)
            return []

    def execute_trades(self, signals: List[Dict]) -> None:
        if not self.broker or not signals:
            return
        for sig in signals:
            try:
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
            self.logger.debug(f"[{self.name}] Position management not implemented yet.")
