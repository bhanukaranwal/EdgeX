"""
zerodha_connector.py
Extensible broker interface for Zerodha KiteConnect.
"""

import os
import logging
from typing import Optional, Dict, Any
from kiteconnect import KiteConnect
from edgeX.utils.config_loader import load_config
from edgeX.utils.logger import get_logger

class ZerodhaConnector:
    def __init__(self, broker_config_path: str = 'config/zerodha.yaml'):
        self.logger = get_logger("ZerodhaConnector")
        self.config = load_config(broker_config_path)
        self.api_key = self.config.get('api_key')
        self.api_secret = self.config.get('api_secret', '')
        self.access_token = self.config.get('access_token', '')
        self.request_token = self.config.get('request_token', '')
        self.kite = KiteConnect(api_key=self.api_key)
        if self.access_token:
            self.kite.set_access_token(self.access_token)
            self.logger.info("Access token loaded.")
        else:
            self.logger.warning("Access token missing; login required.")

    def login(self) -> bool:
        if not self.request_token:
            self.logger.error("Request token missing. Complete Zerodha login flow.")
            return False
        try:
            data = self.kite.generate_session(self.request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            self.config['access_token'] = self.access_token
            with open('config/zerodha.yaml', 'w') as f:
                import yaml
                yaml.safe_dump(self.config, f)
            self.logger.info("Session login successful; access token stored.")
            return True
        except Exception as e:
            self.logger.error(f"Zerodha login error: {e}", exc_info=True)
            return False

    def place_order(
        self,
        exchange: str,
        tradingsymbol: str,
        txn_type: str,
        quantity: int,
        order_type: str = "MARKET",
        product: str = "MIS",
        variety: str = "regular",
        price: Optional[float] = None,
        stoploss: Optional[float] = None
    ) -> Dict[str, Any]:
        try:
            params = dict(
                exchange=exchange,
                tradingsymbol=tradingsymbol,
                transaction_type=txn_type,
                quantity=quantity,
                price=price or 0,
                order_type=order_type,
                product=product,
                variety=variety
            )
            if stoploss:
                params["stoploss"] = stoploss
            order_resp = self.kite.place_order(**params)
            self.logger.info(f"Order placed: {order_resp}")
            return order_resp
        except Exception as e:
            self.logger.error(f"Order placement failed: {e}", exc_info=True)
            return {}

    def get_positions(self) -> Dict[str, Any]:
        try:
            positions = self.kite.positions()
            self.logger.info("Positions fetched.")
            return positions
        except Exception as e:
            self.logger.error(f"Get positions failed: {e}", exc_info=True)
            return {}

    def get_orders(self) -> Any:
        try:
            orders = self.kite.orders()
            self.logger.info(f"Retrieved {len(orders)} orders today.")
            return orders
        except Exception as e:
            self.logger.error(f"Orders fetch error: {e}", exc_info=True)
            return []

    def cancel_order(self, order_id: str, variety: str = "regular") -> Dict[str, Any]:
        try:
            status = self.kite.cancel_order(variety=variety, order_id=order_id)
            self.logger.info(f"Order cancelled: {order_id}")
            return status
        except Exception as e:
            self.logger.error(f"Cancel order failed: {e}", exc_info=True)
            return {}
