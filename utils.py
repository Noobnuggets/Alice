import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

def load_ticks(path):
	#Read in data and execute some transformations
	data_frame = pd.read_csv(path,
							names=["dates", 'price', 'volume'],
							converters={"price":float, "volume":float})

	data_frame = data_frame.set_index(["dates"])
	data_frame.index = pd.to_datetime(data_frame.index, unit='s')
	return data_frame

def load_ohlcv_valid(candle_period):
	ticks = load_ticks("Data/train.csv")
	ohlcv = to_ohlcv(ticks, candle_period)
	return ohlcv

def load_ohlcv(candle_period):
	ticks = load_ticks("Data/validation.csv")
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


def show_metrics(traders, average_fitness, best_fitness):
	print("Best Trader")
	conf = traders[0].conf
	print("Ma period:", conf["ma_period"])
	print()
	print("(L) take profit:", conf["long_tp"], "%")
	print("(S) take profit:", abs(conf["short_tp"]), "%")
	print("(L) stop loss:", abs(conf["long_sl"]), "%")
	print("(S) stop loss", conf["short_sl"], "%")
	print()
	print("Ma source:", conf["ma_source"])
	print()
	print("Long trades:", traders[0].long_trades)
	print("short trades:", traders[0].short_trades)
	print("Total trades:", traders[0].long_trades + traders[0].short_trades)
	print()
	print("winning trades: ", traders[0].winning_trades)
	print("loosing trades: ", traders[0].loosing_trades)
	print()
	print("Final profit:", traders[0].profit, "%")


	if traders[0].loosing_trades == 0:
		traders[0].loosing_trades = 1
	print("profit ratio: ", traders[0].winning_trades/traders[0].loosing_trades)
	print("Both hit: ", traders[0].both_hit)


	plt.title("Average fitness / generation")
	plt.plot(average_fitness, label="fitness")
	x, y = visual_linreg(average_fitness)
	plt.plot(x, y, "r", label="fitted line")
	plt.show()

	plt.clf()

	plt.title("Best Fitness / generation")
	plt.plot(best_fitness, label="fitness")
	x, y = visual_linreg(best_fitness)
	plt.plot(x, y, "r", label="fitted line")
	plt.show()

	plt.title("Best Profit over trades")
	plt.plot(traders[0].profit_over_trades, label="profit")
	x, y = visual_linreg(traders[0].profit_over_trades)
	plt.plot(x, y, "r", label="fitted line")
	plt.show()

	plt.title("Best Profit over time")
	plt.plot(traders[0].profit_over_time, label="profit")
	x, y = visual_linreg(traders[0].profit_over_time)
	plt.plot(x, y, "r", label="fitted line")
	plt.show()


def show_metrics_valid(traders):

	print("Best Trader")
	conf = traders[0].conf
	print("Ma period:", conf["ma_period"])
	print()
	print("(L) take profit:", conf["long_tp"], "%")
	print("(S) take profit:", abs(conf["short_tp"]), "%")
	print("(L) stop loss:", abs(conf["long_sl"]), "%")
	print("(S) stop loss", conf["short_sl"], "%")
	print()
	print("Ma source:", conf["ma_source"])
	print()
	print("Long trades:", traders[0].long_trades)
	print("short trades:", traders[0].short_trades)
	print("Total trades:", traders[0].long_trades + traders[0].short_trades)
	print()
	print("winning trades: ", traders[0].winning_trades)
	print("loosing trades: ", traders[0].loosing_trades)
	print()
	print("Final profit:", traders[0].profit, "%")

	plt.title("Best Profit over trades")
	plt.plot(traders[0].profit_over_trades, label="profit")
	x, y = visual_linreg(traders[0].profit_over_trades)
	plt.plot(x, y, "r", label="fitted line")
	plt.show()

	plt.title("Best Profit over time")
	plt.plot(traders[0].profit_over_time, label="profit")
	x, y = visual_linreg(traders[0].profit_over_time)
	plt.plot(x, y, "r", label="fitted line")
	plt.show()

def linreg(y):
	x = np.arange(len(y))

	slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
	return x, slope, intercept, r_value, p_value, std_err

def visual_linreg(y):
	x, slope, intercept, r_value, p_value, std_err = linreg(y)
	return x, intercept + slope*x