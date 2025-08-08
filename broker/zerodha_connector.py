"""
zerodha_connector.py
Zerodha PyKiteConnect API wrapper:
- Session & access token management
- Order placement, status, and account access
"""

import os
import logging
from kiteconnect import KiteConnect, KiteTicker
from edgeX.utils.config_loader import load_config
from edgeX.utils.logger import get_logger

class ZerodhaConnector:
    """
    Handles Zerodha KiteConnect broker integration, login, and order workflow.
    """

    def __init__(self, broker_config_path='config/zerodha.yaml'):
        self.logger = get_logger(self.__class__.__name__)
        self.config = load_config(broker_config_path)
        self.api_key = self.config.get('api_key')
        self.api_secret = self.config.get('api_secret')
        self.access_token = self.config.get('access_token')  # to be refreshed daily!
        self.request_token = self.config.get('request_token')  # only needed for login

        self.kite = KiteConnect(api_key=self.api_key)
        self.session = None

        if self.access_token:
            self.kite.set_access_token(self.access_token)
            self.logger.info("Access token loaded from config.")
        else:
            self.logger.warning("No access token found, login required!")

    def login(self):
        """
        Authenticate and get new access token.
        User must get request_token manually (via Zerodha login flow).
        """
        if not self.request_token:
            self.logger.error("Request token missing! Please complete Zerodha login flow to get it.")
            return False

        try:
            data = self.kite.generate_session(self.request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            self.logger.info(f"Login successful, new access token acquired: {self.access_token}")
            # Optionally, update config
            self.config['access_token'] = self.access_token
            # Persist new token
            self._store_token(self.access_token)
            return True
        except Exception as e:
            self.logger.error(f"Login error: {e}", exc_info=True)
            return False

    def _store_token(self, token):
        """
        Persist access token to config file.
        """
        self.config['access_token'] = token
        with open('config/zerodha.yaml', 'w') as f:
            import yaml
            yaml.safe_dump(self.config, f)
        self.logger.info("Access token updated in config/zerodha.yaml.")

    def get_profile(self):
        """
        Fetch Zerodha account profile info.
        """
        try:
            profile = self.kite.profile()
            self.logger.info(f"Retrieved user profile: {profile.get('user_name', 'unknown')}")
            return profile
        except Exception as e:
            self.logger.error(f"Could not fetch profile: {e}", exc_info=True)
            return None

    def get_orders(self):
        """
        Retrieve all orders placed today.
        """
        try:
            orders = self.kite.orders()
            self.logger.info(f"Fetched {len(orders)} orders.")
            return orders
        except Exception as e:
            self.logger.error(f"Order fetch error: {e}", exc_info=True)
            return []

    def place_order(self, exchange, tradingsymbol, txn_type, quantity, order_type="MARKET", product="MIS", variety="regular", price=None, stoploss=None):
        """
        Place new market/limit order
        Args:
            exchange (str): "NSE"
            tradingsymbol (str): e.g., "NIFTY24AUG17500CE"
            txn_type (str): "BUY" or "SELL"
            quantity (int)
            order_type (str): "MARKET", "LIMIT", etc.
            product (str): "MIS" (intraday), "NRML" (overnight)
            variety (str): "regular"
            price (float): Required for limit order
            stoploss (float): for SL order (optional)
        Returns:
            dict: Order info
        """
        try:
            order = self.kite.place_order(
                exchange=exchange,
                tradingsymbol=tradingsymbol,
                transaction_type=txn_type,
                quantity=quantity,
                variety=variety,
                order_type=order_type,
                product=product,
                price=price or 0,
                stoploss=stoploss or 0
            )
            self.logger.info(f"Order placed: {order}")
            return order
        except Exception as e:
            self.logger.error(f"Order placement error: {e}", exc_info=True)
            return {}

    def get_positions(self):
        """
        Fetch all open positions.
        """
        try:
            positions = self.kite.positions()
            self.logger.info("Positions fetched.")
            return positions
        except Exception as e:
            self.logger.error(f"Position fetch error: {e}", exc_info=True)
            return {}

    def cancel_order(self, order_id, variety="regular"):
        try:
            status = self.kite.cancel_order(variety=variety, order_id=order_id)
            self.logger.info(f"Order cancelled: {order_id}")
            return status
        except Exception as e:
            self.logger.error(f"Order cancel error: {e}", exc_info=True)
            return {}

    # Additional methods for SR, order modify, etc. can be added here.

