import octobot_commons.constants as commons_constants
import octobot_evaluators.evaluators as evaluators
import octobot_evaluators.util as evaluators_util
import octobot_tentacles_manager.api as tentacles_manager_api
import octobot_trading.api as trading_api


class EvaluatorContext():
    def __init__(self, cryptocurrency: str, symbol: str, time_frame, candles, candle, inc_in_construction_data):
        self.cryptocurrency = cryptocurrency
        self.symbol = symbol
        self.time_frame = time_frame
        self.candles = candles
        self.candle = candle
        self.inc_in_construction_data = inc_in_construction_data

    @property
    def high(self):
        return trading_api.get_symbol_high_candles(self.candles, self.time_frame,
                                                   include_in_construction=self.inc_in_construction_data)

    @property
    def low(self):
        return trading_api.get_symbol_low_candles(self.candles, self.time_frame,
                                                  include_in_construction=self.inc_in_construction_data)

    @property
    def close(self):
        return trading_api.get_symbol_close_candles(self.candles, self.time_frame,
                                                    include_in_construction=self.inc_in_construction_data)

    def eval_time(self):
        return evaluators_util.get_eval_time(full_candle=self.candle, time_frame=self.time_frame)


class BaseOscillatorEvaluator(evaluators.TAEvaluator):

    def __init__(self, tentacles_setup_config):
        super().__init__(tentacles_setup_config)
        self.evaluator_config = tentacles_manager_api.get_tentacle_config(self.tentacles_setup_config, self.__class__)

    @property
    def period(self):
        return self.evaluator_config['period']

    @property
    def short(self):
        return self.evaluator_config['short']

    @property
    def long(self):
        return self.evaluator_config['long']

    @property
    def fast(self):
        return self.evaluator_config['fast']

    @property
    def middle(self):
        return self.evaluator_config['middle']

    @property
    def slow(self):
        return self.evaluator_config['slow']

    def eval_pending(self):
        self.eval_note = commons_constants.START_PENDING_EVAL_NOTE

    def eval_long(self):
        self.eval_note = -1

    def eval_short(self):
        self.eval_note = 1

    async def ohlcv_callback(self, exchange: str, exchange_id: str,
                             cryptocurrency: str, symbol: str, time_frame, candle, inc_in_construction_data):
        candles = self.get_exchange_symbol_data(exchange, exchange_id, symbol)
        context = EvaluatorContext(cryptocurrency, symbol, time_frame, candles, candle, inc_in_construction_data)
        await self.evaluate(context)
