from utils import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from financial_functions import *
from agent import *
from operator import attrgetter
def init_population(population_amt, ma_sources):
	traders = [Trader() for _ in range(population_amt)]
	for trader in traders:
		period = trader.conf["ma_period"]
		ma_func = trader.conf["ma_func"]
		ma_source = trader.conf["ma_source"]
		trader.conf["ma"] = ma_func(ma_sources[ma_source], period)

	return traders


def main():
	price_amt = int(1e10)
	candle_period = "1H"
	ohlcv = load_ohlcv(candle_period=candle_period, price_amt=price_amt)

	opens = ohlcv.open.values
	highs = ohlcv.high.values
	lows = ohlcv.low.values
	closes = ohlcv.close.values
	vol = ohlcv.volume.values

	ma_sources = {
		"open":opens,
		"high":highs,
		"low":lows,
		"close":closes,
		"hl2":(highs+lows)/2,
		"hlc3":(highs+lows+closes)/3,
		"ohlc4":(opens+highs+lows+closes)/4
		}

	ma_maximum_period = 500

	#Genetic config
	population_amt = 1
	generations = 1
	traders = init_population(population_amt=population_amt, ma_sources=ma_sources)

	for gen in range(generations):

		#Test every trader on every trade oppurtinity
		for i in range(ma_maximum_period+3, len(closes)):
			for trader in traders:
				trader.event(i, closes[i], lows[i], highs[i])

		#Sort traders based on performance
		traders.sort(key = attrgetter('profit'))
		print(traders[0].profit)

		#Reset metrics for traders for next generation
		for trader in traders:
			trader.reset()

	for trader in traders:
		plt.plot(trader.profit_over_time)
	plt.show()
main()