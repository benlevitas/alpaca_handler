import time
import logging
import pandas as pd
from datetime import datetime
import alpaca_trade_api as alpaca

logger = logging.getLogger()


class AlpacaData:
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

    Methods
    -------
    is_market_open()
        return 'open' or 'closed' according to current market status

    """
    def __init__(self, key: str, secret_key: str, symbols: list, time_frame: str = '1D'):
        """
        :param symbols: The list of symbols
        :param time_frame: Time frame between bars
        """
        self._symbols = list(map(lambda x: x.upper(), symbols))
        self._time_frame = time_frame  # TODO check the time_frame is valid

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
        :return: (str) 'open' or 'closed'
        """
        return self._live_api.get_clock().is_open

    def _wait_until(self, future_time: pd.Timestamp):
        now = self._live_api.get_clock().timestamp
        delta = (future_time - now).total_seconds()
        if delta > 0:
            time.sleep(delta + 1)

    def await_open(self):
        self._wait_until(self._live_api.get_clock().next_open)

    def await_close(self):
        self._wait_until(self._live_api.get_clock().next_close)

    def set_symbols(self, symbols):
        self._symbols = list(map(lambda x: x.upper(), symbols))

    def wait_for_market_status_change(self) -> bool:
        """
        Waits for market status change and then returns the new market status.
        :return: (str) 'open' or 'closed'
        """
        while True:
            if self._market_status != self.is_market_open:
                self._market_status = self.is_market_open
                logger.info(f"Market is {['open', 'closed'][self._market_status]}")
                break
            time.sleep(60)
        return self._market_status

    def get_bars(self, limit: int = 20, columns: list = None) -> pd.DataFrame:
        """
        Gets full bar sets for relevant symbols.
        :param limit: amount of days to look at (including current day)
        :param columns: relevant df columns
        :return: (dict) Full bar sets
        """
        bar_set = self._live_api.get_barset(self._symbols, self._time_frame, limit=limit)
        df = bar_set.df
        if df.index[-1].date() != datetime.now().date():
            time.sleep(10)
            bar_set = self._live_api.get_barset(self._symbols, self._time_frame, limit=limit)
            df = bar_set.df

        if columns:
            df = df.loc[:, (slice(None), columns)]
        return df
