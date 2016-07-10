from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.algorithms.random_stumps import RandomStumps
from trading.broker.oanda import OandaBroker
from trading.live.live_runner import LiveTradingStrategyRunner


def main():
    classifier_id = '571bf11f16890198e1e0243d'

    base_pair = {'currency': 'usd'}
    quote_pair = {'currency': 'eur'}

    instrument = INSTRUMENT_EUR_USD
    broker = OandaBroker(instrument)
    classifier_config = {'classifier_id': classifier_id}

    strategy_config = {
        'strategy_name': RandomStumps.name,
        'instrument': instrument,
        'base_pair': base_pair,
        'quote_pair': quote_pair,
        'classifier_config': classifier_config
    }

    strategy = LiveTradingStrategyRunner(strategy_config, broker)
    strategy.tick()


if __name__ == '__main__':
    main()
