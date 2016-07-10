import os

from trading.broker.base import Broker
from trading.constants.interval import INTERVAL_FORTY_CANDLES
from trading.constants.granularity import GRANULARITY_DAY


class OandaBroker(Broker):
    name = 'Oanda'

    _account_id = None
    _oanda = None

    def __init__(self, instrument):
        super(OandaBroker, self).__init__(instrument)

    def get_account_information(self):
        account_information = self.oanda.get_account(self.account_id)
        return account_information

    def get_current_price_data(self):
        broker_response = self.oanda.get_prices(instruments=[self.instrument])
        return broker_response

    def get_historical_price_data(self, count=INTERVAL_FORTY_CANDLES, granularity=GRANULARITY_DAY):
        broker_response = self.oanda.get_history(instrument=self.instrument, count=count, granularity=granularity)
        return broker_response

    def get_order(self, order_id):
        order_information = self.oanda.get_order(self.account_id, order_id)
        return order_information

    def make_order(self, order):
        order_confirmation = self.oanda.create_order(self.account_id,
                                                     instrument=order.instrument,
                                                     units=order.units,
                                                     side=order.side,
                                                     type=order.type,
                                                     price=order.price,
                                                     expiry=order.expiry
                                                     )

        return order_confirmation

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

