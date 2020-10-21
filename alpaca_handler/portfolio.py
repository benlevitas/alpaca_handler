import logging
from typing import Dict, List
from alpaca_trade_api.entity import Position
import alpaca_trade_api as alpaca

from alpaca_handler.data import Data

logger = logging.getLogger()


class Portfolio:
    """
    A class for handling Alpaca portfolio trades and orders

    ...

    Attributes
    ----------
    _alpaca_api : alpaca.REST
        Alpaca API connnection
    is_market_open: bool
        return True/False according to current market status
    positions: Dict[str, Position]
        return order positions

    Methods
    -------
    get_current_qty()
        Get stock holding quantities
    open_orders()
        Get stock list with open orders
    get_buying_power()
        Get available buying power
    trade()
        Stock buy or sell
    liquidate()
        Liquidate stock holdings
    liquidate_all()
        Liquidate all stock holdings
    """
    def __init__(self, key: str, secret_key: str, staging: bool = True):
        """
        :param key: Alpaca API key
        :param secret_key: Alpaca API secret key
        :param staging: True for paper trading, False for live trading
        """
        headers = {
            'key_id': key,
            'secret_key': secret_key,
            'api_version': 'v2'
        }
        if not staging:
            headers['base_url'] = 'https://api.alpaca.markets'
        else:
            headers['base_url'] = 'https://paper-api.alpaca.markets'
        self._alpaca_api = alpaca.REST(**headers)

    @property
    def is_market_open(self) -> property:
        """
        Returns current market status.
        :return: Boolean
        """
        return Data.is_market_open

    @property
    def positions(self) -> Dict[str, Position]:
        """
        :return: Dict(symbol: positions)
        """
        positions_list = self._alpaca_api.list_positions()
        return {position.symbol: position for position in positions_list}

    def _submit_order(self, symbol: str, amount: int, trade_type: str) -> None:
        """
        Submits stock buy/sell
        :param symbol: Stock symbol
        :param amount: Buy quantity
        :param trade_type: 'buy'/'sell'
        """
        try:
            self._alpaca_api.submit_order(symbol, amount, trade_type, 'market', 'day')
            #logger.trade(symbol, trade_type, amount)
        except Exception as exc:
            logger.debug(f"{symbol} - order submission unsuccessful - {exc}")

    def get_current_qty(self, symbols: List[str]) -> Dict[str, int]:
        """
        Get stock holding quantities
        :param symbols: Stock symbols
        :return: Dict(symbol: quantity)
        """
        quantities = {}
        for symbol in symbols:
            try:
                quantities[symbol] = self.positions[symbol].qty
            except:
                quantities[symbol] = 0
        return quantities

    def open_orders(self) -> list:
        """:return: symbols that have open orders"""
        orders = self._alpaca_api.list_orders(status='open')
        return list(map(lambda order: order.symbol, orders))

    def get_buying_power(self) -> float:
        """:return: Available buying power"""
        return float(self._alpaca_api.get_account().buying_power)

    def trade(self, symbol: str, amount: int, trade_type: str):
        """
        Stock buy/sell
        :param symbol: Stock symbol
        :param amount: buy/sell quantity
        :param trade_type: 'buy' or 'sell'
        """
        if 0 < self.get_buying_power():
            logger.debug(f"{symbol} - submitting order")
            self._submit_order(symbol, amount, trade_type)

    def liquidate(self, symbols: List[str]):
        """
        Liquidate stock holdings
        :param symbols: Stock symbols
        """
        for symbol in symbols:
            try:
                self._alpaca_api.close_position(symbol)
                logger.info(f"{symbol}\tSold all")
            except Exception as exc:
                pass
                #logger.exception(exc)

    def liquidate_all(self):
        """Liquidate all stock holdings"""
        self._alpaca_api.close_all_positions()
        logger.info("Sold all positions")
