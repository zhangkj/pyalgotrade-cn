from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import macd
from pyalgotrade.technical import cross


class MyStrategy1(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, fastEMA, slowEMA, signalEMA):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        # We'll use adjusted close values, if available, instead of regular close values.
        if feed.barsHaveAdjClose():
            self.setUseAdjustedValues(True)
        self.__priceDS = feed[instrument].getPriceDataSeries()
        self.__macd = macd.MACD(self.__priceDS,12,26,9)
        self.__longPos = None
        self.__shortPos = None

    def getMACD(self):
        return self.__macd

    def getSignal(self):
        return self.__macd.getSignal()

    def getHistogram(self):
        return self.__macd.getHistogram()

    def onEnterCanceled(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onExitOk(self, position):
        if self.__longPos == position:
            self.__longPos = None
        elif self.__shortPos == position:
            self.__shortPos = None
        else:
            assert(False)

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        position.exitMarket()

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate SMA and RSI.
        if self.__macd.getHistogram()[-1] is None or self.__macd.getSignal()[-1] is None  or self.__macd[-1] is None :
            return

        bar = bars[self.__instrument]
        if self.__longPos is not None:
            if self.exitLongSignal():
                self.__longPos.exitMarket()
        elif self.__shortPos is not None:
            if self.exitShortSignal():
                self.__shortPos.exitMarket()
        else:
            if self.enterLongSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__longPos = self.enterLong(self.__instrument, shares, True)
            elif self.enterShortSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__shortPos = self.enterShort(self.__instrument, shares, True)

    def enterLongSignal(self, bar):
        #return bar.getPrice() > self.__entrySMA[-1] and self.__rsi[-1] <= self.__overSoldThreshold
        return self.__macd[-1]-self.getSignal()[-1] > 0

    def exitLongSignal(self):
        #return cross.cross_above(self.__priceDS, self.__exitSMA) and not self.__longPos.exitActive()
         return self.__macd[-1]-self.getSignal()[-1] < 0
    def enterShortSignal(self, bar):
        #return bar.getPrice() < self.__entrySMA[-1] and self.__rsi[-1] >= self.__overBoughtThreshold
         return self.__macd[-1]-self.getSignal()[-1] < 0

    def exitShortSignal(self):
        #return cross.cross_below(self.__priceDS, self.__exitSMA) and not self.__shortPos.exitActive()
        return self.__macd[-1]-self.getSignal()[-1] > 0
