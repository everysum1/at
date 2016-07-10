from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.algorithms.simple_pattern_matcher import PatternMatch
from trading.broker.oanda import OandaBroker
from trading.live.live_runner import LiveTradingStrategyRunner


def main():
    classifier_id = '574db8431689015f6096544c'

    base_pair = {'currency': 'usd'}
    quote_pair = {'currency': 'eur'}

    instrument = INSTRUMENT_EUR_USD
    broker = OandaBroker(instrument)
    classifier_config = {'classifier_id': classifier_id}

    strategy_config = {
        'strategy_name': PatternMatch.name,
        'instrument': instrument,
        'base_pair': base_pair,
        'quote_pair': quote_pair,
        'classifier_config': classifier_config
    }

    strategy = LiveTradingStrategyRunner(strategy_config, broker)
    strategy.tick()


if __name__ == '__main__':
    main()
