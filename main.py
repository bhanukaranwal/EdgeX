"""
main.py
Bot entrypoint. Loads config, initializes logger, and starts the strategy loop.
"""

from edgeX.strategy_manager import StrategyManager
from edgeX.utils.config_loader import load_config
from edgeX.utils.logger import get_logger

def main():
    config = load_config("config/config.yaml")
    logger = get_logger("EdgeX")
    logger.info("EdgeX Automated Options Trading Bot Starting")
    sm = StrategyManager(config, logger=logger)
    try:
        sm.run_loop(poll_interval=config.get("bot", {}).get("poll_interval", 300))
    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt—stopping strategy manager.")
        sm.stop()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sm.stop()

if __name__ == "__main__":
    main()
