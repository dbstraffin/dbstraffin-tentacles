import tulipy
# import numpy
# import math

import octobot_commons.constants as commons_constants
# import octobot_commons.data_util as data_util
import octobot_evaluators.evaluators as evaluators
import octobot_evaluators.util as evaluators_util
import octobot_tentacles_manager.api as tentacles_manager_api
import octobot_trading.api as trading_api
# import tentacles.Evaluator.Util as EvaluatorUtil


class UltimateOscillatorEvaluator(evaluators.TAEvaluator):

    def __init__(self, tentacles_setup_config):
        super().__init__(tentacles_setup_config)
        self.evaluator_config = tentacles_manager_api.get_tentacle_config(self.tentacles_setup_config, self.__class__)
        self.short = self.evaluator_config['short']
        self.long = self.evaluator_config['long']

        self.fast = self.evaluator_config['fast']
        self.middle = self.evaluator_config['middle']
        self.slow = self.evaluator_config['slow']
        self.min_periods = max(self.fast, self.middle, self.slow)

    async def ohlcv_callback(self, exchange: str, exchange_id: str,
                             cryptocurrency: str, symbol: str, time_frame, candle, inc_in_construction_data):

        candles = self.get_exchange_symbol_data(exchange, exchange_id, symbol)
        high = trading_api.get_symbol_high_candles(candles, time_frame,
                                                   include_in_construction=inc_in_construction_data)
        low = trading_api.get_symbol_low_candles(candles, time_frame,
                                                 include_in_construction=inc_in_construction_data)
        close = trading_api.get_symbol_close_candles(candles, time_frame,
                                                     include_in_construction=inc_in_construction_data)

        await self.evaluate(cryptocurrency, symbol, time_frame, high, low, close, candle)

    async def evaluate(self, cryptocurrency, symbol, time_frame, high, low, close, candle):
        self.eval_note = commons_constants.START_PENDING_EVAL_NOTE

        if len(close) >= self.min_periods:
            try:
                ultosc = tulipy.ultosc(high, low, close, self.fast, self.middle, self.slow)[-1]

                if ultosc <= self.long:
                    self.eval_note = -1
                elif ultosc >= self.short:
                    self.eval_note = 1

            except tulipy.lib.InvalidOptionError as e:
                self.logger.debug(f"Error when computing UltimateOscillator: {e}")
                self.logger.exception(e, False)
                self.eval_note = commons_constants.START_PENDING_EVAL_NOTE

        await self.evaluation_completed(cryptocurrency, symbol, time_frame,
                                        eval_time=evaluators_util.get_eval_time(full_candle=candle,
                                                                                time_frame=time_frame))
