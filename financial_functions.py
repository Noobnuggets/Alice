import numpy as np
import matplotlib.pyplot as plt
from utils import *
import pandas as pd

def weigthed_moving_average(prices, period):
	wma = [np.NaN for _ in range(period)]
	weights = np.arange(period)
	weights = weights / np.sum(weights)

	for i in range(period, len(prices)):
		wma.append(np.sum(prices[i-period:i] * weights))

	return np.array(wma)

def simple_moving_average(prices, period):
	sma = [np.NaN for _ in range(period)]
	for i in range(period, len(prices)):
		sma.append(np.sum(prices[i-period:i])/period)
	return np.array(sma)

def MACD(prices, fast_len, slow_len, signal_len):
	#fast_ma = simple_moving_average(prices, period=fast_len)
	#slow_ma = simple_moving_average(prices, period=slow_len)

	#macd_line = fast_ma - slow_ma

	#signal_line = simple_moving_average(macd_line, period=signal_len)

	fast_ma = weigthed_moving_average(prices, period=fast_len)
	slow_ma = weigthed_moving_average(prices, period=slow_len)

	macd_line = fast_ma - slow_ma

	signal_line = weigthed_moving_average(macd_line, period=signal_len)
	return macd_line, signal_line

def find_pivot_points(prices, period):pass
	