from utils import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from financial_functions import *
from agent import *
from genetics import *


def main():
	price_amt = int(1e10)
	candle_period = "15min"
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
	population_amt = 100
	generations = 5

	#Metrics
	average_profits = [0]

	traders = init_population(population_amt=population_amt)
	setup_mas(traders, ma_sources=ma_sources)

	for gen in range(generations):

		#Test every trader on every trade oppurtinity/candle
		for i in range(ma_maximum_period+3, len(closes)):
			for trader in traders:
				trader.event(i, closes[i], lows[i], highs[i])

		
		#Generation done
		#Collect metrics on a per-generation basis
		average_profits.append(average_profit_per_generation(traders))

		#Sort traders based on performance
		traders = sort_traders(traders)
		
		#Reset metrics for traders for next generation
		reset_metrics(traders)

		#Remove the worst traders
		new_traders = kill_worst(traders, survival_factor=0.7)
		

		#Create children from the best traders, aka crossover
		new_traders = crossover(new_traders, mutation_factor=0.01)
		print(len(new_traders))
		setup_mas(new_traders, ma_sources=ma_sources)

		
	plt.plot(average_profits)
	plt.show()

main()