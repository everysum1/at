import numpy as np
import talib

from trading.indicators.exceptions import TalibIntervalException


def calc_average_true_range(close, high, low, interval):
    required_interval = interval + 1

    if len(high) < required_interval or len(low) < required_interval or len(close) < required_interval:
        raise TalibIntervalException

    high = high[-required_interval:]
    low = low[-required_interval:]
    close = close[-required_interval:]

    high = np.asarray(high)
    low = np.asarray(low)
    close = np.asarray(close)

    atr = talib.ATR(high, low, close, timeperiod=interval)
    return atr[-1]


def calc_normalized_average_true_range():
    pass


def calc_true_range():
    pass
