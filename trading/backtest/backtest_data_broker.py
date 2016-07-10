import datetime

from bson import ObjectId

from trading.broker.base import Broker
from trading.constants.interval import INTERVAL_FORTY_CANDLES
from trading.constants.granularity import GRANULARITY_DAY
from trading.backtest.account import Account
from trading.constants.order import SIDE_BUY, SIDE_SELL
from trading.backtest.util import load_json_file
from trading.backtest.exceptions import BacktestBrokerException


class BacktestDataBroker(Broker):
    name = 'Backtest_Data'

    _account_id = None
    _historic_data = {
        'candles': [],
        'meta_data': {}
    }

    def __init__(self, instrument, base_pair, quote_pair, data_file):
        self.account = Account(instrument, base_pair, quote_pair)
        self.data_file = data_file

        super(BacktestDataBroker, self).__init__(instrument)

    def get_account_information(self):
        account_information = self.get_account_info()
        return account_information

    def get_specified_tick_price_data(self, tick):
        backtest_instrument = self.account.instrument
        target_candle = self._historic_data['candles'][tick]
        candle_time = target_candle['time']
        closing_asking_price = target_candle['closeAsk']

        return {
            'prices': [{'ask': closing_asking_price, 'instrument': backtest_instrument, 'time': candle_time}]
        }

    def get_historical_price_data(self, count=INTERVAL_FORTY_CANDLES, granularity=GRANULARITY_DAY, tick=0):
        starting_candle = tick
        ending_candle = tick + count

        historical_data = {
            'candles': self._historic_data['candles'][starting_candle: ending_candle],
            'instrument': self._historic_data['meta_data']['instrument'],
            'granularity': self._historic_data['meta_data']['granularity']
        }

        if len(historical_data['candles']) < count:
            raise BacktestBrokerException
        else:
            return historical_data

    def get_current_price_data(self):
        raise NotImplementedError

    def get_backtest_price_data(self, count, granularity):
        historic_data = load_json_file(self.data_file)
        candles = historic_data['candles']

        self._historic_data['meta_data'] = {
            'instrument': self.instrument,
            'granularity': granularity
        }

        print('Fetched Backtest Data, TARGET COUNT:', count, 'FOUND CANDLES:', len(candles))
        for i in range(0, min(count, len(candles))):
            self._historic_data['candles'].append(candles[i])

    def get_order(self, order_id):
        return {}

    def make_order(self, order):
        self.account.make_order(order)

        side = order.side

        trades_opened = []
        trades_closed = []

        trade_data = {
                "id": str(ObjectId()),
                "units": order.units,
                "side": order.side,
                "takeProfit": 0,
                "stopLoss": 0,
                "trailingStop": 0
            }

        if side == SIDE_BUY:
            trades_opened.append(trade_data)

        elif side == SIDE_SELL:
            trades_closed.append(trade_data)

        order_confirmation = {
            "instrument": order.instrument,
            "time": datetime.datetime.now(),
            "price": order.price,
            "tradeOpened": trades_opened,
            "tradesClosed": trades_closed,
            "tradeReduced": {}
        }

        return order_confirmation

    def get_account_info(self):
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
        if self._account_id is None:
            self._account_id = str(ObjectId())
        return self._account_id


