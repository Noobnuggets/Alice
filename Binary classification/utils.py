import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#from scipy import stats
def plot(arrays):
	for a in arrays:
		plt.plot(a)
	plt.show()

def load_ticks(tick_count=False):
	#Read in data and execute some transformations
	path = "Data/.coinbaseUSD.csv"
	if not tick_count or tick_count == "All":
		data_frame = pd.read_csv(path,
							names=["dates", 'price', 'volume'],
							converters={"price":float, "volume":float})

	else: #Load only relevent data instead of whole dataset
		data_frame = pd.read_csv(path,
							names=["dates", 'price', 'volume'],
							converters={"price":float, "volume":float},
							nrows=tick_count)
	data_frame = data_frame.set_index(["dates"])
	data_frame.index = pd.to_datetime(data_frame.index, unit='s')
	return data_frame


def load_ohlcv(candle_period, price_amt):
	ticks = load_ticks("All")
	ohlcv = to_ohlcv(ticks, candle_period)
	return ohlcv.iloc[-price_amt:]

def to_ohlcv(data_frame, period="30min"):
	ticks = data_frame.ix[:, ['price', 'volume']]
	
	bars = ticks["price"].resample(period).ohlc()
	volumes = ticks["volume"].resample(period).sum()

	ohlcv = bars.assign(volume = volumes.values)
	return ohlcv

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