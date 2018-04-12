import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats
def plot(array, label):
	plt.plot(array, label=label)
	plt.legend()
	plt.show()
	
def load_ticks(path):
	#Read in data and execute some transformations
	data_frame = pd.read_csv(path,
							names=["dates", 'price', 'volume'],
							converters={"price":float, "volume":float})

	data_frame = data_frame.set_index(["dates"])
	data_frame.index = pd.to_datetime(data_frame.index, unit="s")
	return data_frame


def load_ohlcv(candle_period, path):
	ticks = load_ticks(path)
	ohlcv = to_ohlcv(ticks, candle_period)
	return ohlcv

def to_ohlcv(data_frame, period):
	ticks = data_frame.ix[:, ['price', 'volume']]
	
	bars = ticks["price"].resample(period).ohlc()
	volumes = ticks["volume"].resample(period).sum()

	ohlcv = bars.assign(volume = volumes.values)
	return ohlcv

def normalize(array):
	return array / array.max()

def linreg(y):
	x = np.arange(len(y))

	slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
	return x, slope, intercept, r_value, p_value, std_err

def visual_linreg(y):
	x, slope, intercept, r_value, p_value, std_err = linreg(y)
	return x, intercept + slope*x

def load_all_data(candle_period, path):
	ohlcv = load_ohlcv(candle_period, path)

def avg_profit_per_trade(profit_over_trades):
	if len(profit_over_trades):
		return np.sum(profit_over_trades)/len(profit_over_trades)
	return 0

def profit_per_day(profit_over_time):
	#Assume candles were 1hr each
	days = []
	for i in range(0, len(profit_over_time), 24):
		days.append(np.sum(profit_over_time[i:i+24])/24)
	plt.bar(np.arange(len(days)), days)
	plt.show()