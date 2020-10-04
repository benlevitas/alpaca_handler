import logging
from typing import Dict, List
from alpaca_trade_api.entity import Position
import alpaca_trade_api as alpaca

from src.config import HEADERS_LIVE_API, HEADERS_PAPER_API
from src.alpaca_data import AlpacaData

logger = logging.getLogger()


class AlpacaPortfolio:
    def __init__(self, staging: bool = True):
        if staging:
            self._alpaca_api = alpaca.REST(**HEADERS_PAPER_API)
        else:
            self._alpaca_api = alpaca.REST(**HEADERS_LIVE_API)

    @property
    def is_market_open(self) -> property:
        return AlpacaData.is_market_open

    @property
    def positions(self) -> Dict[str, Position]:
        positions_list = self._alpaca_api.list_positions()
        return {position.symbol: position for position in positions_list}

    def submit_order(self, symbol: str, amount: int, trade_type: str) -> None:
        try:
            self._alpaca_api.submit_order(symbol, amount, trade_type, 'market', 'day')
            #logger.trade(symbol, trade_type, amount)
        except Exception as exc:
            logger.debug(f"{symbol} - order submission unsuccessful - {exc}")

    def get_current_qty(self, symbols: List[str]) -> Dict[str, int]:
        quantities = {}
        for symbol in symbols:
            try:
                quantities[symbol] = self.positions[symbol].qty
            except:
                quantities[symbol] = 0
        return quantities

    def open_orders(self):
        orders = self._alpaca_api.list_orders(status='open')
        return list(map(lambda order: order.symbol, orders))

    def get_buying_power(self) -> float:
        return float(self._alpaca_api.get_account().buying_power)

    def trade(self, symbol: str, amount: int, trade_type: str):
        if 0 < self.get_buying_power():
            logger.debug(f"{symbol} - submitting order")
            self.submit_order(symbol, amount, trade_type)

    def liquidate(self, symbols: List[str]):
        for symbol in symbols:
            try:
                self._alpaca_api.close_position(symbol)
                logger.info(f"{symbol}\tSold all")
            except Exception as exc:
                pass
                #logger.exception(exc)

    def liquidate_all(self):
        self._alpaca_api.close_all_positions()
        logger.info("Sold all positions")
