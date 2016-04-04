from pyalgotrade import dataseries
from pyalgotrade import technical
import  pyalgotrade.technical.macd  as macd
import  pandas as pd

# Build a sequence based DataSeries.
seqDS = dataseries.SequenceDataSeries()

values = [16.39, 16.4999, 16.45, 16.43, 16.52, 16.51, 16.423, 16.41, 16.47, 16.45, 16.32, 16.36, 16.34, 16.59, 16.54, 16.52, 16.44, 16.47, 16.5, 16.45, 16.28, 16.07, 16.08, 16.1, 16.1, 16.09, 16.43, 16.4899, 16.59, 16.65, 16.78, 16.86, 16.86, 16.76]

# Put in some values.
for i,value in enumerate(values):
    seqDS.append(value)

macdvalue1= macd.MACD(seqDS,2,5,3)
dataS = macdvalue1.getSignal()
da =""