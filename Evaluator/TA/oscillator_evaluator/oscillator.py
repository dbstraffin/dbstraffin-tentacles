import tulipy
# import numpy
# import math

from .util import BaseOscillatorEvaluator


class UltimateOscillatorEvaluator(BaseOscillatorEvaluator):

    async def evaluate(self, ctx):
        self.eval_pending()

        if len(ctx.close) >= self.slow:
            try:
                ultosc = tulipy.ultosc(ctx.high, ctx.low, ctx.close, self.fast, self.middle, self.slow)[-1]
            except tulipy.lib.InvalidOptionError as e:
                self.logger.debug(f"Error when computing Ultimate Oscillator: {e}")
                self.logger.exception(e, False)
            else:
                if ultosc <= self.long:
                    self.eval_long()
                elif ultosc >= self.short:
                    self.eval_short()

        await self.evaluation_completed(ctx.cryptocurrency, ctx.symbol, ctx.time_frame, eval_time=ctx.eval_time())


class CommodityChannelIndexOscillatorEvaluator(BaseOscillatorEvaluator):

    async def evaluate(self, ctx):
        self.eval_pending()

        if len(ctx.close) >= self.period:
            try:
                cci = tulipy.cci(ctx.high, ctx.low, ctx.close, self.period)[-1]
            except tulipy.lib.InvalidOptionError as e:
                self.logger.debug(f"Error when computing Commodity Channel Index: {e}")
                self.logger.exception(e, False)
            else:
                if cci <= self.long:
                    self.eval_long()
                elif cci >= self.short:
                    self.eval_short()

        await self.evaluation_completed(ctx.cryptocurrency, ctx.symbol, ctx.time_frame, eval_time=ctx.eval_time())
