import time

from collections import defaultdict

from trading.constants.order import SIDE_SELL
from trading.constants.price_data import PRICE_ASK
from trading.live.exceptions import LiveTradingException, KeyboardInterruptMessage
from trading.strategy_runner.base import TradingStrategyRunner
from trading.util.transformations import normalize_current_price_data


class BacktestTradingStrategyRunner(TradingStrategyRunner):
    order_counts = defaultdict(int)

    def __init__(self, strategy_config, broker, backtest_count):
        self.backtest_count = backtest_count
        super(BacktestTradingStrategyRunner, self).__init__(strategy_config, broker)

        broker.get_backtest_price_data(self.instrument, backtest_count, self.strategy.granularity)

    def tick(self):
        while self.tick_num < self.backtest_count:
            try:
                account_information = self.broker.get_account_information()
                self.strategy.portfolio.update_account_portfolio_data(account_information)

                order_responses = self.get_order_updates()

                self.update_strategy_portfolio(order_responses)

                historical_market_data = self.broker.get_historical_price_data(count=self.strategy.data_window,
                                                                               granularity=self.strategy.granularity,
                                                                               tick=self.tick_num)

                current_market_data = self.broker.get_specified_tick_price_data(tick=self.tick_num)

                self.strategy.analyze_data({
                    'historical': historical_market_data,
                    'current': current_market_data
                })

                order_decision, market_order = self.strategy.make_decision()
                self.order_counts[order_decision] += 1
                order_response = self.make_market_order(order_decision, market_order)

                self.update_orders(order_response)

                self.tick_num += 1

            except (KeyboardInterrupt, SystemExit) as e:
                self.logger.error('Manually Stopped Live Trading', data=e)
                self.shutdown(KeyboardInterruptMessage)
                break
            except LiveTradingException as e:
                self.logger.error('Live Trading Error', data=e)
                self.shutdown(e)
                break
            except Exception as e:
                self.logger.error('Uncaught Error', data=e)
                self.shutdown(e)
                break

        self.shutdown('End Backtest')
        self.analyze_backtest()

    def shutdown(self, shutdown_cause):
        shutdown_cause = str(shutdown_cause)
        end_time = time.time()

        if self.invested:
            current_market_data = self.broker.get_current_price_data(instrument=self.instrument, tick=self.tick_num)
            asking_price = normalize_current_price_data(current_market_data, target_field=PRICE_ASK)
            sell_order = self.strategy.make_order(asking_price, order_side=SIDE_SELL)
            order_response = self.make_market_order(SIDE_SELL, sell_order)
            self.update_orders(order_response)

        serialized_strategy = self.strategy.serialize()
        strategy_id = self.strategy.strategy_id
        session = self.make_trading_session_info(self.start_time, end_time, self.tick_num, self.num_orders,
                                                 shutdown_cause)

        query = {'_id': strategy_id}
        update = {'$set': {'strategy_data': serialized_strategy}, '$push': {'sessions': session}}
        self.db.strategies.update(query, update, upsert=True)

    def analyze_backtest(self):
        self.logger.info('Trading Results: Account {account}'.format(account=self.broker.account))
        self.logger.info('Trading Results: Portfolio {portfolio}'.format(portfolio=self.strategy.portfolio))
        self.logger.info('Trading Results: Num Orders {num_orders}'.format(num_orders=self.num_orders))
        self.logger.info('Trading Results: Order Counts {order_counts}'.format(order_counts=self.order_counts))




