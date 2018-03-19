import numpy as np
import matplotlib.pyplot as plt
from utils import *
def weighted_moving_average(prices, period):
	assert type(period) is int

	weights = [i/period for i in range(period)]
	wma = [np.NaN for _ in range(period)]
	for i in range(len(prices)-period):
		wma.append(np.average(prices[i:period+i], weights=weights))
	return np.array(wma)

def hull_moving_average(prices, period):
	assert type(period) is int, "hull_moving_average recieved a period of type: " + str(type(period)) + " Only int allowed!"
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
	assert len(highs) == len(lows), "walk_forward recieved missmatching lows and highs:\nlen(highs): " + str(len(highs)) + "\nlen(lows): " + str(len(lows))
	assert trade_direction == -1 or trade_direction == 1, "walk_forward was unable to determine trade_direction, -1 or 1 is acceptable"
	return True, False