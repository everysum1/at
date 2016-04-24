import datetime
import math

from bson import ObjectId
from decimal import Decimal

from trading.algorithms.base import Strategy
from trading.broker import MarketOrder, ORDER_MARKET, SIDE_BUY, SIDE_SELL, SIDE_STAY, PRICE_ASK_CLOSE
from trading.data.transformations import normalize_price_data
from trading.indicators import INTERVAL_TEN_DAYS, INTERVAL_TWENTY_DAYS
from trading.indicators.overlap_studies import calc_moving_average


class MAC(Strategy):
    name = 'Moving Average Crossover'

    crossover_threshold = 0.005

    def __init__(self, config):
        strategy_id = config.get('strategy_id')

        if strategy_id is None:
            strategy_id = ObjectId()
        else:
            config = self.load_strategy(strategy_id)

        super(MAC, self).__init__(config)
        self.strategy_id = strategy_id
        self.invested = False

    def calc_units_to_buy(self, current_price):
        pair_a_tradeable = self.portfolio.pair_a.tradeable_currency
        num_units = math.floor(pair_a_tradeable / current_price)
        return int(num_units)

    def calc_units_to_sell(self, current_price):
        pair_b_tradeable = self.portfolio.pair_b.tradeable_currency
        return pair_b_tradeable

    def allocate_tradeable_amount(self):
        pair_a = self.portfolio.pair_a
        profit = self.portfolio.profit
        if profit > 0:
            pair_a['tradeable_currency'] = pair_a['initial_currency']

    def analyze_data(self, market_data):
        closing_market_data = normalize_price_data(market_data, PRICE_ASK_CLOSE)

        # Construct the upper and lower Bollinger Bands
        short_ma = Decimal(calc_moving_average(closing_market_data, INTERVAL_TEN_DAYS))
        long_ma = Decimal(calc_moving_average(closing_market_data, INTERVAL_TWENTY_DAYS))

        self.strategy_data['asking_price'] = closing_market_data[-1]
        self.strategy_data['short_term_ma'] = short_ma
        self.strategy_data['long_term_ma'] = long_ma

        self.log_strategy_data()

    def make_decision(self):
        asking_price = self.strategy_data['asking_price']
        short_term = self.strategy_data['short_term_ma']
        long_term = self.strategy_data['long_term_ma']

        decision = SIDE_STAY
        order = None

        try:
            diff = 100 * (short_term - long_term) / ((short_term + long_term) / 2)
        except Exception as e:
            return decision, order


        if diff >= self.crossover_threshold and not self.invested:
            decision = SIDE_BUY
            order = self.make_order(asking_price, decision)

        elif diff <= - self.crossover_threshold and self.invested:
            decision = SIDE_SELL
            order = self.make_order(asking_price, decision)

        return decision, order

    def make_order(self, asking_price, order_side=SIDE_BUY):
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"

        if order_side == SIDE_BUY:
            units = self.calc_units_to_buy(asking_price)
        else:
            units = self.calc_units_to_sell(asking_price)

        instrument = self.portfolio.instrument
        side = order_side
        order_type = ORDER_MARKET
        price = asking_price
        expiry = trade_expire

        return MarketOrder(instrument, units, side, order_type, price, expiry)

    def shutdown(self, started_at, ended_at, num_ticks, num_orders, shutdown_cause):
        session_info = self.make_trading_session_info(started_at, ended_at, num_ticks, num_orders, shutdown_cause)

        pair_a = self.portfolio.pair_a
        pair_b = self.portfolio.pair_b

        config = {
            'instrument': self.portfolio.instrument,
            'pair_a': {'name': pair_a.name, 'starting_currency': pair_a.starting_currency,
                       'tradeable_currency': pair_a.tradeable_currency},
            'pair_b': {'name': pair_b.name, 'starting_currency': pair_b.starting_currency,
                       'tradeable_currency': pair_b.tradeable_currency}
        }

        strategy = {
            'config': config,
            'profit': self.portfolio.profit,
            'data_window': self.data_window,
            'interval': self.interval,
            'indicators': self.strategy_data.keys(),
            'instrument': self.instrument,
        }

        query = {'_id': ObjectId(self.strategy_id)}
        update = {'$set': {'strategy_data': strategy}, '$push': {'sessions': session_info}}
        self.db.strategies.update(query, update, upsert=True)


