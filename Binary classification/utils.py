import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
#from scipy import stats
def plot(arrays):
	for a in arrays:
		plt.plot(a)
	plt.show()

def load_ticks(path):
	#Read in data and execute some transformations
	data_frame = pd.read_csv(path,
							names=["dates", 'price', 'volume'],
							converters={"price":float, "volume":float})

	data_frame = data_frame.set_index(["dates"])
	data_frame.index = pd.to_datetime(data_frame.index, unit='s')
	return data_frame

def load_ohlcv_valid(candle_period):
	ticks = load_ticks("Data/validation.csv")
	ohlcv = to_ohlcv(ticks, candle_period)
	return ohlcv

def load_ohlcv(candle_period):
	ticks = load_ticks("Data/train.csv")
	ohlcv = to_ohlcv(ticks, candle_period)
	return ohlcv

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

def show_metrics(traders, valid=False):
	if not valid:
		plt.title("Average fitness / generation")
		plt.plot(average_fitness)
		plt.show()

		plt.clf()

		plt.title("Best Fitness / generation")
		plt.plot(best_fitness)
		plt.show()

		plt.title("Best Profit over trades")
		plt.plot(traders[0].profit_over_trades)
		plt.show()

		plt.clf()
		plt.title("Best Profit over time")
		plt.plot(traders[0].profit_over_time)
		plt.show()

		print("Long trades:", traders[0].long_trades)
		print("short trades:", traders[0].short_trades)

		print("winning trades: ", traders[0].winning_trades)
		print("loosing trades: ", traders[0].loosing_trades)

		if traders[0].loosing_trades == 0:
			traders[0].loosing_trades = 1
		print("profit ratio: ", traders[0].winning_trades/traders[0].loosing_trades)
		print("Both hit: ", traders[0].both_hit)
	else:
		plt.title("Best Profit over trades")
		plt.plot(traders[0].profit_over_trades)
		plt.show()

		plt.clf()
		plt.title("Best Profit over time")
		plt.plot(traders[0].profit_over_time)
		plt.show()

		print("Long trades:", traders[0].long_trades)
		print("short trades:", traders[0].short_trades)

		print("winning trades: ", traders[0].winning_trades)
		print("loosing trades: ", traders[0].loosing_trades)

		if traders[0].loosing_trades == 0:
			traders[0].loosing_trades = 1
		print("profit ratio: ", traders[0].winning_trades/traders[0].loosing_trades)
		print("Both hit: ", traders[0].both_hit)