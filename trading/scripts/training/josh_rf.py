from trading.constants.instrument import INSTRUMENT_EUR_USD
from trading.algorithms.jenetic_segmentation_oscillatory_heuristics import Josh
from trading.algorithms.random_stumps import RandomStumps
from trading.backtest.backtest_data_broker import BacktestDataBroker
from trading.classifier.random_forest import RFClassifier
from trading.training_strategies.training_runner import TrainingStrategyRunner


def main():
    base_pair = {'currency': 'usd', 'starting_units': 1000}
    quote_pair = {'currency': 'eur', 'starting_units': 0}
    instrument = INSTRUMENT_EUR_USD
    data_file = ''
    broker = BacktestDataBroker(instrument, base_pair, quote_pair, data_file)

    config = {
        'strategy_name': Josh.name,
        'instrument': instrument,
        'base_pair': base_pair,
        'quote_pair': quote_pair,
        'classifier_config': {'classifier_id': None, 'classifier_name': RFClassifier.name,
                              'features': RandomStumps.features}
    }

    num_candles = 14316
    strategy = TrainingStrategyRunner(config, broker, num_candles)
    strategy.tick()


if __name__ == '__main__':
    main()
