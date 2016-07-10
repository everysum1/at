import datetime
import time
import unittest

from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.broker import MarketOrder
from trading.broker.oanda import OandaBroker
from trading.constants.order import ORDER_MARKET, SIDE_SELL
from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.live.live_runner import LiveTradingStrategyRunner
from trading.live.exceptions import LiveTradingException


class StrategyRunnerTests(unittest.TestCase):
    def setUp(self):
        instrument = INSTRUMENT_EUR_USD
        broker = OandaBroker(instrument)

        base_pair = {'currency': 'usd'}
        quote_pair = {'currency': 'eur'}

        config = {
            'strategy_name': Josh.name,
            'instrument': instrument,
            'base_pair': base_pair,
            'quote_pair': quote_pair
        }

        self.runner = LiveTradingStrategyRunner(config, broker)

    def test_remove_recorded_orders(self):
        self.runner.orders = {
            '1': {},
            '2': {},
            '3': {}
        }

        order_responses = {'1': {}, '2': {}, '4': {}}

        with self.assertRaises(KeyError):
            self.runner.remove_recorded_orders(order_responses)

        self.runner.orders = {
            '1': {},
            '2': {},
            '3': {}
        }

        order_responses = {'1': {}}
        self.runner.remove_recorded_orders(order_responses)

        self.assertEqual(self.runner.orders, {'2': {}, '3': {}})

    def test_make_trading_session_info(self):
        end_time = time.time()
        start_time = self.runner.start_time
        shutdown_cause = 'TEST_MAKE_TRADING_SESSION_INFO'

        session = self.runner.make_trading_session_info(self.runner.start_time, end_time, self.runner.tick_num,
                                                        self.runner.num_orders, shutdown_cause)

        self.assertEqual(session['ended_at'], end_time)
        self.assertEqual(session['started_at'], start_time)
        self.assertEqual(session['profit'], 0)
        self.assertEqual(session['num_orders'], 0)
        self.assertEqual(session['shutdown_cause'], shutdown_cause)
        self.assertEqual(session['num_ticks'], 0)

    def test_log_market_order(self):
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"
        units = 1000
        price = 0.982

        instrument = INSTRUMENT_EUR_USD
        side = SIDE_SELL
        order_type = ORDER_MARKET

        market_order = MarketOrder(instrument, units, side, order_type, price, trade_expire)
        self.runner.log_market_order(side, market_order)

    def test_make_marker_order(self):
        trade_expire = datetime.datetime.utcnow() + datetime.timedelta(days=1)
        trade_expire = trade_expire.isoformat("T") + "Z"
        units = 1000
        price = 0.982

        instrument = INSTRUMENT_EUR_USD
        side = 'error'
        order_type = ORDER_MARKET

        market_order = MarketOrder(instrument, units, side, order_type, price, trade_expire)

        with self.assertRaises(LiveTradingException):
            order_response = self.runner.make_market_order(side, market_order)

        side = SIDE_SELL

        market_order = MarketOrder(instrument, units, side, order_type, price, trade_expire)

        order_response = self.runner.make_market_order(side, market_order)

        self.assertEqual(order_response, '')  # Todo fix when can actually trade

    def test_update_order(self):
        order_response = None

        self.assertIsNone(self.runner.update_orders(order_response))

        with self.assertRaises(LiveTradingException):
            self.runner.update_orders({'trades': {}})

    def test_get_order_updates(self):
        order_updates = self.runner.get_order_updates()

        self.assertEqual(order_updates, {})


