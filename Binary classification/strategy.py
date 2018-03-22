from utils import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from financial_functions import *
from agent import *
from genetics import *
from time import time


def main():
	price_amt = int(1e55)
	candle_period = "1H"
	ohlcv = load_ohlcv(candle_period=candle_period, price_amt=price_amt)

	opens = ohlcv.open.values
	highs = ohlcv.high.values
	lows = ohlcv.low.values
	closes = ohlcv.close.values
	vol = ohlcv.volume.values
	print("Candles:", len(opens))

	ma_sources = {
		"open":opens,
		"high":highs,
		"low":lows,
		"close":closes,
		"hl2":(highs+lows)/2,
		"hlc3":(highs+lows+closes)/3,
		"ohlc4":(opens+highs+lows+closes)/4
		}

	ma_maximum_period = 300

	#Genetic config
	population_amt = 100
	generations = 5

	#Metrics
	average_fitness = [0]
	best_fitness = [0]

	traders = init_population(population_amt=population_amt)
	setup_mas(traders, ma_sources=ma_sources)

	for gen in range(generations):

		#Test every trader on every trade oppurtinity/candle
		for i in range(ma_maximum_period+3, len(closes)):
			for trader in traders:
				trader.event(i, closes[i], lows[i], highs[i])

		
		#Generation done
		#Collect metrics on a per-generation basis
		traders = calculate_fitness(traders)
		average_fitness.append(average_fitness_per_generation(traders))


		#Sort traders based on performance
		traders = sort_traders(traders)

		best_fitness.append(traders[0].fitness)
		print(gen, "best:", traders[0].fitness)
		print(gen, "avg:", average_fitness[gen])
		print()

		if not gen+1 == generations:
			#Remove the worst traders
			#Create children from the best traders, aka crossover
			survival_rate = 0.1 #1 - (generations/(gen+1))
			traders = kill_worst(traders, survival_rate=survival_rate)
			traders = crossover(traders, mutation_factor=0.05) #Crossover creates some individuals without fitness

			traders = fresh_dna(traders, population_amt)
			setup_mas(traders, ma_sources=ma_sources)

			#Reset metrics for traders for next generation
			
			reset_metrics(traders)

	print(traders[0].conf)

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

	print("")


	#Validate results
	price_amt = int(1e55)
	candle_period = "1H"
	valid_ohlcv = load_ohlcv_valid(candle_period=candle_period, price_amt=price_amt)

	valid_opens = ohlcv.open.values
	valid_highs = ohlcv.high.values
	valid_lows = ohlcv.low.values
	valid_closes = ohlcv.close.values
	valid_vol = ohlcv.volume.values
	print("valid Candles:", len(opens))

	ma_sources = {
		"open":valid_opens,
		"high":valid_highs,
		"low":valid_lows,
		"close":valid_closes,
		"hl2":(valid_highs+valid_lows)/2,
		"hlc3":(valid_highs+valid_lows+valid_closes)/3,
		"ohlc4":(valid_opens+valid_highs+valid_lows+valid_closes)/4
		}

	ma_maximum_period = 300

	#Metrics
	average_fitness = [0]
	best_fitness = [0]
	#Test every trader on every trade oppurtinity/candle
	reset_metrics(traders)
	for i in range(ma_maximum_period+3, len(valid_closes)):
		for trader in traders:
			trader.event(i, valid_closes[i], valid_lows[i], valid_highs[i])
		traders = calculate_fitness(traders)
		average_fitness.append(average_fitness_per_generation(traders))


	print(traders[0].conf)

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

main()