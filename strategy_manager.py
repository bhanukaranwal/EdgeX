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
