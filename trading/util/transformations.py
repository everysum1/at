from trading.constants.price_data import PRICE_ASK


def normalize_price_data(price_data, target_field=PRICE_ASK):
    prices = [candle_data[target_field] for candle_data in price_data]
    return prices


def normalize_current_price_data(price_data, target_field=PRICE_ASK):
    return price_data['prices'][0][target_field]


def get_last_candle_data(price_data):
    """
    Assumes the last (latest) candle is at position (len - 1)
    :param price_data:
    :return:
    """
    return price_data[-1]
