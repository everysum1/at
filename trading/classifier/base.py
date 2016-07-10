from abc import abstractmethod, ABCMeta
from collections import namedtuple

from trading.constants.order import SIDE_BUY, SIDE_SELL, SIDE_STAY
from trading.db import get_database
from trading.util.log import Logger


MarketPrediction = namedtuple('MarketPrediction', 'decision')


predictions_map = {
    0: SIDE_STAY,
    1: SIDE_BUY,
    2: SIDE_SELL
}


class Classifier:
    __metaclass__ = ABCMeta

    _db = None
    _logger = None

    def __init__(self, config):
        self.config = config

    def passes_filter(self, decision):
        return True

    @abstractmethod
    def load(self, serialized_classifier):
        raise NotImplementedError

    @abstractmethod
    def serialize(self):
        raise NotImplementedError

    def prepare_training_data(self, strategy_data):
        X = []
        y = []

        features = strategy_data[0].keys()
        self.logger.info('Training: Classifier features {features}'.format(features=features))

        for tick in strategy_data:
            tick_data = strategy_data[tick]

            data = []
            for feature in features:

                if feature == 'decision':
                    y.append(tick_data[feature])
                else:
                    data.append(tick_data[feature])

            X.append(data)

        return X, y

    def prepare_prediction_data(self, strategy_data):
        X = []

        features = strategy_data[0].keys()
        self.logger.info('Predicting: Classifier features {features}'.format(features=features))

        for tick in strategy_data:
            tick_data = strategy_data[tick]

            data = []
            for feature in features:

                if feature == 'decision':
                    continue
                else:
                    data.append(tick_data[feature])

            X.append(data)

        return X

    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db

    @property
    def logger(self):
        if self._logger is None:
            self._logger = Logger()
        return self._logger
