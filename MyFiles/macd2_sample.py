import macd2
from pyalgotrade import plotter
from pyalgotrade.tools import yahoofinance
from pyalgotrade.stratanalyzer import sharpe


def main(plot):
    instrument = "DIA"
    fastEMA = 12
    slowEMA = 26
    signalEMA = 9

    # Download the bars.
    feed = yahoofinance.build_feed([instrument], 2012, 2012, ".")

    strat = macd2.MACD2(feed, instrument, fastEMA,slowEMA,signalEMA)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    strat.attachAnalyzer(sharpeRatioAnalyzer)

    if plot:
        plt = plotter.StrategyPlotter(strat, True, True, True)
        plt.getOrCreateSubplot("macd").addDataSeries("MACD Value", strat.getMACD())
        plt.getOrCreateSubplot("macd").addDataSeries("MACD SignalValue", strat.getSignal())
        plt.getOrCreateSubplot("macd").addDataSeries("MACD Histogram", strat.getHistogram())
        #plt.getOrCreateSubplot("rsi").addLine("Overbought", overBoughtThreshold)
        #plt.getOrCreateSubplot("rsi").addLine("Oversold", overSoldThreshold)

    strat.run()
    print "Sharpe ratio: %.2f" % sharpeRatioAnalyzer.getSharpeRatio(0.05)

    if plot:
        plt.plot()


if __name__ == "__main__":
    main(True)
