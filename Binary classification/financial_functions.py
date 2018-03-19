import numpy as np
import matplotlib.pyplot as plt
from utils import *
def long_cnd(hmas):
	return hmas[1] < hmas[2] and hmas[0] > hmas[1]

def short_cnd(hmas):
	return hmas[1] > hmas[2] and hmas[0] < hmas[1]

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

def walk_forward_long(highs, lows, entry_price, take_profit, stop_loss):
	assert len(highs) == len(lows), "walk_forward recieved missmatching lows and highs:\nlen(highs): " + str(len(highs)) + "\nlen(lows): " + str(len(lows))

	tp_hit = False
	sl_hit = False

	future_candles_amt = len(highs) #Could be lows aswell

	#If we are going long, aka buying the secondary currency(BTC)
	for i in range(1, future_candles_amt):

		percent_move_highs = ((highs[i] - entry_price) / entry_price) * 100 #Positive
		percent_move_lows = ((lows[i] - entry_price) / entry_price) * 100 #Negative

		sl_hit = percent_move_lows <= stop_loss
		tp_hit = percent_move_highs > take_profit
		if sl_hit or tp_hit:
			break
	return tp_hit, sl_hit

def walk_forward_short(highs, lows, entry_price, take_profit, stop_loss):
	assert len(highs) == len(lows), "walk_forward recieved missmatching lows and highs:\nlen(highs): " + str(len(highs)) + "\nlen(lows): " + str(len(lows))

	tp_hit = False
	sl_hit = False

	future_candles_amt = len(highs) #Could be lows aswell

	#If we are going short
	for i in range(1, future_candles_amt):
		percent_move_highs = ((highs[i] - entry_price) / entry_price) * 100 #Positive
		percent_move_lows = ((lows[i] - entry_price) / entry_price) * 100 #Negative

		tp_hit = percent_move_lows < take_profit
		sl_hit = percent_move_highs >= stop_loss
		if sl_hit or tp_hit:
			break
	return tp_hit, sl_hit