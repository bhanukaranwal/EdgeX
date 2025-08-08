"""
strategy_manager.py
Main orchestrator for:
    - Loading strategies
    - Fetching market data
    - Dispatching signals to broker
    - Position and risk management
Supports single or multiple concurrent strategies.
"""

import time
import threading

from edgeX.strategies.supertrend_adx import SupertrendADXStrategy
from edgeX.broker.zerodha_connector import ZerodhaConnector
from edgeX.risk_management.risk_policies import BasicRiskManager
from edgeX.data_ingestion.market_data import MarketDataFetcher

class StrategyManager:
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.broker = ZerodhaConnector(config.get("broker_config", "config/zerodha.yaml"))
        self.data_fetcher = MarketDataFetcher(config.get("broker_config", "config/zerodha.yaml"))
        self.risk_manager = BasicRiskManager(config.get("risk", {}), logger=self.logger)
        self.strategies = []
        self.running = False
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

    def load_strategies(self):
        st_params = self.config.get("strategy_params", {})
        # You can extend with multiple strategies; here only SupertrendADX
        st_strategy = SupertrendADXStrategy(
            name="SupertrendADX",
            params=st_params,
            broker=self.broker,
            data_fetcher=self.data_fetcher,
            risk_manager=self.risk_manager,
            logger=self.logger
        )
        st_strategy.initialize()
        self.strategies.append(st_strategy)
        if self.logger:
            self.logger.info("Strategies loaded.")

    def run_loop(self, poll_interval=300):
        self.running = True
        self.load_strategies()
        if self.logger:
            self.logger.info("Starting strategy manager loop.")
        while self.running:
            for strat in self.strategies:
                try:
                    # Fetch latest market data (can be from live or cache/historical for backtest)
                    md = self.data_fetcher.fetch_historical(
                        instrument_token=260105,  # Example for Nifty 50
                        from_date="2025-08-07",
                        to_date="2025-08-08",
                        interval="5minute"
                    )
                    if md.empty:
                        continue
                    signals = strat.generate_signals(md)
                    if signals:
                        # Risk check before execution
                        signals = self.risk_manager.check_signals(signals)
                        strat.execute_trades(signals)
                        strat.manage_positions()
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Error in strategy execution: {e}", exc_info=True)
            time.sleep(poll_interval)

    def stop(self):
        self.running = False
        if self.logger:
            self.logger.info("Strategy manager stopped.")
