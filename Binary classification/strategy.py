from utils import *
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from financial_functions import *
from agent import *
from genetics import *
from time import time


def main():
	candle_period = "1H"
	ma_maximum_period = 50
	population_amt = 100
	generations = 10
	survival_rate = 0.1
	mutation_factor = 0.05
	ohlcv = load_ohlcv(candle_period=candle_period)

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


	ma_maximum_period = 50

	#Genetic config
	population_amt = 100
	generations = 10

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
	show_metrics(traders, valid=False)


	#Validate results
	#Make sure no train data is used
	valid_ohlcv = load_ohlcv_valid(candle_period=candle_period)

	valid_opens = valid_ohlcv.open.values
	valid_highs = valid_ohlcv.high.values
	valid_lows = valid_ohlcv.low.values
	valid_closes = valid_ohlcv.close.values
	valid_vol = valid_ohlcv.volume.values
	print("valid Candles:", len(valid_opens))

	valid_ma_sources = {
		"open":valid_opens,
		"high":valid_highs,
		"low":valid_lows,
		"close":valid_closes,
		"hl2":(valid_highs+valid_lows)/2,
		"hlc3":(valid_highs+valid_lows+valid_closes)/3,
		"ohlc4":(valid_opens+valid_highs+valid_lows+valid_closes)/4
		}

	ma_maximum_period = 50

	setup_mas(traders, ma_sources=valid_ma_sources)

	#Metrics
	average_fitness = [0]
	best_fitness = [0]
	#Test every trader on every trade oppurtinity/candle
	reset_metrics(traders)
	for i in range(ma_maximum_period+3, len(valid_closes)):
		for trader in traders:
			trader.event(i, valid_closes[i], valid_lows[i], valid_highs[i])

	show_metrics(traders, valid=True)

main()