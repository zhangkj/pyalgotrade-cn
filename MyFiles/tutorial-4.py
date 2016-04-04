from pyalgotrade.broker.fillstrategy import DefaultStrategy
from pyalgotrade.broker.backtesting import TradePercentage
from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
import  MyFiles

class DoubleMA(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, n, m):
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        self.getBroker().setFillStrategy(DefaultStrategy(None))
        self.getBroker().setCommission(TradePercentage(0.001))
        self.__position = None
        self.__prices = feed[instrument].getPriceDataSeries()
        self.__malength1 = int(n)
        self.__malength2 = int(m)

        self.__ma1 = ma.SMA(self.__prices, self.__malength1)
        self.__ma2 = ma.SMA(self.__prices, self.__malength2)

    def getPrice(self):
        return self.__prices

    def getSMA(self):
        return self.__ma1,self.__ma2

    def onEnterCanceled(self, position):
        self.__position = None

    def onEnterOK(self):
        pass

    def onExitOk(self, position):
        self.__position = None
        #self.info("long close")

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long position.

        if self.__ma2[-1]is None:
            return

        if self.__position is not None:
            if not self.__position.exitActive() and cross.cross_below(self.__ma1, self.__ma2) > 0:
                self.__position.exitMarket()
                #self.info("sell %s" % (bars.getDateTime()))

        if self.__position is None:
            if cross.cross_above(self.__ma1, self.__ma2) > 0:
                shares = int(self.getBroker().getEquity() * 0.2 / bars[self.__instrument].getPrice())
                self.__position = self.enterLong(self.__instrument, shares)
                #print bars[self.__instrument].getDateTime(), bars[self.__instrument].getPrice()
                #self.info("buy %s" % (bars.getDateTime()))


def run_strategy(smaPeriods,smaPeriodl):
    # Load the yahoo feed from the CSV file
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("mro",MyFiles.dataPath+"mro-2013-yahoofinance.csv")

    # Evaluate the strategy with the feed.
    myStrategy = DoubleMA(feed, "mro", smaPeriods,smaPeriodl)
    myStrategy.run()
    portfolioValue=myStrategy.getBroker().getEquity()
    print "smaPeriod:"+str(smaPeriods)+" "+str(smaPeriodl)+",Final portfolio value: $%.2f" % portfolioValue
    return  portfolioValue,smaPeriods,smaPeriodl

maxValue = 0
smaPeriod = 0
#run_strategy(15)
for i in range(10,30):
    for j in range(5,10):
        result,smas,smal = run_strategy(j,i)
        if result>maxValue:
            maxValue=result
            smaPeriod = str(smas)+" "+str(smal)

print "smaPeriod:"+str(smaPeriod)+",maxValue:"+str(maxValue)
