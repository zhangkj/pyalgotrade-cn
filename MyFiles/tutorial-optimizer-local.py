# -*- coding: utf-8 -*-
import  os
import itertools
from pyalgotrade.optimizer import local
from pyalgotrade.barfeed import yahoofeed
import sma_crossover
import MyFiles
import  doubleMA
from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import returns
if __name__ == '__main__':
    import sys
    sys.path.append("../samples")
    import rsi2


def parameters_generator():
    instrument = ["mro"]
    entrySMA = range(150, 251)
    exitSMA = range(5, 16)
    rsiPeriod = range(2, 11)
    overBoughtThreshold = range(75, 96)
    overSoldThreshold = range(5, 26)
    return itertools.product(instrument, entrySMA, exitSMA, rsiPeriod, overBoughtThreshold, overSoldThreshold)

def MyBackTest():
    instrument = "mro"
    mystrategy = rsi2.RSI2
    feed = yahoofeed.Feed()
    #add esv
    for i in range(2000,2013):
        year = str(i)
        datafilename = MyFiles.dataPath+instrument+"-"+year+"-"+MyFiles.dataFlag+".csv"

        if not os.path.exists(datafilename):
            print "not exists:"+ datafilename
            return
        else:
            feed.addBarsFromCSV(instrument,datafilename)

    local.run(mystrategy, feed, parameters_generator())

def MyPlot():
    instrument = "mro"
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("mro", MyFiles.dataPath+instrument+"-"+"2013"+"-"+MyFiles.dataFlag+".csv")

    # Evaluate the strategy with the feed's bars.
    #myStrategy = sma_crossover.SMACrossOver(feed, "orcl", 20)
    myStrategy  = doubleMA.DoubleMA(feed,instrument,9,12)
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)

    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(myStrategy)
    # Include the SMA in the instrument's subplot to get it displayed along with the closing prices.
    plt.getInstrumentSubplot(instrument).addDataSeries("SMAs", myStrategy.getSMA()[0])
    plt.getInstrumentSubplot(instrument).addDataSeries("SMAl", myStrategy.getSMA()[1])
    # Plot the simple returns on each bar.
    plt.getOrCreateSubplot("returns").addDataSeries("Simple returns", returnsAnalyzer.getReturns())

    # Run the strategy.
    myStrategy.run()
    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

    # Plot the strategy.
    plt.plot()
# The if __name__ == '__main__' part is necessary if running on Windows.
if __name__ == '__main__':
        MyBackTest()
        #MyPlot()
