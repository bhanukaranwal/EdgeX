# edgeX/strategies/bollinger_reversion.py
import pandas as pd
from typing import List, Dict
from edgeX.strategies.base_strategy import BaseStrategy

class BollingerReversionStrategy(BaseStrategy):
    def initialize(self) -> None:
        self.underlying_symbol = self.params.get("underlying_symbol", "NSE:NIFTY 50")
        self.window = self.params.get("window", 20)
        self.num_std = self.params.get("num_std", 2)
        self.lot_size = self.params.get("lot_size", 50)
        if self.logger:
            self.logger.info(f"[{self.name}] Initialized with window {self.window} and std {self.num_std}")

    def generate_signals(self, market_data: pd.DataFrame) -> List[Dict]:
        signals = []
        if market_data is None or market_data.empty or len(market_data) < self.window:
            return signals
        try:
            rolling_mean = market_data['close'].rolling(window=self.window).mean()
            rolling_std = market_data['close'].rolling(window=self.window).std()
            upper_band = rolling_mean + self.num_std * rolling_std
            lower_band = rolling_mean - self.num_std * rolling_std

            last_close = market_data['close'].iloc[-1]
            price = last_close
            strike = int(round(price / 50.0) * 50)

            if last_close > upper_band.iloc[-1]:
                # Price above upper band - buy put option expecting reversion
                symbol = f"NIFTY{strike}PE"
                signals.append({
                    "symbol": symbol,
                    "action": "BUY_PUT",
                    "size": self.lot_size,
                    "price": price,
                    "reason": "Price above upper Bollinger Band, mean reversion expected"
                })
            elif last_close < lower_band.iloc[-1]:
                # Price below lower band - buy call option expecting reversion
                symbol = f"NIFTY{strike}CE"
                signals.append({
                    "symbol": symbol,
                    "action": "BUY_CALL",
                    "size": self.lot_size,
                    "price": price,
                    "reason": "Price below lower Bollinger Band, mean reversion expected"
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
