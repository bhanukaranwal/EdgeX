"""
market_data.py
Module for fetching, caching, and processing market data
Supports:
    - Historical data for backtesting
    - Live tick/Candlestick data for trading
"""

import datetime as dt
import pandas as pd
import os
import logging
from kiteconnect import KiteConnect

from edgeX.utils.config_loader import load_config
from edgeX.utils.logger import get_logger

class MarketDataFetcher:
    """
    Fetches historical and live market data from Zerodha (or other sources).
    Implements local caching and basic preprocessing.
    """

    def __init__(self, broker_config_path: str = "config/zerodha.yaml", cache_dir: str = "data/intraday"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

        # Load configs
        config = load_config(broker_config_path)
        self.api_key = config.get("api_key")
        self.access_token = config.get("access_token")

        # Setup KiteConnect
        self.kite = KiteConnect(api_key=self.api_key)
        if self.access_token:
            self.kite.set_access_token(self.access_token)

        self.logger = get_logger(__name__)
        self.logger.info(f"MarketDataFetcher initialized with cache dir: {self.cache_dir}")

    def fetch_historical(self, instrument_token: int, from_date: str, to_date: str, interval: str = "5minute") -> pd.DataFrame:
        """
        Fetch historical OHLC data from Zerodha API
        Args:
            instrument_token (int): Zerodha instrument token
            from_date (str): e.g. '2025-08-01'
            to_date (str): e.g. '2025-08-08'
            interval (str): 'minute', '5minute', '15minute', 'day'
        Returns:
            pd.DataFrame: OHLCV data
        """
        self.logger.info(f"Requesting historical data: token={instrument_token} from={from_date} to={to_date} interval={interval}")

        try:
            data = self.kite.historical_data(
                instrument_token,
                from_date,
                to_date,
                interval,
                continuous=False
            )
            df = pd.DataFrame(data)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                self.logger.info(f"Fetched {len(df)} rows of historical data.")
            return df
        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}", exc_info=True)
            return pd.DataFrame()

    def fetch_ltp(self, instruments: list) -> dict:
        """
        Fetch live market price (LTP) for multiple symbols
        Args:
            instruments (list): list of instrument symbols (e.g., ['NSE:NIFTY 50', 'NSE:SBIN'])
        Returns:
            dict: {symbol: {'last_price': float, 'timestamp': datetime}}
        """
        self.logger.debug(f"Fetching LTP for instruments: {instruments}")
        try:
            ltp_data = self.kite.ltp(instruments)
            self.logger.debug(f"LTP data: {ltp_data}")
            return ltp_data
        except Exception as e:
            self.logger.error(f"Error fetching LTP: {e}", exc_info=True)
            return {}

    def cache_intraday_data(self, symbol: str, df: pd.DataFrame):
        """
        Save intraday data locally for redundancy/recovery or later replay.
        """
        file_path = os.path.join(self.cache_dir, f"{symbol}_intraday.csv")
        df.to_csv(file_path)
        self.logger.info(f"Intraday data for {symbol} cached at {file_path}")

    def load_cached_intraday(self, symbol: str) -> pd.DataFrame:
        """
        Load locally cached intraday data.
        """
        file_path = os.path.join(self.cache_dir, f"{symbol}_intraday.csv")
        if os.path.exists(file_path):
            return pd.read_csv(file_path, parse_dates=['date'])
        else:
            self.logger.warning(f"No cached data found for {symbol}")
            return pd.DataFrame()

    def fetch_option_chain(self, underlying_symbol: str) -> dict:
        """
        Placeholder for NSE option chain scraping or API pull.
        Currently returns a mock dict - to be implemented.
        """
        self.logger.warning("fetch_option_chain() is not yet implemented.")
        return {}
