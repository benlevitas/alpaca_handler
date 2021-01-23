import time
import logging
import pandas as pd
from datetime import datetime, timedelta
import alpaca_trade_api as alpaca
from alpaca_handler.enums import Timespans

logger = logging.getLogger()


class Data:
    """
    A class for handling Alpaca API

    ...

    Attributes
    ----------
    _symbols : list
        A list of symbols that the handler will be working with
    _time_frame : str
        The time frame between bars collected from Alpaca API (should be a valid time frame that Alpaca can handler
    _live_api : REST
        The Alpaca REST API
    _market_status : str
        An indicator of the market status as of last time checked
    is_market_open : bool
        True/False according to current market status

    Methods
    -------
    await_open()
        wait for open market hours
    await_close()
        wait for market close
    set_symbols()
        set symbols after initialization
    wait_for_market_status_change()
        wait for market status change: open->close or close->open
    get_bars()
        get bars for relevant symbols
    """
    def __init__(self, key: str, secret_key: str, symbols: list, time_frame: str = '1D'):
        """
        :param key: Alpaca API key
        :param secret_key: Alpaca API secret key
        :param symbols: List of symbols
        :param time_frame: Time frame between bars
        """
        self._symbols = list(map(lambda x: x.upper(), symbols))
        self._time_frame = Timespans(time_frame).name  # TODO check the time_frame is valid

        headers = {
            'key_id': key,
            'secret_key': secret_key,
            'base_url': 'https://api.alpaca.markets',
            'api_version': 'v2'
        }
        self._live_api = alpaca.REST(**headers)
        self._market_status = self.is_market_open

    @property
    def is_market_open(self) -> bool:
        """
        Returns current market status.
        :return: Boolean
        """
        return self._live_api.get_clock().is_open

    def _wait_until(self, future_time: pd.Timestamp):
        """
        Sleep until the given time
        :param future_time: given time
        """
        now = self._live_api.get_clock().timestamp
        delta = (future_time - now).total_seconds()
        if delta > 0:
            time.sleep(delta + 1)

    def await_open(self):
        """Awaits open market"""
        self._wait_until(self._live_api.get_clock().next_open)

    def await_close(self):
        """Awaits closed market"""
        self._wait_until(self._live_api.get_clock().next_close)

    def set_symbols(self, symbols):
        """
        Sets symbols after initialization
        :param symbols:
        """
        self._symbols = list(map(lambda x: x.upper(), symbols))

    def wait_for_market_status_change(self) -> bool:
        """
        Waits for market status change.
        :return: market status: open -> True, closed -> False
        """
        while True:
            if self._market_status != self.is_market_open:
                self._market_status = self.is_market_open
                logger.info(f"Market is {['open', 'closed'][self._market_status]}")
                break
            time.sleep(60)
        return self._market_status

    def _get_start_date(self, limit: int, start=None):
        """
        Deduct start date needed to reach ${limit} amount of days
        :param limit: desired amount of days
        :param start: estimate start date - may lower complexity
        :return: start date
        """
        present = datetime.now().date()
        if not start:
            start = present - timedelta(limit)
        market_days = len(self._live_api.get_calendar(str(start), str(present)))
        if limit > market_days:
            start = self._get_start_date(limit, start - timedelta(limit - market_days))
        return start

    def get_bars(self, limit: int = 20, columns: list = None) -> dict:
        """
        Gets full bar sets for self's symbols.
        :param limit: amount of days to pull (includes today)
        :param columns: relevant df columns
        :return: Full bar sets
        """
        present = datetime.now().date()
        start = self._get_start_date(limit)
        bars = {}
        for symbol in self._symbols:
            bar_set = self._live_api.polygon.historic_agg_v2(symbol, 1, self._time_frame, start, present).df
            if columns:
                bar_set = bar_set.loc[:, columns]
            bars[symbol] = bar_set
        return bars
