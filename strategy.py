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
	max_lookback = 200
	population_amt = 100
	generations = 100
	max_survival_factor = 0.8
	
	mutation_factor = 0.05 #Mutation factor should be unique to the individual, 
	#offspring inherit mutation factor either randomly or a convolved version of daddy and mommy

	traders, average_fitness, best_fitness, best_trader = train(candle_period, max_lookback, population_amt, generations, mutation_factor, max_survival_factor)
	
	plot(average_fitness, "Average fitness")
	plot(best_fitness, "Best fitness")

	traders[0].report_conf()
	traders[0].report_metrics()

	plot(traders[0].metrics["profit_over_time"], "Training Profit/Time")
	plot(traders[0].metrics["profit_over_trades"], "Training Profit/Trades")


	
	#Validate results
	reset_metrics([traders[0]])
	validate(traders[0], candle_period, max_lookback)

	traders[0].report_conf()
	traders[0].report_metrics()

	plot(traders[0].metrics["profit_over_time"], "Validation Profit/Time")

	plot(traders[0].metrics["profit_over_trades"], "Validation Profit/Trades")



main()