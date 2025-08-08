"""
supertrend_adx.py
Options strategy based on Supertrend and ADX trend confirmation.
Entry/Exit logic:
    - Go long call if price above supertrend and ADX > threshold
    - Go long put if price below supertrend and ADX > threshold
    - Exit if opposite signal or stop loss hit
"""

import pandas as pd
from edgeX.strategies.base_strategy import BaseStrategy
from edgeX.strategies.strategy_utils import calc_supertrend, calc_adx

class SupertrendADXStrategy(BaseStrategy):
    def initialize(self):
        self.underlying_symbol = self.params.get("underlying_symbol", "NSE:NIFTY 50")
        self.adx_threshold = self.params.get("adx_threshold", 25)
        self.lot_size = self.params.get("lot_size", 50)
        if self.logger:
            self.logger.info(f"{self.name} initialized for {self.underlying_symbol}")

    def generate_signals(self, market_data):
        # market_data: DataFrame of OHLCV
        df = market_data.copy()
        df = calc_supertrend(df)
        df = calc_adx(df)
        signals = []
        # check last row (latest candle)
        last = df.iloc[-1]
        if (last['in_uptrend'] and last['ADX'] > self.adx_threshold):
            # Signal: Buy call option
            signals.append({
                "symbol": self.underlying_symbol,
                "action": "BUY_CALL",
                "size": self.lot_size,
                "price": last['close'],
                "reason": "Supertrend & ADX positive"
            })
        elif (not last['in_uptrend'] and last['ADX'] > self.adx_threshold):
            # Signal: Buy put option
            signals.append({
                "symbol": self.underlying_symbol,
                "action": "BUY_PUT",
                "size": self.lot_size,
                "price": last['close'],
                "reason": "Supertrend Down & ADX positive"
            })
        return signals

    def execute_trades(self, signals):
        for sig in signals:
            if self.logger:
                self.logger.info(f"Executing trade: {sig}")
            # Select ATM option based on signal type
            # Example: Get current price, round to nearest 50 for strike
            price = sig["price"]
            strike = int(round(price / 50.0) * 50)
            if sig["action"] == "BUY_CALL":
                option_symbol = f"NIFTY{strike}CE"  # For simplicity, assuming monthly expiry
            elif sig["action"] == "BUY_PUT":
                option_symbol = f"NIFTY{strike}PE"
            else:
                continue
            # Place order via broker connector
            self.broker.place_order(
                exchange='NSE',
                tradingsymbol=option_symbol,
                txn_type='BUY',
                quantity=sig["size"],
                order_type='MARKET',
                product='MIS'
            )

    def manage_positions(self):
        # In real bot, add stop loss, dynamic exits/trailing, etc.
        pass
