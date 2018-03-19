import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#from scipy import stats
def load_ticks(price_amt=False):
	#Read in data and execute some transformations
	if not price_amt:
		data_frame = pd.read_csv('Data/sample.csv',
							names=["dates", 'price', 'volume'],
							converters={"price":float, "volume":float})
	else: #Load only relevent data instead of whole dataset
		data_frame = pd.read_csv('Data/sample.csv',
							names=["dates", 'price', 'volume'],
							converters={"price":float, "volume":float},
							nrows=price_amt)
	data_frame = data_frame.set_index(["dates"])
	data_frame.index = pd.to_datetime(data_frame.index, unit='s')
	return data_frame


def load_ohlcv(ohlcv_period, price_amt):
	ticks = load_ticks()
	ohlcv = to_ohlcv(ticks, ohlcv_period)
	return ohlcv.iloc[-price_amt:]

def to_ohlcv(data_frame, period="30min"):
	ticks = data_frame.ix[:, ['price', 'volume']]
	
	bars = ticks["price"].resample(period).ohlc()
	volumes = ticks["volume"].resample(period).sum()

	ohlcv = bars.assign(volume = volumes.values)
	return ohlcv

def weighted_moving_average(prices, period):
	weights = [i/period for i in range(period)]
	wma = [np.NaN for _ in range(period)]
	for i in range(len(prices)-period):
		wma.append(np.average(prices[i:period+i], weights=weights))
	return np.array(wma)

def hull_moving_average(prices, period):
	#Source: https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/hull-moving-average
	#1. Calculate a Weighted Moving Average with period n / 2 and multiply it by 2
	wma1 = weighted_moving_average(prices, int(round(period/2))) * 2

	#2. Calculate a Weighted Moving Average for period n and subtract if from step 1
	wma2 = weighted_moving_average(prices, period)
	wma_res = wma1 - wma2

	#3. Calculate a Weighted Moving Average with period sqrt(n) using the data from step 2
	hma = weighted_moving_average(wma_res, int(round(np.sqrt(period))))
	return hma


def normalize(array):
	return array / array.max()

def linnear_regression(y):

	x = np.arange(len(y))

	slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
	#Visualize
	#plt.plot(x, y, 'o', label='original data')
	#plt.plot(x, intercept + slope*x, 'r', label='fitted line')
	#plt.legend()
	#plt.show()


	return (slope, r_value, std_err)