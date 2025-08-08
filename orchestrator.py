"""
orchestrator.py
EdgeX main workflow orchestration with live config reload, strategy management, and monitoring.
"""

import threading
import time
import os
import yaml
from edgeX.strategy_manager import StrategyManager
from edgeX.utils.logger import get_logger
from edgeX.broker.base_broker import get_broker

CONFIG_PATH = "config/config.yaml"

class EdgeXEngine:
    def __init__(self, config_path=CONFIG_PATH):
        self.config_path = config_path
        self.config = self.load_config(config_path)
        self.logger = get_logger("EdgeXEngine")
        self.broker = get_broker(self.config.get("broker", {}), logger=self.logger)
        self.strat_mgr = self.make_strategy_manager()
        self.running = False
        self._monitor_thread = None
        self._reload_flag = False

    def load_config(self, path):
        with open(path, "r") as f:
            return yaml.safe_load(f)
    
    def make_strategy_manager(self):
        return StrategyManager(self.config, logger=self.logger)

    def reload_config_and_strategies(self):
        self.logger.info("[Engine] Hot-reloading config and strategies.")
        self.config = self.load_config(self.config_path)
        self.strat_mgr = self.make_strategy_manager()
        self.strat_mgr.load_strategies()

    def run(self):
        self.logger.info("[Engine] Starting EdgeX...")
        self.running = True
        self.strat_mgr.load_strategies()
        self._monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self._monitor_thread.start()
        try:
            poll_interval = self.config.get("bot", {}).get("poll_interval", 60)
            while self.running:
                for strat in self.strat_mgr.strategies:
                    try:
                        market_data = strat.data_fetcher.fetch_historical(
                            instrument_token=260105,
                            from_date="2025-08-08",
                            to_date="2025-08-09",
                            interval="5minute"
                        )
                        signals = strat.generate_signals(market_data)
                        signals = self.strat_mgr.risk_manager.check_signals(signals)
                        strat.execute_trades(signals)
                        strat.manage_positions()
                    except Exception as e:
                        self.logger.error(f"[Engine] Exception in strategy loop: {e}", exc_info=True)
                time.sleep(poll_interval)
                if self._reload_flag:
                    self.reload_config_and_strategies()
                    self._reload_flag = False
        except KeyboardInterrupt:
            self.logger.info("[Engine] Keyboard interrupt—shutting down.")
            self.running = False

    def monitor_loop(self):
        while self.running:
            health = {
                "broker": self.broker.__class__.__name__,
                "strategies": [s.name for s in self.strat_mgr.strategies],
                "status": "running"
            }
            self.logger.debug(f"[Monitor] Health: {health}")
            if os.path.exists("config/.reload_trigger"):
                self.logger.info("[Monitor] Detected live config reload trigger!")
                self._reload_flag = True
                os.remove("config/.reload_trigger")
            time.sleep(10)

    def update_params(self, new_config: dict):
        with open(self.config_path, "w") as f:
            yaml.safe_dump(new_config, f)
        self._reload_flag = True
        self.logger.info("[Engine] Parameters updated for live reload.")

    def status(self):
        return {
            "status": "running" if self.running else "stopped",
            "strategies": [s.name for s in self.strat_mgr.strategies],
            "broker": self.broker.__class__.__name__,
            "last_log": self.logger.handlers[0].baseFilename if self.logger and self.logger.handlers else "N/A"
        }

if __name__ == "__main__":
    engine = EdgeXEngine()
    engine.run()
