import datetime
import os

from bson import ObjectId

from trading.broker.base import Broker
from trading.constants.interval import INTERVAL_FORTY_CANDLES
from trading.constants.granularity import GRANULARITY_DAY
from trading.backtest.account import Account


class BacktestBroker(Broker):
    name = 'Backtest_OANDA'

    _account_id = None
    _oanda = None
    _historic_data = {
        'candles': [],
        'meta_data': {}
    }

    def __init__(self, instrument, base_pair, quote_pair):
        super(BacktestBroker, self).__init__(instrument)

        self.account = Account(instrument, base_pair, quote_pair)
        self._current_tick = 0

    def get_account_information(self):
        account_information = self.get_account_info(self.account_id)
        return account_information

    def get_current_price_data(self):
        return self._get_current_price_data()

    def get_historical_price_data(self, instrument, count=INTERVAL_FORTY_CANDLES, granularity=GRANULARITY_DAY):
        starting_candle = self._current_tick
        ending_candle = self._current_tick + count

        return {
            'candles': self._historic_data['candles'][starting_candle: ending_candle],
            'instrument': self._historic_data['meta_data']['instrument'],
            'granularity': self._historic_data['meta_data']['granularity']
        }

    def _get_current_price_data(self):
        backtest_instrument = self.account.instrument
        target_candle = self._historic_data['candles'][self._current_tick]
        candle_time = target_candle['time']
        closing_asking_price = target_candle['closeAsk']

        return {
            'prices': [{'ask': closing_asking_price, 'instrument': backtest_instrument, 'time': candle_time}]
        }

    def get_backtest_price_data(self, instrument, count, granularity):
        historic_data = self.oanda.get_history(instrument=instrument, count=count, granularity=granularity)
        candles = historic_data['candles']

        self._historic_data['meta_data'] = {
            'instrument': historic_data['instrument'],
            'granularity': historic_data['granularity']
        }

        for i in range(0, count):
            self._historic_data['candles'].append(candles[i])

    def get_order(self, order_id):
        return {}

    def make_order(self, order):
        self.account.make_order(order)

        order_confirmation = {
            "instrument": order.instrument,
            "time": datetime.datetime.now(),
            "price": order.price,
            "tradeOpened": {
                "id": str(ObjectId()),
                "units": order.units,
                "side": order.side,
                "takeProfit": 0,
                "stopLoss": 0,
                "trailingStop": 0
            },
            "tradesClosed": [],
            "tradeReduced": {}
        }

        return order_confirmation

    def get_account_info(self, account_id):
        account_currency = self.account.base_pair.currency
        balance = self.account.base_pair.tradeable_units

        return {
            'accountCurrency': account_currency,
            'accountId': self.account_id,
            'openOrders': 0,
            'openTrades': 0,
            'balance': balance
        }

    @property
    def account_id(self):
        return os.environ['OANDA_ACCOUNT_ID']

    @property
    def oanda(self):
        import oandapy

        if self._oanda is None:
            self._oanda = oandapy.API(environment=os.environ['OANDA_ENV'],
                                      access_token=os.environ['OANDA_ACCESS_TOKEN'])
        return self._oanda
