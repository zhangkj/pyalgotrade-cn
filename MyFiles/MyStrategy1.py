# -*- coding: utf-8 -*-
"""
Created on  April 06 2016

@author: ZhangKJ
"""

from pyalgotrade import strategy
from pyalgotrade.technical import ma
from pyalgotrade.technical import rsi
from pyalgotrade.technical import macd
from pyalgotrade.technical import cross
from pyalgotrade import plotter
from pyalgotrade.barfeed import  yahoofeed
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade import bar
import  MyFiles

"""
Strategy描述：
采用双均线和macd结合使用，
long
建仓信号：价格位于双均线之上，均线上穿后，macd上穿后，三个条件同时成立；
平仓信号：价格位于位于短期均线之下，均线下穿，macd下穿，三个条件任意一个成立；
short
"""


class MyStrategy1(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument,fastSMA,slowSMA, fastEMA, slowEMA, signalEMA):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        # We'll use adjusted close values, if available, instead of regular close values.
        if feed.barsHaveAdjClose():
            self.setUseAdjustedValues(True)
        self.__priceDS = feed[instrument].getPriceDataSeries()
        self.__macd = macd.MACD(self.__priceDS,12,26,9)
        self.__smaF = ma.SMA(self.__priceDS,fastSMA)
        self.__smaS = ma.SMA(self.__priceDS,slowSMA)
        self.__longPos = None
        self.__shortPos = None
        self.__PosPrice = None
        self.__stopLoss = 0.05
        self.__targetProfit = 1
        self.__waitTime = 5
        self.__time = 5

    def getSMAF(self):
        return  self.__smaF

    def getSMAS(self):
        return  self.__smaS

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
        if self.__macd.getHistogram()[-1] is None or self.__macd.getSignal()[-1] is None  or self.__macd[-1] is None or self.__smaF[-1] is None or self.__smaS[-1] is None:
            return

        bar = bars[self.__instrument]
        if self.__longPos is not None:
            if self.exitLongSignal(bar):
                self.__longPos.exitMarket()
                self.__waitTime = self.__time
                print "exit long:"+str(bar.getPrice())
        elif self.__shortPos is not None:
            if self.exitShortSignal(bar):
                self.__shortPos.exitMarket()
                self.__waitTime = self.__time
                print "exit short:"+str(bar.getPrice())
        else:
            if self.__waitTime>0:
                self.__waitTime-=1
            elif self.enterLongSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__longPos = self.enterLong(self.__instrument, shares, True)
                self.__PosPrice = bar.getPrice()
                print "enter long:"+str(bar.getPrice())
            elif self.enterShortSignal(bar):
                shares = int(self.getBroker().getCash() * 0.9 / bars[self.__instrument].getPrice())
                self.__shortPos = self.enterShort(self.__instrument, shares, True)
                self.__PosPrice = bar.getPrice()
                print "enter short:"+str(bar.getPrice())

    def enterLongSignal(self, bar):
        #return bar.getPrice() > self.__entrySMA[-1] and self.__rsi[-1] <= self.__overSoldThreshold
        return self.__smaF[-1] > self.__smaS[-1] and bar.getPrice() >self.__smaF[-1] and  self.__macd[-1]-self.getSignal()[-1] > 0

    def exitLongSignal(self,bar):
        #return cross.cross_above(self.__priceDS, self.__exitSMA) and not self.__longPos.exitActive()
        return bar.getPrice() < self.__smaS[-1] and self.__smaF[-1] < self.__smaS[-1] and  self.__macd[-1]-self.getSignal()[-1] < 0 or self.__PosPrice - bar.getPrice() > self.__stopLoss or bar.getPrice() - self.__PosPrice > self.__targetProfit
        #return bar.getPrice() < self.__smaS[-1] or  self.__smaF[-1] < self.__smaS[-1] or  self.__macd[-1]-self.getSignal()[-1] < 0 or self.__PosPrice - bar.getPrice() > self.__stopLoss or bar.getPrice() - self.__PosPrice > self.__targetProfit
    def enterShortSignal(self, bar):
        #return bar.getPrice() < self.__entrySMA[-1] and self.__rsi[-1] >= self.__overBoughtThreshold
        return self.__smaF[-1] < self.__smaS[-1] and bar.getPrice() < self.__smaF[-1] and  self.__macd[-1]-self.getSignal()[-1] < 0

    def exitShortSignal(self,bar):
        #return cross.cross_below(self.__priceDS, self.__exitSMA) and not self.__shortPos.exitActive()
        return bar.getPrice() > self.__smaS[-1] and self.__smaF[-1] > self.__smaS[-1] and  self.__macd[-1]-self.getSignal()[-1] > 0  or bar.getPrice() - self.__PosPrice > self.__stopLoss or self.__PosPrice-bar.getPrice() > self.__targetProfit
        #return bar.getPrice() > self.__smaS[-1] or self.__smaF[-1] > self.__smaS[-1] or  self.__macd[-1]-self.getSignal()[-1] > 0  or bar.getPrice() - self.__PosPrice > self.__stopLoss or self.__PosPrice-bar.getPrice() > self.__targetProfit




def main(plot):
    instrument = "mro"
    fastSMA = 5
    slowSMA = 10
    fastEMA = 12
    slowEMA = 26
    signalEMA = 9
    frequency = bar.Frequency.MINUTE

    if frequency == bar.Frequency.DAY:
        path = MyFiles.dataPath+"mro-2013-yahoofinance.csv"
    elif frequency == bar.Frequency.MINUTE:
        path = MyFiles.dataIntradayPath+"MRO.csv"
    filepath = path

    #############################################don't change ############################33
    from pyalgotrade.barfeed.csvfeed import GenericBarFeed

    feed = GenericBarFeed(frequency)
    feed.setDateTimeFormat('%Y/%m/%d %H:%M')
    feed.addBarsFromCSV(instrument, filepath)

    #feed = yahoofeed.Feed()
    #feed.addBarsFromCSV(instrument,MyFiles.dataPath+"mro-2013-yahoofinance.csv")
    #feed.addBarsFromCSV(instrument,MyFiles.dataIntradayPath+"MRO.csv")


    strat = MyStrategy1(feed, instrument, fastSMA, slowSMA, fastEMA,slowEMA,signalEMA)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        plt.getOrCreateSubplot("macd").addDataSeries("MACD Value", strat.getMACD())
        plt.getOrCreateSubplot("macd").addDataSeries("MACD SignalValue", strat.getSignal())
        # plt.getOrCreateSubplot("macd").addDataSeries("MACD Histogram", strat.getHistogram())
        plt.getInstrumentSubplot(instrument).addDataSeries("Fast SMA", strat.getSMAF())
        plt.getInstrumentSubplot(instrument).addDataSeries("Slow SMA", strat.getSMAS())

        #plt.getOrCreateSubplot("rsi").addLine("Overbought", overBoughtThreshold)
        #plt.getOrCreateSubplot("rsi").addLine("Oversold", overSoldThreshold)

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    if plot:
        plt.plot()


if __name__ == "__main__":
    main(True)
