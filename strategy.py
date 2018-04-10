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
	max_lookback = 50
	population_amt = 50
	generations = 100
	max_survival_factor = 1
	
	mutation_factor = 0.05 #Mutation factor should be unique to the individual, 
	#offspring inherit mutation factor either randomly or a convolved version of daddy and mommy

	traders, average_fitness, best_fitness, best_trader = train(candle_period, max_lookback, population_amt, generations, mutation_factor, max_survival_factor)

	
	show_metrics(traders, average_fitness, best_fitness)
	reset_metrics(traders)
	#Validate results
	validate(traders, candle_period, max_lookback)
	show_metrics_valid(traders)

	print("Best Trader of all time stats")
	reset_metrics([best_trader])
	#Validate results
	validate([best_trader], candle_period, max_lookback)
	show_metrics_valid([best_trader])


main()