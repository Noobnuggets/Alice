import numpy as np
import matplotlib.pyplot as plt
from utils import *
def weighted_moving_average(prices, period):
	weights = [i/period for i in range(period)]
	wma = [np.NaN for _ in range(period)]
	for i in range(len(prices)-period):
		wma.append(np.average(prices[i:period+i], weights=weights))
	return np.array(wma)

def hull_moving_average(prices, period):
	#Source: https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/hull-moving-average
	#1. Calculate a Weighted Moving Average with period n / 2 and multiply it by 2
	wma1 = weighted_moving_average(prices, int(round(period/2))) * 2

	#2. Calculate a Weighted Moving Average for period n and subtract if from step 1
	wma2 = weighted_moving_average(prices, period)
	wma_res = wma1 - wma2

	#3. Calculate a Weighted Moving Average with period sqrt(n) using the data from step 2
	hma = weighted_moving_average(wma_res, int(round(np.sqrt(period))))
	return hma

def walk_forward(highs, lows, trade_direction, entry_price, take_profit, stop_loss):
	print(len(highs))
	print(len(lows))
	future_prices_amt = len(highs)
